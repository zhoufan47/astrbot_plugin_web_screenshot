# CHANGELOG

## v1.0.0 (2024-06-11)

### ✨ 新功能

- **网页截图** — 基于 Playwright Chromium 无头浏览器，支持截取任意网页截图
- **手动指令** — 通过 `/screenshot` 指令截图，支持 `--width`、`--height`、`--full-page`、`--timeout` 参数
- **LLM 工具调用** — 通过 `@filter.llm_tool` 注册 `screenshot_webpage` 工具，AI 可直接调用截图
- **自定义视口** — 支持自定义浏览器窗口宽度和高度（默认 1920×1080）
- **整页截图** — 支持截取包括滚动区域的整个页面
- **自动 URL 补全** — URL 缺少协议前缀时自动添加 `https://`
- **浏览器生命周期管理** — 初始化时预启动浏览器，卸载时自动清理资源

### 🐛 修复

- 修复命令参数解析中命令名被误认为 URL 的问题
- 修复浏览器继承 AstrBot 代理环境变量的问题（通过 `env` 参数过滤代理变量 + `--no-proxy-server`）
- 修复连续截图时浏览器连接状态冲突的问题（添加 `asyncio.Lock()` 并发控制 + 移除不稳定的 `--single-process` 参数）

### ⚙️ 技术细节

- 浏览器引擎：Playwright Chromium headless
- 截图格式：PNG
- 代理处理：启动时清除 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` 等环境变量
- 并发控制：`asyncio.Lock()` 串行化截图操作
