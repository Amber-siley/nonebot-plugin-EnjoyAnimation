from nonebot import on_keyword,on_command,require,get_driver,get_bot,require
from nonebot.adapters.onebot.v11 import ActionFailed,Message,GroupMessageEvent,Event,MessageSegment,Bot,PrivateMessageEvent,MessageEvent
from nonebot.params import Arg,CommandArg
from nonebot.matcher import Matcher
import requests,os,json,random
from bs4 import BeautifulSoup
from datetime import datetime
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import (
    text_to_pic,
)
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

plugin_version="0.0.4b0"
animation=on_command("番剧更新")
animation_infor=on_command("番剧信息")
search_number=on_command("番剧查询")
animation_help=on_command("番剧帮助")
upgrade_animation_today=on_command("今日新番")
emmmm=on_keyword(keywords=["哦哦","奥奥","呃呃"])#5bCx5L2g5pW36KGN5oiR5piv5ZCn😅
sub_drama=on_command("新增追番")
sub_sub_drama=on_command("取消追番")
sub_drama_list=on_command("我的追番")
async def admin_check(event:MessageEvent) -> bool:
    animation_config=get_driver().config
    animation_admin=animation_config.animation_admin
    return animation_admin==event.user_id
everyday_push=on_command("新增订阅")
everyday_push_off=on_command("取消订阅")
month=["01","01","01","04","04","04","07","07","07","10","10","10"]
random_face= ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '🙂', '🤗', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '🥱', '😴', '😌', '😛', '😜', '😝', '🤤','🙃','🤑','🤠','🥳','🥴','🥺','🤥','🤫','🤭','🧐',"😊","❤","😂","👍","😭","🙏","😘","🥰","😍","😊","🎉","😁","💕","🥺","😅","🔥","🙂","🥱","♥","🙄","😋","🤗","😎","🤩","😡","😴","😮‍💨","😮","😱","😨","😵‍💫","😵","😷","🤒","🤕","🤢","🤮","🤧","🥵","🥶","🥴","😵‍💫","🤠","🤡","🥳","🥸","😇","🤖","💩", "👻", "💀", "☠", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾","💋", "👋", "👌", "✌", "🤞", "🤟", "🤘", "🤙", "💪", "✊", "✋", "💅", "💍", "💄", "💋","💘","😂","😘","😍","😊","😁","😭","😜","😝","😄","😡","😀","😥","🙃","😋","👍","👌","❤","😱","🐷"]
weekday_map = {
    " ":"网络动画",
    'Monday': '周一',
    'Tuesday': '周二',
    'Wednesday': '周三',
    'Thursday': '周四',
    'Friday': '周五',
    'Saturday': '周六',
    'Sunday': '周日',
    0: '周一',
    1: '周二',
    2: '周三',
    3: '周四',
    4: '周五',
    5: '周六',
    6: '周日'
}
yuc_header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
}
animation_config=get_driver().config
animation_tmp=animation_config.animation_time
animation_default_return_img=animation_config.animation_default_return_img
animation_hour=animation_tmp[0]
animation_minute=animation_tmp[1]
work_path=os.path.join(os.getcwd(),"data")#指向data路径
pic_path=os.path.join(work_path,"Animation_pic")#指向pic路径
animation_path=os.path.join(work_path,"animations.json")#指向animation.json文件路径
User_setting_path=os.path.join(work_path,"User_setting.json")#指向user setting.json文件路径
img_tmp_path=os.path.join(pic_path,"img.jpg")#指向临时图片路径
os.makedirs(pic_path,exist_ok=True)

