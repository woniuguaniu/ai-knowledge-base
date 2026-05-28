# 静态站点生成器与 Quartz 部署实战

> 本笔记从 2026-05-27 把这个知识库部署到 `kingrich.top/knowledge-base/quartz/` 的实战流程提炼而来。重点是讲清楚:**Quartz 不是孤例,它属于「静态站点生成器(SSG)」这个更大的工程范式**——学会一个,其他都通。

---

## § 1. 这是什么:静态站点生成器(SSG)范式

### 一句话定义

**静态站点生成器(Static Site Generator, SSG)** = 把"写起来很爽的源文件(Markdown / MDX / 模板)"**提前编译成"浏览器能直接吃的静态文件(HTML/CSS/JS)"** 的工具。

### 类比:为什么叫"静态"

| | 动态站点(传统 Web) | 静态站点(SSG 产物) |
|---|-------------------|---------------------|
| **类比** | 餐厅现炒——你点菜,后厨现做 | 便利店饭团——提前做好,放冷柜,谁来都直接拿 |
| **首次响应** | 浏览器请求 → 后端 PHP/Python 跑数据库 → 拼 HTML → 返回(慢,有计算) | 浏览器请求 → web 服务器直接吐已写好的 HTML 文件(快,零计算) |
| **代表** | WordPress / Django / Rails | Hugo / Jekyll / **Quartz** / Astro / Eleventy |
| **服务器需要** | PHP/Python 运行时 + 数据库 + 大内存 | 任何能吐文件的服务器(nginx / Caddy / GitHub Pages / S3) |
| **更新方式** | 在网页后台编辑 → 立刻可见 | 改源文件 → 跑 build → 上传产物 → 可见 |
| **适合场景** | 评论、用户登录、商品库存等"内容随时变" | 博客 / 文档 / 笔记 / 项目主页等"内容稳定" |

**核心思想**:把"用户每次访问都重算"提前到"作者每次改完才重算一次",换性能、换稳定性、换部署简单。

### 为什么 SSG 在文档/笔记场景统治市场

1. **速度**:无后端 = 没有"数据库查询慢"这个常见瓶颈
2. **便宜**:静态文件可以扔到 Cloudflare Pages / GitHub Pages 这种**免费 CDN**
3. **安全**:没有后端进程在跑 = 没有 SQL 注入 / 命令注入这些攻击面
4. **可移植**:产物就是一堆文件,换托管平台只是改 DNS
5. **版本可控**:源文件在 Git 里,什么时候改了什么一目了然

---

## § 2. 这套工作流的 4 个角色

不管你用哪个 SSG,流水线都是这 4 个角色:

```
┌──────────────┐    ┌────────────┐    ┌──────────────┐    ┌──────────────┐
│  作者(你)   │ →  │  生成器     │ →  │  静态产物    │ →  │  Web 服务器  │
│              │    │            │    │              │    │              │
│  写 Markdown │    │  Quartz    │    │  public/     │    │  nginx /     │
│  source 文件 │    │  Hugo 等   │    │  HTML/CSS/JS │    │  Cloudflare  │
└──────────────┘    └────────────┘    └──────────────┘    └──────────────┘
   source            build 工具          build 产物          托管 + 提供
```

具体到这个知识库:

| 角色 | 实物 | 路径 / 工具 |
|------|------|------------|
| **作者** | 我 | 写 `.md` 文件 |
| **源文件** | 知识库本体 | `/Users/xxddd/Desktop/与AI交流AI/` |
| **生成器** | Quartz 4 | `~/Desktop/quartz-preview/quartz/`(通过软链读源文件) |
| **静态产物** | 编译好的 HTML | `~/Desktop/quartz-preview/quartz/public/`(16 MB / 93 个文件) |
| **Web 服务器** | nginx | 远端 `47.110.250.139` 上的 `/www/wwwroot/.../quartz/` |

`content` 软链是个值得单独说的细节——它让"源文件"和"生成器"解耦,让一个知识库可以被多个生成器吃,或者一个生成器可以吃多个知识库。

---

## § 3. Quartz 4 核心配置速览

Quartz 的"主配置文件"是 `quartz.config.ts`,落在生成器目录(不是源文件目录)。本节只挑跟部署最相关的字段:

