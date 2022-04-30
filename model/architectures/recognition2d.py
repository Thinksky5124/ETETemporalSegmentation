'''
Author: Thyssen Wen
Date: 2022-04-29 10:59:22
LastEditors: Thyssen Wen
LastEditTime: 2022-04-29 15:08:52
Description: Action Recognition 2D framework
FilePath: /ETESVS/model/architectures/recognition2d.py
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
from mmcv.runner import load_checkpoint

from utils.logger import get_logger

from ..builder import build_backbone
from ..builder import build_neck
from ..builder import build_head

from ..builder import ARCHITECTURE

@ARCHITECTURE.register()
class Recognition2D(nn.Module):
    def __init__(self,
                 backbone=None,
                 neck=None,
                 head=None,
                 loss=None):
        super().__init__()
        if backbone is not None:
            self.backbone = build_backbone(backbone)
        else:
            self.backbone = None
            
        if neck is not None:
            self.neck = build_neck(neck)
        else:
            self.neck = None

        self.head = build_head(head)
        
        self.init_weights()

        self.sample_rate = loss.sample_rate

    def init_weights(self):
        if self.backbone is not None:
            self.backbone.init_weights(child_model=True)
        if self.neck is not None:
            self.neck.init_weights()
        self.head.init_weights()
        
        if isinstance(self.backbone.pretrained, str):
            logger = logger = get_logger("ETESVS")
            load_checkpoint(self, self.backbone.pretrained, strict=False, logger=logger)
    
    def _clear_memory_buffer(self):
        # self.backbone._clear_memory_buffer()
        # self.neck._clear_memory_buffer()
        # self.head._clear_memory_buffer()
        pass

    def forward(self, imgs, masks, idx=None):
        # masks.shape=[N,T]
        masks = masks.unsqueeze(1)

        # x.shape=[N,T,C,H,W], for most commonly case
        imgs = torch.reshape(imgs, [-1] + list(imgs.shape[2:]))
        # x [N * T, C, H, W]

        if self.backbone is not None:
             # masks.shape [N * T, 1, 1, 1]
            backbone_masks = torch.reshape(masks[:, :, ::self.sample_rate], [-1]).unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
            feature = self.backbone(imgs, backbone_masks)
        else:
            feature = imgs

        # feature [N * T , F_dim, 7, 7]
        # step 3 extract memory feature
        if self.neck is not None:
            seg_feature, backbone_score, neck_score = self.neck(
                feature, masks[:, :, ::self.sample_rate])
            
        else:
            seg_feature = feature
            backbone_score = None
            neck_score = None

        # step 5 segmentation
        # seg_feature [N, H_dim, T]
        # cls_feature [N, F_dim, T]
        if self.head is not None:
            head_score = self.head(seg_feature, masks[:, :, ::self.sample_rate])
        else:
            head_score = None
        # head_score [stage_num, N, C, T // sample_rate]
        head_score = head_score.unsqueeze(0)
        # head_score [stage_num, N, C, T]
        head_score = F.interpolate(
            input=head_score,
            scale_factor=[1, self.sample_rate],
            mode="nearest")
        return head_score