def animation_informtions() -> None:#爬取番剧详细信息
    with open(animation_path,"w",encoding="utf-8") as f:
        url="https://yuc.wiki/"+str(datetime.now().year)+(month[datetime.now().month-1])+"/"#拼接成当前季度番剧的查询网址
        url_html=requests.get(url=url,headers=yuc_header)
        url_txt=url_html.text
        url_structure=BeautifulSoup(url_txt,"html.parser")
        animation_all=url_structure.find_all("div",attrs={"style":"float:left"})
        classesX=["date_title","date_title_","date_title__"]
        data={}
        def animation_information(classes):
            for animation_boki in animation_all:
                try:
                    animation_name=animation_boki.find("td",attrs={"class":classes}).get_text()
                    animation_urls=animation_boki.find_all("a")
                    animation_pic_url=animation_boki.find("img")
                    animation_pic=requests.get(url=animation_pic_url["src"],headers=yuc_header)
                except AttributeError:
                    continue
                animation_href=[a["href"] for a in animation_urls]
                with open (img_tmp_path,mode="wb") as p:
                    p.write(animation_pic.content)
                try:
                    os.rename(p.name,os.path.join(pic_path,f"{animation_name}.jpg"))
                except:
                    os.remove(img_tmp_path)
                    pass
                try:
                    animation_date=str(datetime.now().year)+"/"+animation_boki.find("p",attrs={"class":"imgtext"}).get_text()[:-1]
                    animation_week=datetime.strptime(animation_date,"%Y/%m/%d").strftime("%A")
                    animation_times=animation_boki.find("p",attrs={"class":"imgep"}).get_text()[:-1]
                except  AttributeError:
                    animation_date,animation_week,animation_times=None,None,None
                    pass
                tmp=os.path.join(pic_path,f"{animation_name}.jpg")
                animation_hrefs={"urls":animation_href,
                                 "path":f"file:///{tmp}",
                                 "date":animation_date,
                                 "week":animation_week,
                                 "time":animation_times
                                 }
                data[animation_name]=(animation_hrefs)
        for classes in classesX:
            animation_information(classes) 
        json.dump(data,f,indent=4,ensure_ascii=False)
def r_animation_informations_name():#读取番剧json文本信息，读取番剧名称
    with open(animation_path,"r",encoding="utf-8") as r:
        work_r=json.load(r)
        return(work_r.keys())
def r_animation_informations_num_to_name(number:int):#通过序列号查询名字
    return str(list(r_animation_informations_name())[number-1])
def r_animation_information_path(names) ->str:#通过名称寻找路径
    with open(animation_path,"r",encoding="utf-8") as r:
        tmp=json.load(r)
        return tmp[names]["path"]
def r_animation_information_url(names) -> str:#通过名称寻找网址
    with open(animation_path,"r",encoding="utf-8") as r:
        tmp=json.load(r)
        return(tmp[names]["urls"])
def r_animation_information_date(names) -> str:#返回番剧首播日期
    with open(animation_path,"r",encoding="utf-8") as r:
        tmp=json.load(r)
        if tmp[names]["date"]==None:
            return ""
        return(tmp[names]["date"])
def r_animation_information_week(names)->str:#返回番剧更新周几
    with open(animation_path,"r",encoding="utf-8") as r:
        tmp=json.load(r)
        if tmp[names]["week"]==None:
            return " "
        return(tmp[names]["week"])
def r_animation_information_time(names)->str:#返回当日更新时间
    with open(animation_path,"r",encoding="utf-8") as r:
        tmp=json.load(r)
        if tmp[names]["time"]==None:
            return ""
        return(tmp[names]["time"])
def file_json_store() -> None:#检测json文件是否存在,若存在则跳过，不存在则创建,
    try:
        with open(animation_path,"x",encoding="utf-8"):
            animation_informtions()
            return 0
    except:
        pass
    with open(animation_path,"r",encoding="utf-8") as f:
        tmp=json.load(f)
        tmp_y=datetime.strptime(tmp[list(tmp.keys())[0]]["date"],"%Y/%m/%d").strftime("%Y")
        tmp_m=datetime.strptime(tmp[list(tmp.keys())[0]]["date"],"%Y/%m/%d").strftime("%m")
        if int(tmp_y) != datetime.now().year or month[int(tmp_m)-1] != month[datetime.now().month]:
            animation_informtions()
        else:
            pass
