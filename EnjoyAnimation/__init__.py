import re
from .EnjoyAnimation import *
from .index import *
from nonebot.permission import SUPERUSER
from .html_render import *
from .variable import (
    month,
    animation_path,
    ani_config,
    yes_list,
    random_list
)
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message
)
from nonebot import (
    on_keyword,
    on_command,
)
from nonebot.params import CommandArg

animation_db=db_lite(animation_path)
animation_info=on_command(cmd="本季番剧",aliases={"番剧信息"})
animation_update=on_command(cmd="番剧更新",aliases={'更新番剧'},permission=SUPERUSER)
today_update=on_command(cmd="今日更新")
animation_inqurie=on_command("番剧查询",aliases={"查询番剧"})



@animation_info.handle()
async def animation_info_func(event:MessageEvent):
    '''番剧信息返回本季番剧列表'''
    re_message=""
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    '''当前季度最低时间'''
    anime_id_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}')")
    for i,id in enumerate(anime_id_list):
        anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
        re_message+=f"{i+1}，{anime_name}\n"
    re_message="本季番剧\n"+re_message
    await return_message(re_message,animation_info,event)
    await animation_info.finish()
    
@animation_update.handle()
async def animation_update_func(event:MessageEvent):
    '''（管理员）强制更新数据库'''
    timetable.remove_task(task_id=233)
    timetable.add_job("fixed","1w0h5m30s",233,True)(get_animation_infors)
    await animation_update.finish(random_list(yes_list))
    
@today_update.handle()
async def today_update_func(event:MessageEvent):
    '''返回当日更新的番剧'''
    re_message=""
    anime_id_list=animation_db.universal_select_db("animations",("id","start_date"),f"datetime(status)>=datetime('{dlite.testfor_lastweek()}')")
    anime_id_list=[i[0] for i in anime_id_list if dlite(i[1]).week==datetime.now().weekday()]
    for i,id in enumerate(anime_id_list):
        anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
        re_message+=f"{i+1}，{anime_name}\n"
    re_message="今日更新\n"+re_message
    await return_message(re_message,today_update,event)
    await today_update.finish()

@animation_inqurie.handle()
async def animation_inqurie_func(event:MessageEvent,args:Message=CommandArg()):
    '''番剧查询，名字或者id查询'''
    if other:=args.extract_plain_text():
        if anime_id_list:=animation_db.universal_select_db("names","relation","name",f"%{other}%"):
            if all(i == anime_id_list[0] for i in anime_id_list):
                anime_name=animation_db.universal_select_db("names","name",f"relation={anime_id_list[0]}")[0]
                anime_infor=animation_db.universal_select_db("animations",("pic_path","start_date"),f"id={anime_id_list[0]}")
                