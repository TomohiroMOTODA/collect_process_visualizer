# -*- coding: utf-8 -*-
"""
@file main.py
@brief Main script to load and analyze meta information from JSON files.
This script reads JSON files containing meta information about segments and instructions,
aggregates statistics, and visualizes daily and cumulative data counts.

@author Tomohiro MOTODA
@date 2025-06-10
@version 1.0
@note This script requires the following Python packages:
    - json
    - os
    - datetime
    - statistics
    - glob
    - matplotlib.pyplot

***This script is written assisted by Copilot.***
"""

import json
from datetime import timedelta
import statistics
import glob
import os
import matplotlib.pyplot as plt

def load_metajson(path, is_shown=False):
    # JSONファイルを読み込む
    with open(os.path.join(path), "r") as f:
        data = json.load(f)

    # メタ情報の表示
    if is_shown:
        print("=== Meta Information ===")
        print(f"Bag path        : {data['bag_path']}")
        print(f"HSR ID          : {data['hsr_id']}")
        print(f"Version         : {data['version']}")
        print(f"Location        : {data['location_name']}")
        print(f"Interface       : {data['interface']}")
        print(f"Git Branch      : {data['git_branch']}")
        print(f"Git Hash        : {data['git_hash']}")
        print()

    # 命令の集計
    instructions = [instr[0] for instr in data["instructions"]]
    
    if is_shown:
        print("=== Instructions Summary ===")
        print(f"Total instructions: {len(instructions)}\n")
        for idx, instr in enumerate(instructions):
            print(f"{idx:02d}: {instr}")
        print()

    # セグメント時間の統計
    if is_shown:
        print("=== Segment Time Statistics ===")
    durations = []
    suboptimal_segments = []

    for segment in data["segments"]:
        duration = segment["end_time"] - segment["start_time"]
        durations.append(duration)
        if segment["has_suboptimal"]:
            suboptimal_segments.append(segment)

    # 時間統計
    total_time = sum(durations)
    mean_time = statistics.mean(durations)
    max_time = max(durations)
    min_time = min(durations)

    statics_epi = dict()
    statics_epi["total_time"] = total_time
    statics_epi["total_duration"] = timedelta(seconds=total_time)
    statics_epi["mean_duration"] = mean_time
    statics_epi["max_duration"] = max_time
    statics_epi["min_duration"] = min_time
    statics_epi["total_segments"] = len(durations)
    statics_epi["suboptimal_segments"] = len(suboptimal_segments)

    if is_shown:
        print(f"Total duration : {timedelta(seconds=total_time)} ({total_time:.2f} sec)")
        print(f"Mean duration  : {mean_time:.2f} sec")
        print(f"Max duration   : {max_time:.2f} sec")
        print(f"Min duration   : {min_time:.2f} sec")
        print(f"Total segments : {len(durations)}")
        print(f"Suboptimal segments: {len(suboptimal_segments)}")
        print()

        # サブオプティマルなセグメントの詳細表示
        if suboptimal_segments:
            print("=== Suboptimal Segments ===")
            for s in suboptimal_segments:
                idx = s["instructions_index"]
                dur = s["end_time"] - s["start_time"]
                print(f"- Instruction {idx}: \"{instructions[idx]}\" (Duration: {dur:.2f} sec)")
        else:
            print("No suboptimal segments detected.")

    return statics_epi

def main(data_dir):

    files = glob.glob(os.path.join(data_dir, "*/*.json"), recursive=True)
    statics_all = [] 
    date_counts = {}
    for f in files:
        tmp_data_info = load_metajson(f)
        statics_all.append(tmp_data_info)
        
        # ファイル名から日付を抽出
        date_str = os.path.basename(f).split('_')[0]
        if date_str in date_counts:
            date_counts[date_str] += 1
        else:
            date_counts[date_str] = 1

    # 総和を求める．
    total_duration = 0
    for epi in statics_all:
        total_duration += epi["total_time"]
    print(f"Total duration : {total_duration} (sec)")
    print(f"Total duration : {total_duration /3600.} (hours)")

    # 日付ごとのデータ件数を棒グラフで表示
    dates = sorted(date_counts.keys())
    counts = [date_counts[date] for date in dates]
    cumulative_counts = [sum(counts[:i+1]) for i in range(len(counts))]

    plt.figure(figsize=(10, 6))
    plt.bar(dates, counts, color='blue', label='Daily Count')
    plt.plot(dates, cumulative_counts, color='red', marker='o', label='Cumulative Count')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title('Daily Data Count and Cumulative Count')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('./data/data_count_graph.png')
    plt.show()

    # 分析結果をJSON形式で保存
    analysis_result = {
        "total_duration_sec": total_duration,
        "total_duration_hours": total_duration / 3600.0,
        "date_counts": date_counts,
        "cumulative_counts": cumulative_counts
    }

    with open('analysis_result.json', 'w') as f:
        json.dump(analysis_result, f, indent=4)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load and analyze meta information from JSON files.")
    parser.add_argument('--data_dir', type=str, default='./data', help='Directory containing JSON files')
    args = parser.parse_args()
    main(args.data_dir)
