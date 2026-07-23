"""
===========================================================
 保险理赔数据分析引擎
 功能：
   1. 读取10万条理赔数据
   2. 按保单号汇总，找出"理赔金额最高的Top 10保单"
   3. 绘制折线图（带数据标签）
   4. 输出分析报告
 作者：精算实战项目
===========================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import sys

# ====== 确保中文字体显示 ======
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

# ====== 路径配置 ======
DATA_PATH = "data/claims_data.csv"
OUTPUT_DIR = "output"
CHART_PATH = os.path.join(OUTPUT_DIR, "top10_policies_chart.png")
REPORT_PATH = os.path.join(OUTPUT_DIR, "analysis_report.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("[保险理赔数据分析引擎] 启动")
print("=" * 60)

# ====== 第一步：读取数据 ======
print("\n[1/6] 正在读取数据: %s" % DATA_PATH)
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
print("     成功读取 %d 条理赔记录" % len(df))
print("     数据字段: %s" % list(df.columns))

# ====== 数据概览 ======
print("\n[数据概览]")
print("  - 总记录数: %d" % len(df))
print("  - 理赔总金额: %.2f 元" % df['理赔金额'].sum())
print("  - 平均理赔金额: %.2f 元" % df['理赔金额'].mean())
print("  - 最大单笔理赔: %.2f 元" % df['理赔金额'].max())
print("  - 最小单笔理赔: %.2f 元" % df['理赔金额'].min())
print("  - 涉及保单数: %d" % df['保单号'].nunique())
print("  - 险种类型: %s" % list(df['险种类型'].unique()))

# ====== 第二步：按保单号汇总理赔金额 ======
print("\n[2/6] 正在按保单号汇总理赔金额...")

# 核心操作：groupby 按保单号分组，sum 汇总理赔金额
policy_summary = (
    df.groupby("保单号")["理赔金额"]
    .sum()
    .reset_index()
    .sort_values("理赔金额", ascending=False)
)

# 重置索引，并添加排名列
policy_summary = policy_summary.reset_index(drop=True)
policy_summary["排名"] = range(1, len(policy_summary) + 1)

print("     汇总完成，共有 %d 个保单产生理赔" % len(policy_summary))

# ====== 第三步：提取 Top 10 ======
print("\n[3/6] ==== 理赔金额最高的 Top 10 保单 ====")
print("-" * 60)
top10 = policy_summary.head(10).copy()
top10["理赔金额（万元）"] = (top10["理赔金额"] / 10000).round(2)

for _, row in top10.iterrows():
    print("  第%2d名 | %s | %12.2f 元 | %8.2f万元" % (
        row['排名'], row['保单号'], row['理赔金额'], row['理赔金额（万元）']))

print("-" * 60)
print("  Top 10 理赔总额: %.2f 元" % top10['理赔金额'].sum())
print("  占全部理赔比例: %.2f%%" % (top10['理赔金额'].sum() / df['理赔金额'].sum() * 100))

# ====== 看看 Top 10 保单都理赔了哪些险种 ======
print("\n[4/6] Top 10 保单的险种分布：")
top10_policies = top10["保单号"].tolist()
top10_details = df[df["保单号"].isin(top10_policies)]
top10_type_dist = top10_details.groupby("险种类型")["理赔金额"].agg(["count", "sum"]).sort_values("sum", ascending=False)
print(top10_type_dist.to_string())

# ====== 第五步：绘制折线图 ======
print("\n[5/6] 正在绘制折线图...")

fig, ax = plt.subplots(figsize=(14, 7))

# 准备数据
x = range(1, 11)
y = top10["理赔金额（万元）"].values
labels = [p[:10] + "..." if len(p) > 10 else p for p in top10["保单号"].values]

# 绘制折线图
line = ax.plot(x, y, 
               marker="o", 
               markersize=10,
               linewidth=3,
               color="#2C6B9E",
               markerfacecolor="#E8734A",
               markeredgecolor="white",
               markeredgewidth=2,
               label="理赔金额")

# 在每个数据点上标注金额
for i, (v, lbl) in enumerate(zip(y, labels)):
    offset = 1.5 if v < max(y) * 0.5 else -3.5
    ax.annotate("%.2f万" % v,
                xy=(i + 1, v),
                xytext=(0, 15 if i % 2 == 0 else -25),
                textcoords="offset points",
                ha="center",
                fontsize=10,
                fontweight="bold",
                color="#2C6B9E",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF9E6", edgecolor="#E8734A", alpha=0.9))

# 设置X轴标签（保单号简写）
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)

# 设置标题和轴标签
ax.set_title("[Top 10] 理赔金额最高的保单排名", fontsize=18, fontweight="bold", pad=20)
ax.set_xlabel("理赔排名", fontsize=13)
ax.set_ylabel("理赔金额（万元）", fontsize=13)

# 添加网格
ax.grid(axis="y", alpha=0.3, linestyle="--")
ax.set_axisbelow(True)

# 添加背景色和边框美化
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#CCCCCC")
ax.spines["bottom"].set_color("#CCCCCC")

# 添加统计信息小标签
stats_text = "总保单数: %d\nTop 10 占比: %.2f%%" % (
    len(policy_summary), 
    top10['理赔金额'].sum() / df['理赔金额'].sum() * 100
)
ax.text(0.98, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment="top", horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#CCCCCC", alpha=0.9))

plt.tight_layout()
plt.savefig(CHART_PATH, dpi=200, bbox_inches="tight")
print("     折线图已保存: %s" % CHART_PATH)

# ====== 第六步：生成分析报告 ======
print("\n[6/6] 正在生成分析报告...")

report_lines = []
report_lines.append("=" * 60)
report_lines.append("  保险理赔数据分析报告")
report_lines.append("=" * 60)
report_lines.append("")
report_lines.append("[数据概况]")
report_lines.append("  - 分析数据量: %d 条理赔记录" % len(df))
report_lines.append("  - 数据时间范围: %s ~ %s" % (df['理赔日期'].min(), df['理赔日期'].max()))
report_lines.append("  - 涉及保单数: %d" % df['保单号'].nunique())
report_lines.append("  - 涉及险种: %s" % ', '.join(df['险种类型'].unique()))
report_lines.append("")
report_lines.append("[理赔总览]")
report_lines.append("  - 理赔总金额: %.2f 元" % df['理赔金额'].sum())
report_lines.append("  - 平均理赔金额: %.2f 元" % df['理赔金额'].mean())
report_lines.append("  - 中位数理赔金额: %.2f 元" % df['理赔金额'].median())
report_lines.append("  - 最大单笔理赔: %.2f 元" % df['理赔金额'].max())
report_lines.append("")
report_lines.append("[Top 10 保单排名]")
for _, row in top10.iterrows():
    report_lines.append("  第%2d名 | %s | %.2f 元" % (row['排名'], row['保单号'], row['理赔金额']))

report_lines.append("")
report_lines.append("  Top 10 理赔总额: %.2f 元" % top10['理赔金额'].sum())
report_lines.append("  Top 10 占比: %.2f%%" % (top10['理赔金额'].sum() / df['理赔金额'].sum() * 100))
report_lines.append("")
report_lines.append("[可视化图表]")
report_lines.append("  折线图文件: %s" % CHART_PATH)
report_lines.append("")
report_lines.append("=" * 60)
report_lines.append("报告生成时间: %s" % pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
report_lines.append("=" * 60)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("     分析报告已保存: %s" % REPORT_PATH)

# ====== 完成 ======
print("\n" + "=" * 60)
print("分析完成！")
print("图表输出: %s" % CHART_PATH)
print("报告输出: %s" % REPORT_PATH)
print("=" * 60)

# 额外：显示Top 10保单的详细理赔记录
print("\n[Top 10 保单理赔明细（前5条/每单）]：")
for pid in top10_policies:
    sub = df[df["保单号"] == pid].head(5)
    total = sub["理赔金额"].sum()
    print("\n  保单 %s (合计: %.2f 元)：" % (pid, total))
    for _, r in sub.iterrows():
        print("    %s | %s | %s | %.2f 元 | %s" % (
            r['理赔日期'], r['险种类型'], r['理赔原因'], r['理赔金额'], r['理赔状态']))
