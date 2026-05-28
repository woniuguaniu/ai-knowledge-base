# CI/CD 与 GitHub Actions

> "推一次代码,自动构建、检测、部署、有问题通知"——这套机制叫 **CI/CD**。本笔记从概念入手讲清楚:它是什么、为什么"持续"是关键、主流工具横评、怎么写一个 yaml workflow、踩坑总结。**主案例用 Quartz 部署到 GitHub Pages**(跟 [静态站点生成器与 Quartz 部署实战](静态站点生成器与Quartz部署实战.md) 配套使用)。

---

## § 1. CI / CD / CI/CD 是什么

### 1.1 一句话定义

**CI = Continuous Integration(持续集成)**:让一台机器在你每次提交代码后,自动跑一遍"**构建 + 测试 + 静态检查**",出问题立刻通知,不用人盯着。

**CD = Continuous Delivery(持续交付)** 或 **Continuous Deployment(持续部署)**:CI 通过后,产物自动准备好或自动上线。

**CI/CD**(连起来说):整条从"代码提交"到"线上服务"的自动化流水线。

### 1.2 Delivery vs Deployment 的区别(很多人弄混)

| | Continuous Delivery | Continuous Deployment |
|---|---------------------|----------------------|
| **中文** | 持续交付 | 持续部署 |
| **关键差异** | CI 通过 → 产物准备好,**等人点按钮**上线 | CI 通过 → **直接自动**上线,不用按按钮 |
| **比喻** | 货物送到仓库门口,等老板签字才开门 | 货物直接进仓库上货架 |
| **适合场景** | 金融 / 医疗等高风险行业,要人工审批 | 互联网产品 / 内部工具 / 文档站 |

**很多公司把 CI/CD 当一个词说**,边界没那么严格。**核心区别只在最后一步**:**自动上线 vs 等人按按钮**。

### 1.3 为什么叫"持续"(Continuous)

对比"没 CI 的世界"和"有 CI 的世界":

| 阶段 | 没 CI | 有 CI |
|------|-------|-------|
| **开发** | 团队 5 个人各写各的,一周后才合并 | 每人 push 一次代码就立刻验证 |
| **集成时机** | 周五"集成日"统一合并 | 每次 push 都是一次集成 |
| **冲突暴露** | 集成日发现 5 人改了同一文件 → 合并地狱 | 5 分钟内暴露,小冲突分摊解决 |
| **测试** | 上线前手动跑,经常忘 | 每次 push 自动跑,绝不漏 |
| **部署** | 运维 ssh 上服务器手动 scp + 重启 | yaml 写一次,无限重复 |
| **出问题** | 用户报 bug 才发现 | 测试挂 1 分钟内邮件通知 |

**"持续"的核心** = **每一次小提交都验证一次**,把"集成痛苦"分摊成 1000 次小验证,而不是一次大爆炸。这个理念出自 2000 年左右极限编程(eXtreme Programming, XP)运动,Martin Fowler 等人提出。现在是软件行业的标配,不会用 CI 几乎等于"不会现代开发"。

---

## § 2. 类比:CI 就是"不睡觉的实习生"

想象你雇了一个**24 小时不睡觉、不抱怨、不会忘事、按规则办事**的实习生。

你给他一张工作清单(yaml 文件),写明:

> 每次有人往代码仓库 push,你立刻:
> 1. 把代码拉下来
> 2. 装好所有依赖
> 3. 跑一遍编译/构建
> 4. 跑一遍所有测试
> 5. 跑一遍代码风格检查、安全扫描
> 6. 如果都过了 → 把产物部署到服务器 / 发布到应用商店 / 推到 CDN
> 7. 如果哪一步挂了 → 立刻发邮件 / Slack / 微信通知我"x 月 x 日 14:32 的提交挂在 step 4"

这个"实习生"就是 **CI 系统**。CI 工具 = 雇这个实习生的服务。

### 2.1 主流 CI 工具横评

