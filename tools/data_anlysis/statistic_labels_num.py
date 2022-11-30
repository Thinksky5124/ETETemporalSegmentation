'''
Author       : Thyssen Wen
Date         : 2022-05-10 10:15:26
LastEditors  : Thyssen Wen
LastEditTime : 2022-11-23 15:59:06
Description  : statistic labels number for dataset
FilePath     : /SVTAS/tools/data_anlysis/statistic_labels_num.py
'''
import argparse
import os
from tqdm import tqdm

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_arguments() -> argparse.Namespace:
    """
    parse all the arguments from command line inteface
    return a list of parsed arguments
    """

    parser = argparse.ArgumentParser(description="convert pred and gt list to images.")
    parser.add_argument(
        "file_list_path",
        type=str,
        help="path to dataset file list",
    )
    parser.add_argument(
        "labels_path",
        type=str,
        help="path to dataset labels",
    )
    parser.add_argument(
        "mapping_txt_path",
        type=str,
        help="path to mapping labels",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="path to output img",
        default="output"
    )

    return parser.parse_args()

def load_action_dict(label_path):
    with open(label_path, "r", encoding='utf-8') as f:
        actions = f.read().split("\n")[:-1]

    id2class_map = dict()
    for a in actions:
        id2class_map[int(a.split(" ")[0])] = a.split(" ")[1]

    return id2class_map

def parse_file_paths(input_path):
    file_ptr = open(input_path, 'r')
    info = file_ptr.read().split('\n')[:-1]
    file_ptr.close()
    return info

def main() -> None:
    args = get_arguments()
    
    file_list = parse_file_paths(args.file_list_path)
    id2class_map = load_action_dict(args.mapping_txt_path)

    num_dict = {}
    total_frame_cnt = {}
    duration_list = []

    for file_name in tqdm(file_list, desc="label count"):
        video_name = file_name.split('.')[0]
        label_path = os.path.join(args.labels_path, video_name + '.txt')
        file_ptr = open(label_path, 'r')
        content = file_ptr.read().split('\n')[:-1]

        # save action duration
        boundary_index_list = [0]
        before_action_name = content[0]
        for index in range(1, len(content)):
            if before_action_name != content[index]:
                boundary_index_list.append(index)
                before_action_name = content[index]
        boundary_index_list.append(len(content) - 1)
        for index in range(len(boundary_index_list) - 1):
            start_frame = float(boundary_index_list[index])
            end_frame = float(boundary_index_list[index + 1] - 1)
            duration_list.append(end_frame - start_frame)

        count_dict = pd.value_counts(content)

        for key, value in count_dict.items():
            if key not in num_dict.keys():
                num_dict[key] = value
                total_frame_cnt[key] = len(content)
            else:
                num_dict[key] = num_dict[key] + value
                total_frame_cnt[key] = total_frame_cnt[key] + len(content)
    
    num_duraction = np.array(duration_list)
    
    plt.hist(num_duraction, bins=100, density = True, range=(0, 400))
    plt.vlines(64, 0, 0.008, color="red")
    plt.title('hist for action duration')
    plt.xlabel("Frame duration")
    plt.ylabel('Density')
    plt.savefig(os.path.join(args.output_dir, "action_duration_count.png"), bbox_inches='tight', dpi=500)
    plt.close()
    
    print(num_dict)

    names = list(num_dict.keys())
    x = range(len(names))
    y = list(num_dict.values())
    plt.bar(x, y)
    plt.xticks(x, names, rotation=90)
    plt.title('Categories of statistical')
    plt.xlabel("Labels' name")
    plt.ylabel('Number')
    plt.xticks(fontsize=5)
    plt.savefig(os.path.join(args.output_dir, "labels_count.png"), bbox_inches='tight', dpi=500)
    plt.close()

    weights_dict = {}
    # crossentropy weight compute by median frequency balancing
    for key, name in id2class_map.items():
        weights_dict[key] = num_dict[name] / total_frame_cnt[name]
    

    out_txt_file_path = os.path.join(args.output_dir, "weights.txt")
    f = open(out_txt_file_path, "w", encoding='utf-8')
    for key, action_wights in weights_dict.items():
        str_str = str(key) + " " + str(action_wights) + "\n"
        f.write(str_str)
    f.close()


if __name__ == "__main__":
    main()