import requests,os,json,random,sqlite3,difflib #requests
from bs4 import BeautifulSoup   #bs4
from datetime import datetime,timedelta
from lxml import html,etree #lxml

from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment,MessageEvent,Message
from .classes import *
from .schedule_lite import *
from .html_render import *
from .variable import (
    text_img_path,
    month,
    header,
    animation_path,
    animation_pic_path,
    enjoy_log,
    ani_config,
    debug_path
)

animation_db=db_lite(animation_path)

@timetable.add_job("fixed","1w0h5m30s",233,True)
async def get_animation_infors():
    '''通过bgm api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    onair_get=requests.get(url=onair,headers=header,timeout=10)
    onair_json=json.loads(onair_get.text)["items"]
    site_get=requests.get(url=site,headers=header,timeout=10)
    site_json=json.loads(site_get.text)
    enjoy_log.info("Animation database Updating......")
    try:
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
                start_date=start_date,
                JP_start_date_UTC8=JP_start_date_UTC8,
                CN_start_date=CN_start_date,
                official=official,
                status=status,
                urls=urls
            )
        enjoy_log.info("Animation database bgmlist Completes")
    except AttributeError as attr:
        now_time=str(datetime.now())[:-16]
        onair_json_path=os.path.join(debug_path,f'yuc_onair_{now_time}.json')
        site_json_path=os.path.join(debug_path,f'yuc_site_{now_time}.json')
        enjoy_log.error(f"Animation database bgmlist error !!! \
                        \nURL_1={onair} \
                        \nURL_2={site}\nerror:{attr} \
                        \nfile_1:{onair_json_path} \
                        \nfile_2:{site_json_path}")
        json_files(onair_json_path).write(onair_json)
        json_files(site_json_path).write(site_json)
    await yuc_wiki_infors(animation_db)
    
    
async def yuc_wiki_infors(animation_db:db_lite):
    '''yuc_wiki网站的信息爬取整合''' 
    now=datetime.now()
    yuc_url=f"https://yuc.wiki/{now.year}{month[now.month-1]}/"
    yuc_text=requests.get(url=yuc_url,headers=header,timeout=10).text
    yuc_items=html.fromstring(yuc_text)
    try:
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
        enjoy_log.info("Animation database yuc_wike Completes")
    except AttributeError:
        enjoy_log.error(f"Animation database yuc_wike error !!! \nURL：{yuc_url}")
        
async def return_message(message:str,event:MessageEvent) ->str | Message:
    '''在qq上返回消息，读取配置分别返回消息（图片或者str）'''
    re_msg=None
    if ani_config.re_type_img and message:
        await text_to_img(message)
    if event.sub_type=="friend":
        if ani_config.re_type_img and message:
            '''好友消息，图片'''
            re_msg=Message(MessageSegment.image(file=f"file:///{text_img_path}"))
        else:
            '''好友消息，文字'''
            re_msg=message
    elif event.sub_type=="normal":
        if ani_config.need_to:
            re_msg=MessageSegment.reply(event.message_id)
            if ani_config.need_at:
                re_msg+=MessageSegment.at(event.user_id)
        if ani_config.need_at:
            re_msg+=MessageSegment.at(event.user_id)
        if ani_config.re_type_img and message:
            re_msg+=MessageSegment.image(file=f"file:///{text_img_path}")
        else:
            re_msg+=MessageSegment.text(message)
    else:
        enjoy_log.debug(f"other person message{event.message_id}=={event.user_id}:{event.message}")
    return re_msg
        
def find_animation_id(tmp_str:str)->list[int]:
    '''寻找番剧id列表'''
    anime_id_list=animation_db.universal_select_db("names","relation","name",f"%{tmp_str}%")
    if anime_id_list:
        return anime_id_list
    return False

def insert_qq_anime(qq_id:int,anime_id:int):
    '''在数据库中插入订阅信息''' 
    tmp_data={
        "qq_id":qq_id,
        "anime_relation":anime_id
    }
    if not animation_db.universal_select_db("user_subscriptions","qq_id",f"qq_id={qq_id} and anime_relation={anime_id}"):
        animation_db.universal_insert_db(table="user_subscriptions",**tmp_data)