| 工具 | 谁的 | 价格 | 难度 | 备注 |
|------|------|------|------|------|
| **GitHub Actions** | GitHub 自带 | 公开仓库免费,私有仓有免费额度 | ⭐⭐ | 配置最简单,跟仓库深度集成,目前最主流 |
| **GitLab CI** | GitLab 自带 | 公开仓免费,有自由额度 | ⭐⭐ | 跟 GitLab 集成最深,功能成熟 |
| **Jenkins** | 开源,自部署 | 自己装在服务器,无授权费 | ⭐⭐⭐⭐ | 老牌,功能最强但配置最复杂,大企业常见 |
| **CircleCI** | 第三方 | 有免费额度 | ⭐⭐ | 早年很火,被 GH Actions 蚕食 |
| **Travis CI** | 第三方 | 公开仓免费 → 后期收费政策变动 | ⭐⭐ | 曾经是开源项目首选,现在用得少了 |
| **Drone / Woodpecker** | 开源,自部署 | 自己装 | ⭐⭐⭐ | 轻量 Jenkins 替代品 |
| **Tekton / Argo Workflows** | Kubernetes 生态 | 自部署 | ⭐⭐⭐⭐⭐ | K8s 原生,复杂场景 |
| **Cloudflare Pages / Vercel / Netlify** | 简化版 CI | 个人免费 | ⭐ | 只为前端站设计,yaml 都不用写,选模板就行 |

**个人/小团队选型建议**:

- **代码在 GitHub** → 直接用 **GitHub Actions**,90% 场景够用
- **代码在 GitLab** → 用 **GitLab CI**
- **要复杂流水线 + 多机房** → **Jenkins**(但要有运维)
- **只是前端站** → **Cloudflare Pages / Vercel / Netlify**,不用写 workflow

---

## § 3. "推一次代码就触发"的机制

以 **GitHub Actions** 为例,看一次 push 在背后发生了什么:

```
你电脑                GitHub 服务器              GitHub Actions 云
  │                       │                           │
  ├── git push main ────→ │                           │
  │                       │                           │
  │                       ├── 检测到 push 事件         │
  │                       ├── 读 .github/workflows/*.yml│
  │                       │   找出"匹配此事件的任务"      │
  │                       │                           │
  │                       ├── 派发任务 ──────────────→│
  │                       │                           │
  │                       │                           ├── 启动一台临时 Linux VM(干净)
  │                       │                           ├── git clone 你的仓库
  │                       │                           ├── 依次跑 yaml 里写的每一步:
  │                       │                           │   step 1: 装 Node
  │                       │                           │   step 2: npm install
  │                       │                           │   step 3: build
  │                       │                           │   step 4: 部署
  │                       │                           ├── 任意一步失败 → 整体标红
  │                       │                           ├── 全部通过 → 标绿
  │                       │                           ├── 上传产物 / 部署到 Pages
  │                       │                           ├── VM 销毁(下次 push 再开新的)
  │                       │  ←── 状态回报 ─────────── │
  │                       │                           │
  │ ←── 邮件/通知 ─────── │                           │
  │                       │                           │
  在 GitHub 仓库页 commit 旁
  看到 ✓ 或 ✗ 标记
```

### 3.1 核心要素四件套

| 概念 | 中文 | 一句话 | 在 yaml 里长什么样 |
|------|------|--------|-------------------|
| **trigger / event** | 触发器 | 什么事件发生时跑这个 workflow | `on: push: branches: [main]` |
| **job** | 任务 | 一个独立的并行单元 | `jobs: build:` |
| **runner** | 运行器 | 跑任务的那台云端 VM | `runs-on: ubuntu-latest` |
| **step** | 步骤 | job 里依次跑的命令 | `steps: - run: npm test` |

一个 workflow 可以有**多个 job**(并行跑),每个 job 里有**多个 step**(顺序跑)。

---

## § 4. 一个最小可工作的 workflow(以 Quartz 部署为案例)

