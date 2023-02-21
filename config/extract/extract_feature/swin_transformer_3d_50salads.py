'''
Author       : Thyssen Wen
Date         : 2022-12-22 16:37:36
LastEditors  : Thyssen Wen
LastEditTime : 2023-02-17 15:11:08
Description  : file content
FilePath     : /SVTAS/config/extract/extract_feature/swin_transformer_3d_50salads.py
'''
_base_ = [
    '../../_base_/collater/stream_compose.py'
]

sample_rate = 1
ignore_index = -100
sliding_window = 128
clip_seg_num = 128
output_dir_name = 'extract_features'

MODEL = dict(
    architecture = "Recognition3D",
    backbone = dict(
        name = "SwinTransformer3D",
        pretrained = "./data/checkpoint/swin_tiny_patch244_window877_kinetics400_1k.pth",
        pretrained2d = False,
        patch_size = [2, 4, 4],
        embed_dim = 96,
        depths = [2, 2, 6, 2],
        num_heads = [3, 6, 12, 24],
        window_size = [8,7,7],
        mlp_ratio = 4.,
        qkv_bias = True,
        qk_scale = None,
        drop_rate = 0.,
        attn_drop_rate = 0.,
        drop_path_rate = 0.2,
        patch_norm = True
    ),
    neck = None,
    head = dict(
        name = "FeatureExtractHead",
        in_channels = 768,
        input_seg_num = clip_seg_num // 2,
        output_seg_num = clip_seg_num,
        sample_rate = sample_rate * 2,
        pool_space = True,
        in_format = "N,C,T,H,W",
        out_format = "NCT"
    ),
    loss = None
)

PRETRAINED = None

POSTPRECESSING = dict(
    name = "StreamFeaturePostProcessing",
    sliding_window = sliding_window,
    ignore_index = ignore_index
)

DATASET = dict(
    temporal_clip_batch_size = 3,
    video_batch_size = 2,
    num_workers = 2,
    config = dict(
        name = "RawFrameStreamSegmentationDataset",
        data_prefix = "./",
        file_path = "./data/50salads/splits/all_files.txt",
        videos_path = "./data/50salads/Videos",
        gt_path = "./data/50salads/groundTruth",
        actions_map_file_path = "./data/50salads/mapping.txt",
        dataset_type = "50salads",
        train_mode = False,
        sliding_window = sliding_window
    )
)

PIPELINE = dict(
    name = "BasePipline",
    decode = dict(
        name = "VideoDecoder",
        backend = dict(name="DecordContainer")
    ),
    sample = dict(
        name = "VideoStreamSampler",
        is_train = False,
        sample_rate_dict={"imgs":sample_rate,"labels":sample_rate},
        clip_seg_num_dict={"imgs":clip_seg_num ,"labels":clip_seg_num},
        sliding_window_dict={"imgs":sliding_window,"labels":sliding_window},
        sample_add_key_pair={"frames":"imgs"},
        sample_mode = "uniform"
    ),
    transform = dict(
        name = "VideoTransform",
        transform_dict = dict(
            imgs = [
            dict(ResizeImproved = dict(size = 256)),
            dict(CenterCrop = dict(size = 224)),
            dict(PILToTensor = None),
            dict(ToFloat = None),
            dict(Normalize = dict(
                mean = [0.5139909998345553 * 255, 0.5117725498677757 * 255, 0.4798814301515671 * 255],
                std = [0.23608918491478523 * 255, 0.23385714300069754 * 255, 0.23755006337414028* 255]
            ))
        ])
    )
)