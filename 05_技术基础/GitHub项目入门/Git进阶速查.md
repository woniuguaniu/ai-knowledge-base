# Git 进阶速查（rebase / stash / reflog 等）

> 本文是 [`程序小白概念扫盲手册.md`](程序小白概念扫盲手册.md) 第十二章的**进阶补充**。
>
> 主手册讲完了"日常 90% 场景"——add / commit / push / pull / branch / merge / reset。
> 这份速查讲剩下 10%——**协作、整理历史、救命**——但其中 `stash` 和 `reflog` 你日后大概率天天用到。

---

## 阅读顺序建议

| 先学的（个人开发也常用） | 后学的（多人协作再用） |
|---------------------|---------------------|
| ① `stash` 临时藏起改动 | ④ `--force-with-lease` 安全强推 |
| ② `reflog` 救命操作    | ⑤ `cherry-pick` 挑单个 commit |
| ③ `rebase` 整理历史    | ⑥ `tag` 版本号管理 |

---

## ① stash —— 临时藏起改动（**最常用**）

### 什么时候用

> "我刚改了一半代码，老板突然说线上有个 bug，要我立刻切到 main 分支修。但我现在改的代码还没 commit，切分支会被警告……"

这就是 `stash` 的场景：**改了一半还不想 commit，但又必须切走**。

### 命令

```bash
# 1. 把当前所有未提交改动"藏起来"（工作区变干净）
git stash

# 2. 切走干别的事（修 bug、切分支……）
git switch main
# ... 修完 bug，切回来 ...

# 3. 把刚才藏的拿回来
git stash pop          # 拿回最近一次的，并从藏匿列表删除
git stash list         # 看现在藏了几份
git stash apply        # 拿回但不从列表删除（适合多次试用）
git stash drop         # 删掉列表里的某一份
```

### `stash` ≠ `commit`

| 维度 | `commit` | `stash` |
|------|---------|---------|
| 进入历史 | ✅ 是 | ❌ 不是（藏在本地一个特殊队列） |
| 可推送到远程 | ✅ | ❌ 只在本机 |
| 适合长期保存 | ✅ | ❌ 几小时～几天，太久会忘 |
| 类比 | 存档 | 把桌面文件先扫进抽屉 |

> **铁律**：stash 是**短期**临时方案。超过一天没回来 pop，就改成 commit 到一个临时分支。

---

## ② reflog —— 救命操作（误删/误回退后找回）

### 什么时候用

> "我刚 `git reset --hard HEAD~3`，三次 commit 全没了……能找回来吗？"
>
> "我把分支 `git branch -D feature` 删了，发现里面还有没合的代码……"

能找回。`git reflog` 记录了**你本机所有 HEAD 移动过的位置**——包括 reset、删分支、rebase 中途——绝大多数"以为没了"的提交都还在。

### 命令

```bash
# 1. 看 HEAD 历史（每行有一个独有的 hash）
git reflog
# 输出例子：
# a3f5b2c HEAD@{0}: reset: moving to HEAD~3
# 8d9e4f1 HEAD@{1}: commit: 修了登录bug   ← 这个是被 reset 掉的，但还在
# 7c2a1b0 HEAD@{2}: commit: 加了首页样式

# 2. 找到要找回的那个 hash（如 8d9e4f1），强制回到那个状态
git reset --hard 8d9e4f1
```

### `reflog` vs `log` 的区别

- `git log`：**项目的 commit 历史**（线性的、共享的）
- `git reflog`：**你这个本机 HEAD 的移动轨迹**（私人的，含被"丢弃"的提交）

> **铁律**：发现误操作后**立刻** `git reflog`，不要再敲别的命令——reflog 默认 90 天清理，但部分操作会立刻让 commit 真的消失。

---

## ③ rebase —— 整理 commit 历史

### 用法 A：`git pull --rebase`（推荐替代 `git pull`）

普通 `git pull` 会产生一个 `Merge branch 'main'` 的合并提交，搞脏历史。`--rebase` 让你的本地 commit "排"在远程 commit 后面：

```
普通 pull：    A--B--M  ← 多了个 M (merge commit)
              \  /
               C-D（你的）

pull --rebase: A--B--C'--D'  ← 历史是直线，干净
```

```bash
git pull --rebase           # 一次
git config --global pull.rebase true   # 永久开启
```

### 用法 B：`git rebase -i HEAD~3` 交互式整理最近 3 次提交

