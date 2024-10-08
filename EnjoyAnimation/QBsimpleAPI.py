#简易的qbittorrent的api接口
import json,requests,os,re
from datetime import datetime as dt
from lxml import html
from .variable import (
    enjoy_log
)
from urllib.parse import quote

class Byte_to_speed:
    def __init__(self,byte:int) -> None:
        self.byte=byte
        '''下载字节速度'''
        unit="B/s"
        if byte>1024:
            byte>>=10
            unit="KB/s"
        if byte>1024:
            byte>>=10
            unit="MB/s"
        self.speed=byte
        '''下载速度'''
        self.unit=unit
        '''下载速度单位'''

    def __str__(self) -> str:
        return f"""{self.speed} {self.unit}"""    
    
    
class rss_item:
    def __init__(self,data:dict) -> None:
        self.titles = list(data.keys())
        self.rss_list = [self.one_rss(i) for i in data.items()]
        self.rss_urls = [i.url for i in self.rss_list]
        
        #以后优化
        self.torrent_urls = [j.torrenturl for i in self.rss_list for j in i.art_list]
        self.torrent_hashs = [j.hash for i in self.rss_list for j in i.art_list]
        self.hash_to_Turl = {j.hash:j.torrenturl for i in self.rss_list for j in i.art_list}
        self.hash_to_rssname = {j.hash:i.rss_name for i in self.rss_list for j in i.art_list}
        self.hash_to_rssurl = {j.hash:i.url for i in self.rss_list for j in i.art_list}
    
    def get_torrent_hashs(self,rss_url):
        for item in self.rss_list:
            if item.url == rss_url:
                return item.hashs
            
    
    class one_rss:
        def __init__(self,data:tuple) -> None:
            self.rss_name,infor = data 
            self.title = infor["title"]
            self.uid = infor["uid"].replace("{","").replace("}","")
            self.url = infor["url"]
            self.art_list = [rss_item.one_torrent(i) for i in infor["articles"]]
            """articles列表"""
            self.hashs = [i.hash for i in self.art_list]
            self.__Tauthors = [i.author for i in self.art_list]
            self.authors = list(set(self.__Tauthors))

        def use_aurthor_search_torrrent(self,author:str):
            return [i for i in self.art_list if i.author == author]
        
    class one_torrent:
        def __init__(self,data:dict) -> None:
            tmp=data["description"]
            tmp=html.fromstring(tmp)
            tmp="".join(tmp.xpath("//img/@src"))
            tmp=re.sub(f"@\w+\.jpg","",tmp)
            pic_url=tmp
            title=data["title"]
            torrenturl=data["torrentURL"]
            
            self.author = data["author"]
            self.title=title
            self.__tags = re.findall(r"[\[,【,『](.*?)[\],】,』]",self.title)
            title_sub_tag = re.sub(r"\s*\[.*?\]\s*","",self.title)
            self.__tags.append(title_sub_tag)
            
            self.tags = []
            for i in self.__tags:
                self.tags.extend(i.split(" "))
            self.hash = re.findall(r"&hash=(\w+)",torrenturl)[0]
            self.pic_url=pic_url
            self.torrenturl=torrenturl

class dowload_item:
    def __init__(self,data:dict) -> None:
        try:
            self.__torrents:dict = data["torrents"]
        except KeyError:
            self.__torrents:dict = {}
        self.hashs = list(self.__torrents.keys())
        self.task_list = [self.one_task(i) for i in self.__torrents.items()]
    
    class one_task:
        def __init__(self,data:tuple) -> None:
            self.hash , _ = data
            self.progress = self.__get_value(_,"progress",1)

        @staticmethod
        def __get_value(data:str,key:str,default=None):
            try:
                return data[key]
            except:
                return default
        
