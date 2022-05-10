'''
Author: Thyssen Wen
Date: 2022-04-29 10:56:18
LastEditors: Thyssen Wen
LastEditTime: 2022-04-30 14:42:03
Description: Action recognition model loss
FilePath: /ETESVS/model/losses/tsm_loss.py
'''
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..builder import LOSSES

@LOSSES.register()
class SegmentationLoss(nn.Module):
    def __init__(self,
                 num_classes,
                 label_mode='soft',
                 sample_rate=4,
                 loss_weight=1.0,
                 ignore_index=-100):
        super().__init__()
        self.loss_weight = loss_weight
        self.ignore_index = ignore_index
        self.num_classes = num_classes
        self.sample_rate = sample_rate
        self.label_mode = label_mode
        self.elps = 1e-10

        if self.label_mode in ["soft"]:
            self.criteria = SoftLabelLoss(self.num_classes, ignore_index=self.ignore_index)
        elif self.label_mode in ['hard']:
            self.criteria = HardLableLoss(self.num_classes, ignore_index=self.ignore_index)
        else:
            raise NotImplementedError

    def forward(self, model_output, masks, labels):
        score = model_output
        # seg_score [stage_num, N, C, T]
        # masks [N, T]
        # labels [N, T]

        # classification branch loss
        if self.label_mode in ["soft"]:
            labels = labels[:, ::self.sample_rate]
            masks = masks[:, ::self.sample_rate]
        elif self.label_mode in ['hard']:
            labels = labels[:, ::self.sample_rate]
            labels = torch.repeat_interleave(labels, self.sample_rate, dim=-1)
            masks = masks[:, ::self.sample_rate]
            masks = torch.repeat_interleave(masks, self.sample_rate, dim=-1)

        loss = self.criteria(score, labels, masks)

        loss = self.loss_weight * loss

        loss_dict={}
        loss_dict["loss"] = loss
        return loss_dict

class HardLableLoss(nn.Module):
    def __init__(self,
                 num_classes,
                 smooth_weight=0.15,
                 ignore_index=-100):
        super().__init__()
        self.num_classes = num_classes
        self.ignore_index = ignore_index
        self.smooth_weight = smooth_weight
        self.ce = nn.CrossEntropyLoss(ignore_index=self.ignore_index, reduction='none')
        self.mse = nn.MSELoss(reduction='none')
        self.elps = 1e-10

    def forward(self, score, labels, masks):
        seg_loss = 0.
        for p in score:
            seg_cls_loss = self.ce(p.transpose(2, 1).contiguous().view(-1, self.num_classes), labels.view(-1))
            seg_loss += torch.sum(seg_cls_loss / (torch.sum(labels != -100) + self.elps))
            seg_loss += self.smooth_weight * torch.mean(torch.clamp(
                self.mse(F.log_softmax(p[:, :, 1:], dim=1), F.log_softmax(p.detach()[:, :, :-1], dim=1)
                ), min=0, max=16) * masks[:, 1:].unsqueeze(1))
        return seg_loss

class SoftLabelLoss(nn.Module):
    def __init__(self,
                 num_classes,
                 ignore_index=-100):
        super().__init__()
        self.num_classes = num_classes
        self.ignore_index = ignore_index
        self.ce = nn.CrossEntropyLoss(ignore_index=self.ignore_index, reduction='none')
        self.elps = 1e-10
    
    def forward(self, score, gt, mask):
        score = torch.mean(score, axis=-1)  # [N, num_class]
        cls_score = torch.reshape(score,
                               shape=[-1, self.num_classes])  # [N, num_class]

        # smooth label learning
        with torch.no_grad():
            device = cls_score.device
            # [N T]
            raw_labels = gt
            # deal label over num_classes
            # [N, 1]
            y = torch.zeros(raw_labels.shape, dtype=raw_labels.dtype, device=device)
            refine_label = torch.where(raw_labels != self.ignore_index, raw_labels, y)
            # [N C T]
            ce_y = F.one_hot(refine_label, num_classes=self.num_classes)

            raw_labels_repeat = torch.tile(raw_labels.unsqueeze(2), dims=[1, 1, self.num_classes])
            ce_y = torch.where(raw_labels_repeat != self.ignore_index, ce_y, torch.zeros(ce_y.shape, device=device, dtype=ce_y.dtype))
            # [N C]
            smooth_label = (torch.sum(ce_y.float(), dim=1) / ce_y.shape[1])

            # [N, 1]
            x = torch.ones((smooth_label.shape[0]), device=device)
            y = torch.zeros((smooth_label.shape[0]), device=device)
            mask = torch.where(torch.sum(smooth_label, dim=1)!=0, x, y)

        cls_loss = torch.mean(self.ce(cls_score, smooth_label) * mask)
        return cls_loss