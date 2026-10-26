
# 实验2：电商销售数据清洗
# 使用 Pandas 对原始销售数据进行预处理

import pandas as pd
from pathlib import Path

# 第一步：设置文件路径
project_dir = Path(__file__).resolve().parent
input_file = project_dir / "data" / "sales_raw.csv"
output_file = project_dir / "data" / "sales_clean.csv"

# 第二步：检查原始数据文件是否存在
if not input_file.exists():
    print("错误：找不到原始销售数据文件！")
    raise SystemExit(1)

# 第三步：读取原始CSV文件
try:
    df = pd.read_csv(input_file, encoding="utf-8-sig")
except Exception as e:
    print("错误：读取CSV文件失败！")
    print("错误详情：", e)
    raise SystemExit(1)

print("===== 电商销售数据清洗 =====")
print("原始数据行数：", len(df))

# 第四步：检查必要字段
required_columns = [
    "订单编号", "日期", "商品类别",
    "商品名称", "地区", "数量", "单价"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("错误：缺少字段：", missing_columns)
    raise SystemExit(1)

print("字段检查通过！")

# 第五步：处理空字符串和缺失值
df = df.replace(r"^\s*$", pd.NA, regex=True)
df = df.dropna(subset=required_columns)

# 第六步：转换数据类型
# 如果数量或单价不能转换为数字，则变成NaN
df["数量"] = pd.to_numeric(df["数量"], errors="coerce")
df["单价"] = pd.to_numeric(df["单价"], errors="coerce")

# 如果日期格式不正确，则变成NaT
df["日期"] = pd.to_datetime(
    df["日期"],
    format="%Y-%m-%d",
    errors="coerce"
)

# 第七步：删除转换失败的记录
df = df.dropna(subset=["数量", "单价", "日期"])

# 第八步：删除数量或单价不合理的记录
df = df[
    (df["数量"] > 0) &
    (df["单价"] > 0) &
    (df["数量"] % 1 == 0)
].copy()

# 第九步：删除重复数据
df = df.drop_duplicates().copy()

# 第十步：整理数量、单价和日期
df["数量"] = df["数量"].astype(int)
df["单价"] = df["单价"].round(2)
df["日期"] = df["日期"].dt.strftime("%Y-%m-%d")

# 第十一步：计算每条订单的销售额
df["销售额"] = (
    df["数量"] * df["单价"]
).round(2)

# 第十二步：提取月份
df["月份"] = df["日期"].str[:7]

# 第十三步：检查是否还有有效数据
if df.empty:
    print("错误：清洗后没有有效销售数据！")
    raise SystemExit(1)

# 第十四步：保存清洗后的数据
df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

# 第十五步：输出清洗结果
print("\n===== 数据清洗结果 =====")
print("清洗后有效记录数：", len(df))
print("删除记录数：", 601 - len(df))
print("销售总额：", round(df["销售额"].sum(), 2), "元")

print("\n清洗后的前5条数据：")
print(df.head())

print("\n数据清洗成功！")
print("输出文件：", output_file)
