from nonebot import on_keyword,on_command,require,get_driver,get_bot
from nonebot.adapters.onebot.v11 import ActionFailed,Message,MessageSegment,Bot,MessageEvent
from nonebot.params import Arg,CommandArg
from nonebot.matcher import Matcher
import requests,os,json,random,sqlite3 #
from bs4 import BeautifulSoup   #
from datetime import datetime,timedelta
from lxml import html,etree #
from .QBsimpleAPI import *
from .classes import *
from .schedute_lite import *
from .variable import (
    header,
    work_path,
    animation_path,
    pic_path,
    plugin_file_path
)

def get_animation_infors():
    '''通过api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    onair_json=json.loads(requests.get(url=onair,headers=header).text)["items"]
    site_json=json.loads(requests.get(url=site,headers=header).text)
    animation_db=db_lite(animation_path)
    for i in onair_json:
        names=[item for sublist in i["titleTranslate"].values() for item in sublist]+[i["title"]]
        official=i["officialSite"]
        start_date=isotime_format(i["begin"]).datatime_operation("add","hours",8)
        try:
            JP_start_date_UTC8=isotime_format(i["broadcast"]).datatime_operation("add","hours",8)
        except KeyError:
            JP_start_date_UTC8=None
        # end_date=[i["end"] if i["end"] != "" else None][0]
        urls,CN_start_date=[],[]
        for item in i["sites"]:
            urls.append(f"{site_json[item['site']]['urlTemplate']}".replace("{{id}}",f"{item['id']}"))
            try:
                if item["broadcast"]!="":
                    CN_start_date.append(isotime_format(item["broadcast"]).datatime_operation("add","hours",8))
            except (KeyError,ValueError):
                ...
        if CN_start_date:
            CN_start_date.sort()
            CN_start_date=CN_start_date[0]
        else:
            CN_start_date=None
        animation_db.testafter_insert_db(
            names=names,
            path="tmp",
            start_date=start_date,
            JP_start_date_UTC8=JP_start_date_UTC8,
            CN_start_date=CN_start_date,
            official=official,
            # end_tag=end_date,
            urls=urls
        )

def yuc_wiki_infors():
    '''yuc_wiki网站的信息爬取整合''' 
    
    ...
def dir_ready():
    '''文件目录创建'''
    os.makedirs(work_path,exist_ok=True)
    os.makedirs(pic_path,exist_ok=True)
    os.makedirs(plugin_file_path,exist_ok=True)

def bot_start_function():
    '''插件初始化函数'''
    dir_ready()
    get_animation_infors()

bot_start_function()