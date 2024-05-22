import requests,os,json
from datetime import datetime
from lxml import html,etree #lxml

from nonebot.adapters.onebot.v11 import MessageSegment,MessageEvent,Message
from .classes import *
from .schedule_lite import *
from .html_render import *
from .QBsimpleAPI import login_qb
from .variable import (
    text_img_path,
    month,
    header,
    animation_path,
    animation_pic_path,
    enjoy_log,
    ani_config,
    debug_path,
    video_path
)

animation_db=db_lite(animation_path)
qbit=login_qb(ani_config.qbit_port,ani_config.qbit_admin,ani_config.qbit_pw)

#后台入口
@timetable.add_job("fixed","1w0h5m30s",233,True)
async def background_main():
    #animations information
    await get_animation_infors()
    await yuc_wiki_infors()

    #connect qb & db
    try:
        timetable.remove_task(8787)
    except IndexError:
        ...
    finally:
        @timetable.add_job("interval","5m",task_id=8787,first_run=True)
        def _():
            db_connect_qb.set_subcription_rss()
            db_connect_qb.rss_set_dl_task()
    
async def get_animation_infors():
    '''通过bgm api获取动漫信息并放入数据库'''
    onair="https://bgmlist.com/api/v1/bangumi/onair"
    site="https://bgmlist.com/api/v1/bangumi/site"
    onair_get=requests.get(url=onair,headers=header,timeout=10)
    onair_json=json.loads(onair_get.text)["items"]
    site_get=requests.get(url=site,headers=header,timeout=10)
    site_json=json.loads(site_get.text)
    enjoy_log.info("Animation database Updating......")
    if ani_config.debug_mode:
        now_time=str(datetime.now())[:-16]
        onair_json_path=os.path.join(debug_path,f'bgm_onair_{now_time}.json')
        site_json_path=os.path.join(debug_path,f'bgm_site_{now_time}.json')
        json_files(onair_json_path).write(onair_json)
        json_files(site_json_path).write(site_json)
    try:
        for i in onair_json:
            # names=[item for sublist in i["titleTranslate"].values() for item in sublist]+[i["title"]]
            names=[]
            try:
                names+=[item for item in i["titleTranslate"]["zh-Hans"]]
            except:...
            try:
                names+=[item for item in i["titleTranslate"]["zh-Hant"]]
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
            
            #加判断
            lock,__lock = False,True
            
            for name in names:
                if relations := animation_db.universal_select_db("names","relation",f'''name="{name}"'''):
                    if __lock:
                        id = relations[0]
                    lock = True
                    __Lock = False
            
            
            #通过names判断是否存在数据库中
            if lock:
                #存在于数据库中
                animation_db.update_animation_info_db(
                    id=id,
                    names=names,
                    start_date=start_date,
                    JP_start_date_UTC8=JP_start_date_UTC8,
                    CN_start_date=CN_start_date,
                    official=official,
                    froms="bgm",
                    status=status,
                )
            else:
                #不存在于数据库中
                animation_db.insert_animation_info_db(
                    names=names,
                    start_date=start_date,
                    JP_start_date_UTC8=JP_start_date_UTC8,
                    CN_start_date=CN_start_date,
                    official=official,
                    froms="bgm",
                    status=status,
                    urls=urls
                )
        enjoy_log.info("Animation database bgmlist Completes")
    except AttributeError as attr:
        now_time=str(datetime.now())[:-16]
        onair_json_path=os.path.join(debug_path,f'bgm_onair_{now_time}.json')
        site_json_path=os.path.join(debug_path,f'bgm_site_{now_time}.json')
        enjoy_log.error(f"Animation database bgmlist error !!! \
                        \nURL_1={onair} \
                        \nURL_2={site}\nerror:{attr}{i} \
                        \nfile_1:{onair_json_path} \
                        \nfile_2:{site_json_path}")
        json_files(onair_json_path).write(onair_json)
        json_files(site_json_path).write(site_json)
    
