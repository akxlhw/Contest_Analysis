# ICPC 竞赛选手标签识别 —— AI Agent 项目指南

本文档面向 AI 编程助手，用于快速理解本项目结构、技术栈与开发约定。

---

## 项目概述

本项目是一个基于 **Streamlit** 的 Web 工具，用于自动识别并标注 ICPC 竞赛选手的 achievement 等级。用户上传一份包含学生竞赛记录的 Excel 文件后，系统会根据预设规则为每位学生打上标签：

- **顶尖竞赛选手**：EC-Final 金奖，或 World-Final 金/银/铜奖
- **卓越竞赛选手**：EC-Final 银/铜奖，或 World-Final 参赛但未获奖

当两个等级同时满足时，取最高等级（顶尖优先）。

---

## 技术栈

| 组件 | 说明 |
|------|------|
| Python | 3.8+ |
| Streamlit | Web UI 框架（>= 1.28.0） |
| openpyxl | Excel 读写（>= 3.1.0） |
| pandas | DataFrame 展示与导出（由 Streamlit / openpyxl 间接引入） |

**无构建步骤**，纯 Python 解释执行。

---

## 项目结构

```
.
├── app.py                 # Streamlit Web UI（仅负责交互与展示）
├── processor.py           # 核心处理逻辑（纯函数，无 UI 依赖）
├── config.py              # 配置常量、列映射、正则、归一化函数
├── generate_mock_data.py  # 生成 34 种测试场景的模拟 Excel
├── start.py               # 一键启动脚本（检查依赖 → 生成数据 → 启动服务 → 打开浏览器）
├── start.bat              # Windows 批处理版一键启动
├── requirements.txt       # Python 依赖清单
├── mock_students.xlsx     # 生成的模拟数据（运行时自动创建）
└── AGENTS.md              # 本文件
```

### 模块职责

- **config.py**：
  - 定义 5 组竞赛列的 1-based 索引（CS-DL，共 20 列）
  - 学生基本信息列映射（A-D 列：序号、姓名、学号、学院）
  - EC-Final / World-Final 的正则表达式与默认关键词列表
  - 等级别名映射（金奖/银奖/铜奖的多种写法）
  - 标签常量
  - `normalize_grade()`：等级归一化（Unicode NFKC + 大小写无关 + 别名匹配）
  - `match_competition_name()`：双层匹配（正则优先，关键词兜底）

- **processor.py**：
  - `extract_competitions()`：从一行中提取 5 组竞赛记录
  - `classify_student()`：根据竞赛记录判定标签
  - `get_qualifying_reasons()`：生成人类可读的达标原因描述
  - `find_label_column()`：动态定位标签写入列（DL 列后第一个空列）
  - `process_excel()`：主入口，读取 Excel → 打标签 → 返回字节流 + DataFrame + 统计

- **app.py**：
  - 文件上传（`.xlsx` / `.xls`）
  - Session State 管理关键词与别名（支持增删改、重置默认）
  - Dry Run 预览 / 正式处理按钮
  - 统计卡片、数据表格展示、按标签筛选
  - 下载按钮（标签文件 + 合格名单）

---

## 运行方式

### 手动启动

```bash
pip install -r requirements.txt
streamlit run app.py
```

服务默认运行在 http://localhost:8501。

### 一键启动（推荐）

```bash
# Python 方式
python start.py

# Windows 方式
start.bat
```

一键启动脚本会自动：
1. 检查 Python 与依赖是否就绪，缺失则自动安装
2. 若不存在 `mock_students.xlsx` 则调用 `generate_mock_data.py` 生成
3. 后台启动 Streamlit 服务
4. 等待服务就绪后自动打开系统默认浏览器

---

## Excel 输入格式约定

输入 Excel 必须遵循固定的列布局（1-based 列号）：

| 列号 | 含义 |
|------|------|
| 1 (A) | 序号 |
| 2 (B) | 姓名 |
| 3 (C) | 学号 |
| 4 (D) | 学院 |
| 97-100 (CS-CV) | 竞赛 1（名称、时间、级别、等级） |
| 101-104 (CW-CZ) | 竞赛 2 |
| 105-108 (DA-DD) | 竞赛 3 |
| 109-112 (DE-DH) | 竞赛 4 |
| 113-116 (DI-DL) | 竞赛 5 |