file_json_store()
async def text_to_img(bot,message:Message,group=0,user:int=0):#消息文字转图片
    if animation_default_return_img:
        tmp=str(message)
        tmp_bic=await text_to_pic(tmp)
        if group==0:
            if user==0:
                await bot.send(MessageSegment.image(tmp_bic))
            else:
                await bot.send_msg(user_id=user,message_type="private",message=Message(MessageSegment.image(tmp_bic)))
        else:
            await bot.send_group_msg(group_id=group,message=MessageSegment.image(tmp_bic))
    else:
        try:
            if group==0:
                if user==0:
                    await bot.send(message)
                else:
                    await bot.send_msg(user_id=user,message_type="private",message=message)
            else:
                await bot.send_group_msg(group_id=group,message=message)
        except:
            tmp=str(message)
            tmp_bic=await text_to_pic(tmp)
            if group==0:
                if user==0:
                    await bot.send(MessageSegment.image(tmp_bic))
                else:
                    await bot.send_msg(user_id=user,message_type="private",message=Message(MessageSegment.image(tmp_bic)))
            else:
                await bot.send_group_msg(group_id=group,message=MessageSegment.image(tmp_bic))
async def r_animation_information_message(message_bot:Bot,num):#返回查询的动漫信息
    search_list=list(str(num).split(" "))
    msg_error,message_url=False,""
    try:
        for num in search_list:
            tmp=list(r_animation_informations_name())[int(str(num))-1]
            number=0
            for tmp_url in r_animation_information_url(tmp):
                number+=1
                message_url+=f'{number}，{tmp_url}\n'
            try:
                await message_bot.send(Message(Message(tmp+"\n"+weekday_map[r_animation_information_week(tmp)])+Message("【"+r_animation_information_time(tmp)+"】\n")+Message(message_url)+MessageSegment.image(file=r_animation_information_path(tmp))))
            except ActionFailed:
                await message_bot.send(Message(Message("【链接被风控了】\n")+Message(tmp+"\n"+weekday_map[r_animation_information_week(tmp)])+Message("【"+r_animation_information_time(tmp)+"】\n")+MessageSegment.image(file=r_animation_information_path(tmp))))
            msg_error,message_url=True,""
    except (IndexError,ValueError,TypeError):
        pass
    if not msg_error:await message_bot.finish("😊")
    await message_bot.finish()
async def return_animation_message(bot:Bot):#返回番剧详细信息
    file_json_store()
    number,messages=0,""
    for tmp in r_animation_informations_name():
        number+=1
        messages +=str(number) + "，"+tmp+"\n"
    number=0
    messages=str(datetime.now().year)+"年—"+str(datetime.now().month)+"月季度↓\n"+messages
    try:
        await text_to_img(bot,messages)
    except ActionFailed:
        await bot.finish(Message(f"可能被风控了捏！{random.choice(random_face)}"))
async def animation_today_(bot:Bot,group=0,user=0):#查询今日更新的番剧，编辑信息并发送
    number,r_message=0,""
    today_week=weekday_map[datetime.now().weekday()]
    for tmp in r_animation_informations_name():
        if today_week==weekday_map[r_animation_information_week(str(tmp))]:
            tmp_time=r_animation_information_time(str(tmp))
            number+=1
            r_message+=f'{number}，【{tmp_time}】{str(tmp)}\n'
    r_message=f"今日番剧【{today_week}】\n"+r_message
    try:
        await text_to_img(bot,message=r_message,group=group,user=user)
    except:
        await bot.finish(Message(f"可能被风控了捏！{random.choice(random_face)}"))
def load_user_setting()->list:#返回用户设置
    try:
        with open(User_setting_path,"r",encoding="utf-8") as f:
            tmp=json.load(f)
            sub_qq_group=tmp["sub_qq_group"]
            Users_sub=tmp["Users_sub"]
            Users_sub_animation=tmp["Users_sub_animation"]
            sub_time=tmp["sub_time"]
            tmp_version=tmp["version"]
            return [sub_qq_group,Users_sub,Users_sub_animation,sub_time,tmp_version]
    except KeyError:
        return [None,None,None,None,None]
