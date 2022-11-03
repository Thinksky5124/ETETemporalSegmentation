'''
Author       : Thyssen Wen
Date         : 2022-10-28 19:51:25
LastEditors  : Thyssen Wen
LastEditTime : 2022-11-03 12:57:21
Description  : file content
FilePath     : /SVTAS/svtas/model/architectures/segmentation/feature/__init__.py
'''
from .feature_segmentation import FeatureSegmentation
from .feature_segmentation3d import FeatureSegmentation3D

__all__ = [
    'FeatureSegmentation', 'FeatureSegmentation3D'
]