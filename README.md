# 🌐 Web Screenshot - AstrBot 网页截图插件

基于 Playwright 的网页截图插件，支持通过 **手动指令** 和 **LLM 工具调用** 两种方式截取网页截图。

## ✨ 功能特性

- 📸 **网页截图** — 使用 Playwright 无头浏览器截取指定 URL 的网页截图
- 🖥️ **自定义视口** — 支持自定义浏览器窗口宽度和高度（默认 1920×1080）
- 📄 **整页截图** — 支持截取整个页面内容（包括滚动区域）
- 🤖 **LLM 工具调用** — 通过 `@filter.llm_tool` 注册为 LLM 函数，AI 可直接调用截图
- ⏱️ **超时控制** — 可配置页面加载超时时间
- 🔒 **无代理** — 浏览器启动时自动清除代理环境变量，直连目标网站

## 📋 安装

### 方法一：通过 AstrBot 插件市场安装

在 AstrBot 管理面板的插件市场中搜索 `web_screenshot` 并安装。

### 方法二：手动安装

将本仓库克隆或下载到 AstrBot 的 `addons` 目录：

```bash
cd /path/to/astrbot/addons
git clone https://github.com/zhoufan47/astrbot_plugin_web_screenshot.git
```

### 安装 Playwright 及浏览器

```bash
pip install playwright
playwright install chromium
```

> **Linux 系统**：如果遇到 `libnspr4.so` 等库缺失错误，运行 `playwright install-deps chromium` 安装系统依赖。

## 🚀 使用方法

### 手动指令

```
/screenshot <url> [--width 宽度] [--height 高度] [--full-page] [--timeout 超时(ms)]
```

**示例：**

| 命令 | 说明 |
|------|------|
| `/screenshot https://example.com` | 截取 example.com 首页 |
| `/screenshot https://example.com --width 1280 --height 720` | 自定义视口 1280×720 |
| `/screenshot https://example.com --full-page` | 截取整个页面 |
| `/screenshot https://example.com --timeout 15000` | 设置页面加载超时 15 秒 |

### LLM 工具调用

配置好 LLM 后，AI 会自动识别 `screenshot_webpage` 工具。当对话中涉及需要查看网页内容时，LLM 将自动调用该工具进行截图。

LLM 调用参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | 必填 | 目标网页 URL |
| `width` | int | 1920 | 浏览器视口宽度 |
| `height` | int | 1080 | 浏览器视口高度 |
| `full_page` | bool | false | 是否截取整个页面 |

## ⚙️ 技术细节

- **浏览器引擎**：Chromium（Playwright 管理）
- **截图格式**：PNG
- **浏览器生命周期**：插件初始化时预启动，卸载时自动清理；运行中自动检测断连并重连
- **并发控制**：使用 `asyncio.Lock()` 串行化截图操作，避免并发冲突
- **代理处理**：启动浏览器前过滤 `HTTP_PROXY` / `HTTPS_PROXY` 等环境变量，确保直连

## 📦 依赖

- `playwright` — 浏览器自动化库
- `astrbot` — AstrBot 框架（插件运行环境）

## 📝 CHANGELOG

详见 [CHANGELOG.md](./CHANGELOG.md)

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。
