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
import matplotlib.dates as mdates
from itertools import accumulate
from .filter_and_calculate import filter_data
import csv

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

    if len(data["segments"])!=1:
        for i in range(len(data["segments"])):
            if i == len(data["segments"])-1:
                continue

            segment = data["segments"][i]
            duration = segment["end_time"] - segment["start_time"]

            durations.append(duration)
            if segment["has_suboptimal"]:
                suboptimal_segments.append(segment)
    else:
        # セグメントが1つだけの場合、全体の時間をdurationとして扱う
        segment = data["segments"][0]
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
    statics_epi["json_fullpath"] = os.path.abspath(path)  # ここでフルパスを追加
    statics_epi["json_dir"] = os.path.dirname(os.path.abspath(path))  # ディレクトリ名のみ追加

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


def rolling_mean(values, window):
    """Simple rolling mean; returns a list aligned with input length, padded with None."""
    if window is None or window <= 1:
        return None
    n = len(values)
    if n < window:
        return None
    out = []
    s = sum(values[:window])
    out.append(s / window)
    for i in range(window, n):
        s += values[i] - values[i - window]
        out.append(s / window)
    return [None] * (window - 1) + out


def main(data_dir, meta_filter=None, date_from=None, show=True, style=None, rolling=None, dpi=150):
    # files = glob.glob(os.path.join(data_dir, "*/*.json"), recursive=True)

    files = []
    for i, d in enumerate(data_dir):
        print ("Accessing directory:", d)
        if not os.path.isdir(d):
            print(f"Error: {d} is not a valid directory.")
            return
        files += glob.glob(os.path.join(d, "*", "*.json"), recursive=True)
    statics_all = []
    date_counts = {}
    source_files = []
    subtask_types = set()
    for f in files:
        folder_name = os.path.basename(os.path.dirname(f))
        date = extract_date_from_folder(folder_name)
        tmp_data_info = load_metajson(f)
        if tmp_data_info is not None:
            # サブタスクの種類を収集
            with open(f, "r") as jf:
                meta = json.load(jf)
                # サブタスクの種類があれば追加
                if "subtasks" in meta and isinstance(meta["subtasks"], list):
                    for sub in meta["subtasks"]:
                        if isinstance(sub, dict) and "type" in sub:
                            subtask_types.add(sub["type"])
                        elif isinstance(sub, str):
                            subtask_types.add(sub)
            # 日付フィルタ: date_from以降のみ
            if date_from is not None and tmp_data_info["date"]:
                if tmp_data_info["date"] < date_from:
                    continue
            statics_all.append(tmp_data_info)
            source_files.append(os.path.abspath(f))  # フルパスで格納
            if date:
                if date not in date_counts:
                    date_counts[date] = 0
                date_counts[date] += 1

    # --- ここでフィルタリング ---
    if meta_filter:
        statics_all = filter_data(statics_all, meta_filter)
        # フィルタ後のファイルリストも更新（ディレクトリ名のみで出力）
        filtered_files = [s["json_dir"] for s in statics_all if "json_dir" in s]
    else:
        filtered_files = [s["json_dir"] for s in statics_all if "json_dir" in s]

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
    total_segments = sum(epi["total_segments"] for epi in statics_all)
    total_suboptimal_segments = sum(epi["suboptimal_segments"] for epi in statics_all)
    unique_hsr_ids = sorted(set(epi.get("hsr_id", "") for epi in statics_all))
    unique_locations = sorted(set(epi.get("location_name", "") for epi in statics_all))

    print (f"AIST TOTAL: {total_duration/3600.} (hours)")
    
    # プロット用データ整理（Noneの除外と累積の計算）
    dates = sorted([d for d in dates if d is not None])
    daily_counts = [filtered_date_counts[d] for d in dates]
    cumulative_counts = list(accumulate(daily_counts))
    daily_hours = [time_counts[d] for d in dates]
    cumulative_hours = list(accumulate(daily_hours))

    # 日付をdatetimeに変換してx軸を見やすく
    date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates] if dates else []

    if not date_objs:
        print('No valid dates to plot. Skipping figure generation.')
        # 出力先の確保
        os.makedirs('./data', exist_ok=True)
        # 空のCSVを出力
        csv_path = './data/daily_summary.csv'
        with open(csv_path, 'w', newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(['date', 'daily_hours', 'cumulative_hours', 'daily_files', 'cumulative_files'])
        # 解析結果はJSONに出力して終了
        analysis_result = {
            "total_duration_sec": total_duration,
            "total_duration_hours": total_duration / 3600.0,
            "total_segments": total_segments,
            "total_suboptimal_segments": total_suboptimal_segments,
            "unique_hsr_ids": unique_hsr_ids,
            "unique_locations": unique_locations,
            "date_counts": filtered_date_counts,
            "cumulative_counts": cumulative_counts,
            "source_files": filtered_files,
            "filter_conditions": meta_filter if meta_filter else {},
            "date_from": date_from if date_from else None,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # "data_dir": data_dir,
            "subtask_types": sorted(list(subtask_types)),
            "series_dates": dates,
            "series_daily_hours": daily_hours,
            "series_cumulative_hours": cumulative_hours,
            "series_daily_counts": daily_counts,
            # 追加: 出力ファイル/設定
            "figure_hours": None,
            "figure_files": None,
            "summary_csv": csv_path,
            "rolling_window": rolling,
            "style": style,
            "dpi": dpi,
        }
        with open('analysis_result.json', 'w') as f:
            json.dump(analysis_result, f, indent=4)
        return

    # 出力先の確保
    os.makedirs('./data', exist_ok=True)

    # スタイル適用（あれば）
    if style:
        try:
            plt.style.use(style)
        except Exception:
            print(f"Warn: style '{style}' not found. Using default style.")

    # x軸共通の目盛り設定を返す関数
    def apply_date_axis(ax):
        n = len(date_objs)
        if n <= 15:
            locator = mdates.DayLocator(interval=1)
            formatter = mdates.DateFormatter('%Y-%m-%d')
        elif n <= 60:
            locator = mdates.WeekdayLocator(byweekday=mdates.MO, interval=1)
            formatter = mdates.DateFormatter('%Y-%m-%d')
        elif n <= 370:
            locator = mdates.MonthLocator(interval=1)
            formatter = mdates.DateFormatter('%Y-%m')
        else:
            step = max(1, n // 12)
            locator = mdates.MonthLocator(interval=step)
            formatter = mdates.DateFormatter('%Y-%m')
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

    # ローリング平均（任意）
    ma_hours = rolling_mean(daily_hours, rolling)
    ma_counts = rolling_mean(daily_counts, rolling)

    # 現在の日時を取得（タイトル用）
    analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 図1：時間（hours）専用
    fig_h, axes_h = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax_h_top = axes_h[0]
    ax_h_top.bar(date_objs, daily_hours, color='darkblue', alpha=0.8)
    if ma_hours:
        ax_h_top.plot(date_objs, ma_hours, color='tab:blue', linestyle = "dashed", linewidth=2, label=f'Rolling mean ({rolling}d)')
        ax_h_top.legend(loc='upper left')
    
    # 最大値をアノテーション
    if daily_hours:
        max_hour_idx = daily_hours.index(max(daily_hours))
        max_hour_val = daily_hours[max_hour_idx]
        ax_h_top.annotate(f"Max: {max_hour_val:.1f}h",
                         xy=(date_objs[max_hour_idx], max_hour_val),
                         xytext=(5, 10), textcoords='offset points',
                         fontsize=9, color='red', fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
    
    # 総時間を表示
    # ax_h_top.text(0.02, 0.98, f"Total: {total_duration/3600.:.1f}h",
    #               transform=ax_h_top.transAxes, fontsize=10, fontweight='bold',
    #               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax_h_top.set_ylabel('Hours')
    ax_h_top.set_title(f'Daily duration (hours) - Generated: {analysis_date}')
    ax_h_top.grid(True, axis='y', alpha=0.3)
    ax_h_top.set_ylim(bottom=0)

    ax_h_bot = axes_h[1]
    ax_h_bot.plot(date_objs, cumulative_hours, color='tab:red', marker='o')
    ax_h_bot.set_ylabel('Hours (cumulative)')
    ax_h_bot.set_xlabel('Date')
    ax_h_bot.grid(True, axis='y', alpha=0.3)
    ax_h_bot.set_ylim(bottom=0)
    if cumulative_hours:
        ax_h_bot.annotate(f"Final: {cumulative_hours[-1]:.1f}h",
                          xy=(date_objs[-1], cumulative_hours[-1]),
                          xytext=(5, 5), textcoords='offset points',
                          fontsize=9, color='tab:blue', fontweight='bold')

    apply_date_axis(ax_h_bot)
    fig_h.autofmt_xdate(rotation=30, ha='right')
    fig_h.tight_layout()
    out_hours = './data/data_hours_graph.png'
    fig_h.savefig(out_hours, dpi=dpi)

    # 図2：ファイル数（counts）専用
    fig_c, axes_c = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax_c_top = axes_c[0]
    ax_c_top.bar(date_objs, daily_counts, color='tab:orange', alpha=0.8)
    if ma_counts:
        ax_c_top.plot(date_objs, ma_counts, color='tab:red', linewidth=2, label=f'Rolling mean ({rolling}d)')
        ax_c_top.legend(loc='upper left')
    
    # 最大値をアノテーション
    if daily_counts:
        max_count_idx = daily_counts.index(max(daily_counts))
        max_count_val = daily_counts[max_count_idx]
        ax_c_top.annotate(f"Max: {max_count_val}",
                         xy=(date_objs[max_count_idx], max_count_val),
                         xytext=(5, 10), textcoords='offset points',
                         fontsize=9, color='red', fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
    
    # 総ファイル数を表示
    ax_c_top.text(0.02, 0.98, f"Total: {len(statics_all)} files",
                  transform=ax_c_top.transAxes, fontsize=10, fontweight='bold',
                  verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax_c_top.set_ylabel('Files')
    ax_c_top.set_title(f'Daily files - Generated: {analysis_date}')
    ax_c_top.grid(True, axis='y', alpha=0.3)
    ax_c_top.set_ylim(bottom=0)

    ax_c_bot = axes_c[1]
    ax_c_bot.plot(date_objs, cumulative_counts, color='tab:green', marker='s')
    ax_c_bot.set_ylabel('Files (cumulative)')
    ax_c_bot.set_xlabel('Date')
    ax_c_bot.grid(True, axis='y', alpha=0.3)
    ax_c_bot.set_ylim(bottom=0)
    
    # 最終累積値をアノテーション
    if cumulative_counts:
        ax_c_bot.annotate(f"Final: {cumulative_counts[-1]} files",
                         xy=(date_objs[-1], cumulative_counts[-1]),
                         xytext=(5, 5), textcoords='offset points',
                         fontsize=9, color='tab:green', fontweight='bold')

    apply_date_axis(ax_c_bot)
    fig_c.autofmt_xdate(rotation=30, ha='right')
    fig_c.tight_layout()
    out_files = './data/data_files_graph.png'
    fig_c.savefig(out_files, dpi=dpi)

    # CSVで日次サマリを出力
    csv_path = './data/daily_summary.csv'
    with open(csv_path, 'w', newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(['date', 'daily_hours', 'cumulative_hours', 'daily_files', 'cumulative_files'])
        for d, h, ch, c, cc in zip(dates, daily_hours, cumulative_hours, daily_counts, cumulative_counts):
            writer.writerow([d, f"{h:.3f}", f"{ch:.3f}", c, cc])

    if show:
        plt.show()

    # 分析結果をJSON形式で保存（拡張版）
    analysis_result = {
        "total_duration_sec": total_duration,
        "total_duration_hours": total_duration / 3600.0,
        "total_segments": total_segments,
        "total_suboptimal_segments": total_suboptimal_segments,
        "unique_hsr_ids": unique_hsr_ids,
        "unique_locations": unique_locations,
        "date_counts": filtered_date_counts,
        "cumulative_counts": cumulative_counts,
    "source_files": filtered_files,
        "filter_conditions": meta_filter if meta_filter else {},
        "date_from": date_from if date_from else None,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_dir": data_dir,
        "subtask_types": sorted(list(subtask_types)),
    # 追加: 可視化に使った系列を出力
    "series_dates": dates,
    "series_daily_hours": daily_hours,
    "series_cumulative_hours": cumulative_hours,
    "series_daily_counts": daily_counts,
    # 追加: 出力ファイル
    "figure_hours": out_hours if 'out_hours' in locals() else None,
    "figure_files": out_files if 'out_files' in locals() else None,
    "summary_csv": csv_path,
    "rolling_window": rolling,
    "style": style,
    "dpi": dpi,
    }

    with open('analysis_result.json', 'w') as f:
        json.dump(analysis_result, f, indent=4)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Load and analyze meta information from JSON files.")
    parser.add_argument('--data_dir', type=str, default='./data', nargs='*', help='Directory containing JSON files')
    parser.add_argument('--filter', action='append', help='Filter condition in key=value format (can specify multiple times)')
    parser.add_argument('--date_from', type=str, help='Include data from this date (YYYY-MM-DD) and after')
    parser.add_argument('--no_show', action='store_true', help='Do not display figures (save only)')
    parser.add_argument('--style', type=str, help='Matplotlib style name (e.g., seaborn-v0_8, ggplot)')
    parser.add_argument('--rolling', type=int, help='Rolling window size in days for daily series')
    parser.add_argument('--dpi', type=int, default=150, help='DPI for saved figures')
    args = parser.parse_args()
    # 例: --date_from 2024-06-01 で2024年6月1日以降のデータのみ集計
    # 例: --filter hsr_id=HSR001 でhsr_idがHSR001のデータのみ集計
    meta_filter = {}
    if args.filter:
        for f in args.filter:
            if '=' in f:
                k, v = f.split('=', 1)
                meta_filter[k] = v
    main(
        args.data_dir,
        meta_filter=meta_filter,
        date_from=args.date_from,
        show=not args.no_show,
        style=args.style,
        rolling=args.rolling,
        dpi=args.dpi,
    )
