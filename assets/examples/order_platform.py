#!/usr/bin/env python3
"""Example board: 订单履约中枢 · 组件架构 (fictional system).

    python3 order_platform.py [out.drawio]

Reference for the house style: big title, value chips, three numbered tinted
zones, one dark focal block, icon cards, labeled colored arrows.
"""

import os
import sys

_candidates = [
    os.environ.get("BOARDKIT_DIR"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"),
    os.path.expanduser("~/skills-manager/architecture-board-builder/scripts"),
]
for _p in _candidates:
    if _p and os.path.isdir(_p):
        sys.path.insert(0, _p)
        break

from boardkit import (  # noqa: E402
    AMBER, BLUE, BLUE_D, BODY, GREEN, INK, NAVY, SLATE, TEAL, TINT, VIOLET, Board,
)

b = Board(2100, 2260, title="order-platform", name="订单履约中枢（示例）")

# ---------------------------------------------------------------- header
b.rect(100, 44, 56, 8, BLUE, "none", 0, 0)
b.text(100, 68, 900, 24, "SAMPLE BOARD / COMPONENT ARCHITECTURE", 14, "#7E8FA6", True)
b.text(100, 96, 1600, 82, "订单履约中枢 · 组件架构", 56, INK, True)
b.text(100, 186, 1600, 34, "统一入口 · 按租户隔离 · 共享规则与知识 · 跨系统执行", 21, "#465A75")
b.badge(1790, 78, 210, 40, "示例 · 虚构系统", "#FFFFFF", "#7E8FA6", 13, 50, 1, "#DCE6F4")

chips = [
    (100, 250, "双入口 · 零迁移", BLUE),
    (370, 300, "每租户独立 Worker", GREEN),
    (690, 270, "规则 + 知识共享", VIOLET),
    (980, 260, "执行统一收口", AMBER),
]
for x, w, label, accent in chips:
    light, border, text = TINT[accent]
    b.pill(x, 262, w, 46, label, light, border, text, 15)
b.text(1300, 274, 664, 22, "示例画板 · 强调职责边界与协作关系", 13, "#9AA8BA", False, "right")

# ---------------------------------------------------------------- 01 entry
b.section(100, 356, 1900, 334, "01", "统一工作入口",
          "同一个控制台入口，两种交互方式",
          "旧命令照常可用，新体验随时启用")

b.card(136, 472, 880, 196, "控制台自然语言", "提出目标 / 定制需求",
       bullets=["用自然语言描述任务，不必记命令与参数",
                "Gateway 识别身份与租户后交给租户 Worker"],
       accent=BLUE, icon="言", caption="Gateway → 租户 Worker")

b.card(1084, 472, 880, 196, "旧版命令 · 保留", "orders d(/ship)",
       bullets=["老入口零改动，熟手继续用命令",
                "Gateway 直接路由到 Job Engine"],
       accent=TEAL, icon="令", caption="Gateway → Job Engine")

# ---------------------------------------------------------------- gateway
b.rect(100, 736, 1900, 168, "#EAF2FE", "#A9C6F4", 2, 3)
b.badge(136, 792, 56, 56, "G", BLUE, "#FFFFFF", 26)
b.text(212, 772, 460, 34, "Edge Gateway", 29, INK, True)
b.text(212, 808, 470, 26, "消息接入与租户路由", 17, BODY)
b.text(212, 838, 470, 22, "无状态 · 可水平扩展", 13, "#6C82A0")

steps = [(700, 340, "① 识别用户与租户"), (1090, 390, "② 查询 / 创建租户 Worker"),
         (1530, 390, "③ 分发任务 · 回传状态")]
for x, w, label in steps:
    b.pill(x, 796, w, 50, label, "#FFFFFF", "#C7DAF4", BLUE_D, 15)
b.edge([(1040, 821), (1088, 821)], BLUE, 2.6)
b.edge([(1480, 821), (1528, 821)], BLUE, 2.6)

# ---------------------------------------------------------------- 02 platform
b.section(100, 940, 1900, 780, "02", "Fulfillment Platform",
          "租户专属 Worker + 共享能力服务", "Worker 隔离 · 能力共享",
          accent=VIOLET, badge_fill="#123A7A")

b.card(136, 1056, 524, 250, "Policy Wiki · 规则库", "业务规则 / 文档 / 条款",
       bullets=["检索：为 Worker 补齐上下文", "沉淀：履约记录变成经验", "追溯：规则变更可查"],
       accent=VIOLET, icon="知", caption="规则闭环", fill="#FBF9FF")
b.card(136, 1346, 524, 304, "PostgreSQL", "history + 业务数据",
       bullets=["向量记忆，跨会话召回", "会话上下文与用户偏好",
                "任务、权限与审计记录", "变更历史索引"],
       accent=VIOLET, icon="存", caption="控制平面统一读写", fill="#FBF9FF")
b.card(1440, 1056, 524, 250, "ToolKit · 工具中心", "能力即插件，按需装载",
       bullets=["基础 Tools", "租户 Tools · 加载复用", "升级工具不动运行时上下文"],
       accent=GREEN, icon="技", caption="可组合")
b.card(1440, 1346, 524, 304, "Job Engine", "共享执行与鉴权",
       bullets=["Worker / 用户身份校验", "外部系统触发与跟踪",
                "任务卡片 / 状态通知", "同时通知用户与 Worker"],
       accent=AMBER, icon="执")
b.rect(1468, 1576, 468, 50, "#FDF3E3", "none", 0, 4)
b.text(1468, 1576, 468, 50, "唯一执行收口：所有请求在此鉴权", 15, AMBER, True, "center")

# focal block
b.rect(760, 1056, 580, 594, NAVY, "#0A2455", 2, 4)
b.pill(790, 1084, 116, 32, "CORE", "#1D4C96", "#1D4C96", "#9FC0F5", 13)
b.text(790, 1128, 520, 44, "Fulfillment Worker × N", 29, "#FFFFFF", True)
b.text(790, 1178, 520, 28, "每租户实例 · 独立上下文 · 并发处理", 16, "#A9C6F5")
b.rect(790, 1224, 520, 2, "#2A5AA8", "none", 0, 0)

for i, label in enumerate(["理解目标", "检索规则", "选择工具",
                           "调用接口", "执行任务", "后续动作"]):
    b.badge(790 + (i % 2) * 270, 1250 + (i // 2) * 68, 250, 52,
            f"{i + 1:02d}  {label}", "#163E82", "#DDEAFF", 15, 12, 1.5, "#2C5EA8")

b.rect(790, 1466, 520, 88, "#0B2557", "#1D4485", 1.5, 4)
b.text(790, 1478, 520, 26, "每个租户一个 Worker，互不干扰", 15, "#EAF2FF", False, "center")
b.text(790, 1506, 520, 26, "共享能力升级无需触碰租户上下文", 15, "#9FC0F5", False, "center")
b.text(790, 1596, 520, 24, "越权或失败 → 回退旧版命令", 13, "#7FA3D8", False, "center")

b.arrow([(660, 1181), (760, 1181)], VIOLET, "检索规则")
b.arrow([(660, 1498), (760, 1498)], VIOLET, "记忆上下文")
b.arrow([(1340, 1181), (1440, 1181)], GREEN, "加载工具", dashed=True)
b.arrow([(1340, 1498), (1440, 1498)], AMBER, "受控任务")

# ---------------------------------------------------------------- 03 execution
b.section(100, 1800, 1900, 300, "03", "执行平台与能力生态",
          "任务执行、资源承载与跨系统扩展", "虚线框 = 规划能力", accent=AMBER)

b.card(136, 1912, 580, 154, "物流网关", "Carrier A · Carrier B · Webhook",
       bullets=["下单执行 · 状态回传", "按区域选择承运商"], accent=AMBER, icon="发")
b.card(756, 1912, 580, 154, "计算与运行资源", "K8s 集群 / 批处理集群",
       bullets=["承载 Worker 与业务应用", "任务产物最终落地"], accent=SLATE, icon="算")
b.rect(1376, 1912, 580, 154, "#FDFCFF", "#D8CBF5", 2, 5, dashed=True)
b.circle(1404, 1928, 44, "#F1EAFE", "#C9B3F2", "接", VIOLET, 18)
b.text(1462, 1926, 470, 30, "合作方 API · 扩展愿景", 22, INK, True)
b.text(1462, 1960, 470, 24, "对账 · 发票 · 客服工单", 15, "#6B5A8E")
b.text(1404, 1996, 524, 24, "跨团队流程与业务协同", 15, BODY)
b.text(1404, 2024, 524, 24, "虚线框表示规划能力", 15, BODY)

# ---------------------------------------------------------------- links + footer
b.edge([(1050, 690), (1050, 736)], BLUE, 2.6)
b.edge([(1050, 904), (1050, 940)], BLUE, 2.6)
b.edge([(1050, 1720), (1050, 1800)], AMBER, 2.6)

b.text(100, 2152, 980, 24, "设计愿景：跨团队流程与外部系统扩展；虚线框表示规划能力", 14, "#8A99AD")
b.text(1200, 2152, 764, 24, "深蓝 = 核心 Worker · 绿 = 工具 · 紫 = 规则与数据 · 琥珀 = 执行",
       13, "#98A6B8", False, "right")

out = sys.argv[1] if len(sys.argv) > 1 else "order-platform.drawio"
path, size, cells = b.save(out)
print(f"board: {path} ({size} bytes, {cells} cells, {b.w}x{b.h})")