def user_file_json():#检测是否存在用户配置文件 无则创建
    global plugin_version
    if not os.path.exists(User_setting_path):
        with open(User_setting_path,"w",encoding="utf-8") as r:
            data_tmp={
                "sub_qq_group":[],
                "Users_sub":[],
                "Users_sub_animation":{},
                "sub_time":[],
                "version":plugin_version
            }
            json.dump(data_tmp,r,indent=4,ensure_ascii=False) 
    try:
        if load_user_setting()[4]!=plugin_version:
            with open(User_setting_path,"r",encoding="utf-8") as f:
                tmp=json.load(f)
                for i in ["sub_qq_group","Users_sub","Users_sub_animation","sub_time","version"]:
                    if i not in list(tmp.keys()):
                        if i!="version":
                            tmp[i]=[]
                        else:
                            tmp[i]=plugin_version
                tmp["version"]=plugin_version
            with open(User_setting_path,"w",encoding="utf-8") as f:
                json.dump(tmp,f,indent=4,ensure_ascii=False) 
    except json.JSONDecodeError:
        os.remove(User_setting_path)
        user_file_json()
user_file_json()
async def add_user_sub_animation(bot:Bot,event:MessageEvent,numbers):#添加用户追番
    num_list=str(numbers).split(" ")
    msg=""
    with open(User_setting_path,"r",encoding="utf-8") as f:
        tmp_1=json.load(f)
        if str(event.user_id) not in list(tmp_1["Users_sub_animation"].keys()):
            tmp_1["Users_sub_animation"][str(event.user_id)]=[]
    with open(User_setting_path,"w",encoding="utf-8") as f:
        json.dump(tmp_1,f,indent=4,ensure_ascii=False)
    for i in num_list:
        try:
            if 0<=int(i)<=len(list(r_animation_informations_name())):
                i_name=r_animation_informations_num_to_name(int(i))
                with open(User_setting_path,"r",encoding="utf-8") as f:
                    tmp=json.load(f)
                    if i_name not in tmp["Users_sub_animation"][str(event.user_id)]:
                        tmp["Users_sub_animation"][str(event.user_id)].append(i_name)
                        msg+=i_name+"\n"
                with open(User_setting_path,"w",encoding="utf-8") as f:
                    json.dump(tmp,f,indent=4,ensure_ascii=False)
        except:
            pass
    if msg:
        try:
            await bot.finish(f"{msg}\n已新增至【{event.user_id}】的追番列表")   
        except ActionFailed:
            msg=f"{msg}\n已新增至【{event.user_id}】的追番列表"
            tmp_pic=await text_to_pic(msg)
            await bot.finish(Message(MessageSegment.image(tmp_pic)))
    else:
        await bot.finish(random.choice(random_face))
async def r_messagetype_message(bot:Bot or Matcher,type:str,id:int,msg):#根据 群or个人 类型发送消息
    '''
    type="private / group"
    '''
    if type=="private":
        await bot.send_msg(message_type="private",user_id=int(id),message=Message(msg))
    elif type=="group":
        await bot.send_msg(message_type="group",group_id=int(id),message=Message(msg))
async def pre_r_sub_animation(bot:Bot or Matcher,qq_user:int,sub_animation:str):#向订阅列表中的成员发送订阅消息
    msg=MessageSegment.at(user_id=int(qq_user))+Message(f"你的追番【{str(sub_animation)}】已更新{random.choice(random_face)}")
    if int(qq_user) in load_user_setting()[1]:
        await r_messagetype_message(bot,"private",qq_user,msg)
    if load_user_setting()[0]:
        for qq_group in load_user_setting()[0]:
            if int(qq_user) in groupmemberlist_userID_list(await bot.get_group_member_list(group_id=qq_group)):
                await r_messagetype_message(bot,"group",qq_group,msg)
def groupmemberlist_userID_list(dict) ->list:#返回该群成员信息中的qq号
    r_list=[]
    for i in dict:
        r_list.append(i['user_id'])
    return r_list
@animation.handle()
async def animtions_return():#强制更新番剧信息
    animation_informtions()
    await return_animation_message(animation)
@animation_infor.handle()#番剧信息
async def animation_infors():
    await return_animation_message(animation_infor)
@search_number.handle()#番剧查询
async def return_number(numbers:Message=CommandArg()):
    if str(numbers):
        file_json_store()
        await r_animation_information_message(search_number,numbers)
    else:
        await return_animation_message(search_number)
