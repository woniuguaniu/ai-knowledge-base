# Quartz 定制配置

这个目录存放本知识库对 [Quartz](https://quartz.jzhao.xyz/) 的**定制文件**，供 GitHub Actions 在云端构建时使用。

## 为什么需要它

Quartz 项目本身不在这个仓库里（本地在 `~/Desktop/quartz-preview/quartz`）。CI 跑在 GitHub 的云端机器上，会现拉一份**官方原版** Quartz——但原版是英文默认样式，没有本站的标题、配色和中文排版。

所以流程是：**拉官方版 → 用这里的文件覆盖 → 再构建**。

## 三个文件各管什么

| 文件 | 覆盖到 | 定制了什么 |
|---|---|---|
| `quartz.config.ts` | `quartz/quartz.config.ts` | 站点标题「与 AI 交流 AI」、中文 locale、ignorePatterns（排除 `_templates`、`.claude`、`CLAUDE.md` 等非笔记内容）、暖色调明暗主题 |
| `quartz.layout.ts` | `quartz/quartz.layout.ts` | 页面组件布局（清空了默认 footer 链接） |
| `styles/custom.scss` | `quartz/quartz/styles/custom.scss` | 「纸质杂志风」排版：中文字体栈（PingFang / 思源黑体等）、三栏宽度、标题层级、行高 |

## 改动时的注意事项

**本地和这里要保持同步。** 你在 `~/Desktop/quartz-preview/quartz` 里调完样式满意后，记得把改动同步过来：

```bash
cp ~/Desktop/quartz-preview/quartz/quartz.config.ts   .quartz-config/
cp ~/Desktop/quartz-preview/quartz/quartz.layout.ts   .quartz-config/
cp ~/Desktop/quartz-preview/quartz/quartz/styles/custom.scss .quartz-config/styles/
```

否则会出现「本地预览是对的，线上还是旧样式」。

**`baseUrl` 不用手动改。** 本地这份写的是 `localhost:8080`，CI 构建时会自动替换成线上域名（见 `.github/workflows/deploy-pages.yml` 的「设置 baseUrl」步骤）。所以本地保持 localhost 即可，不需要来回切换。

**Quartz 版本要对齐。** 当前锁定 **v4.5.2**（与本地一致），版本号写在 workflow 的 `QUARTZ_VERSION` 环境变量里。升级 Quartz 时，本地和那个变量要一起改——跨大版本时配置文件的 API 可能不兼容。

---

*最后更新：2026-08-31*
