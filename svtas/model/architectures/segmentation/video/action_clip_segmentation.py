'''
Author       : Thyssen Wen
Date         : 2022-10-30 19:21:00
LastEditors  : Thyssen Wen
LastEditTime : 2022-10-30 19:24:33
Description  : file content
FilePath     : /SVTAS/svtas/model/architectures/segmentation/video/action_clip_segmentation.py
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Union
from mmcv.runner import load_state_dict
from collections import OrderedDict
import re

from .....utils.logger import get_logger

from ....builder import build_backbone
from ....builder import build_neck
from ....builder import build_head

from ....builder import ARCHITECTURE

@ARCHITECTURE.register()
class ActionCLIPSegmentation(nn.Module):
    def __init__(self,
                 pretrained=None,
                 image_prompt=None,
                 text_prompt=None,
                 fusion_neck=None,
                 head=None,
                 loss=None,
                 aligin_head=None,
                 is_feature_extract=False):
        super().__init__()
        self.pretrained = pretrained
        self.is_feature_extract = is_feature_extract
        if image_prompt is not None:
            self.image_prompt = build_backbone(image_prompt)
        else:
            self.image_prompt = None
            
        if text_prompt is not None:
            self.text_prompt = build_backbone(text_prompt)
        else:
            self.neck = None

        if fusion_neck is not None:
            self.fusion_neck = build_neck(fusion_neck)
        else:
            self.fusion_neck = None
        
        if head is not None:
            self.head = build_head(head)
            self.sample_rate = head.sample_rate
        else:
            self.head = None
            self.sample_rate = loss.sample_rate
        
        if aligin_head is not None:
            self.aligin_head = build_head(aligin_head)
        else:
            self.aligin_head = None
    
        self.init_weights()

    def init_weights(self):
        if isinstance(self.pretrained, str):
            def revise_keys_fn(state_dict, revise_keys=[(r'module.', r'')]):
                # strip prefix of state_dict
                metadata = getattr(state_dict, '_metadata', OrderedDict())
                for p, r in revise_keys:
                    state_dict = OrderedDict(
                        {re.sub(p, r, k): v
                        for k, v in state_dict.items()})
                # Keep metadata in state_dict
                state_dict._metadata = metadata
                return state_dict

            logger  = get_logger("SVTAS")
            checkpoint = torch.load(self.pretrained)
            load_state_dict(self.image_prompt, checkpoint['model_state_dict'], strict=False, logger=logger)
            revise_state_dict = revise_keys_fn(checkpoint['fusion_model_state_dict'])
            load_state_dict(self.fusion_neck, revise_state_dict, strict=False, logger=logger)
        else:
            if self.image_prompt is not None:
                self.image_prompt.init_weights(child_model=False, revise_keys=[(r'backbone.', r'')])
            if self.text_prompt is not None:
                self.text_prompt.init_weights()
            if self.fusion_neck is not None:
                self.fusion_neck.init_weights()
            if self.head is not None:
                self.head.init_weights()
            if self.aligin_head is not None:
                self.aligin_head.init_weights()
    
    def _clear_memory_buffer(self):
        if self.image_prompt is not None:
            self.image_prompt._clear_memory_buffer()
        if self.text_prompt is not None:
            self.text_prompt._clear_memory_buffer()
        if self.fusion_neck is not None:
            self.fusion_neck._clear_memory_buffer()
        if self.head is not None:
            self.head._clear_memory_buffer()
        if self.aligin_head is not None:
            self.aligin_head._clear_memory_buffer()

    def forward(self, input_data):

        masks = input_data['masks']
        imgs = input_data['imgs']
        labels = input_data['labels']
        
        # masks.shape=[N,T]
        masks = F.adaptive_max_pool1d(masks, imgs.shape[1], return_indices=False)
        masks = masks.unsqueeze(1)

        # x.shape=[N,T,C,H,W], for most commonly case
        b, t, _, _, _ = imgs.shape
        imgs = torch.reshape(imgs, [-1] + list(imgs.shape[2:]))
        # x [N * T, C, H, W]

        if self.text_prompt is not None and self.is_feature_extract is False:
            texts = self.text_prompt(labels, masks)
            text_embedding = self.image_prompt.encode_text(texts)
        else:
            text_embedding = None

        if self.image_prompt is not None:
             # masks.shape [N * T, 1, 1, 1]
            imgs_masks = masks[:, :, ::self.sample_rate].permute([0, 2, 1])
            image_embedding = self.image_prompt.encode_image(imgs)
            image_embedding = image_embedding.view(b, t, -1) * imgs_masks
        else:
            image_embedding = imgs

        # step 5 segmentation
        # seg_feature [N, H_dim, T]
        # cls_feature [N, F_dim, T]
        if self.fusion_neck is not None:
            neck_feature = self.fusion_neck(image_embedding, masks)
        else:
            neck_feature = image_embedding
        
        if self.head is not None:
            head_score = self.head(neck_feature, masks)
        else:
            head_score = neck_feature
        
        if self.aligin_head is not None:
            head_score = self.aligin_head(head_score, input_data['labels'], masks)
        else:
            head_score = head_score
            
        return image_embedding, text_embedding, head_score