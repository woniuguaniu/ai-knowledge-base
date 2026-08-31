import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "与 AI 交流 AI",
    pageTitleSuffix: " · 知识库",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-CN",
    baseUrl: "localhost:8080",
    ignorePatterns: [
      "private",
      "templates",
      ".obsidian",
      "_templates",
      ".claude",
      "CLAUDE.md",
      "claude code skills知识",
      ".quartz-config",
      "_scripts",
      ".github",
    ],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Schibsted Grotesk",
        body: "Source Sans Pro",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#f8f4ec",
          lightgray: "#d9d2c2",
          gray: "#807866",
          darkgray: "#3a342a",
          dark: "#1a1815",
          secondary: "#a8482c",
          tertiary: "#5c7349",
          highlight: "rgba(168, 72, 44, 0.08)",
          textHighlight: "#f5d28a66",
        },
        darkMode: {
          light: "#1a1714",
          lightgray: "#363128",
          gray: "#7a7064",
          darkgray: "#c9c0ad",
          dark: "#ebe5d5",
          secondary: "#d97757",
          tertiary: "#9bb88a",
          highlight: "rgba(217, 119, 87, 0.12)",
          textHighlight: "#7a4b1a66",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "relative" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // CustomOgImages 因数字键帽 emoji (1️⃣) 在中文笔记里报错，先禁用
      // Plugin.CustomOgImages(),
    ],
  },
}

export default config