```ts
const config: QuartzConfig = {
  configuration: {
    pageTitle: "与 AI 交流 AI",         // 浏览器标签页和站点 logo 显示的名字
    pageTitleSuffix: " · 知识库",       // 拼在每个页面 title 后的固定后缀
    enableSPA: true,                    // 是否启用 SPA 路由(切页不刷新整页,体验更顺)
    enablePopovers: true,               // 鼠标悬停链接预览目标页
    locale: "zh-CN",                    // 影响日期格式、搜索分词等
    baseUrl: "kingrich.top/...",        // ⚠️ 部署的关键字段,见下方详解
    ignorePatterns: [                   // 哪些路径不参与 build
      "private", ".obsidian", "_templates", ".claude", "CLAUDE.md",
    ],
    defaultDateType: "modified",        // 页面顶部显示"修改时间"还是"创建时间"
    theme: { /* 颜色 / 字体 / dark mode */ },
  },
  plugins: {
    transformers: [/* 处理 markdown 节点,如解析 frontmatter / 渲染 LaTeX / 高亮代码 */],
    filters:      [/* 过滤,如 RemoveDrafts 去掉 draft: true 的草稿 */],
    emitters:     [/* 产出物,如 ContentPage / TagPage / Sitemap / RSS / 404 / Assets */],
  },
}
```

**记忆口诀**:`transformers` 改内容、`filters` 删内容、`emitters` 产出物。改样式和插件结构在 `quartz.layout.ts` 和 `quartz/styles/custom.scss`,本笔记不展开。

### `baseUrl` 这个字段的"坑"

**官方说法**:`baseUrl` 用于生成 sitemap.xml、RSS feed、social meta(Open Graph) 的**绝对 URL**。格式是 `hostname[/path]`,**不带 `https://`**(协议会被自动加)。

**容易被误解的点**:很多人以为它会"自动给所有内部资源加路径前缀",其实不会——Quartz **内部资源和页面跳转用的是相对路径**,跟 `baseUrl` 无关。这就是为什么哪怕你忘了改 `baseUrl`,本地访问 `http://localhost:8080/` 也能正常显示——只是 sitemap/RSS 里 URL 全是 localhost 罢了。

**这个"用相对路径"的设计**反而让 **Quartz 天然支持子路径部署**(见 § 6)——这是 Quartz 一个非常友好的隐藏特性。

---

## § 4. 三种部署路线对比

部署目标都一样:让用户从浏览器访问到你的站。但**怎么把 build 产物送到用户面前**有三种主流路线:

| 路线 | 一句话 | 难度 | 月成本 | 自动化 | 国内访问 | 适合 |
|------|--------|------|--------|--------|---------|------|
| **A. 自有 VPS + 手动 rsync** | 本地 build → 用 rsync 推到自己的服务器 → nginx 当文件服务 | ⭐⭐ | 已有 VPS 就 ¥0 增量 | 写 shell 脚本一键 | 国内 VPS 速度最快 | 已有服务器、想完全可控、要绑自己域名 |
| **B. Git push + Cloudflare Pages / Vercel / Netlify** | 推 Git → 平台自动检测 → 在它机房 build → 全球 CDN 分发 | ⭐ | 免费(免费额度够个人用) | 完全自动,push 即部署 | 国内速度看 Cloudflare 国内节点(波动较大) | 不想管服务器、要全球 CDN、对国内速度要求不极致 |
| **C. 服务器自己 build** | 把整个 SSG 项目推到服务器 → 服务器 npm install + build → nginx 服务 | ⭐⭐⭐ | 已有 VPS 就 ¥0 | 用 webhook + Git 拉取也能自动 | 国内 VPS 最快 | 服务器够强 + 想在服务器本地编辑 + 团队多人协作 |

### 这次走的是路线 A

`kingrich.top/knowledge-base/quartz` 落在用户已有的阿里云 VPS(47.110.250.139)上,宝塔面板(`/www/wwwroot/`)+ nginx。这条路线最直接,但**远端必须装 rsync**(见 § 8.1)。

### 怎么选?

- **个人笔记 + 想图省事 + 不在乎国内速度** → 路线 B(Cloudflare Pages),5 分钟搞定
- **已经有 VPS + 想绑自己域名 + 完全可控** → 路线 A(本笔记重点)
- **服务器要做内容协作 + 想在服务器本地编辑 .md** → 路线 C(略复杂,不在本笔记展开)

---

## § 5. 自有 VPS 部署实战(本次完整流程)

把这次实战流程沉淀成可重复的 7 步,后续每次部署或者新人接手都按这个走。

