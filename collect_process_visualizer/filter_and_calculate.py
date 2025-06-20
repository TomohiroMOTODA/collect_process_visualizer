from typing import List, Dict, Any, Callable

def filter_data(data: List[Dict[str, Any]], meta_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    メタ情報(meta_filter)に従ってデータをフィルタリングする
    """
    def match(item):
        return all(item.get(k) == v for k, v in meta_filter.items())
    return [item for item in data if match(item)]

def calculate_stats(filtered_data: List[Dict[str, Any]], calc_func: Callable[[List[Dict[str, Any]]], Any]) -> Any:
    """
    フィルタ済みデータに対して計算処理を行う
    """
    return calc_func(filtered_data)

# 使用例
if __name__ == "__main__":
    # サンプルデータ
    data = [
        {"date": "2024-06-01", "category": "A", "value": 10},
        {"date": "2024-06-01", "category": "B", "value": 20},
        {"date": "2024-06-02", "category": "A", "value": 30},
    ]
    meta_filter = {"date": "2024-06-01", "category": "A"}
    filtered = filter_data(data, meta_filter)
    total = calculate_stats(filtered, lambda d: sum(item["value"] for item in d))
    print(f"合計値: {total}")
