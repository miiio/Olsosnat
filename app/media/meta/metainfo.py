import os.path
import regex as re

import log
from app.helper import WordsHelper
from app.media.meta.metaanime import MetaAnime
from app.media.meta.metavideo import MetaVideo
from app.media.meta.metajav import MetaJav
from app.utils.types import MediaType
from config import RMT_MEDIAEXT


def MetaInfo(title, subtitle=None, mtype=None):
    """
    媒体整理入口，根据名称和副标题，判断是哪种类型的识别，返回对应对象
    :param title: 标题、种子名、文件名
    :param subtitle: 副标题、描述
    :param mtype: 指定识别类型，为空则自动识别类型
    :return: MetaAnime、MetaVideo
    """

    # 应用自定义识别词
    title, msg, used_info = WordsHelper().process(title)
    if subtitle:
        subtitle, _, _ = WordsHelper().process(subtitle)

    if msg:
        for msg_item in msg:
            log.warn("【Meta】%s" % msg_item)

    # 判断是否处理文件
    if title and os.path.splitext(title)[-1] in RMT_MEDIAEXT:
        fileflag = True
    else:
        fileflag = False

    if mtype == MediaType.JAV or is_jav(title):
        fh = is_jav(title)
        cc = checkChineseCaptions(fh, title)
        meta_info = MetaJav(title, fh, cc, fileflag)
    elif mtype == MediaType.ANIME or is_anime(title):
        meta_info = MetaAnime(title, subtitle, fileflag)
    else:
        meta_info = MetaVideo(title, subtitle, fileflag)

    meta_info.ignored_words = used_info.get("ignored")
    meta_info.replaced_words = used_info.get("replaced")
    meta_info.offset_words = used_info.get("offset")
    return meta_info

def is_jav(title):
    if not title:
        return None
    if title.endswith('/'):
        title = title[:-1]
    else:
        title = title[title.rfind('/')+1:]
    title = title.upper().replace("SIS001", "").replace("1080P", "").replace("720P", "").replace("2160P", "")
    t = re.search(r'T28[\-_]\d{3,4}', title)
    # 一本道
    if not t:
        t = re.search(r'1PONDO[\-_]\d{6}[\-_]\d{2,4}', title)
        if t:
            t = t.group().replace("1PONDO_", "").replace("1PONDO-", "")
    if not t:
        t = re.search(r'HEYZO[\-_]?\d{4}', title)
    if not t:
        # 加勒比
        t = re.search(r'CARIB[\-_]\d{6}[\-_]\d{3}' ,title)
        if t:
            t = t.group().replace("CARIB-", "").replace("CARIB_", "")
    if not t:
        # 东京热
        t = re.search(r'N[-_]\d{4}' ,title)
    
    if not t:
        # Jukujo-Club | 熟女俱乐部
        t = re.search(r'JUKUJO[-_]\d{4}' ,title)

    # 通用
    if not t:
        t = re.search(r'S[A-Z]{1,4}[-_]\d{3,5}' ,title)
    if not t:
        t = re.search(r'[A-Z]{2,5}[-_]\d{3,5}' ,title)
    if not t:
        t = re.search(r'\d{6}[\-_]\d{2,4}' ,title)

    # if not t:
    #     t = re.search(r'[A-Z]+\d{3,5}' ,title)
    
    # if not t:
    #     t = re.search(r'[A-Za-z]+[-_]?\d+' ,title)
    
    # if not t:
    #     t = re.search(r'\d+[-_]?\d+' ,title)
        
    if not t:
        return None
    else:
        t = t.group().replace("_", "-")
        return t

def checkChineseCaptions(fh, title):
    if not fh or not title:
        return False
    if title.find("中文字幕") != -1:
        return True
    match = re.match(fh + "[_-]C", title.upper().replace('_','-'))
    if match:
        return True
    return False


def is_anime(name):
    """
    判断是否为动漫
    :param name: 名称
    :return: 是否动漫
    """
    if not name:
        return False
    if re.search(r'【[+0-9XVPI-]+】\s*【', name, re.IGNORECASE):
        return True
    if re.search(r'\s+-\s+[\dv]{1,4}\s+', name, re.IGNORECASE):
        return True
    if re.search(r"S\d{2}\s*-\s*S\d{2}|S\d{2}|\s+S\d{1,2}|EP?\d{2,4}\s*-\s*EP?\d{2,4}|EP?\d{2,4}|\s+EP?\d{1,4}", name,
                 re.IGNORECASE):
        return False
    if re.search(r'\[[+0-9XVPI-]+]\s*\[', name, re.IGNORECASE):
        return True
    return False
