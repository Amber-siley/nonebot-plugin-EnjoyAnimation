import requests,os,json,random,sqlite3 #requests
from bs4 import BeautifulSoup   #bs4
from datetime import datetime,timedelta
from lxml import html,etree #lxml
import logging

from nonebot.log import logger

from .QBsimpleAPI import *
from .schedule_lite import timetable
from .classes import *
from .schedule_lite import *
from .variable import (
    dirver,
    header,
    work_path,
    animation_path,
    pic_path,
    plugin_file_path,
    enjoy_log
)

@timetable.add_job("fixed","1w0h0m30s",233,True)
async def get_animation_infors():
    '''通过bgm api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    onair_json=json.loads(requests.get(url=onair,headers=header).text)["items"]
    site_json=json.loads(requests.get(url=site,headers=header).text)
    animation_db=db_lite(animation_path)
    for i in onair_json:
        names=[item for sublist in i["titleTranslate"].values() for item in sublist]+[i["title"]]
        official=i["officialSite"]
        start_date=isotime_format(i["begin"]).datetime_operation("add","hours",8)
        try:
            JP_start_date_UTC8=isotime_format(i["broadcast"]).datetime_operation("add","hours",8)
        except KeyError:
            JP_start_date_UTC8=None
        urls,CN_start_date=[],[]
        for item in i["sites"]:
            urls.append(f"{site_json[item['site']]['urlTemplate']}".replace("{{id}}",f"{item['id']}"))
            try:
                if item["broadcast"]!="":
                    CN_start_date.append(isotime_format(item["broadcast"]).datetime_operation("add","hours",8))
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
            status=None,
            urls=urls
        )

def yuc_wiki_infors():
    '''yuc_wiki网站的信息爬取整合''' 
    