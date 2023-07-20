from .EnjoyAnimation import *
from .index import *
from nonebot.permission import SUPERUSER
from .html_render import text_to_img
from .variable import (
    dirver,
    month,
    animation_path,
    animation_pic_path
)
from nonebot.adapters.onebot.v11 import (
    MessageEvent
)
from nonebot import (
    on_keyword,
    on_command
)

animation_db=db_lite(animation_path)
animation_info=on_command(cmd="本季番剧",aliases=set("番剧信息"))
anime_time_list=[]

@animation_info.handle()
async def animation_info_func(event:MessageEvent):
    re_message=""
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    anime_time_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}')")
    for i,id in enumerate(anime_time_list):
        anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
        re_message+=f"{i+1},{anime_name}\n"
    await text_to_img(re_message)
    