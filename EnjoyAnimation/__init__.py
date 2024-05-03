from .EnjoyAnimation import *
from .index import *
from .QBsimpleAPI import *
from .variable import (
    month,
    animation_path,
    yes_list,
    video_path,
    random_list,
    anime_user_help_txt,
    anime_admin_help_txt,
    config,
    datetime_week
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
qbit=login_qb(ani_config.qbit_port,ani_config.qbit_admin,ani_config.qbit_pw)
animation_info=on_command(cmd="本季番剧",aliases={"番剧信息"})
animation_update=on_command(cmd="番剧更新",aliases={'更新番剧'},permission=SUPERUSER)
today_update=on_command(cmd="今日更新")
animation_inqurie=on_command("番剧查询",aliases={"查询番剧"})
subscribe_animation=on_command(cmd="订阅番剧",aliases={"番剧订阅"})
anime_help=on_command(cmd="番剧帮助")
select_sub_animes=on_command(cmd="我的追番",aliases={"我的订阅"})
unsub_animes = on_command(cmd="取消追番",aliases={"取消订阅"})
sreach_anime_configs=on_command(cmd="debug番剧配置项")

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
    re_message=f"今日更新:【{datetime_week[datetime.now().weekday()]}】\n"+re_message
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
                    pic_path,start_date=anime_infor[0],anime_infor[1]
                    start_date=dlite(start_date).cn_date()
                    re_msg=MessageSegment.image(file=f"file:///{pic_path}")
                    await animation_inqurie.finish(message=Message(await return_message(None,event)+f"{anime_name} 于{start_date} 首播\n"+re_msg))
                    
                    

@subscribe_animation.handle()
async def subscribe_animation_func(event:MessageEvent,state:T_State,args:Message=CommandArg()):
    '''番剧订阅'''
    if other:=args.extract_plain_text():
        anime_id_tmp=find_animation_id(other)
        re_msg=""
        if anime_id_tmp:
            if len(anime_id_tmp)==1:
                anime_name=animation_db.universal_select_db("names","name",f"relation={anime_id_tmp[0]}")[0]
                insert_qq_anime(qq_id=event.user_id,anime_id=anime_id_tmp[0])
                anime_work_path=os.path.join(video_path,anime_name)
                os.makedirs(anime_work_path,exist_ok=True)
                qbit.cn_add_rss(ani_config.dl_url[0],anime_name)
                #未连接qbit时会添加到tmp.json中，暂时放置
                re_msg=f"动漫 {anime_name} 已添加进追番列表"
                if anime_path:=animation_db.universal_select_db("animations","pic_path",f"id={anime_id_tmp[0]}")[0]:
                    re_msg=Message(re_msg+MessageSegment.image(file=f"file:///{anime_path}"))
                await subscribe_animation.finish(re_msg)
            else:
                for item_index,id in enumerate(anime_id_tmp):
                    anime_name=animation_db.universal_select_db("names","name",f"relation={id}")[0]
                    re_msg+=f"{item_index+1}，{anime_name}\n"
                re_msg="检索内容似乎冲突了😊，请选择订阅编号：（输入非数字退出）\n"+re_msg
                state["anime_id_list"]=anime_id_tmp
                await subscribe_animation.send(await return_message(re_msg,event))

@subscribe_animation.got(key="number")
async def subscribe_animation_chooice_func(event:MessageEvent,state:T_State,args:str=ArgPlainText("number")):
    '''番剧订阅_选择'''
    if args.isdigit():
        if other:=int(args):
            if int(other)<=len(state["anime_id_list"]):
                insert_qq_anime(qq_id=event.user_id,anime_id=state["anime_id_list"][int(other)-1])
                ...
            await subscribe_animation.finish()



@anime_help.handle()
async def anime_help_func(event:MessageEvent):
    '''番剧帮助'''
    if str(event.user_id) in config.superusers:
        await anime_help.finish(await return_message(anime_admin_help_txt,event))
    else:
        await anime_help.finish(await return_message(anime_user_help_txt,event))

@select_sub_animes.handle()
async def select_sub_anime_func(event:MessageEvent):
    '''我的追番，获取用户订阅的番剧'''
    id = event.user_id
    datas = user_subanime(id)
    re_msg = ""
    for index,data in enumerate(datas):
        re_msg += f"{index+1}，{data}\n"
    if msg := await return_message(re_msg,event):
        await select_sub_animes.finish(Message("您的订阅番剧如下：\n"+msg))
    await select_sub_animes.finish("您还没有没有订阅番剧哟🤔")
    
@unsub_animes.handle()
async def unsub_animes_func(match:Matcher,event:MessageEvent,args:Message=CommandArg()):
    '''取消追番'''
    if args.extract_plain_text():
        match.set_arg(key="unsub_num",message=args)
    id = event.user_id
    anime_names = user_subanime(id)
    if len(anime_names) == 0:
        await unsub_animes.finish("您还没有没有订阅番剧哟😐")
    await unsub_animes.send(await return_message("".join([f"{index+1}，{name}\n" for index,name in enumerate(user_subanime(id))]),event))
    
@unsub_animes.got(key="unsub_num",prompt="请选择番剧编号")
async def unsub_animes_got_func(event:MessageEvent,args:Message | str=ArgPlainText("unsub_num")):
    '''取消追番——选择'''
    id = event.user_id
    locked = True
    num_error = False
    excute_bit = False
    anime_names = user_subanime(id)
    animes_msg = await return_message("".join([f"{index+1}，{name}\n" for index,name in enumerate(anime_names)]),event)
    if args in ["all","All"]:
        animation_db.universal_delete_db("user_subscriptions",f"qq_id={id}")
    if args == "dd":
        await unsub_animes.finish(random_list(yes_list))
    else:
        ids = args.split(" ")
        sub_anime_ids = animation_db.universal_select_db("user_subscriptions","anime_relation",f"qq_id={id}")
        for i in ids:
            if i.isdigit():
                try:
                    animation_db.universal_delete_db("user_subscriptions",f"qq_id={id} and anime_relation={sub_anime_ids[int(i)-1]}")
                    excute_bit = True
                except IndexError:
                    num_error = True
                locked = False
        if locked or num_error and not excute_bit:
            await unsub_animes.reject("请输入合法数字编号哦😘，请重新输入，或者输入dd退出\n"+animes_msg)
    await unsub_animes.send(Message("已取消订阅番剧，正在订阅的番剧如下\n"+await return_message("".join([f"{index+1}，{name}\n" for index,name in enumerate(user_subanime(id))]),event)))