class login_qb:
    _rss_default_ruleDef={"addPaused":None,#添加后不开始下载None,True,False
                     "affectedFeeds":[],#rss_url(list[str])
                     "assignedCategory":"",#指定类别(str)
                     "enabled":False,#是否启用该下载器(bool)
                     "episodeFilter":"",#剧集过滤器(str)
                     "ignoreDays":0,#忽略指定时间后的匹配项 (0 = 禁用)
                     "lastMatch":"",#上一次结果
                     "mustContain":"",#正则表达式必须包含(str)
                     "mustNotContain":"",#正则表达式不必包含(str)
                     "previouslyMatchedEpisodes":[],
                     "savePath":"",#保存路径(str)
                     "smartFilter":False,#是否启用剧集过滤器(bool)
                     "torrentContentLayout":None,#torrent内容布局None,Original,Subfolder,NoSubfolder==全局，原始，创建子文件夹，不创建子文件夹
                     "useRegex":False,#是否使用正则表达式(bool)
                     }

    _rss_default_donlowd_ruleDef=_rss_default_ruleDef
    _rss_default_donlowd_ruleDef["priority"] = 0
    _rss_default_donlowd_ruleDef["torrentParams"] = {"category":"",
                                                     "download_limit":-1,
                                                     "download_path":"",
                                                     "inactive_seeding_time_limit":-2,
                                                     "operating_mode":"AutoManaged",
                                                     "ratio_limit":-2,
                                                     "save_path":"",
                                                     "seeding_time_limit":-2,
                                                     "skip_checking":False,
                                                     "tags":[""],
                                                     "upload_limit":-1,
                                                     "use_auto_tmm":False,
                                                     "stopped":False}
    
    NaN = float("nan")
    
    def __init__(self,port:int,login_user:str=None,login_passwd:str=None) -> None:
        '''
        - port：qb web ui 端口
        
        可选：
        - login_user：登录用户名
        - login_passwd：登录密码
        '''
        self.login_data={
            "username":login_user,
            "password":login_passwd
        }
        self.port=str(port)
        self.__root_url=f"http://localhost:{(self.port)}"
        self.__login_url=f"{self.__root_url}/api/v2/auth/login"
        self.__get_setting_url=f"{self.__root_url}/api/v2/app/preferences"
        self.__set_setting_url=f"{self.__root_url}/api/v2/app/setPreferences"
        self.__add_torrent_url=f"{self.__root_url}/api/v2/torrents/add"
        self.__get_download_infor_url=f"{self.__root_url}/api/v2/sync/maindata"
        self.__get_rss_infor_url=f"{self.__root_url}/api/v2/rss/items?withData=true"
        self.__add_rss_url=f"{self.__root_url}/api/v2/rss/addFeed"
        self.__rename_rss_url=f"{self.__root_url}/api/v2/rss/moveItem"
        self.__refres_rss_url=f"{self.__root_url}/api/v2/rss/refreshItem"
        self.__add_rss_download_rule=f"{self.__root_url}/api/v2/rss/setRule"
        self.__get_rss_dl_rule=f"{self.__root_url}/api/v2/rss/rules"
        self.__remove_rss_url = f"{self.__root_url}/api/v2/rss/removeItem"
        self.__delete_dl_url = f"{self.__root_url}/api/v2/torrents/delete"
        
        self.__matching_artcles_url=f"{self.__root_url}/api/v2/rss/matchingArticles"
        self.session=requests.session()
        self.__session=self.session
        if not self.ok:
            enjoy_log.warning(f"qbittorrent 未连接 \n \
                \t url = {self.__root_url} \n \
                \t login = {self.login_data}")
        else:
            enjoy_log.info(f"qbittorrent 已链接")
    
    @property
    def __add_torrent_setting(self):
        '''从文件选择添加任务设置参数'''
        return {
            "autoTMM": self.user_setting["auto_tmm_enabled"],
            "savepath": self.user_setting["save_path"],
            "rename": "",
            "category": "",
            "paused": False,
            "stopCondition": None,
            "contentLayout": "Original",
            "dlLimit": float('nan'),
            "upLimit": float('nan')
        }
    
    @property
    def ok(self):
        '''链接状态'''
        try:
            if self.login_data["username"] and self.login_data["password"]:
                login=self.__session.post(url=self.__login_url,data=self.login_data)
            else:
                login=self.__session.get(url=self.__root_url)
        except:
            return False
        if not login.ok:
            # raise ConnectionError("qb链接错误")
            return False
        return True
    
    def check(func):
        '''装饰器，检测是否能链接qbittorrent后再决定执行'''
        def _(self,*args, **kwargs):
            if self.ok:
                func(self,*args, **kwargs)
                return True
            else:
                # enjoy_log.error(f"执行方法{func.__name__}时，qbit未链接")
                return False
        return _

    @property
    def user_setting(self):
        '''用户设置'''
        return json.loads(self.session.get(url=self.__get_setting_url).text)
    
    def set_default_download_path(self,path:str):
        '''设置默认保存路径\\
        path:保存文件路径'''
        if os.path.exists(path=path):
            self.user_setting["save_path"]=path
            self.session.post(url=self.__set_setting_url,data={"json":json.dumps(self.user_setting)})
        else:
            raise ValueError("路径错误")

    def add_download_torrent(self,pa_url:str,save_path:str=None,cookie:dict={},proxy:str=None):
        '''添加bt种子文件任务
        - path：种子文件路径 或者 torrent网址
        - save_path：保存路径，默认为默认保存路径
        - cookie：通过网址添加任务的时候可能会用到
        - proxy：代理网址'''
        url_dl=self.__add_torrent_setting
        if save_path:
            if os.path.exists(save_path):
                url_dl["savepath"]=save_path.replace("\\","/")
        if os.path.exists(path=pa_url):
            with open(pa_url,"rb") as r:
                torrent_bit=r.read()
            name=os.path.split(pa_url)[1]
            files={"fileselect[]":(name,torrent_bit,'application/x-bittorrent')}
            self.session.post(url=self.__add_torrent_url,data=url_dl,files=files)
        elif requests.get(url=pa_url,proxies=proxy).ok:
            url_dl["urls"]=pa_url
            url_dl["cookie"]=cookie
            self.session.post(url=self.__add_torrent_url,data=url_dl)
        else:
            raise ValueError("路径，网址，或者代理有问题")
     
    def _get_download_infor(self) -> dict:
        '''获取下载信息'''
        return json.loads(self.session.get(url=self.__get_download_infor_url).text)
    
    def get_download_speed(self) -> Byte_to_speed:
        '''获取下载速度\\
        返回一个类对象'''
        tmp=self._get_download_infor()["server_state"]["dl_info_speed"]
        return Byte_to_speed(tmp)
    
    @property
    def download_info(self):
        '''获取下载项目的信息'''
        return dowload_item(self._get_download_infor())
    
    def add_rss(self,rss_url:str,r_path:str="") ->bool:
        '''添加rss订阅，返回是否成功的布尔值
        - rss_url：rss网址，中文要使用url编码
        - r_path：忘了有什么用，不用设置'''
        status=self.session.post(url=self.__add_rss_url,data={"url":rss_url,"path":r_path}).ok
        if not status:
            #raise IndexError("项目已存在")
            return False
        return True

    def cn_add_rss(self,url_tplt:str,cn_str:str,r_path:str=""):
        '''含有中文路径的添加rss订阅
        - url_tplt：rss网址模板，https://www.example.com/.xml?item={xxx}，{xxx}会被替换成tmp_str中的字符
        - cn_str：需要替换的字符
        - r_path：忘了有什么用，不用设置'''
        return self.add_rss(rss_url=self._chinese_url_replace_encoding(url_tplt,cn_str),r_path=r_path)

    def get_rss_dl_rule(self) -> dict:
        '''获取rss下载器信息'''
        rules=json.loads(self.session.get(url=self.__get_rss_dl_rule).text)
        return rules
    
    def _rss_dl_rule(self,enabled:bool=False,
                         addpaused:bool=None,
                         save_path:str=''
                         )-> dict:
        '''返回rss下解器规则文件'''
        re_ruledef=self._rss_default_ruleDef
        re_ruledef["enabled"]=enabled
        re_ruledef["addPaused"]=addpaused
        re_ruledef["savePath"]=save_path
        return re_ruledef
    
    def add_rss_dl_rule(self,rulename:str,ruledef:dict={}):
        '''添加rss下载器'''
        self.session.post(url=self.__add_rss_download_rule,data={"ruleName":rulename,"ruleDef":ruledef})
    
    @property
    def rss_infor(self) -> rss_item:
        '''rss订阅信息,返回rss_item类对象的列表'''
        infors:dict=json.loads(self.session.get(url=self.__get_rss_infor_url).text)
        return rss_item(infors)
    
    def refres_rss(self):
        '''刷新rss订阅'''
        for i in self.rss_infor:
            self.session.post(url=self.__refres_rss_url,data={"itemPath":i.name})
    
    def rename_rss(self,item:str,dest:str):
        '''将rss订阅item改名为dest'''
        status=self.session.post(url=self.__rename_rss_url,data={"itemPath":item,"destPath":dest}).ok
        if not status:
            raise IndexError(f"不存在名为{item}的rss对象")
       
    def _test_json(self,json_str:dict | list):
        '''将json文本保存至文件'''
        with open(f"{dt.now().day}.json","w",encoding="utf-8") as w:
            json.dump(json_str,w,indent=4,ensure_ascii=False)

    @staticmethod
    def _chinese_url_replace_encoding(url:str,tmp_str:str="") ->str:
        '''将中文编码转url进行拼接
        - url：https://www.example.com/.xml?item={xxx}，{xxx}会被替换成tmp_str中的字符
        - tmp_str：需要进行替换的字符串，将会使用url进行编码'''
        re_rule="\{x{3}\}"
        return(re.sub(re_rule,quote(tmp_str),url,1))
    
    def remove_rss(self,rss_url):
        '''移除rss订阅'''
        for i,url in enumerate(self.rss_infor.rss_urls):
            if rss_url == url:
                title = self.rss_infor.titles[i]
        self.delete_dl(rss_url)
        self.session.post(self.__remove_rss_url,data = {'path':title})
    
    def delete_dl(self,rss_url):
        '''删除下载文件'''
        hashs = self.rss_infor.get_torrent_hashs(rss_url)
        for h in hashs:
            self.session.post(url = self.__delete_dl_url,data = {
                "hashes":h,
                "deleteFiles":True
            })