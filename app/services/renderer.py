from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def render_html(context: dict[str, Any], template_name: str = "resume_template.html") -> str:
    template = _env.get_template(template_name)
    return template.render(**context)


def html_to_pdf(html: str) -> bytes:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html)
            return page.pdf(format="Letter")
        finally:
            browser.close()