@search_number.got("tmp",prompt="请选择编号捏😘")#番剧查询编号
async def scond_search_number(num:Message=Arg("tmp")):
    file_json_store()
    await r_animation_information_message(search_number,num)
@animation_help.handle()#番剧帮助
async def animation_helps():
    tmp=f"""====================
#番剧信息 【当前季度的番剧】
#番剧更新 【强制更新番剧信息】
#今日新番 【今日更新的番剧】
#新增订阅 【订阅=追番提醒】
#取消订阅
==================== 
#番剧查询 【番剧信息中的序号】
#新增追番 【番剧信息中的序号】
#我的追番 【查看追番列表】
#取消追番"""
    try:
        await animation_help.finish(Message(tmp))
    except ActionFailed:
        await text_to_img(animation_help,tmp)
@upgrade_animation_today.handle()
async def animation_today():
    await animation_today_(upgrade_animation_today)
@scheduler.scheduled_job("cron",hour=animation_hour,minute=animation_minute)#每日推送番剧
async def today_animation(): 
    bot=get_bot()
    for i in load_user_setting()[0]:
        await animation_today_(bot=bot,group=i)
    for i in load_user_setting()[1]:
        await animation_today_(bot=bot,user=i)
@everyday_push.got("tmp",prompt=f"是否订阅每日推送 Y/N")#新增订阅
async def everyday_push_setting(bot:Bot,event:MessageEvent):
    with open(User_setting_path,"r",encoding="utf-8") as f:
        tmp1=event.get_plaintext()
        tmp1_txt=str(tmp1)
        tmp_json=json.load(f)
        if (tmp1_txt) in ["y","Y","是","yes","Yes","1"]:
            try:
                qq_group=int(event.group_id)
                if (qq_group not in load_user_setting()[0]) and await (admin_check(event)):
                    tmp_json["sub_qq_group"].append(qq_group)
                    await everyday_push.send(message=f'QQ群：{qq_group}已新增至订阅')
                else:
                    if await (admin_check(event)):
                        await everyday_push.send(message=f'QQ群：{qq_group}不可重复订阅')
                    else:
                        await everyday_push.send(f'无管理员权限不可修改群订阅\n————UR not an Admin')
            except: 
                user_qq=int(event.user_id)
                if user_qq not in load_user_setting()[1]:
                    tmp_json["Users_sub"].append(user_qq)
                    await everyday_push.send(message=f'QQ：{user_qq}已新增至订阅')
                else:
                    await everyday_push.send(message=f'QQ：{user_qq}不可重复订阅')
        else:
            await everyday_push.finish(message=random.choice(random_face))
    with open(User_setting_path,"w",encoding="utf-8") as f:
        json.dump(tmp_json,f,indent=4,ensure_ascii=False)
@everyday_push_off.got("tmp",prompt=f"是否取消每日推送 Y/N")#取消订阅
async def everyday_push_off_setting(bot:Bot,event:MessageEvent):
    with open(User_setting_path,"r",encoding="utf-8") as f:
        tmp1=event.get_plaintext()
        tmp1_txt=str(tmp1)
        tmp_json=json.load(f)
        if (tmp1_txt) in ["y","Y","是","yes","Yes","1"]:
            try:
                qq_group=int(event.group_id)
                if (qq_group in load_user_setting()[0]) and await (admin_check(event)):
                    tmp_json["sub_qq_group"].remove(qq_group)
                    await everyday_push_off.send(message=f'QQ群：{qq_group}已取消订阅')
                else:
                    if await (admin_check(event)):
                        await everyday_push_off.send(message=f'QQ群：{qq_group}无订阅信息')
                    else:
                        await everyday_push_off.send(f'无管理员权限不可修改群订阅\n————UR not an Admin')
            except: 
                user_qq=int(event.user_id)
                if user_qq in load_user_setting()[1]:
                    tmp_json["Users_sub"].remove(user_qq)
                    await everyday_push_off.send(message=f'QQ：{user_qq}已取消订阅')
                else:
                    await everyday_push_off.send(message=f'QQ：{user_qq}无订阅信息')
        else:
            await everyday_push_off.finish(message=random.choice(random_face))
    with open(User_setting_path,"w",encoding="utf-8") as f:
        json.dump(tmp_json,f,indent=4,ensure_ascii=False)
