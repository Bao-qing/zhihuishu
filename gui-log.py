import base64
import ctypes
import io
import json
import re
import subprocess
import threading
import time
from functools import partial
from tkinter import *
from tkinter import Tk
from tkinter.ttk import *

import requests
from PIL import Image as PILImage, ImageTk
from tqdm import trange
from ttkbootstrap import *
from ttkbootstrap import *

from encrypt import *

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs

ctypes.windll.shcore.SetProcessDpiAwareness(1)

request = requests


class Requests:
    def __init__(self):
        pass

    def get(self, url, headers=None, cookies=None, verify=None, timeout=3, allow_redirects=None, params=None):
        times = 0
        while times < 3:
            try:
                return request.get(url, headers=headers, cookies=cookies, timeout=timeout,
                                   allow_redirects=allow_redirects, params=params, verify=verify)

            except:
                times += 1
                print("重试", times)
        # return request.get(url, headers=headers, cookies=cookies, verify=verify, timeout=3, allow_redirects=allow_redirects)

    def post(self, url, headers=None, cookies=None, data=None, verify=None, timeout=3, allow_redirects=None, ):
        times = 0
        while times < 3:
            try:
                return request.post(url, headers=headers, cookies=cookies, data=data, timeout=timeout,
                                    allow_redirects=allow_redirects, verify=verify)
            except:
                print("重试", times)
                times += 1
                print("重试", times)
        # return request.post(url, headers=headers, cookies=cookies, data=data, verify=verify, timeout=3, allow_redirects=allow_redirects)


requests = Requests()


class Zhihuishu:
    def __init__(self, username, password, ctx, validate, fp, cookies=None):
        self.wait_time = 0
        self.totaltime = None
        self.playtime = None
        self.playspeed = 1
        self.videoChapterDtos = None
        self.courseId = None
        self.recruitId = None
        if cookies is None:
            cookies = {}
        self.username = username
        self.password = password
        self.validate = validate
        self.uuid = None

        self.fp = fp

        self.ctx = ctx
        self.pwd = None
        self.uuid = None
        # self.session = requests.session()
        self.SESSION = None
        self.jt_cas = None
        self.cookies = cookies
        self.class_data = {
            "recruitAndCourseId": "4b515a5f415c4859454a585959455f445b",
            "dateFormate": 1703671623000
        }
        self.key = "azp53h0kft7qi78q"
        self.iv = '31673371716468346a7662736b623978'

    def get_all_class(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://onlineweb.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://onlineweb.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }

        url = "https://onlineservice-api.zhihuishu.com/gateway/t/v1/student/course/share/queryShareCourseInfo"
        data = {
            "secretStr": "NEuH3llD9woD4DQgu0k6Uvp5yyo8WT84Dq5lU2iPwvgKNatePzJ+vu/4PRaNYy+K",
            "date": "1704217471129"
        }

        cookies = {"jt-cas": self.cookies.get("jt-cas")}

        response = requests.post(url, headers=headers, cookies=cookies, data=data)

        # print(response)
        # print(response.text)

        try:

            class_list = []
            for i in response.json()["result"]["courseOpenDtos"]:
                class_list.append({"name": i["courseName"], "id": i["courseId"], "recruitAndCourseId": i['secret']})

            print("获取课程列表成功")
            # print(class_list)
            self.class_list = class_list
            return class_list
        except:
            print("获取课程列表失败,请检查cookies")
            return -1

    def login(self):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://passport.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://passport.zhihuishu.com/login?service=https://onlineservice-api.zhihuishu.com/login/gologin",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }

        url = "https://passport.zhihuishu.com/user/validateAccountAndPassword"
        data = {
            "secretStr": ctx.call("login_encrypt", self.username, self.password, self.validate, self.fp),

        }
        # print(data)
        # print("va")
        # print(self.validate)
        # print("fp")
        # print(self.fp)

        response = requests.post(url, data=data, verify=False, headers=headers)
        try:
            response_json = response.json()



        except:
            print("login错误：json加载失败")
            return -1, 0

        if response_json['status'] == -2:
            print("用户名或密码错误")

            return -2, response_json["pwdErrorCount"]
        if response_json['status'] == -6:
            print("你已连续5次登录失败，请5分钟后尝试")
            return -6, 0

        if response_json['status'] != 1:
            print(response_json)
            print("登录失败,未知错误")
            return response_json['status'], 0

        # print(response.text)
        # print(response.headers)
        # print(response)
        # cookie处理
        set_cookie = dict(response.cookies)
        self.cookies.update(set_cookie)
        # print(set_cookie)
        self.pwd = response_json["pwd"]
        self.uuid = response_json["uuid"]
        ## 还要向login发送请求

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://passport.zhihuishu.com/login?service=https^%^3A^%^2F^%^2Fonlineservice-api.zhihuishu.com^%^2Fgateway^%^2Ff^%^2Fv1^%^2Flogin^%^2Fgologin^%^3Ffromurl^%^3Dhttps^%^253A^%^252F^%^252Fonlineweb.zhihuishu.com^%^252F",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://passport.zhihuishu.com/login"
        params = {
            "pwd": self.pwd,
            "service": "https://onlineservice-api.zhihuishu.com/gateway/f/v1/login/gologin?fromurl=https%3A%2F%2Fonlineweb.zhihuishu.com%2F"
        }
        # 阻止重定向
        response = requests.get(url, headers=headers, cookies=self.cookies, params=params, verify=False,
                                allow_redirects=False)

        print("login2:", response.text)
        # print(response.text)
        # print(response)
        # print(response.headers)
        set_cookie = dict(response.cookies)
        self.cookies.update(set_cookie)
        # print(self.cookies)
        location1 = response.headers.get("location")
        # print("location1,重定向：", location1)
        response = requests.get(location1, headers=headers, cookies=self.cookies, verify=False,
                                allow_redirects=False)
        set_cookie = dict(response.cookies)
        self.cookies.update(set_cookie)
        # print(response)
        print("登录成功")

        # location2 = response.headers.get("location")
        # print("location2,重定向：", location2)
        # response = requests.get(location1, headers=headers, cookies=self.cookies, verify=False,
        #                         allow_redirects=False)
        # set_cookie = dict(response.cookies)
        # self.cookies.update(set_cookie)
        # print(response)

        print(self.cookies)

        # 保存cookies,fp,vaildate
        with open("cookies.json", "w") as f:
            write_data = {"cookies": self.cookies, "fp": self.fp, "validate": self.validate, "username": self.username,
                          "password": self.password}
            f.write(json.dumps(write_data))

        return 0, 0

    def get_videolist(self):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/videolist"

        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(self.class_data).replace("'", '"'), self.key, self.iv)
        # data = "secretStr=QhSgx0MEvvp0jRL20aaxWrXZYS%2F7NpyvaxFF5i8yEdUC0od6TN2zhNHxLPe53K4QZk0iJZX5DHKsdURDV9qsC7owkrF40cd%2FqJw1NxfwcCqOlIapESCmBFwJLBMJnVuo&dateFormate=1703742779000"
        response = requests.post(url, headers=headers, verify=False, cookies=self.cookies, data=data)
        # print(self.session.cookies)
        #
        # print(response.text)
        # print(response)
        response_json = response.json()

        # recruitId 和 courseId 在之前已获取（query_course）
        print(response.text)
        try:
            self.recruitId = response_json["data"]["recruitId"]
            self.courseId = response_json["data"]["courseId"]
            self.videoChapterDtos = response_json["data"]["videoChapterDtos"]
            print("获取课程列表成功")
            return response_json
        except:
            print("获取课程列表失败,请检查cookies")
            return -1

    def get_study_info(self):
        import requests

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "sec-ch-ua": "^\\^Google",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStuyInfo"
        all_class = {}
        lessonIds = []
        lessonVideoIds = []
        # videoSmallLessons
        video_data = {}
        for i in self.videoChapterDtos:
            for j in i["videoLessons"]:
                lessonIds.append(j["id"])
                if j["ishaveChildrenLesson"]:  # 有小节
                    for k in j["videoSmallLessons"]:
                        lessonVideoIds.append(k["id"])
                        video_data[str(k["id"])] = {"name": k["name"], "videoId": k["videoId"],
                                                    "chapterId": j["chapterId"], "videoSec": k["videoSec"],
                                                    "bigLessionId": j["id"], "smallLessionId": k["id"]}
                else:
                    video_data[str(j["id"])] = {"name": j["name"], "videoId": j["videoId"], "chapterId": j["chapterId"],
                                                "videoSec": j["videoSec"], "bigLessionId": j["id"], "smallLessionId": 0}
        all_class["recruitId"] = self.recruitId
        all_class["lessonVideoIds"] = lessonVideoIds
        all_class["lessonIds"] = lessonIds
        # print(all_class)
        # all_class = {"lessonIds":[1000309492,1000309493,1000309489,1000309494,1000309498,1001489532,1000309490,1000309496,1000309500,1000309491,1000309495,1000309499,1000309502,1001088268,1001088269,1001088270],"lessonVideoIds":[1001248005,1001248006,1001248007,1000227613,1000227616,1001248008,1001248009,1001248010,1001248011,1001248012,1001248013,1001248014],"recruitId":193745,"dateFormate":1703672514000}

        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(all_class).replace("'", '"'), self.key, self.iv)
        response = requests.post(url, headers=headers, cookies=self.cookies, data=data, verify=False)
        self.study_info = response.json()["data"]
        # print(video_data)
        # print(response.text)
        # print(response)
        for video_id, video_info in self.study_info["lv"].items():
            try:
                video_data[str(video_id)].update(video_info)
            except:
                pass
        for video_id, video_info in self.study_info["lesson"].items():
            try:
                video_data[str(video_id)].update(video_info)
            except:
                pass
        print("获取学习信息成功：")
        # print(video_data)
        self.video_data = video_data

    def query_course(self):
        course_data = self.class_data
        import requests

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryCourse"
        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(course_data).replace("'", '"'), self.key, self.iv)
        response = requests.post(url, headers=headers, cookies=self.cookies, data=data, verify=False)
        response_json = response.json()
        # print(response.text)
        # print(response)
        self.recruitId = response_json["data"]["recruitId"]
        self.courseId = response_json["data"]["courseInfo"]["courseId"]
        print("获取课程信息成功")

    def get_real_name(self):
        import requests

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }

        url = "https://studyservice-api.zhihuishu.com/gateway/f/v1/login/getLoginUserInfo"
        params = {
            "dateFormate": "1704220652000"
        }
        response = requests.get(url, headers=headers, cookies=self.cookies, params=params, verify=False)
        print("realname:", response.text)

        try:
            json_data = response.json()
            realName = json_data["data"]["realName"]
            self.uuid = json_data["data"]["uuid"]

            return realName
        except:
            return -1

    def play_class(self, class_id):
        print("开始播放课程：", self.video_data[class_id]["name"])
        if self.video_data[class_id]["watchState"] == 1:
            return
        play_js_hex = "766172206D61696E3D7B5F613A224167726365706E6474736C7A796F6843696130755340222C5F623A224130696C6E6468676140757372657A746F5343707963222C5F633A22643040796F7241746C687A534365756E706361676973222C5F643A227A7A7074746A64222C5A3A66756E6374696F6E2874297B666F722876617220693D22222C683D303B683C742E6C656E6774683B682B2B29692B3D745B685D2B223B223B72657475726E20693D692E737562737472696E6728302C692E6C656E6774682D31292C746869732E582869297D2C583A66756E6374696F6E2874297B666F722876617220693D22222C683D303B683C745B746869732E5F635B385D2B746869732E5F615B345D2B746869732E5F635B31355D2B746869732E5F615B315D2B746869732E5F615B385D2B746869732E5F625B365D5D3B682B2B297B76617220733D745B746869732E5F615B335D2B746869732E5F615B31345D2B746869732E5F635B31385D2B746869732E5F615B325D2B746869732E5F625B31385D2B746869732E5F625B31365D2B746869732E5F635B305D2B746869732E5F615B345D2B746869732E5F625B305D2B746869732E5F625B31355D5D2868295E746869732E5F645B746869732E5F625B32315D2B746869732E5F625B365D2B746869732E5F615B31375D2B746869732E5F635B355D2B746869732E5F625B31385D2B746869732E5F635B345D2B746869732E5F615B375D2B746869732E5F615B345D2B746869732E5F615B305D2B746869732E5F635B375D5D286825746869732E5F645B746869732E5F615B31305D2B746869732E5F625B31335D2B746869732E5F625B345D2B746869732E5F615B315D2B746869732E5F635B375D2B746869732E5F615B31345D5D293B692B3D746869732E592873297D72657475726E20697D2C593A66756E6374696F6E2874297B72657475726E28743D28743D745B746869732E5F635B375D2B746869732E5F615B31335D2B746869732E5F615B32305D2B746869732E5F625B31355D2B746869732E5F615B325D2B746869732E5F625B325D2B746869732E5F635B31355D2B746869732E5F635B31395D5D28313629295B746869732E5F625B335D2B746869732E5F615B345D2B746869732E5F625B345D2B746869732E5F615B315D2B746869732E5F635B375D2B746869732E5F635B395D5D3C323F746869732E5F625B315D2B743A74295B746869732E5F615B395D2B746869732E5F625B335D2B746869732E5F635B32305D2B746869732E5F635B31375D2B746869732E5F635B31335D5D282D34297D7D3B66756E6374696F6E20656E63727970742874297B72657475726E206D61696E2E5A2874297D"
        ctx_play = execjs.compile(bytes.fromhex(play_js_hex).decode("utf-8"))
        pre_learn_data = self.pre_learning_note(class_id)
        this_video_data = [
            self.recruitId,  # 0
            self.video_data[str(class_id)]["bigLessionId"],  # 1
            self.video_data[str(class_id)]["smallLessionId"],  # smallLessionId # 2
            self.video_data[str(class_id)]["videoId"],  # 3
            self.video_data[str(class_id)]["chapterId"],  # chapterId         # 4
            "0",  # studyStatus                               # 5
            0,  # 6 playtime
            pre_learn_data['studyTotalTime'],  # 7 totalstudytime
            pre_learn_data['learnTime'],  # 8 getPosition
            self.uuid + "zhs",  # 9 getDuration
        ]
        total_time = self.video_data[str(class_id)]["videoSec"]

        for i in trange(round(pre_learn_data['studyTotalTime'] / 10), round((total_time) / 10)):
            self.playtime = i
            self.totaltime = round((total_time) / 10)
            this_video_data[6] = 0
            watch_point = "0,1"
            ctrl = 1
            while ctrl:
                self.wait_time = this_video_data[6]
                time.sleep(1 / self.playspeed)
                this_video_data[6] += 1
                this_video_data[7] += 1
                a = this_video_data[7]
                b = a // 3600
                c = (a - b * 3600) // 60
                d = a - b * 3600 - c * 60
                this_video_data[8] = "%02d:%02d:%02d" % (b, c, d)
                watch_point += "," + str(round(this_video_data[7] / 5) + 2)
                if this_video_data[6] > 10:
                    ctrl = 0

            post_data = {
                'ewssw': watch_point,
                'sdsew': ctx_play.call("encrypt", this_video_data),
                'zwsds': str(base64.b64encode(str(pre_learn_data['id']).encode("utf-8"))).replace("b'", "").replace("'",
                                                                                                                    ""),
                'courseId': self.courseId,
            }
            self.post_class(post_data)
            print("已完成：" + str(i) + "/" + str(round((total_time) / 10)))

    def post_class(self, postData):
        # print("post_class:", postData)
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTimeV2"
        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(postData).replace("'", '"'), self.key, self.iv)
        # print(encrypt_aes_cbc_pkcs7(str(postData).replace("'", '"'), self.key, self.iv))

        response = requests.post(url, headers=headers, cookies=self.cookies, data=data, verify=False)
        print("post_class:", response.json()['message'])

        # print(response.text)
        # print(response)

    def pre_learning_note(self, class_id):
        import requests

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Pragma": "no-cache",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "^\\^Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\\^Windows^^"
        }
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/prelearningNote"
        data_to_encrypt = {"ccCourseId": self.courseId, "chapterId": self.video_data[str(class_id)]["chapterId"],
                           "isApply": 1, "lessonId": self.video_data[str(class_id)]["bigLessionId"],
                           "lessonVideoId": self.video_data[str(class_id)]["smallLessionId"],
                           "recruitId": self.recruitId, "videoId": self.video_data[str(class_id)]["videoId"],
                           }

        data = {
            "secretStr": encrypt_aes_cbc_pkcs7(str(data_to_encrypt).replace("'", '"'), self.key, self.iv),
            "dateFormate": "1703765635000"
        }
        response = requests.post(url, headers=headers, cookies=self.cookies, data=data, verify=False)
        print("获取视频播放进度成功")
        # print(response.text)
        # print(response)
        try:
            return response.json()["data"]['studiedLessonDto']
        except:
            # print(self.video_data)
            print("获取视频播放进度失败")
            print(response.text)