### Step 1:改 `baseUrl`

打开 `~/Desktop/quartz-preview/quartz/quartz.config.ts`,第 17 行附近,把:

```ts
baseUrl: "localhost:8080",
```

改成实际部署的域名 + 子路径(不带 `https://`):

```ts
baseUrl: "kingrich.top/knowledge-base/quartz",
```

**注意**:本地预览和部署用不同的 `baseUrl`,所以这是个"部署前改一下,部署完改回 localhost"的反复操作。如果嫌烦,可以做条件分支(进阶,本笔记不展开)。

### Step 2:本地 build

```bash
cd ~/Desktop/quartz-preview/quartz
npx quartz build
```

正常输出:
```
Parsed 67 Markdown files in 5s
Filtered out 0 files in 185μs
Emitting files
Emitted 93 files to `public` in 757ms
Done processing 67 files in 6s
```

build 产物在 `public/` 目录,**16 MB / 93 个文件**(笔记数 + 静态资源 + sitemap.xml + RSS feed)。

### Step 3:验证产物路径(避免子路径部署翻车)

```bash
# sitemap 是否生成了正确的远端 URL?
head -10 ~/Desktop/quartz-preview/quartz/public/sitemap.xml

# 资源是绝对路径还是相对路径?(决定子路径能否兼容)
grep -oE '(href|src)="[^"]+"' ~/Desktop/quartz-preview/quartz/public/index.html | head
```

判断标准:
- ✅ sitemap 里的 URL 是 `https://kingrich.top/knowledge-base/quartz/...` 完整域名
- ✅ 内部资源是 `./index.css` / `./prescript.js` / `./00_核心概念/Transformer` 这种**相对路径**

满足以上两条 → 子路径部署天然兼容(见 § 6)。

### Step 4:打通 SSH

第一次部署需要:
```bash
ssh root@47.110.250.139
# 输密码登录,确认能进
```

要省去后续每次输密码 → 配 SSH key(本笔记不展开,可查 GitHub 或服务器供应商的官方文档)。

### Step 5:rsync 上传(关键!远端必须装 rsync)

```bash
rsync -avz --progress \
    /Users/xxddd/Desktop/quartz-preview/quartz/public/ \
    root@47.110.250.139:/www/wwwroot/kingrichhtml/knowledge-base/quartz/
```

**参数解释**:
- `-a`:archive 模式,保留权限/时间戳/软链
- `-v`:verbose,打印每个文件
- `-z`:传输时压缩(16 MB 实际传 4-5 MB)
- `--progress`:显示进度条
- 源路径**末尾的 `/`** 必须有(`public/` 表示"目录内容",`public` 不带斜杠会嵌套一层)

**远端没装 rsync 时的备选**(见 § 8.1)。

### Step 6:nginx 配置

宝塔面板的网站根目录是 `/www/wwwroot/kingrichhtml/`,在 nginx 的 server 块里加 location:

```nginx
location /knowledge-base/quartz/ {
    alias /www/wwwroot/kingrichhtml/knowledge-base/quartz/;
    index index.html;
    try_files $uri $uri.html $uri/ =404;
    charset utf-8;
}

# 末尾没斜杠时强制重定向到带斜杠(子路径部署的小坑,见 § 6.2)
location = /knowledge-base/quartz {
    return 301 /knowledge-base/quartz/;
}
```

**三个关键点缺一不可**:
1. `try_files $uri $uri.html` —— Quartz 产物是 `xxx.html`,URL 不带 `.html`
2. `location = ... return 301 ...` —— 末尾斜杠重定向
3. `charset utf-8` —— 中文路径

### Step 7:验证部署

回本地 Mac 跑:

```bash
# 1. 首页 200?
curl -s -o /dev/null -w "HTTP %{http_code}\n" https://kingrich.top/knowledge-base/quartz/

# 2. 任意一篇笔记 200?(中文 URL 自动 percent-encode)
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
    "https://kingrich.top/knowledge-base/quartz/00_核心概念/Transformer"

# 3. sitemap 能拿到?
curl -s https://kingrich.top/knowledge-base/quartz/sitemap.xml | head -5
```

三条全 `HTTP 200` → 部署成功。

### 部署完别忘记

把 `baseUrl` **改回 `localhost:8080`**,否则本地 build --serve 出来的 sitemap 和分享链接全是远端 URL。

---

## § 6. 子路径部署的特殊处理

