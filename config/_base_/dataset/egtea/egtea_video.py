'''
Author       : Thyssen Wen
Date         : 2022-10-28 14:26:33
LastEditors  : Thyssen Wen
LastEditTime : 2022-10-31 09:49:48
Description  : EGTEA dataset Config
FilePath     : /SVTAS/config/_base_/dataset/egtea/egtea_video.py
'''
DATASET = dict(
    temporal_clip_batch_size = 3,
    video_batch_size = 1,
    num_workers = 2,
    train = dict(
        name = "RawFrameSegmentationDataset",
        data_prefix = "./",
        file_path = "./data/egtea/splits/train_split1.txt",
        videos_path = "./data/egtea/Videos",
        gt_path = "./data/egtea/groundTruth",
        actions_map_file_path = "./data/egtea/mapping.txt",
        dataset_type = "egtea"
    ),
    test = dict(
        name = "RawFrameSegmentationDataset",
        data_prefix = "./",
        file_path = "./data/egtea/splits/test_split1.txt",
        videos_path = "./data/egtea/Videos",
        gt_path = "./data/egtea/groundTruth",
        actions_map_file_path = "./data/egtea/mapping.txt",
        dataset_type = "egtea"
    )
)

METRIC = dict(
    name = "TASegmentationMetric",
    overlap = [.1, .25, .5],
    actions_map_file_path = "./data/egtea/mapping.txt",
    file_output = False,
    score_output = False
)