'''
Author: Thyssen Wen
Date: 2022-04-28 19:46:22
LastEditors  : Thyssen Wen
LastEditTime : 2022-05-10 20:00:46
Description: 3D TCN model
FilePath     : /ETESVS/model/heads/tcn_3d_head.py
'''
from dataclasses import dataclass
import torch
import copy
import torch.nn as nn
import torch.nn.functional as F
from mmcv.cnn import constant_init, kaiming_init, xavier_init

from ..builder import HEADS

@HEADS.register()
class TCN3DHead(nn.Module):
    def __init__(self,
                 num_classes,
                 num_layers=4,
                 sample_rate=4,
                 sliding_window=60,
                 seg_in_channels=2048,
                 num_f_maps=64):
        super(TCN3DHead, self).__init__()
        self.seg_in_channels = seg_in_channels
        self.num_f_maps = num_f_maps
        self.num_classes = num_classes
        self.sample_rate = sample_rate
        self.num_layers = num_layers
        if sample_rate % 2 != 0:
            raise NotImplementedError

        self.conv_1x1 = nn.Conv3d(seg_in_channels, num_f_maps, (1, 1, 1))
        self.layers = nn.ModuleList([copy.deepcopy(DilatedResidual3DLayer(2 ** i, num_f_maps, num_f_maps)) for i in range(num_layers)])
        self.head_avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.conv_out = nn.Conv1d(num_f_maps, num_classes, 1)

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                xavier_init(m)
            elif isinstance(m, (nn.BatchNorm3d, nn.GroupNorm)):
                constant_init(m, 1)

    def _clear_memory_buffer(self):
        # self.seg_conv._clear_memory_buffer()
        pass

    def forward(self, seg_feature, mask):
        # segmentation branch
        # seg_feature [N, num_segs, 1280, 7, 7]
        out = self.conv_1x1(seg_feature)
        for layer in self.layers:
            out = layer(out, mask[:, :, ::self.sample_rate])
        
        out = torch.permute(out, dims=[0, 2, 1, 3, 4])
        # seg_feature [N, num_segs, 1280, 7, 7]
        out = torch.reshape(out, shape=[-1] + list(out.shape[-3:]))
        # seg_feature_pool.shape = [N * num_segs, 1280, 1, 1]
        out = self.head_avgpool(out)

        # seg_feature_pool.shape = [N, num_segs, 1280, 1, 1]
        out = torch.reshape(out, shape=[-1, seg_feature.shape[2]] + list(out.shape[-3:]))

        # segmentation feature branch
        # [N, 2048, num_segs]
        out = out.squeeze(-1).squeeze(-1).transpose(1, 2)

        out = self.conv_out(out) * mask[:, 0:1, ::self.sample_rate]

        outputs = out.unsqueeze(0)
        outputs = F.interpolate(
            input=outputs,
            scale_factor=[1, self.sample_rate],
            mode="nearest")
        return outputs


class DilatedResidual3DLayer(nn.Module):
    def __init__(self, dilation, in_channels, out_channels):
        super(DilatedResidual3DLayer, self).__init__()
        self.conv_dilated = nn.Conv3d(in_channels, out_channels, (3,3,3), stride=(1, 1, 1), padding=(dilation, dilation, dilation), dilation=(dilation, dilation, dilation))
        self.conv_1x1 = nn.Conv3d(out_channels, out_channels, (1, 1, 1))
        self.norm = nn.BatchNorm3d(out_channels)

    def forward(self, x, mask):
        # !
        out = F.leaky_relu(self.conv_dilated(x))
        # !
        # out = F.relu(self.conv_dilated(x))
        out = self.conv_1x1(out)
        out = self.norm(out)
        return (x + out) * mask[:, 0:1, :].unsqueeze(-1).unsqueeze(-1)