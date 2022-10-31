'''
Author       : Thyssen Wen
Date         : 2022-10-28 10 = 59 = 31
LastEditors  : Thyssen Wen
LastEditTime : 2022-10-28 14:15:02
Description  : SLViT
FilePath     : /SVTAS/config/_base_/models/image_classification/slvit.py
'''
MODEL = dict(
    architecture = "Recognition2D",
    backbone = dict(
        name = "SLViT",
        image_size = 224,
        patch_size = 32,
        depth = 4,
        heads = 12,
        mlp_dim = 1024,
        dropout = 0.3,
        emb_dropout = 0.3,
    ),
    neck = None,
    head = dict(
        name = "TimeSformerHead",
        num_classes = 11,
        clip_seg_num = 8,
        sample_rate = 4,
        in_channels = 1024,
    ),
    loss = dict(
        name = "RecognitionSegmentationLoss",
        label_mode = "hard",
        num_classes = 11,
        sample_rate = 4,
        loss_weight = 1.0,
        ignore_index = -100
    )
)