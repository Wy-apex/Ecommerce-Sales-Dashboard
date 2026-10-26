
# 实验2：电商销售数据看板
# 使用 Streamlit + Pandas + Plotly 实现

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 第一步：设置网页基本信息
st.set_page_config(
    page_title="电商销售数据看板",
    page_icon="📊",
    layout="wide"
)

# 第二步：读取清洗后的数据
data_file = Path(__file__).resolve().parent / "data" / "sales_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(data_file, encoding="utf-8-sig")

    # 将日期转换为日期类型
    df["日期"] = pd.to_datetime(df["日期"])

    # 提取月份，用于趋势统计
    df["月份"] = df["日期"].dt.strftime("%Y-%m")

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"数据读取失败：{e}")
    st.stop()

if df.empty:
    st.warning("没有可以展示的销售数据！")
    st.stop()

# 第三步：设置页面标题
st.title("📊 电商销售数据分析看板")
st.caption("实验2：数据看板的设计与实现｜数据来源：Python模拟销售数据")

st.divider()

# 第四步：侧边栏筛选
st.sidebar.header("🔍 数据筛选")

# 商品类别筛选
category_options = sorted(df["商品类别"].unique())

selected_categories = st.sidebar.multiselect(
    "选择商品类别",
    category_options,
    default=category_options
)

# 地区筛选
region_options = sorted(df["地区"].unique())

selected_regions = st.sidebar.multiselect(
    "选择地区",
    region_options,
    default=region_options
)

# 日期范围筛选
min_date = df["日期"].min().date()
max_date = df["日期"].max().date()

date_range = st.sidebar.date_input(
    "选择日期范围",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) != 2:
    st.info("请选择完整的开始日期和结束日期。")
    st.stop()

# 根据用户选择过滤数据
filtered_df = df[
    (df["商品类别"].isin(selected_categories)) &
    (df["地区"].isin(selected_regions)) &
    (df["日期"].dt.date >= date_range[0]) &
    (df["日期"].dt.date <= date_range[1])
].copy()

if filtered_df.empty:
    st.warning("当前筛选条件下没有销售数据！")
    st.stop()

# 第五步：计算核心指标
total_sales = filtered_df["销售额"].sum()
total_orders = filtered_df["订单编号"].nunique()
avg_sales = total_sales / total_orders

# 按月份统计销售额
monthly_summary = (
    filtered_df.groupby("月份", as_index=False)["销售额"]
    .sum()
    .sort_values("月份")
)

# 计算最近两个日历月份的销售额变化
growth_text = "暂无数据"

if len(monthly_summary) >= 2:
    last_month = pd.Period(
        monthly_summary["月份"].iloc[-1], freq="M"
    )
    previous_month = str(last_month - 1)

    current_sales = monthly_summary["销售额"].iloc[-1]

    previous_sales = monthly_summary.loc[
        monthly_summary["月份"] == previous_month,
        "销售额"
    ].sum()

    if previous_sales > 0:
        growth = (current_sales - previous_sales) / previous_sales * 100
        growth_text = f"{growth:+.2f}%"

# 第六步：展示核心指标卡片
st.subheader("一、数据概览")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 销售总额", f"¥{total_sales:,.2f}")

with col2:
    st.metric("📦 订单总数", f"{total_orders} 单")

with col3:
    st.metric("🛒 平均客单价", f"¥{avg_sales:,.2f}")

with col4:
    st.metric("📈 最近月度增长率", growth_text)

st.divider()

# 第七步：分类维度统计
st.subheader("二、销售维度统计")

col_left, col_right = st.columns(2)

# 按商品类别统计销售额
category_summary = (
    filtered_df.groupby("商品类别", as_index=False)["销售额"]
    .sum()
    .sort_values("销售额", ascending=False)
)


with col_left:
    fig_bar = px.bar(
        category_summary,
        x="销售额",
        y="商品类别",
        orientation="h",
        color="商品类别",
        title="各商品类别销售额对比",
        text="销售额"
    )

    # 将销售额显示为整数，避免标签过长
    fig_bar.update_traces(
        texttemplate="¥%{x:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    # 按销售额排序，并保留标签显示空间
    fig_bar.update_layout(
        showlegend=False,
        yaxis=dict(categoryorder="total ascending"),
        xaxis_title="销售额（元）",
        yaxis_title="商品类别",
        margin=dict(l=20, r=90, t=60, b=40)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# 按地区统计销售占比
region_summary = (
    filtered_df.groupby("地区", as_index=False)["销售额"]
    .sum()
)

with col_right:
    fig_pie = px.pie(
        region_summary,
        names="地区",
        values="销售额",
        hole=0.5,
        title="各地区销售额占比"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# 第八步：销售趋势分析
st.subheader("三、销售趋势分析")

fig_line = px.line(
    monthly_summary,
    x="月份",
    y="销售额",
    markers=True,
    title="月度销售额变化趋势"
)

# 将月份作为分类标签，避免单个月份时横坐标显示时间小数
fig_line.update_xaxes(type="category")

# 让销售额纵坐标从0开始，避免单个数据点被过度放大
fig_line.update_yaxes(rangemode="tozero")


fig_line.update_layout(
    xaxis_title="月份",
    yaxis_title="销售额（元）"
)

st.plotly_chart(fig_line, use_container_width=True)

st.divider()


# 第九步：销售明细展示
st.subheader("四、销售明细数据")

st.write(f"当前筛选后共有 {len(filtered_df)} 条销售记录")

# 按日期从新到旧排序
display_df = filtered_df.sort_values(
    "日期", ascending=False
).copy()

# 将日期转换为年月日格式，去掉00:00:00
display_df["日期"] = display_df["日期"].dt.strftime("%Y-%m-%d")

# 展示销售明细
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# 第十步：下载数据
csv_data = display_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 下载筛选后的销售数据",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.divider()
st.caption("Python 数据看板实验｜Streamlit + Pandas + Plotly")
