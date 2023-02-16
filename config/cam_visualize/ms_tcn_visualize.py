'''
Author       : Thyssen Wen
Date         : 2022-12-23 20:48:59
LastEditors  : Thyssen Wen
LastEditTime : 2022-12-25 11:51:26
Description  : file content
FilePath     : /SVTAS/config/cam_visualize/ms_tcn_visualize.py
'''
_base_ = [
    '../_base_/models/temporal_action_segmentation/ms_tcn.py',
    '../_base_/default_runtime.py', '../_base_/collater/batch_compose.py'
]

split = 1
num_classes = 11
sample_rate = 1
ignore_index = -100
epochs = 50
batch_size = 1

MODEL = dict(
    head = dict(
        dim = 512,
        num_classes = num_classes,
        sample_rate = sample_rate
    ),
    loss = dict(
        num_classes = num_classes,
        sample_rate = sample_rate,
        ignore_index = ignore_index
    )
)

PRETRAINED = "./output/MSTCN_gtea_split1/MSTCN_gtea_split1_best.pt"

VISUALIZE = dict(
    layer_name = ["model.head.stages.2.layers.9.conv_1x1"],
    batch_size = batch_size,
    sample_rate = sample_rate,
    ignore_index = ignore_index,
    data_key = "feature",
    return_targets_name = dict(
        TemporalSegmentationTarget = dict(select_frame_idx_list=[0,1,2,3,4])
        # CategorySegmentationTarget = dict(category=0)
    ),
    reshape_transform = "NCT",
    label_path = "./data/gtea/mapping.txt",
    match_fn_name = "feature_batch_match_fn"
)

POSTPRECESSING = dict(
    name = "CAMImagePostProcessing",
    ignore_index = ignore_index,
    sample_rate = sample_rate,
    output_frame_size = [720, 404],
    need_label = True
)

DATASET = dict(
    temporal_clip_batch_size = batch_size,
    video_batch_size = batch_size,
    num_workers = 2,
    config = dict(
        name = "CAMFeatureSegmentationDataset",
        data_prefix = "./",
        file_path = "./data/gtea/splits/train.split1.bundle",
        feature_path = "./data/gtea/features",
        gt_path = "./data/gtea/groundTruth",
        actions_map_file_path = "./data/gtea/mapping.txt",
        dataset_type = "gtea"
    ),
)

PIPELINE = dict(
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
        name = "FeatureSampler",
        is_train = False,
        sample_rate_dict={ "feature": sample_rate,"labels": sample_rate },
        sample_add_key_pair={ "frames": "feature" },
        sample_mode = "uniform",
    ),
    transform = dict(
        name = "FeatureRawStoreTransform",
        transform_dict = dict(
            feature = [dict(XToTensor = None)]
        )
    )
)