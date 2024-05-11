import os,logging
from random import choice
from nonebot import get_driver
from nonebot.log import LoguruHandler

header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
    }

class ani_configs:
    '''本插件的配置信息'''
    def __init__(self) -> None:
        self.default={
            "re_type_img":True,
            "need_to":True,
            "need_at":True,
            "qbit_port":8070,
            "qbit_admin":None,
            "qbit_pw":None,
            "proxy":None,
            "web_ui":False,
            "admin_user":"admin",
            "admin_pw":"123456",
            "web_token_length":20,
            "bt_dl_url":{},
            "acgrip_enable":False,
            "kisssub_enable":True,
            "kisssub_cookie_path":None,
            "debug_mode":False
            }
        self.re_type_img=self.get_config("re_type_img")
        '''返回消息类型是否为图片'''
        self.need_to=self.get_config("need_to")
        '''是否需要在群聊中回复指令触发者的消息'''
        self.need_at=self.get_config("need_at")
        '''是否需要在群聊中@用户回复消息'''
        self.qbit_port=self.get_config("qbit_port")
        '''qbit 端口'''
        self.qbit_admin=self.get_config("qbit_admin")
        '''qbit web账号'''
        self.qbit_pw=self.get_config("qbit_pw")
        '''qbit web密码'''
        self.web_ui=self.get_config("web_ui")
        '''web ui是否开启'''
        self.admin=self.get_config("admin_user")
        '''web管理员账号'''
        self.admin_pw=self.get_config("admin_pw")
        '''web管理员密码'''
        self.web_token_length=self.get_config("web_token_length")
        '''web token长度'''
        self.bt_dl_url:dict=self.get_config("bt_dl_url")
        '''torrent文件搜索urls,网站返回类型xml格式 
        >>> {"https://www.example.com/.xml?item={xxx}":
                {
                    "proxy":"127.0.0.1:8080",//字符串或者None
                    "cookie_path":None       //cookie文件路径（相对路径/绝对路径）或者None
                }
            }'''
        self.acgrip_enable=self.get_config("acgrip_enable")
        '''acgrip种子网址是否启用'''
        self.kisssub_enable=self.get_config("kisssub_enable")
        '''爱恋种子网址是否启用'''
        self.proxy=self.get_config("proxy")
        '''代理地址 没啥用，目前唯一作用给acgrip使用'''
        self.kisssub_cookie_path=self.get_config("kisssub_cookie_path")
        '''爱恋种子cookie文件路径，没啥用，看后续开发提高兼容性时可能会使用'''
        self.debug_mode = self.get_config("debug_mode")
        '''debug模式'''
        
        #bt_dl_url
        if self.acgrip_enable:
            self.bt_dl_url["https://acg.rip/.xml?term={xxx}"]={"proxy":self.proxy,"cookie_path":None}
        if self.kisssub_enable:
            self.bt_dl_url["http://www.kisssub.org/rss-{xxx}.xml"]={"proxy":None,"cookie_path":self.kisssub_cookie_path}
        if self.acgrip_enable and self.kisssub_enable:
            enjoy_log.info("暂时不支持使用多个bt站点，默认选择用户设置的第一个站点")
    
    @property
    def dl_url(self)->list:
        '''bt配置中的url'''
        return list(self.bt_dl_url.keys())
        
    def get_config(self,attr:str):
        try:
            re=getattr(config,attr)
        except AttributeError:
            re=self.default[attr]
        return re

def random_list(list:list):
    '''在一个列表随机选取一个元素 额，我也不知道为什么写了这个函数，鬼上身了'''
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
date_files=os.path.join(work_path,"Animation_data")                     #数据文件夹路径
animation_pic_path=os.path.join(date_files,"Animation_pic")             #指向pic路径
text_img_path=os.path.join(animation_pic_path,"text_pic.jpg")           #文转图路径
video_path=os.path.join(date_files,"Animation_video")                   #指向vidoe路径
plugin_file_path=os.path.join(work_path,"Animation_admin")              #插件数据文件路径
debug_path=os.path.join(plugin_file_path,"debug")                       #开发测试的debug目录

#files_path
animation_path=os.path.join(plugin_file_path,"animation.db")            #指向animation.db文件路径
User_setting_path=os.path.join(plugin_file_path,"User_setting.json")    #指向user setting.json文件路径
# img_tmp_path=os.path.join(animation_pic_path,"img.jpg")                 #指向临时图片路径

#目录创建
os.makedirs(work_path,exist_ok=True)
os.makedirs(animation_pic_path,exist_ok=True)
os.makedirs(video_path,exist_ok=True)
os.makedirs(plugin_file_path,exist_ok=True)
os.makedirs(debug_path,exist_ok=True)

#db
month=["01","01","01","04","04","04","07","07","07","10","10","10"]     #季度对应的时间表
animes_db_colnames = ['id', 'pic_path', 'start_date', 'JP_start_date_UTC8', 'CN_start_date', 'status', 'official_url',"description"] #animations列名

#qbit-api


#nonebot
dirver=get_driver()             #驱动器
config=dirver.config            #配置信息
log_level=config.log_level      #日志等级 

#杂项
yes_list=["Yes sir","All set","Check","Yet","Affirmative","You got it","Absolutely","Right away","On the dot"]
anime_user_help_txt='''
Commands：(必须参数)【可选参数】
#番剧帮助：显示帮助
#番剧信息：返回当前季度番剧列表
#今日更新：返回今日更新番剧列表
#番剧查询 【番剧名称】：返回番剧详细信息
#番剧订阅 【番剧名称】：订阅番剧设置下载任务，自动提醒
#我的追番：获取用户订阅的番剧
#取消追番 【番剧编号】：取消订阅番剧
'''
anime_admin_help_txt='''
admin's Commands：
#更新番剧：强制更新番剧信息的数据库
'''
anime_admin_help_txt=anime_user_help_txt+anime_admin_help_txt
datetime_week={0:"周一",1:"周二",2:"周三",3:"周四",4:"周五",5:"周六",6:"周日"}

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
ani_config=ani_configs()        #提供调用配置的对象