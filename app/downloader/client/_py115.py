import re
import time
from urllib import parse

import requests
import re

from app.utils import RequestUtils, ExceptionUtils


class Py115:
    cookie = None
    user_agent = None
    req = None
    uid = ''
    sign = ''
    err = None

    def __init__(self, cookie):
        self.cookie = cookie
        self.req = RequestUtils(cookies=self.cookie, session=requests.Session())

    # 登录
    def login(self):
        # if not self.getuid():
        #     return False
        if not self.getsign():
            return False
        return True

    # 获取目录ID
    def getdirid(self, tdir):
        try:
            url = "https://webapi.115.com/files/getid?path=" + parse.quote(tdir or '/')
            p = self.req.get_res(url=url)
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = "获取目录 [{}]ID 错误：{}".format(tdir, rootobject["error"])
                    return False, ''
                return True, rootobject.get("id")
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False, ''

    # 获取sign
    def getsign(self):
        try:
            self.sign = ''
            url = "https://115.com/?ct=offline&ac=space&_=" + str(round(time.time() * 1000))
            p = self.req.get_res(url=url)
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = "获取 SIGN 错误：{}".format(rootobject.get("error_msg"))
                    return False
                self.sign = rootobject.get("sign")
                return True
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False

    # 获取UID
    def getuid(self):
        try:
            self.uid = ''
            url = "https://webapi.115.com/files?aid=1&cid=0&o=user_ptime&asc=0&offset=0&show_dir=1&limit=30&code=&scid=&snap=0&natsort=1&star=1&source=&format=json"
            p = self.req.get_res(url=url)
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = "获取 UID 错误：{}".format(rootobject.get("error_msg"))
                    return False
                self.uid = rootobject.get("uid")
                return True
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False

    # 获取任务列表
    def gettasklist(self, page=1):
        try:
            tasks = []
            url = "https://115.com/web/lixian/?ct=lixian&ac=task_lists"
            while True:
                postdata = "page={}&uid={}&sign={}&time={}".format(page, self.uid, self.sign,
                                                                   str(round(time.time() * 1000)))
                p = self.req.post_res(url=url, params=postdata.encode('utf-8'))
                if p:
                    rootobject = p.json()
                    if not rootobject.get("state"):
                        self.err = "获取任务列表错误：{}".format(rootobject["error"])
                        return False, tasks
                    if rootobject.get("count") == 0:
                        break
                    tasks += rootobject.get("tasks") or []
                    if page >= rootobject.get("page_count"):
                        break
            return True, tasks
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False, []

    # 添加任务
    def addtask(self, tdir, content):
        try:
            ret, dirid = self.getdirid(tdir)
            if not ret or (tdir != '/' and dirid == 0):
                return False, '115目录不存在'

            # 转换为磁力
            if re.match("^https*://", content):
                try:
                    p = self.req.get_res(url=content)
                    if p and p.headers.get("Location"):
                        content = p.headers.get("Location")
                except Exception as result:
                    ExceptionUtils.exception_traceback(result)
                    content = str(result).replace("No connection adapters were found for '", "").replace("'", "")

            url = "https://115.com/web/lixian/?ct=lixian&ac=add_task_url"
            postdata = "url={}&savepath=&wp_path_id={}&uid={}&sign={}&time={}".format(parse.quote(content), dirid,
                                                                                      self.uid, self.sign,
                                                                                      str(round(time.time() * 1000)))
            p = self.req.post_res(url=url, params=postdata.encode('utf-8'))
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = rootobject.get("error_msg")
                    return False, ''
                return True, rootobject.get("info_hash")
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False, ''

    # 删除任务
    def deltask(self, thash):
        try:
            url = "https://115.com/web/lixian/?ct=lixian&ac=task_del"
            postdata = "hash[0]={}&uid={}&sign={}&time={}".format(thash, self.uid, self.sign,
                                                                  str(round(time.time() * 1000)))
            p = self.req.post_res(url=url, params=postdata.encode('utf-8'))
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = rootobject.get("error_msg")
                    return False
                return True
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False

    # 根据ID获取文件夹路径
    def getiddir(self, tid):
        try:
            path = '/'
            url = "https://aps.115.com/natsort/files.php?aid=1&cid={}&o=file_name&asc=1&offset=0&show_dir=1&limit=40&code=&scid=&snap=0&natsort=1&record_open_time=1&source=&format=json&fc_mix=0&type=&star=&is_share=&suffix=&custom_order=0".format(
                tid)
            p = self.req.get_res(url=url)
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = "获取 ID[{}]路径 错误：{}".format(id, rootobject["error"])
                    return False, path
                patharray = rootobject["path"]
                for pathobject in patharray:
                    if pathobject.get("cid") == 0:
                        continue
                    path += pathobject.get("name") + '/'
                if path == "/":
                    self.err = "文件路径不存在"
                    return False, path
                return True, path
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False, '/'

    def adddir(self, pid, cname):
        try:
            url = "https://webapi.115.com/files/add"
            postdata = "pid={}&cname={}".format(pid, cname)
            p = self.req.post_res(url=url, params=postdata.encode('utf-8'))
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = rootobject.get("error_msg")
                    return False
                return True
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False
    
    def getm3u8(self, pid):
        if pid.startswith('https://v.anxia.com/?pickcode='):
            pid = pid[30:]
        try:
            url = "https://115.com/api/video/m3u8/" + pid + ".m3u8"
            p = self.req.get_res(url=url).text
            if p:
                # #EXTM3U
                # #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=3000000,RESOLUTION=1920x1080,NAME="UD"
                # http://cpats01.115.com/3bb1095f4b8bdfceeb0badfab4de1a04/63E8E052/E7C7E8A0389912E4520193142C3FA1A86A98D7AC/E7C7E8A0389912E4520193142C3FA1A86A98D7AC_1920.m3u8?u=594084887&t=d1d984a902535d4e024a3ce51f512a77&s=157286400
                # #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1800000,RESOLUTION=1280x720,NAME="HD"
                # http://cpats01.115.com/89ef0b182759a4e01cb0ac35a1b2659c/63E8E052/E7C7E8A0389912E4520193142C3FA1A86A98D7AC/E7C7E8A0389912E4520193142C3FA1A86A98D7AC_1280.m3u8?u=594084887&t=d1d984a902535d4e024a3ce51f512a77&s=104857600
                dataList = p.split('\n')
                m3u8 = []
                temp = '"YH"|原画|"BD"|4K|"UD"|蓝光|"HD"|超清|"SD"|高清|"3G"|标清'
                txt = temp.split('|')
                for i in range(6):
                    for j,e in enumerate(dataList):
                        if e.find(txt[i*2]) != -1:
                            m3u8.append({'name': txt[i*2+1], 'url': dataList[j+1].replace('\r', ''), 'type': 'hls'})
                            
                return True, m3u8
            else:
                return False, "播放失败，视频未转码！"
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return False, self.err
    
    def searchjav(self, javid):
        if not javid:
            return None
        javid2 = javid.replace('-', "")
        javid3 = javid.replace('-', "00")
        javid4 = javid.replace('-', "0")
        reg = '{}|{}|{}|{}'.format(javid,javid2,javid3,javid4)
        try:
            url = "https://webapi.115.com/files/search?search_value={}%20{}%20{}%20{}&format=json".format(javid,javid2,javid3,javid4)
            p = self.req.get_res(url=url)
            if p:
                rootobject = p.json()
                if not rootobject.get("state"):
                    self.err = rootobject.get("error_msg")
                    return None
                for item in rootobject.get('data', []):
                    if item.get('play_long') and item.get('n') and re.search(reg.upper(), item.get('n').upper()):
                        return 'https://v.anxia.com/?pickcode=' + item.get('pc')
                return None
        except Exception as result:
            ExceptionUtils.exception_traceback(result)
            self.err = "异常错误：{}".format(result)
        return None