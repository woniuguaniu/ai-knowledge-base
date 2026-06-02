---
source: ../程序小白概念扫盲手册.md
---

# 第十二章：Git 常用命令实战图解

> **目标**：让你能用 Git 完成 95% 的日常操作，不需要"精通"，但绝不能"懵逼"。
> **方法**：图解 + 生活类比 + 真实场景 + 命令拆解。

---

### 12.1 先建立 Git 的「心智模型」（最重要！）

很多人学 Git 越学越乱，就是因为**没建立正确的心智模型**——把 Git 当成"网盘"或"同步盘"。

#### Git ≠ 网盘

| 类型 | 关注点 | 例子 |
|---|---|---|
| 网盘（百度云/iCloud） | "最新的文件" | 改了就同步覆盖 |
| **Git** | **"每次改了什么、为什么改"** | 完整保留每次修改的历史和原因 |

> 💡 **核心认知**：Git 是一个**时间机器**，不是同步盘。你每次"提交"就是给当下打一个**存档点**，未来可以回到任意一个存档点。

#### 四个核心区域（Git 的世界）

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   工作区     │  │   暂存区     │  │  本地仓库    │  │  远程仓库    │
│              │  │              │  │              │  │              │
│ Working Dir  │  │   Staging    │  │  Local Repo  │  │  Remote Repo │
│              │  │     Area     │  │              │  │  (GitHub)    │
│  你正在改的  │  │  打算下次    │  │  已经存档的  │  │  云端的      │
│  那些文件    │  │  提交的清单  │  │  历史快照    │  │  备份/分享   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │                  │
       │   git add        │   git commit     │   git push       │
       └────────────────→ └─────────────────→└─────────────────→│
       │                                                        │
       │              git pull / git fetch                      │
       └────────────────────────────────────────────────────────┘
```

#### 用「写论文 + 备份到云」类比

| Git 区域 | 论文场景类比 |
|---|---|
| **工作区** | 你 Word 文档里正在打的字 |
| **暂存区** | 你勾选了"这一段我改好了，待会儿存档" |
| **本地仓库** | 点了"另存为：v1、v2、v3"在自己电脑上 |
| **远程仓库** | 把这些版本备份到了百度云/Google Drive |

四个核心命令对应四个动作：

```
打字           → 工作区有改动
git add        → 把改动放进"待存档清单"
git commit     → 真正打一个存档点（带说明文字）
git push       → 把所有存档同步到云端
```

---

### 12.2 一次性的配置（注册个"作者身份"）

第一次用 Git 之前，告诉 Git "你是谁"，相当于注册账号：

```bash
# 设置你的名字（提交记录里会显示这个）
git config --global user.name "你的名字"

# 设置你的邮箱（建议用 GitHub 注册的那个邮箱）
git config --global user.email "your@email.com"

# 把默认分支名设为 main（现代 Git 推荐，跟 GitHub 一致）
git config --global init.defaultBranch main

# 查看已设置的配置
git config --list
```

> 📌 `--global` 表示"对所有项目生效"。设一次就行。
>
> ⚠️ **关于第三条**：老版本 Git 默认创建的分支叫 `master`（"主人"含义在欧美社区有歧义），现在 GitHub 已统一改成 `main`。如果不设置这条，后面 `git push -u origin main` 可能报错（因为本地分支是 master）。

#### 类比

> 你去图书馆借书前要办借书证（写名字+联系方式），办完一次以后所有图书馆都能用。

---

### 12.3 场景一：把别人的项目下载到本地（最常见）

#### 命令

```bash
git clone https://github.com/cooksleep/gpt_image_playground.git
```

#### 图解

```
GitHub.com (远程仓库)              你的电脑
┌────────────────────┐             ┌────────────────────┐
│ gpt_image_         │             │                    │
│  playground/       │  git clone  │  gpt_image_        │
│   ├── src/         │ ─────────→  │   playground/      │
│   ├── package.json │             │   ├── src/         │
│   └── README.md    │             │   ├── package.json │
└────────────────────┘             │   ├── README.md    │
                                    │   └── .git/   ←── 完整历史 │
                                    └────────────────────┘
```

> 📌 **clone 不是简单下载**——它把**完整的历史记录**都搬下来了，藏在 `.git/` 文件夹里。

---

### 12.4 场景二：自己写代码 → 推到 GitHub（完整流程）

这是最常用、也最容易搞混的流程。我用**面包店类比**串起来：

#### 完整 7 步流程图

```
你（面包师傅）每天做面包，要把日记+成品都备份到云端。

