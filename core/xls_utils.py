"""
XLS 数据处理工具（UV/FL 共用）
提供：找最新 xls、找波峰、读 A31、保存/加载结果等
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json


def find_latest_xls_file(data_dir: str = r"E:\code\data"):
    """找到目录下最新的 xls 文件（按修改时间）。"""
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"错误：目录不存在: {data_dir}")
        return None
    all_xls_files = list(data_path.glob("*.xls")) + list(data_path.glob("*.xlsx"))
    if not all_xls_files:
        print(f"错误：在 {data_dir} 目录下找不到xls文件")
        return None
    xls_files = [p for p in all_xls_files if not p.name.startswith("~$")]
    if not xls_files:
        print(f"错误：当前目录下只有临时锁文件（~$ 开头），请先关闭 Excel 后再重试")
        return None
    latest_file = max(xls_files, key=lambda p: p.stat().st_mtime)
    print(f"找到最新的xls文件: {latest_file.name}")
    return str(latest_file)


def _resolve_nm_abs_columns(df: pd.DataFrame, abs_column: str = "ABS", nm_column: str = "nm"):
    """在 DataFrame 中定位 nm / ABS 列。返回 (nm_col, abs_col)。"""
    abs_col = nm_col = None
    for col in df.columns:
        col_str = str(col).strip().upper()
        if col_str == abs_column.upper():
            abs_col = col
        elif col_str == nm_column.upper():
            nm_col = col
    return nm_col, abs_col


def find_first_prominent_peak(
    xls_file: str,
    abs_column: str = "ABS",
    nm_column: str = "nm",
    header_row: int = 30,
    nm_min: float | None = None,
    nm_max: float | None = None,
    smooth_window: int = 7,
    flat_eps: float = 0.003,
    flat_min_len: int = 8,
    min_prominence: float = 0.01,
    min_peak_abs: float | None = None,
    saturation_abs: float = 6.0,
    saturation_tolerance: float = 0.05,
):
    """找到曲线「第一个明显波峰」对应的 nm/ABS。"""
    try:
        print(f"\n读取文件: {xls_file}")
        df = pd.read_excel(xls_file, header=header_row)
        nm_col, abs_col = _resolve_nm_abs_columns(df, abs_column=abs_column, nm_column=nm_column)
        if abs_col is None or nm_col is None:
            print(f"错误：找不到ABS/nm列，可用列: {list(df.columns)}")
            return None
        data = df[[nm_col, abs_col]].copy()
        data.columns = ["nm", "abs"]
        data = data.replace([np.inf, -np.inf], np.nan).dropna()
        data["nm"] = pd.to_numeric(data["nm"], errors="coerce")
        data["abs"] = pd.to_numeric(data["abs"], errors="coerce")
        data = data.dropna().sort_values("nm")
        if nm_min is not None:
            data = data[data["nm"] >= nm_min]
        if nm_max is not None:
            data = data[data["nm"] <= nm_max]
        if len(data) < 5:
            print("警告：有效数据点过少，无法找峰")
            return None
        w = int(max(1, smooth_window))
        if w % 2 == 0:
            w += 1
        y = data["abs"].rolling(window=w, center=True, min_periods=max(1, w // 2)).mean().to_numpy()
        x = data["nm"].to_numpy()
        saturation_mask = np.abs(y - saturation_abs) < saturation_tolerance
        dy = np.abs(np.diff(y))
        is_flat = dy < float(flat_eps)
        flat_point = np.zeros_like(y, dtype=bool)
        flat_point[1:] = is_flat
        flat_point = flat_point | saturation_mask
        i = 0
        while i < len(y):
            if not flat_point[i]:
                i += 1
                continue
            j = i
            while j < len(y) and flat_point[j]:
                j += 1
            if (j - i) >= int(flat_min_len):
                flat_point[i:j] = True
            else:
                flat_point[i:j] = False
            i = j
        valid_mask = ~flat_point
        valid_mask[:1] = False
        valid_mask[-1:] = False
        if min_prominence is None:
            min_prominence = 0.05
        if min_peak_abs is None:
            min_peak_abs = float(np.nanmin(y)) + float(min_prominence)
        for idx in range(1, len(y) - 1):
            if not valid_mask[idx] or not (y[idx - 1] < y[idx] > y[idx + 1]) or y[idx] < min_peak_abs:
                continue
            left, left_min = idx - 1, y[idx - 1]
            while left > 0 and y[left] <= y[left + 1]:
                left -= 1
                left_min = min(left_min, y[left])
            right, right_min = idx + 1, y[idx + 1]
            while right < len(y) - 1 and y[right] <= y[right - 1]:
                right += 1
                right_min = min(right_min, y[right])
            prom = float(y[idx] - max(left_min, right_min))
            if prom < float(min_prominence):
                continue
            result = {
                "peak_nm": float(x[idx]),
                "peak_abs": float(y[idx]),
                "prominence": prom,
                "file": xls_file,
                "filename": Path(xls_file).name,
                "method": "first_prominent_peak_ignore_flat",
            }
            print(f"\n找到第一个明显波峰: peak_nm={result['peak_nm']:.6f}, peak_abs={result['peak_abs']:.6f}")
            return result
        print("\n警告：未找到满足条件的第一个明显波峰")
        return None
    except Exception as e:
        print(f"处理文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_result(result: dict, output_file: str = "step22_result.json"):
    """保存结果到 JSON 文件。"""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✓ 结果已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"保存结果失败: {e}")
        return False


def read_cell_a31(xls_file: str):
    """读取 xls/xlsx 中 A31 单元格的值。"""
    try:
        print(f"\n读取文件以获取 A31: {xls_file}")
        df = pd.read_excel(xls_file, header=None)
        row_idx, col_idx = 30, 0
        if df.shape[0] <= row_idx or df.shape[1] <= col_idx:
            print("警告：文件数据行/列不足，无法访问 A31")
            return None
        value = df.iat[row_idx, col_idx]
        if pd.isna(value):
            print("警告：A31 单元格为空")
            return None
        stored_value = float(value) if isinstance(value, (int, float, np.floating)) else str(value)
        result = {"cell": "A31", "value": stored_value, "file": xls_file, "filename": Path(xls_file).name}
        print(f"✓ 读取到 A31={stored_value}")
        return result
    except Exception as e:
        print(f"读取 A31 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_result(input_file: str = "step22_result.json"):
    """从 JSON 文件加载结果。"""
    if not os.path.exists(input_file):
        return None
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载结果失败: {e}")
        return None
