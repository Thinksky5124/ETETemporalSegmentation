'''
Author       : Thyssen Wen
Date         : 2022-05-18 21:30:25
LastEditors  : Thyssen Wen
LastEditTime : 2022-12-22 15:37:06
Description  : Video Filed model zoom
FilePath     : /SVTAS/svtas/model/backbones/video/__init__.py
'''
from .i3d import I3D
from .mobilenet_v2_tsm import MobileNetV2TSM
from .movinet import MoViNet
from .resnet2plus1d import ResNet2Plus1d
from .predrnn_v2 import PredRNNV2
from .resnet_3d import ResNet3d
from .timesfromer import TimeSformer
from .resnet_tsm import ResNetTSM
from .swin_transformer_3d import SwinTransformer3D
from .vit_3d import ViT3D
from .sample_vit_3d import SampleViT3D
from .mvit import MViT
from .x3d import X3D
from .swin_transformer_tsm import SwinTransformerV2TSM

__all__ = [
    "I3D", "MobileNetV2TSM", "MoViNet", "ResNet2Plus1d", "PredRNNV2", "ResNet3d",
    "TimeSformer", "ResNetTSM", "SwinTransformer3D", "ViT3D", "SampleViT3D",
    "MViT", "X3D", "SwinTransformerV2TSM"
]