"部署到根路径"(`kingrich.top/`)和"部署到子路径"(`kingrich.top/knowledge-base/quartz/`)有几个微妙差异,踩过一次就懂。

### 6.1 为什么 Quartz 子路径"恰好"工作

很多 SSG(比如早期 Hugo / 一些 React SPA)会把内部资源链接写成**绝对路径**(`/static/icon.png`)。如果你部署在子路径,这条链接会指向 `kingrich.top/static/icon.png` —— 404。要么改 SSG 配置加 `pathPrefix`,要么 nginx 加 `rewrite`,都麻烦。

**Quartz 的设计选择了相对路径**:
- 首页(`index.html`):`./static/icon.png` / `./00_核心概念/Transformer`
- 一级子页(`00_核心概念/Transformer.html`):`../static/icon.png`(自动多一级 `../`)
- 子目录的 README:同样按嵌套深度计算

效果:**你可以把 build 产物扔到任何路径下,所有内部链接都自然解析**。这是 Quartz 文档里没大力宣传但极其友好的特性。

### 6.2 末尾斜杠的坑

浏览器解析相对路径基于"当前 URL"。看这个例子:

| 访问的 URL | 浏览器把 `./static/icon.png` 解析成 |
|-----------|--------------------------------|
| `kingrich.top/knowledge-base/quartz/`(末尾 /) | `kingrich.top/knowledge-base/quartz/static/icon.png` ✅ |
| `kingrich.top/knowledge-base/quartz`(末尾无 /) | `kingrich.top/knowledge-base/static/icon.png` ❌(少一级!) |

所以 nginx 必须给"末尾无斜杠"的请求返回 301 加上斜杠,见 § 5 Step 6 的第二个 location 块。

### 6.3 sitemap / RSS 是绝对路径,所以必须改 `baseUrl`

虽然内部资源是相对路径,但 sitemap.xml 必须用绝对 URL(W3C 规范)。所以 `baseUrl` 必须改对,否则:

```xml
<!-- baseUrl 没改的话 -->
<loc>https://localhost:8080/00_核心概念/Transformer</loc>
                  ^^^^^^^^^^^^^^^ Google / Bing 爬虫看了想哭
```

---

## § 7. 后续每次更新流程

把上面 7 步压成一个 shell 脚本,后续更新一行命令搞定。

### 一键脚本 `deploy.sh`

放在 `~/Desktop/quartz-preview/deploy.sh`(`chmod +x deploy.sh` 加执行权限):

```bash
#!/bin/bash
# Quartz 部署脚本:改 baseUrl → build → rsync → 改回 localhost
set -e

QUARTZ_DIR="$HOME/Desktop/quartz-preview/quartz"
CONFIG="$QUARTZ_DIR/quartz.config.ts"
REMOTE_BASEURL="kingrich.top/knowledge-base/quartz"
LOCAL_BASEURL="localhost:8080"
REMOTE_TARGET="root@47.110.250.139:/www/wwwroot/kingrichhtml/knowledge-base/quartz/"

cd "$QUARTZ_DIR"

echo "→ 把 baseUrl 改成远端"
sed -i.bak "s|baseUrl: \"$LOCAL_BASEURL\"|baseUrl: \"$REMOTE_BASEURL\"|" "$CONFIG"

echo "→ 跑 quartz build"
npx quartz build

echo "→ rsync 推到远端"
rsync -avz --progress public/ "$REMOTE_TARGET"

echo "→ 改回本地 baseUrl"
sed -i.bak "s|baseUrl: \"$REMOTE_BASEURL\"|baseUrl: \"$LOCAL_BASEURL\"|" "$CONFIG"
rm -f "$CONFIG.bak"

echo "✓ 部署完成 → https://kingrich.top/knowledge-base/quartz/"
```

使用:
```bash
~/Desktop/quartz-preview/deploy.sh
```

进阶:可以加 `read -p "确认部署?[y/N] "` 防误触、加 `git commit` 自动提交知识库改动、加部署完后 `curl` 验证等。

---

## § 8. 常见报错速查

### 8.1 `bash: rsync: 未找到命令`(远端报)

**原因**:rsync 是"两端协议",本地有,但远端服务器没装。

