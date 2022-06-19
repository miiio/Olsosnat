import requests
import urllib3

from config import DEFAULT_HEADERS


# noinspection RequestsNoVerify
class RequestUtils:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    __headers = None
    __cookies = None
    __proxies = None
    __timeout = 15
    __session = None

    def __init__(self, headers, cookies, proxies=False, session=None):
        if headers:
            if isinstance(headers, str):
                self.__headers = {"User-Agent": f"{headers}"}
            else:
                self.__headers = headers
        else:
            self.__headers = DEFAULT_HEADERS

        if cookies:
            if isinstance(cookies, str):
                self.__cookies = self.cookie_parse(cookies)
            else:
                self.__cookies = cookies
        if proxies:
            self.__proxies = proxies

        if session:
            self.__session = session

    def post(self, url, params, json=None):
        if json is None:
            json = {}
        i = 0
        while i < 3:
            try:
                if self.__session:
                    return self.__session.post(url, data=params, verify=False, headers=self.__headers,
                                               proxies=self.__proxies, json=json)
                else:
                    return requests.post(url, data=params, verify=False, headers=self.__headers,
                                         proxies=self.__proxies, json=json)
            except requests.exceptions.RequestException:
                i += 1

    def get(self, url, params=None):
        i = 0
        while i < 3:
            try:
                if self.__session:
                    r = self.__session.get(url, verify=False, headers=self.__headers,
                                           proxies=self.__proxies, params=params, timeout=10)
                else:
                    r = requests.get(url, verify=False, headers=self.__headers,
                                     proxies=self.__proxies, params=params, timeout=self.__timeout)
                return str(r.content, 'UTF-8')
            except requests.exceptions.RequestException:
                i += 1

    def get_res(self, url, params=None):
        i = 0
        while i < 3:
            try:
                if self.__session:
                    return self.__session.get(url, params=params, verify=False, headers=self.__headers,
                                              proxies=self.__proxies, cookies=self.__cookies, timeout=10)
                else:
                    return requests.get(url, params=params, verify=False, headers=self.__headers,
                                        proxies=self.__proxies, cookies=self.__cookies, timeout=self.__timeout)
            except requests.exceptions.RequestException as e:
                print(e)
                i += 1

    def post_res(self, url, params=None, allow_redirects=True):
        i = 0
        while i < 3:
            try:
                if self.__session:
                    return self.__session.post(url, params=params, verify=False, headers=self.__headers,
                                               proxies=self.__proxies, cookies=self.__cookies,
                                               allow_redirects=allow_redirects)
                else:
                    return requests.post(url, params=params, verify=False, headers=self.__headers,
                                         proxies=self.__proxies, cookies=self.__cookies,
                                         allow_redirects=allow_redirects)
            except requests.exceptions.RequestException as e:
                print(e)
                i += 1

    @staticmethod
    def cookie_parse(cookies_str):
        cookie_dict = {}
        cookies = cookies_str.split(';')
        for cookie in cookies:
            cstr = cookie.split('=')
            cookie_dict[cstr[0]] = cstr[1]
        return cookie_dict
