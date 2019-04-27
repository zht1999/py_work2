# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:56:13 2019

@author: dell
"""

#%matplotlib qt5
import sqlite3
import requests
import time
import numpy as np
import matplotlib.pyplot as plt

# 用来获取时间戳
def gettime():
    return int(round(time.time() * 1000))
#爬取数据并存入
class Data_op:
    #初始化
    def __init__(self):
        
        self.datadict={}
        self.request()
        self.data_tract()
        self.data_write()
    #爬取数据    
    def request(self):
        # 用来自定义头部的
        headers = {}
        # 用来传递参数的
        keyvalue = {}
        # 目标网址
        url = 'http://data.stats.gov.cn/easyquery.htm'
        # 头部的填充
        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14)'\
                                'AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                                'Version/12.0 Safari/605.1.15'
        # 参数的填充
        keyvalue['m'] = 'QueryData'
        keyvalue['dbcode'] = 'hgnd'
        keyvalue['rowcode'] = 'zb'
        keyvalue['colcode'] = 'sj'
        keyvalue['wds'] = '[]'
        keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0301"}]'
        keyvalue['k1'] = str(gettime())
        # 建立一个Session
        s = requests.session()
        #在此Session基础上访问数据
        r = s.post(url, params=keyvalue, headers=headers)
        keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
        r = s.get(url, params=keyvalue, headers=headers)
        js=r.json()
        self.requ_get=js["returndata"]["datanodes"]
    #提取返回数据中所需的数据
    def data_tract(self):
        #重新建立数据结构
        for year in range(1999,2019):
            self.datadict[str(year)]={}
        for node in self.requ_get:
            self.datadict[node["wds"][1]["valuecode"]][node["wds"]
                          [0]["valuecode"]]=node["data"]["data"]
    #将数据写入数据库    
    def data_write(self):
        #写入数据库
        self.conn = sqlite3.connect('dbfirst.db')
        self.c = self.conn.cursor()
        #建立表
        self.c.execute('''CREATE TABLE DATA
           (YEAR INT PRIMARY KEY    NOT NULL,
           TOTAL         INT        NOT NULL,
           MALE          INT        NOT NULL,
           FEMALE        INT,
           URBAN         INT,
           RURAL         INT);''')
        #写入表
        for year in self.datadict:
            single=self.datadict[year]
            #格式化写入
            self.c.execute("INSERT INTO DATA VALUES(?,?,?,?,?,?)",\
              (int(year), single["A030101"],single["A030102"],\
               single["A030103"],single["A030104"],single["A030105"]));
        #提交修改
        self.conn.commit()
        #关闭文件
        self.conn.close()
#读取数据并绘图        
class Plot_op:
    #初始化
    def __init__(self):
        #存储数据的列表
        self.datadict={}
        self.yearlist=[]
        self.totallist=[]
        self.malelist=[]
        self.femalelist=[]
        self.n_groups = 20
        self.data_read()
        self.total_plot()
        self.gender_plot()
    #读取数据
    def data_read(self):
        
        self.conn = sqlite3.connect('dbfirst.db')
        self.c = self.conn.cursor()
        cursor = self.c.execute("SELECT year,total,male,"\
                                "female,urban,rural from DATA")
        #从表中读取数据
        for row in cursor:
            self.datadict[row[0]]={"total":row[1],"male":row[2],
                         "female":row[3],"urban":row[4],"rural":row[5]}
            self.yearlist.append(row[0])
            self.totallist.append(row[1])
            #处理数据为比例
            self.malelist.append(100*row[2]/row[1])
            self.femalelist.append(100*row[3]/row[1])
        self.conn.close()
    #总人口变化图    
    def total_plot(self):
        #由于作图方式都类似，故重复操作只作一次注释
        #定义axes
        fig, ax = plt.subplots()
        index = np.arange(self.n_groups)
        width = 0.7#柱宽
        opacity =0.7#颜色透明度
        #条形图传递参数
        rects = ax.bar(index, tuple(self.totallist), width,
                        alpha=opacity, color='g',
                        label='总人口',)
        #设置标签，字体大小
        ax.set_xlabel('年份（年）',fontsize=15)
        ax.set_ylabel('总人口（万人）',fontsize=15)
        #设置题目
        ax.set_title('1999-2018年全国总人口数目条形图',fontsize=25)
        #x轴数值
        ax.set_xticks(index)
        ax.set_xticklabels(self.yearlist)
        ax.legend()
        #设置图片大小
        fig.set_size_inches(15, 7)
        #用来正常显示中文标签
        plt.rcParams['font.sans-serif']=['SimHei']
        #用来正常显示负号
        plt.rcParams['axes.unicode_minus']=False 
        #设置y轴区间
        plt.ylim([125000,145000])
        #设置网格
        plt.grid(True)
        #可保存生成图片
        fig.savefig('total_1.png', dpi=100)
        plt.show()
    #性别比例绘图
    def gender_plot(self):
        
        index = np.arange(self.n_groups)
        fig, ax = plt.subplots()
        #设置标签
        ax.set_xlabel('年份（年）',fontsize=15)
        ax.set_ylabel('比例（%）',fontsize=15)
        ax.set_title('1999-2018年全国男女人口占比',fontsize=25)
        ax.set_xticks(index )
        ax.set_xticklabels(self.yearlist)

        fig.set_size_inches(15, 7)
        plt.rcParams['font.sans-serif']=['SimHei'] 
        plt.rcParams['axes.unicode_minus']=False
        #折线图传参数
        plt.plot(index,self.malelist,color='blue', linestyle='-', \
                 linewidth=3, marker='x', markersize=8,label='男性人口占比')
        plt.plot(index,self.femalelist,color='red', linestyle='-',\
                 linewidth=3, marker='o', markersize=8,label='女性人口占比')
        plt.grid(True)
        plt.ylim([48,52])
        ax.legend()
        fig.savefig('gender_1.png', dpi=100)
        plt.show()

if __name__ == '__main__':
    
    data=Data_op()
    plot=Plot_op()