第 1 步：建立工作记录簿
git init                       ← 在新文件夹初始化 Git，相当于新开本日记簿

第 2 步：今天做了 3 个面包
（编辑文件 a.txt, b.txt, c.txt）  ← 工作区改动

第 3 步：选择哪些要写进日记
git add a.txt b.txt            ← 把 a 和 b 放进暂存区（c 暂时不写）

第 4 步：写日记盖个章
git commit -m "今天做了甜甜圈"  ← 创建一个存档点，附说明

第 5 步：跟云端账户绑定（首次需要）
git remote add origin https://github.com/你/仓库.git

第 6 步：把存档同步到云端
git push -u origin main        ← 推送到 GitHub

第 7 步：以后再修改
（修改文件）→ git add → git commit → git push
   循环这 3 步即可
```

#### 命令逐字拆解

| 命令 | 干啥 | 关键参数 |
|---|---|---|
| `git init` | 在当前目录初始化 Git | 无 |
| `git status` | **看当前状态**（必学！哪些改了、哪些待提交） | 无 |
| `git add <文件>` | 把指定文件加入暂存区 | `git add .` = 加入所有改动 |
| `git commit -m "说明"` | 提交存档，带说明文字 | `-m` = message |
| `git remote add origin <url>` | 绑定一个远程仓库，起名 origin | `origin` 是惯例名字 |
| `git push -u origin main` | 推送到远程的 main 分支 | `-u` 第一次要加，记住对应关系 |

#### 实战例子：从零到 GitHub

```bash
# 1. 创建并进入项目文件夹
mkdir ~/Desktop/我的小项目
cd ~/Desktop/我的小项目

# 2. 初始化
git init

# 3. 创建几个示例文件（写代码）
echo "<h1>Hello</h1>" > index.html
echo "body { color: red; }" > style.css

# 4. 看看状态
git status
# 输出：Untracked files: index.html, style.css

# 5. 把所有新文件加入暂存区
git add .

# 6. 第一次提交
git commit -m "首次提交：项目初始化"

# 7. 在 GitHub 网站上手动建一个空仓库（点 New repository）
#    然后复制它的 URL

# 8. 绑定远程仓库
git remote add origin https://github.com/你的用户名/你的仓库.git

# 9. 推送
git push -u origin main
```

> 📌 第一次推送可能要登录 GitHub。现在 GitHub 不允许密码登录，要用 **Personal Access Token**（在 GitHub 设置里生成）或 **SSH key**。

---

### 12.5 场景三：日常工作的 3 步循环

项目搭好之后，每天的工作就是这个**循环**：

```
        改代码
          │
          ▼
   ┌──────────┐
   │  改完了？ │── 否 ─→ 继续改
   └────┬─────┘
        │ 是
        ▼
   git status        ← 看看改了哪些（自检）
        │
        ▼
   git add .         ← 把改动加入暂存
        │
        ▼
   git commit -m "本次干了啥"   ← 存档
        │
        ▼
   git push          ← 同步到云端
        │
        └──→ 回到"改代码"
```

#### 提交说明（commit message）怎么写？

| ❌ 不好的提交说明 | ✅ 好的提交说明 |
|---|---|
| `update` | `修复登录页面密码框无法输入的 bug` |
| `123` | `新增用户头像上传功能` |
| `wip` | `重构数据库连接池，提升 30% 性能` |

**简单原则：让未来的自己（或同事）看到这条说明，能一眼明白这次改了什么。**

---

### 12.6 场景四：和远程仓库同步

如果**别人也在改同一个项目**（或者你在多台电脑工作），就需要同步。

#### 两个最重要的命令

```bash
git pull   # 把远程的改动拉下来合并到本地
git push   # 把本地的改动推到远程
```

#### 图解：你和同事的协作（双泳道时间线）

```
时间 ↓                你（本地）              远程仓库            同事（本地）
─────────────────────────────────────────────────────────────────────
T1：起点         git pull ←─── commit A ───→ git pull
                  本地 = A                       本地 = A
─────────────────────────────────────────────────────────────────────
T2：各自改代码   改 a.txt                                       改 b.txt
                  git commit                                    git commit
                  本地 = A→B(你)                                 本地 = A→C(同事)
