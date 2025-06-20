# Meta Data Checker [limited Use]

[English/[日本語](./README_ja.md)]

A simple tool for validating and visualizing metadata in your data processing workflows. **This is related to my own private project.**

## 📝 Overview

Meta Data Checker is a lightweight utility designed to help you ensure the quality and structure of metadata used in data processing pipelines. It supports validation, visualization, and reporting, making it easier to maintain consistency across your datasets.

## 🚀 Features

- Validate metadata files for consistency and correctness.
- Visualize metadata relationships and structures.
- Generate summary reports.
- Easy command-line interface.
- Supports JSON and YAML metadata formats.
- Extensible for custom validation rules.

## ✍ Usage

```bash
python -m collect_process_visualizer.main --data_dir ./data
```

### Optional Arguments

- `--data_dir`: Path to the directory containing JSON files. Default is `./data`.
- `--filter`: Filter condition in `key=value` format. Can be specified multiple times to apply multiple filters.
- `--date_from`: Include data from this date (`YYYY-MM-DD`) and after.

#### Available filter keys

You can use the following keys with the `--filter` option (these correspond to metadata fields in each JSON):

- `bag_path`: Filter by bag file path
- `hsr_id`: Filter by HSR (robot) ID
- `version`: Filter by metadata version
- `location_name`: Filter by location name
- `interface`: Filter by interface type
- `git_branch`: Filter by git branch name
- `git_hash`: Filter by git commit hash
- `json_fullpath`: Filter by the full path to the JSON file
- `json_dir`: Filter by the directory containing the JSON file

You may also use any other key present in your metadata JSON objects.  
Multiple filters can be combined, and only entries matching all conditions will be included.

### Example

```bash
python -m collect_process_visualizer.main --data_dir ./sample_data --filter status=active --filter type=experiment --date_from 2024-01-01 --output ./report --format yaml --strict
```

## 🐚 Utility Shell Script

A helper shell script `scp_source_dirs.sh` is included for copying source directories listed in a JSON file to a remote server using `scp`.

### Usage

```bash
./scp_source_dirs.sh <user>@<host>:/remote/path [source_files.json]
```

- `<user>@<host>:/remote/path`: Destination for `scp` (e.g., `user@192.168.1.100:/home/user/data`)
- `[source_files.json]`: (Optional) JSON file listing source directories (default: `analysis_result.json`)

The script requires `jq` to parse JSON. It reads the `source_files` array from the JSON and copies each directory to the remote destination.

### Example

```bash
./scp_source_dirs.sh user@192.168.1.100:/home/user/data my_sources.json
```

## 📂 Supported Metadata Formats

- JSON (`.json`)
- YAML (`.yaml`, `.yml`)

## 🛠 Requirements

- Python 3.8+
- Install dependencies with:

    ```bash
    pip install -r requirements.txt
    ```
- `jq` for shell script JSON parsing

## 📄 License

TBD

## 🙋‍♂️ Contact

TBD
