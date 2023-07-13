import os,logging
from nonebot import get_driver
from nonebot.log import LoguruHandler

header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
    }
#dirs_path
work_path=os.path.join(os.getcwd(),"data")                              #指向data路径
date_files=os.path.join(work_path,"Animation_date")                     #数据文件夹路径
animation_pic_path=os.path.join(date_files,"Animation_pic")             #指向pic路径
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

#nonebot
dirver=get_driver()             #驱动器
config=dirver.config            #配置信息
log_level=config.log_level      #日志等级



#logging
enjoy_log=logging.getLogger("EnjoyAnimation")                   #日志输出
enjoy_log.setLevel(log_level)
log_path=os.path.join(plugin_file_path,"EnjoyAnimation.log")    #日志文件路径
fg=logging.FileHandler(filename=log_path,encoding="utf-8")
formation=logging.Formatter("%(asctime)s %(levelname)s: %(message)s",)                               #输出到文件
fg.setFormatter(formation)
enjoy_log.addHandler(LoguruHandler())
enjoy_log.addHandler(fg)
