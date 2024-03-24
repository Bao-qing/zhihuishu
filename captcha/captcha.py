import base64
import json
import re

import requests

from captcha.yidun_encrypt import yidun_encrypt


class Captcha:
    def __init__(self, id, referer):
        self.id = id
        self.referer = referer
        self.result = None
        self.type = None
        self.ctx = self.load_js()
        # 加载js文件后，获取fp和callback
        self.fp = self.ctx.call("fp")
        self.cb = self.ctx.call("n2")

        # 获取验证配置
        self.conf = json.loads(self.get_config())
        self.captchar_conf = self.get_captcha()
        self.captcha_data = self.format_captcha_data()

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
            # "dt": "TGloUsmhPF9FFxQFEAeVuWYDl9KV5leG",
            "id": self.id,
            "ipv6": "false",
            "runEnv": "10",
            "iv": "3",
            "loadVersion": "2.4.0",
            "callback": "__JSONP_4xhi7dv_0"
        }

        response = requests.get(url, headers=headers, params=params)
        # print(response.text)
        return re.findall("\\((.*)\\)", response.text)[0]

    def load_js(self):
        """
        加载加密函数
        :return:
        """
        # """
        # 加载js文件
        # :return:
        # """
        # with open("captcha/encrypt.js", "r", encoding="UTF-8") as f:
        #     all_js = f.read()
        # ctx = execjs.compile(all_js)

        ctx = yidun_encrypt()
        return ctx

    def encrypt_check_data(self, move_rate):
        """
        加密验证数据
        :param data: 验证数据
        :return: 加密后的验证数据
        """

        return self.ctx.call("get_data", self.captcha_data["token"], move_rate)

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

    def get_captcha(self):
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
            # "dt": "TGloUsmhPF9FFxQFEAeVuWYDl9KV5leG",
            "fp": self.fp,
            "https": "true",
            "type": "2",
            "version": "2.26.1",
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
        response_data = json.loads(re.findall("\\((.*)\\)", response.text)[0])

        # print(response_data)
        # 滑块 11 点选 2
        if response_data['data']["type"] == 2:
            print("滑块")
        if response_data['data']["type"] == 11:
            print("点选")

        self.type = response_data['data']["type"]

        return response_data

    def check_captcha(self, move_rate):
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
            "referer": self.referer,
            "zoneId": "CN31",
            # "dt": "TGloUsmhPF9FFxQFEAeVuWYDl9KV5leG",
            "id": self.id,
            "token": self.captcha_data["token"],
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

        return re.findall("\\((.*)\\)", response.text)[0]

    def format_captcha_data(self):
        """
        格式化验证码数据
        :return: 包含背景图，前景图（提示语），token和type(int)的字典
        """
        # 如果是点选，front里是提示语
        bg = requests.get(self.captchar_conf["data"]["bg"][0])
        bg = str(base64.b64encode(bg.content)).replace("b'", "").replace("'", "")

        if self.captchar_conf["data"]["type"] == 2:
            front = requests.get(self.captchar_conf["data"]["front"][0])
            front = str(base64.b64encode(front.content)).replace("b'", "").replace("'", "")

        elif self.captchar_conf["data"]["type"] == 11:
            front = self.captchar_conf["data"]["front"]

        # print("front:\t", front)

        token = self.captchar_conf["data"]["token"]

        charchar_data = {
            "smallImage": front,
            "bigImage": bg,
            "token": token,
            "type": self.type
        }
        return charchar_data

# if __name__ == "__main__":
# captcha_referer = "https://passport.zhihuishu.com/login"
# # 获取手机验证码和密码登录不一样
# captcha_id = "73a18dc827b24b18ad0783701a75277d"
# capt_cha = Captcha(captcha_id, captcha_referer)
#
# # 获取滑块移动距离（比例，0-1）
# move_rate = get_gap(capt_cha.captcha_data) / 320 * 100
# #print(move_rate)
#
# # 提交，直接传入移动比例即可，返回验证结果，包含validate和token等
# res = capt_cha.check_captcha(move_rate)
# print(res)
