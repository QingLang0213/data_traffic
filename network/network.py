#coding=utf-8
import os,time
import subprocess
import threading
import xlsxwriter
from Tkinter import *


file_path=os.path.abspath(sys.argv[0])  
path_list=file_path.split('\\')
path_list.pop()
path='\\'.join(path_list)

path=path+'\\result\\'
log_path=path+'\\'

log_path=unicode(log_path,"gb2312")
path=unicode(path,"gb2312")

if not os.path.exists(path): os.makedirs(path)
if not os.path.exists(log_path): os.makedirs(log_path)
flag=False

class Traffic(threading.Thread):

    def __init__(self, threadID, device, delay_time, pkg_name, app):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.device = device
        self.delay_time = int(delay_time)
        self.pkg_name = pkg_name
        self.app = app
        self.Time = []
        self.rx_total=[]
        self.tx_total = []
        self.rx_list = []
        self.tx_list = []

    @staticmethod
    def set_flag(f):
        global flag
        if f == "False":
            flag = False
        else:
            flag = True
            print 'True'

    def get_uid(self):
        uid_info=os.popen('adb -s %s shell dumpsys package %s |findstr userId'%(self.device, self.pkg_name)).readline()
        uid = uid_info.split()[0].split('=')[-1]
        return uid

    def run(self):

        uid=self.get_uid()
        self.app.text_msglist.insert(END, u"          userID: "+uid+'\n\n', 'blue')

        def counter(i):
            if not flag:
                sum_rx = sum_tx = 0
                net_info=subprocess.Popen('adb -s %s shell cat /proc/net/xt_qtaguid/stats |findstr %s'%(self.device,uid),\
                shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.readlines()
                for item in net_info:
                    tmp=item.split()
                    rx_bytes = tmp[5]
                    tx_bytes = tmp[7]
                    sum_rx += float(rx_bytes)
                    sum_tx += float(tx_bytes)
                self.rx_total.append(sum_rx/1024)
                self.tx_total.append(sum_tx/1024)
                if i>=1:
                    rx=round(self.rx_total[i]-self.rx_total[i-1],2)
                    tx=round(self.tx_total[i]-self.tx_total[i-1],2)
                    print rx,tx
                    self.app.text_msglist.insert(END,u"下载流量%-12s"%(str(rx)+'kb'),'blue')
                    self.app.text_msglist.insert(END,u"上传流量%-12s\n"%(str(tx)+'kb'), 'blue')
                    self.app.text_msglist.see(END)
                    self.rx_list.append(rx)
                    self.tx_list.append(tx)
                    self.Time.append(time.strftime('%H:%M:%S', time.localtime()))
                self.app.text_msglist.after(self.delay_time * 1000-10, counter, i + 1)

            else:
                self.write_xlsx()
                self.app.b2.config(state='disabled')
                self.app.b1.config(state='normal')
                self.app.text_msglist.insert(END, u"测试完成\n", 'green')
        counter(0)

    def write_xlsx(self):
        date = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        w = xlsxwriter.Workbook(path + 'net_traffic' + date + '.xlsx')
        ws = w.add_worksheet('data')
        title_list=['Time',u'下载流量kb', u'上传流量kb']
        ws.write_row('A1', title_list)
        length = len(self.Time)
        ws.write_column('A2',self.Time)
        ws.write_column('B2',self.rx_list)
        ws.write_column('C2',self.tx_list)

        chart = w.add_chart({'type': 'line'})
        chart.add_series(
            {'name': '=data!$B$1'
                , 'categories': '=data!$A$2:$A$%d' % length
                , 'values': '=data!$B$2:$B$%d' % length
                , 'line': {'width': 1.25, 'color': 'blue'}
             })
        chart.add_series(
            {'name': '=data!$C$1'
                , 'values': '=data!$C$2:$C$%d' % length
                , 'line': {'width': 1.25, 'color': 'green'}
             })
        chart.set_title({'name': self.pkg_name})  # 图标名称
        chart.set_size({'width': 1200, 'height': 800})
        ws.insert_chart('E7', chart, {'x_offset': 40, 'y_offset': 10})
        w.close()


