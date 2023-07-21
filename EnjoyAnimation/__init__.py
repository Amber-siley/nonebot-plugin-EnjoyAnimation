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
)
from nonebot import (
    on_keyword,
    on_command
)
from nonebot.matcher import Matcher

animation_db=db_lite(animation_path)
animation_info=on_command(cmd="本季番剧",aliases=set("番剧信息"))
anime_time_list=[]
animation_update=on_command(cmd="番剧更新",aliases=set('更新番剧'),permission=SUPERUSER)



@animation_info.handle()
async def animation_info_func(event:MessageEvent):
    '''番剧信息返回本季番剧列表'''
    re_message=""
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    anime_time_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}')")
    for i,id in enumerate(anime_time_list):
        anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
        re_message+=f"{i+1}，{anime_name}\n"
    re_message="本季番剧\n"+re_message
    await return_message(re_message,animation_info,event)
    await animation_info.finish()
    
@animation_update.handle()
async def animation_update_func(event:MessageEvent):
    timetable.remove_task(task_id=233)
    timetable.add_job("fixed","1w0h5m30s",233,True)(get_animation_infors)
    await animation_update.finish(random_list(yes_list))