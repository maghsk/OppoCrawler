import scrapy
import scrapy.selector
import random

import logging

from pathlib import Path

from scrapy import Request
from scrapy.http import Response
from typing import Optional

from ..items import HtmlData, JavaScriptData

from datetime import datetime


class TrancoSpider(scrapy.Spider):
    name = "tranco"
    # start_urls = ['https://www.oppo.com/cn/smartphones/series-find-n/find-n/3d/']
    tranco_top1M_csv_path_str = "/home/maghsk/storage/Projects/WebGL Empirical Study/Crawler/tranco/top-1m.csv"
    max_depth = 2
    max_width = 2
    max_retry = 2  # total access := max_retry + 1

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    def start_requests(self):
        # tranco_top1M_csv_path = Path(self.tranco_top1M_csv_path_str)
        # tranco_list: list[str] = [x.strip().split(',')[1] for x in tranco_top1M_csv_path.read_text().strip().splitlines()]
        tranco_list = ['www.oppo.com']
        for url in tranco_list:
            logging.info(f"seeding {url}")
            yield Request(url=f"http://{url}", callback=self.parse, meta={"cur_depth": 0, "retry": 0})

    def parse_js(self, response: Response):
        if response.status != 200:
            if response.meta["retry"] < self.max_retry:
                yield Request(url=response.url, callback=self.parse_js,
                              meta={"cur_depth": response.meta["cur_depth"], "retry": response.meta["retry"] + 1})
            else:
                yield JavaScriptData(
                    access_time=None,
                    url=response.url,
                    code=None,
                    lit_used_getcontext=None,
                    lit_used_webgl=None,
                )
            return

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
            lit_used_getcontext=code.find("getContext") != -1,
            lit_used_webgl=code.find("webgl") != -1,
            # origin_url=origin_url,
            # url=response.url,
            # js=JavaScriptData.from_str(r),
            # name=response.meta.get('name')
        )

    def parse(self, response: Response):
        if response.status != 200:
            if response.meta["retry"] < self.max_retry:
                yield Request(url=response.url, callback=self.parse_js,
                              meta={"cur_depth": response.meta["cur_depth"], "retry": response.meta["retry"] + 1})
            else:
                yield HtmlData(
                    url=response.url,
                    access_time=None,
                    js_code_list=None,
                    remote_js_url_list=None,
                    lit_used_webgl=None,
                    lit_used_getcontext=None,
                )
            return

        logging.info(f"parsing {response.url}")
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
                    url=url,
                    callback=self.parse_js,  # lambda x: js_lst.append(x.body),
                    meta={'origin_url': response.url, 'retry': 0, },
                    priority=10,
                )
            else:
                js_lst.append(item.get())

        # Expanding
        next_depth = response.meta.get("cur_depth") + 1
        if next_depth <= self.max_depth:
            a_set = set(x.attrib.get('href') for x in response.xpath("//a"))
            a_set = set(x for x in a_set if x and (x.startswith("http") or x[0] == '/'))
            a_set = set(x if x.startswith("http") else response.urljoin(x) for x in a_set)

            if len(a_set) > 0:
                expand_list = random.choices(list(a_set), k=min(len(a_set), self.max_width))
                for url in expand_list:
                    yield Request(url, callback=self.parse, meta={"cur_depth": next_depth, "retry": 0})

        # Yielding
        yield HtmlData(
            access_time=datetime.utcnow(),
            url=response.url,
            js_code_list=js_lst,
            remote_js_url_list=remote_js_url_list,
            lit_used_getcontext=any(code.find("getContext") != -1 for code in js_lst),
            lit_used_webgl=any(code.find("webgl") != -1 for code in js_lst),
        )
