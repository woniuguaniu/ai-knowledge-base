# 小白入门：从 GitHub 拉取项目到部署使用完整指南

> 以 `gpt_image_playground` 项目为教学样本
> 整理日期：2026/05/01

---

## 📚 阅读说明 & 配套资料

本指南是**实操手册**——告诉你"怎么一步步把项目跑起来"。

同目录下还有两份配套资料：

| 文件 | 定位 | 什么时候看 |
|---|---|---|
| 📘 **本文件**（部署使用指南） | 实操手册：流程、命令、踩坑 | 想动手做的时候 |
| 📗 [程序小白概念扫盲手册.md](./程序小白概念扫盲手册.md) | 知识地图：名词、原理、关系 | 遇到不懂的概念时 |
| 🃏 [五看一跑_小白工程运行部署学习文档.md](./五看一跑_小白工程运行部署学习文档.md) | 速查卡：30 秒口令记忆版 | 临时回忆流程时 |

**推荐阅读顺序：**
1. 先翻《扫盲手册》**第零章**（30 分钟看完一张全景图）→ 建立全局观
2. 回到本指南，跟着 7 个步骤动手做
3. 操作时遇到陌生名词 → 去《扫盲手册》对应章节查
4. 想深挖某个工具（如 Docker / Nginx / pnpm）→ 看《扫盲手册》专门章节
5. 临时忘记流程 → 翻《五看一跑》速查卡

---

## 🧘 写在最前：先建立正确心态

**你不需要"看懂所有代码"才能跑项目。**

很多人卡在第一步是因为"想全部搞懂再动手"——结果什么也没做。正确的顺序是：

> **先把项目跑起来 → 再慢慢理解细节。**

只要先搞定这 3 件事，就能让 80% 的项目跑起来：

1. 这个项目用什么技术写的（Node / Python / Java...）
2. 它要什么环境和配置（版本、环境变量、数据库）
3. 正确的启动命令是什么（dev / build / start）

报错不可怕，**报错是好事**——它告诉你"哪里缺东西"，比静默失败强 100 倍。

---

## 目录

