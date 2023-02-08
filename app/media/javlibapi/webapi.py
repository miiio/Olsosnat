from functools import lru_cache

import requests
from lxml import etree

from app.utils import RequestUtils, ExceptionUtils
from app.utils.commons import singleton


@singleton
class JavlibWeb(object):
    _session = requests.Session()

    _web_base = "https://www.u65w.com/cn/"
    _page_limit = 50
    _timout = 5

    _weburls = {
        # 最想要
        "mostwanted": f"{_web_base}/vl_mostwanted.php?page=%s&mode=%s&",
        # 评价最高
        "bestrated": f"{_web_base}/vl_bestrated.php?page=%s&mode=%s&",
        # 新发行
        "newrelease": f"{_web_base}/vl_newrelease.php?page=%s&mode=%s&",
        # 新加入
        "newentries": f"{_web_base}/vl_newentries.php?page=%s&mode=%s&",
    }

    _webparsers = {
        "common_list": {
            "list": '//*[@class="video"]',
            "item": {
                "title": "./a/div[2]/text()",
                "cover": "./a/img/@onerror",
                "code": "./a/div[1]/text()",
                "vid": "./@id",
            }
        },
    }

    def __int__(self, cookie=None):
        pass

    @classmethod
    def __invoke_web(cls, url, *kwargs):
        req_url = cls._weburls.get(url)
        if not req_url:
            return None
        return RequestUtils(session=cls._session,
                            timeout=cls._timout).get(url=req_url % kwargs)

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
                text = item.xpath(value)
                if text:
                    obj[key] = text[0]
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
    @lru_cache(maxsize=256)
    def mostwanted(cls, page=1, mode=1):
        """
        查询最想要
        """
        return cls.__get_list("common_list", cls.__invoke_web("mostwanted", page, mode))

    @classmethod
    @lru_cache(maxsize=256)
    def bestrated(cls, page=1, mode=1):
        """
        查询评价最高
        """
        return cls.__get_list("common_list", cls.__invoke_web("bestrated", page, mode))
    
    
    @classmethod
    @lru_cache(maxsize=256)
    def newrelease(cls, page=1, mode=1):
        """
        查询新发行
        """
        return cls.__get_list("common_list", cls.__invoke_web("newrelease", page, mode))
    
    
    @classmethod
    @lru_cache(maxsize=256)
    def newentries(cls, page=1, mode=1):
        """
        查询新加入
        """
        return cls.__get_list("common_list", cls.__invoke_web("newentries", page, mode))
    