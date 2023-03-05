import random
from threading import Lock
from time import sleep

import zhconv

from app.utils.commons import singleton
from app.utils import ExceptionUtils, StringUtils

import log
from config import Config
from app.media.javbusapi import JavbusApi, JavbusWeb
from app.media.javlibapi import JavlibWeb
from app.media.meta import MetaInfo
from app.utils import RequestUtils
from app.utils.types import MediaType
from app.helper import JavMetaHelper

lock = Lock()


@singleton
class Javbus:
    cookie = None
    # javbusapi = None
    javbusweb = None
    javlibweb = None
    message = None
    metaHelper = None

    def __init__(self):
        self.init_config()

    def init_config(self):
        # self.javbusapi = JavbusApi()
        self.javbusweb = JavbusWeb()
        self.javlibweb = JavlibWeb()
        self.metaHelper = JavMetaHelper()
        
    def search_jav_medias_by_ids(self, ids, mtype: MediaType = None, season=None, episode=None, page=1):
        """
        根据关键字搜索豆瓣，返回可能的标题和年份信息
        """
        if not ids:
            return []
        ret_medias = []
        save_flag = False
        for id in ids: 
            item = self.metaHelper.get_meta_data_by_key(id.upper())
            if not item:
                item = self.get_jav_detail(id, wait=True)
                save_flag = True
            
            if item not in ret_medias:
                ret_medias.append(item)
        if save_flag:
            self.metaHelper.save_meta_data(True)
        return ret_medias

    def search_jav_medias(self, keyword, mtype: MediaType = None, season=None, episode=None, page=1):
        """
        根据关键字搜索豆瓣，返回可能的标题和年份信息
        """
        if not keyword:
            return []
        result = self.javbusweb.search(keyword, page=page)
        if not result:
            return []
        ret_medias = []
        for item_obj in result.get("movies"):
            item = item_obj
            meta_info = MetaInfo(title=item.get("id"))
            meta_info.type = MediaType.JAV
            
            meta_info.year = item.get("date")
            meta_info.tmdb_id = item.get('id')
            meta_info.douban_id = item.get("id")
            meta_info.overview = item.get("title") or ""
            meta_info.poster_path = item.get("img").split('?')[0]
            rating = item.get("rating", {}) or {}
            meta_info.vote_average = rating.get("value")
            if meta_info not in ret_medias:
                ret_medias.append(meta_info)

        return ret_medias
    
    
    def search_jav_actor_medias(self, aid, page=1):
        if not aid:
            return []
        result = self.javbusweb.actor_medias(aid, page=page)
        return result.get('movies', [])
        
    
    def get_jav_detail(self, id, wait=False):
        """
        根据jav ID返回jav详情，带休眠
        """
        # 缓存
        cache = self.metaHelper.get_meta_data_by_key(id)
        
        if cache and cache.get('id') and len(cache.get('magnets', [])) > 0:
            log.info("【Javbus】使用Javbus缓存获取Jav详情：%s" % id)
            return cache
        
        log.info("【Javbus】正在通过Javbus API查询Jav详情：%s" % id)
        # 随机休眠
        if wait:
            time = round(random.uniform(1, 3), 1)
            log.info("【Javbus】随机休眠：%s 秒" % time)
            sleep(time)
            
            
        jav_info = self.javbusweb.detail(id)
        
        jav_info['post_img'] = jav_info.get('img', '')
        if jav_info.get('img'):
            jav_info['post_img'] = jav_info.get('img').replace('cover', 'thumb').replace('_b.jpg', '.jpg')
            
        if not jav_info:
            log.warn("【Javbus】%s 未找到Jav详细信息" % id)
            return None
        if not jav_info.get("title"):
            log.warn("【Javbus】%s 未找到Jav详细信息" % id)
            return None
        log.info("【Javbus】查询到数据：%s" % jav_info.get("title"))
        
        
        # 去javlib获取评分
        log.info("【Javlib】正在通过Javlib API查询Jav详情(获取评分)：%s" % id)
        javlib_info = self.javlibweb.detail_by_javid(id)
        if javlib_info:
            log.info("【Javlib】查询到数据：%s, 评分：%s" % (javlib_info.get("id"), str(javlib_info.get('rating'))))
            jav_info['rating'] = javlib_info.get('rating')
            jav_info['javlib_id'] = javlib_info.get('vid')
        else:
            jav_info['rating'] = 0.0
            jav_info['javlib_id'] = ''
            
        self.metaHelper.update_meta_data({
            id.upper() : jav_info
        })
        return jav_info

    @staticmethod
    def __dict_items(infos, media_type=None):
        """
        转化为字典
        """
        # ID
        ret_infos = []
        for info in infos:
            rid = info.get("id")
            # 评分
            rating = info.get('rating')
            if rating:
                vote_average = float(rating.get("value"))
            else:
                vote_average = 0
            # 标题
            title = info.get('title')
            # 年份
            year = info.get('year')

            if not media_type:
                if info.get("type") not in ("movie", "tv"):
                    continue
                mtype = MediaType.MOVIE if info.get("type") == "movie" else MediaType.TV
            else:
                mtype = media_type

            if mtype == MediaType.MOVIE:
                type_str = "MOV"
                # 海报
                poster_path = info.get('cover', {}).get("url")
                if not poster_path:
                    poster_path = info.get('cover_url')
                if not poster_path:
                    poster_path = info.get('pic', {}).get("large")
            else:
                type_str = "TV"
                # 海报
                poster_path = info.get('pic', {}).get("normal")

            # 简介
            overview = info.get("card_subtitle") or ""
            if not year and overview:
                if overview.split("/")[0].strip().isdigit():
                    year = overview.split("/")[0].strip()

            # 高清海报
            if poster_path:
                poster_path = poster_path.replace("s_ratio_poster", "m_ratio_poster")

            ret_infos.append({
                'id': "DB:%s" % rid,
                'orgid': rid,
                'title': title,
                'type': type_str,
                'media_type': mtype.value,
                'year': year[:4] if year else "",
                'vote': vote_average,
                'image': poster_path,
                'overview': overview
            })
        return ret_infos
