from functools import lru_cache

import requests
from lxml import etree

from app.utils import RequestUtils, ExceptionUtils
from app.utils.commons import singleton
from config import Config
from app.helper.chrome_helper import ChromeHelper
import log

@singleton
class MissavWeb(object):
    _session = requests.Session()

    _web_base = "https://missav.com/cn"
    _page_limit = 50
    _timout = 5
    _proxies = Config().get_proxies()
    _ua = Config().get_ua()
    chrome = None

    _weburls = {
        # 今日
        "today_views": f"{_web_base}/today-hot?page=%s",
        # 本周
        "week_views": f"{_web_base}/weekly-hot?page=%s",
        # 本月
        "month_views": f"{_web_base}/monthly-hot?page=%s",
    }

    _webparsers = {
        "hots": {
            "list": "//div[@class='grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-5']/div/div",
            "item": {
                "title": "./div[2]/a/text()",
                "cover": "./div[1]/a[1]/img/@src",
                "url": "./div[1]/a[2]/@href",
                "code": "./div[1]/a[2]/@href",
                "vid": "./div[1]/a[2]/@href",
                "videoLength": "./div[1]/a[2]/span/text()"
            },
            "format": {
                "code": lambda a:None if not a else a[a.rfind('/')+1:].upper(),
                "vid": lambda a:None if not a else a[a.rfind('/')+1:].upper(),
                "videoLength": lambda x:None if not x else x.strip()
            }
        },
    }

    def __int__(self, cookie=None):
        # self.chrome = ChromeHelper()
        pass

    @classmethod
    def __invoke_web(cls, url, *kwargs):
        req_url = cls._weburls.get(url)
        url=req_url % kwargs
        
        chrome = ChromeHelper()
        if not chrome.get_status():
            log.error("【MISSAV】未找到浏览器内核")
            return []
        # 访问页面
        if not chrome.visit(url, ua=cls._ua):
            log.error("【MISSAV】无法连接missav.com！")
            return []
        # 源码
        html_text = chrome.get_html()
        return html_text

    @classmethod
    def __invoke_json(cls, url, *kwargs):
        req_url = cls._jsonurls.get(url)
        if not req_url:
            return None
        req = RequestUtils(session=cls._session,
                           timeout=cls._timout).get_res(url=req_url % kwargs)
        return req.json() if req else None

    @staticmethod
    def __get_json(json):
        if not json:
            return None
        return json.get("subjects")

    @classmethod
    def __get_list(cls, url, html):
        if not url or not html:
            return None
        xpaths = cls._webparsers.get(url)
        if not xpaths:
            return None
        items = etree.HTML(html).xpath(xpaths.get("list"))
        if not items:
            return None
        result = []
        for item in items:
            obj = {}
            for key, value in xpaths.get("item").items():
                format = lambda x:x
                if xpaths.get("format") and xpaths.get("format").get(key):
                    format = xpaths.get("format").get(key)
                default = None
                if isinstance(value, list):
                    default = value[1]
                    value = value[0]
                if isinstance(value, str):
                    text = item.xpath(value)
                    if text:
                        obj[key] = format(text) if len(text) > 1 else format(text[0])
                    else:
                        obj[key] = default
            if obj:
                result.append(obj)
        return result

    @classmethod
    def __get_obj(cls, url, html):
        if not url or not html:
            return None
        xpaths = cls._webparsers.get(url)
        if not xpaths:
            return None
        obj = {}
        for key, value in xpaths.items():
            try:
                text = etree.HTML(html).xpath(value)
                if text:
                    obj[key] = text[0]
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
        return obj

    @classmethod
    @lru_cache(maxsize=1)
    def hot(cls, type="today",page=1):
        """
        查询最想要
        :param type: [today, week, month]
        :param page: 页码
        """
        if type not in ['today', 'week', 'month']: type = 'today'
        ret = cls.__get_list("hots", cls.__invoke_web("%s_views"%type, page))
        