- [第一部分：理解项目结构](#第一部分理解项目结构)
- [第二部分：四种部署方式详解](#第二部分四种部署方式详解)
- [第三部分：从零开始的 7 个步骤](#第三部分从零开始的-7-个步骤)
- [第四部分：小白排错四件套（90% 问题都在这）](#第四部分小白排错四件套90-问题都在这)
- [第五部分：高效求助提问模板](#第五部分高效求助提问模板)
- [第六部分：心智图总结](#第六部分心智图总结)
- [第七部分：长期学习建议](#第七部分长期学习建议)
- [终章：30 秒口令速记](#终章30-秒口令速记)

---

## 第一部分：理解项目结构

### 1.1 为什么一个工程里会有那么多语言？

> 💡 **想先看全景图？** → 翻《扫盲手册》**第零章**，那里用 7 个使用场景把所有工具一次性讲清楚。本节只针对你现在看到的这个项目。

打开任意 GitHub 项目，会看到 `.ts` `.js` `.json` `.html` `.css` `.md` `.sh` `.conf` `Dockerfile`…… 看起来吓人，其实它们各司其职。

**用「餐厅」类比理解：**

| 文件 / 语言 | 在餐厅里相当于 | 它的作用 |
|---|---|---|
| `.tsx` / `.ts`（TypeScript） | 厨师（写菜的人） | 项目的核心源代码 |
| `.html` | 菜单封面 | 浏览器最先打开的那一页 |
| `.css` / Tailwind | 餐厅装修 | 控制颜色、字体、布局 |
| `.json` | 配置/清单 | 比如 `package.json` 是「食材清单+操作手册」 |
| `.md`（Markdown） | 说明书/告示牌 | 给人看的文档，比如 `README.md` |
| `.sh`（Shell 脚本） | 后厨流程纸条 | 一键执行一串命令 |
| `Dockerfile` | 打包整间餐厅的图纸 | 告诉电脑怎么把整个项目装进「集装箱」 |
| `nginx.conf` | 大堂经理规则手册 | 告诉服务器收到请求怎么转发 |

**关键认知：**
- 这些语言不是同时在写一个程序，而是**分工**——有的写代码、有的写样式、有的写部署
- 真正"干活的代码"在 `src/`，其他都是"配置 + 部署 + 文档"
- 所谓"多语言"，大多是各种工具的小配置文件，**不是真的让你都学会**

---

### 1.2 gpt_image_playground 项目目录解析

```
gpt_image_playground/
├── src/                        ← 真正的程序代码（TypeScript + React）
│   ├── App.tsx                 ← 应用主入口组件
│   ├── main.tsx                ← 程序入口（最先跑的代码）
│   ├── components/             ← 页面上的各种小部件（按钮、弹窗等）
│   ├── hooks/                  ← React 的"逻辑复用单元"
│   ├── lib/                    ← 工具函数库
│   └── store.ts                ← 数据状态管理（用了 zustand）
│
├── public/                     ← 不需要被打包处理的静态资源
│   ├── manifest.webmanifest    ← PWA（可装到桌面的 App）的配置
│   └── sw.js                   ← Service Worker，离线缓存用
│
├── deploy/                     ← 部署相关（不是运行时代码）
│   ├── Dockerfile              ← Docker 部署脚本
│   ├── nginx.conf              ← Nginx 服务器配置
│   └── inject-api-url.sh       ← 启动时注入变量的小脚本
│
├── index.html                  ← 浏览器打开的入口 HTML
├── package.json                ← 项目「身份证 + 操作手册」
├── package-lock.json           ← 锁定每个依赖的精确版本
├── tsconfig.json               ← TypeScript 编译器的配置
├── vite.config.ts              ← Vite 构建工具的配置
├── tailwind.config.js          ← Tailwind 样式工具的配置
├── postcss.config.js           ← PostCSS 配置（处理 CSS）
├── vercel.json                 ← Vercel 部署的配置
├── README.md                   ← 项目说明
└── LICENSE                     ← 开源协议（如 MIT）
```

---

### 1.3 关键文件速读

#### `package.json`（前端项目"身份证"）

```json
{
  "name": "gpt-image-playground",      // 项目名
  "version": "0.2.19",                  // 版本号
  "scripts": {                          // ★ 重点看这里：「我能跑哪些命令」
    "dev": "vite",                      // 启动开发服务器
    "build": "tsc -b && vite build",    // 打包生产版
    "preview": "vite preview",          // 预览打包结果
    "test": "vitest run"                // 跑测试
  },
  "dependencies": { ... },              // 运行时依赖（必须）
  "devDependencies": { ... }            // 开发时依赖（构建/调试用）
}
```

> **看完 `scripts` 部分就知道：要启动 → 敲 `npm run dev`**

---

## 第二部分：四种部署方式详解

| 方式 | 跑在哪 | 难度 | 适合谁 |
|---|---|---|---|
| ① Vercel | 别人的云服务器（免费） | ⭐ | 想白嫖一个公网网址的人 |
| ② Docker | 自己电脑/服务器 | ⭐⭐⭐ | 想"一键搬家、不污染电脑环境"的人 |
| ③ 本地开发模式 | 自己电脑 | ⭐⭐ | 想改代码看效果的开发者 |
| ④ 静态部署 | 任何静态文件服务器 | ⭐⭐ | 自己有服务器、想完全掌控的人 |

---

### ① Vercel 一键部署（最适合小白）

**Vercel 是什么？**
美国一家提供"云托管平台"的公司。把 GitHub 仓库授权给它，它就帮你：
1. 自动下载代码
2. 自动跑 `npm install`
3. 自动跑 `npm run build`
4. 把打包结果放到它的服务器上
5. 给你一个公网网址（如 `xxx.vercel.app`），全世界都能访问

**为什么免费？** 个人项目免费有流量限额，靠企业用户赚钱。同行还有 Netlify、Cloudflare Pages、GitHub Pages。

**操作流程：**
1. 注册 vercel.com（用 GitHub 账号登录）
2. 点 `Import Project` → 选仓库
3. 一路下一步 → 等 1~2 分钟 → 拿到网址

**项目里的 `vercel.json`** 就是给 Vercel 看的配置文件。

> **类比**：你把书的原稿（代码）交给印刷厂（Vercel），印刷厂自己印好然后帮你上架到书店（网址）。

---

### ② Docker 部署

> 💡 **想深入理解 Docker？** → 看《扫盲手册》**第五章（Docker 使用与管理）+ 第七章（容器化部署）**；想知道 pnpm 在 Docker 里怎么共用 → 看 **第十章**。

**先理解一个常见痛点：**
软件在你电脑上能跑，搬到别人电脑/服务器上就报错——因为环境不一样（Node 版本、缺库、操作系统不同……）

**Docker 干的事：**
把"程序 + 它需要的全部环境（操作系统、Node、Nginx、依赖）"打包成一个**集装箱（Container）**。
这个集装箱在任何装了 Docker 的电脑上都能原样跑起来，不用再操心环境。

**核心三个概念：**

| 名词 | 类比 | 解释 |
|---|---|---|
| Dockerfile | 菜谱 | 写明"先放什么、再装什么、最后启动什么" |
| Image（镜像） | 做好的预制菜 | 按菜谱执行后的成品，可以分发、复用 |
| Container（容器） | 一份在跑的菜 | 把镜像"启动起来"就是一个容器 |

**用户使用就一两条命令：**
```bash
docker build -t gpt-image-playground .       # 按菜谱做好预制菜
docker run -p 8080:80 gpt-image-playground   # 启动它，对外开 8080 端口
```
浏览器打开 `http://localhost:8080`。

**适合谁？**
- 公司服务器、自建 NAS、云主机
- 想在不同机器之间无痛迁移
- 不想本地装一堆 Node、Nginx 污染系统

---

### ③ 本地开发模式（`npm run dev`）

**这不是"部署"，是"边写边看效果"的开发流程。**

执行 `npm run dev`，Vite 会启动一个本地开发服务器，在你电脑上开个端口（如 5173），同时有两个魔法：

1. **热更新（HMR）**：保存代码 → 浏览器自动刷新
2. **开发代理**：能把请求转发到别处，绕开跨域限制（看 `dev-proxy.config.json`）

> **注意**：这种模式只有你自己电脑能访问，**不是给真实用户用的**。

---

### ④ 自己的静态服务器部署

最"原始"也最自由的方式：

```bash
npm run build
```

会在项目里生成一个 `dist/` 文件夹，里面是一堆 HTML、JS、CSS——这些就是"成品网页"。

把 `dist/` 整个上传到任何能放静态文件的地方都能用：
- 自己的云服务器（用 Nginx / Apache 提供服务）
- 阿里云 OSS、腾讯云 COS、AWS S3 等对象存储
- GitHub Pages
- Netlify / Cloudflare Pages

> **类比**：Vercel 是"全自动化印刷+上架"，方式④是你自己"印刷+租门面+摆上货架"，更累但完全掌控。

---

## 第三部分：从零开始的 7 个步骤

### 第 1 步：先「读懂」项目（不要急着动手）

#### 1.1 看 README.md（永远的第一步）

`README.md` 是作者写给你的"使用说明书"。打开方式：
1. 在 GitHub 网页打开仓库，下面会自动渲染显示
2. 用 VS Code / Cursor 打开
3. 终端：`cat README.md`

#### 1.2 看根目录的「标志性文件」识别技术栈

| 看到的文件 | 代表的语言/工具 |
|---|---|
| `package.json` | Node.js / 前端项目（要装 Node + npm） |
| `requirements.txt` / `pyproject.toml` | Python 项目（要装 Python + pip） |
| `pom.xml` / `build.gradle` | Java 项目 |
| `Cargo.toml` | Rust 项目 |
| `go.mod` | Go 项目 |
| `Dockerfile` / `docker-compose.yml` | 可以用 Docker 跑 |

#### 1.3 看 `package.json` 的 `scripts`

知道作者给你准备了哪些"快捷按钮"。

#### 1.4 扫一眼 `src/` 目录结构

不用读代码，**记住"代码住在 src/ 下"** 就够了。

---

### 第 2 步：把项目「搞」到自己电脑上

#### 方式 A：下载 ZIP（最简单但不推荐）
GitHub 网页 → 绿色 `Code` 按钮 → `Download ZIP` → 解压
**缺点：** 没法用 git 命令同步更新

#### 方式 B：git clone（推荐）
```bash
# 确认装了 git
git --version

# 进入存放仓库的目录
cd ~/Desktop/仓库

# 克隆
git clone https://github.com/cooksleep/gpt_image_playground.git
```

**好处：** 以后只要 `git pull` 就能拉最新代码。

---

### 第 3 步：准备运行环境（装工具）

| 项目类型 | 需要装 | 验证命令 |
|---|---|---|
| Node.js / 前端 | Node.js（自带 npm） | `node -v` 和 `npm -v` |
| Python | Python 3 | `python3 --version` |
| Java | JDK | `java --version` |
| Go | Go | `go version` |
| Rust | Rust | `rustc --version` |

**macOS 装 Node.js：**
```bash
# 推荐：通过 Homebrew
brew install node

# 或者去官网下载安装包：https://nodejs.org（选 LTS 版）
```

验证：
```bash
node -v   # 类似 v20.x.x
npm -v    # 类似 10.x.x
```

> **小坑**：项目对 Node 版本可能有要求，看根目录有没有 `.nvmrc` 文件。

---

### 第 4 步：安装项目依赖

```bash
cd /Users/<your-username>/Desktop/仓库/gpt_image_playground
npm install
```

**这一步在干啥？**
读取 `package.json`，把所有依赖（react、vite、tailwindcss…）下载到 `node_modules/`。

> 这就是为什么 `node_modules/` 通常很大、且不放进 git——它可以由 `package.json` 重新生成。

**常见报错与解决：**

| 报错 | 原因 | 解决 |
|---|---|---|
| `command not found: npm` | 没装 Node | 回第 3 步 |
| `EACCES: permission denied` | 权限问题 | 不要用 sudo，改 npm 路径或重装 Node |
| 下载特别慢 | 默认用国外源 | 换镜像：`npm config set registry https://registry.npmmirror.com` |
| `peer dependency` 警告 | 依赖版本冲突 | 多数能忽略；严重时加 `--legacy-peer-deps` |

---

### 第 5 步：配置（环境变量、API 密钥）

很多项目跑起来需要敏感信息——API Key、数据库连接串等。这些**不会写死在代码里**。

**怎么判断要不要配置？**
1. README 里有没有「配置」「Configuration」「Environment Variables」章节
2. 有没有 `.env.example`、`*.config.example.json` 这种"示例文件"

**典型流程：**
1. 复制示例文件：`cp dev-proxy.config.example.json dev-proxy.config.json`
2. 打开新文件，填入真实信息

> **gpt_image_playground 特殊**：它的 OpenAI API Key 是**启动后在网页右上角"设置"里填**，不需要在文件里配。

---

### 第 6 步：启动起来！

```bash
npm run dev
```

终端会输出：
```
  VITE v6.3.2  ready in 320 ms
  ➜  Local:   http://localhost:5173/
```

**复制 `http://localhost:5173/` 到浏览器** → 看到页面。

**核心概念扫盲：**
- **localhost** = 你自己这台电脑
- **5173** = 端口号
- **Ctrl + C**（在终端里）= 停止运行

**常见问题：**

| 现象 | 原因 | 解决 |
|---|---|---|
| `port 5173 already in use` | 端口被占用 | 关掉占用程序，或改端口 |
| 浏览器空白 | 控制台可能有错 | F12 看 Console |
| 终端一闪退 | 启动失败 | 看终端最后几行报错 |

---

### 第 7 步：把项目「发布」给别人用

到这一步，项目只能你自己电脑上访问。要让别人能用 → 部署到公网。

#### 🟢 新手 → 选 Vercel
1. 把项目推到 GitHub 仓库
2. 注册 vercel.com（用 GitHub 登录）
3. 点 `Add New Project` → 选仓库 → 一路 `Continue`
4. 等 1~2 分钟，拿到 `xxx.vercel.app` 网址
5. 打开网址 → 设置里填 OpenAI API Key → 用起来

#### 🟡 想自己掌控 → 选 Docker
```bash
cd /Users/<your-username>/Desktop/仓库/gpt_image_playground
docker build -f deploy/Dockerfile -t my-gpt-image .
docker run -d -p 8080:80 my-gpt-image
```
浏览器打开 `http://localhost:8080`。

> **前提**：装 Docker Desktop（macOS 从 docker.com 下）

#### 🔴 有自己的服务器 → 静态部署
```bash
npm run build
# 把 dist/ 文件夹整个上传到服务器，用 Nginx 提供服务
```

---

## 第四部分：小白排错四件套（90% 问题都在这）

> 不管什么项目，新手最容易卡的就是这 4 个错误。把它们当成"急救手册"。

### 🚨 问题 1：依赖装不上

**典型报错关键词：** `EACCES`、`EPERM`、`ENOTFOUND`、`peer dependency`

**排查顺序：**
1. **看版本**：`node -v`、`npm -v`，是否符合项目要求
2. **看错误关键词**：
   - `EACCES / EPERM` → 权限问题，**不要用 sudo**，改 npm 路径或重装 Node
   - `ENOTFOUND` → 网络问题，换镜像源：`npm config set registry https://registry.npmmirror.com`
   - `peer dependency` → 依赖冲突，加 `--legacy-peer-deps`
3. **清理重装**（核武器，谨慎）：
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### 🚨 问题 2：端口被占用

**典型报错：** `port already in use` / `EADDRINUSE`

**做法（任选其一）：**

```bash
# 方法 1：查找占用端口的进程并结束
lsof -i :5173        # 看 PID
kill -9 <PID>        # 杀掉

# 方法 2：换端口启动
npm run dev -- --port 4173
```

### 🚨 问题 3：前端能开，但接口报错

**典型表现：** 页面打开了，但点按钮没反应/报红。

**3 大原因：**
1. **API Key 没填** → 看右上角设置 / `.env` 文件
2. **API URL 填错** → 检查协议（http/https）、域名、端口
3. **跨域被拦截（CORS）** → 浏览器控制台会有 `Access-Control-Allow-Origin` 字样

**排查工具：**
- 按 **F12** 打开浏览器开发者工具
- 切到 **Network 面板** → 点失败的请求 → 看红色报错
- 切到 **Console 面板** → 看具体报错信息

### 🚨 问题 4：build 成功但部署后白屏

**典型表现：** 本地 `npm run dev` 没事，部署上去打开是白屏。

**3 大原因：**
1. **前端 base 路径配置不对**（`vite.config.ts` 里 `base` 字段）
2. **静态资源没上传完整** → `dist/` 里的文件传全了吗
3. **部署平台路由配置不对** → 比如 SPA 需要把所有路由 fallback 到 `index.html`

**排查 3 步：**
1. **本地先用 `npm run preview`** 看是否正常 → 如果本地 preview 都白屏，问题在构建
2. **对比线上和本地的浏览器控制台报错** → 通常会有 `404` 或 `MIME type` 错误
3. **检查部署平台的构建命令和输出目录**（Vercel 的 Build Command / Output Directory）

> 💡 **关键习惯**：每次 build 后用 `npm run preview` 在本地模拟生产环境跑一遍，**80% 的部署问题能在本地提前发现**。

---

## 第五部分：高效求助提问模板

> 错误解决不了时，要么自己搜，要么问别人。**会提问的人比不会的人快 10 倍**。

### 提问黄金 4 要素

不管是发给 AI、问同事、发到论坛，都要包含：

```
1️⃣ 你执行了什么命令
2️⃣ 完整报错截图或文本（不要只贴一行！）
3️⃣ 你的系统和版本
   - 操作系统（macOS / Windows / Linux）
   - 主要工具版本（node -v / python --version / docker -v）
4️⃣ 你已经尝试过什么
```

### 模板（直接复制改）

```
【环境】
- macOS 14.5
- Node v20.10.0
- npm 10.2.3

【操作】
我执行了 npm install 后，运行 npm run dev

【报错】
（粘贴完整报错文本）

【已尝试】
1. 删除 node_modules 重装 → 同样报错
2. 换 npm 镜像源 → 没变化
3. 在 stackoverflow 搜了关键词 xxx → 没找到完全匹配的

【期望】
能正常启动开发服务器，浏览器能打开 localhost:5173
```

### 三种"反面教材"避免

| ❌ 错误提问 | 为什么差 |
|---|---|
| "我代码跑不起来" | 没说什么代码、什么报错 |
| "报错截图来一张" | 截图没显示完整堆栈 |
| "你帮我看下吧" | 没尝试过任何排查 |

> 💡 **AI 时代特别提示**：把上面这个模板直接发给 ChatGPT/Claude，得到的解答质量会**比你随便问高 5 倍以上**。

---

## 第六部分：心智图总结

```
拿到 GitHub 项目
       │
       ▼
[ Step 1: 读 README + 看技术栈 ]   ← 先看说明书
       │
       ▼
[ Step 2: 下载到本地 (git clone) ]
       │
       ▼
[ Step 3: 装运行环境 (Node/Python...) ]
       │
       ▼
[ Step 4: 装依赖 (npm install / pip install) ]
       │
       ▼
[ Step 5: 配置（.env / config.json） ]
       │
       ▼
[ Step 6: 跑起来 (npm run dev) ]   ← 此时只你自己能访问
       │
       ▼
[ Step 7: 部署到公网 (Vercel / Docker / 服务器) ]
```

---

## 第七部分：长期学习建议

1. **别怕看英文报错**——把报错信息整段复制去搜，90% 都有人遇到过
2. **先模仿，再理解**——前几个项目按 README 抄就行，不用每行命令都搞懂
3. **保护自己的环境**——能用 Docker 就用 Docker，不要在主系统装一堆乱七八糟的依赖
4. **学一点 Git**——`clone / pull / status / log` 四条命令够用很久了
5. **常见踩坑词汇要记住**：
   - 依赖（dependency）
   - 构建（build）
   - 端口（port）
   - 环境变量（env var）
   - 镜像（image）
   - 容器（container）

---

## 终章：30 秒口令速记

> 看完了整本指南，最后给你一个"考试前的小抄"——把 7 步压缩成最精炼的版本。

### 🎯 核心口诀：**「五看一跑」**

```
拿到任何 GitHub 项目，默念 6 件事：

1️⃣ 一看 README       ← 作者写的使用说明
2️⃣ 二看项目类型      ← package.json / requirements.txt / ...
3️⃣ 三看 scripts       ← 启动命令是 dev 还是 start？
4️⃣ 四看环境变量      ← .env.example 复制改名
5️⃣ 五看部署文件      ← Dockerfile / vercel.json
6️⃣ 一跑本地          ← npm install && npm run dev
```

### 🎯 本地跑通的 3 条标准

判断"项目跑起来了"的依据：

1. ✅ 终端**无致命报错**（warning 可以忽略）
2. ✅ 浏览器能打开本地地址（如 `http://localhost:5173`）
3. ✅ 核心功能能**点通一条流程**（不只是首页能开）

三条都满足 = 你已经超过 80% 的"只会复制命令"的人。

### 🎯 通用实战三模板

**模板 A：拿到新项目第一天**
```bash
cd 项目目录            # 1. 进项目
# 打开 README.md       # 2. 看说明
npm install            # 3. 装依赖
npm run dev            # 4. 启动
# 打开浏览器访问地址    # 5. 看效果
```

**模板 B：准备上线前**
```bash
npm run build          # 1. 生产构建
npm run preview        # 2. 本地模拟生产环境
# 没问题再部署 dist/   # 3. 上线
```

**模板 C：遇到报错时**
→ 按"小白排错四件套"对号入座
→ 解决不了用"高效求助提问模板"问 AI 或同事

---

## 附录：常用命令速查

### Git 命令
```bash
git clone <url>          # 下载远程仓库到本地
git pull                 # 拉取远程最新代码
git status               # 查看当前修改状态
git log                  # 查看提交历史
```

### npm 命令
```bash
npm install              # 安装 package.json 所有依赖
npm install <包名>        # 安装某个包
npm run <脚本名>         # 运行 package.json 里 scripts 中的命令
npm run dev              # 启动开发服务器（最常用）
npm run build            # 打包生产版本
```

### Docker 命令
```bash
docker build -t <名字> .                # 构建镜像
docker run -d -p 8080:80 <名字>         # 运行容器
docker ps                               # 查看正在运行的容器
docker stop <容器ID>                    # 停止容器
docker rm <容器ID>                      # 删除容器
docker images                           # 列出所有镜像
```

---

## 🎯 看完本指南后，下一步去哪？

| 你的状态 | 下一步建议 |
|---|---|
| 还有名词没搞懂 | 翻《[程序小白概念扫盲手册](./程序小白概念扫盲手册.md)》对应章节 |
| 想看全景图建立体系 | 看《扫盲手册》**第零章** |
| 想深挖某个工具（Docker / Nginx / pnpm） | 看《扫盲手册》**第五~十章** |
| 想动手做下一个项目 | 找一个新的 GitHub 仓库，重复本指南的 7 步 |
| 想系统学一门语言 | 推荐 MDN（前端）或廖雪峰（Python） |