─────────────────────────────────────────────────────────────────────
T3：同事先推     ─────────────→ 同事 push ───→ 远程 = A→C
─────────────────────────────────────────────────────────────────────
T4：你想推       git push ❌
                  报错：远程比你新（远程是 A→C，你是 A→B）
─────────────────────────────────────────────────────────────────────
T5：你先拉       git pull ←─── 远程 A→C ───
                  本地变成 A→C→合并(B+C)
─────────────────────────────────────────────────────────────────────
T6：你再推       git push ───→ 远程 = A→C→合并 ✅
─────────────────────────────────────────────────────────────────────
```

#### 黄金法则

> 📌 **每次开始工作前先 `git pull`，每次推送前再 `git pull`。**

---

### 12.7 场景五：查看历史 / 对比改动

#### `git log` —— 查看历史提交

```bash
git log              # 完整历史
git log --oneline    # 简洁版（每条一行）
git log --graph      # 带图形分支结构
git log -5           # 只看最近 5 条
```

输出示例：

```
* a3f9c12 (HEAD -> main) 修复登录 bug
* 7b8e3d4 新增用户头像上传
* 5c1d2a8 重构数据库连接
* d4e5f6a 首次提交
```

每行：**短哈希 + 提交说明**。哈希是这次提交的"身份证号"，可以用它定位。

#### `git diff` —— 看改了啥

```bash
git diff              # 看工作区相对于暂存区的改动
git diff --staged     # 看暂存区相对于上次提交的改动
git diff a3f9c12      # 看当前相对于某次提交的改动
```

输出：以"+"和"-"显示新增/删除的行（红绿对比）。

---

### 12.8 场景六：版本回退 / 救命操作

> ⚠️ 这一节涉及**红灯区**操作（可能丢失代码），做之前一定看清楚！

#### 先理解一个概念：HEAD 是啥？

`HEAD` = **当前分支最新提交的指针**，可以理解为"你当前所在的位置"。

```
git log 历史：
   d4e5f6a   ← 首次提交
   ↑
   5c1d2a8   ← 重构数据库
   ↑
   7b8e3d4   ← 新增头像功能
   ↑
   a3f9c12   ← 修复 bug    ← HEAD 指向这里（最新提交）
```

衍生写法：
- `HEAD~1` 或 `HEAD^` = HEAD 的**上一个提交**（也就是 7b8e3d4）
- `HEAD~2` = HEAD 的**上上个提交**（5c1d2a8）
- `HEAD~3` = 再往前一个

> 💡 **类比**：HEAD 像是你看书时书签夹的位置，`HEAD~1` 就是"往回翻一页"。

#### 三种"回到过去"的方式（区别非常重要）

| 命令 | 干啥 | 危险度 | 何时用 |
|---|---|---|---|
| **git checkout** `<commit>` -- `<文件>` | 把某个文件恢复到某次提交时的样子 | ⭐ 安全 | 改坏了某个文件想恢复 |
| **git revert** `<commit>` | **新建一个反向提交**，撤销某次改动 | ⭐⭐ 安全 | 已经推到远程，要撤销 |
| **git reset --hard** `<commit>` | **强行**把分支拨回到某次提交，**之后的改动全丢** | ⭐⭐⭐⭐⭐ 危险 | 只本地、且 100% 确定 |

#### 图解三者区别

```
原始历史：  A ── B ── C ── D (最新)

git revert C：
            A ── B ── C ── D ── C'(反向C)
            （历史保留，新增一个抵消 C 的提交）

git reset --hard B：
            A ── B
            （C 和 D 直接消失！本地未推送时还能救，已推送会出大问题）

git checkout A -- 文件.txt：
            历史不变，只是把"文件.txt"恢复到 A 时的内容
```

#### 实战建议

| 你想做的事 | 推荐命令 |
|---|---|
| "我刚改坏了某个文件，想恢复到上次提交的样子" | `git checkout -- 文件名` |
| "我刚 commit 了，但还没 push，想撤销这次 commit" | `git reset --soft HEAD~1`（保留改动）<br>`git reset --hard HEAD~1`（连改动都丢） |
| "已经推到远程了，要撤销" | `git revert <提交哈希>`，再 push |
| "完全乱了想回到 3 次提交之前" | 先 `git log` 找到那次提交的哈希，再决定用 reset 还是 revert |

> 📌 **新手保险法**：操作前先 `git status` 和 `git log` 看清楚，不确定就别敲 `--hard`！

---

### 12.9 场景七：分支（Branch）—— Git 的精髓

#### 什么是分支？

把"主线代码"想象成一棵树的主干。**分支 = 从主干分出来的旁支**，可以在上面随便实验，不影响主干。

```
主分支 main：     A ── B ── C ────────── F (合并后)
                       \              /
