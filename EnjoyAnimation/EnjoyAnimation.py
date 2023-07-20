import requests,os,json,random,sqlite3,difflib #requests
from bs4 import BeautifulSoup   #bs4
from datetime import datetime,timedelta
from lxml import html,etree #lxml

from .QBsimpleAPI import *
from .schedule_lite import timetable
from .classes import *
from .schedule_lite import *
from .variable import (
    dirver,
    month,
    header,
    animation_path,
    animation_pic_path,
    enjoy_log
)

@timetable.add_job("fixed","1w0h5m30s",233,True)
async def get_animation_infors():
    '''通过bgm api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    animation_db=db_lite(animation_path)
    onair_json=json.loads(requests.get(url=onair,headers=header,timeout=10).text)["items"]
    site_json=json.loads(requests.get(url=site,headers=header,timeout=10).text)
    enjoy_log.info("Animation database Updating......")
    for i in onair_json:
        # names=[item for sublist in i["titleTranslate"].values() for item in sublist]+[i["title"]]
        names=[]
        try:
            names+=[item for item in i["titleTranslate"]["zh-Hans"]]
        except:...
        try:
            names+=[item for item in i["titleTranslate"]["zh-Hans"]]
        except:...
        names+=[item for subkey in i["titleTranslate"].keys() if subkey not in ["zh-Hans","zh-Hant"] for item in i["titleTranslate"][subkey]]+[i["title"]]
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
        status=str(datetime.now())[:-7]
        animation_db.testafter_insert_db(
            names=names,
            pic_path=None,
            video_path=None,
            start_date=start_date,
            JP_start_date_UTC8=JP_start_date_UTC8,
            CN_start_date=CN_start_date,
            official=official,
            status=status,
            urls=urls
        )
    enjoy_log.info("Animation database bgmlist Completes")
    await yuc_wiki_infors(animation_db)
    enjoy_log.info("Animation database yuc_wike Completes")

def testfor_lastweek(timestr:str)->bool:
    '''检测时间是否来自不属于本周'''
    time_datetime=datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S")
    now=datetime.now()
    now_week=now.weekday()
    if now_week==0:
        now_week=8
    week_1=now-timedelta(days=now_week)
    if time_datetime.strftime("%Y-%m-%d %H:%M:%S") < week_1.strftime("%Y-%m-%d %H:%M:%S"):
        return True
    else:
        return False
    
async def yuc_wiki_infors(animation_db:db_lite):
    '''yuc_wiki网站的信息爬取整合''' 
    now=datetime.now()
    yuc_url=f"https://yuc.wiki/{now.year}{month[now.month-1]}/"
    yuc_text=requests.get(url=yuc_url,headers=header,timeout=10).text
    yuc_items=html.fromstring(yuc_text)
    yuc_list=yuc_items.xpath('//div[@style="float:left"]/div[@class="div_date" or @class="div_date_"]')
    for i in yuc_list:
        yuc_name="".join(i.xpath('..//td[@class="date_title" or @class="date_title_" or @class="date_title__"]//text()'))
        yuc_name=re.sub(r'Part.\d',"",yuc_name).replace("/","_")
        yuc_pic_url="".join(i.xpath('.//img/@src')).replace(" ","")
        yuc_pic_path=os.path.join(animation_pic_path,f"{yuc_name}.jpg")
        if not os.path.isfile(yuc_pic_path):
            with open(yuc_pic_path,"xb") as xb:
                xb.write(requests.get(url=yuc_pic_url,headers=header,timeout=10).content)
        time_1=("".join(i.xpath('./p[@class="imgtext" or @class="imgtext2"]/text()')))[:-1]
        time_2=("".join(i.xpath('./p[@class="imgep"]/text()'))).replace(" ","")[:-1].split(":")
        if time_1:
            time_a=datetime.strptime(f"{now.year}-{time_1}","%Y-%m/%d")
            time_a=time_a+timedelta(days=int(time_2[0])//24,hours=int(time_2[0])%24,minutes=int(time_2[1]))
            time_a=str(time_a)
        else:
            time_a=None
        urls=i.xpath('..//a/@href')
        animation_db.testafter_insert_db(
            names=[yuc_name],
            pic_path=yuc_pic_path,
            urls=urls,
            start_date=time_a
        )