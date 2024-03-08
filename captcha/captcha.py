import base64
import json
import re
import requests
import subprocess
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs


class Captcha:
    def __init__(self, id, referer):
        self.id = id
        self.referer = referer
        self.result = None
        self.ctx = self.load_js()
        # 加载js文件后，获取fp和callback
        self.fp = self.ctx.call("fp")
        self.cb = self.ctx.call("n2")

        # 获取验证配置
        self.conf = json.loads(self.get_config())
        self.captchar_conf = json.loads(self.get_captchar())
        self.captchar_data = self.format_captchar_data()

    def get_config(self):
        """
        获取验证配置
        :return: 返回验证配置数据，包括zoneId和acToken
        """
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": self.referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
        }
        url = "http://c.dun.163.com/api/v2/getconf"
        params = {
            "referer": self.referer,
            "zoneId": "",
            "dt": "mb4hpi1g6N9AA1FRFELBoZJAWfjtjfZm",
            "id": self.id,
            "ipv6": "false",
            "runEnv": "10",
            "iv": "3",
            "loadVersion": "2.4.0",
            "callback": "__JSONP_4xhi7dv_0"
        }

        response = requests.get(url, headers=headers, params=params)
        print(response.text)
        return re.findall("\\((.*)\\)", response.text)[0]

    def load_js(self):
        """
        加载js文件
        :return:
        """
        with open("captcha/encrypt.js", "r", encoding="UTF-8") as f:
            all_js = f.read()
        ctx = execjs.compile(all_js)
        return ctx

    def encrypt_check_data(self, move_rate):
        """
        加密验证数据
        :param data: 验证数据
        :return: 加密后的验证数据
        """

        return self.ctx.call("get_data", self.captchar_data["token"], move_rate)

    def encrypt_login_data(self, username, password, validate, fp):
        """
        加密登录数据
        :param username: 用户名
        :param password: 密码
        :param validate: 验证码
        :param fp: fp
        :return: 加密后的登录数据
        """
        return self.ctx.call("login_encrypt", username, password, validate, fp)

    def get_captchar(self):
        """
        获取验证码
        :param
        :return 返回验证码数据，包括背景图，前景图和token
        """
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": self.referer,
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "http://c.dun.163.com/api/v3/get"

        params = {
            "referer": self.referer,
            "zoneId": self.conf["data"]["zoneId"],
            "acToken": self.conf["data"]["ac"]["token"],
            "id": self.id,
            "dt": "mb4hpi1g6N9AA1FRFELBoZJAWfjtjfZm",
            "fp": self.fp,
            "https": "true",
            "type": "2",
            "version": "2.24.0",
            "dpr": "1.5",
            "dev": "3",
            "cb": self.cb,
            "ipv6": "false",
            "runEnv": "10",
            "group": "",
            "scene": "",
            "lang": "zh-CN",
            "sdkVersion": "undefined",
            "iv": "3",
            "width": "0",
            "audio": "false",
            "sizeType": "10",
            "smsVersion": "v3",
            "token": "",
            "callback": "__JSONP_rd0fzi9_0"
        }

        response = requests.get(url, headers=headers, params=params)

        # {"data":{"bg":["https://necaptcha.nosdn.127.net/0e8dd1c225e94c438e5234812913446e.jpg","https://necaptcha1.nosdn.127.net/0e8dd1c225e94c438e5234812913446e.jpg"],"front":["https://necaptcha.nosdn.127.net/eb8f980cbbf4453492f69c52b5795219.png","https://necaptcha1.nosdn.127.net/eb8f980cbbf4453492f69c52b5795219.png"],"token":"4137c182bc0c4bcfb06a8d0a7f42a80d","type":2,"zoneId":"CN31"},"error":0,"msg":"ok"}

        return re.findall("\\((.*)\\)", response.text)[0]

    def check_captchar(self, move_rate):
        """
        提交验证
        :param: move_rate: 验证码滑块移动距离和总长度的比值，范围0-1
        :return: 返回验证结果 _JSONP_7oahebp_1({"data":{"result":true,
                "zoneId":"CN31","token":"dec6de880bd14a28a85bb22cf55ad638",
                "validate":"smU5uUd8C4R6FE5occftQk3OC9zFQ3qvmQJlX0BjwKesaqK6BJ0Z0NtdiTPzf1li5AnFVmqv4ueCJqYCig55fjXMs136VcByxFqjWekRoiO5YXjBFtnUPRMj6eDBXQZKR/Wi7Xdho7Id4UyPGi2t83KIUsBUgCS5TuzzCX2AuDM="},"error":0,"msg":"ok"
                });
        """
        data = self.encrypt_check_data(move_rate)
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": self.referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
        }
        url = "http://c.dun.163.com/api/v3/check"

        params = {
            "referer": "http://app.miit-eidc.org.cn/miitxxgk/gonggao/xxgk/queryQyData",
            "zoneId": "CN31",
            "dt": "GWGte120lfdFQkFVUFeR5dCkL9BcQwab",
            "id": self.id,
            "token": self.captchar_data["token"],
            "acToken": self.conf["data"]["ac"]["token"],
            "data": json.dumps(data),
            "width": "320",
            "type": "2",
            "version": "2.24.0",
            "cb": self.cb,
            "extraData": "",
            "bf": "0",
            "runEnv": "10",
            "sdkVersion": "undefined",
            "iv": "3",
            "callback": "__JSONP_7oahebp_1"
        }
        response = requests.get(url, headers=headers, params=params)
        # print("验证码验证结果：", response.text)
        return re.findall("\\((.*)\\)", response.text)[0]

    def format_captchar_data(self):
        """
        格式化验证码数据
        :return: 包含背景图，前景图和token的字典
        """
        bg = requests.get(self.captchar_conf["data"]["bg"][0])
        bg = str(base64.b64encode(bg.content)).replace("b'", "").replace("'", "")
        front = requests.get(self.captchar_conf["data"]["front"][0])
        front = str(base64.b64encode(front.content)).replace("b'", "").replace("'", "")

        token = self.captchar_conf["data"]["token"]

        charchar_data = {
            "smallImage": front,
            "bigImage": bg,
            "token": token
        }
        return charchar_data