class WinGUI_verify(Toplevel):
    def __init__(self):

        super().__init__()
        self.__win()
        self.tk_scale_lm35sfc1 = self.__tk_scale_lm35sfc1(self)
        self.canvas = self.tk_canve()
        self.tk_lable_tips = self.tk_lable_tips()
        self.tk_button_sub_verify = self.tk_button_sub_verify()
        self.tk_button_refresh = self.tk_button_refresh()

    def __win(self):
        self.title("网易易盾")
        # 设置窗口大小、居中
        width = int(400 * 1.5)
        height = int(300 * 1.5)
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

    # ... rest of the code ...

    def tk_lable_tips(self):
        lable = Label(self, text="移动滑块，与缺口对齐")
        lable.place(x=int(40 * 1.5), y=int(250 * 1.5), width=int(200 * 1.5), height=int(30 * 1.5))
        return lable

    def tk_button_sub_verify(self):
        btn = Button(self, text="提交验证")
        btn.place(x=int(290 * 1.5), y=int(250 * 1.5), width=int(70 * 1.5), height=int(30 * 1.5))
        return btn

    def tk_button_refresh(self):
        btn = Button(self, text="刷新")
        btn.place(x=int(205 * 1.5), y=int(250 * 1.5), width=int(70 * 1.5), height=int(30 * 1.5))
        return btn

    # ... rest of the code ...

    def __tk_scale_lm35sfc1(self, parent):
        scale = Scale(parent, orient=HORIZONTAL, from_=0, to=100, command=lambda x: self.move(x))
        scale.place(x=int(40 * 1.5), y=int(210 * 1.5), width=int(315 * 1.5), height=int(30 * 1.5))
        return scale

    def move(self, x):
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_file)
        if float(x) * 3 * 1.5 > 370:
            self.canvas.create_image(370, 1, anchor='nw', image=self.im_slide)
        else:
            self.canvas.create_image(float(x) * 3 * 1.5, 1, anchor='nw', image=self.im_slide)

    def tk_canve(self):
        canvas = Canvas(self, bg='blue', height=int(100 * 1.5), width=int(400 * 1.5))
        canvas.place(x=int(40 * 1.5), y=int(20 * 1.5), width=int(300 * 1.5), height=int(170 * 1.5))
        return canvas


class Win_verify(WinGUI_verify):
    def __init__(self, captchar_data, conf, ctx):
        self.check_res = None
        self.move_rate = 0
        self.success = False
        self.captchar_data = captchar_data
        self.conf = conf
        self.ctx = ctx
        super().__init__()
        self.loadImg()
        self.__event_bind()

    def __event_bind(self):
        # self.tk_scale_lm35sfc1.bind('<Button-1>', self.move(self.tk_scale_lm35sfc1.get()))
        self.tk_button_sub_verify.bind('<Button-1>', self.submit)
        # self.tk_scale_lm35sfc1.bind('<ButtonRelease-1>', self.submit(self.tk_scale_lm35sfc1.get()))
        self.tk_button_refresh.bind('<Button-1>', self.refress)

        # self.ima.place(x=40, y=20, width=300, height=170)

    def wait_distory(self):
        time.sleep(1)
        try:
            self.destroy()
        except:
            pass

    def submit(self, evt):
        self.move_rate = self.tk_scale_lm35sfc1.get()
        self.tk_lable_tips["text"] = "验证中..."
        data = ctx.call("get_data", self.captchar_data["token"], self.move_rate)
        cb = ctx.call("n2")
        res = capt_char.check_captchar(data)
        res_json = json.loads(res)
        self.check_res = res_json
        result = res_json["data"]["result"]
        capt_char.result = result
        if result:
            print("\033[1;32mTrue\033[0m")
        else:

            print("\033[1;31mFalse")

            print("data:\t", data)
            print("res:\t", res, "\033[0m")
        # 展示结果
        if result:
            self.success = True
            self.tk_lable_tips["foreground"] = "green"
            # with open("token.txt", "a") as f:
            #     f.write(self.captchar_data["token"] + "\n")
            # login
            self.tk_lable_tips["text"] = "验证结果：" + str(result)
            validate = res_json["data"]["validate"]
            thread = threading.Thread(target=self.wait_distory)
            thread.setDaemon(True)
            thread.start()



        else:
            self.tk_lable_tips["foreground"] = "red"

            self.tk_lable_tips["text"] = "验证结果：" + str(result)
            thread = threading.Thread(target=self.refress_th)
            thread.setDaemon(True)
            thread.start()

    def refress_th(self):
        time.sleep(1)
        try:
            if self.winfo_exists():
                self.refress(None)
        except:
            return

    def refress(self, evt):
        if self.winfo_exists():
            if capt_char.result is not None:
                capt_char.__init__()
                self.captchar_data = capt_char.captchar_data
                # 滑块归位
                self.tk_scale_lm35sfc1.set(0)
                # 提示文字
                self.tk_lable_tips["foreground"] = "black"
                self.tk_lable_tips["text"] = "移动滑块，与缺口对齐"

                self.loadImg()

    def loadImg(self):
        background_image = self.captchar_data['bigImage']

        imgdata = base64.b64decode(background_image)
        im = PILImage.open(io.BytesIO(imgdata))
        width_big, height_big = im.size
        im = im.resize((int(300 * 1.5), int(170 * 1.5)), PILImage.LANCZOS)
        im = ImageTk.PhotoImage(im)

        imgdata_slide = base64.b64decode(self.captchar_data['smallImage'])
        im_slide = PILImage.open(io.BytesIO(imgdata_slide))
        width_slide, height_slide = im_slide.size
        im_slide = im_slide.resize(
            (int((300 / width_big * width_slide) * 1.5), int((170 / height_big * height_slide) * 1.5)),
            PILImage.LANCZOS)
        im_slide = ImageTk.PhotoImage(im_slide)
        image_file = im
        # 0,0 -> 锚定的点, anchor='nw' -> 左上角锚定
        image = self.canvas.create_image(0, 0, anchor='nw', image=image_file)
        self.canvas.create_image(0, 1, anchor='nw', image=im_slide)

        self.image_file = image_file
        self.im_slide = im_slide


class captChar():
    def __init__(self):
        self.id = "75f9f716460a422f89a628f50fd8cc2b"
        self.referer = "https://passport.zhihuishu.com/login"
        self.fp = ctx.call("fp")
        self.cb = ctx.call("n2")
        self.conf = json.loads(self.get_config())
        self.captchar_conf = json.loads(self.get_captchar())
        self.captchar_data = self.format_captchar_data()
        self.result = None
        # print("captchar_data", self.captchar_data)

        # print("conf", self.conf)
        # print("captchar_conf", self.captchar_conf)
        # print("captchar_data", self.captchar_data)

    def get_config(self):
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
        return re.findall("\((.*)\)", response.text)[0]

    def get_captchar(self):
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

        response = requests.get(url, headers=headers, params=params, verify=False)

        # print(response.text)
        # print(response)
        return re.findall("\((.*)\)", response.text)[0]

        # 生成签名

    def check_captchar(self, data):
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
        response = requests.get(url, headers=headers, params=params, verify=False)
        return re.findall("\((.*)\)", response.text)[0]

    def format_captchar_data(self):
        bg = requests.get(self.captchar_conf["data"]["bg"][0], verify=False)
        bg = str(base64.b64encode(bg.content)).replace("b'", "").replace("'", "")
        front = requests.get(self.captchar_conf["data"]["front"][0], verify=False)
        front = str(base64.b64encode(front.content)).replace("b'", "").replace("'", "")

        token = self.captchar_conf["data"]["token"]

        charchar_data = {
            "smallImage": front,
            "bigImage": bg,
            "token": token
        }
        return charchar_data


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_frame_user = self.__tk_frame(self)
        self.tk_frame_mode = self.__tk_frame_mode(self)
        self.tk_frame_prossbar = self.__tk_frame_prossbar(self)
        self.tk_lable_title = self.__tk_lable_title(self)
        self.tk_table_tabal = self.__tk_table_tabal(self)
        self.tk_label_lqwiv6c4 = self.__tk_label_lqwiv6c4(self.tk_frame_user)
        self.tk_label_lqwivlzb = self.__tk_label_lqwivlzb(self.tk_frame_user)
        self.tk_label_list_title = self.__tk_label_list_title(self)
        self.tk_button_select_all = self.__tk_button_select_all(self)
        self.tk_label_lqwiydbk = self.__tk_label_lqwiydbk(self)
        self.tk_input_speed = self.__tk_input_speed(self)
        self.tk_text_log = self.__tk_text_lqwj10d9(self)
        self.tk_label_lqwj1vq1 = self.__tk_label_lqwj1vq1(self)
        self.tk_progressbar_prograssbar = self.__tk_progressbar_progressbar(self)
        self.tk_button_start = self.__tk_button_start(self)
        self.tk_playing_class_name = self.__tk_playing_class_name(self)
        self.tk_progressbar_prograssbar_little = self.__tk_progressbar_progressbar_little(self)

    def __win(self):
        self.title("智慧树")
        # 设置窗口大小、居中
        width = 1052
        height = 926
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.configure(bg="#faf7c0")

        self.resizable(width=False, height=False)
        # base64编码的图标
        base64_icon = "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"
        # 用base64解码
        icon = base64.b64decode(base64_icon)
        self.iconphoto(True, PhotoImage(data=icon))

    def __tk_frame(self, parent):
        frame = Frame(parent, borderwidth=1, relief='ridge')
        frame['style'] = 'TFrame'
        frame.place(x=57, y=25, width=400, height=52)
        return frame

    def __tk_frame_mode(self, parent):
        frame = Frame(parent, borderwidth=1, relief='ridge')
        frame['style'] = 'TFrame'
        frame.place(x=57, y=765, width=670, height=65)
        return frame

    def __tk_lable_title(self, parent):
        label = Label(parent, text="请点击选择要刷的课程，已完成的会自动跳过", style="info.TLabel", borderwidth=0.5,
                      relief='ridge', anchor="center")
        label.place(x=500, y=25, width=512, height=52)
        return label

    def __tk_frame_prossbar(self, parent):
        frame = Frame(parent, borderwidth=1, relief='ridge')
        frame['style'] = 'TFrame'
        frame.place(x=57, y=845, width=955, height=57)
        return frame

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_table_tabal(self, parent):
        # 表头字段 表头宽度
        columns = {"编号": 60, "name": 480, "状态": 60, "选中": 60, "id": 0}
        tk_table = Treeview(parent, show="headings", columns=list(columns), )
        for text, width in columns.items():  # 批量设置列属性
            tk_table.heading(text, text=text, anchor='center')
            tk_table.column(text, anchor='center', width=width, stretch=False)  # stretch 不自动拉伸

        tk_table.place(x=61, y=147, width=667, height=598)
        return tk_table

    def __tk_label_lqwiv6c4(self, parent):
        label = Label(parent, text="登录账号：", style="success.TLabel", width=18)
        # label.place(x=60, y=18, width=150, height=36)
        label.pack(side=LEFT)
        return label

    def __tk_label_lqwivlzb(self, parent):
        label = Label(parent, text="username", style="success.TLabel")
        # label.place(x=210, y=18, width=140, height=36)
        label.pack(side=LEFT)
        return label

    def __tk_label_list_title(self, parent):
        label = Label(parent, text="课程列表：", )
        label.place(x=60, y=105, width=664, height=30)
        return label

    def __tk_button_select_all(self, parent):
        btn = Button(parent, text="全选", takefocus=False, )
        btn.place(x=613, y=776, width=99, height=40)
        return btn

    def __tk_label_lqwiydbk(self, parent):
        label = Label(parent, text="倍速：", anchor="center", )
        label.place(x=68, y=776, width=69, height=42)
        return label

    def __tk_input_speed(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=171, y=778, width=174, height=41)
        ipt.insert(0, "1.0")
        return ipt

    def __tk_text_lqwj10d9(self, parent):
        text = Text(parent)
        text.place(x=770, y=146, width=247, height=599)
        return text

    def __tk_label_lqwj1vq1(self, parent):
        label = Label(parent, text="日志：")
        label.place(x=770, y=105, width=249, height=31)
        return label

    def __tk_progressbar_progressbar_little(self, parent):
        progressbar = Progressbar(parent, orient=HORIZONTAL, style="success-striped")
        progressbar.place(x=387, y=783, width=180, height=32)
        return progressbar

    def __tk_progressbar_progressbar(self, parent):
        progressbar = Progressbar(parent, orient=HORIZONTAL, style="success-striped")
        progressbar.place(x=286, y=858, width=709, height=32)
        return progressbar

    def __tk_playing_class_name(self, parent):
        labal = Label(parent, text="视频名称：", )
        labal.place(x=61, y=858, width=200, height=31)
        return labal

    def __tk_button_start(self, parent):
        btn = Button(parent, text="启动！", takefocus=False, style="success.TButton")
        btn.place(x=770, y=768, width=243, height=60)
        return btn


class Win(WinGUI):
    def __init__(self):

        super().__init__()
        self.list_data = None
        # self.insert_data(0)
        self.__event_bind()
        self.playing = False

    def insert_data(self):

        i = 1
        for id, data in self.list_data.items():
            self.tk_table_tabal.insert("", "end",
                                       values=(
                                           i, data["name"], "已完成" if data["watchState"] == 1 else "未完成", 0, id))
            i += 1

    def show(self, event):
        selected_items = self.tk_table_tabal.selection()  # 获取选中的项
        for item in selected_items:  # 遍历选中的项
            # print("你点击了行：", item)
            if self.tk_table_tabal.set(item, "选中") == 1:  # 如果已经选中
                self.tk_table_tabal.set(item, "选中", 0)  # 将选中行的"状态"列的值设置为0
                # self.tk_table_tabal.selection_remove(item)  # 取消选择
            else:
                self.tk_table_tabal.set(item, "选中", 1)  # 将选中行的"状态"列的值设置为1

    def updata_prossbar_th(self):
        while self.playing:
            time.sleep(0.3)
            self.tk_progressbar_prograssbar["value"] = zhihuishu.playtime
            self.tk_progressbar_prograssbar["maximum"] = zhihuishu.totaltime

            self.tk_progressbar_prograssbar_little["value"] = zhihuishu.wait_time
            self.tk_progressbar_prograssbar_little["maximum"] = 10

    def play_class_th(self, select_idlist):
        for classid in select_idlist:
            # 改变正在播放的课程名称
            # print(zhihuishu.video_data)
            # print(zhihuishu.video_data[str(classid)])
            name = zhihuishu.video_data[str(classid)]["name"]
            self.tk_playing_class_name["text"] = name

            zhihuishu.play_class(classid)

        self.playing = False

    def play(self, evt):
        if self.playing:
            print("正在播放中")
            return
        else:
            self.playing = True

        # 获取倍速
        self.playspeed = self.tk_input_speed.get()
        # 如果倍速不是数字
        try:
            self.playspeed = float(self.playspeed)
        except:
            print("倍速不是数字,已设置为1.0")
            self.playspeed = 1.0

        zhihuishu.playspeed = self.playspeed

        # 获取选中的值为1的行,遍历所有行

        select_idlist = []
        for item in self.tk_table_tabal.get_children():
            if self.tk_table_tabal.set(item, "选中") == 1:
                # print(self.tk_table_tabal.item(item, "values")[0])
                # print(self.tk_table_tabal.item(item, "values")[4])
                select_idlist.append(self.tk_table_tabal.item(item, "values")[4])

        th = threading.Thread(target=self.play_class_th, args=(select_idlist,))
        th.daemon = True
        th.start()

        th_progressbar = threading.Thread(target=self.updata_prossbar_th, args=())
        th_progressbar.daemon = True
        th_progressbar.start()

    def select_all(self, evt):
        # 如果已经全选
        if self.tk_button_select_all["text"] == "全选":
            for item in self.tk_table_tabal.get_children():
                self.tk_table_tabal.set(item, "选中", 1)
                self.tk_button_select_all["text"] = "取消全选"
        else:
            for item in self.tk_table_tabal.get_children():
                self.tk_table_tabal.set(item, "选中", 0)
                self.tk_button_select_all["text"] = "全选"

    def __event_bind(self):
        self.tk_button_start.bind('<Button-1>', self.play)
        self.tk_button_select_all.bind('<Button-1>', self.select_all)
        self.tk_table_tabal.bind("<<TreeviewSelect>>", self.show)
        pass


