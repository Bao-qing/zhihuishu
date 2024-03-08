import base64
import json
import time

import requests
from tqdm import trange

from encrypt.encrypt import encrypt_aes_cbc_pkcs7


class Zhihuishu:

    def __init__(self, username, password, validate, fp, cookies=None):
        if cookies is None:
            cookies = {}
        self.wait_time = 0
        self.playspeed = 1
        self.username = username
        self.password = password
        self.validate = validate
        self.fp = fp
        self.cookies = cookies

        self.class_list = None
        self.video_data = None
        self.pop_up_exam = None
        self.totaltime = None
        self.playtime = None
        self.videoChapterDtos = None
        self.courseId = None
        self.recruitId = None
        self.uuid = None
        self.pwd = None
        self.uuid = None
        self.SESSION = None
        self.jt_cas = None
        self.playing_class = None
        self.log = ""
        self.finished_block = 0
        self.total_block = 0

        self.class_data = {
            "recruitAndCourseId": "",
            "dateFormate": 1703671623000
        }
        self.key = "azp53h0kft7qi78q"
        self.iv = '31673371716468346a7662736b623978'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
            "sec-ch-ua": "Not",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows"
        }

    def get_all_class(self):
        headers = {
            "Origin": "https://onlineweb.zhihuishu.com",
            "Referer": "https://onlineweb.zhihuishu.com/",
        }
        headers.update(self.headers)

        url = "https://onlineservice-api.zhihuishu.com/gateway/t/v1/student/course/share/queryShareCourseInfo"
        data = {
            "secretStr": "NEuH3llD9woD4DQgu0k6Uvp5yyo8WT84Dq5lU2iPwvgKNatePzJ+vu/4PRaNYy+K",
            "date": "1704217471129"
        }

        cookies = {"jt-cas": self.cookies.get("jt-cas")}

        response = requests.post(url, headers=headers, cookies=cookies, data=data)

        try:

            class_list = []
            for i in response.json()["result"]["courseOpenDtos"]:
                class_list.append({"name": i["courseName"], "id": i["courseId"], "recruitAndCourseId": i['secret']})

            print("获取课程列表成功")
            # print(class_list)
            self.class_list = class_list
            return class_list
        except:
            print(response.text)
            print("获取课程列表失败,请检查cookies")

            self.class_list = []
            return -1

    # secretStr通过调用验证码模块的encrypt_login_data方法获取
    def login(self, secretStr):
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
            "secretStr": secretStr,

        }

        response = requests.post(url, data=data, headers=headers)
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
        response = requests.get(url, headers=headers, cookies=self.cookies, params=params,
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
        response = requests.get(location1, headers=headers, cookies=self.cookies,
                                allow_redirects=False)
        set_cookie = dict(response.cookies)
        self.cookies.update(set_cookie)
        # print(response)
        print("登录成功")

        # location2 = response.headers.get("location")
        # print("location2,重定向：", location2)
        # response = requests.get(location1, headers=headers, cookies=self.cookies,
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
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/videolist"

        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(self.class_data).replace("'", '"'), self.key, self.iv)
        # data = "secretStr=QhSgx0MEvvp0jRL20aaxWrXZYS%2F7NpyvaxFF5i8yEdUC0od6TN2zhNHxLPe53K4QZk0iJZX5DHKsdURDV9qsC7owkrF40cd%2FqJw1NxfwcCqOlIapESCmBFwJLBMJnVuo&dateFormate=1703742779000"

        response = requests.post(url, headers=headers, cookies=self.cookies, data=data)
        response_json = response.json()
        print("获取sp列表:", response_json)

        # recruitId 和 courseId 在之前已获取（query_course）
        # print(response.text)
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
        headers = {
            "Accept": "*/*",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
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
        response = requests.post(url, headers=headers, cookies=self.cookies, data=data)
        self.study_info = response.json()["data"]

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

    def get_pop_up_exam_list(self, lessonId, lessonVideoId):
        headers = {
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/loadVideoPointerInfo"
        # print(self.recruitId)
        date_formate = int(time.time() * 1000)
        to_encrypt_ = {"lessonId": lessonId, "recruitId": self.recruitId, "courseId": self.courseId,
                       "dateFormate": date_formate, "lessonVideoId": lessonVideoId}
        # print("获取弹窗题目list：", str(to_encrypt_))
        # print(self.class_data)

        data = {
            "secretStr": encrypt_aes_cbc_pkcs7(str(to_encrypt_).replace("'", '"'), self.key, self.iv),
            "dateFormate": str(date_formate)
        }
        response = requests.post(url, headers=headers, data=data, cookies=self.cookies)
        pop_exam_res = response.json()
        if pop_exam_res["code"] == 0:
            print("获取弹窗题目成功")
            self.log = "获取弹窗题目成功"
            try:
                self.pop_up_exam = pop_exam_res["data"]["questionPoint"]
            except KeyError:
                print("没有弹窗题目")
                self.log = "没有弹窗题目"
                self.pop_up_exam = []

            return pop_exam_res
        else:
            print("警告：获取弹窗题目失败，将忽略弹窗题目")
            self.log = "获取弹窗题目失败,将忽略弹窗题目"
            self.pop_up_exam = []

            return -1

    def get_pop_up_exam_detail(self, lessonId, questionId):
        import requests

        headers = {
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/lessonPopupExam"

        date_formate = int(time.time() * 1000)
        to_encrypt_ = {"lessonId": lessonId,
                       "questionIds": questionId,
                       "dateFormate": date_formate}

        print("获取弹窗题目详情：", to_encrypt_)

        data = {
            "secretStr": encrypt_aes_cbc_pkcs7(str(to_encrypt_).replace("'", '"'), self.key, self.iv),
            "dateFormate": str(date_formate)
        }
        response = requests.post(url, headers=headers, data=data, cookies=self.cookies)
        pop_exam_detail_res = response.json()
        if pop_exam_detail_res["code"] == 0:
            print("获取弹窗题目详情成功")
            self.log = "获取弹窗题目详情成功"
            return pop_exam_detail_res
        else:
            print("警告：获取弹窗题目详情失败")
            self.log = "获取弹窗题目详情失败"
            return -1

    def save_pop_up_exam(self, lessonId, questionDetail):

        date_formate = int(time.time() * 1000)
        for question in questionDetail["lessonTestQuestionUseInterfaceDtos"]:
            # 遍历寻找正确答案
            answers = []
            print(question)

            for answer in question['testQuestion']['questionOptions']:
                if answer['result'] == "1":
                    answers.append(str(answer['id']))

            to_encrypt_ = {"courseId": 1000102147,
                           "recruitId": 244565,
                           "testQuestionId": question['testQuestion']['questionId'],
                           "isCurrent": "1",
                           "lessonId": lessonId,
                           "answer": ",".join(answers),
                           "testType": 0,
                           "dateFormate": date_formate}

            # print("答案：", to_encrypt_)
            # 提交答案
            headers = {
                "Origin": "https://studyvideoh5.zhihuishu.com",
                "Referer": "https://studyvideoh5.zhihuishu.com/",
            }
            headers.update(self.headers)
            url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/saveLessonPopupExamSaveAnswer"
            data = {
                "secretStr": encrypt_aes_cbc_pkcs7(str(to_encrypt_).replace("'", '"'), self.key, self.iv),
                "dateFormate": str(date_formate)
            }
            response = requests.post(url, headers=headers, data=data, cookies=self.cookies)
            save_answer_res = response.json()
            if save_answer_res["code"] == 0:
                print("提交弹窗题目答案成功")
                self.log = "提交弹窗题目答案成功"

            else:
                print("警告：提交弹窗题目答案失败")
                self.log = "提交弹窗题目答案失败"
                print(save_answer_res)

    def query_course(self):
        course_data = self.class_data

        headers = {
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryCourse"
        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(course_data).replace("'", '"'), self.key, self.iv)
        response = requests.post(url, headers=headers, cookies=self.cookies, data=data)
        response_json = response.json()
        self.recruitId = response_json["data"]["recruitId"]
        self.courseId = response_json["data"]["courseInfo"]["courseId"]

        print("获取课程信息成功")

    def get_real_name(self):
        import requests

        headers = {
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)

        url = "https://studyservice-api.zhihuishu.com/gateway/f/v1/login/getLoginUserInfo"
        params = {
            "dateFormate": "1704220652000"
        }
        response = requests.get(url, cookies=self.cookies, params=params, headers=headers)
        print("realname:", response.text)

        try:
            json_data = response.json()
            realName = json_data["data"]["realName"]
            self.uuid = json_data["data"]["uuid"]

            return realName
        except:
            return -1

    def playing_encrypt(self, t):
        t = list(map(str, t))

        def Z(t):
            i = ";".join(t)
            return X(i)

        def X(t):
            _d = "zzpttjd"
            i = ""
            for h in range(len(t)):
                s = ord(t[h]) ^ ord(_d[h % 7])
                i += Y(s)
            return i

        def Y(t):
            t = hex(t)[2:]
            if len(t) < 2:
                t = "0" + t
            return t[-4:]

        return Z(t)

    def play_class(self, class_id):
        if self.video_data[class_id]["watchState"] == 1:
            return
        print("开始播放课程：", self.video_data[class_id]["name"])
        self.playing_class = self.video_data[class_id]["name"]

        # 获取弹窗题目
        self.get_pop_up_exam_list(self.video_data[str(class_id)]["bigLessionId"],
                                  self.video_data[class_id]["smallLessionId"])

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

        self.total_block = round(total_time / 10)

        for i in trange(round(pre_learn_data['studyTotalTime'] / 10), round((total_time) / 10)):
            self.playtime = i
            self.totaltime = round((total_time) / 10)
            this_video_data[6] = 0
            watch_point = "0,1"
            ctrl = 1
            while ctrl:
                self.wait_time = this_video_data[6]
                time.sleep(1 / self.playspeed)

                # 本段已观看时间
                this_video_data[6] += 1

                # 总观看时间
                this_video_data[7] = this_video_data[7] + 1
                a = this_video_data[7]

                # print("totaltime:", this_video_data[7])
                # print("\n")

                # 触发弹窗题目

                for question_time in self.pop_up_exam:
                    if this_video_data[7] == question_time["timeSec"]:
                        print("触发弹窗题目")
                        self.log = "触发弹窗题目"
                        question_detail = self.get_pop_up_exam_detail(self.video_data[str(class_id)]["bigLessionId"],
                                                                      question_time["questionIds"])

                        self.save_pop_up_exam(class_id, question_detail["data"])

                b = a // 3600
                c = (a - b * 3600) // 60
                d = a - b * 3600 - c * 60
                this_video_data[8] = "%02d:%02d:%02d" % (b, c, d)
                watch_point += "," + str(round(this_video_data[7] / 5) + 2)
                if this_video_data[6] > 10:
                    ctrl = 0

            post_data = {
                'ewssw': watch_point,
                'sdsew': self.playing_encrypt(this_video_data),
                'zwsds': str(base64.b64encode(str(pre_learn_data['id']).encode("utf-8"))).replace("b'", "").replace("'",
                                                                                                                    ""),
                'courseId': self.courseId,
            }

            self.post_class(post_data)
            self.finished_block = i
            print("已完成：" + str(i) + "/" + str(round(total_time / 10)))

    def post_class(self, postData):
        headers = {
            "Accept": "*/*",
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
        url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTimeV2"
        data = "secretStr=" + encrypt_aes_cbc_pkcs7(str(postData).replace("'", '"'), self.key, self.iv)
        # print(encrypt_aes_cbc_pkcs7(str(postData).replace("'", '"'), self.key, self.iv))

        response = requests.post(url, cookies=self.cookies, data=data, headers=headers)
        # print("post_class:", response.json()['message'])
        self.log = response.json()['message']

    def pre_learning_note(self, class_id):
        import requests

        headers = {
            "Origin": "https://studyvideoh5.zhihuishu.com",
            "Referer": "https://studyvideoh5.zhihuishu.com/",
        }
        headers.update(self.headers)
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
        response = requests.post(url, cookies=self.cookies, data=data, headers=headers)
        print("获取视频播放进度成功")
        try:
            return response.json()["data"]['studiedLessonDto']
        except:
            # print(self.video_data)
            print("获取视频播放进度失败")
            print(response.text)