async def yuc_wiki_infors():
    '''yuc_wiki网站的信息爬取整合 对bgm信息爬取的完善，不补充不存在的信息''' 
    now=datetime.now()
    yuc_url=f"https://yuc.wiki/{now.year}{month[now.month-1]}/"
    yuc_text=requests.get(url=yuc_url,headers=header,timeout=10).text
    yuc_items=html.fromstring(yuc_text)
    status=str(datetime.now())[:-7]
    try:
        pic_urls = yuc_items.xpath("//div[@style='float:left']/img/@src")
        title_cns_items = yuc_items.xpath("//td[@class='title_main_r']/p[@class='title_cn_r' or @class='title_cn_r3' or @class='title_cn_r2' or @class='title_cn_r1']")
        title_cns = [i.xpath('string()') for i in title_cns_items]
        title_jps_items = yuc_items.xpath("//td[@class='title_main_r']/p[@class='title_jp_r' or @class='title_jp_r3' or @class='title_jp_r2' or @class='title_jp_r1']")
        title_jps = [i.xpath('string()') for i in title_jps_items]
        pvs = yuc_items.xpath("//td[@class='link_a_r']/a[last()]/@href")
        anime_types_items = yuc_items.xpath("//td[@class='type_c_r' or @class='type_a_r' or @class='type_b_r' or @class='type_d_r' or @class='type_e_r' or @class='type_e_r1']")
        anime_types = [i.xpath("string()") for i in anime_types_items]
        anime_tags_items = yuc_items.xpath("//td[@class='type_tag_r' or @class='type_tag_r1']")
        anime_tags = [i.xpath("string()") for i in anime_tags_items]
        anime_episodes_items = yuc_items.xpath("//p[@class='broadcast_ex_r']")
        anime_episodes =  [i.xpath("string()") for i in anime_episodes_items]
        
        if len(pic_urls) == len(title_cns) == len(title_jps) == len(pvs) == \
            len(anime_types) == len(anime_tags) == len(anime_episodes):
            for index in range(len(pic_urls)):
                cns = title_cns[index].split(" / ")
                jps = title_jps[index].split(" / ")
                names = cns + jps
                
                if num:=animation_db.name_ratio(names):
                    #get picture
                    pic_path = os.path.join(animation_pic_path,f"{names[0]}.png")
                    if not os.path.isfile(pic_path):
                        with open(pic_path,"xb") as xb:
                            xb.write(requests.get(url=pic_urls[index],headers=header,timeout=10).content)
                        
                    #更新动漫信息
                    animation_db.update_animation_info_db(
                        id = num,
                        names=names,
                        pic_path=pic_path,
                        status=status,
                        pv = pvs[index],
                        anime_typetag = anime_tags[index],
                        anime_type = anime_types[index],
                        froms = "yuc",
                        episodes=anime_episodes[index]
                    )
                else:
                    #未找到别称
                    enjoy_log.debug(f"{names}未找到别称")
            enjoy_log.info("Animation database yucwiki Completes")
        else:
            enjoy_log.error(f"Animation database yuc_wike error !!! \nURL：{yuc_url} (可以反馈给开发者哦)")
        
    except AttributeError:
        enjoy_log.error(f"Animation database yuc_wike error !!! \nURL：{yuc_url}")
        
async def return_message(message:str,event:MessageEvent) ->str | Message:
    '''在qq上返回消息，读取配置分别返回消息（图片或者str）,返回消息段，需要使用send进行消息发送'''
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
        if ani_config.re_type_img and message:
            re_msg+=MessageSegment.image(file=f"file:///{text_img_path}")
        else:
            re_msg+=MessageSegment.text(message)
    else:
        enjoy_log.debug(f"other person message{event.message_id}=={event.user_id}:{event.message}")
    return re_msg if re_msg is not None else ""
        
def find_animation_id(tmp_str:str)->list[int]:
    '''使用缺省搜索寻找番剧id列表'''
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

def user_subanime(id) -> list[str]:
    '''通过qqid获取订阅的番剧名称列表'''
    re_data = []
    sub_anime_ids = animation_db.universal_select_db("user_subscriptions","anime_relation",f"qq_id={id}")
    for _id in sub_anime_ids:
        anime_name = animation_db.universal_select_db("names","name",f"relation={_id}")[0]
        re_data.append(anime_name)
    return re_data

