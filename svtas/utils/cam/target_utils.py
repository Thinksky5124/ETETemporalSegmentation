'''
Author       : Thyssen Wen
Date         : 2022-12-23 17:41:24
LastEditors  : Thyssen Wen
LastEditTime : 2022-12-24 18:41:36
Description  : file content
FilePath     : /SVTAS/svtas/utils/cam/target_utils.py
'''
import torch
import numpy as np
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

__all__ = [
    "TemporalSegmentationTarget", "CategorySegmentationTarget"
]
        
class CategorySegmentationTarget:
    def __init__(self, category=None):
        self.category = category
        
    def __call__(self, model_output):
        # model_output [stage_num N C T] -> [stage_num N T C]
        model_output = torch.transpose(model_output, -1, -2)
        if self.category is None:
            target_categories = np.argmax(model_output[-1].cpu().data.numpy(), axis=-1)
            targets = [ClassifierOutputTarget(
                category) for category in target_categories]
            loss = sum([target(output)
                       for target, output in zip(targets, model_output[-1])])
            return loss
        else:
            return model_output[-1, :, self.category]

class TemporalSegmentationTarget:
    def __init__(self, select_frame_idx_list=[]):
        self.select_frame_idx_list = select_frame_idx_list
        
    def __call__(self, model_output):
        # model_output [stage_num N C T] -> [stage_num N T C]
        model_output = torch.transpose(model_output, -1, -2)
        select_output = model_output[-1, :, self.select_frame_idx_list]
        target_categories = np.argmax(select_output.cpu().data.numpy(), axis=-1)
        targets = [ClassifierOutputTarget(
            category) for category in target_categories]
        loss = sum([target(output)
                    for target, output in zip(targets, select_output)])
        return loss