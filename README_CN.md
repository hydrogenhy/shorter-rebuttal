# 📝 Markdown 字符压缩工具

🌐 **语言** | [English](./README.md) | [中文](#markdown-字符压缩工具)

一个强大的 Markdown 文件压缩工具，内置渲染等价验证。`safe` 模式优先保证渲染稳定，`aggressive` 模式优先追求更高压缩率并可能出现 mismatch 风险。

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## ✨ 主要功能

- 🖥️ **双模式操作**：命令行一键转换和交互式图形界面
- 🎯 **基于规则的压缩**：安全模式和激进模式，支持 15+ 可配置规则
- ✅ **渲染等价性验证**：在最终输出前检测潜在渲染差异
- 📊 **详细规则贡献报告**：清晰显示每条规则节省了多少字符
- 🔧 **自定义规则支持**：添加您自己的字符替换或转换函数
- 🌍 **多语言支持**：支持 UTF-8 中文、英文、数学符号等

## 📦 安装

```bash
pip install -e .
```

## 🚀 快速开始

### 🎨 图形界面模式（推荐）

启动交互式编辑和预览（使用嵌入式 iframe 方式渲染）：

```bash
streamlit run ui/app.py
```

### 💻 命令行模式

一行命令转换：

```bash
python main.py source.md target.md
```

附加选项：

```bash
python main.py source.md target.md --mode aggressive --contribution report.json
```


## 🎛️ 模式建议

- `safe`（默认推荐）：仅使用低风险规则，适合对渲染一致性要求高的最终提交。
- `aggressive`：启用中高风险规则以获得更高压缩率，但在边界场景可能出现渲染 mismatch。
- 推荐流程：先跑 `aggressive`，若验证失败则切回 `safe` 或逐步禁用高风险规则。

## ⚙️ CLI 选项

```
--mode safe|aggressive        压缩模式（safe=稳定优先，aggressive=压缩优先）
--verify/--no-verify          启用渲染等价性检查 (默认: 启用)
--strict-verify               验证失败时拒绝输出
--report FILE                 输出详细的 JSON 报告
--contribution FILE           输出规则贡献明细
--only-rule RULE_ID           仅运行指定规则 (可重复)
--skip-rule RULE_ID           跳过指定规则 (可重复)
```

## 📋 压缩规则

### 🟢 低风险规则（安全模式）
- 删除行尾多余空格
- 压缩 3+ 连续空行到最多 2 行
- 规范化标题/引用/列表标记间距
- 删除标题尾部可选的 ###
- 压缩表格分隔符和单元格空格
- 调整表格单元格内边距
- 数学块中的空格压缩

### 🟡 中等风险规则（激进模式）
- 压缩文本行内的重复空格
- 合并列表项之间的多余空行
- 删除表格可选的外层竖线
- 规范化主题分割线

这些规则在某些渲染器的边界情况下可能改变解析结果。

### 🔴 高风险规则（激进模式）
- **数学公式宏转 UTF-8** (30+ 个映射):
  - 希腊字母：α β γ δ λ π σ Σ ω Ω φ ψ 等
  - 数学运算符：× · ± ≤ ≥ ≠ ≈ ∞
  - 箭头符号：→ ← ↔

这些规则能显著提升压缩率，但也是最容易触发渲染 mismatch 的来源。

基于 Sample.md (3996 字符) 的实测：
- 安全模式：225 字符节省 (5.6%)
- 激进模式：642 字符节省 (16.1%)

## 📤 输出示例

运行带贡献报告的压缩：

```
=== Rule Contribution Report ===
Total chars saved: 642

 1. collapse-intra-line-spaces        368 chars ( 57.3%)
 2. trim-table-cell-padding           136 chars ( 21.2%)
 3. math-trim-spaces                   42 chars (  6.5%)
 4. math-macro-to-unicode              42 chars (  6.5%)
 ...
```

## 🔧 自定义规则

现在可以直接通过命令行加载自定义规则文件，文件中导出 `CUSTOM_RULES` 即可：

```bash
python main.py file.md out.md --custom-rules my_rules.py
```

规则文件中应定义：

```python
CUSTOM_RULES = [rule1, rule2, ...]
```

### 用户定义的替换规则

```python
from mdcompressor.rules.custom_rules import CustomReplacementRule

rule = CustomReplacementRule(
    rule_id="my-shorthand",
    description="替换常用学术短语",
    replacements={
        "therefore": "∴",
        "because": "∵",
    },
    targets={"text"},
    risk="low"
)
```

### 用户定义的函数规则

```python
from mdcompressor.rules.custom_rules import CustomFunctionRule

def my_compressor(text: str) -> str:
    return text.replace("  ", " ")

rule = CustomFunctionRule(
    rule_id="my-function",
    description="自定义压缩",
    func=my_compressor,
    targets={"text"},
    risk="low"
)
```

替换规则和函数规则可以同时放进同一个 `CUSTOM_RULES` 列表里，然后一次性从命令行加载。

## 📐 渲染器配置

默认：GitHub Flavored Markdown (GFM)
- 支持表格
- 支持删除线
- 数学：作为文本传递（不进行渲染计算）

## ✔️ 验证机制

工具对压缩前后的 HTML 进行规范化比较：
- 去除语义无关的空白符
- 规范化属性顺序
- 检测结构变化

使用 `--strict-verify` 会在渲染有差异时拒绝输出。

补充说明：
- 当必须保证视觉等价时，优先使用 `safe` 模式。
- `aggressive` 在公式较多或渲染器差异较大时更容易触发 mismatch。
- 发生 mismatch 时，建议保持验证开启并逐步禁用高风险规则定位问题。

## 💡 使用场景

### 📚 学术论文 Rebuttal

```bash
python main.py rebuttal.md rebuttal.compressed.md --mode aggressive --contribution report.json
```

通常可以获得更高压缩率，但提交前应始终检查验证结果。

### 📖 开发文档

```bash
python main.py docs.md docs.min.md --mode safe
```

安全模式保留所有渲染效果，适合版本控制。

### 📦 批量处理

查看 `Sample.md` 获取包含以下元素的完整示例：
- 5 层标题
- 多个表格
- 行内和显示数学表达式
- 列表（嵌套、有序、无序）
- 代码块
- 引用块
- 链接和格式化文本

## 🎨 图形界面功能

- 👁️ 实时预览原文和压缩后的 Markdown
- 📊 并排显示字符和字节数统计
- 🎚️ 规则启用/禁用开关
- 🔄 模式切换（安全/激进）
- 📄 并排渲染预览对比
- 📈 规则贡献明细
- 📋 复制和导出按钮

## 🏗️ 技术细节

### 架构设计
- 🔀 分段解析器：保护代码、数学公式和 HTML 块不被误改
- ⚙️ 流水线：按段应用规则，避免误报
- ✔️ 验证器：渲染并比较规范化后的 HTML
- 📊 报告：追踪每条规则贡献并生成排名

### 性能指标
- ⚡ 5-20KB 文件：普通笔记本上 <200ms
- 🔍 验证：已包含在总耗时中
- 🎯 增量应用：可按需选择性应用规则

## ⚠️ 限制事项

- HTML 内容会原文通过，块内不进行验证
- 某些渲染器对 Markdown 的解析可能不同
- 数学渲染依赖于渲染器的支持（不实际执行数学计算）
- 平台间对 Unicode 符号的支持差异

## 🔄 渲染器兼容性

已测试：
- GitHub (GFM)
- Jupyter Notebook
- Pandoc (markdown 模式)
- 标准 CommonMark

注意：不同渲染器对边界情况的处理可能不同。务必视觉上验证输出。

## 🤝 贡献

要添加新规则：

1. 在 `src/mdcompressor/rules/` 中创建 `BaseRule` 的子类
2. 实现 `apply()` 方法
3. 在 `src/mdcompressor/rules/registry.py` 中注册
4. 在 `tests/` 中添加测试

参考现有规则了解模式。

## 📚 文档

- [IMPLEMENTATION_BLUEPRINT.md](./IMPLEMENTATION_BLUEPRINT.md) - 架构设计文档
- [CUSTOM_RULES_GUIDE.md](./CUSTOM_RULES_GUIDE.md) - 自定义规则指南
- [Sample.md](./Sample.md) - 示例 Markdown 文件

## 📄 许可证

MIT