开发分支 feature：       D ── E ──────/
                       (在分支上开发新功能)
```

**为什么要用分支？**
1. 同时做多个功能，互不干扰
2. 实验性改动出了问题不影响主线
3. 多人协作时各自占一个分支

#### 常用分支命令

```bash
git branch                    # 查看本地所有分支（带 * 的是当前分支）
git branch <名字>              # 创建新分支
git checkout <名字>            # 切换到某个分支（老语法）
git switch <名字>              # 切换分支（新语法，更直观）
git checkout -b <名字>         # 创建并切换（最常用）
git switch -c <名字>           # 同上（新语法）
git merge <名字>               # 把某个分支合并到当前分支
git branch -d <名字>           # 删除已合并的分支
git branch -D <名字>           # 强制删除（红灯区）
```

#### 实战例子：在分支上加功能

```bash
# 1. 当前在 main 分支，看一眼
git status
# 输出：On branch main

# 2. 创建并切换到新分支
git switch -c feature-login
# 输出：Switched to a new branch 'feature-login'

# 3. 在这个分支上随便改、提交（不会影响 main）
# ...编辑代码...
git add .
git commit -m "实现登录功能"

# 4. 功能做完了，切回 main
git switch main

# 5. 把 feature-login 的改动合并进 main
git merge feature-login

# 6. 删掉用过的分支
git branch -d feature-login

# 7. 推到远程
git push
```

#### 分支合并图解

```
合并前：
  main:        A ── B ── C
                    \
  feature-login:     D ── E
                      ↑ 你在这分支上加了登录功能

git switch main + git merge feature-login

合并后：
  main:        A ── B ── C ────── F   ← F 是合并提交
                    \           /
  feature-login:     D ── E ───/
```

---

### 12.10 场景八：合并冲突（Merge Conflict）—— 新手最怕的

#### 什么是冲突？

你和同事**同时改了同一个文件的同一行**，Git 不知道该听谁的，就会"卡住"，等你手动解决。

#### 冲突长什么样？

打开冲突的文件会看到这种"奇怪标记"：

```
正常的代码...
<<<<<<< HEAD
你写的版本
=======
同事写的版本
>>>>>>> feature-login
正常的代码...
```

#### 解决步骤

```
1. git pull / git merge 失败，提示冲突
        │
        ▼
2. git status 看哪些文件有冲突
        │
        ▼
3. 打开冲突文件，找到 <<<<<<< 标记
        │
        ▼
4. 决定怎么改（核心规则：保留你想要的内容，删干净所有标记行）
        │
        ▼
5. git add <冲突文件>     ← 告诉 Git "我解决好了"
        │
        ▼
6. git commit              ← 完成合并提交
```

#### 第 4 步详解：到底怎么改？

冲突文件长这样（5 行：3 个标记行 + 2 段内容）：

```
<<<<<<< HEAD                    ← 标记行 1
你写的版本                       ← 内容 A
=======                          ← 标记行 2
同事写的版本                     ← 内容 B
>>>>>>> feature-login            ← 标记行 3
```

**核心规则：决定保留哪段内容，然后把所有 `<<<<<<<` `=======` `>>>>>>>` 三种标记行全部删掉。**

| 你想要的结果 | 操作 | 改完文件长这样 |
|---|---|---|
| 只保留你的版本 | 删 3 个标记行 + 删"同事写的版本"那行 | `你写的版本` |
| 只保留同事版本 | 删 3 个标记行 + 删"你写的版本"那行 | `同事写的版本` |
| 两段都要（合并） | 删 3 个标记行，两段内容都留下 | `你写的版本`<br>`同事写的版本` |
| 自己重写 | 删 3 个标记行 + 删两段，写一段新的 | `（你重新写的内容）` |

> 💡 **铁律**：改完后，文件里**绝对不能再有任何 `<<<<<<<`、`=======`、`>>>>>>>`** ——只要还剩一个，git add 就还会报冲突未解决。

#### 类比

> 你和同事合写一篇文章，同时改了第 3 段。Git 把两个版本都贴出来，问你"留谁的？或者怎么揉一起？"——决定权在你。

---

### 12.11 必须知道的 `.gitignore` 文件

有些文件**永远不该提交到 Git**：
- `node_modules/`（依赖，太大）
- `.env`（含密码、API Key）
- `dist/` `build/`（构建产物）
- `.DS_Store`（macOS 系统文件）
- `*.log`（日志）

在项目根目录创建一个名为 `.gitignore` 的文件，列出要忽略的：

```gitignore
# 依赖
node_modules/
__pycache__/

