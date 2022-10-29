'''
Author: Thyssen Wen
Date: 2022-04-27 16:24:59
LastEditors  : Thyssen Wen
LastEditTime : 2022-10-28 20:11:22
Description: recorder construct function
FilePath     : /SVTAS/svtas/utils/recorder.py
'''
from .logger import AverageMeter

def build_recod(architecture_type, mode):
    assert mode in ["train", "validation", "test"]
    if architecture_type in ["StreamSegmentation2DWithNeck"]:
        if mode == "train":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                    'reader_time': AverageMeter('reader_time', '.5f'),
                    'loss': AverageMeter('loss', '7.5f'),
                    'lr': AverageMeter('lr', 'f', need_avg=False),
                    'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                    'Acc': AverageMeter("Acc", '.5f'),
                    'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                    'backbone_loss': AverageMeter("backbone_loss", '.5f'),
                    'neck_loss': AverageMeter("neck_loss", '.5f'),
                    'head_loss': AverageMeter("head_loss", '.5f')
                    }
        elif mode == "validation":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                   'reader_time': AverageMeter('reader_time', '.5f'),
                   'loss': AverageMeter('loss', '7.5f'),
                   'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                   'Acc': AverageMeter("Acc", '.5f'),
                   'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                   'backbone_loss': AverageMeter("backbone_loss", '.5f'),
                   'neck_loss': AverageMeter("neck_loss", '.5f'),
                   'head_loss': AverageMeter("head_loss", '.5f')
                  }
    elif architecture_type in ["StreamSegmentation2DWithBackbone", "MulModStreamSegmentation",
                "StreamSegmentation3DWithBackbone"]:
        if mode == "train":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                    'reader_time': AverageMeter('reader_time', '.5f'),
                    'loss': AverageMeter('loss', '7.5f'),
                    'lr': AverageMeter('lr', 'f', need_avg=False),
                    'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                    'Acc': AverageMeter("Acc", '.5f'),
                    'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                    'backbone_loss': AverageMeter("backbone_loss", '.5f'),
                    'head_loss': AverageMeter("head_loss", '.5f')
                    }
        elif mode == "validation":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                   'reader_time': AverageMeter('reader_time', '.5f'),
                   'loss': AverageMeter('loss', '7.5f'),
                   'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                   'Acc': AverageMeter("Acc", '.5f'),
                   'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                   'backbone_loss': AverageMeter("backbone_loss", '.5f'),
                   'head_loss': AverageMeter("head_loss", '.5f')
                  }
    elif architecture_type in ["FeatureSegmentation", "Recognition2D", "Recognition3D",
                                "StreamSegmentation3D", "StreamSegmentation2D", "Transeger",
                                "Segmentation2D", "Segmentation3D"]:
        if mode == "train":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                    'reader_time': AverageMeter('reader_time', '.5f'),
                    'loss': AverageMeter('loss', '7.5f'),
                    'lr': AverageMeter('lr', 'f', need_avg=False),
                    'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                    'Acc': AverageMeter("Acc", '.5f'),
                    'Seg_Acc': AverageMeter("Seg_Acc", '.5f')
                    }
        elif mode == "validation":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                   'reader_time': AverageMeter('reader_time', '.5f'),
                   'loss': AverageMeter('loss', '7.5f'),
                   'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                   'Acc': AverageMeter("Acc", '.5f'),
                   'Seg_Acc': AverageMeter("Seg_Acc", '.5f')
                  }
    elif architecture_type in ["SegmentationCLIP"]:
        if mode == "train":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                    'reader_time': AverageMeter('reader_time', '.5f'),
                    'loss': AverageMeter('loss', '7.5f'),
                    'lr': AverageMeter('lr', 'f', need_avg=False),
                    'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                    'Acc': AverageMeter("Acc", '.5f'),
                    'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                    'img_seg_loss': AverageMeter("img_seg_loss", '.5f'),
                    'clip_loss': AverageMeter("clip_loss", '.5f'),
                    }
        elif mode == "validation":
            return {'batch_time': AverageMeter('batch_cost', '.5f'),
                   'reader_time': AverageMeter('reader_time', '.5f'),
                   'loss': AverageMeter('loss', '7.5f'),
                   'F1@0.5': AverageMeter("F1@0.50", '.5f'),
                   'Acc': AverageMeter("Acc", '.5f'),
                   'Seg_Acc': AverageMeter("Seg_Acc", '.5f'),
                   'img_seg_loss': AverageMeter("img_seg_loss", '.5f'),
                   'clip_loss': AverageMeter("clip_loss", '.5f'),
                  }
    else:
        raise NotImplementedError