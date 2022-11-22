'''
Author: Thyssen Wen
Date: 2022-04-14 15:29:53
LastEditors  : Thyssen Wen
LastEditTime : 2022-11-22 14:09:17
Description: file content
FilePath     : /SVTAS/svtas/model/losses/__init__.py
'''
from .etesvs_loss import ETESVSLoss
from .segmentation_loss import SegmentationLoss, ActionCLIPSegmentationLoss, LSTRSegmentationLoss
from .recognition_segmentation_loss import RecognitionSegmentationLoss
from .recognition_segmentation_loss import SoftLabelRocgnitionLoss
from .steam_segmentation_loss import StreamSegmentationLoss
from .video_prediction_loss import VideoPredictionLoss
from .segmentation_clip_loss import SgementationCLIPLoss, CLIPLoss
from .bridge_prompt_clip_loss import BridgePromptCLIPLoss, BridgePromptCLIPSegmentationLoss
from .lovasz_softmax_loss import LovaszSegmentationLoss
from .dice_loss import DiceSegmentationLoss

__all__ = [
    'ETESVSLoss', 'SegmentationLoss', 'RecognitionSegmentationLoss',
    'StreamSegmentationLoss', 'SoftLabelRocgnitionLoss', 'VideoPredictionLoss',
    'SgementationCLIPLoss', 'CLIPLoss', 'BridgePromptCLIPLoss',
    'BridgePromptCLIPSegmentationLoss', 'ActionCLIPSegmentationLoss',
    'LSTRSegmentationLoss', 'LovaszSegmentationLoss', 'DiceSegmentationLoss'
]