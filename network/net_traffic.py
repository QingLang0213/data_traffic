# coding=utf-8
import os
import tkFileDialog
import tkMessageBox
import re
from Tkinter import *
import  network
from ttk import Combobox

def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)


class Application(Frame):
    file_list = []
    buffer_list = []

    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.root.title('Network Traffic Test(v1.0.0,qing.guo)')
        self.root.geometry('660x350')
        self.root.resizable(0, 0)  # 禁止调整窗口大小
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.iconbitmap(get_path('net_traffic.ico'))

    def creatWidgets(self):
        frame_left = Frame(self.root, width=355, height=350, bg='#C1CDCD')
        frame_right = Frame(self.root, width=305, height=350, bg='#C1CDCD')

        frame_left.grid_propagate(0)
        frame_right.propagate(0)
        frame_right.grid_propagate(0)

        frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        self.v1 = StringVar()
        self.v2 = StringVar()
        self.v3 = StringVar()
        self.v4 = StringVar()
        self.v2.set('1')
        self.v4.set(network.path)


        Label(frame_left, text=u"选择设备id:", bg='#C1CDCD').grid(row=0, column=0, pady=20, padx=10)
        self.cb1 = Combobox(frame_left, width=25, textvariable=self.v1, postcommand=self.cb1_click)
        self.cb1.grid(row=0, column=1, ipady=1, padx=5, sticky=W)
        self.cb1.bind('<<ComboboxSelected>>', self.cb1_select)

        Label(frame_left, text=u"间隔时间:", bg='#C1CDCD').grid(row=1, column=0, pady=20, padx=10)
        Entry(frame_left, width=27, textvariable=self.v2).grid(row=1, column=1, ipady=2, padx=5, sticky=W)

        Button(frame_left, text=u"应用包名:", bg='#C1CDCD',command=self.get_focused_package).grid(row=2, column=0, pady=20, padx=10)
        Entry(frame_left, width=35, textvariable=self.v3).grid(row=2, column=1,ipady=2, pady=20, padx=5, sticky=W)

        self.b1 = Button(frame_left, text=u"开始测试", command=self.start_test, bg='#C1CDCD')
        self.b1.grid(row=4, column=0, padx=15, pady=15)
        self.b2 = Button(frame_left, text=u"结束测试", command=self.end_test, bg='#C1CDCD')
        self.b2.grid(row=4, column=1, padx=15, pady=15)

        Button(frame_left, text=u"测试结果", command=self.open_file, bg='#C1CDCD').grid(row=5, column=0, padx=5, pady=25)
        Entry(frame_left, width=35, textvariable=self.v4).grid(row=5, column=1, ipady=1, padx=5, pady=15)

        scrollbar = Scrollbar(frame_right, bg='#C1CDCD')
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_msglist = Text(frame_right, yscrollcommand=scrollbar.set, bg='#C1CDCD')
        self.text_msglist.pack(side=RIGHT, fill=BOTH)
        scrollbar['command'] = self.text_msglist.yview
        self.text_msglist.tag_config('green', foreground='#008B00')
        self.text_msglist.tag_config('blue', foreground='#0000FF')
        self.text_msglist.tag_config('red', foreground='#FF3030')
        self.text_msglist.tag_config('purple', foreground='#CD00CD')

    def cb1_click(self):
        device_list = os.popen('adb devices').readlines()
        self.cb1['values'] = device_list

    def cb1_select(self, event):
        v = self.v1.get()
        self.v1.set(v.split()[0])

    def start_test(self):
        device = self.v1.get()
        delay_time = self.v2.get()
        pkg_name=self.v3.get()

        if device == '' or device.isspace():
            self.text_msglist.insert(END, 'please input device id\n', 'red')
            return -1
        if delay_time == '' or delay_time.isspace() or not delay_time.isdigit():
            self.text_msglist.insert(END, 'please input device id\n', 'red')
            return -1
        network.Traffic.set_flag('False')
        f1 = network.Traffic(1, device, delay_time, pkg_name,app)
        f1.setDaemon(True)
        f1.start()
        self.b1.config(state='disabled')
        self.b2.config(state='normal')

    def end_test(self):

        self.b1.config(state='normal')
        network.Traffic.set_flag('True')
        self.b2.config(state='disabled')

    def get_focused_package(self):
        pattern = re.compile(r"[a-zA-Z0-9_\.]+/.[a-zA-Z0-9_\.]+")
        out = os.popen("adb shell dumpsys window w | findstr \/ | findstr name=").read()
        component = pattern.findall(out)[-1]
        pkg_name = component[:component.index('/')]
        self.v3.set(pkg_name)


    def open_file(self):
        filename = tkFileDialog.askopenfilename(initialdir=network.path)
        if filename == '':
            return 0
        os.startfile(filename)

    def close(self):
        result = tkMessageBox.askokcancel(title=u"退出", message=u"确定退出程序? 请先保存测试数据!")
        if result:
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    f = open(network.log_path + 'net_traffic.txt', 'w')
    sys.stderr = f
    root = Tk()
    app = Application(root)
    app.creatWidgets()
    app.mainloop()
    f.close()

