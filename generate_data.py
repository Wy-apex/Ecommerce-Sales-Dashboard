
# 实验2：电商销售模拟数据生成
# 用于数据看板的设计与实现

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# 第一步：固定随机种子，保证每次生成的数据一致
random.seed(42)

# 第二步：定义商品类别、名称和基础价格
products = {
    "数码": [("鼠标", 59), ("键盘", 129), ("耳机", 199)],
    "服装": [("T恤", 89), ("外套", 259), ("运动裤", 139)],
    "食品": [("饼干", 25), ("牛奶", 49), ("咖啡", 79)],
    "家居": [("台灯", 99), ("水杯", 39), ("收纳盒", 45)],
    "文具": [("笔记本", 15), ("钢笔", 35), ("文件夹", 12)]
}

# 第三步：定义销售地区
regions = ["华东", "华南", "华北", "华中", "西南"]

# 第四步：设置日期范围
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 10, 25)
days = (end_date - start_date).days

# 第五步：生成600条销售记录
data = []

for i in range(600):

    # 随机生成订单日期
    date = start_date + timedelta(
        days=random.randint(0, days)
    )

    # 随机选择商品类别
    category = random.choice(list(products.keys()))

    # 随机选择具体商品
    product, base_price = random.choice(products[category])

    # 随机选择销售地区
    region = random.choice(regions)

    # 随机生成数量和单价
    quantity = random.randint(1, 10)
    price = round(base_price * random.uniform(0.8, 1.2), 2)

    # 保存订单记录
    data.append({
        "订单编号": f"ORD{i + 1:04d}",
        "日期": date.strftime("%Y-%m-%d"),
        "商品类别": category,
        "商品名称": product,
        "地区": region,
        "数量": quantity,
        "单价": price
    })

# 第六步：加入少量异常数据，用于后续清洗测试
data[0]["数量"] = -2
data[1]["地区"] = ""
data[2]["日期"] = "错误日期"
data[3]["单价"] = 0

# 加入一条重复记录
data.append(data[4].copy())

# 第七步：创建data文件夹
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# 第八步：保存CSV文件
file_path = output_dir / "sales_raw.csv"

with open(file_path, "w", newline="", encoding="utf-8-sig") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "订单编号",
            "日期",
            "商品类别",
            "商品名称",
            "地区",
            "数量",
            "单价"
        ]
    )

    writer.writeheader()
    writer.writerows(data)

# 第九步：输出生成结果
print("===== 电商销售模拟数据生成 =====")
print("原始销售记录数：", len(data))
print("数据文件：", file_path)
print("数据生成成功！")
