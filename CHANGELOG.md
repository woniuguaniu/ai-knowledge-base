# 知识库变更记录

本文件记录知识库层面的新增、迁移、回填和结构整改。具体笔记内部的小修订仍可写在各自文末。

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
