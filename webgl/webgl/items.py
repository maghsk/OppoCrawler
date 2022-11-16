# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass
from datetime import datetime

@dataclass
class JavaScriptData:
    access_time: datetime
    url: str
    code: str
    lit_used_webgl: bool
    lit_used_getcontext: bool

    # @staticmethod
    # def from_url_str(url: str, code: str):
    #     lit_used_getcontext = code.find("getContext") != -1
    #     lit_used_webgl = code.find("webgl") != -1
    #     return JavaScriptData(
    #         url = url,
    #         code = code,
    #         lit_used_getcontext = lit_used_getcontext,
    #         lit_used_webgl = lit_used_webgl,
    #     )

@dataclass
class HtmlData:
    access_time: datetime
    url: str
    js_code_list: list[str]
    remote_js_url_list: list[str]
    lit_used_webgl: bool
    lit_used_getcontext: bool
