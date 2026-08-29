# 知识库变更记录

本文件记录知识库层面的新增、迁移、回填和结构整改。具体笔记内部的小修订仍可写在各自文末。

## 2026-07-10

- 新建模块 `07_文生图与文生视频/`（经用户确认），首篇笔记《AI绘画提示词的基本结构》：六要素框架（主体/场景/光线/构图/色调/风格，源自 SD 官方教程截图）+ 网络搜索拓展的 SD 权重语法与负面提示词、文生视频提示词公式（运镜词速查 + Sora/Kling 纪律）。
- 反向回填 `00_核心概念/计算机视觉与深度学习框架.md` CV 任务表"图像生成"行，指向新笔记。
- 根 README 同步：结构树新增 07 模块 + 新增"### 07 文生图与文生视频"索引小节。

## 2026-07-06

- Harness 主线回填：吸收词源考据长文《什么是 Harness Engineering：聊聊最近爆火的技术词》（PDF 存档），未新建重复笔记，补入 `06_Agent工程/Harness工程与Agent解剖.md` 五处增量：§ 1.1 词源时间线（Mitchell Hashimoto → OpenAI → Anthropic → 源码泄露催化）+ swyx IMPACT 前传、§ 1.2 三种解释口径（马具派 / 工作空间派 / 约束执行派）、§ 2.1 "三层楼板不是三代拳王"修正视角、§ 2.2 通用 / 项目 / 任务三层 harness 划分、§ 7.6 八大器官系统对照表。
- 叙事修正：同笔记 § 3 的"泄露让术语一夜成为通用词汇"改为"泄露是催化剂而非词源"（术语 2026 年 2 月已由 Mitchell / OpenAI 带火），补泄露发现者 Chaofan Shou、日期 2026-03-31 与披露推文 1700 万浏览细节。
- 完成 3 处反向回填：`Loop Engineering与四代演化.md`（任务 harness 层 = Loop 的作业面）、`极简可控的Coding-Agent设计-pi.md`（pi = 通用 harness 层极简案例）、`Agent发展轨迹四阶段.md`（词源时间线 = 第四阶段断代史细节）。

## 2026-06-18

- RAG 主线回填：吸收微信公众号文章《PageIndex：扔掉向量数据库，RAG 准确率飙到 98.7%》，未新建重复笔记，改为补入 `03_应用实践/RAG/LLM-Wiki知识库架构.md` 作为语义导航 / Vectorless RAG 工程案例。
- 同步补充 `03_应用实践/Embedding-Reranker-向量数据库.md`：新增“向量库什么时候不是首选”，明确 PageIndex 适合结构化长文档深度问答，但不替代大规模短文档检索中的向量库 / Hybrid Search。
- 回填 `03_应用实践/RAG/RAG学习笔记.md`、`03_应用实践/README.md` 与根 `README.md`，让 PageIndex、Vectorless RAG、FinanceBench 98.7% 的适用边界可被索引检索到。

## 2026-05-29

- 结构整改：将 README 里的长更新日志拆出到 `CHANGELOG.md`，将待探索主题拆出到 `ROADMAP.md`。
- 修复 README 中知识关联示例的相对路径，避免从根目录跳到上级目录。
- 明确根目录只保留入口类 Markdown 文件：`README.md`、`index.md`、`CHANGELOG.md`、`ROADMAP.md`、`CLAUDE.md`。
- 为 `03_应用实践/`、`05_技术基础/`、`06_Agent工程/` 增加模块级 README，降低单一根 README 的导航压力。
- 将 `02_提示词工程/AI提示词框架速查手册.md` 登记进提示词工程子项目 README，避免孤立笔记。
- 新增 `_templates/正式笔记模板.md`，统一正式主题笔记的最小章节结构。
- 第二轮治理：为高时效笔记补“适用时间”提示，为模块 README 增加边缘笔记入口说明，并在 ROADMAP 中固化超长文档拆分路线。
- 长文拆分：将 `05_技术基础/GitHub项目入门/程序小白概念扫盲手册.md` 从 2300+ 行正文拆成 `概念扫盲/` 下 8 个分卷，原路径保留为 61 行兼容入口。

## 2026-05-28

- 新增 `05_技术基础/静态站点生成器与Quartz部署实战.md`：把知识库部署到 `kingrich.top/knowledge-base/quartz/` 的实战流程沉淀成 SSG 范式入门、三种部署路线对比、完整 7 步 SOP 和常见报错速查。
- 新增 `05_技术基础/CI-CD与GitHub-Actions.md`：讲清 CI/CD 与 GitHub Actions，含 workflow yaml 详解、5 大踩坑和 8 大 CI 工具横评。
- 新增 `05_技术基础/Claude调用Codex协作实战案例.md`：通过 MCP 协议实现双模型协作的完整配置流程，含首次授权、3 个实战场景和常见问题排查。
- 完成 7 处反向回填：SSG 篇回填云服务、术语、程序小白概念；CI/CD 篇回填 SSG 与术语；MCP 协作篇回填多 CLI 联动与 Claude Code 扩展生态。

## 2026-05-26

- 新增 `06_Agent工程/Claude Code goal命令.md`：Anthropic v2.1.139 长任务原语解析，含 Haiku 独立评估器机制、4 个实战例子和与 Codex `/goal` 对比。
- 完成 3 处反向回填：`Claude Code 实战速查.md`、`Claude Code 扩展生态.md`、`LLM典型失败模式.md`。

## 2026-05-25

- 填补作者 @flymyd 的 5 个待填坑，新增 5 篇 Claude 原创补充笔记：
  - `03_应用实践/LLM推理引擎选型.md`
  - `03_应用实践/HomeLab到中小企业LLM部署架构.md`
  - `03_应用实践/Embedding-Reranker-向量数据库.md`
  - `05_技术基础/NVIDIA驱动-CUDA-PyTorch工程基础.md`
  - `06_Agent工程/Function Calling与MCP工程指南.md`
- 每篇均含「作者声明 + 局限性」节，明确标注非作者原稿。
- 完成 9 处反向回填，保持双向引用。
