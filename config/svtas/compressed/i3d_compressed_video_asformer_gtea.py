'''
Author       : Thyssen Wen
Date         : 2022-11-05 20:27:29
LastEditors  : Thyssen Wen
LastEditTime : 2022-11-11 15:06:53
Description  : file content
FilePath     : /SVTAS/config/svtas/rgb/i3d_compressed_video_asformer_gtea.py
'''
_base_ = [
    '../../_base_/schedules/optimizer/adam.py', '../../_base_/schedules/lr/liner_step_50e.py',
    '../../_base_/default_runtime.py', '../../_base_/collater/stream_compose.py',
    '../../_base_/dataset/gtea/gtea_stream_compressed_video.py'
]
split = 1
num_classes = 11
sample_rate = 1
gop_size = 16
clip_seg_num = 128
sliding_window = 128

ignore_index = -100
batch_size = 1
epochs = 50
model_name = "I3D_Compressed_Video_Asformer_128x1_gtea_split" + str(split)

MODEL = dict(
    architecture = "MultiModalityStreamSegmentation",
    rgb_backbone = dict(
        name = "I3D",
        pretrained = "./data/checkpoint/i3d_rgb.pt",
        in_channels = 3
    ),
    flow_backbone = dict(
        name = "I3D",
        pretrained = "./data/checkpoint/i3d_flow.pt",
        in_channels = 2
    ),
    neck = dict(
        name = "IPBFusionNeck",
        gop_size = gop_size,
        spatial_expan_mode ='trilinear',
        parse_method ='separate',
        fusion_neck_module = dict(
            name = "PoolNeck",
            num_classes = num_classes,
            in_channels = 2048,
            clip_seg_num = clip_seg_num // 8,
            drop_ratio = 0.5,
            need_pool = True
        )
    ),
    head = dict(
        name = "ASFormer",
        num_decoders = 3,
        num_layers = 10,
        r1 = 2,
        r2 = 2,
        num_f_maps = 64,
        input_dim = 2048,
        channel_masking_rate = 0.5,
        num_classes = num_classes,
        sample_rate = sample_rate * 8
    ),
    loss = dict(
        name = "SegmentationLoss",
        num_classes = num_classes,
        sample_rate = sample_rate,
        smooth_weight = 0.15,
        ignore_index = -100
    )
)

POSTPRECESSING = dict(
    name = "StreamScorePostProcessing",
    sliding_window = sliding_window,
    ignore_index = ignore_index
)

LRSCHEDULER = dict(
    step_size = [epochs]
)

DATASET = dict(
    temporal_clip_batch_size = 3,
    video_batch_size = batch_size,
    num_workers = batch_size * 4,
    train = dict(
        sliding_window = sliding_window,
        need_residual = True,
        need_mvs = True
    ),
    test = dict(
        sliding_window = sliding_window,
        need_residual = True,
        need_mvs = True
    )
)

PIPELINE = dict(
    train = dict(
        name = "BaseDatasetPipline",
        decode = dict(
            name = "VideoDecoder",
            backend=dict(
                    name='PyAVMVExtractor',
                    need_residual=True,
                    need_mvs=True,
                    argument=False)
        ),
        sample = dict(
            name = "VideoStreamSampler",
            is_train = True,
            sample_rate_dict={"imgs":sample_rate * gop_size, "flows":sample_rate, "res":sample_rate, "labels":sample_rate},
            clip_seg_num_dict={"imgs":clip_seg_num // gop_size, "flows":clip_seg_num, "res":clip_seg_num, "labels":clip_seg_num},
            sliding_window_dict={"imgs":sliding_window, "flows":sliding_window, "res":sliding_window, "labels":sliding_window},
            sample_add_key_pair={"frames":"imgs", "flow_frames":"flows", "res_frames":"res"},
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "CompressedVideoStreamTransform",
            rgb = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(RandomCrop = dict(size = 224)),
                dict(RandomHorizontalFlip = None),
                dict(Normalize = dict(
                    mean = [140.39158961711036, 108.18022223151027, 45.72351736766547],
                    std = [33.94421369129452, 35.93603536756186, 31.508484434367805]
                ))
            ],
            flow = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(Clamp = dict(min_val=-20, max_val=20)),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(RandomCrop = dict(size = 224)),
                dict(ScaleTo1_1 = None)
            ],
            res = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(RandomCrop = dict(size = 224)),
                dict(ScaleTo1_1 = None)
            ]
        )
    ),
    test = dict(
        name = "BaseDatasetPipline",
        decode = dict(
            name = "VideoDecoder",
            backend=dict(
                    name='PyAVMVExtractor',
                    need_residual=True,
                    need_mvs=True,
                    argument=False)
        ),
        sample = dict(
            name = "VideoStreamSampler",
            is_train = False,
            sample_rate_dict={"imgs":sample_rate * gop_size, "flows":sample_rate, "res":sample_rate, "labels":sample_rate},
            clip_seg_num_dict={"imgs":clip_seg_num // gop_size, "flows":clip_seg_num, "res":clip_seg_num, "labels":clip_seg_num},
            sliding_window_dict={"imgs":sliding_window, "flows":sliding_window, "res":sliding_window, "labels":sliding_window},
            sample_add_key_pair={"frames":"imgs", "flow_frames":"flows", "res_frames":"res"},
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "CompressedVideoStreamTransform",
            rgb = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(TensorCenterCrop = dict(crop_size = 224)),
                dict(Normalize = dict(
                    mean = [140.39158961711036, 108.18022223151027, 45.72351736766547],
                    std = [33.94421369129452, 35.93603536756186, 31.508484434367805]
                ))
            ],
            flow = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(TensorCenterCrop = dict(crop_size = 224)),
                dict(ScaleTo1_1 = None)
            ],
            res = [
                dict(XToTensor = None),
                dict(ToFloat = None),
                dict(TensorPermute = dict(permute_list = [2, 0, 1])),
                dict(TensorImageResize = dict(size = 256)),
                dict(TensorCenterCrop = dict(crop_size = 224)),
                dict(ScaleTo1_1 = None)
            ]
        )
    )
)