下面这个 yaml 文件放在仓库根目录 `.github/workflows/deploy.yml`,就是一个**完整的 CI/CD 流水线**:每次 push 到 main 自动构建 Quartz 并部署到 GitHub Pages。

```yaml
# .github/workflows/deploy.yml

# ① 名字(显示在 GitHub 仓库 Actions 标签页里,人类看)
name: Deploy Quartz to GitHub Pages

# ② 触发器:什么事件发生时跑
on:
  push:
    branches: [main]      # main 分支被 push 时
  workflow_dispatch:      # 也支持手动触发(在 Actions 页面点按钮)

# ③ 权限:这个 workflow 需要哪些权限
permissions:
  contents: read          # 能读仓库内容
  pages: write            # 能写 GitHub Pages
  id-token: write         # 能拿 OIDC token(部署 Pages 需要)

jobs:
  # ④ 第一个 job: 构建
  build:
    runs-on: ubuntu-latest    # 跑在 GitHub 提供的 Ubuntu VM 上
    steps:
      # 4.1 拉代码
      - name: 拉仓库
        uses: actions/checkout@v4
        with:
          fetch-depth: 0    # ⚠️ 取全部 git 历史,Quartz 读 commit 时间会用

      # 4.2 装 Node
      - name: 装 Node 22
        uses: actions/setup-node@v4
        with:
          node-version: 22

      # 4.3 装依赖 + build
      - name: 构建 Quartz
        working-directory: ./_quartz
        run: |
          npm ci
          npx quartz build

      # 4.4 上传产物给下一个 job
      - name: 上传产物
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./_quartz/public

  # ⑤ 第二个 job: 部署(依赖 build job)
  deploy:
    needs: build              # 必须 build 跑通才会跑 deploy
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: 部署到 Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 4.1 这个 yaml 在讲什么(逐行白话)

- **`name`**:这个 workflow 叫什么,显示给人看
- **`on:`**:**触发条件**——main 分支被 push 时跑,以及支持在 GitHub Web 界面手动点按钮触发(`workflow_dispatch`)
- **`permissions:`**:**权限声明**——只给最小必要权限(Pages 写权限),其他默认禁止。这是 GitHub Actions 的安全最佳实践
- **`jobs:`**:有 2 个 job,`build` 和 `deploy`
- **`runs-on:`**:这个 job 跑在哪种 VM 上(Linux / macOS / Windows 任选)
- **`steps:`**:job 内部按顺序跑的命令
- **`uses:`**:用别人写好的"action 模块"(像 npm 包,叫 **Action**)。如 `actions/checkout@v4` 是 GitHub 官方的"拉代码"模块,`@v4` 是版本号
- **`run:`**:跑一个原始 shell 命令
- **`needs:`**:**job 依赖**——`deploy` 必须等 `build` 跑完才开始。这就是为什么能拆出"构建 + 部署"两个 job
- **`environment:`**:把这个 job 标记为某个"环境"(production / staging 等),Pages 部署专用

### 4.2 关键提示:Action 模块是"积木"

GitHub Actions 的强大之处在于 **Marketplace 上有 1 万+ 个现成的 Action 模块**——你需要的几乎所有功能都有人写好了:

| 你想做什么 | 用哪个 Action |
|-----------|--------------|
| 拉仓库代码 | `actions/checkout` |
| 装 Node / Python / Go / Rust | `actions/setup-node` / `setup-python` / `setup-go` / `actions-rust-lang/setup-rust-toolchain` |
| 部署到 GitHub Pages | `actions/deploy-pages` |
| 推 Docker 镜像 | `docker/build-push-action` |
| 部署到 AWS / Cloudflare / Vercel | 各家官方都提供 |
| 发 Slack / 钉钉 / 飞书通知 | 社区有多个版本 |
| 跑 ESLint / Prettier | 直接 `run: npx eslint .` 即可 |

**写 workflow 90% 时间是"拼积木"**,只有少数原创 shell 命令。

---

## § 5. CI 能跑什么 — 8 大典型阶段

不同项目阶段不同。**yaml 里写什么就跑什么**,完全自由组合。

| 阶段 | 干什么 | 典型工具 |
|------|--------|---------|
| **拉代码** | 把当前提交的代码拉到 VM 里 | `actions/checkout` |
| **装环境** | 装 Node / Python / Java 等运行时 | `setup-node` / `setup-python` 等 |
| **装依赖** | npm / pip / mvn / cargo 装包 | `npm ci` / `pip install -r requirements.txt` |
| **静态检查** | 代码风格、bug 模式、类型 | ESLint / Prettier / mypy / clippy / SonarCloud |
| **安全扫描** | 依赖漏洞、密钥泄露、SAST | `npm audit` / Snyk / TruffleHog / GitHub CodeQL |
| **构建** | 编译 / 打包 | `npm run build` / `mvn package` / `cargo build` / `npx quartz build` |
| **测试** | 单元 + 集成 + e2e | `npm test` / `pytest` / `cargo test` / Playwright |
| **打镜像** | Docker / OCI 镜像 | `docker build` + `docker push` |
| **部署** | 推到服务器 / 云 / CDN | `rsync` / `kubectl apply` / `aws s3 sync` / `actions/deploy-pages` |
| **发版** | 打 tag / 发包 / 写 changelog | `npm publish` / `gh release create` / semantic-release |
| **通知** | 告诉团队 | Slack / 钉钉 / 飞书 webhook / 邮件 |

### 5.1 几个有趣的"非传统"用法

- **定时跑**:每天凌晨 3 点跑一遍数据备份脚本(用 `on: schedule: cron`)
- **PR 自动审查**:有人开 Pull Request → 自动跑 Linter 并在 PR 里评论"哪行风格不对"
- **依赖自动升级**:Dependabot / Renovate 检测到依赖有新版 → 自动开 PR 升级 + 跑测试 → 测试过了通知人合并
- **链接体检**:每周自动扫描整个文档站找死链
- **AI 自动 review**:Pull Request 触发 → 调 Claude / GPT API 自动 review 代码 → 在 PR 里评论建议
- **跨平台编译**:同一个 workflow 在 Linux / macOS / Windows 上各跑一遍,产物分别上传(叫 **matrix build**)

---

## § 6. 触发器类型 — `on:` 后面能写什么

GitHub Actions 支持 30+ 种事件触发,常见的:

| 触发器 | yaml 写法 | 什么时候触发 |
|--------|----------|------------|
| **push** | `on: push` | 任何 push 都触发 |
| **特定分支 push** | `on: push: branches: [main, dev]` | 只在 main / dev push 触发 |
| **PR** | `on: pull_request` | 有人开 PR 或往 PR 推新提交 |
| **PR 合并到主分支** | `on: pull_request: types: [closed]` | PR 关闭(含合并)时 |
| **打 tag** | `on: push: tags: ["v*"]` | 打 v1.0.0 这种 tag 时(用于发版) |
| **定时** | `on: schedule: - cron: "0 3 * * *"` | 每天凌晨 3 点(UTC) |
| **手动** | `on: workflow_dispatch` | 在 GitHub Web 界面点按钮 |
| **被另一个 workflow 触发** | `on: workflow_call` | 把 workflow 当函数复用 |
| **release 发布** | `on: release: types: [published]` | 在 GitHub Web 界面创建 release 时 |
| **issue / PR 评论** | `on: issue_comment` | 有人评论(可以做"评论 /deploy 触发部署") |

**`on:` 后还能加 paths 过滤**:`on: push: paths: ["src/**", "package.json"]` —— 只在这些路径变更时才触发,改 README 不浪费 CI 资源。

---

## § 7. 5 大踩坑速查

### 7.1 Secrets 管理(最容易出事故)

**绝对不要**:把密码 / API key / 私钥直接写在 yaml 里——yaml 是 git 仓库的一部分,提交上去就**永久泄露**。

**正确做法**:
1. 在 GitHub 仓库 Settings → Secrets and variables → Actions 添加密钥(如 `DEPLOY_KEY` / `OPENAI_API_KEY`)
2. yaml 里通过 `${{ secrets.DEPLOY_KEY }}` 引用
3. GitHub 会自动在日志里把 secret 值用 `***` 替换,不会泄露

**真实事故**:历史上很多公司把 AWS key 不小心 push 到公开仓 → 几分钟内被爬虫扫到 → 黑客跑了一晚上 EC2 实例 → 收到 $30000 账单。

### 7.2 `fetch-depth: 0` 这个坑

`actions/checkout@v4` 默认 `fetch-depth: 1`(只拉最新一次 commit,**没有 git 历史**)。

**什么时候必须设 `fetch-depth: 0`(拉全部历史)**:
- Quartz 要从 git log 读"创建时间 / 修改时间"
- semantic-release / standard-version 要从 commit 历史算下一个版本号
- 任何需要 `git log` / `git diff main..HEAD` 的脚本

**症状**:跑出来的产物日期全是 1970-01-01,或者脚本报 "fatal: not a git repository / unknown revision"。

### 7.3 缓存优化(否则每次 npm install 都很慢)

每次 CI 跑都是干净 VM → `npm install` 从零下载所有包 → 慢。**加缓存**:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: 'npm'        # 自动缓存 ~/.npm,加这一行就行
```

