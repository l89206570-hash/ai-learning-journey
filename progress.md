# AI 应用开发学习进度

## 当前状态
- **当前周：** W2（W1 已完成）
- **开始日期：** 2026-05-21
- **今日日期：** 2026-05-23
- **今日工作时长：** 2h
- **累计工作时长：** 12h
- **状态：** 🟢 正常推进
- **特殊：** MiMo-V2.5-Pro Token Plan 激活（5/23 → 6/23），已接入 Codex Desktop
- **兴趣线：** 游戏开发（业余，入职前不主动投入时间）→ 计划见 `game-dev-track.md`

## 本周进度（W1 — Python 速成）
- ✅ Day 1 完成：API 调用、函数定义、try/except、for 循环、enumerate、空值过滤
- ✅ Day 2 完成：文件读写（with open, .readlines(), 编码, 文件写入, 统计计数, .startswith()）
- ✅ Day 3 完成：Streamlit 入门 — 侧边栏、多标签页、文件上传、翻译历史、多语言翻译
- ✅ Day 4 完成：独立练习 — 用 API 从零写 Streamlit 工具（邮件润色 + 润色历史）

## W2 进度（W2 — 多模型与 API 进阶）
- ✅ Day 1 完成：多模型对比器 — 字典配置管理、time.time() 计时、response.usage Token 追踪、getattr 安全取值、st.checkbox、st.rerun() + session_state 分离模式、sidebar 对比历史（reversed/[::-1] 倒序）、模型差异分析（Chat vs Reasoner 设计目标）
- ✅ Day 2 完成：MiMo-V2.5-Pro 接入 — Token Plan 激活（6/23 到期）、mimo2codex 代理部署、Codex Desktop 接入、config.toml 配置

## 遇到的困难
- f-string 嵌套双引号导致 SyntaxError（已解决：内层改用单引号）
- 变量使用在赋值之前（已理解：代码执行顺序）
- 展示区错误嵌套在按钮内（已理解：st.rerun() 后展示区必须在按钮外部）
- deepseek-chat 偶尔响应 36 秒（已理解：服务端排队，非模型本身问题）

## 明日计划
- W2 Day 3：battle.py 升级为 4 模型对决（DS Chat / DS Reasoner / Qwen / MiMo-Pro），重点测 MiMo reasoning 模式

## 已完成的产出
| 周 | 产出 | 链接 |
|----|------|------|
| W1 | translator.py（API 调用 + 批量翻译） | projects/w1-translator/translator.py |
| W1 | app.py（Streamlit Web 界面 — 单条/批量翻译、多语言、历史记录） | projects/w1-translator/app.py |
| W1 | polish_app.py（邮件润色工具 — 独立练习） | projects/w1-translator/polish_app.py |
| W2 | battle.py（多模型对比器 — 独立从零编写） | projects/w2-model-battle/battle.py |
| W2 | mimo-30day-plan.md（MiMo 30 天利用计划） | mimo-30day-plan.md |

## 收入记录
| 日期 | 来源 | 金额 |
|------|------|------|

## 面试记录
| 日期 | 公司 | 岗位 | 结果 | 复盘要点 |
|------|------|------|------|----------|
