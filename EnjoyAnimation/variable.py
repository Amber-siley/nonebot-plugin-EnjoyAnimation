import os

header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0"
    }
#dirs
work_path=os.path.join(os.getcwd(),"data")                              #指向data路径
pic_path=os.path.join(work_path,"Animation_pic")                        #指向pic路径
plugin_file_path=os.path.join(work_path,"Animation_admin")              #插件数据文件路径

#files
animation_path=os.path.join(plugin_file_path,"animation.db")            #指向animation.db文件路径
User_setting_path=os.path.join(plugin_file_path,"User_setting.json")    #指向user setting.json文件路径
img_tmp_path=os.path.join(pic_path,"img.jpg")                           #指向临时图片路径