# 用途：第 3 章 3.4 节示例——读 CSV 文件 + 异常处理（出错不崩溃）
# 运行前：axes.csv 与本脚本同目录
# 场景：从轴参数表（CSV）读入数据；文件不存在时给友好提示，而不是程序崩掉。

import csv


def 读轴参数表(路径):
    """读 CSV 返回字典列表，每行一个字典"""
    rows = []
    with open(路径, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


try:
    rows = 读轴参数表("axes.csv")
    print(f"成功读入 {len(rows)} 行轴参数，字段：{list(rows[0].keys())}")
except FileNotFoundError:
    print("找不到 axes.csv——请确认文件与脚本在同一目录")
except UnicodeDecodeError:
    print("编码不对——请把 CSV 另存为 UTF-8 编码")
