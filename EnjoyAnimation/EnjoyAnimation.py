from nonebot import on_keyword,on_command,require,get_driver,get_bot
from nonebot.adapters.onebot.v11 import ActionFailed,Message,MessageSegment,Bot,MessageEvent
from nonebot.params import Arg,CommandArg
from nonebot.matcher import Matcher
import requests,os,json,random,sqlite3,isodate
from .QBsimpleAPI import *
from .classes import *
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from lxml import html,etree

def get_animation_infors():
    '''通过api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
    }
    onair_json=json.loads(requests.get(url=onair,headers=header).text)["items"]
    site_json=json.loads(requests.get(url=site,headers=header).text)
    animation_db=db_lite("test.db")
    for i in onair_json:
        names=[item for sublist in i["titleTranslate"].values() for item in sublist]+[i["title"]]
        official=i["officialSite"]
        start_date=isotime_format(i["begin"]).datatime_operation("add","hours",8)
        try:
            JP_start_date_UTC8=isotime_format(i["broadcast"]).datatime_operation("add","hours",8)
        except KeyError:
            JP_start_date_UTC8=None
        end_date=[i["end"] if i["end"] != "" else None][0]
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
            end_date=end_date,
            urls=urls
        )
        
get_animation_infors()
