# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
from datetime import datetime
from functools import lru_cache
from random import choice
from urllib import parse

import requests

from app.utils import RequestUtils
from app.utils.commons import singleton


@singleton
class JavbusApi(object):
    _urls = {
        # 搜索类
        "search": "/api/v1/movies/search",
        "detail": "/api/v1/movies",
    }

    _user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"]
    _base_url = "http://192.168.1.101:8922"
    _session = requests.Session()

    def __init__(self):
        pass

    @classmethod
    @lru_cache(maxsize=256)
    def __invoke(cls, url, **kwargs):
        req_url = cls._base_url + url

        params = {}
        if kwargs:
            params.update(kwargs)

        headers = {'User-Agent': choice(cls._user_agents)}
        resp = RequestUtils(headers=headers, session=cls._session).get_res(url=req_url, params=params)

        return resp.json() if resp else None

    def search(self, keyword, page=1, magnet='all', type='normal'):
        return self.__invoke(self._urls["search"], keyword=keyword, page=page, magnet=magnet, type=type)
    
    def jav_detail(self, id):
        return self.__invoke(self._urls["detail"] + "/" + id)
