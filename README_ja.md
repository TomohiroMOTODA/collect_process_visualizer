# メタデータチェッカー [限定利用]

[[English](./README.md)/日本語]

データ処理ワークフローにおけるメタデータの検証と可視化を行うシンプルなツールです。**これは個人プロジェクトに関連しています。**

## 🚀 特徴

- メタデータファイルの一貫性と正確性を検証
- メタデータの関係性や構造を可視化
- サマリーレポートの生成
- 簡単なコマンドラインインターフェース

## ✍ 使い方

```bash
python -m collect_process_visualizer.main --data_dir ~/data ~/data.-20250828 --rolling 7 --style seaborn-v0_8 --dpi 144
```

### オプション引数

- `--data_dir`: JSONファイルを含むディレクトリへのパス。デフォルトは `./data`。
- `--date_from`: この日付（YYYY-MM-DD）以降のデータのみ集計。
- `--filter`: `key=value` 形式のフィルタ条件。複数指定可。
- `--no_show`: 図を表示せず、ファイル保存のみにする。
- `--style`: Matplotlibのスタイル（例: `seaborn-v0_8`, `ggplot`）。
- `--rolling`: 日次系列に重ねる移動平均の窓（日数）。
- `--dpi`: 保存する図の解像度（DPI, 既定150）。

### 出力

- 図
    - `data/data_hours_graph.png`（日別/累積の時間）
    - `data/data_files_graph.png`（日別/累積のファイル数）
- CSVサマリ
    - `data/daily_summary.csv`（日付ごとの日別/累積の時間・ファイル数）
- JSONサマリ
    - `analysis_result.json`（図パスや指定オプションを含む）

## 🛠 必要要件

- Python 3.8以上
- 依存パッケージのインストール:

    ```bash
    pip install -r requirements.txt
    ```

## 📒 注意

- メタデータファイルはサポートされている形式（例：JSON, YAML）であることを確認してください。
- ファイルサイズが大きい場合、処理時間が長くなることがあります。
- コントリビューションやフィードバックを歓迎します！

## 📄 ライセンス

未定

## 🙋‍♂️ 連絡先

未定