def use_num_select_animeID(num:str) -> list[int]:
    '''使用编号字符串，其中番剧id为当前季度的番剧id，无法通过id获取往期季度的番剧'''
    num = num.split(" ")
    anime_ids = set()
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    '''当前季度最低时间'''
    anime_id_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}')")
    for i in num:
        if i.isdigit():
            anime_ids.add(anime_id_list[int(i)-1])
        else:
            tmp = animation_db.universal_select_db("names","relation","name",f"%{i}%")
            #查询数据库符合名称的id
            if len(tmp) == 1:
                #结果唯一
                anime_ids.add(tmp[0])
    return anime_ids
    
def get_nowM_animeidlist():
    '''获取当前季度返回的番剧id列表'''
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    '''当前季度最低时间'''
    anime_id_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}') and froms='yuc'")
    return anime_id_list

class db_connect_qb:
    def check() -> Callable:
        def __(func:Callable):
            def _(*args, **kwargs):
                if not qbit.ok:
                    return 0
                
                func(*args, **kwargs)
            return _
        return __
    
    @staticmethod
    @check()
    def set_subcription_rss():
        '''添加rss订阅'''
        ids = list(set(animation_db.universal_select_db("user_subscriptions","anime_relation")))
        names = [animation_db.universal_select_db("names","name",f"relation={id}")[0] for id in ids]
        for url,(proxy,cookie_p) in ani_config.bt_dl_url.items():
            for id_index,anime_name in enumerate(names):
                anime_url = qbit._chinese_url_replace_encoding(url,anime_name)
                rss_xml = etree.fromstring(requests.get(anime_url,headers=header).content)
                authors:list = rss_xml.xpath("//item/author/text()")
                titles:list = rss_xml.xpath("//item/title/text()")
                main_author = None
                for index,value in enumerate(titles):
                    jum = False
                    for dis in ani_config.rss_tags_discard:
                        if re.search(rf"{dis}",value):
                            jum = True
                            break
                    
                    if jum:
                        continue
                    
                    for tag in ani_config.rss_tags:
                        if re.search(rf"{tag}",value):
                            main_author = authors[index]
                            break
                    
                    if main_author:
                        break
                else:
                    main_author = max(authors,key=authors.count)
                anime_rss = qbit._chinese_url_replace_encoding(url,f"{anime_name}+{main_author}")
                if anime_rss not in qbit.rss_infor.rss_urls:
                    qbit.add_rss(anime_rss)
                    enjoy_log.info(f"订阅rss连接：{anime_name}+{main_author}")
                if not animation_db.universal_select_db("qbits","relation",f"qb_rssurl='{anime_rss}'"):
                    animation_db.universal_insert_db("qbits",qb_rssurl = anime_rss,relation = ids[id_index],anime_name = anime_name)
                savepath = os.path.join(video_path,anime_name).replace("\\","/")
                os.makedirs(savepath,exist_ok=True)
            break
    
    @staticmethod
    @check()
    def rss_set_dl_task():
        '''将rss订阅链接添加下载任务'''
        rss_hash_to_Turl = qbit.rss_infor.hash_to_Turl
        hash_to_rssurl = qbit.rss_infor.hash_to_rssurl
        hash_to_animename = qbit.rss_infor.hash_to_rssname
        dowload_hashs = qbit.download_info.hashs

        set_dl_hashs = []
        if not ani_config.dowload_all:
            for rss in qbit.rss_infor.rss_list:
                for item in rss.art_list:
                    jum = False
                    for dis in ani_config.rss_tags_discard:
                        if re.search(rf"{dis}",item.title):
                            jum = True
                            break
                        
                    if jum:
                        continue
                    
                    for tags in ani_config.rss_tags:
                        if re.search(rf"{tags}",item.title):
                            set_dl_hashs.append(item.hash)
                            break
        else:
            #rss订阅链接的torrent链接hash值
            set_dl_hashs = qbit.rss_infor.torrent_hashs

        if not set_dl_hashs:
            set_dl_hashs = qbit.rss_infor.torrent_hashs
        
        for i in set_dl_hashs:
            if i not in dowload_hashs:
                save_path = os.path.join(video_path,animation_db.universal_select_db("qbits","anime_name",f"qb_rssurl='{hash_to_rssurl[i]}'")[0])
    
                #该hash值不存在于下载任务中，添加下载任务
                qbit.add_download_torrent(rss_hash_to_Turl[i],save_path)
                enjoy_log.debug(f"已添加下载任务 {hash_to_animename[i]}，hash:{i}")
