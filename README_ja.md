# メタデータチェッカー [限定利用]

[[English](./README.md)/日本語]

データ処理ワークフローにおけるメタデータの検証と可視化を行うシンプルなツールです。**これは個人プロジェクトに関連しています。**

## 📝 概要

Meta Data Checkerは、データ処理パイプラインで利用されるメタデータの品質や構造を簡単にチェックできる軽量ツールです。検証・可視化・レポート生成機能を備え、データセット間の一貫性維持をサポートします。

## 🚀 特徴

- メタデータファイルの一貫性と正確性を検証
- メタデータの関係性や構造を可視化
- サマリーレポートの生成
- 簡単なコマンドラインインターフェース
- JSONおよびYAML形式のメタデータに対応
- カスタム検証ルールの拡張が可能

## ✍ 使い方

```bash
python -m collect_process_visualizer.main --data_dir ./data
```

### オプション引数

- `--data_dir`: JSONファイルを含むディレクトリへのパス。デフォルトは `./data`。
- `--filter`: `key=value` 形式のフィルタ条件。複数回指定可能でAND条件として適用されます。
- `--date_from`: この日付（`YYYY-MM-DD`）以降のデータのみを対象とします。
- `--output`: レポートや可視化結果の出力先パス
- `--format`: メタデータ形式（`json` または `yaml`）。デフォルトは `json`
- `--strict`: 厳格な検証モードを有効化

#### 利用可能なfilterキー

`--filter` オプションでは、以下のようなキーが利用できます（メタデータ構造に依存します）:

- `status`: ステータスで絞り込み（例: `active`, `inactive`）
- `type`: データや実験の種類で絞り込み（例: `experiment`, `control`）
- `owner`: 所有者や担当者で絞り込み
- `project`: プロジェクト名やIDで絞り込み
- `category`: カテゴリラベルで絞り込み
- `tag`: タグやラベルで絞り込み
- その他、メタデータJSON内に存在する任意のキー

複数のフィルタを組み合わせると、すべての条件を満たすエントリのみが対象となります。

### サンプル

```bash
python -m collect_process_visualizer.main --data_dir ./sample_data --filter status=active --filter type=experiment --date_from 2024-01-01 --output ./report --format yaml --strict
```

## 🐚 ユーティリティシェルスクリプト

`scp_source_dirs.sh` という補助シェルスクリプトが付属しており、JSONファイルに記載されたディレクトリをリモートサーバーに `scp` でコピーできます。

### 使い方

```bash
./scp_source_dirs.sh <user>@<host>:/remote/path [source_files.json]
```

- `<user>@<host>:/remote/path`: 転送先（例: `user@192.168.1.100:/home/user/data`）
- `[source_files.json]`: （省略可）ディレクトリリストを含むJSONファイル（デフォルト: `analysis_result.json`）

このスクリプトはJSON解析に `jq` を利用します。JSON内の `source_files` 配列からディレクトリを読み取り、順次リモート先へコピーします。

### 例

```bash
./scp_source_dirs.sh user@192.168.1.100:/home/user/data my_sources.json
```

## 📂 サポートされているメタデータ形式

- JSON（`.json`）
- YAML（`.yaml`, `.yml`）

## 🛠 必要要件

- Python 3.8以上
- 依存パッケージのインストール:

    ```bash
    pip install -r requirements.txt
    ```
- シェルスクリプト利用時は `jq` コマンドが必要です

## 📄 ライセンス

未定

## 🙋‍♂️ 連絡先

未定