打开一个编辑器列出最近 3 次 commit，可以：

```
pick   a3f5b2c 加了登录页
squash 8d9e4f1 改了typo            ← 把这次合并到上一次
reword 7c2a1b0 wrok in progress    ← 改 commit 信息
```

保存退出，git 会按你的指令重写历史。

> ⚠️ **铁律**：**只对未推送的 commit 用 rebase**。已经 push 到远程、被同事拉过的 commit 用 rebase 会引发协作灾难。

---

## ④ --force-with-lease —— 比 --force 安全的强推

rebase 改写历史后再 push，会被远程拒绝（因为 hash 都变了）。两种强推方式：

| 命令 | 行为 | 风险 |
|------|-----|------|
| `git push --force` | 无脑覆盖远程 | ⚠️⚠️⚠️ 会冲掉同事的提交 |
| `git push --force-with-lease` | 只在远程没人改过的前提下覆盖 | ⚠️ 安全得多 |

```bash
git push --force-with-lease   # 永远用这个，不要用 --force
```

---

## ⑤ cherry-pick —— 从别的分支挑单个 commit

> "feature 分支上有 5 次提交，我只想把其中那次 bug 修复合到 main，其他不要。"

```bash
git switch main
git cherry-pick a3f5b2c    # 把 a3f5b2c 这次 commit 复制一份到 main
```

适合"挑樱桃"式合并——比 merge 整条分支灵活。

---

## ⑥ tag —— 给某个 commit 打版本标记

```bash
git tag v1.0.0                     # 在当前 commit 打轻量 tag
git tag -a v1.0.0 -m "首次发布"    # 带说明的 annotated tag（推荐）
git tag                            # 看所有 tag
git push origin v1.0.0             # 推单个 tag 到远程
git push --tags                    # 推所有 tag

# 检出某个 tag 对应的代码
git checkout v1.0.0
```

发版本（`v1.0.0` / `v2.3.1`）必备，GitHub 的 Release 页面就是基于 tag。

---

## 进阶速查图

```
┌─────────────────────────────────────────────────────────────┐
│                  Git 进阶命令速查                            │
├─────────────────────────────────────────────────────────────┤
│ 【临时切换上下文】                                           │
│   git stash                 ← 藏起改动                       │
│   git stash pop             ← 拿回最近一次                   │
│   git stash list            ← 看藏了几份                     │
│                                                              │
│ 【救命】                                                     │
│   git reflog                ← 看 HEAD 移动过的所有位置       │
│   git reset --hard <hash>   ← 跳回 reflog 里的某个状态       │
│                                                              │
│ 【整理历史】                                                 │
│   git pull --rebase         ← 拉取时不留 merge commit        │
│   git rebase -i HEAD~N      ← 交互式整理最近 N 次提交         │
│   git rebase --abort        ← rebase 中途反悔                │
│                                                              │
│ 【强推（仅自己分支）】                                       │
│   git push --force-with-lease  ← 永远用这个                  │
│                                                              │
│ 【挑选与版本】                                               │
│   git cherry-pick <hash>    ← 单挑一个 commit 合到当前分支   │
│   git tag -a v1.0.0 -m "..." ← 打版本标记                    │
│   git push --tags           ← 推送所有 tag                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 进阶 5 条铁律

1. **rebase 只动未推送的 commit**——已 push 的别动，否则同事炸毛
2. **强推用 `--force-with-lease`**，永远别用裸 `--force`
3. **stash 是短期方案**，超过一天就改成临时分支 commit
4. **误操作后立刻 `git reflog`**，不要再敲其他命令
5. **tag 之前先确认 commit 没问题**——tag 是"盖章"，盖错了要删要重推都麻烦

---

## 实战练习（建议跑一遍）

```bash
# 练习 1：stash 流程
echo "正在写一半" >> README.md   # 改一下
git stash                          # 藏起来
git status                         # 工作区干净了
git stash pop                      # 拿回来

# 练习 2：reflog 救命
git log --oneline                  # 记下当前最新 hash
echo "test" > test.txt && git add . && git commit -m "test"
git reset --hard HEAD~1            # 假装误删
git reflog                         # 找回刚才那个 commit
git reset --hard <reflog里的hash>  # 救回来

# 练习 3：交互式 rebase
git rebase -i HEAD~3               # 看见编辑器后直接 :q 退出（不实际改）
```
