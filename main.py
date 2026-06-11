import os
import tempfile
from typing import Optional

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger


@register(
    "web_screenshot",
    "YourName",
    "基于 Playwright 的网页截图插件，支持 LLM 工具调用或手动指令进行网页截图。",
    "1.0.0",
)
class WebScreenshotPlugin(Star):
    """
    网页截图插件
    功能：截取指定 URL 的网页截图，返回图片。
    支持手动指令和 LLM 工具调用两种方式。
    """

    def __init__(self, context: Context):
        super().__init__(context)
        self._browser = None
        self._playwright = None

    async def initialize(self):
        """异步初始化，预启动 Playwright 浏览器实例"""
        try:
            await self._ensure_browser()
            logger.info("WebScreenshotPlugin: Playwright browser started successfully.")
        except Exception as e:
            logger.warning(
                f"WebScreenshotPlugin: Browser pre-start failed, will retry on first use: {e}"
            )

    async def terminate(self):
        """插件卸载时清理浏览器资源"""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            logger.info("WebScreenshotPlugin: Playwright browser closed.")
        except Exception as e:
            logger.error(f"WebScreenshotPlugin: Cleanup error: {e}")

    async def _ensure_browser(self):
        """确保浏览器实例已启动且可用"""
        from playwright.async_api import async_playwright

        if self._playwright is None:
            self._playwright = await async_playwright().start()
        if self._browser is None or not self._browser.is_connected():
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                    "--no-proxy-server",
                ],
            )
            logger.info("WebScreenshotPlugin: Browser instance created.")

    async def _take_screenshot(
        self,
        url: str,
        width: int = 1920,
        height: int = 1080,
        full_page: bool = False,
        timeout: int = 30000,
    ) -> str:
        """
        执行网页截图
        :param url: 目标网页 URL
        :param width: 视口宽度
        :param height: 视口高度
        :param full_page: 是否截取整个页面
        :param timeout: 超时时间（毫秒）
        :return: 截图文件的临时路径
        """
        await self._ensure_browser()

        # 自动补全 URL 协议
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        context = await self._browser.new_context(
            viewport={"width": width, "height": height},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            # 等待页面稳定
            await page.wait_for_timeout(1000)

            # 生成截图文件
            fd, filepath = tempfile.mkstemp(suffix=".png")
            os.close(fd)

            screenshot_options = {"path": filepath, "type": "png"}
            if full_page:
                screenshot_options["full_page"] = True

            await page.screenshot(**screenshot_options)
            logger.info(f"WebScreenshotPlugin: Screenshot saved to {filepath}")
            return filepath
        finally:
            await page.close()
            await context.close()

    # ==================== 手动指令方式 ====================

    @filter.command("screenshot")
    async def screenshot_command(self, event: AstrMessageEvent):
        """
        截取网页截图。
        用法: /screenshot <url> [--width 宽度] [--height 高度] [--full-page] [--timeout 超时(ms)]
        示例:
          /screenshot https://example.com
          /screenshot https://example.com --width 1280 --height 720
          /screenshot https://example.com --full-page
          /screenshot https://example.com --timeout 15000
        """
        text = event.message_str.strip()

        # 解析参数
        url = None
        width = 1920
        height = 1080
        full_page = False
        timeout = 30000

        # 分割参数，跳过第一个 token（即命令名本身 "screenshot"）
        parts = text.split()
        for i, part in enumerate(parts):
            if part == "--width" and i + 1 < len(parts):
                try:
                    width = int(parts[i + 1])
                except ValueError:
                    pass
            elif part == "--height" and i + 1 < len(parts):
                try:
                    height = int(parts[i + 1])
                except ValueError:
                    pass
            elif part == "--timeout" and i + 1 < len(parts):
                try:
                    timeout = int(parts[i + 1])
                except ValueError:
                    pass
            elif part == "--full-page":
                full_page = True
            elif not part.startswith("--") and url is None and part != "screenshot":
                url = part

        if not url:
            yield event.plain_result(
                "请提供一个 URL。\n"
                "用法: /screenshot <url> [--width 宽度] [--height 高度] [--full-page]"
            )
            return

        yield event.plain_result(f"正在截取 {url} 的截图，请稍候...")

        try:
            filepath = await self._take_screenshot(
                url=url,
                width=width,
                height=height,
                full_page=full_page,
                timeout=timeout,
            )
            yield event.image_result(filepath)
            # 清理临时文件
            try:
                os.remove(filepath)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"WebScreenshotPlugin: Screenshot failed: {e}")
            yield event.plain_result(f"截图失败: {str(e)}")

    # ==================== LLM 工具调用方式 ====================

    @filter.llm_tool(name="screenshot_webpage")
    async def screenshot_webpage(
        self,
        event: AstrMessageEvent,
        url: str,
        width: Optional[int] = 1920,
        height: Optional[int] = 1080,
        full_page: Optional[bool] = False,
    ):
        """
        截取指定网页的截图并返回图片。

        Args:
            url(string): 要截图的网页完整 URL，例如 https://example.com
            width(int): 浏览器视口宽度，默认 1920
            height(int): 浏览器视口高度，默认 1080
            full_page(bool): 是否截取整个页面（包括滚动部分），默认 false
        """
        try:
            filepath = await self._take_screenshot(
                url=url,
                width=width or 1920,
                height=height or 1080,
                full_page=full_page or False,
            )
            yield event.image_result(filepath)
            try:
                os.remove(filepath)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"WebScreenshotPlugin: Tool screenshot failed: {e}")
            yield event.plain_result(f"网页截图失败: {str(e)}")