第一次还是慢,之后从 1 分钟降到 10 秒。Python / Java / Rust 都有类似缓存方案。

### 7.4 Matrix builds 别滥用

`matrix:` 让同一个 job 在多种参数组合下跑:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node: [18, 20, 22]
```

这会跑 **3 × 3 = 9 次**!免费额度容易用爆。常用于库的跨平台/跨版本测试,不要无脑全开。

### 7.5 别在 main 上直接调试 workflow

刚开始写 workflow,大概率会失败 5-10 次才跑通。**不要直接推 main 触发**——commit 历史会满是 "fix workflow / fix workflow / fix again" 的垃圾。

**正确做法**:开一个 `ci/test-workflow` 分支,在分支里改 yaml,push 触发(`on: push` 配 `branches: [ci/**]` 让它在所有 ci/ 开头的分支都触发)。调通后再 cherry-pick / squash 到 main。

或者用 [act](https://github.com/nektos/act) 这个工具,在本地用 Docker 模拟运行 GitHub Actions(不完美,但能省 80% 的来回 push)。

---

## § 8. 进阶概念速览

下面这些不是必学,但读懂了会理解 CI 在大型项目里长什么样:

| 概念 | 一句话 |
|------|--------|
| **artifact** | job 之间传递文件用的"工件"——build job 产出 dist/,deploy job 拿来用,通过 `upload-artifact` + `download-artifact` 传递 |
| **environment** | 把部署目标分组(production / staging / preview),可以设审批人、密钥隔离 |
| **OIDC** | OpenID Connect。CI 不存 AWS 长期 key,通过 OIDC 临时换 AWS 凭证,更安全 |
| **self-hosted runner** | 自己提供运行器机器(企业内部用,有合规需求) |
| **reusable workflow** | 一个 workflow 用 `on: workflow_call` 后,可以被其他 workflow `uses:` 复用,像函数 |
| **composite action** | 把几个 step 打包成一个自定义 Action,跨 workflow 共享 |
| **monorepo CI 拆分** | 大仓库一个 workflow 跑全部 = 慢。用 `paths:` 过滤 + 多个 workflow 拆分,各管各的 |
| **GitOps** | 把"想要的状态"写进 Git(K8s yaml),CI 检测到变更后 `kubectl apply`——基础设施也走 CI 流程 |

---

## § 9. 与本知识库其他章节的关联

- **研发总纲**:[软件工程产品研发 SOP](软件工程产品研发SOP.md) 把 CI/CD 放在"阶段 6：质量门禁与自动化验证"中,说明它在从需求到上线的完整产品研发流程里承担什么角色
- **配套实战**:[静态站点生成器与 Quartz 部署实战](静态站点生成器与Quartz部署实战.md) § 4 "三种部署路线对比"提到了 GitHub Pages / Cloudflare Pages 路线——本笔记就是把"自动 build & 部署"这个机制单独讲透
- **概念铺垫**:[云服务交付模型](云服务交付模型.md) 讲 IaaS / PaaS / SaaS——GitHub Actions / Cloudflare Pages 这些"CI/CD 平台"实际是 **PaaS 在"开发流水线"场景的产品化**
- **基础环境**:[GitHub项目入门/程序小白概念扫盲手册](GitHub项目入门/程序小白概念扫盲手册.md) 讲了 npm / Docker / git 等本笔记假设你已经会的基础工具
- **Git 操作**:[GitHub项目入门/Git进阶速查](GitHub项目入门/Git进阶速查.md) 的 `tag` / `cherry-pick` 等命令,在 CI 发版 / 调试 workflow 时常用
- **术语速查**:[程序员黑话速查](程序员黑话速查.md) 已有 SaaS / IaaS / PaaS 等条目,本笔记追加 CI/CD 相关术语
- **Agent 工程关联**:CI 是 "**让机器自动做事**" 最早最成熟的范式;[什么是 Agent](../06_Agent工程/什么是Agent.md) 讲的 Agent 是这套思路在 LLM 时代的延伸——都是"定义触发条件 + 自动跑步骤 + 出问题反馈"

---

## § 10. 术语速查

| 术语 | 中英对照 | 一句话 |
|------|---------|--------|
| **CI** | Continuous Integration,持续集成 | 自动跑 build + test + check 的机制 |
| **CD** | Continuous Delivery / Deployment,持续交付/部署 | CI 通过后自动准备产物或自动上线 |
| **CI/CD** | —— | 从代码到线上服务的整条自动化流水线 |
| **pipeline** | 流水线 | CI/CD 流程的整体,有时也指 workflow 的别名 |
| **workflow** | 工作流 | 一个完整的 yaml 文件定义的流程 |
| **job** | 任务 | workflow 里的一个并行单元 |
| **step** | 步骤 | job 里的一条命令 |
| **runner** | 运行器 | 跑任务的那台机器(VM 或物理机) |
| **action**(GH 专有) | —— | 别人封装好的可复用步骤(像 npm 包) |
| **artifact** | 工件 / 产物 | job 之间传递的文件 |
| **trigger / event** | 触发器 / 事件 | 让 workflow 跑起来的事件(push / PR / 定时等) |
| **secret** | 密钥 | 安全存储的敏感信息(API key / 密码) |
| **matrix build** | 矩阵构建 | 一个 job 在多种参数组合下并行跑 |
| **green build** | 绿色构建 | CI 全部通过(对应 GitHub 的绿色 ✓) |
| **red build / broken build** | 红色构建 / 挂了 | CI 有失败(红色 ✗),阻止合并 |
| **OIDC** | OpenID Connect | CI 不存长期凭证,临时换取云厂商凭证 |
| **self-hosted runner** | 自托管运行器 | 用自己机器当 CI runner(企业内 / 合规需求) |
| **GitOps** | —— | 基础设施(K8s yaml)放 Git,CI 自动同步 |
| **cron expression** | cron 表达式 | 定时任务的时间表达式(如 `0 3 * * *` 每天 3 点) |
| **webhook** | —— | "我这边有事件时通知你"的 HTTP 回调机制,CI 触发的底层 |
| **YAML** | —— | 配置文件格式,语法对缩进敏感,workflow 都用它写 |

---

*创建时间:2026-05-28(继 SSG 部署实战笔记后,把"GitHub Actions / CI/CD" 这个概念单独拆出来讲透。本笔记定位是"以 GitHub Actions + Quartz 部署为主案例的 CI/CD 入门",其他 CI 工具如 GitLab CI / Jenkins 只做横评,不展开。后续若需扩展:可加 § 11 安全专题(SAST/DAST/SCA/supply chain attack)、§ 12 GitOps 进阶等。)*