@emmmm.handle()#u know,that's right
async def emm():
    await emmmm.finish(message=Message(random.choice(random_face)))
@sub_drama.handle()#新增追番
async def sub_dramas(bot:Bot,event:MessageEvent,numbers:Message=CommandArg()):
    if str(numbers):
        await add_user_sub_animation(sub_drama,event,numbers)
    else:
        await return_animation_message(sub_drama)
@sub_drama.got("key",prompt="请选择编号")#询问新增追番
async def sub_dramas_(bot:Bot,event:MessageEvent):
    await add_user_sub_animation(sub_drama,event,event.get_plaintext())
@sub_drama_list.handle()#追番列表
async def sub_drama_list_(bot:Bot,event:MessageEvent):
    try:
        tmp=load_user_setting()[2][str(event.user_id)]
    except KeyError:
        await sub_drama_list.finish("无追番信息")
    num,msg=0,""
    for i in tmp:
        num+=1
        msg+=f"{num}，{i}\n"
    await text_to_img(sub_drama_list,msg)
@sub_sub_drama.handle()#取消追番
async def sub_sub_list(bot:Bot,event:MessageEvent):
    try:
        sub_list=load_user_setting()[2][str(event.user_id)]
    except KeyError:
        await sub_sub_drama.finish(f"QQ：{event.user_id}无订阅信息")
    msg,num="",0
    for i in sub_list:
        num+=1
        msg+=f"{num}，{i}\n"
    await text_to_img(sub_sub_drama,msg)
    await sub_sub_drama.send(f"请发送编号捏{random.choice(random_face)}#")
@sub_sub_drama.got("key")
async def sub_sub_list_get(bot:Bot,event:MessageEvent):
    with open(User_setting_path,"r",encoding="utf-8") as f:
        sub_list=event.get_plaintext().split(" ")
        tmp=json.load(f)
        msg,remove_ani="",[]
        if "all" in sub_list:
            tmp["Users_sub_animation"].pop(str(event.user_id))
            for i in sub_list:
                msg+=i+"\n"
            msg=f"已取消追番：\n{msg}"
        for i in sub_list:
            try:   
                remove_ani.append(tmp["Users_sub_animation"][str(event.user_id)][int(i)-1])
            except (IndexError,ValueError,TypeError):
                pass
        for i in remove_ani:
            tmp["Users_sub_animation"][str(event.user_id)].remove(i)
            if not tmp["Users_sub_animation"][str(event.user_id)]:
                tmp["Users_sub_animation"].pop(str(event.user_id))
        for i in remove_ani:
            msg+=i+'\n'
        msg=f"已取消追番：\n{msg}"
        if not remove_ani:
            await sub_sub_drama.finish(random.choice(random_face))
    with open(User_setting_path,"w",encoding="utf-8") as f:
        json.dump(tmp,f,indent=4,ensure_ascii=False)
    await text_to_img(sub_sub_drama,msg)
    await sub_sub_drama.finish()
@scheduler.scheduled_job("interval",minutes=1)#追番更新提醒
async def user_sub():
    sub_list=load_user_setting()[2]
    for qq_user in sub_list:
        tmp=load_user_setting()[2][str(qq_user)]
        for sub_animation in tmp:
            time_list=list(map(int,r_animation_information_time(sub_animation).split(":")))
            if weekday_map[r_animation_information_week(sub_animation)]==weekday_map[datetime.now().weekday()]:
                if datetime.now().hour==time_list[0] and datetime.now().minute==int(time_list[1]):
                    bot:Bot=get_bot()
                    await pre_r_sub_animation(bot,qq_user,sub_animation)
            if weekday_map[r_animation_information_week(sub_animation)]==weekday_map[(datetime.now().weekday()-1)%7]:
                if time_list[0]>23 and datetime.now().hour==time_list[0]%24 and datetime.now().minute==int(time_list[1]):
                    bot:Bot=get_bot()
                    await pre_r_sub_animation(bot,qq_user,sub_animation)