**解决**(选一个):
```bash
# 方案 A:远端装 rsync(推荐,一劳永逸)
ssh root@<server>
yum install -y rsync   # CentOS / 阿里云 Linux / RHEL
apt install -y rsync   # Ubuntu / Debian
dnf install -y rsync   # Rocky / AlmaLinux

# 方案 B:改用 scp(SSH 自带,远端不用装东西)
scp -r ~/.../public/. root@<server>:/path/   # 注意源路径末尾是 /. 不是 /

# 方案 C:tar 打包后 scp(更快,16M → 4-5M)
tar czf /tmp/site.tar.gz -C ~/.../public .
scp /tmp/site.tar.gz root@<server>:/tmp/
ssh root@<server> "cd /path/ && tar xzf /tmp/site.tar.gz && rm /tmp/site.tar.gz"
```

### 8.2 `Permission denied (publickey,password)`

- 密码输错 / 远端禁了密码登录 → 跟管理员要密码或配 SSH key
- SSH key 在但没加进 ssh-agent → `ssh-add ~/.ssh/id_rsa`

### 8.3 部署后访问 404

可能原因(按出现概率排序):
1. **nginx 没配 `try_files $uri $uri.html`** —— Quartz URL 不带 `.html`,但产物是 `.html`,nginx 默认找不到
2. **路径写错** —— `alias` 后面那段必须末尾带斜杠,且跟 `location` 末尾斜杠一致(`location /a/` 配 `alias /b/`)
3. **文件没真传过去** —— `ssh root@<server> "ls /path/"` 验证

### 8.4 访问 200 但样式乱

- 浏览器缓存 → 强刷(Cmd+Shift+R / Ctrl+F5)
- 子路径部署末尾没斜杠 → 见 § 6.2
- 子页面 `../static/...` 找不到 → 同样是末尾斜杠问题

### 8.5 中文路径访问报错

- nginx 缺 `charset utf-8;`
- 链接没做 URL 编码(percent-encode) → 浏览器一般自动做,但用 curl 测试要手动 `urlencode`

### 8.6 sitemap.xml 里全是 localhost

`baseUrl` 没改成远端域名就 build 了 → 改完 `baseUrl` **重新 build** 再上传。Quartz 不会自动更新已 emit 的 sitemap。

### 8.7 build 时报 `isn't yet tracked by git, dates will be inaccurate`

Quartz 默认从 git 历史读"创建时间 / 修改时间"。新增的 `.md` 还没 commit → 它就 fall back 到文件系统时间,**只是日期不准,不影响 build 成功**。`git add` 一下就消失。

---

## § 9. 概念扩展:其他 SSG 怎么类比

学会 Quartz 这套流水线(`改源 → build → 产物 → 部署`),其他 SSG 几乎一通百通,差异只在工具替换:

| SSG | 写作语言 | build 命令 | 产物目录 | 主语言 | 定位 |
|-----|---------|-----------|---------|--------|------|
| **Quartz** | Markdown + Obsidian flavor | `npx quartz build` | `public/` | TypeScript | 笔记/Wiki(Backlinks / Graph) |
| **Hugo** | Markdown + Hugo shortcodes | `hugo` | `public/` | Go | 速度王者,博客通用 |
| **Jekyll** | Markdown + Liquid | `jekyll build` | `_site/` | Ruby | GitHub Pages 默认 |
| **Astro** | `.astro` 组件 + Markdown | `astro build` | `dist/` | TypeScript | 灵活,可混 React/Vue/Svelte |
| **Eleventy(11ty)** | Markdown / Nunjucks 等 | `eleventy` | `_site/` | JavaScript | 极简,无前端框架强加 |
| **Docusaurus** | Markdown + React 组件 | `npm run build` | `build/` | TypeScript(React) | 技术文档,Meta 出品 |
| **MkDocs** | Markdown | `mkdocs build` | `site/` | Python | 极简文档,Material 主题神 |
| **VitePress** | Markdown + Vue 组件 | `vitepress build` | `.vitepress/dist/` | TypeScript(Vue) | Vue 生态官方文档 |
| **Next.js(static export)** | TSX + Markdown | `next build && next export` | `out/` | TypeScript(React) | 既能 SSG 也能 SSR,大型项目 |

**学过 Quartz 之后,你接手任何一个新 SSG 最需要确认的 3 件事**:
1. 写作语法 / frontmatter 字段(每家略有差异,核心都是 markdown + 元数据)
2. 配置文件的位置和关键字段(baseUrl / theme / plugins / 输出目录)
3. build 命令和产物目录

剩下的部署流程(rsync / nginx / Cloudflare Pages)**完全通用**——这就是为什么这套工作流值得专门学一次。

---

