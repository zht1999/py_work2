# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 20:42:27 2019

@author: dell
"""

#import matplotlib
import sqlite3
import requests
import time
import numpy as np
import matplotlib.pyplot as plt
#渐变色条形图
def gbar(ax, x, y, width=0.5, bottom=0):
    X = [[.6, .6], [.7, .7]]
    for left, top in zip(x, y):
        right = left + width
        #颜色填充
        ax.imshow(X, interpolation='bicubic', cmap=plt.cm.Greens,
                  extent=(left, right, top,bottom), alpha=1)
#获取时间戳
def gettime():
    return int(round(time.time() * 1000))
#获取数据
class Data_op:
    #初始化
    def __init__(self):
        self.datadict={}
        self.request()
        self.data_tract()
        self.data_write()
    #访问数据
    def request(self):
        #头部
        headers = {}
        # 用来传递参数的
        keyvalue = {}
        # 目标网址(问号前面的东西)
        url = 'http://data.stats.gov.cn/easyquery.htm'
        # 头部的填充
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) '\
                                'AppleWebKit/537.36 (KHTML, like Gecko) '\
                                'Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.00'
        # 参数的填充
        keyvalue['m'] = 'QueryData'
        keyvalue['dbcode'] = 'hgnd'
        keyvalue['rowcode'] = 'zb'
        keyvalue['colcode'] = 'sj'
        keyvalue['wds'] = '[]'
        keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0O0K"}]'
        keyvalue['k1'] = str(gettime())
        # 建立一个Session
        s = requests.session()
        # 在Session基础上进行一次请求
        r = s.post(url, params=keyvalue, headers=headers)
        # 修改dfwds字段内容
        keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
        # 再次进行请求
        r = s.get(url, params=keyvalue, headers=headers)
        js=r.json()
        self.requ_get=js["returndata"]["datanodes"]
    #提取数据
    def data_tract(self):
        
        for year in range(1999,2019):
            self.datadict[str(year)]={}
        for node in self.requ_get:
            #若data为空，则填充-1
            if node["data"]["hasdata"]==False:
                node["data"]["data"]=-1
            self.datadict[node["wds"][1]["valuecode"]][node["wds"][0]["valuecode"]]\
            =node["data"]["data"]
    #写入数据    
    def data_write(self):
        
        self.conn = sqlite3.connect('dbsecond.db')
        self.c = self.conn.cursor()
        #创建表
        self.c.execute('''CREATE TABLE DATA
           (YEAR INT PRIMARY KEY     NOT NULL,
           TOTAL         INT    NOT NULL,
           GOVER         INT    NOT NULL,
           SOCIE         INT     NOT NULL,
           INDIV         INT,
           AVE           INT,
           URBAN         INT,
           RURAL         INT);''')
        for year in self.datadict:
            single=self.datadict[year]
            self.c.execute("INSERT INTO DATA VALUES(?,?,?,?,?,?,?,?)",\
              (int(year), single["A0O0K01"],single["A0O0K02"],single["A0O0K03"],
               single["A0O0K04"],single["A0O0K05"],
               single["A0O0K06"],single["A0O0K07"]));
        self.conn.commit()
        self.conn.close()
#提取数据
class Plot_op:
    #初始化
    def __init__(self):
        
        self.datadict={}
        self.yearlist=[]
        self.totallist=[]
        self.goverlist=[]
        self.socielist=[]
        self.indivlist=[]
        self.avelist=[]
        self.urbanlist=[]
        self.rurallist=[]
        self.data_read()
        self.plot_total()
        self.plot_aspect()
        self.plot_ur_ru()
    #读取数据    
    def data_read(self):
        
        self.conn = sqlite3.connect('dbsecond.db')
        self.c = self.conn.cursor()
        cursor = self.c.execute("SELECT year,total,gover,socie,"\
                                "indiv,ave,urban,rural  from DATA")
        for row in cursor:
            self.datadict[row[0]]={"total":row[1],"gover":row[2],
                         "socie":row[3],"indiv":row[4],
                         "ave":row[5],"urban":row[6],
                         "rural":row[7]}
            self.yearlist.append(row[0])
            #若数据为空则不读入
            if row[1]!=-1:
                self.totallist.append(row[1])
                self.goverlist.append(100*row[2]/row[1])
                self.socielist.append(100*row[3]/row[1])
                self.indivlist.append(100*row[4]/row[1])
            self.avelist.append(row[5])
            if row[6]!=-1:
                self.urbanlist.append(row[6])
                self.rurallist.append(row[7])
        self.conn.close()
    #全国卫生支出条形图
    def plot_total(self):
        #设置上下限
        xmin, xmax = xlim = 0,19
        ymin, ymax = ylim = 0,60000
        
        fig, ax = plt.subplots()
        ax.set(xlim=xlim, ylim=ylim, autoscale_on=False)
        index=np.arange(19)
        x = index + 0.25
        y = self.totallist
        gbar(ax, x, y, width=0.5)
        ax.set_aspect('auto')
        fig.set_size_inches(15, 7)
        #设置标签
        ax.set_xlabel('年份（年）',fontsize=15)
        ax.set_ylabel('卫生总费用（亿元）',fontsize=15)
        ax.set_title('1999-2017年全国卫生总费用条形图',fontsize=25)
        ax.set_xticks(index+0.5 )
        ax.set_xticklabels(index+1999)
        fig.savefig('total_2.png', dpi=100)
        plt.show()
    #全国卫生支出方面比例折线图
    def plot_aspect(self):
        
        index = np.arange(19)
        fig, ax = plt.subplots()
        ax.set_xlabel('年份（年）',fontsize=15)
        ax.set_ylabel('比例（%）',fontsize=15)
        ax.set_title('1999-2017年各方面卫生支出比例',fontsize=25)
        ax.set_xticks(index )
        ax.set_xticklabels(index+1999)

        fig.set_size_inches(15, 7)
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus']=False 
        
        plt.plot(index,self.goverlist,color='blue', linestyle='-',
                 linewidth=3, marker='x', markersize=8,
                 label='政府')
        plt.plot(index,self.socielist,color='red', linestyle='-', 
                 linewidth=3, marker='o', markersize=8,
                 label='社会')
        plt.plot(index,self.indivlist,color='green', linestyle='-',
                 linewidth=3, marker='s', markersize=8,
                 label='个人')
        plt.grid(True)
        plt.ylim([0,70])
        ax.legend()
        fig.savefig('aspect_2.png', dpi=100)
        plt.show()

    def plot_ur_ru(self):

        fig, ax = plt.subplots()
        index = np.arange(16)
        bar_width = 0.35
        opacity = 0.4
        #设置两个axis
        rects1 = ax.bar(index, self.urbanlist, bar_width,
                        alpha=opacity, color='b',
                        label='城镇')
        rects2 = ax.bar(index + bar_width, self.rurallist, bar_width,
                        alpha=opacity, color='r',
                        label='乡村')
        
        ax.set_xlabel('年份（年）',fontsize=15)
        ax.set_ylabel('居民人均卫生支出（元）',fontsize=15)
        ax.set_title('1999-2014城镇乡村居民人均卫生支出',fontsize=25)
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(index+1999)
        fig.set_size_inches(15, 7)
        plt.rcParams['font.sans-serif']=['SimHei'] 
        plt.rcParams['axes.unicode_minus']=False
        plt.grid(True)
        ax.legend()
        fig.savefig('ur_ru_2.png', dpi=100)
        plt.show()                
                
if __name__ == '__main__':
    
    data=Data_op()
    plot=Plot_op()
