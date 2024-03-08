from tkinter import *
from tkinter import Tk

import base64
import ctypes
import io
import json
import requests
import threading
import time
from PIL import Image as PILImage
from ttkbootstrap import *

from Zhihuishu import Zhihuishu
from captcha.captcha import Captcha

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


requests = Requests()


# 验证码窗口ui
class WinguiVerify(Toplevel):
    def __init__(self):

        super().__init__()
        self.im_slide = None
        self.image_file = None
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


# 验证码窗口
class WinVerify(WinguiVerify):
    def __init__(self, captchar_data, conf):
        self.check_res = None
        self.move_rate = 0
        self.success = False
        self.captchar_data = captchar_data
        self.conf = conf
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
        res = capt_cha.check_captchar(self.move_rate)
        res_json = json.loads(res)
        self.check_res = res_json
        result = res_json["data"]["result"]
        capt_cha.result = result
        if result:
            print("\033[1;32mTrue\033[0m")
        else:

            print("\033[1;31mFalse")
            print("res:\t", res, "\033[0m")
        # 展示结果
        if result:
            self.success = True
            self.tk_lable_tips["foreground"] = "green"
            self.tk_lable_tips["text"] = "验证结果：" + str(result)
            thread = threading.Thread(target=self.wait_distory)
            thread.daemon = True
            thread.start()
        else:
            self.tk_lable_tips["foreground"] = "red"

            self.tk_lable_tips["text"] = "验证结果：" + str(result)
            thread = threading.Thread(target=self.refress_th)
            thread.daemon = True
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
            if capt_cha.result is not None:
                capt_cha.__init__(captcha_id, captcha_referer)
                self.captchar_data = capt_cha.captchar_data
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


# 主窗口ui
class WinguiMain(Tk):
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
        # 设置窗口图标
        self.iconphoto(True, PhotoImage(file="img/icon.png"))

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


# 主窗口
class Win(WinguiMain):
    def __init__(self):

        super().__init__()
        self.playspeed = None
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

    # 更新：进度条，正在播放的课程名称，日志
    def updata_prossbar_th(self):
        finished_block_temp = 0
        log_temp = ""
        while self.playing:
            time.sleep(0.3)
            self.tk_progressbar_prograssbar["value"] = zhihuishu.playtime
            self.tk_progressbar_prograssbar["maximum"] = zhihuishu.totaltime

            self.tk_progressbar_prograssbar_little["value"] = zhihuishu.wait_time
            self.tk_progressbar_prograssbar_little["maximum"] = 10

            finished_block = zhihuishu.finished_block
            total_block = zhihuishu.total_block

            if finished_block_temp != finished_block:
                self.insert_log("已完成：" + str(finished_block) + "/" + str(total_block))
                finished_block_temp = finished_block

            log = zhihuishu.log
            if log_temp != log:
                self.insert_log(log)
                log_temp = log

    def play_class_th(self, select_idlist):
        for classid in select_idlist:
            # 改变正在播放的课程名称
            # print(zhihuishu.video_data)
            # print(zhihuishu.video_data[str(classid)])
            name = zhihuishu.video_data[str(classid)]["name"]
            self.tk_playing_class_name["text"] = name
            self.insert_log("正在播放：" + name)

            zhihuishu.play_class(classid)
            self.insert_log("完成")

        self.playing = False

    def play(self, evt):
        if self.playing:
            self.insert_log("正在播放中，请勿重复点击")
            return
        else:
            self.playing = True

        # 获取倍速
        self.playspeed = self.tk_input_speed.get()
        # 如果倍速不是数字
        try:
            self.playspeed = float(self.playspeed)
        except:
            self.insert_log("倍速输入错误，已自动设置为1.0")
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

    def insert_log(self, data):
        self.tk_text_log.insert("1.0", data + "\n")


# 选课窗口
class WinguiSelectClass(Toplevel):
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
            # print(classes)
            self.tk_table_lqwnmy9p.insert("", "end",
                                          values=(classes["id"], classes["name"], classes["recruitAndCourseId"]))

    def select(self, evt):
        selected_items = self.tk_table_lqwnmy9p.selection()
        if len(selected_items) == 0 or len(selected_items) > 1:
            print("未选择课程或选择了多个课程")
            return
        self.select_class = self.tk_table_lqwnmy9p.item(selected_items[0], "values")[2]


# 登录窗口
class WinguiLogin(Toplevel):
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

    # 验证码通过，获取token和validate
    captcha_id = "75f9f716460a422f89a628f50fd8cc2b"
    captcha_referer = "https://passport.zhihuishu.com/login"

    win = Win()
    win.withdraw()

    # 登录循环
    need_login = False
    login_success = False
    win_login = WinguiLogin()

    while not login_success:
        while not win_login.success:
            if win_login.winfo_exists():
                win_login.update()
            else:
                print("登录窗口关闭")
                win.destroy()
                exit(0)
        username = win_login.username
        password = win_login.password
        print("登录窗口：", username, password)
        try:
            with open("cookies.json", "r") as f:
                cookie_data = json.loads(f.read())
                zhihuishu = Zhihuishu(cookie_data["username"], cookie_data['password'], cookie_data["validate"],
                                      cookie_data["fp"],
                                      cookie_data["cookies"])
            real_name = zhihuishu.get_real_name()
            if real_name == -1:
                print("重新登录")
                need_login = True
            else:
                login_success = True
            # 检测是否切换了账号
            if username != cookie_data["username"]:
                need_login = True


        except:
            print("读取配置失败")
            need_login = True
        if need_login:
            capt_cha = Captcha(captcha_id, captcha_referer)

            win_verify = WinVerify(capt_cha.captchar_data, capt_cha.conf)
            while win_verify.check_res is None or not win_verify.success:
                if win_verify.winfo_exists():
                    win_verify.update()
                else:
                    print("验证码窗口关闭")
                    win.destroy()
                    exit(0)
            win_verify.destroy()
            if win_verify.success and win_verify.check_res is not None:
                print("check_res", win_verify.check_res)

                zhihuishu = Zhihuishu(username, password,
                                      win_verify.check_res["data"]["validate"],
                                      capt_cha.fp)

                secretStr = capt_cha.encrypt_login_data(username, password, win_verify.check_res["data"]["validate"],
                                                        capt_cha.fp)
                status_tuple = zhihuishu.login(secretStr)

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

    # 登录完成
    # 获取真实姓名
    real_name = zhihuishu.get_real_name()
    win.tk_label_lqwivlzb['text'] = real_name

    # 获取课程列表
    zhihuishu.get_all_class()

    win_login.destroy()

    # 选课界面
    win_select_class = WinguiSelectClass(zhihuishu.class_list)

    while win_select_class.select_class is None:
        if win_select_class.winfo_exists():
            win_select_class.update()
        else:
            print("选择课程窗口关闭")
            win.destroy()
            exit(0)

    # 选课完成，准备播放
    zhihuishu.class_data['recruitAndCourseId'] = win_select_class.select_class
    zhihuishu.get_videolist()
    zhihuishu.get_study_info()
    zhihuishu.query_course()

    win.list_data = zhihuishu.video_data
    win.insert_data()
    win.deiconify()

    win_select_class.destroy()
    win.mainloop()