标签列会在 **DL（116 列）之后的第一个空列** 动态写入，表头写为 `竞赛标签`。

**表头行**默认为第 1 行，可在 UI 侧边栏调整。

---

## 核心匹配逻辑

### 竞赛名称识别（双层匹配）

1. **正则层**：
   - EC-Final：`r'ec[\s\-_\.]?finals?'`
   - WF：`r'world[\s\-_\.]?finals?|(?<![a-zA-Z])wf(?![a-zA-Z])'`
2. **关键词兜底层**：去除空格、横线、点、下划线后进行子串匹配

> 注意：正则已做边界防护，避免 `ECO-Final`、`SWIFT`、`workflow` 等误匹配。

### 等级归一化

输入等级经 `strip()` → Unicode NFKC 标准化 → `lower()` 后，与别名表比对：

| 标准等级 | 覆盖别名示例 |
|----------|--------------|
| 金奖 | 金奖、金牌、金、第一名、一等、一等奖、冠军、gold、1st |
| 银奖 | 银奖、银牌、银、第二名、二等、二等奖、亚军、silver、2nd |
| 铜奖 | 铜奖、铜牌、铜、第三名、三等、三等奖、季军、bronze、3rd |

---

## 测试策略

本项目**未引入单元测试框架**，测试通过 `generate_mock_data.py` 生成的模拟数据完成。

模拟数据覆盖 **34 个场景**，包括：
- 基本场景（EC-Final / WF 各等级）
- 组合场景（多竞赛同时满足）
- 边界场景（无关竞赛、全空、误匹配字符串）
- 名称变体（大小写、空格、标点、缩写、中文名称）
- Slot 分布测试（竞赛填在第 3/4/5 组列）
- 等级变体（别名映射全覆盖）

验证方式：在 UI 中上传 `mock_students.xlsx`，执行 Dry Run，人工核对统计与标签是否符合预期。

如需新增测试场景，在 `generate_mock_data.py` 的 `SCENARIOS` 列表中追加元组：

```python
("姓名", [(竞赛名, 时间, 级别, 等级), ...], "预期标签")
```

然后删除旧的 `mock_students.xlsx` 并重新运行 `python generate_mock_data.py`。

---

## 代码风格与约定

- **注释与文档**：所有 docstring、行注释、UI 文本均使用**中文**。
- **常量命名**：配置常量全大写（如 `COMPETITION_COLUMNS`、`LABEL_TOP`）。
- **函数命名**：小写 + 下划线，与 Python PEP 8 一致。
- **列索引**：Excel 操作使用 **1-based** 索引（openpyxl 原生）。
- **纯逻辑分离**：`processor.py` 不导入 Streamlit，保证核心逻辑可在无头环境复用。
- **Session State**：`app.py` 中所有可变配置（关键词、别名）均通过 `st.session_state` 持久化，避免页面刷新丢失。

---

## 安全与部署注意事项

- **无认证机制**：Streamlit 默认本地运行，若需暴露到公网，请自行配置反向代理或 Streamlit Cloud。
- **数据隐私**：上传的 Excel 仅在内存中处理，不会落盘。
- **依赖最小化**：仅依赖 Streamlit、openpyxl、pandas，无数据库、无外部 API 调用。
- **生产部署**：当前项目为轻量内部工具，未配置 Docker、CI/CD 或日志轮转。如需部署，建议：
  - 使用虚拟环境隔离依赖
  - 通过 `start.py` 中的参数（`--server.headless true`）禁止自动打开浏览器
  - 考虑使用 `streamlit config` 或环境变量限制 CORS 与文件上传大小

---

## 常见问题

| 现象 | 可能原因 | 排查方向 |
|------|----------|----------|
| 标签列未写入 | DL 后已有非空列占用了预期位置 | 检查 Excel 第 117 列及之后是否已有数据 |
| 竞赛未被识别 | 竞赛名称不在正则/关键词覆盖范围 | 在 UI 的「关键词与别名管理」中添加自定义关键词 |
| 等级识别错误 | 等级写法不在别名表中 | 在 UI 中为对应标准等级添加新别名 |
| 启动失败 | 依赖缺失或端口被占用 | 检查 `pip install` 是否成功，以及 8501 端口是否被占用 |
