'''
Author       : Thyssen Wen
Date         : 2022-10-28 14:53:59
LastEditors  : Thyssen Wen
LastEditTime : 2022-10-28 14:54:01
Description  : file content
FilePath     : /SVTAS/config/_base_/pipline/feature_pipline.py
'''
PIPELINE = dict(
    train = dict(
        name = "BasePipline",
        decode = dict(
            name = "FeatureDecoder",
            backend = "numpy"
        ),
        sample = dict(
            name = "FeatureSampler",
            is_train = True,
            sample_rate = 1,
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "FeatureStreamTransform",
            transform_list = [
                dict(FeatureToTensor = None)
            ]
        )
    ),
    test = dict(
        name = "BasePipline",
        decode = dict(
            name = "FeatureDecoder",
            backend = "numpy"
        ),
        sample = dict(
            name = "FeatureSampler",
            is_train = False,
            sample_rate = 1,
            sample_mode = "uniform"
        ),
        transform = dict(
            name = "FeatureStreamTransform",
            transform_list = [
                dict(FeatureToTensor = None)
            ]
        )
    )
)