# 构建产物
dist/
build/

# 环境变量（敏感！）
.env
.env.local

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log

# IDE 配置
.vscode/
.idea/
```

> 📌 不同语言的项目有不同的 .gitignore 模板，可以去 https://github.com/github/gitignore 抄。

---

### 12.12 一张终极速查图

```
┌─────────────────────────────────────────────────────────────┐
│                     Git 命令速查                              │
├─────────────────────────────────────────────────────────────┤
│ 【入门 4 件套（每天用）】                                     │
│   git status                ← 看现状                          │
│   git add <文件>             ← 加入暂存区                     │
│   git commit -m "说明"       ← 存档                           │
│   git push                  ← 同步到云端                      │
│                                                              │
│ 【克隆与同步】                                                │
│   git clone <url>            ← 下载远程项目                   │
│   git pull                  ← 拉取并合并远程改动              │
│   git fetch                 ← 只拉取不合并                    │
│                                                              │
│ 【查看与对比】                                                │
│   git log --oneline          ← 查看历史                       │
│   git diff                  ← 看改动                          │
│   git blame <文件>           ← 看每行是谁写的                 │
│                                                              │
│ 【分支】                                                      │
│   git branch                ← 看分支                          │
│   git switch -c <名>         ← 新建并切换                     │
│   git merge <名>             ← 合并                           │
│   git branch -d <名>         ← 删除                           │
│                                                              │
│ 【撤销与回退】                                                │
│   git checkout -- <文件>     ← 恢复某文件                     │
│   git reset --soft HEAD~1   ← 撤销上次 commit（保留改动）    │
│   git reset --hard HEAD~1   ← 撤销上次 commit（丢弃改动）⚠️   │
│   git revert <hash>         ← 新建反向提交                    │
│                                                              │
│ 【其他高频】                                                  │
│   git stash                 ← 临时藏起改动                    │
│   git stash pop             ← 把藏起的恢复                    │
│   git remote -v             ← 看远程仓库                      │
└─────────────────────────────────────────────────────────────┘
```

---

### 12.13 给小白的「Git 5 条铁律」

1. **每次开工前先 `git pull`**，避免冲突
2. **commit 信息写清楚**，未来的你会感谢现在的你
3. **不要把 `.env`、`node_modules`、密钥提交到仓库**（用 .gitignore）
4. **`--hard` 这种参数想 3 遍再敲**，不可恢复
5. **不确定的时候先 `git status` 和 `git log`**，看清楚再操作

---

### 12.14 常见报错速查

| 报错信息 | 原因 | 解决 |
|---|---|---|
| `fatal: not a git repository` | 当前目录没初始化 Git | `git init` 或换到正确目录 |
| `Your branch is behind` | 远程比本地新 | 先 `git pull` |
| `rejected (non-fast-forward)` | 同上 | 先 `git pull`，解决冲突再 push |
| `Authentication failed` | 密码/Token 错 | 重新生成 Personal Access Token |
| `merge conflict` | 合并冲突 | 看 12.10 节解决步骤 |
| `Permission denied (publickey)` | SSH key 没配 | 在 GitHub 添加 SSH key |
| `Please tell me who you are` | 没配置 user.name/email | 跑 12.2 节的命令 |

---

### 12.15 实战练习（强烈推荐做一遍）

```bash
# ============ 练习：从零搭一个仓库并推到 GitHub ============

# 1. 在桌面建测试目录
mkdir ~/Desktop/git-练习
cd ~/Desktop/git-练习

# 2. 初始化
git init

# 3. 创建一个文件
echo "Hello Git" > hello.txt

# 4. 看状态
git status        # 应该看到 hello.txt 是 Untracked

# 5. 加入暂存
git add hello.txt
git status        # 现在 hello.txt 是 to be committed

# 6. 提交
git commit -m "首次提交"
git log           # 看到你的第一条记录！

