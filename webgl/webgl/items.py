# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class JavaScriptData:
    url: str
    access_time: Optional[datetime]
    code: Optional[str]
    lit_used_webgl: Optional[bool]
    lit_used_getcontext: Optional[bool]

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
    url: str
    access_time: Optional[datetime]
    js_code_list: Optional[List[str]]
    remote_js_url_list: Optional[List[str]]
    lit_used_webgl: Optional[bool]
    lit_used_getcontext: Optional[bool]
