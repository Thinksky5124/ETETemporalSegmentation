'''
Author       : Thyssen Wen
Date         : 2023-02-18 19:31:19
LastEditors  : Thyssen Wen
LastEditTime : 2023-02-18 19:45:59
Description  : file content
FilePath     : /SVTAS/config/extract/extract_feature/swin_v2_rgb_gtea.py
'''
_base_ = [
    '../../_base_/collater/stream_compose.py'
]

sample_rate = 1
ignore_index = -100
sliding_window = 64
clip_seg_num = 64
output_dir_name = 'extract_features'

MODEL = dict(
    architecture = "Recognition2D",
    backbone = dict(
        name = "SwinTransformerV2",
        pretrained = "./data/checkpoint/swinv2_tiny_patch4_window8_256.pth",
        img_size=256,
        in_chans=3,
        embed_dim=96,
        depths=[2, 2, 6, 2],
        num_heads=[3, 6, 12, 24],
        window_size=8,
        drop_path_rate=0.2,
    ),
    neck = None,
    head = dict(
        name = "FeatureExtractHead",
        in_channels = 1024,
        input_seg_num = clip_seg_num,
        output_seg_num = clip_seg_num,
        sample_rate = sample_rate,
        pool_space = True,
        in_format = "N*T,C,L",
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
    video_batch_size = 1,
    num_workers = 2,
    config = dict(
        name = "RawFrameStreamSegmentationDataset",
        data_prefix = "./",
        file_path = "./data/gtea/splits/all_files.txt",
        videos_path = "./data/gtea/Videos",
        gt_path = "./data/gtea/groundTruth",
        actions_map_file_path = "./data/gtea/mapping.txt",
        dataset_type = "gtea",
        train_mode = False,
        sliding_window = sliding_window
    )
)

PIPELINE = dict(
    name = "BaseDatasetPipline",
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
            dict(CenterCrop = dict(size = 256)),
            dict(PILToTensor = None),
            dict(ToFloat = None),
            dict(Normalize = dict(
                mean = [140.39158961711036, 108.18022223151027, 45.72351736766547],
                std = [33.94421369129452, 35.93603536756186, 31.508484434367805]
            ))]
        )
    )
)