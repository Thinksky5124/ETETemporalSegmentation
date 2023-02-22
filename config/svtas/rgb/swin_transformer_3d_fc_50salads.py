'''
Author       : Thyssen Wen
Date         : 2022-12-18 19:04:09
LastEditors  : Thyssen Wen
LastEditTime : 2023-02-22 10:09:43
Description  : file content
FilePath     : /SVTAS/config/svtas/rgb/swin_transformer_3d_fc_50salads.py
'''
_base_ = [
    '../../_base_/schedules/optimizer/adamw.py', '../../_base_/schedules/lr/liner_step_50e.py',
    '../../_base_/models/action_recognition/swin_transformer.py',
    '../../_base_/default_runtime.py', '../../_base_/collater/stream_compose.py',
    '../../_base_/dataset/50salads/50salads_stream_video.py'
]
from svtas.model.backbones.video.swin_transformer_3d import Mlp
from svtas.utils.sbp import Swin3DMLPMaskMappingFunctor

num_classes = 19
sample_rate = 4
clip_seg_num = 64
ignore_index = -100
sliding_window = clip_seg_num * sample_rate
split = 1
batch_size = 1
epochs = 50
log_interval = 10

model_name = "SwinTransformer3D_FC_"+str(clip_seg_num)+"x"+str(sample_rate)+"_50salads_split" + str(split)

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
        patch_norm = True,
        # sbp_build=True,
        # keep_ratio_list=[0.125],
        # sample_dims=[2],
        # grad_mask_mode_lsit=['random'],
        # register_sbp_module_dict={Mlp: Swin3DMLPMaskMappingFunctor(permute_dims=[0, 2, 3, 4, 1])}
    ),
    neck = dict(
        name = "PoolNeck",
        in_channels = 768,
        clip_seg_num = clip_seg_num // 2,
        need_pool = True
    ),
    head = dict(
        name = "FCHead",
        num_classes = num_classes,
        sample_rate = sample_rate * 2,
        clip_seg_num = clip_seg_num // 2,
        drop_ratio=0.5,
        in_channels=768
    ),
    loss = dict(
        name = "SegmentationLoss",
        num_classes = num_classes,
        sample_rate = sample_rate * 2,
        smooth_weight = 0.0,
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

OPTIMIZER = dict(
    learning_rate = 0.00001,
    weight_decay = 1e-4,
    betas = (0.9, 0.999),
    need_grad_accumulate = False,
    finetuning_scale_factor=0.5,
    no_decay_key = [],
    finetuning_key = [],
    freeze_key = [],
)

DATASET = dict(
    temporal_clip_batch_size = 3,
    video_batch_size = batch_size,
    num_workers = 2,
    train = dict(
        file_path = "./data/50salads/splits/train.split" + str(split) + ".bundle",
        sliding_window = sliding_window
    ),
    test = dict(
        file_path = "./data/50salads/splits/train.split" + str(split) + ".bundle",
        sliding_window = sliding_window,
    )
)

PIPELINE = dict(
    train = dict(
        name = "BasePipline",
        decode = dict(
            name="VideoDecoder",
            backend=dict(
                    name='DecordContainer')
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
                dict(RandomCrop = dict(size = 224)),
                dict(RandomHorizontalFlip = None),
                dict(PILToTensor = None),
                dict(ToFloat = None),
                dict(Normalize = dict(
                    mean = [0.5139909998345553 * 255, 0.5117725498677757 * 255, 0.4798814301515671 * 255],
                    std = [0.23608918491478523 * 255, 0.23385714300069754 * 255, 0.23755006337414028* 255]
                ))]
            )
        )
    ),
    test = dict(
        name = "BasePipline",
        decode = dict(
            name="VideoDecoder",
            backend=dict(
                    name='DecordContainer')
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
                    ))]
            )
        )
    )
)