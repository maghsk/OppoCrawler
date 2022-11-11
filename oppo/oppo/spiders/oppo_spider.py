import scrapy
import scrapy.selector

from scrapy import Request
from scrapy.http import Response
from typing import Optional

from oppo.items import HtmlData, JavaScriptData

from datetime import datetime

class OppoSpider(scrapy.Spider):
    name = "oppo"
    start_urls = ['https://www.oppo.com/cn/smartphones/series-find-n/find-n/3d/']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse_js(self, response: Response):
        origin_url: str = response.meta.get('origin_url')
        if type(response.body) is bytes:
            code = response.body.decode('utf-8')
        elif type(response.body) is str:
            code = response.body
        else:
            raise ValueError()

        yield JavaScriptData(
            access_time=datetime.utcnow(),
            url=response.url,
            code=code,
            lit_used_getcontext = code.find("getContext") != -1,
            lit_used_webgl = code.find("webgl") != -1,
            # origin_url=origin_url,
            # url=response.url,
            # js=JavaScriptData.from_str(r),
            # name=response.meta.get('name')
        )

    def parse(self, response: Response):
        lst = response.xpath('//script')
        js_lst: list[str] = []
        # remote_js_dict: dict[str, Optional[str]] = {}
        # remote_js_count = 0
        remote_js_url_list: list[str] = []
        for item in lst:
            if 'src' in item.attrib:
                # remote_js_count += 1
                url: str = item.attrib.get('src')
                if not url.startswith('http'):
                    url = response.urljoin(url)

                # remote_js_dict[url] = f"{remote_js_count}.json"
                remote_js_url_list.append(url)

                yield scrapy.Request(
                    url = url,
                    callback = self.parse_js,     # lambda x: js_lst.append(x.body),
                    meta = {
                        'origin_url': response.url,
                        # 'name': f"{remote_js_count}.json"
                    },
                    priority = 1,
                )
            else:
                js_lst.append(item.get())

        yield HtmlData(
            access_time=datetime.utcnow(),
            url=response.url,
            js_code_list=js_lst,
            remote_js_url_list=remote_js_url_list,
            lit_used_getcontext = any(code.find("getContext") != -1 for code in js_lst),
            lit_used_webgl = any(code.find("webgl") != -1 for code in js_lst),
        )

