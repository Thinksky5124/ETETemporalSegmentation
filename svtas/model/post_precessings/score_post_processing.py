'''
Author       : Thyssen Wen
Date         : 2022-05-26 18:50:50
LastEditors  : Thyssen Wen
LastEditTime : 2022-11-17 14:18:08
Description  : Score Post precessing Module
FilePath     : /SVTAS/svtas/model/post_precessings/score_post_processing.py
'''
import numpy as np
import torch
from ..builder import POSTPRECESSING

@POSTPRECESSING.register()
class ScorePostProcessing():
    def __init__(self,
                 ignore_index=-100):
        self.ignore_index = ignore_index
        self.init_flag = False
        self.epls = 1e-10
    
    def init_scores(self, sliding_num, batch_size):
        self.pred_scores = None
        self.video_gt = None
        self.init_flag = True

    def update(self, seg_scores, gt, idx):
        # seg_scores [stage_num N C T]
        # gt [N T]
        with torch.no_grad():
            if torch.is_tensor(seg_scores):
                self.pred_scores = seg_scores[-1, :].detach().cpu().numpy().copy()
                self.video_gt = gt.detach().cpu().numpy().copy()
                pred = np.argmax(seg_scores[-1, :].detach().cpu().numpy(), axis=-2)
                acc = np.mean((np.sum(pred == gt.detach().cpu().numpy(), axis=1) / (np.sum(gt.detach().cpu().numpy() != self.ignore_index, axis=1) + self.epls)))
            else:
                self.pred_scores = seg_scores[-1, :].copy()
                self.video_gt = gt.copy()
                pred = np.argmax(seg_scores[-1, :], axis=-2)
                acc = np.mean((np.sum(pred == gt, axis=1) / (np.sum(gt != self.ignore_index, axis=1) + self.epls)))
        return acc

    def output(self):
        pred_score_list = []
        pred_cls_list = []
        ground_truth_list = []

        for bs in range(self.pred_scores.shape[0]):
            index = np.where(self.video_gt[bs, :] == self.ignore_index)
            ignore_start = min(list(index[0]) + [self.pred_scores[bs].shape[-1]])
            predicted = np.argmax(self.pred_scores[bs, :, :ignore_start], axis=0)
            predicted = predicted.squeeze()
            pred_cls_list.append(predicted.copy())
            pred_score_list.append(self.pred_scores[bs, :, :ignore_start].copy())
            ground_truth_list.append(self.video_gt[bs, :ignore_start].copy())

        return pred_score_list, pred_cls_list, ground_truth_list