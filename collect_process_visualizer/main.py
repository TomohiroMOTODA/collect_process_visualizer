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
import argparse
from datetime import datetime
from datetime import timedelta
import statistics
import glob
import os
import matplotlib.pyplot as plt
from filter_and_calculate import filter_data

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
    statics_epi["date"] = extract_date_from_folder(os.path.basename(path.split("/")[-2]))
    statics_epi["total_time"] = total_time
    statics_epi["total_duration"] = timedelta(seconds=total_time)
    statics_epi["mean_duration"] = mean_time
    statics_epi["max_duration"] = max_time
    statics_epi["min_duration"] = min_time
    statics_epi["total_segments"] = len(durations)
    statics_epi["suboptimal_segments"] = len(suboptimal_segments)

    # メタ情報をstatics_epiに追加
    statics_epi["bag_path"] = data.get("bag_path", "")
    statics_epi["hsr_id"] = str(data.get("hsr_id", ""))
    statics_epi["version"] = data.get("version", "")
    statics_epi["location_name"] = data.get("location_name", "")
    statics_epi["interface"] = data.get("interface", "")
    statics_epi["git_branch"] = data.get("git_branch", "")
    statics_epi["git_hash"] = data.get("git_hash", "")

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

def extract_date_from_folder(folder_name):
    # フォルダ名から日付を抽出する
    parts = folder_name.split('-')
    if len(parts) >= 6:
        date_str = parts[2] + parts[3] + parts[4]
        try:
            date = datetime.strptime(date_str, '%y%m%d')
            date_fold = date.strftime('%Y-%m-%d')
            return date_fold
        except ValueError:
            return None
    return None

def parse_filter_args(filter_args):
    """
    コマンドライン引数からフィルタ条件を辞書としてパース
    例: --filter key1=value1 --filter key2=value2
    """
    meta_filter = {}
    if filter_args:
        for f in filter_args:
            if '=' in f:
                k, v = f.split('=', 1)
                meta_filter[k] = v
    return meta_filter


def main(data_dir, meta_filter=None):
    files = glob.glob(os.path.join(data_dir, "*/*.json"), recursive=True)
    statics_all = []
    date_counts = {}
    for f in files:
        folder_name = os.path.basename(os.path.dirname(f))
        date = extract_date_from_folder(folder_name)
        tmp_data_info = load_metajson(f)
        if tmp_data_info is not None:
            statics_all.append(tmp_data_info)
            if date:
                if date not in date_counts:
                    date_counts[date] = 0
                date_counts[date] += 1

    # --- ここでフィルタリング ---
    if meta_filter:
        # すべてのメタ情報キーでフィルタ可能
        statics_all = filter_data(statics_all, meta_filter)

    # フィルタ後のdate_counts, time_countsを再計算
    filtered_date_counts = {}
    for epi in statics_all:
        d = epi["date"]
        if d not in filtered_date_counts:
            filtered_date_counts[d] = 0
        filtered_date_counts[d] += 1

    dates = sorted(filtered_date_counts.keys())
    time_counts = {}
    for d in dates:
        total_tmp = 0
        for epi in statics_all:
            if epi["date"] == d:
                total_tmp += epi["total_time"]
        time_counts[d] = total_tmp/3600.
        print (f"{d} : {total_tmp/3600.} (hours)")

    # 総和を求める．
    total_duration = sum(epi["total_time"] for epi in statics_all)
    print(f"Total duration : {total_duration} (sec)")
    print(f"Total duration : {total_duration /3600.} (hours)")

    # 日付ごとのデータ件数を棒グラフで表示
    counts = [filtered_date_counts[date] for date in dates]
    cumulative_counts = [sum(counts[:i+1]) for i in range(len(counts))]
    datasize = [time_counts[date] for date in dates]
    cumulative_datasize = [sum(datasize[:i+1]) for i in range(len(datasize))]

    plt.figure(figsize=(10, 6))
    plt.bar(dates, datasize, color='blue', label='Daily Data (hours)')
    plt.plot(dates, cumulative_datasize, color='red', marker='o', label='Cumulative Data Size (hours)')
    plt.xlabel('Date')
    plt.ylabel('Data (hours)')
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
        "date_counts": filtered_date_counts,
        "cumulative_counts": cumulative_counts
    }

    with open('analysis_result.json', 'w') as f:
        json.dump(analysis_result, f, indent=4)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Load and analyze meta information from JSON files.")
    parser.add_argument('--data_dir', type=str, default='./data', help='Directory containing JSON files')
    parser.add_argument('--filter', action='append', help='Filter condition in key=value format (can specify multiple times)')
    args = parser.parse_args()
    meta_filter = {}
    if args.filter:
        for f in args.filter:
            if '=' in f:
                k, v = f.split('=', 1)
                meta_filter[k] = v
    main(args.data_dir, meta_filter=meta_filter)