class WinGUI_select_class(Toplevel):
    def __init__(self, class_data):
        super().__init__()
        self.__win()
        self.class_data = class_data
        self.tk_table_lqwnmy9p = self.__tk_table_lqwnmy9p(self)
        self.tk_button_lqwnwe2c = self.__tk_button_lqwnwe2c(self)
        self.select_class = None

        self.insert_data()
        self.tk_button_lqwnwe2c.bind('<Button-1>', self.select)

    def __win(self):
        self.title("选择课程")
        # 设置窗口大小、居中
        width = 606
        height = 363
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_table_lqwnmy9p(self, parent):
        # 表头字段 表头宽度
        columns = {"ID": 108, "name": 430, }
        tk_table = Treeview(parent, show="headings", columns=list(columns), )
        for text, width in columns.items():  # 批量设置列属性
            tk_table.heading(text, text=text, anchor='center')
            tk_table.column(text, anchor='center', width=width)  # stretch 不自动拉伸

        tk_table.place(x=33, y=29, width=544, height=257)
        return tk_table

    def __tk_button_lqwnwe2c(self, parent):
        btn = Button(parent, text="确认", takefocus=False, )
        btn.place(x=34, y=308, width=542, height=35)
        return btn

    def insert_data(self):
        for classes in self.class_data:
            print(classes)
            self.tk_table_lqwnmy9p.insert("", "end",
                                          values=(classes["id"], classes["name"], classes["recruitAndCourseId"]))

    def select(self, evt):
        selected_items = self.tk_table_lqwnmy9p.selection()
        if len(selected_items) == 0 or len(selected_items) > 1:
            print("未选择课程或选择了多个课程")
            return
        self.select_class = self.tk_table_lqwnmy9p.item(selected_items[0], "values")[2]


class WinGUI_login(Toplevel):
    def __init__(self):
        super().__init__()
        self.success = False
        self.username = None
        self.password = None
        self.login = None

        self.__win()
        self.tk_label_lqx57o8d = self.__tk_label_lqx57o8d(self)
        self.tk_label_lqx57ukl = self.__tk_label_lqx57ukl(self)
        self.tk_input_username = self.__tk_input_username(self)
        self.tk_input_password = self.__tk_input_password(self)
        self.tk_button_login = self.__tk_button_login(self)
        self.tk_button_cancel = self.__tk_button_cancel(self)
        self.load_data()

    def __win(self):
        self.title("智慧树登录")
        # 设置窗口大小、居中
        width = 621
        height = 321
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def tips(self, text):
        # 红色字体
        label = Label(self, text=text, anchor="center", foreground="red")
        label.place(x=95, y=199, width=442, height=30)
        return label

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_label_lqx57o8d(self, parent):
        label = Label(parent, text="账号：", anchor="center", )
        label.place(x=90, y=54, width=120, height=42)
        return label

    def __tk_label_lqx57ukl(self, parent):
        label = Label(parent, text="密码：", anchor="center", )
        label.place(x=90, y=148, width=115, height=41)
        return label

    def __tk_input_username(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=240, y=53, width=301, height=45)
        return ipt

    def __tk_input_password(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=237, y=147, width=298, height=44)
        return ipt

    def __tk_button_login(self, parent):
        btn = Button(parent, text="登录", takefocus=False, command=self.submit, style="success.TButton")
        btn.place(x=428, y=234, width=111, height=49)
        return btn

    def __tk_button_cancel(self, parent):
        btn = Button(parent, text="取消", takefocus=False, style="danger.TButton", command=self.destroy)
        btn.place(x=267, y=234, width=111, height=49)
        return btn

    def submit(self):
        self.get_data()

        self.success = True

    def get_data(self):
        self.username = self.tk_input_username.get()
        self.password = self.tk_input_password.get()

    def load_data(self):
        try:
            with open("cookies.json", "r") as f:
                cookie_data = json.loads(f.read())
                username = cookie_data['username']
                password = cookie_data['password']
                self.tk_input_username.insert("end", username)
                self.tk_input_password.insert("end", password)

        except:

            print("获取用户名和密码失败")


