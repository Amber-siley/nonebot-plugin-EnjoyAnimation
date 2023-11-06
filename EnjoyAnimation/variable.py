import os,logging
from random import choice
from nonebot import get_driver
from nonebot.log import LoguruHandler
from .QBsimpleAPI import login_qb

header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
    }

class ani_configs:
    '''本插件的配置信息'''
    def __init__(self) -> None:
        self.default={
            "re_type_img":True,
            "need_to_you":True,
            "qbit_port":8080,
            "admin_user":"admin",
            "admin_pw":"123456",
            "web_token_length":20
            }
        self.re_type_img=self.get_config("re_type_img")
        '''返回消息类型是否为图片'''
        self.need_to_you=self.get_config("need_to_you")
        '''是否需要在群聊中回复指令触发者的消息'''
        self.qbit_port=self.get_config("qbit_port")
        '''qbit端口'''
        self.admin=self.get_config("admin_user")
        '''web管理员账号'''
        self.admin_pw=self.get_config("admin_pw")
        '''web管理员密码'''
        self.web_token_length=self.get_config("web_token_length")
        '''web token长度'''
        
    def get_config(self,attr:str):
        try:
            re=getattr(config,attr)
        except AttributeError:
            re=self.default[attr]
        return re

def random_list(list:list):
    '''在一个列表随机选取一个元素'''
    return choice(list)

def random_str(length:int):
    '''随机生成length长度的字符串'''
    data_str="ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789,.;:[]!@#$%^&*-+="
    re_str=""
    for i in range(0,length):
        re_str+=random_list(data_str)
    return re_str

#dirs_path
work_path=os.path.join(os.getcwd(),"data")                              #指向data路径
date_files=os.path.join(work_path,"Animation_date")                     #数据文件夹路径
animation_pic_path=os.path.join(date_files,"Animation_pic")             #指向pic路径
text_img_path=os.path.join(animation_pic_path,"text_pic.jpg")           #文转图路径
video_path=os.path.join(date_files,"Animation_video")                   #指向vidoe路径
plugin_file_path=os.path.join(work_path,"Animation_admin")              #插件数据文件路径

#files_path
animation_path=os.path.join(plugin_file_path,"animation.db")            #指向animation.db文件路径
User_setting_path=os.path.join(plugin_file_path,"User_setting.json")    #指向user setting.json文件路径
# img_tmp_path=os.path.join(animation_pic_path,"img.jpg")                 #指向临时图片路径

#目录创建
os.makedirs(work_path,exist_ok=True)
os.makedirs(animation_pic_path,exist_ok=True)
os.makedirs(video_path,exist_ok=True)
os.makedirs(plugin_file_path,exist_ok=True)

#db
month=["01","01","01","04","04","04","07","07","07","10","10","10"]     #季度对应的时间表

#qbit-qpi


#nonebot
dirver=get_driver()             #驱动器
config=dirver.config            #配置信息
log_level=config.log_level      #日志等级 

#杂项
yes_list=["Yes sir","All set","It's a wrap","Check","Yet","Affirmative","You got it","Absolutely","Right away","On the dot"]

#logging
enjoy_log=logging.getLogger("EnjoyAnimation")                   #日志输出
enjoy_log.setLevel(log_level)
log_path=os.path.join(plugin_file_path,"EnjoyAnimation.log")    #日志文件路径
fg=logging.FileHandler(filename=log_path,encoding="utf-8")
formation=logging.Formatter("%(asctime)s %(levelname)s: %(message)s",)                               #输出到文件
fg.setFormatter(formation)
enjoy_log.addHandler(LoguruHandler())
enjoy_log.addHandler(fg)

#nonebot
ani_config=ani_configs()        #配置设置