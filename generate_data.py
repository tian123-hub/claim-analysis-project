"""
============================================
 保险理赔模拟数据生成器
 用途：生成10万条真实感理赔数据用于分析演练
 作者：精算实战项目
============================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import sys

# ====== 设置随机种子（保证每次生成的数据一致，可复现）======
np.random.seed(42)
random.seed(42)

# ====== 参数配置 ======
NUM_RECORDS = 100_000        # 生成10万条理赔记录
OUTPUT_PATH = "data/claims_data.csv"

print("=" * 50)
print("开始生成 %d 条理赔数据..." % NUM_RECORDS)
print("=" * 50)

# ====== 1. 生成保单号（格式：P2024XXXXXX）======
policy_ids = [f"P2024{str(i).zfill(6)}" for i in range(1, NUM_RECORDS + 1)]

# ====== 2. 生成理赔金额（右偏分布，模拟真实保险理赔）======
# 用对数正态分布：大部分小额理赔 + 少数大额理赔
# 均值约 5000，标准差较大，有极值（模拟真实场景）
claim_amounts = np.random.lognormal(mean=8.0, sigma=1.5, size=NUM_RECORDS)
claim_amounts = np.clip(claim_amounts, 100, 5_000_000)  # 限制在100~500万之间
claim_amounts = np.round(claim_amounts, 2)

# ====== 3. 生成理赔日期（2024年全年）======
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days
random_days = np.random.randint(0, date_range + 1, size=NUM_RECORDS)
claim_dates = [start_date + timedelta(days=int(d)) for d in random_days]
claim_dates_str = [d.strftime("%Y-%m-%d") for d in claim_dates]

# ====== 4. 生成险种类型 ======
insurance_types = ["车险", "健康险", "寿险", "意外险", "家财险", "责任险", "航运险"]
insurance_weights = [0.30, 0.25, 0.15, 0.12, 0.08, 0.07, 0.03]  # 车险最多
claim_types = np.random.choice(insurance_types, size=NUM_RECORDS, p=insurance_weights)

# ====== 5. 生成理赔原因 ======
reasons_map = {
    "车险": ["交通事故", "车辆被盗", "自然灾害", "火灾"],
    "健康险": ["住院医疗", "重大疾病", "门诊手术", "慢性病"],
    "寿险": ["身故赔付", "满期给付", "年金领取"],
    "意外险": ["意外受伤", "意外身故", "意外医疗"],
    "家财险": ["火灾损失", "水浸损失", "盗窃损失", "管道破裂"],
    "责任险": ["第三方人身伤害", "财产损失", "法律诉讼"],
    "航运险": ["货物损毁", "船舶事故", "延误损失", "海盗风险"],
}
claim_reasons = []
for ct in claim_types:
    claim_reasons.append(np.random.choice(reasons_map[ct]))

# ====== 6. 生成理赔状态 ======
statuses = ["已结案", "理赔中", "已拒赔", "撤销"]
status_weights = [0.75, 0.15, 0.07, 0.03]
claim_statuses = np.random.choice(statuses, size=NUM_RECORDS, p=status_weights)

# ====== 7. 生成被保人年龄（18~70岁）======
ages = np.random.randint(18, 71, size=NUM_RECORDS)

# ====== 8. 生成性别 ======
genders = np.random.choice(["男", "女"], size=NUM_RECORDS, p=[0.52, 0.48])

# ====== 组装 DataFrame ======
df = pd.DataFrame({
    "保单号": policy_ids,
    "理赔金额": claim_amounts,
    "理赔日期": claim_dates_str,
    "险种类型": claim_types,
    "理赔原因": claim_reasons,
    "理赔状态": claim_statuses,
    "被保人年龄": ages,
    "性别": genders,
})

# ====== 按理赔日期排序 ======
df = df.sort_values("理赔日期").reset_index(drop=True)

# ====== 添加一个"理赔ID"作为唯一标识 ======
df.insert(0, "理赔ID", [f"CLM{str(i).zfill(8)}" for i in range(1, len(df) + 1)])

# ====== 保存为CSV ======
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print("生成完成！共 %d 条记录" % len(df))
print("文件保存至: %s" % OUTPUT_PATH)
print("理赔金额范围: %.2f ~ %.2f 元" % (claim_amounts.min(), claim_amounts.max()))
print("平均理赔金额: %.2f 元" % claim_amounts.mean())
print("险种分布: %s" % df['险种类型'].value_counts().to_dict())
print("\n数据前5行预览：")
print(df.head())