if __name__ == "__main__":
    # all.js
    js_hex = "66756E6374696F6E20512872297B66756E6374696F6E20682872297B72657475726E20723C2D3132383F68283235362B72293A3132373C723F6828722D323536293A727D66756E6374696F6E206F28722C6E297B72657475726E206828722B6E297D66756E6374696F6E20752872297B666F7228766172206E3D5B5D2C743D302C653D302C613D28723D22222B72292E6C656E6774682F323B743C613B742B2B297B76617220753D7061727365496E7428722E63686172417428652B2B292C3136293C3C342C663D7061727365496E7428722E63686172417428652B2B292C3136293B6E5B745D3D6828752B66297D72657475726E206E7D66756E6374696F6E206E2872297B666F7228766172206E3D5B5D2C743D302C653D28723D656E636F6465555249436F6D706F6E656E74287229292E6C656E6774683B743C653B742B2B292225223D3D3D722E6368617241742874293F742B323C6526266E2E7075736828752822222B722E636861724174282B2B74292B722E636861724174282B2B7429295B305D293A6E2E70757368286828722E63686172436F6465417428742929293B72657475726E206E7D66756E6374696F6E20742872297B766172206E3D5B5D3B69662821722E6C656E6774682972657475726E206E62283634293B69662836343C3D722E6C656E6774682972657475726E20722E73706C69636528302C3634293B666F722876617220743D303B743C36343B742B2B296E5B745D3D725B7425722E6C656E6774685D3B72657475726E206E7D66756E6374696F6E206928722C6E297B72657475726E206828682872295E68286E29297D66756E6374696F6E206528722C6E297B666F722876617220743D303C617267756D656E74732E6C656E6774682626766F69642030213D3D723F723A5B5D2C653D313C617267756D656E74732E6C656E6774682626766F69642030213D3D6E3F6E3A5B5D2C613D5B5D2C753D652E6C656E6774682C663D302C683D742E6C656E6774683B663C683B662B2B29615B665D3D6928745B665D2C655B6625755D293B72657475726E20617D66756E6374696F6E20662872297B766172206E3D5B5D3B72657475726E206E5B305D3D6828723E3E3E323426323535292C6E5B315D3D6828723E3E3E313626323535292C6E5B325D3D6828723E3E3E3826323535292C6E5B335D3D68283235352672292C6E7D66756E6374696F6E20632872297B72657475726E20723D22222B722C6828287061727365496E7428722E6368617241742830292C3136293C3C34292B7061727365496E7428722E6368617241742831292C313629297D66756E6374696F6E206C2872297B72657475726E20722E6D61702866756E6374696F6E2872297B72657475726E22222B286E3D5B2230222C2231222C2232222C2233222C2234222C2235222C2236222C2237222C2238222C2239222C2261222C2262222C2263222C2264222C2265222C2266225D295B28723D72293E3E3E342631355D2B6E5B313526725D3B766172206E7D292E6A6F696E282222297D66756E6374696F6E206728722C6E2C742C652C61297B666F722876617220753D302C663D722E6C656E6774683B753C613B752B2B296E2B753C66262628745B652B755D3D725B6E2B755D293B72657475726E20747D66756E6374696F6E207628722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286928725B655D2C6E29293B72657475726E20747D66756E6374696F6E207028722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286928725B655D2C6E2B2B29293B72657475726E20747D66756E6374696F6E207328722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286928725B655D2C6E2D2D29293B72657475726E20747D66756E6374696F6E206428722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286F28725B655D2C6E29293B72657475726E20747D66756E6374696F6E206228722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286F28725B655D2C6E2B2B29293B72657475726E20747D66756E6374696F6E207928722C6E297B69662821722E6C656E6774682972657475726E5B5D3B6E3D68286E293B666F722876617220743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29742E70757368286F28725B655D2C6E2D2D29293B72657475726E20747D66756E6374696F6E204D2872297B72657475726E20303C3D28313C617267756D656E74732E6C656E6774682626766F69642030213D3D617267756D656E74735B315D3F617267756D656E74735B315D3A30292B3235363F723A5B5D7D66756E6374696F6E20612872297B69662841727261792E69734172726179287229297B666F7228766172206E3D302C743D417272617928722E6C656E677468293B6E3C722E6C656E6774683B6E2B2B29745B6E5D3D725B6E5D3B72657475726E20747D72657475726E2041727261792E66726F6D2872297D66756E6374696F6E204128722C6E2C74297B76617220653D766F696420302C613D766F696420302C753D766F696420302C663D5B5D3B73776974636828722E6C656E677468297B6361736520313A653D725B305D2C613D753D302C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C742C74293B627265616B3B6361736520323A653D725B305D2C613D725B315D2C753D302C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C6E5B28613C3C32263630292B28753E3E3E362633295D2C74293B627265616B3B6361736520333A653D725B305D2C613D725B315D2C753D725B325D2C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C6E5B28613C3C32263630292B28753E3E3E362633295D2C6E5B363326755D293B627265616B3B64656661756C743A72657475726E22227D72657475726E20662E6A6F696E282222297D66756E6374696F6E206D2872297B69662821722E6C656E6774682972657475726E5B5D3B666F7228766172206E2C743D5B5D2C653D302C613D722E6C656E6774683B653C613B652B2B29745B655D3D286E3D725B655D2C752822613762653366333933336661386335666366383663346236393038623536396261316532366331613664376366626636306165346230306530373461313934646163346237336537663839383534313135396133396430383138336237366565646565336564333431653636383564323335373434303135383339346231666630336139303034636262623563613764636237663431343839613136653033646363396337316562336339373936363835623164303162346435363139336136653166316132343730343435633139316165343963356438323736356463383263333530663236333338376132346135303266636266343432653264646461616430653933366439656132326238393237353330376234323531386662633361363236626138303664346563643664373235663530636338633732666566613435353163636436666339623262376162393534663831356337323634633665353166346561663939383835613739383932623162363061306233353236653537626135643137386433373039353838343765623966643238663963653062633032336634313438613261646665363332313236373639303537303433643362643865646130646637383732363239663338303965663035333130653833313133323136616665323032633436306663323365373839663737643161646462356522295B31362A286E3E3E3E34263135292B283135266E295D293B72657475726E20747D666F722876617220492C6A2C6B2C772C783D66756E6374696F6E28722C6E297B69662841727261792E697341727261792872292972657475726E20723B69662853796D626F6C2E6974657261746F7220696E204F626A6563742872292972657475726E2066756E6374696F6E28722C6E297B76617220743D5B5D2C653D21302C613D21312C753D766F696420303B7472797B666F722876617220662C683D725B53796D626F6C2E6974657261746F725D28293B2128653D28663D682E6E6578742829292E646F6E6529262628742E7075736828662E76616C7565292C216E7C7C742E6C656E677468213D3D6E293B653D2130293B7D63617463682872297B613D21302C753D727D66696E616C6C797B7472797B21652626682E72657475726E2626682E72657475726E28297D66696E616C6C797B69662861297468726F7720757D7D72657475726E20747D28722C6E293B7468726F77206E657720547970654572726F722822496E76616C696420617474656D707420746F206465737472756374757265206E6F6E2D6974657261626C6520696E7374616E636522297D2C513D6E2872292C723D782828493D6E2822666436613433616532356637343339386236316330336338336265333734343922292C6A3D66756E6374696F6E28297B666F722876617220723D5B5D2C6E3D303B6E3C343B6E2B2B29725B6E5D3D68284D6174682E666C6F6F72283235362A4D6174682E72616E646F6D282929293B72657475726E20727D28292C493D6528493D742849292C74286A29292C5B493D742849292C6A5D292C32292C533D725B305D2C783D725B315D2C723D6E2866756E6374696F6E2872297B666F7228766172206E3D5B302C313939363935393839342C333939333931393738382C323536373532343739342C3132343633343133372C313838363035373631352C333931353632313638352C323635373339323033352C3234393236383237342C323034343530383332342C333737323131353233302C323534373137373836342C3136323934313939352C323132353536313032312C333838373630373034372C323432383434343034392C3439383533363534382C313738393932373636362C343038393031363634382C323232373036313231342C3435303534383836312C313834333235383630332C343130373538303735332C323231313637373633392C3332353838333939302C313638343737373135322C343235313132323034322C323332313932363633362C3333353633333438372C313636313336353436352C343139353330323735352C323336363131353331372C3939373037333039362C313238313935333838362C333537393835353333322C323732343638383234322C313030363838383134352C313235383630373638372C333532343130313632392C323736383934323434332C3930313039373732322C313131393030303638342C333638363531373230362C323839383036353732382C3835333034343435312C313137323236363130312C333730353031353735392C323838323631363636352C3635313736373938302C313337333530333534362C333336393535343330342C333231383130343539382C3536353530373235332C313435343632313733312C333438353131313730352C333039393433363330332C3637313236363937342C313539343139383032342C333332323733303933302C323937303334373831322C3739353833353532372C313438333233303232352C333234343336373237352C333036303134393536352C313939343134363139322C33313135383533342C323536333930373737322C343032333731373933302C313930373435393436352C3131323633373231352C323638303135333235332C333930343432373035392C323031333737363239302C3235313732323033362C323531373231353337342C333737353833303034302C323133373635363736332C3134313337363831332C323433393237373731392C333836353237313239372C313830323139353434342C3437363836343836362C323233383030313336382C343036363530383837382C313831323337303932352C3435333039323733312C323138313632353032352C343131313435313232332C313730363038383930322C3331343034323730342C323334343533323230322C343234303031373533322C313635383635383237312C3336363631393937372C323336323637303332332C343232343939343430352C313330333533353936302C3938343936313438362C323734373030373039322C333536393033373533382C313235363137303831372C313033373630343331312C323736353231303733332C333535343037393939352C313133313031343530362C3837393637393939362C323930393234333436322C333636333737313835362C313134313132343436372C3835353834323237372C323835323830313633312C333730383634383634392C313334323533333934382C3635343435393330362C333138383339363034382C333337333031353137342C313436363437393930392C3534343137393633352C333131303532333931332C333436323532323031352C313539313637313035342C3730323133383737362C323936363436303435302C333335323739393431322C313530343931383830372C3738333535313837332C333038323634303434332C333233333434323938392C333938383239323338342C323539363235343634362C36323331373036382C313935373831303834322C333933393834353934352C323634373831363131312C38313437303939372C313934333830333532332C333831343931383933302C323438393539363830342C3232353237343433302C323035333739303337362C333832363137353735352C323436363930363031332C3136373831363734332C323039373635313337372C343032373535323538302C323236353439303338362C3530333434343037322C313736323035303831342C343135303431373234352C323135343132393335352C3432363532323232352C313835323530373837392C343237353331333532362C323331323331373932302C3238323735333632362C313734323535353835322C343138393730383134332C323339343837373934352C3339373931373736332C313632323138333633372C333630343339303838382C323731343836363535382C3935333732393733322C313334303037363632362C333531383731393938352C323739373336303939392C313036383832383338312C313231393633383835392C333632343734313835302C323933363637353134382C3930363138353436322C313039303831323531322C333734373637323030332C323832353337393636392C3832393332393133352C313138313333353136312C333431323137373830342C333136303833343834322C3632383038353430382C313338323630353336362C333432333336393130392C333133383037383436372C3537303536323233332C313432363430303831352C333331373331363534322C323939383733333630382C3733333233393935342C313535353236313935362C333236383933353539312C333035303336303632352C3735323435393430332C313534313332303232312C323630373037313932302C333936353937333033302C313936393932323937322C34303733353439382C323631373833373232352C333934333537373135312C313931333038373837372C38333930383337312C323531323334313633342C333830333734303639322C323037353230383632322C3231333236313131322C323436333237323630332C333835353939303238352C323039343835343037312C3139383935383838312C323236323032393031322C343035373236303631302C313735393335393939322C3533343431343139302C323137363731383534312C343133393332393131352C313837333833363030312C3431343636343536372C323238323234383933342C343237393230303336382C313731313638343535342C3238353238313131362C323430353830313732372C343136373231363734352C313633343436373739352C3337363232393730312C323638353036373839362C333630383030373430362C313330383931383631322C3935363534333933382C323830383535353130352C333439353935383236332C313233313633363330312C313034373432373033352C323933323935393831382C333635343730333833362C313038383335393237302C39333639313865332C323834373731343839392C333733363833373832392C313230323930303836332C3831373233333839372C333138333334323130382C333430313233373133302C313430343237373535322C3631353831383135302C333133343230373439332C333435333432313230332C313432333835373434392C3630313435303433312C333030393833373631342C333239343731303435362C313536373130333734362C3731313932383732342C333032303636383437312C333237323338303036352C313531303333343233352C3735353136373131375D2C743D343239343936373239352C653D302C613D722E6C656E6774683B653C613B652B2B29743D743E3E3E385E6E5B3235352628745E725B655D295D3B72657475726E206C286628343239343936373239355E7429297D285129292C433D66756E6374696F6E2872297B696628722E6C656E677468253634213D302972657475726E5B5D3B666F7228766172206E3D5B5D2C743D722E6C656E6774682F36342C653D302C613D303B653C743B652B2B297B6E5B655D3D5B5D3B666F722876617220753D303B753C36343B752B2B296E5B655D5B755D3D725B612B2B5D7D72657475726E206E7D2866756E6374696F6E2872297B69662821722E6C656E6774682972657475726E206E62283634293B766172206E3D5B5D2C743D722E6C656E6774682C653D742536343C3D36303F36342D742536342D343A3132382D742536342D343B6728722C302C6E2C302C74293B666F722876617220613D303B613C653B612B2B296E5B742B615D3D303B72657475726E206728662874292C302C6E2C742B652C34292C6E7D285B5D2E636F6E63617428612851292C612872292929292C4F3D5B5D2E636F6E6361742861287829292C5F3D532C523D302C553D432E6C656E6774683B523C553B522B2B297B76617220713D652866756E6374696F6E2872297B6E6A3D2230333736303664613032393630353563223B666F7228766172206E3D5B4D2C762C642C702C622C732C795D2C743D6E6A2C653D302C613D742E6C656E6774683B653C613B297B76617220753D742E737562737472696E6728652C652B34292C663D6328752E737562737472696E6728302C3229292C753D6328752E737562737472696E6728322C3429293B723D6E5B665D28722C75292C652B3D347D72657475726E20727D28435B525D292C53293B67285F3D6D286D28713D652866756E6374696F6E28722C6E297B666F722876617220743D303C617267756D656E74732E6C656E6774682626766F69642030213D3D723F723A5B5D2C653D313C617267756D656E74732E6C656E6774682626766F69642030213D3D6E3F6E3A5B5D2C613D5B5D2C753D652E6C656E6774682C663D302C683D742E6C656E6774683B663C683B662B2B29615B665D3D6F28745B665D2C655B6625755D293B72657475726E20617D28712C5F292C5F2929292C302C4F2C36342A522B342C3634297D72657475726E20773D6E756C6C213D773F773A2237222C66756E6374696F6E28722C6E2C74297B69662821727C7C303D3D3D722E6C656E6774682972657475726E22223B7472797B666F722876617220653D302C613D5B5D3B653C722E6C656E6774683B297B6966282128652B333C3D722E6C656E67746829297B76617220753D722E736C6963652865293B612E70757368284128752C6E2C7429293B627265616B7D753D722E736C69636528652C652B33293B612E70757368284128752C6E2C7429292C652B3D337D72657475726E20612E6A6F696E282222297D63617463682872297B72657475726E22227D7D284F2C286E756C6C213D6B3F6B3A224D422E436648557A45654A707375476B674E77687169536149344664394C366A594B5A41786E312F566D6C30633572625852502B3874443351544F327657796F22292E73706C6974282222292C77297D66756E6374696F6E206E3228297B72657475726E206E6B3D7B757569643A66756E6374696F6E28722C6E297B76617220743D22303132333435363738394142434445464748494A4B4C4D4E4F505152535455565758595A6162636465666768696A6B6C6D6E6F707172737475767778797A222E73706C6974282222292C653D5B5D2C613D766F696420303B6966286E3D6E7C7C742E6C656E6774682C7229666F7228613D303B613C723B612B2B29655B615D3D745B307C4D6174682E72616E646F6D28292A6E5D3B656C73657B76617220753B666F7228655B385D3D655B31335D3D655B31385D3D655B32335D3D222D222C655B31345D3D2234222C613D303B613C33363B612B2B29655B615D7C7C28753D307C31362A4D6174682E72616E646F6D28292C655B615D3D745B31393D3D3D613F3326757C383A755D297D72657475726E20652E6A6F696E282222297D7D2C51286E6B2E7575696428333229297D66756E6374696F6E204928722C6E297B66756E6374696F6E20742872297B666F7228766172206E3D5B5D2C743D302C653D28723D656E636F6465555249436F6D706F6E656E74287229292E6C656E6774683B743C653B742B2B292225223D3D3D722E6368617241742874293F742B323C6526266E2E707573682866756E6374696F6E2872297B666F7228766172206E3D5B5D2C743D302C653D302C613D28723D22222B72292E6C656E6774682F323B743C613B742B2B297B76617220753D7061727365496E7428722E63686172417428652B2B292C3136293C3C342C663D7061727365496E7428722E63686172417428652B2B292C3136293B6E5B745D3D6328752B66297D72657475726E206E7D2822222B722E636861724174282B2B74292B722E636861724174282B2B7429295B305D293A6E2E70757368286328722E63686172436F6465417428742929293B72657475726E206E7D66756E6374696F6E206628722C6E2C74297B76617220653D766F696420302C613D766F696420302C753D766F696420302C663D5B5D3B73776974636828722E6C656E677468297B6361736520313A653D725B305D2C613D753D302C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C742C74293B627265616B3B6361736520323A653D725B305D2C613D725B315D2C753D302C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C6E5B28613C3C32263630292B28753E3E3E362633295D2C74293B627265616B3B6361736520333A653D725B305D2C613D725B315D2C753D725B325D2C662E70757368286E5B653E3E3E322636335D2C6E5B28653C3C34263438292B28613E3E3E34263135295D2C6E5B28613C3C32263630292B28753E3E3E362633295D2C6E5B363326755D293B627265616B3B64656661756C743A72657475726E22227D72657475726E20662E6A6F696E282222297D66756E6374696F6E20632872297B72657475726E20723C2D3132383F63283235362B72293A3132373C723F6328722D323536293A727D76617220653D74286E292C613D742872293B72657475726E2066756E6374696F6E28722C6E2C74297B69662821727C7C303D3D3D722E6C656E6774682972657475726E22223B7472797B666F722876617220653D302C613D5B5D3B653C722E6C656E6774683B297B6966282128652B333C3D722E6C656E67746829297B76617220753D722E736C6963652865293B612E70757368286628752C6E2C7429293B627265616B7D753D722E736C69636528652C652B33293B612E70757368286628752C6E2C7429292C652B3D337D72657475726E20612E6A6F696E282222297D63617463682872297B72657475726E22227D7D2866756E6374696F6E28722C6E297B666F722876617220742C652C613D303C617267756D656E74732E6C656E6774682626766F69642030213D3D723F723A5B5D2C753D313C617267756D656E74732E6C656E6774682626766F69642030213D3D6E3F6E3A5B5D2C663D5B5D2C683D752E6C656E6774682C6F3D302C693D612E6C656E6774683B6F3C693B6F2B2B29665B6F5D3D28743D615B6F5D2C653D755B6F25685D2C6328632874295E6328652929293B72657475726E20667D28652C61292C5B2269222C222F222C2278222C2231222C2258222C2267222C2255222C2230222C227A222C2237222C226B222C2238222C224E222C222B222C226C222C2243222C2270222C224F222C226E222C2250222C2272222C2276222C2236222C225C5C222C2271222C2275222C2232222C2247222C226A222C2239222C2248222C2252222C2263222C2277222C2254222C2259222C225A222C2234222C2262222C2266222C2253222C224A222C2242222C2268222C2261222C2257222C2273222C2274222C2241222C2265222C226F222C224D222C2249222C2245222C2251222C2235222C226D222C2244222C2264222C2256222C2246222C224C222C224B222C2279225D2C223322297D66756E6374696F6E204228297B76617220723D66756E6374696F6E28722C6E297B69662841727261792E697341727261792872292972657475726E20723B69662853796D626F6C2E6974657261746F7220696E204F626A6563742872292972657475726E206B28722C6E293B7468726F77206E657720547970654572726F722822496E76616C696420617474656D707420746F206465737472756374757265206E6F6E2D6974657261626C6520696E7374616E636522297D3B66756E6374696F6E206F28722C6E297B666F722876617220743D5B5D2C653D5B5D2C613D303B613C722E6C656E6774682D313B612B2B29742E7075736828725B612B315D2D725B615D292C652E70757368286E5B612B315D2D6E5B615D293B666F722876617220753D5B5D2C663D303B663C652E6C656E6774683B662B2B29752E7075736828655B665D2F745B665D293B72657475726E20757D66756E6374696F6E206E2872297B666F7228766172206E3D5B5D2C743D722E6C656E6774682C653D303B653C743B652B2B292D313D3D3D6E2E696E6465784F6628725B655D2926266E2E7075736828725B655D293B72657475726E206E7D66756E6374696F6E20742872297B72657475726E207061727365466C6F617428722E746F4669786564283429297D66756E6374696F6E206528722C6E297B76617220743D722E736F72742866756E6374696F6E28722C6E297B72657475726E20722D6E7D293B6966286E3C3D302972657475726E20745B305D3B6966283130303C3D6E2972657475726E20745B742E6C656E6774682D315D3B76617220653D4D6174682E666C6F6F722828742E6C656E6774682D31292A286E2F31303029292C723D745B655D3B72657475726E20722B28745B652B315D2D72292A2828742E6C656E6774682D31292A286E2F313030292D65297D66756E6374696F6E20612872297B69662841727261792E69734172726179287229297B666F7228766172206E3D302C743D417272617928722E6C656E677468293B6E3C722E6C656E6774683B6E2B2B29745B6E5D3D725B6E5D3B72657475726E20747D72657475726E2041727261792E66726F6D2872297D66756E6374696F6E20752872297B666F7228766172206E3D692872292C743D722E6C656E6774682C653D5B5D2C613D303B613C743B612B2B297B76617220753D725B615D2D6E3B652E70757368284D6174682E706F7728752C3229297D666F722876617220663D302C683D303B683C652E6C656E6774683B682B2B29655B685D262628662B3D655B685D293B72657475726E204D6174682E7371727428662F74297D66756E6374696F6E20692872297B666F7228766172206E3D302C743D722E6C656E6774682C653D303B653C743B652B2B296E2B3D725B655D3B72657475726E206E2F747D76617220663D303C617267756D656E74732E6C656E6774682626766F69642030213D3D617267756D656E74735B305D3F617267756D656E74735B305D3A5B5D3B6966282141727261792E697341727261792866297C7C662E6C656E6774683C3D322972657475726E5B5D3B76617220682C632C6C2C672C763D722866756E6374696F6E2872297B766172206E3D303C617267756D656E74732E6C656E6774682626766F69642030213D3D723F723A5B5D2C743D5B5D2C653D5B5D2C613D5B5D3B6966282141727261792E69734172726179286E297C7C6E2E6C656E6774683C3D322972657475726E5B742C652C615D3B666F722876617220753D303B753C6E2E6C656E6774683B752B2B297B76617220663D6E5B755D3B742E7075736828665B305D292C652E7075736828665B315D292C612E7075736828665B325D297D72657475726E5B742C652C615D7D2866292C33292C703D765B305D2C733D765B315D2C643D765B325D2C623D722866756E6374696F6E28722C6E2C74297B666F722876617220653D6F28742C72292C613D6F28742C6E292C753D5B5D2C663D303B663C722E6C656E6774683B662B2B297B76617220683D4D6174682E73717274284D6174682E706F7728725B665D2C32292B4D6174682E706F77286E5B665D2C3229293B752E707573682868297D72657475726E5B652C612C6F28742C75295D7D28702C732C64292C33292C793D625B305D2C4D3D625B315D2C663D625B325D2C763D722828683D792C633D4D2C6C3D662C5B6F28673D28673D64292E736C69636528302C2D31292C68292C6F28672C63292C6F28672C6C295D292C33292C623D765B305D2C723D765B315D2C763D765B325D3B72657475726E5B6E2870292E6C656E6774682C6E2873292E6C656E6774682C742869287329292C742875287329292C702E6C656E6774682C74284D6174682E6D696E2E6170706C79284D6174682C6128792929292C74284D6174682E6D61782E6170706C79284D6174682C6128792929292C742869287929292C742875287929292C6E2879292E6C656E6774682C74286528792C323529292C74286528792C373529292C74284D6174682E6D696E2E6170706C79284D6174682C61284D2929292C74284D6174682E6D61782E6170706C79284D6174682C61284D2929292C742869284D29292C742875284D29292C6E284D292E6C656E6774682C742865284D2C323529292C742865284D2C373529292C74284D6174682E6D696E2E6170706C79284D6174682C6128662929292C74284D6174682E6D61782E6170706C79284D6174682C6128662929292C742869286629292C742875286629292C6E2866292E6C656E6774682C74286528662C323529292C74286528662C373529292C74284D6174682E6D696E2E6170706C79284D6174682C6128622929292C74284D6174682E6D61782E6170706C79284D6174682C6128622929292C742869286229292C742875286229292C6E2862292E6C656E6774682C74286528622C323529292C74286528622C373529292C74284D6174682E6D696E2E6170706C79284D6174682C6128722929292C74284D6174682E6D61782E6170706C79284D6174682C6128722929292C742869287229292C742875287229292C6E2872292E6C656E6774682C74286528722C323529292C74286528722C373529292C74284D6174682E6D696E2E6170706C79284D6174682C6128762929292C74284D6174682E6D61782E6170706C79284D6174682C6128762929292C742869287629292C742875287629292C6E2876292E6C656E6774682C74286528762C323529292C74286528762C373529295D7D66756E6374696F6E206765745F6461746128722C6E297B666F722876617220743D5B5B342C302C3136325D2C5B362C302C3137305D2C5B382C302C3137395D2C5B31302C302C3138385D2C5B31342C302C3139365D2C5B31372C312C3230355D2C5B32302C312C3231345D2C5B32342C312C3232335D2C5B32362C312C3233325D2C5B32372C312C3234305D2C5B32392C322C3234395D2C5B33302C322C3235385D2C5B33322C322C3236365D2C5B33322C322C3237355D2C5B33332C322C3239335D2C5B33342C322C3239345D2C5B33352C322C3330325D2C5B33362C322C3331305D2C5B33372C322C3331395D2C5B33392C322C3332385D2C5B34302C322C3333365D2C5B34322C322C3334355D2C5B34332C322C3336335D2C5B34352C322C3336345D2C5B34372C322C3338305D2C5B35302C342C3338395D2C5B35322C342C3430375D2C5B35342C342C3431365D2C5B35352C342C3432345D2C5B35382C342C3433335D2C5B35392C342C3434315D2C5B36302C342C3435305D2C5B36332C342C3435395D2C5B36352C342C3436385D2C5B36362C342C3437365D2C5B36382C342C3438355D2C5B37322C342C3439345D2C5B37362C342C3530335D2C5B38302C342C3531315D2C5B38322C342C3532305D2C5B38342C342C3532395D2C5B38362C342C3533385D2C5B38382C342C3534365D2C5B39322C342C3535355D2C5B39362C342C3536345D2C5B3130322C342C3537335D2C5B3130372C342C3538325D2C5B3131322C342C3539305D2C5B3131382C342C3539395D2C5B3132332C342C3630385D2C5B3132392C342C3631365D2C5B3133342C342C3632355D2C5B3134302C342C3634335D2C5B3134352C342C3634345D2C5B3135302C342C3635325D2C5B3135362C342C3636305D2C5B3136312C342C3636395D2C5B3136372C342C3637385D2C5B3137312C342C3638365D2C5B3137352C342C3639355D2C5B3137392C342C3731335D2C5B3138332C342C3731345D2C5B3138362C342C3732325D2C5B3138392C342C3733305D2C5B3139332C342C3733395D2C5B3139372C342C3734385D2C5B3230322C342C3735375D2C5B3230362C342C3736355D2C5B3231302C342C3738345D2C5B3231342C342C3738355D2C5B3231372C342C3739315D2C5B3232312C342C3830305D2C5B3232342C342C3830395D2C5B3232362C342C3831375D2C5B3232362C342C3832375D2C5B3232382C342C3833355D2C5B3232382C342C3835335D2C5B3233302C342C3835345D2C5B3233312C342C3836315D2C5B3233322C342C3837395D2C5B3233322C342C3838305D2C5B3233342C342C3838385D2C5B3233342C342C3839375D2C5B3233362C342C3930355D2C5B3233362C342C3932345D2C5B3233372C342C3933315D2C5B3233392C342C3934305D2C5B3234302C342C3934395D2C5B3234312C342C3935385D2C5B3234322C342C3936375D2C5B3234342C342C3937355D2C5B3234362C342C3938345D2C5B3234362C342C3939335D2C5B3234372C342C313030325D2C5B3234382C342C313031305D2C5B3235302C342C313031395D2C5B3235322C342C313032385D2C5B3235322C342C313033365D2C5B3235342C342C313034355D2C5B3235342C342C313036335D2C5B3235352C342C313037315D2C5B3235362C342C313038305D2C5B3235362C342C313039385D2C5B3235372C342C313130365D2C5B3235382C342C313131355D2C5B3235382C342C313133335D2C5B3236302C352C313135305D2C5B3236302C352C313135395D2C5B3236312C352C313138355D2C5B3236322C362C313230335D2C5B3236332C362C313231315D2C5B3236342C362C313232305D2C5B3236342C362C313232395D2C5B3236352C362C313233385D2C5B3236362C362C313235365D2C5B3236362C362C313236345D2C5B3236372C362C313238325D2C5B3236382C362C313239315D2C5B3236382C362C313239395D2C5B3236392C362C313330385D2C5B3237302C362C313331365D2C5B3237302C362C313334335D2C5B3237302C362C313336305D2C5B3237312C362C313338375D2C5B3237322C362C313339365D2C5B3237322C362C313431335D2C5B3237332C362C313431345D2C5B3237342C362C313432315D2C5B3237342C372C313433305D2C5B3237342C372C313433395D2C5B3237352C372C313435375D2C5B3237362C372C313436365D2C5B3237362C372C313438335D2C5B3237372C372C313438345D2C5B3237382C372C313530305D2C5B3237382C372C313530395D2C5B3237392C372C313531385D2C5B3238302C382C313532365D2C5B3238302C382C313533355D5D2C653D5B5D2C613D303B613C742E6C656E6774683B612B2B297B76617220753D5B302C302C305D3B755B305D3D7061727365496E7428745B615D5B305D2A6E2F313030292C755B315D3D745B615D5B315D2C755B325D3D745B615D5B325D2C652E707573682875297D666F722876617220663D5B5D2C613D303B613C35303B612B2B29662E70757368284928722C655B615D5B305D2B222C222B655B615D5B315D2B222C222B655B615D5B325D29293B72657475726E7B643A5128662E6A6F696E28223A2229292C6D3A22222C703A51284928722C7061727365496E74283165332A6E292F3165332B222229292C663A51284928722C422865292E6A6F696E28222C222929292C6578743A51284928722C22312C222B652E6C656E67746829297D7D66756E6374696F6E206C6F67696E5F656E637279707428722C6E2C742C65297B76617220612C752C662C653D28613D652C753D22434E3331222C6E533D66756E6374696F6E2872297B766172206E3D7B225C5C223A222D222C222F223A225F222C222B223A222A227D3B72657475726E20722E7265706C616365282F5B5C5C5C2F2B5D2F672C66756E6374696F6E2872297B72657475726E206E5B725D7D297D2C613D6E53285128742B223A3A222B6129292C28753F752B225F222B613A61292B225F765F695F3122293B72657475726E20663D4A534F4E2E737472696E67696679287B6163636F756E743A722C70617373776F72643A6E2C76616C69646174653A657D292C62746F6128656E636F6465555249286629297D66756e6374696f6e20667028297b646f63756d656e743d7b636f6f6b69653a22227d3b76617220673d5b33362c32382c35312c392c32332c372c302c322c313432333835373434392c2d322c332c2d332c333433323931383335332c313535353236313935362c342c323834373731343839392c2d342c352c2d352c323731343836363535382c313238313935333838362c362c2d362c3139383935383838312c313134313132343436372c323937303334373831322c2d372c372c333131303532333931332c382c2d382c323432383434343034392c2d392c392c31302c2d31302c2d31312c31312c323536333930373737322c2d31322c31322c31332c323238323234383933342c2d31332c323135343132393335352c2d31342c31342c31352c2d31352c31362c2d31362c31372c2d31372c2d31382c31382c31392c2d31392c32302c2d32302c32312c2d32312c2d32322c32322c2d32332c32332c32342c2d32342c32352c2d32352c2d32362c32362c32372c2d32372c32382c2d32382c32392c2d32392c33302c2d33302c33312c2d33312c33332c2d33332c2d33322c33322c2d33342c2d33352c33342c33352c33372c2d33372c33362c2d33362c33382c33392c2d33392c2d33382c34302c34312c2d34312c2d34302c34322c2d34332c2d34322c34332c34352c2d34352c2d34342c34342c34372c2d34362c2d34372c34362c34382c2d34392c2d34382c34392c2d35302c35312c2d35312c35302c3537303536323233332c35332c2d35322c35322c2d35332c2d35342c2d35352c35352c35342c3530333434343037322c35372c2d35362c2d35372c35362c35392c35382c2d35392c2d35382c36302c36312c2d36312c2d36302c36322c36332c2d36332c2d36322c2d36342c3731313932383732342c2d36362c36372c2d36352c36352c2d36372c36362c36342c2d37312c2d36392c36392c36382c37302c2d36382c2d37302c37312c2d37322c333638363531373230362c2d37342c2d37332c37332c37352c37342c2d37352c37322c2d37392c37362c37392c37382c2d37382c2d37362c37372c2d37372c333535343037393939352c2d38312c38312c2d38322c2d38332c38302c2d38302c38322c38332c2d38342c38342c38352c2d38362c2d38372c38362c2d38352c38372c39302c2d38382c2d38392c2d39302c38382c38392c39312c2d39312c39342c39322c39352c2d39342c39332c2d39332c2d39352c2d39322c2d39382c39372c39382c2d39372c2d39392c39362c39392c2d39362c2d3130302c333237323338303036352c3130322c2d3130322c2d3130312c2d3130332c3130332c3130302c3130312c2d3130372c2d3130342c3130352c3130342c3130362c2d3130362c2d3130352c3130372c3130392c2d3130392c2d3130382c2d3131312c3131302c2d3131302c3131312c3130382c3235313732323033362c3131352c2d3131352c3131322c2d3131342c2d3131322c3131332c3131342c2d3131332c2d3131372c3131392c2d3131362c2d3131392c3131372c2d3131382c3131382c3131362c3132332c2d3132302c3132322c2d3132312c3132302c2d3132322c2d3132332c3132312c3132352c3132372c333431323137373830342c2d3132372c3132362c2d3132362c3132342c2d3132352c2d3132342c2d3132382c3132382c2d3132392c313834333235383630332c333830333734303639322c3938343936313438362c333933393834353934352c343139353330323735352c343036363530383837382c3235352c313730363038383930322c3235362c313936393932323937322c323039373635313337372c3337363232393730312c3835333034343435312c3735323435393430332c3432363532323232352c3165332c333737323131353233302c3631353831383135302c333930343432373035392c343136373231363734352c343032373535323538302c333635343730333833362c313838363035373631352c3837393637393939362c333531383731393938352c333234343336373237352c323031333737363239302c333337333031353137342c313735393335393939322c3238353238313131362c313632323138333633372c313030363838383134352c313233313633363330312c3165342c38333930383337312c313039303831323531322c323436333237323630332c313337333530333534362c323539363235343634362c323332313932363633362c313530343931383830372c323138313632353032352c323838323631363636352c323734373030373039322c333030393833373631342c333133383037383436372c3339373931373736332c38313437303939372c3832393332393133352c323635373339323033352c3935363534333933382c323531373231353337342c323236323032393031322c34303733353439382c323339343837373934352c333236363438393930392c3730323133383737362c323830383535353130352c323933363637353134382c313235383630373638372c313133313031343530362c333231383130343539382c333038323634303434332c313430343237373535322c3536353530373235332c3533343431343139302c313534313332303232312c313931333038373837372c323035333739303337362c313738393932373636362c333936353937333033302c333832363137353735352c343130373538303735332c343234303031373533322c313635383635383237312c333537393835353333322c333730383634383634392c333435333432313230332c333331373331363534322c313837333833363030312c313734323535353835322c3436313834353930372c333630383030373430362c313939363935393839342c333734373637323030332c333438353131313730352c323133373635363736332c333335323739393431322c3231333236313131322c333939333931393738382c312e30312c333836353237313239372c343133393332393131352c343237353331333532362c3238323735333632362c313036383832383338312c323736383934323434332c323930393234333436322c39333639313865332c333138333334323130382c32373439322c3134313337363831332c333035303336303632352c3635343435393330362c323631373833373232352c313435343632313733312c323438393539363830342c323232373036313231342c313539313637313035342c323336323637303332332c343239343936373239352c313330383931383631322c323234363832323530372c3739353833353532372c313138313333353136312c3431343636343536372c343237393230303336382c313636313336353436352c313033373630343331312c343135303431373234352c333838373630373034372c313830323139353434342c343032333731373933302c323037353230383632322c313934333830333532332c3930313039373732322c3632383038353430382c3735353136373131372c333332323733303933302c333436323532323031352c333733363833373832392c333630343339303838382c323336363131353331372c2e342c323233383030313336382c323531323334313633342c323634373831363131312c2d2e322c3331343034323730342c313531303333343233352c3965352c35383936342c313338323630353336362c33313135383533342c3435303534383836312c333032303636383437312c313131393030303638342c333136303833343834322c323839383036353732382c313235363137303831372c323736353231303733332c333036303134393536352c333138383339363034382c323933323935393831382c3132343633343133372c323739373336303939392c3336363631393937372c36323331373036382c2d2e32362c313230323930303836332c3439383533363534382c313334303037363632362c323430353830313732372c323236353439303338362c313539343139383032342c313436363437393930392c323534373137373836342c3234393236383237342c323638303135333235332c323132353536313032312c333239343731303435362c3835353834323237372c333432333336393130392c2e3733323133343434342c333730353031353735392c333536393033373533382c313939343134363139322c313731313638343535342c313835323530373837392c3939373037333039362c3733333233393935342c343235313132323034322c3630313435303433312c343131313435313232332c3136373831363734332c333835353939303238352c333938383239323338342c333336393535343330342c333233333434323938392c333439353935383236332c333632343734313835302c36353533352c3435333039323733312c2d2e392c323039343835343037312c313935373831303834322c3332353838333939302c343035373236303631302c313638343737373135322c343138393730383134332c333931353632313638352c3136323934313939352c313831323337303932352c333737353833303034302c3738333535313837332c333133343230373439332c313137323236363130312c323939383733333630382c323732343638383234322c313330333533353936302c323835323830313633312c3131323633373231352c313536373130333734362c3635313736373938302c313432363430303831352c3930363138353436322c323231313637373633392c313034373432373033352c323334343533323230322c323630373037313932302c323436363930363031332c3232353237343433302c3534343137393633352c323137363731383534312c323331323331373932302c313438333233303232352c313334323533333934382c323536373532343739342c323433393237373731392c313038383335393237302c3637313236363937342c313231393633383835392c383465342c3935333732393733322c333039393433363330332c323936363436303435302c3831373233333839372c323638353036373839362c323832353337393636392c343038393031363634382c343232343939343430352c333934333537373135312c333831343931383933302c3437363836343836362c313633343436373739352c3333353633333438372c313736323035303831342c312c323034343530383332342c2d312c333430313233373133302c333236383933353539312c333532343130313632392c333636333737313835362c313930373435393436355d2c643d5b22222c224772617954657874222c22706172656e74222c22e5b9bce59c86222c22706c7567696e73222c2241646f626545784d616e446574656374222c2230303130222c22476f6f676c6520456172746820506c7567696e222c22566565746c6520545620436f7265222c2230303037222c2230303034222c2230303032222c2230303033222c2230303030222c2230303031222c22556e69747920506c61796572222c22536b7970652057656220506c7567696e222c225765624b69742d696e74656772696572746520504446222c226764786964707968786445222c2242656c6c204d54222c2230303038222c22676574537570706f72746564457874656e73696f6e73222c2230303039222c2253616665536561726368222c2273657454696d65222c22617070656e644368696c64222c2722272c2224222c22556e6976657273222c2225222c2226222c2227222c2231313130222c2267657420706c7567696e20737472696e6720657863657074696f6e222c22546872656544536861646f77222c222b222c222c222c222d222c2241726162222c22e88bb9e69e9ce4b8bde7bb86e5ae8b222c222e222c2246555a455368617265222c222f222c2230222c2231222c2232222c2233222c2234222c22e4bbbfe5ae8b5f474232333132222c2235222c2236222c22496e61637469766543617074696f6e54657874222c2237222c225745425a454e2042726f7773657220457874656e73696f6e222c2238222c2239222c22446976582042726f7773657220506c75672d496e222c223a222c223b222c2255706c6179205043222c223d222c2263616e76617320657863657074696f6e222c2241222c2242222c2243222c2244222c2245222c22e5beaee8bdafe99b85e9bb91222c2246222c2248617272696e67746f6e222c2247222c2248222c2249222c224a222c22476e6f6d65205368656c6c20496e746567726174696f6e222c224b222c224c222c224d222c224e222c224f222c2250222c2251222c2252222c2253222c224e69616761726120536f6c6964222c2254222c22536566436c69656e7420506c7567696e222c2255222c2256222c2231313131222c2257222c2258222c2259222c225a222c22476f756479204f6c64205374796c65222c225c5c222c22526f626c6f78204c61756e6368657220506c7567696e222c224d6963726f736f6674204f66666963652032303133222c2251514d75736963222c2261222c224575726f7374696c65222c2262222c22726d6f63782e5265616c506c6179657220473220436f6e74726f6c2e31222c2263222c22536372697074696e672e44696374696f6e617279222c2264222c22e4bbbfe5ae8b222c2265222c2266222c2267222c2268222c224d612d436f6e6669672e636f6d20706c7567696e222c2269222c2231303130222c2243617375616c222c226a222c226b222c226c222c226d222c226e222c226f222c2270222c2231303038222c22646f4e6f74547261636b222c2271222c226374222c22e4b8bde5ae8b2050726f222c2272222c2273657454696d656f7574222c224769736861222c2267657454696d657a6f6e654f6666736574222c2273222c2231303035222c2231303034222c2274222c2231303033222c2275222c2276222c2231303031222c2277222c2278222c2264726177417272617973222c2279222c227a222c227b222c227d222c227e222c22666f6e74222c2231303039222c227375666669786573222c223d6e756c6c3b20706174683d2f3b20657870697265733d222c225368656c6c2e554948656c706572222c22746f4461746155524c222c2257696e646f7754657874222c226c616e6775616765222c22e4b8bde9bb912050726f222c22646f222c22486967686c6967687454657874222c22646976222c224d656e7554657874222c22414f4c204d6564696120506c61796261636b20506c7567696e222c22436974726978206f6e6c696e6520706c75672d696e222c226563222c2244657364656d6f6e61222c22496e616374697665426f72646572222c225265616c506c61796572222c222c2027636f6465273a222c2248454c4c4f222c226e70546f6e676275416464696e222c22656d222c22637265617465456c656d656e74222c227068616e746f6d222c224d5320504d696e63686f222c22e6a5b7e4bd93222c226576616c222c226578222c224469765820564f442048656c70657220506c75672d696e222c22e696b0e7bb86e6988ee4bd93222c22517569636b54696d65436865636b4f626a6563742e517569636b54696d65436865636b2e31222c22466c794f724469652047616d657320506c7567696e222c22617474616368536861646572222c22506c61794f6e20506c75672d696e222c2267657454696d65222c22312e3031222c2242726f6164776179222c226670222c22416c61776172204e50415049207574696c73222c22466f727465222c2268617368436f6465222c22e696b9e6ada3e5a79ae4bd93222c2245534e20536f6e617220415049222c224850446574656374222c22426974646566656e64657220517569636b5363616e222c2249452054616220706c7567696e222c22427574746f6e46616365222c22272c222c22637075436c617373222c226d657373616765222c2243656e7475727920476f74686963222c224f6e6c696e652053746f7261676520706c75672d696e222c22536166657220557064617465222c224d73786d6c322e444f4d446f63756d656e74222c22456e67726176657273204d54222c2253696c7665726c6967687420506c75672d496e222c22476f6f676c6520476561727320302e352e33332e30222c224369747269782049434120436c69656e74222c22616c7068616265746963222c22636f6e74657874222c2256446f776e6c6f61646572222c22e58d8ee69687e6a5b7e4bd93222c2261747472566572746578222c22e5ae8be4bd93222c22636f6f6b6965222c22253232222c22253236222c2243656e74617572222c223467616d65222c22526f636b77656c6c222c224c6f674d65496e20506c7567696e20312e302e302e393631222c224f63746f73686170652053747265616d696e67205365727669636573222c22746f474d54537472696e67222c2274683d2f222c2253756d617472615044462042726f7773657220506c7567696e222c225044462e5064664374726c222c2266696c6c5374796c65222c22666f6e7453697a65222c2241646f6265204d696e6720537464222c226a65222c22546f72636848656c706572222c224672616e6b6c696e20476f74686963204865617679222c22e58d8ee69687e4bbbfe5ae8b222c224861726d6f6e7920506c75672d496e222c2247696769222c2276312e31222c224b696e6f204d54222c2253696d486569222c22416c6953534f4c6f67696e20706c7567696e222c225265616c506c617965722e5265616c506c6179657228746d29204163746976655820436f6e74726f6c202833322d62697429222c2259616e6465782050444620566965776572222c2243697472697820526563656976657220506c75672d696e222c22746f70222c226d6169222c224163726f5044462e504446222c2263616e7661732061706920657863657074696f6e222c22496e61637469766543617074696f6e222c224d656e75222c22707265636973696f6e206d656469756d7020666c6f61743b2076617279696e6720766563322076617279696e546578436f6f7264696e6174653b20766f6964206d61696e2829207b202020676c5f46726167436f6c6f72203d20766563342876617279696e546578436f6f7264696e6174652c20302c2031293b207d222c225151323031332046697265666f7820506c7567696e222c22476f6f676c6520557064617465222c22e58d8ee69687e5bda9e4ba91222c22654d75736963506c7567696e20444c4d36222c2257656220436f6d706f6e656e7473222c22426162796c6f6e20546f6f6c426172222c22436f6f776f6e20557064617465222c22496e666f54657874222c22726d6f63782e5265616c506c6179657220473220436f6e74726f6c222c22694d65736820706c7567696e222c225265616c446f776e6c6f6164657220506c7567696e222c2253796d616e74656320504b4920436c69656e74222c225f7068616e746f6d222c2247444c204f626a6563742057656220506c75672d696e2031362e3030222c22776562676c222c22e58d8ee69687e5ae8be4bd93222c2273637265656e222c22626f6479222c22545249414e474c455f5354524950222c22546c77674d6f6e6f222c226e3d222c224c6f674d65496e20506c7567696e20312e302e302e393335222c22273a27222c2266756e6374696f6e222c22636f6e746578742e68617368436f6465222c224172636869434144222c225645525445585f534841444552222c225562756e7475222c2246616365626f6f6b20506c7567696e222c2241637469766543617074696f6e222c22e7bb86e6988ee4bd93222c224d616c67756e20476f74686963222c224e65777320476f74686963204d54222c2243617074696f6e54657874222c22615a625930635864573165566632556733546834536952356a516b36506c4f376d4e6e384d6f4c39704b714a724973487447754676457744784379427a41222c2244656a615675204c47432053616e73204d6f6e6f222c22436f70706572706c61746520476f74686963204c69676874222c225365676f65205072696e74222c225361776173646565222c2242617568617573203933222c224368616c6b647573746572222c224162616469204d5420436f6e64656e736564204c69676874222c224c756369646120427269676874222c2257696465204c6174696e222c22666f6e7420646574656374206572726f72222c224b6f7a756b6120476f74686963205072364e222c2248746d6c35206c6f636174696f6e2070726f7669646572222c224469765820506c75732057656220506c61796572222c22566c6164696d697220536372697074222c2246696c6520446f776e6c6f6164657220506c75672d696e222c226f62222c2241646f64622e53747265616d222c224d656e6c6f222c2263616c6c5068616e746f6d222c22576f6c6672616d204d617468656d6174696361222c22436174616c696e6147726f757020557064617465222c224572617320426f6c6420495443222c22446576616c5652584374726c2e446576616c5652584374726c2e31222c22e58d8ee69687e7bb86e9bb91222c226164644265686176696f72222c227061222c2242697473747265616d2056657261205365726966222c222866756e6374696f6e28297b72657475726e203132333b7d2928293b222c227069222c2254656e63656e742046544e20706c75672d696e222c2272656d6f76654368696c64222c22466f6c7820332042726f7773657220506c7567696e222c2275736550726f6772616d222c22686f73746e616d65222c227068616e746f6d2e696e6a6563744a73222c2253686f636b77617665466c6173682e53686f636b77617665466c617368222c22686569676874222c2272676261283130322c203230342c20302c20302e3729222c224164626c6f636b506c7567696e222c224261636b67726f756e64222c224167436f6e74726f6c2e4167436f6e74726f6c222c2250686f746f43656e746572506c7567696e312e312e322e32222c2247756e6753656f222c22733d222c226465636f6465555249222c22e696b9e6ada3e88892e4bd93222c22e58d8ee69687e696b0e9ad8f222c22313233222c22776562676c20657863657074696f6e222c227265222c22574d506c617965722e4f4358222c2237327078222c22417070576f726b7370616365222c22486967686c69676874222c22646f63756d656e74222c2259616e646578204d6564696120506c7567696e222c2245534e204c61756e6368204d6f7a696c6c6120506c7567696e222c22373070782027417269616c27222c22696e6a6563744a73222c224c6f6d61222c22426974436f6d65744167656e74222c2243616c69627269222c22426f6f6b6d616e204f6c64205374796c65222c2273657373696f6e53746f72616765222c2255746f706961222c22636f6d70696c65536861646572222c22657363617065222c225363726f6c6c626172222c2257696e646f77222c22e99ab6e4b9a6222c224b6173706572736b792050617373776f7264204d616e61676572222c224d696e674c69552d45787442222c226765742073797374656d20636f6c6f727320657863657074696f6e222c22536b7970652e446574656374696f6e222c2246696c654c616220706c7567696e222c226e7041504920506c7567696e222c226e6f745f65786973745f686f7374222c223264222c22416374697665584f626a656374222c22446f74756d222c225044462d584368616e676520566965776572222c226f6666736574486569676874222c22504d696e674c6955222c22636f6c6f724465707468222c224e6f6b696120537569746520456e61626c657220506c7567696e222c225265616c566964656f2e5265616c566964656f28746d29204163746976655820436f6e74726f6c202833322d62697429222c224d61676e65746f222c2241646f626545784d616e4343446574656374222c2247616272696f6c61222c22506c617962696c6c222c226e6176696761746f72222c2252616368616e61222c2254772043656e204d5420436f6e64656e73656420457874726120426f6c64222c2251514d696e69444c20506c7567696e222c2223663630222c2266696c6c52656374222c2244656661756c742042726f777365722048656c706572222c223d6e756c6c3b20706174683d2f3b20646f6d61696e3d222c224672656e636820536372697074204d54222c22e6a087e6a5b7e4bd93222c22656e636f6465555249222c22556d70757368222c22696370222c22e58d8ee69687e790a5e78f80222c2263726561746550726f6772616d222c226d6f6e6f7370616365222c22427574746f6e536861646f77222c22426f646f6e69204d54222c225354415449435f44524157222c22e9bb91e4bd93222c22646f776e6c6f616455706461746572222c22416c696564697420506c75672d496e222c2250444620696e7465677261646f20646f205765624b6974222c22756e69666f726d4f6666736574222c22656e636f6465555249436f6d706f6e656e74222c22506963617361222c2241646f62652046616e67736f6e6720537464222c2262696e64427566666572222c22415647205369746553616665747920706c7567696e222c224f7262697420446f776e6c6f61646572222c22636f6c6f72222c2268696464656e222c226c6f63616c53746f72616765222c22476f6f676c652054616c6b204566666563747320506c7567696e222c226465736372697074696f6e222c22696e64657865644442222c224c756369646120466178222c22416d617a6f6e4d5033446f776e6c6f61646572506c7567696e222c22637265617465427566666572222c2243617374656c6c6172222c226c696e6b50726f6772616d222c2243616c69666f726e69616e204642222c22546872656544486967686c69676874222c22637265617465536861646572222c2247756c696d222c224e79784c61756e63686572222c22596f755475626520506c75672d696e222c22e6a5b7e4bd935f474232333132222c22535743746c2e535743746c222c22476f6f676c6520456172746820506c75672d696e222c225151446f776e6c6f616420506c7567696e222c224e6f72746f6e204964656e746974792053616665222c227061727365496e74222c2253696d706c652050617373222c22436f6c6f6e6e61204d54222c227a616b6f222c22676574556e69666f726d4c6f636174696f6e222c22736861646572536f75726365222c22446f776e6c6f616465727320706c7567696e222c226c6f636174696f6e222c224865726f657320262047656e6572616c73206c697665222c2277696e646f77222c2253686f776361726420476f74686963222c22e5beaee8bdafe6ada3e9bb91e4bd93222c22e58d8ee69687e8a18ce6a5b7222c2247696e676572222c22526f636b4d656c7420557064617465222c2257696e646f774672616d65222c22656e61626c655665727465784174747269624172726179222c224b616373744f6e65222c22617474726962757465207665633220617474725665727465783b2076617279696e6720766563322076617279696e546578436f6f7264696e6174653b20756e69666f726d207665633220756e69666f726d4f66667365743b20766f6964206d61696e2829207b20202076617279696e546578436f6f7264696e617465203d2061747472566572746578202b20756e69666f726d4f66667365743b202020676c5f506f736974696f6e203d207665633428617474725665727465782c20302c2031293b207d222c225065727065747561222c226f70656e4461746162617365222c2263616e766173222c226947657474657253637269707461626c65506c7567696e222c22496e666f726d616c20526f6d616e222c224e6974726f2050444620506c75672d496e222c224d73786d6c322e584d4c48545450222c22e58d8ee69687e9bb91e4bd93222c224e504c61737450617373222c2254687265654446616365222c227374796c65222c224c61737450617373222c223a3a222c227061727365466c6f6174222c22e58d8ee69687e99ab6e4b9a6222c223b20222c226765744174747269624c6f636174696f6e222c227b276e616d65273a222c224e79616c61222c226e6f745f65786973745f686f73746e616d65222c225c5c27222c22474641434520506c7567696e222c22756e646566696e6564222c22e696b0e5ae8be4bd93222c225c5c2e222c224d6174757261204d5420536372697074204361706974616c73222c22417269616c20426c61636b222c2246616e67536f6e67222c226d7743206e6b6261666a6f726420706873676c792065787674207a7169752c20e1bda02074706873742f3a2f756862677469632e6d6f2f6c65767661222c22427261676761646f63696f222c224861726d6f6e792046697265666f7820506c7567696e222c2250616c61636520536372697074204d54222c224e617469766520436c69656e74222c226f66667365745769647468225d3b77696e646f773d7b7d3b766172206f3d2266756e6374696f6e223d3d747970656f662053796d626f6c26262273796d626f6c223d3d747970656f662053796d626f6c2e6974657261746f723f66756e6374696f6e2865297b72657475726e20747970656f6620657d3a66756e6374696f6e2865297b72657475726e206526262266756e6374696f6e223d3d747970656f662053796d626f6c2626652e636f6e7374727563746f723d3d3d53796d626f6c262665213d3d53796d626f6c2e70726f746f747970653f2273796d626f6c223a747970656f6620657d3b66756e6374696f6e20652865297b6966286e756c6c3d3d652972657475726e206e756c6c3b666f7228766172206e3d5b5d2c723d675b365d2c743d652e6c656e6774683b723c743b722b2b297b76617220693d655b725d3b6e5b725d3d6e655b28693e3e3e675b31345d26675b34375d292a675b34395d2b286926675b34375d295d7d72657475726e206e7d66756e6374696f6e206e2865297b766172206e3d5b5d3b6966286e756c6c3d3d657c7c6e756c6c3d3d657c7c652e6c656e6774683d3d675b365d2972657475726e2069286e55293b696628652e6c656e6774683e3d6e55297b6e3d675b365d3b76617220723d5b5d3b6966286e756c6c213d652626652e6c656e677468213d675b365d297b696628652e6c656e6774683c6e55297468726f77204572726f7228645b3133355d293b666f722876617220743d675b365d3b743c6e553b742b2b29725b745d3d655b6e2b745d7d72657475726e20727d666f7228723d675b365d3b723c6e553b722b2b296e5b725d3d655b7225652e6c656e6774685d3b72657475726e206e7d66756e6374696f6e207228652c6e2c72297b76617220743d5b645b34355d2c645b34375d2c645b34335d2c645b39395d2c645b39325d2c645b37315d2c645b3131325d2c645b38315d2c645b3134305d2c645b37365d2c645b39355d2c645b39335d2c645b3133365d2c645b3130385d2c645b38385d2c645b3131375d2c645b3130395d2c645b35345d2c645b3133315d2c645b38305d2c645b37375d2c645b38325d2c645b35305d2c645b3130355d2c645b37305d2c645b3131365d2c645b39315d2c645b3133375d2c645b37395d2c645b34325d2c645b36345d2c645b3130315d2c645b3133395d2c645b35355d2c645b39305d2c645b36355d2c645b3131355d2c645b34345d2c645b36365d2c645b38355d2c645b3134325d2c645b37325d2c645b38335d2c645b3130335d2c645b3131385d2c645b3130375d2c645b3132305d2c645b37335d2c645b3134335d2c645b34365d2c645b35325d2c645b3132345d2c645b3133345d2c645b3131305d2c645b36335d2c645b3132375d2c645b38375d2c645b33355d2c645b37355d2c645b37385d2c645b36325d2c645b34395d2c645b3132315d2c645b3131395d5d2c693d645b36385d2c6f3d5b5d3b696628723d3d675b3533315d297b723d655b6e5d3b76617220613d675b365d3b6f2e7075736828745b723e3e3e675b375d26675b3134345d5d292c6f2e7075736828745b28723c3c675b31345d26675b3131335d292b28613e3e3e675b31345d26675b34375d295d292c6f2e707573682869292c6f2e707573682869297d656c736520696628723d3d675b375d29723d655b6e5d2c613d655b6e2b675b3533315d5d2c653d675b365d2c6f2e7075736828745b723e3e3e675b375d26675b3134345d5d292c6f2e7075736828745b28723c3c675b31345d26675b3131335d292b28613e3e3e675b31345d26675b34375d295d292c6f2e7075736828745b28613c3c675b375d26675b3133395d292b28653e3e3e675b32315d26675b31305d295d292c6f2e707573682869293b656c73657b69662872213d675b31305d297468726f77204572726f7228645b3131335d293b723d655b6e5d2c613d655b6e2b675b3533315d5d2c653d655b6e2b675b375d5d2c6f2e7075736828745b723e3e3e675b375d26675b3134345d5d292c6f2e7075736828745b28723c3c675b31345d26675b3131335d292b28613e3e3e675b31345d26675b34375d295d292c6f2e7075736828745b28613c3c675b375d26675b3133395d292b28653e3e3e675b32315d26675b31305d295d292c6f2e7075736828745b6526675b3134345d5d297d72657475726e206f2e6a6f696e28645b305d297d66756e6374696f6e20692865297b666f7228766172206e3d5b5d2c723d675b365d3b723c653b722b2b296e5b725d3d675b365d3b72657475726e206e7d66756e6374696f6e207428652c6e2c722c742c69297b6966286e756c6c3d3d657c7c652e6c656e6774683d3d675b365d2972657475726e20723b6966286e756c6c3d3d72297468726f77204572726f7228645b3133335d293b696628652e6c656e6774683c69297468726f77204572726f7228645b3133355d293b666f7228766172206f3d675b365d3b6f3c693b6f2b2b29725b742b6f5d3d655b6e2b6f5d3b72657475726e20727d66756e6374696f6e20612865297b766172206e3d5b5d3b72657475726e206e5b305d3d653e3e3e675b36355d26675b3239305d2c6e5b315d3d653e3e3e675b34395d26675b3239305d2c6e5b325d3d653e3e3e675b32395d26675b3239305d2c6e5b335d3d6526675b3239305d2c6e7d66756e6374696f6e206c2865297b6966286e756c6c3d3d657c7c6e756c6c3d3d652972657475726e20653b666f7228766172206e3d5b5d2c723d28653d656e636f6465555249436f6d706f6e656e74286529292e6c656e6774682c743d675b365d3b743c723b742b2b29696628652e6368617241742874293d3d645b32395d297b6966282128742b675b375d3c7229297468726f77204572726f7228645b3134385d293b6e2e707573682866756e6374696f6e2865297b6966286e756c6c3d3d657c7c652e6c656e6774683d3d675b365d2972657475726e5b5d3b666f7228766172206e3d5b5d2c723d28653d6e657720537472696e67286529292e6c656e6774682f675b375d2c743d675b365d2c693d675b365d3b693c723b692b2b297b766172206f3d7061727365496e7428652e63686172417428742b2b292c675b34395d293c3c675b31345d2c613d7061727365496e7428652e63686172417428742b2b292c675b34395d293b6e5b695d3d68286f2b61297d72657475726e206e7d28652e636861724174282b2b74292b645b305d2b652e636861724174282b2b7429295b305d297d656c7365206e2e7075736828652e63686172436f64654174287429293b72657475726e206e7d66756e6374696f6e207528652c6e297b6966286e756c6c3d3d657c7c6e756c6c3d3d6e7c7c652e6c656e677468213d6e2e6c656e6774682972657475726e20653b666f722876617220723d5b5d2c743d675b365d2c693d652e6c656e6774683b743c693b742b2b29725b745d3d6328655b745d2c6e5b745d293b72657475726e20727d66756e6374696f6e206328652c6e297b72657475726e20653d682865292c6e3d68286e292c6828655e6e297d66756e6374696f6e20682865297b696628653c675b3238315d2972657475726e206828675b3238325d2d28675b3238315d2d6529293b696628653e3d675b3238315d2626653c3d675b3237335d2972657475726e20653b696628653e675b3237335d2972657475726e206828675b3238335d2b652d675b3237335d293b7468726f77204572726f7228645b3133385d297d66756e6374696f6e20662865297b72657475726e206e756c6c3d3d657c7c6e756c6c3d3d657d66756e6374696f6e207028652c6e297b696628662865292972657475726e20645b305d3b666f722876617220723d675b365d3b723c652e6c656e6774683b722b2b297b76617220743d655b725d3b69662821662874292626742e683d3d6e2972657475726e20747d7d66756e6374696f6e20732865297b666f7228766172206e3d5b5d2c723d675b365d3b723c653b722b2b297b76617220743d36322a4d6174682e72616e646f6d28292c743d4d6174682e666c6f6f722874293b6e2e707573682822615a625930635864573165566632556733546834536952356a516b36506c4f376d4e6e384d6f4c39704b714a724973487447754676457744784379427a41222e636861724174287429297d72657475726e206e2e6a6f696e28645b305d297d6e6c3d5b302c313939363935393839342c333939333931393738382c323536373532343739342c3132343633343133372c313838363035373631352c333931353632313638352c323635373339323033352c3234393236383237342c323034343530383332342c333737323131353233302c323534373137373836342c3136323934313939352c323132353536313032312c333838373630373034372c323432383434343034392c3439383533363534382c313738393932373636362c343038393031363634382c323232373036313231342c3435303534383836312c313834333235383630332c343130373538303735332c323231313637373633392c3332353838333939302c313638343737373135322c343235313132323034322c323332313932363633362c3333353633333438372c313636313336353436352c343139353330323735352c323336363131353331372c3939373037333039362c313238313935333838362c333537393835353333322c323732343638383234322c313030363838383134352c313235383630373638372c333532343130313632392c323736383934323434332c3930313039373732322c313131393030303638342c333638363531373230362c323839383036353732382c3835333034343435312c313137323236363130312c333730353031353735392c323838323631363636352c3635313736373938302c313337333530333534362c333336393535343330342c333231383130343539382c3536353530373235332c313435343632313733312c333438353131313730352c333039393433363330332c3637313236363937342c313539343139383032342c333332323733303933302c323937303334373831322c3739353833353532372c313438333233303232352c333234343336373237352c333036303134393536352c313939343134363139322c33313135383533342c323536333930373737322c343032333731373933302c313930373435393436352c3131323633373231352c323638303135333235332c333930343432373035392c323031333737363239302c3235313732323033362c323531373231353337342c333737353833303034302c323133373635363736332c3134313337363831332c323433393237373731392c333836353237313239372c313830323139353434342c3437363836343836362c323233383030313336382c343036363530383837382c313831323337303932352c3435333039323733312c323138313632353032352c343131313435313232332c313730363038383930322c3331343034323730342c323334343533323230322c343234303031373533322c313635383635383237312c3336363631393937372c323336323637303332332c343232343939343430352c313330333533353936302c3938343936313438362c323734373030373039322c333536393033373533382c313235363137303831372c313033373630343331312c323736353231303733332c333535343037393939352c313133313031343530362c3837393637393939362c323930393234333436322c333636333737313835362c313134313132343436372c3835353834323237372c323835323830313633312c333730383634383634392c313334323533333934382c3635343435393330362c333138383339363034382c333337333031353137342c313436363437393930392c3534343137393633352c333131303532333931332c333436323532323031352c313539313637313035342c3730323133383737362c323936363436303435302c333335323739393431322c313530343931383830372c3738333535313837332c333038323634303434332c333233333434323938392c333938383239323338342c323539363235343634362c36323331373036382c313935373831303834322c333933393834353934352c323634373831363131312c38313437303939372c313934333830333532332c333831343931383933302c323438393539363830342c3232353237343433302c323035333739303337362c333832363137353735352c323436363930363031332c3136373831363734332c323039373635313337372c343032373535323538302c323236353439303338362c3530333434343037322c313736323035303831342c343135303431373234352c323135343132393335352c3432363532323232352c313835323530373837392c343237353331333532362c323331323331373932302c3238323735333632362c313734323535353835322c343138393730383134332c323339343837373934352c3339373931373736332c313632323138333633372c333630343339303838382c323731343836363535382c3935333732393733322c313334303037363632362c333531383731393938352c323739373336303939392c313036383832383338312c313231393633383835392c333632343734313835302c323933363637353134382c3930363138353436322c313039303831323531322c333734373637323030332c323832353337393636392c3832393332393133352c313138313333353136312c333431323137373830342c333136303833343834322c3632383038353430382c313338323630353336362c333432333336393130392c333133383037383436372c3537303536323233332c313432363430303831352c333331373331363534322c323939383733333630382c3733333233393935342c313535353236313935362c333236383933353539312c333035303336303632352c3735323435393430332c313534313332303232312c323630373037313932302c333936353937333033302c313936393932323937322c34303733353439382c323631373833373232352c333934333537373135312c313931333038373837372c38333930383337312c323531323334313633342c333830333734303639322c323037353230383632322c3231333236313131322c323436333237323630332c333835353939303238352c323039343835343037312c3139383935383838312c323236323032393031322c343035373236303631302c313735393335393939322c3533343431343139302c323137363731383534312c343133393332393131352c313837333833363030312c3431343636343536372c323238323234383933342c343237393230303336382c313731313638343535342c3238353238313131362c323430353830313732372c343136373231363734352c313633343436373739352c3337363232393730312c323638353036373839362c333630383030373430362c313330383931383631322c3935363534333933382c323830383535353130352c333439353935383236332c313233313633363330312c313034373432373033352c323933323935393831382c333635343730333833362c313038383335393237302c39333639313865332c323834373731343839392c333733363833373832392c313230323930303836332c3831373233333839372c333138333334323130382c333430313233373133302c313430343237373535322c3631353831383135302c333133343230373439332c333435333432313230332c313432333835373434392c3630313435303433312c333030393833373631342c333239343731303435362c313536373130333734362c3731313932383732342c333032303636383437312c333237323338303036352c313531303333343233352c3735353136373131375d2c6e573d5b2230222c2231222c2232222c2233222c2234222c2235222c2236222c2237222c2238222c2239222c2261222c2262222c2263222c2264222c2265222c2266225d2c6e613d342c6e553d36342c6e733d36342c6e4e3d342c6e653d5b2d392c2d38342c2d35302c35392c3131352c3130322c35372c3132352c39342c2d31352c31352c322c2d37322c2d39382c2d37392c33382c2d35362c2d34392c37362c2d32362c2d3131372c36302c39302c392c2d3130372c2d31322c2d37312c2d3130302c36332c34322c2d31382c32382c2d3132302c2d31312c33332c34352c37392c39322c33372c39372c342c35382c39382c38342c2d39372c2d38382c39352c2d3130342c2d31332c2d38392c37382c2d39302c3131392c2d36362c31332c2d352c32392c2d3131362c2d342c2d38312c32372c34302c2d35392c2d34332c38352c34382c2d37342c3130392c2d36342c32362c36372c2d33332c2d3131352c302c2d33372c2d3130322c38382c2d34382c3132372c2d38362c34312c3130352c2d322c3132322c2d34322c3131322c2d39342c38312c2d33312c2d36352c2d3130312c2d31342c36352c34392c2d36372c2d3131342c2d3130332c2d38372c2d31392c3130342c36362c2d37332c2d33342c2d37382c2d34352c2d32372c2d3130392c2d3130382c34372c36312c38362c34332c2d35342c32352c36342c2d33352c2d34342c35332c2d3131322c33362c37332c38392c2d38322c35312c2d33322c33392c2d38332c38302c2d38352c2d3131312c31322c2d35382c3130332c2d37362c2d34362c2d3132372c33342c312c2d39392c31342c2d35372c3131302c3130362c39332c2d35322c31312c3131332c32302c2d3130362c37352c36322c2d36392c2d33392c2d35352c2d3131392c3132362c3131342c3132332c31302c37372c2d3132312c2d382c37342c32312c2d39332c31372c2d36312c2d32312c2d3130352c2d3132362c31382c3132342c2d31372c35322c2d31302c2d37372c2d32342c2d32322c3132302c2d39352c2d32352c39362c2d3131302c32322c2d32332c36392c2d3132352c2d3132382c2d34372c2d33382c2d312c332c2d32302c3130302c36382c3130312c352c3131372c2d3132322c34342c2d35312c2d33362c2d34312c32342c2d38302c33302c38322c2d36332c2d34302c2d39322c39312c2d362c2d35332c2d3132342c2d36322c2d32382c3131312c31392c35302c3130382c37302c2d36382c2d32392c2d37352c39392c2d39312c2d36302c2d37302c37312c2d3131382c2d332c38332c38372c2d372c33322c35352c33312c2d3132332c3132312c3130372c2d3131332c34362c2d33302c3131382c35342c32332c3131362c2d31362c372c362c33352c31362c2d39362c35362c37322c385d2c6e743d226764786964707968786445222c6e543d5b7b683a2277696e646f77222c633a2230303030222c693a21307d2c7b683a22646f63756d656e74222c633a2230303031222c693a21307d2c7b683a226e6176696761746f72222c633a2230303032222c693a21307d2c7b683a226c6f636174696f6e222c633a2230303033222c693a21307d2c7b683a22686973746f7279222c633a2230303034222c693a21307d2c7b683a2273637265656e222c633a2230303037222c693a21307d2c7b683a22706172656e74222c633a2230303038222c693a21307d2c7b683a22746f70222c633a2230303039222c693a21307d2c7b683a2273656c66222c633a2230303130222c693a21307d2c7b683a227061727365466c6f6174222c633a2230313030222c693a21307d2c7b683a227061727365496e74222c633a2230313031222c693a21307d2c7b683a226465636f6465555249222c633a2230313032222c693a21307d2c7b683a226465636f6465555249436f6d706f6e656e74222c633a2230313033222c693a21307d2c7b683a22656e636f6465555249222c633a2230313034222c693a21307d2c7b683a22656e636f6465555249436f6d706f6e656e74222c633a2230313035222c693a21307d2c7b683a22657363617065222c633a2230313036222c693a21307d2c7b683a22756e657363617065222c633a2230313037222c693a21307d2c7b683a226576616c222c633a2230313038222c693a21307d2c7b683a225f7068616e746f6d222c633a2230323030222c693a21317d2c7b683a2263616c6c5068616e746f6d222c633a2230323031222c693a21317d2c7b683a227068616e746f6d222c633a2230323032222c693a21317d2c7b683a227068616e746f6d2e696e6a6563744a73222c633a2230323033222c693a21317d2c7b683a22636f6e746578742e68617368436f6465222c633a2230323131222c693a21317d5d3b76617220763d5b22757365724167656e74222c22517569636b54696d652e517569636b54696d65222c226578706572696d656e74616c2d776562676c222c2241525241595f425546464552222c22e88bb9e69e9ce4b8bde4b8ade9bb91222c22416c6970617920536563757269747920436f6e74726f6c2033222c22536372697074204d5420426f6c64222c222c202762726f7773657250726f70273a222c2254444343746c2e54444343746c222c227769647468222c2273656c66222c22496e666f4261636b67726f756e64222c2250616e646f2057656220506c7567696e222c224861657474656e7363687765696c6572222c227370616e222c22696e6e657248544d4c222c22416374697665426f72646572222c225468726565444c69676874536861646f77222c2230323032222c2230323033222c22666f6e7446616d696c79222c2230323030222c2230323031222c22575049204465746563746f7220312e34222c223b20657870697265733d222c225468726565444461726b536861646f77222c22457869662045766572797768657265222c22426174746c656c6f672047616d65204c61756e63686572222c22496d70616374222c22564c43204d756c74696d6564696120506c7567696e222c2241646f626520486562726577222c22426c7565537461636b7320496e7374616c6c204465746563746f72222c227777776d6d6d6d6d6d6d6d6d6d6c6c69222c22686973746f7279222c2273616e732d7365726966222c223134373331323535323334643431346346393133353664363834453445384635463536633866316263222c2250617079727573222c22427574746f6e54657874222c2230323131222c224170705570222c225061726f6d2e545620706c6179657220706c7567696e222c224465616c506c794c69766520557064617465222c224c6f6869742047756a6172617469222c22465241474d454e545f534841444552222c224167656e6379204642222c224d6163726f6d65646961466c61736850617065722e4d6163726f6d65646961466c6173685061706572222c22232323222c22576f72644361707475726558222c22676574436f6d70757465645374796c65222c22706c6174666f726d222c2230313035222c22417261626963205479706573657474696e67222c2230313036222c2230313033222c22e58d8ee69687e4b8ade5ae8b222c2230313034222c2230313031222c2230313032222c2230313030222c2230313037222c22427574746f6e486967686c69676874222c22766572746578417474726962506f696e746572222c2230313038222c2274657874426173656c696e65222c2223303639222c22646f75626c6554776973742057656220506c7567696e222c226d61746368222c22756e657363617065222c225468756e646572204461704374726c204e5041504920506c7567696e222c22426174616e67222c2244464b61692d5342222c22536e617020495443222c224d696e69626172506c7567696e222c2244617465222c226465636f6465555249436f6d706f6e656e74222c224e50506c617965725368656c6c222c224d53205265666572656e63652053616e73205365726966222c224869726167696e6f2053616e73204742222c227365726966222c22676574436f6e74657874222c22756e69666f726d3266222c224d6f6f6c426f72616e225d2c6d3d2877696e646f772e67647869647079687864653d6e756c6c2c7b763a645b3233335d7d293b2166756e6374696f6e28297b766172206e3d66756e6374696f6e28297b653a7b76617220653d6e543b696628216628652929666f7228766172206e3d675b365d3b6e3c652e6c656e6774683b6e2b2b297b76617220723d655b6e5d3b696628722e6926262166756e6374696f6e2865297b6966282128662865297c7c6628652e68297c7c6628652e632929297b7472797b696628662877696e646f775b652e685d292972657475726e7d63617463682865297b72657475726e7d72657475726e20317d7d287229297b653d723b627265616b20657d7d653d6e756c6c7d69662866286529297b7472797b76617220743d77696e646f772e7061727365466c6f617428645b3138335d293d3d3d675b3337345d262677696e646f772e69734e614e2877696e646f772e7061727365466c6f617428645b3136375d29297d63617463682865297b743d21317d69662874297b7472797b76617220693d77696e646f772e7061727365496e7428645b3332395d293d3d3d675b3236345d262677696e646f772e69734e614e2877696e646f772e7061727365496e7428645b3136375d29297d63617463682865297b693d21317d69662869297b7472797b766172206f3d77696e646f772e6465636f646555524928645b3231335d293d3d3d645b32365d7d63617463682865297b6f3d21317d6966286f297b7472797b76617220613d77696e646f772e6465636f6465555249436f6d706f6e656e7428645b3231345d293d3d3d645b33305d7d63617463682865297b613d21317d69662861297b7472797b766172206c3d77696e646f772e656e636f646555524928645b32365d293d3d3d645b3231335d7d63617463682865297b6c3d21317d6966286c297b7472797b76617220753d77696e646f772e656e636f6465555249436f6d706f6e656e7428645b33305d293d3d3d645b3231345d7d63617463682865297b753d21317d69662875297b7472797b76617220633d77696e646f772e65736361706528645b33305d293d3d3d645b3231345d7d63617463682865297b633d21317d69662863297b7472797b76617220683d77696e646f772e756e65736361706528645b3231345d293d3d3d645b33305d7d63617463682865297b683d21317d69662868297b7472797b76617220733d77696e646f772e6576616c28645b3330395d293d3d3d675b3236345d7d63617463682865297b733d21317d743d733f6e756c6c3a70286e542c645b3137345d297d656c736520743d70286e542c765b36375d297d656c736520743d70286e542c645b3334385d297d656c736520743d70286e542c645b3339365d297d656c736520743d70286e542c645b3338325d297d656c736520743d70286e542c765b37345d297d656c736520743d70286e542c645b3332365d297d656c736520743d70286e542c645b3432345d297d656c736520743d70286e542c645b3435365d297d656c736520743d653b72657475726e20747d28293b6966282166286e292972657475726e206e2e633b7472797b6e3d662877696e646f775b645b3137315d5d297c7c662877696e646f775b645b3137315d5d5b645b3334305d5d293f6e756c6c3a70286e542c645b3331365d297d63617463682865297b6e3d6e756c6c7d6966282166286e292972657475726e206e2e633b7472797b6e3d662877696e646f775b645b3230375d5d297c7c662877696e646f775b645b3230375d5d5b645b3138385d5d293f6e756c6c3a70286e542c645b3237315d297d63617463682865297b6e3d6e756c6c7d66286e297c7c6e2e637d28292c6d5b645b3131305d5d3d226170702e6d6969742d656964632e6f72672e636e223b76617220503d286e65772044617465292e67657454696d6528292b3965353b675b3239395d2c675b3133395d2c675b3133395d2c675b36355d2c675b37375d2c6d5b645b3133365d5d3d7328675b31305d292b502b7328675b31305d292c47333d5b223338323631393439373535343438222c2236333638303030313132373533225d2c6e756c6c213d473326266e756c6c213d4733262647332e6c656e6774683e675b365d3f6d5b645b3138355d5d3d47332e6a6f696e28645b33365d293a286d5b645b3138355d5d3d66756e6374696f6e28652c6e297b666f722876617220723d5b5d2c743d675b365d3b743c6e3b742b2b29722e707573682865293b72657475726e20722e6a6f696e28645b305d297d28645b34335d2c675b33345d292c6d5b645b3136325d5d3d645b34345d292c6e413d223134373331323535323334643431346346393133353664363834453445384635463536633866316263223b76617220773d66756e6374696f6e2865297b766172206e3d5b645b3133375d2c645b3138355d2c645b3133365d2c645b3131305d2c645b3136325d2c645b3136395d2c645b3338345d5d2c723d645b305d3b6966286e756c6c3d3d657c7c6e756c6c3d3d652972657475726e20653b69662828766f696420303d3d3d653f22756e646566696e6564223a6f28652929213d5b645b3239375d2c645b3232375d2c645b3132355d5d2e6a6f696e28645b305d292972657475726e206e756c6c3b722b3d645b3134345d3b666f722876617220742c693d675b365d3b693c6e2e6c656e6774683b692b2b29652e6861734f776e50726f7065727479286e5b695d29262628722b3d645b33315d2b6e5b695d2b645b3236395d2b28743d6e756c6c3d3d28743d645b305d2b655b6e5b695d5d297c7c6e756c6c3d3d743f743a742e7265706c616365282f272f672c645b3436335d292e7265706c616365282f222f672c645b32365d29292b645b3139355d293b72657475726e20722e63686172417428722e6c656e6774682d675b3533315d293d3d645b33365d262628723d722e737562737472696e6728675b365d2c722e6c656e6774682d675b3533315d29292c722b645b3134355d7d286d293b6966286e756c6c3d3d286d3d6e41297c7c6e756c6c3d3d6d297468726f77204572726f7228645b3132325d293b6e756c6c213d7726266e756c6c213d777c7c28773d645b305d293b76617220793d66756e6374696f6e2865297b766172206e2c722c743d675b3339345d3b6966286e756c6c213d6529666f722876617220693d675b365d3b693c652e6c656e6774683b692b2b29743d743e3e3e675b32395d5e6e6c5b28745e655b695d2926675b3239305d5d3b696628743d28653d6128745e675b3339345d29292e6c656e6774682c6e756c6c3d3d657c7c743c675b365d29653d6e657720537472696e6728645b305d293b656c73657b693d5b5d3b666f7228766172206f3d675b365d3b6f3c743b6f2b2b29692e7075736828286e3d655b6f5d2c723d766f696420302c28723d5b5d292e70757368286e575b6e3e3e3e675b31345d26675b34375d5d292c722e70757368286e575b6e26675b34375d5d292c722e6a6f696e28645b305d2929293b653d692e6a6f696e28645b305d297d72657475726e20657d286e756c6c3d3d2847333d77293f5b5d3a6c287729292c533d6c2847332b79292c433d6c286d293b6e756c6c3d3d53262628533d5b5d292c793d5b5d3b666f722876617220543d675b365d3b543c6e613b542b2b297b76617220623d4d6174682e72616e646f6d28292a675b3239325d2c623d4d6174682e666c6f6f722862293b795b545d3d682862297d696628433d75286e2843292c6e287929292c543d433d6e2843292c6e756c6c3d3d28623d53297c7c6e756c6c3d3d627c7c622e6c656e6774683d3d675b365d2976617220783d69286e73293b656c73657b76617220413d622e6c656e6774682c4d3d41256e733c3d6e732d6e4e3f6e732d41256e732d6e4e3a6e732a675b375d2d41256e732d6e4e2c533d5b5d3b7428622c675b365d2c532c675b365d2c41293b666f722876617220443d675b365d3b443c4d3b442b2b29535b412b445d3d675b365d3b7428612841292c675b365d2c532c412b4d2c6e4e292c783d537d6966286e756c6c3d3d28413d78297c7c412e6c656e677468256e73213d675b365d297468726f77204572726f7228645b3133325d293b783d5b5d3b666f722876617220463d675b365d2c493d412e6c656e6774682f6e732c423d675b365d3b423c493b422b2b297b785b425d3d5b5d3b666f722876617220473d675b365d3b473c6e733b472b2b29785b425d5b475d3d415b462b2b5d7d463d5b5d2c7428792c675b365d2c462c675b365d2c6e61293b666f722876617220453d782e6c656e6774682c523d675b365d3b523c453b522b2b297b76617220553d785b525d3b6966286e756c6c3d3d5529766172206b3d6e756c6c3b656c73657b666f7228766172204c3d6828675b38395d292c493d5b5d2c4e3d552e6c656e6774682c483d675b365d3b483c4e3b482b2b29492e70757368286328555b485d2c4c29293b6b3d497d6966286e756c6c3d3d28493d6b292976617220573d6e756c6c3b656c73657b666f7228766172204f3d6828675b38385d292c423d5b5d2c563d492e6c656e6774682c6a3d675b365d3b6a3c563b6a2b2b29422e70757368286328495b6a5d2c4f2d2d29293b573d427d6966286e756c6c3d3d28493d57292976617220513d6e756c6c3b656c73657b76617220583d6828675b3130375d293b423d5b5d3b666f7228766172205f3d492e6c656e6774682c4b3d675b365d3b4b3c5f3b4b2b2b29422e70757368286828495b4b5d2b582b2b29293b513d427d766172207a3d7528512c43293b696628423d542c6e756c6c3d3d28493d7a292976617220593d6e756c6c3b656c7365206966286e756c6c3d3d4229593d493b656c73657b473d5b5d3b666f7228766172204a3d422e6c656e6774682c5a3d675b365d2c713d492e6c656e6774683b5a3c713b5a2b2b29475b5a5d3d6828495b5a5d2b425b5a254a5d293b593d477d7a3d65287528592c5429292c74287a3d65287a292c675b365d2c462c522a6e732b6e612c6e73292c543d7a7d6966286e756c6c3d3d467c7c6e756c6c3d3d462976617220243d6e756c6c3b656c736520696628462e6c656e6774683d3d675b365d29243d645b305d3b656c73657b7661722065653d675b31305d3b7472797b453d5b5d3b666f72287661722072653d675b365d3b72653c462e6c656e6774683b297b696628212872652b65653c3d462e6c656e67746829297b452e70757368287228462c72652c462e6c656e6774682d726529293b627265616b7d452e70757368287228462c72652c656529292c72652b3d65657d243d452e6a6f696e28645b305d297d63617463682865297b7468726f77204572726f7228645b3131335d297d7d72657475726e20242b645b35375d2b507d"
    all_js = bytes.fromhex(js_hex).decode("utf-8")
    ctx = execjs.compile(all_js)

    # 验证码通过，获取token和validate
    captchar_id = "75f9f716460a422f89a628f50fd8cc2b"
    captchar_referer = "https://passport.zhihuishu.com/login"

    win = Win()
    win.withdraw()

    # 登录循环
    need_login = False
    login_success = False

    win_login = WinGUI_login()

    while not login_success:

        while not win_login.success:

            if win_login.winfo_exists():
                win_login.update()
            else:
                print("登录窗口关闭")
                # exit(0)
                win.destroy()

        username = win_login.username
        password = win_login.password
        print("登录窗口：", username, password)

        try:
            with open("cookies.json", "r") as f:
                cookie_data = json.loads(f.read())
                zhihuishu = Zhihuishu(cookie_data["username"], cookie_data['password'], ctx, cookie_data["validate"],
                                      cookie_data["fp"],
                                      cookie_data["cookies"])

            # video_list = zhihuishu.get_videolist()
            # print(video_list)
            #
            # if video_list == -1:
            #     print("重新登录")
            #     need_login = True
            # else:
            #     login_success = True

            # class_list = zhihuishu.get_all_class()
            # print("class_list:",class_list)

            real_name = zhihuishu.get_real_name()

            if real_name == -1:
                print("重新登录")
                need_login = True
            else:
                login_success = True



        except:
            print("读取配置失败")
            need_login = True

        if need_login:
            capt_char = captChar()
            win_verify = Win_verify(capt_char.captchar_data, capt_char.conf, ctx)

            # ima.place(x=40, y=20, width=300, height=170)

            while win_verify.check_res is None or not win_verify.success:
                if win_verify.winfo_exists():
                    win_verify.update()
                else:
                    print("验证码窗口关闭")
                    # exit(0)
                    win.destroy()

            win_verify.destroy()

            if win_verify.success and win_verify.check_res is not None:
                print("check_res", win_verify.check_res)
                zhihuishu = Zhihuishu(username, password, ctx,
                                      win_verify.check_res["data"]["validate"],
                                      capt_char.fp)
                status_tuple = zhihuishu.login()
                if status_tuple[0] == 0:
                    login_success = True

                elif status_tuple[0] == -2:
                    print("登录失败，用户名或密码错误")
                    win_login.tips("用户名或密码错误" + str(status_tuple[1]))
                elif status_tuple[0] == -1:
                    print("登录失败，出现未知错误")
                    win_login.tips("登录失败，出现未知错误")
                elif status_tuple[0] == -6:
                    print("你已连续5次登录失败，请5分钟后尝试")
                    win_login.tips("你已连续5次登录失败，请5分钟后尝试")
                else:
                    print("登录失败，出现未知错误")
                    win_login.tips("登录失败，出现未知错误")

                if status_tuple[0] != 0:
                    win_login.success = False


            else:
                print("验证码验证出现未知错误")
                # exit(0)
                win.destroy()

    # with open("cookies.json", "r") as f:
    #     cookie_data = json.loads(f.read())
    #     zhihuishu = Zhihuishu(cookie_data["username"], cookie_data['password'], ctx, cookie_data["validate"],
    #                           cookie_data["fp"],
    #                           cookie_data["cookies"])

    # 获取账号信息
    real_name = zhihuishu.get_real_name()
    win.tk_label_lqwivlzb['text'] = real_name

    zhihuishu.get_all_class()

    win_login.destroy()
    win_select_class = WinGUI_select_class(zhihuishu.class_list)

    while win_select_class.select_class is None:
        if win_select_class.winfo_exists():
            win_select_class.update()
        else:
            print("选择课程窗口关闭")
            # exit(0)
            win.destroy()

    zhihuishu.class_data['recruitAndCourseId'] = win_select_class.select_class

    zhihuishu.get_videolist()
    zhihuishu.get_study_info()
    zhihuishu.query_course()


    def print(first, second=""):
        win.tk_text_log.insert("1.0", first + " " + second + "\n")


    win.list_data = zhihuishu.video_data
    win.insert_data()
    win.deiconify()

    win_select_class.destroy()
    win.mainloop()
