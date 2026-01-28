# Meta Data Checker [limited Use]

[English/[日本語](./README_ja.md)]

A simple tool for validating and visualizing metadata in your data processing workflows. **This is related to my own private project.**

## 🚀 Features

- Validate metadata files for consistency and correctness.
- Visualize metadata relationships and structures.
- Generate summary reports.
- Easy command-line interface.

## ✍ Usage

```bash
python -m collect_process_visualizer.main --data_dir ~/data ~/data.-20250828 --rolling 7 --style seaborn-v0_8 --dpi 144
```

### Optional Arguments

- `--data_dir`: Path to the directory containing JSON files. Default is `./data`.
- `--date_from`: Include data from this date (YYYY-MM-DD) and after.
- `--filter`: Filter condition(s) in key=value format. Can be repeated.
- `--no_show`: Do not display figures, only save images.
- `--style`: Matplotlib style (e.g., `seaborn-v0_8`, `ggplot`).
- `--rolling`: Rolling window size (days) for daily series overlays.
- `--dpi`: DPI for saved figures (default 150).

### Outputs

- Figures
    - `data/data_hours_graph.png` (Daily and cumulative hours)
    - `data/data_files_graph.png` (Daily and cumulative file counts)
- CSV Summary
    - `data/daily_summary.csv` (date, daily/cumulative hours and files)
- JSON Summary
    - `analysis_result.json` (includes figure paths and options)

## 🛠 Requirements

- Python 3.8+
- Install dependencies with:

    ```bash
    pip install -r requirements.txt
    ```

## 📒 Note

- Ensure your metadata files are in the supported format (e.g., JSON, YAML).
- For large files, processing time may increase.
- Contributions and feedback are welcome!

## 📄 License

TBD

## 🙋‍♂️ Contact

TBD
