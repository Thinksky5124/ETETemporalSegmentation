'''
Author       : Thyssen Wen
Date         : 2022-11-04 19:50:40
LastEditors  : Thyssen Wen
LastEditTime : 2022-12-16 13:37:16
Description  : file content
FilePath     : /SVTAS/config/svtas/feature/asformer_gtea.py
'''
_base_ = [
    '../../_base_/schedules/optimizer/adam.py', '../../_base_/schedules/lr/liner_step_50e.py',
    '../../_base_/models/temporal_action_segmentation/asformer.py',
    '../../_base_/default_runtime.py', '../../_base_/collater/stream_compose.py',
    '../../_base_/dataset/gtea/gtea_stream_feature.py'
]

split = 1
num_classes = 11
sample_rate = 1
ignore_index = -100
epochs = 50
clip_seg_num = 256
sliding_window = clip_seg_num * sample_rate
dim = 1280
model_name = "Stream_ASFormer_512x1_gtea_split" + str(split)

MODEL = dict(
    head = dict(
        num_decoders = 3,
        num_layers = 10,
        r1 = 2,
        r2 = 2,
        num_f_maps = 64,
        input_dim = dim,
        channel_masking_rate = 0.5,
        num_classes = num_classes,
        sample_rate = sample_rate
    ),
    loss = dict(
        num_classes = num_classes,
        sample_rate = sample_rate,
        ignore_index = ignore_index
    )
)

POSTPRECESSING = dict(
    name = "StreamScorePostProcessing",
    sliding_window = sliding_window,
    ignore_index = ignore_index
)

DATASET = dict(
    temporal_clip_batch_size = 3,
    video_batch_size = 2,
    num_workers = 2,
    train = dict(
        file_path = "./data/gtea/splits/train.split" + str(split) + ".bundle",
        # feature_path = './data/gtea/raw_features',
        sliding_window = sliding_window,
        # flow_feature_path = "./data/gtea/flow_features"
    ),
    test = dict(
        file_path = "./data/gtea/splits/test.split" + str(split) + ".bundle",
        # feature_path = './data/gtea/raw_features',
        sliding_window = sliding_window,
        # flow_feature_path = "./data/gtea/flow_features"
    )
)

LRSCHEDULER = dict(
    step_size = [epochs]
)

PIPELINE = dict(
    train = dict(
        name = "BasePipline",
        decode = dict(
            name='FeatureDecoder',
            backend=dict(
                    name='NPYContainer',
                    is_transpose=False,
                    temporal_dim=-1,
                    revesive_name=[(r'(mp4|avi)', 'npy')]
                 )
        ),
        sample = dict(
            name = "FeatureStreamSampler",
            is_train = True,
            sample_rate_dict={"feature":sample_rate, "labels":sample_rate},
            clip_seg_num_dict={"feature":clip_seg_num, "labels":clip_seg_num},
            sliding_window_dict={"feature":sliding_window, "labels":sliding_window},
            sample_add_key_pair={"frames":"feature"},
            feature_dim_dict={"feature":dim},
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "FeatureStreamTransform",
            transform_dict = dict(
                feature = [dict(XToTensor = None)]
            )
        )
    ),
    test = dict(
        name = "BasePipline",
        decode = dict(
            name='FeatureDecoder',
            backend=dict(
                    name='NPYContainer',
                    is_transpose=False,
                    temporal_dim=-1,
                    revesive_name=[(r'(mp4|avi)', 'npy')]
                 )
        ),
        sample = dict(
            name = "FeatureStreamSampler",
            is_train = False,
            sample_rate_dict={"feature":sample_rate, "labels":sample_rate},
            clip_seg_num_dict={"feature":clip_seg_num, "labels":clip_seg_num},
            sliding_window_dict={"feature":sliding_window, "labels":sliding_window},
            sample_add_key_pair={"frames":"feature"},
            feature_dim_dict={"feature":dim},
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "FeatureStreamTransform",
            transform_dict = dict(
                feature = [dict(XToTensor = None)]
            )
        )
    )
)