## § 10. 与本知识库其他章节的关联

- **概念铺垫**:[云服务交付模型](云服务交付模型.md) 解释了 IaaS / PaaS / SaaS 的分层——你用 VPS 是 IaaS,用 Cloudflare Pages 是 PaaS。本笔记的"路线 A vs 路线 B"对照就是 IaaS vs PaaS 的实战选择
- **CI/CD 配套**:[CI/CD 与 GitHub Actions](CI-CD与GitHub-Actions.md) 把"路线 B(GH Pages / Cloudflare Pages)"里的"自动 build + 部署"机制单独讲透——含 workflow yaml 详解 / 触发器类型 / 5 大踩坑 / 主流 CI 工具横评
- **底层工具**:[GitHub项目入门/程序小白概念扫盲手册](GitHub项目入门/程序小白概念扫盲手册.md) 讲了 npm / Docker / Nginx 的基础,本笔记假设你看过它对 nginx / npm 有最低限度认知
- **Git 基础**:[GitHub项目入门/Git进阶速查](GitHub项目入门/Git进阶速查.md) 讲了 `stash` / `rebase` / `tag` 等——本笔记的"deploy.sh 进阶加 git commit 自动提交"流程配合它使用
- **术语速查**:[程序员黑话速查](程序员黑话速查.md) 已有 SaaS / IaaS / PaaS / FaaS 等云服务条目,可对照看
- **网络基础**(待补全):本笔记没展开 HTTPS 证书申请、CDN 缓存策略、DNS 解析等——这些属于"运维基础"主题,目前知识库没专门笔记,后续可补

---

## § 11. 术语速查

| 术语 | 中英对照 | 一句话解释 |
|------|---------|-----------|
| **SSG** | Static Site Generator,静态站点生成器 | 把源文件提前编译成静态 HTML 的工具 |
| **build** | 构建 | 跑 SSG,把源文件变成产物 |
| **产物 / artifact** | build 输出 | 编译完的 HTML/CSS/JS 文件集合(Quartz 里是 `public/`) |
| **baseUrl** | 基础 URL | 站点的对外访问域名 + 路径,用于 sitemap/RSS 等绝对链接 |
| **sitemap** | 站点地图 | 列出站点所有页面 URL 的 XML 文件,给搜索引擎爬虫看 |
| **RSS feed** | 订阅源 | 让读者用 RSS 阅读器订阅你站点更新的 XML |
| **SPA** | Single Page Application,单页应用 | 切页时只换内容不刷新整个浏览器(Quartz 默认开) |
| **canonical URL** | 标准 URL | 告诉搜索引擎"同一内容的多个 URL 里哪个是正版",避免 SEO 罚分 |
| **rsync** | remote sync,远程同步 | 增量传输工具,只传差异部分,比 scp 高效 |
| **scp** | secure copy,安全复制 | SSH 自带的文件传输工具,简单但不增量 |
| **子路径部署** | subpath deployment | 把站点部署在域名的某个路径下(如 `/knowledge-base/quartz/`)而不是根 |
| **try_files**(nginx 指令) | —— | 按顺序尝试匹配多个文件路径,第一个找到的就返回 |
| **location**(nginx 指令) | —— | 根据 URL 路径匹配不同的处理规则 |
| **alias / root**(nginx 指令) | —— | `root` 拼接 URL 后缀到磁盘路径,`alias` 替换前缀(子路径部署常用) |
| **CDN** | Content Delivery Network,内容分发网络 | 在全球部署节点缓存内容,让用户就近访问 |
| **PaaS** | Platform as a Service | 平台即服务,如 Cloudflare Pages / Vercel(你不管服务器,只管推代码) |
| **frontmatter** | —— | markdown 文件开头用 `---` 包裹的 YAML 元数据(title / date / tags 等) |
| **Backlinks** | 反向链接 | "哪些页面引用了当前页",Quartz / Obsidian 等笔记工具的核心特性 |
| **hot reload** | 热重载 | 改源文件 → 浏览器自动刷新,无需手动 build(`quartz build --serve` 提供) |

---

*最后更新:2026-05-27(从这次把知识库部署到 `kingrich.top/knowledge-base/quartz/` 的实战流程沉淀而来。本笔记定位是"路线 A(自有 VPS + rsync)的完整 SOP + SSG 范式入门",路线 B(Cloudflare Pages)/路线 C(服务器自 build)的详细实战可作为后续补全方向。)*
