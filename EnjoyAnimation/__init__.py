from .EnjoyAnimation import *
from .index import *
from .QBsimpleAPI import *
from .variable import (
    month,
    animation_path,
    yes_list,
    random_list
)

from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message
)
from nonebot import (
    on_keyword,
    on_command,
)
from nonebot.params import CommandArg,ArgPlainText

animation_db=db_lite(animation_path)
animation_info=on_command(cmd="本季番剧",aliases={"番剧信息"})
animation_update=on_command(cmd="番剧更新",aliases={'更新番剧'},permission=SUPERUSER)
today_update=on_command(cmd="今日更新")
animation_inqurie=on_command("番剧查询",aliases={"查询番剧"})
subscribe_animation=on_command(cmd="订阅番剧")


@animation_info.handle()
async def animation_info_func(event:MessageEvent):
    '''番剧信息返回本季番剧列表'''
    re_message=""
    now=str(datetime.strptime(f"{datetime.now().year}-{month[datetime.now().month-1]}","%Y-%m").strftime("%Y-%m-%d %H:%M:%S"))
    '''当前季度最低时间'''
    anime_id_list=animation_db.universal_select_db("animations","id",f"datetime(start_date)>=datetime('{now}')")
    for i,id in enumerate(anime_id_list):
        anime_name=animation_db.universal_select_db("names","name",f"relation={id}",order="row_id")[0]
        re_message+=f"{i+1}，{anime_name}\n"
    re_message="本季番剧\n"+re_message
    await animation_info.finish(await return_message(re_message,event))
    
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
    await today_update.finish(await return_message(re_message,event))

@animation_inqurie.handle()
async def animation_inqurie_func(event:MessageEvent,args:Message=CommandArg()):
    '''番剧查询，名字查询，触发具体番剧后update番剧的description，无图片的会尝试爬取图片'''
    if other:=args.extract_plain_text():
        if anime_id_list:=animation_db.universal_select_db("names","relation","name",f"%{other}%"):
            if all(i == anime_id_list[0] for i in anime_id_list):
                #确定返回的id列表中答案唯一，若不唯一则存在冲突
                target_id=anime_id_list[0]
                anime_name=animation_db.universal_select_db("names","name",f"relation={target_id}")[0]
                if anime_infor:=animation_db.universal_select_db("animations",("pic_path","start_date"),f"id={target_id}")[0]:
                    ...
                    

@subscribe_animation.handle()
async def subscribe_animation_func(event:MessageEvent,state:T_State,args:Message=CommandArg()):
    '''番剧订阅'''
    if other:=args.extract_plain_text():
        anime_id_tmp=find_animation_id(other)
        re_msg=""
        if anime_id_tmp:
            if len(anime_id_tmp)==1:
                insert_qq_anime(qq_id=event.user_id,anime_id=anime_id_tmp[0])
                ...
                await subscribe_animation.finish()
            else:
                for item_index,id in enumerate(anime_id_tmp):
                    anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
                    re_msg+=f"{item_index+1}，{anime_name}\n"
                re_msg="检索内容似乎冲突了😊，请选择订阅编号：（输入非数字退出）\n"+re_msg
                state["anime_id_list"]=anime_id_tmp
                await subscribe_animation.send(await return_message(re_msg,event))

@subscribe_animation.got(key="number")
async def subscribe_animation_chooice_func(event:MessageEvent,state:T_State,args:str=ArgPlainText("number")):
    '''番剧订阅 选择'''
    if args.isdigit():
        if other:=int(args):
            if int(other)<=len(state["anime_id_list"]):
                insert_qq_anime(qq_id=event.user_id,anime_id=state["anime_id_list"][int(other)-1])
                ...
            await subscribe_animation.finish()
