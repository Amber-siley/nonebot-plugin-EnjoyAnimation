import json,requests,os,re
from datetime import datetime as dt
from lxml import html
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

class rss_item:
    def __init__(self,nameL:str,item:dict) -> None:
        self.__art_list=item["articles"]
        self.uid=item["uid"].replace("{","").replace("}","")
        self.url=item["url"]
        self.name=nameL
    
    class one_torrent:
        def __init__(self,data:dict) -> None:
            tmp=data["description"]
            tmp=html.fromstring(tmp)
            tmp="".join(tmp.xpath("//img/@src"))
            tmp=re.sub(f"@\w+\.jpg","",tmp)
            pic_url=tmp
            title=data["title"]
            torrenturl=data["torrentURL"]
            self.pic_url=pic_url
            self.title=title
            self.torrenturl=torrenturl

    @property
    def art_list(self) ->list[one_torrent]:
        ret=[]
        for i in self.__art_list:
            ret.append(self.one_torrent(i))
        return ret
        
class login_qb:
    def __init__(self,port:int,login_user:str=None,login_passwd:str=None) -> None:
        '''
        - port：qb web ui 端口
        
        可选：
        - login_user：登录用户名
        - login_passwd：登录密码
        '''
        login_data={
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
        self.session=requests.session()
        if login_user and login_passwd:
            login=self.session.post(url=self.__login_url,data=login_data)
        else:
            login=self.session.get(url=self.__root_url)
        if login.ok:
            self.user_setting=json.loads(self.session.get(url=self.__get_setting_url).text)
            # self.rss_infor=json.loads(self.session.get(url=self.__get_rss_infor_url).text)
        else:
            raise ConnectionError("qb链接错误")
        self.__add_torrent_setting={
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
    
    def set_default_download_path(self,path:str):
        '''设置默认保存路径\\
        path:保存文件路径'''
        if os.path.exists(path=path):
            self.user_setting["save_path"]=path
            self.session.post(url=self.__set_setting_url,data={"json":json.dumps(self.user_setting)})
        else:
            raise ValueError("路径错误")
        
    def add_download_torrent(self,pa_url:str,save_path:str=None,cookie:dict={},proxy:str=None):
        '''添加bt种子文件
        - path：种子文件路径 或者 torrent网址
        - save_path：保存路径，默认为默认保存路径
        - cookie：通过网址添加任务的时候可能会用到
        - proxy：代理网址'''
        url_dl=self.__add_torrent_setting
        if save_path:
            if os.path.exists(save_path):
                url_dl["savepath"]=save_path
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
    
    def get_download_project(self):
        '''获取下载项目的信息hash值'''
        tmp:dict=self._get_download_infor()["torrents"]
        tmp_keys=list(tmp.keys)
        return tmp_keys
    
    def add_rss(self,rss_url:str,r_path:str=""):
        '''添加rss订阅'''
        status=self.session.post(url=self.__add_rss_url,data={"url":rss_url,"path":r_path}).ok
        if not status:
            raise IndexError("项目已存在")
    
    def add_rss_dl_rule(self,rulename:str,ruledef:dict={}):
        '''添加rss下载器'''
        self.session.post(url=self.__add_rss_download_rule,data={"ruleName":rulename,"ruleDef":ruledef})
        
    @property
    def rss_infor(self)->list[rss_item]:
        '''rss订阅信息'''
        infors:dict=json.loads(self.session.get(url=self.__get_rss_infor_url).text)
        re=[]
        for i in infors:
            re.append(rss_item(i,infors[i]))
        return re
    
    def refres_rss(self):
        '''刷新rss订阅'''
        for i in self.rss_infor:
            self.session.post(url=self.__refres_rss_url,data={"itemPath":i.name})
       
    def rename_rss(self,item:str,dest:str):
        '''将rss订阅item改名为dest'''
        status=self.session.post(url=self.__rename_rss_url,data={"itemPath":item,"destPath":dest}).ok
        if not status:
            raise IndexError(f"不存在名为{item}的rss对象")
             
    def _test_json(self,json_str:dict or list):
        '''将json文本保存至文件'''
        with open(f"{dt.now().day}.json","w",encoding="utf-8") as w:
            json.dump(json_str,w,indent=4,ensure_ascii=False)