# 7. 修改文件
echo "再来一行" >> hello.txt

# 8. 看改动
git diff          # 看到 +再来一行

# 9. 提交
git add .
git commit -m "新增第二行"

# 10. 创建分支并切换
git switch -c experiment
echo "实验内容" > exp.txt
git add . && git commit -m "实验提交"

# 11. 切回主分支
git switch main
ls               # 看不到 exp.txt（因为它在 experiment 分支）

# 12. 合并实验分支
git merge experiment
ls               # 现在能看到 exp.txt 了

# 13. 看完整历史
git log --oneline --graph
```

走完这 13 步，你就完整理解 Git 了。

---

### 12.16 进阶补充（rebase / stash / reflog 等）

本章覆盖了 90% 的日常 Git 场景。剩下 10%——**协作整理历史 / 误操作救命 / 短期切换上下文**——单独整理在另一篇：

> 📖 **[Git 进阶速查](../Git进阶速查.md)** — 6 个进阶命令 + 实战练习
>
> - `stash` 临时藏起改动（**最常用**，每天都可能用到）
> - `reflog` 救命操作（误删 / 误回退后找回）
> - `rebase` 整理 commit 历史
> - `--force-with-lease` 比 `--force` 安全的强推
> - `cherry-pick` 单挑一个 commit
> - `tag` 版本号管理

---

## 附录：学习路径推荐

### 阶段一：能跑起来（1~2 周）
1. ✅ 学会 git clone、npm install、npm run dev 这套流程
2. ✅ 看懂 README.md 的安装步骤
3. ✅ 用 Vercel 部署一个静态网站

### 阶段二：能改东西（1~2 个月）
1. 学 HTML / CSS / JavaScript 基础
2. 学 React 或 Vue 任选一个
3. 自己改改别人项目的样式、文字

### 阶段三：能做点东西（3~6 个月）
1. 自己从 0 创建一个 React 项目
2. 用 Docker 部署
3. 学一点后端（Node.js / Python）

### 阶段四：能独立开发（6 个月+）
1. 数据库、API 设计
2. CI/CD 自动化
3. 云服务、容器编排（K8s）

---

## 附录：实用资源

### 中文学习资源
- **MDN Web 文档**：https://developer.mozilla.org/zh-CN/  → 前端最权威文档
- **菜鸟教程**：https://www.runoob.com/  → 各种语言的快速入门
- **廖雪峰的官方网站**：https://www.liaoxuefeng.com/  → Python、Git、JavaScript 教程
- **掘金**：https://juejin.cn/  → 中文技术社区

### 工具网站
- **GitHub**：https://github.com/  → 代码托管
- **Vercel**：https://vercel.com/  → 一键部署
- **Docker Hub**：https://hub.docker.com/  → 镜像仓库
- **npm**：https://www.npmjs.com/  → JS 包仓库

### 命令速查
- **Git 速查表**：https://education.github.com/git-cheat-sheet-education.pdf
- **Docker 速查表**：https://docs.docker.com/get-started/docker_cheatsheet.pdf

---

## 🎯 看完本手册后，下一步去哪？

| 你的状态 | 下一步建议 |
|---|---|
| 想动手实操 | 翻《[小白入门-GitHub项目部署使用指南](../小白入门-GitHub项目部署使用指南.md)》跟着 7 步走 |
| 想跑通第一个项目 | 拿你电脑上的 `gpt_image_playground`，按指南执行 `npm install` → `npm run dev` |
| 想巩固名词 | 重点回看 **第零章 + 第八章（缩写表）** |
| 想深入某个具体工具 | 直接定位本手册第 1~10 章 |
| 想交叉验证 | 找一个 GitHub 项目从头部署一遍，碰到的所有名词都查得到 |
| 想理解从需求到产品完成的完整工程流程 | 翻《[软件工程产品研发 SOP](../../软件工程产品研发SOP.md)》:需求判断 → Spec → 架构 → 计划 → TDD → 质量门禁 → 上线反馈的一条证据链 |
| 想把自己的笔记/文档站发布出去 | 翻《[静态站点生成器与 Quartz 部署实战](../../静态站点生成器与Quartz部署实战.md)》:**SSG 范式 + 三种部署路线 + 自有 VPS 完整 7 步实战**(以本知识库部署到 `kingrich.top/knowledge-base/quartz/` 为案例) |
