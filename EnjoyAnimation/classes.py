import json,sqlite3,re,difflib
from datetime import datetime,timedelta
from typing import Literal
from .variable import (
    enjoy_log
)

class json_files:
    '''json管道'''
    def __init__(self,json_path:None) -> None:
        self.__json_path=json_path
        
    def read(self):
        '''读取json文件'''
        r=open(self.__json_path,"r",encoding="utf-8")
        re=json.load(r)
        r.close()
        return json.load(re)
    
    def write(self,data):
        '''刷新写入json文件'''
        w=open(self.__json_path,"w",encoding="utf-8")
        json.dump(data,w,indent=4,ensure_ascii=False)
        w.close()
    
class isotime_format:
    '''UTC时间字符格式转换'''
    def __init__(self,time_str:str) -> None:
        if len(time_str) < 13:
            raise KeyError
        if time_str.startswith("R/"):
            self.iso_time_str=time_str[2:-9]
        else:
            self.iso_time_str=time_str[:-5]
        self.time_datetime=datetime.fromisoformat(self.iso_time_str)
        
    def datetime_operation(self,oper:str,unit:str,var:int):
        '''datetime的运算+/-
        - oper:"+"/"-"
        - unit:需要在那=哪部分相加减'''
        if oper in ["+","add","plus"]:
            pos_neg=1
        else:
            pos_neg=-1
        self.time_datetime+=pos_neg*self.__timedelta_dict(unit,var)
        return str(self.time_datetime)
    
    def __timedelta_dict(self,unit:str,var:int):
        tmp={unit:var}
        return timedelta(**tmp)
    
    @property
    def datetim_str(self):
        return str(self.time_datetime)
    
class dlite:
    '''datetime_lite简单的时间类以及字符串管理'''
    def __init__(self,time:datetime | str=None) -> None:
        if isinstance(time,datetime):
            self.date_time=time
            self.str=self.d_to_str(self.date_time)
        elif time==None:
            ...
        elif isinstance(time,str):
            self.str=time
            self.date_time=self.str_to_d(time)
        if time:
            self.week:int=self.date_time.weekday()
    
    @staticmethod
    def d_to_str(date_time:datetime) -> str:
        '''时间类转%Y-%m-%d %H:%M:%S格式   字符串'''
        return date_time.strftime("%Y-%m-%d %H:%M:%S")
    @staticmethod
    def str_to_d(str_time:str) -> datetime:
        '''%Y-%m-%d %H:%M:%S格式字符串转   时间类'''
        return datetime.strptime(str_time,"%Y-%m-%d %H:%M:%S")
    
    def testfor_lastweek()->str:
        '''返回本周一的时间字符串'''
        now=datetime.now()
        now_week=now.weekday()
        week_1=now-timedelta(days=now_week)
        week_1=week_1.replace(hour=0,minute=0,second=0)
        return week_1.strftime("%Y-%m-%d %H:%M:%S")
    
    def cn_date(self,format:str="Y年M月d日")->str:
        '''中文时间字符串，使用与schedule_lite相同格式的字符串
        - Y：年
        - M：月
        - d：日
        - h：时
        - m：分
        - s：秒
        - w：周
        
        use
        >>> dlite(datetime).cn_date() -> 符合format格式的str'''
        format=format.replace("Y","%Y").replace("M","%x").replace("d","%d").replace("h","%H").replace("m","%M").replace("s","%S").replace("w","%w").replace("%x","%m")
        return self.date_time.strftime(format)
    
class db_lite:
    '''动漫数据库管理'''
    def commit(func):
        '''数据修改后，向数据库提交修改的装饰器'''
        def commit_1(self,*args, **kwargs):
            func(self,*args, **kwargs)
            self.conn.commit()
        return commit_1
    
    @commit
    def __fix_self(self):
        '''自捡，'''
        for table in self.__tables_colnames.keys():
            anime_colnames = self.get_colname(table)
            for real_col in self.__tables_colnames[table].keys():
                #检查animations中的列名是否缺失
                if real_col not in anime_colnames:
                    #缺失列则添加
                    self.alter_table_db(table,"add",real_col,self.__tables_colnames[table][real_col])
                    enjoy_log.debug(f"在{table}中缺失 {real_col} 已添加")
                    
    @commit
    def __init__(self,db_path) -> None:
        self.__db_path=db_path
        self.conn=sqlite3.connect(self.__db_path,check_same_thread=False)
        self.cursor=self.conn.cursor()
        self.__animes_colnames = {'id':'integer', 'pic_path':'text', 'start_date':"date", 'JP_start_date_UTC8':'date', \
                'CN_start_date':'date', 'status':"date", 'official_url':'text',"description":'text',"anime_type":"text",\
                "anime_typetag":'text',"pv":"text","froms":"text","episodes":"text"} #animations列名
        self.__user_subscriptions_colnames = {"qq_id":"integer","anime_relation":"integer","web_username":"text","status":"integer"}
        self.__tables_colnames = {
            "animations":self.__animes_colnames,
            "user_subscriptions":self.__user_subscriptions_colnames
        }
        self.cursor.execute('''
                            create table if not exists animations(
                                id integer primary key,
                                pic_path text,
                                start_date date,
                                JP_start_date_UTC8 date,
                                CN_start_date date,
                                status date,
                                froms text,
                                official_url text,
                                pv text,
                                description text,
                                anime_type text,
                                anime_typetag text,
                                episodes text
                            ) 
                            ''')
        self.cursor.execute(''' 
                            create table if not exists urls(
                                url text not null primary key,
                                relation integer,
                                foreign key (relation) references animations(id)
                            )
                            ''')
        self.cursor.execute('''
                            create table if not exists names(
                                row_id integer primary key,
                                name text not null,
                                relation integer,
                                foreign key (relation) references animations(id)
                            )
                            ''')
        self.cursor.execute('''
                            create table if not exists qbits(
                                qb_rssurl text not null primary key,
                                relation integer,
                                anime_name text,
                                foreign key (relation) references animations(id)
                            )
                            ''')
        self.cursor.execute('''
                            create table if not exists enjoy_users(
                                username text not null primary key,
                                password text not null,
                                token text,
                                token_update date,
                                qq_id integer,
                                foreign key (qq_id) references user_subscriptions(qq_id)
                            )
                            ''')
        self.cursor.execute('''
                            create table if not exists user_subscriptions(
                                qq_id integer not null,
                                anime_relation integer not null,
                                web_username text,
                                status integer,
                                foreign key (anime_relation) references animations(id),
                                foreign key (web_username) references enjoy_users(username)
                            )
                            ''')
        self.__fix_self()

    def test_name_db(self,names:list | str) -> bool:
        '''检测动漫名称是否存在数据库中'''
        back=False
        if isinstance(names,str):
            names=[names]
        for name in names:
            if self.universal_select_db(table="names",attribute="relation",where="name",like=f"""{name}"""):
                back = True
                break
        return back
    
    @commit
    def universal_insert_db(self,table:str,**kwargs):
        '''通用插入数据库
            
            Kwargs：
            -    key 表示表中的列，
                
            -    value 表示insert into values()中的值，可以是sql语句“run(sql语句)”
                
            >>> 在animations中插入数据'animations',{"path":path,"JP_start_date_UTC8":JP_start_date_UTC8,"status":status,"official_url":official}
            >>> 插入sql语句’names‘,{"name":item,"relation":"run(select max(id) from animations)"}'''
        if all([True if i==None else False for i in kwargs.values()]):
            #参数为设置则什么都不执行
            return 0
        
        attrbute=str(tuple(kwargs.keys()))
        value=str(tuple(i if i is not None else 'NULL' for i in list(kwargs.values()))).replace("'NULL'","NULL")
        sql_text=f'''
        insert into {table} {attrbute}
        values{value}
        ''' 
        sql_text=self.__run_command(r"'run(.*?)'",sql_text)
        try:
            self.cursor.execute(sql_text)
        except sqlite3.OperationalError:
            enjoy_log.error(f"{sql_text}语法错误")
        except sqlite3.IntegrityError:
            enjoy_log.error(f"{sql_text}已存在")
        
    @commit
    def insert_animation_info_db(self,
                                 names:list[str]=None,
                                 pic_path:str=None,
                                 start_date=None,
                                 JP_start_date_UTC8=None,
                                 CN_start_date=None,
                                 status=None,
                                 froms=None,
                                 urls:list=None,
                                 official:str=None):
        '''插入animations信息数据 
        重写后：仅保存插入功能移除名称检测\n
        属性对照表格
        | value | table |
        |:-:|:-:|
        | names | names |
        | pic_path | animations |
        | start_date | animations |
        | jp_start_date | animations |
        | cn_start_date | animations |
        | status | animations |
        | urls | urls |
        | froms | animations |
        | offical | animations |'''
        tmp_data = {
            "pic_path":pic_path,
            "start_date":start_date,
            "JP_start_date_UTC8":JP_start_date_UTC8,
            "CN_start_date":CN_start_date,
            "status":status,
            "froms":froms,
            "official_url":official
        }
        
        #插入animations表
        self.universal_insert_db("animations",**tmp_data)
        #插入names表
        for name in names:
            self.universal_insert_db("names",name=name,relation="run(select max(id) from animations)")
        #插入url表
        for url in urls:
            self.universal_insert_db("urls",url=url,relation="run(select max(id) from animations)")
        
    @commit
    def update_animation_info_db(self,
                                 id,
                                 names:list[str]=None,
                                 pic_path:str=None,
                                 start_date=None,
                                 JP_start_date_UTC8=None,
                                 CN_start_date=None,
                                 status=None,
                                 froms=None,
                                 urls:list=None,
                                 pv=None,
                                 anime_type=None,
                                 episodes=None,
                                 anime_typetag=None,
                                 official:str=None):
        '''更新animations信息数据，但也会执行插入操作，因为必须指定id'''
        tmp_data={
            "pic_path":pic_path,
            "start_date":start_date,
            "JP_start_date_UTC8":JP_start_date_UTC8,
            "CN_start_date":CN_start_date,
            "status":status,
            "froms":froms,
            "pv":pv,
            "episodes":episodes,
            "anime_type":anime_type,
            "anime_typetag":anime_typetag,
            "official_url":official
        }

        #更新animations表
        self.universal_update_db("animations",f"id={id}",**tmp_data)
        #插入names表
        if names:
            exists_names = self.universal_select_db("names","name",f"relation={id}")
            not_exists_names = [i for i in names if i not in exists_names]
            for name in not_exists_names:
                self.universal_insert_db("names",name = name,relation=id)
        #插入urls表
        if urls:
            exists_urls = self.universal_select_db("urls","url",f"relation={id}")
            not_exists_urls = [i for i in urls if i not in exists_urls]
            for url in not_exists_urls:
                self.universal_insert_db("urls",url = url,relation=id)
            
    @commit 
    def reset_table(self,table):
        '''重置表'''
        self.cursor.execute(f'''delete from {table}''')
    
    def name_ratio(self,name_list:list | str)->int:
        '''检测动漫名称的相似度大于0.7的id'''
        tmp_list = self.universal_select_db("names","name")
        if isinstance(name_list,str):
            name_list=[name_list]
        for i in name_list:
            i=re.sub(r"[,，?？！~]","",i).replace(" ","")
            if len(i)>5:
                rou=i[:round(len(i)*0.8)]
            else:
                rou=i
            for j in tmp_list:
                z=re.sub(r"[,，?？！~]","",j).replace(" ","")
                Match=difflib.SequenceMatcher(None,rou,z[:len(rou)])
                if Match.ratio() >= 0.7:
                    num=self.universal_select_db("names","relation",f"name=\"{j}\"")[0]
                    return num
        return False
    
    def __run_command(self,rule:str,sql_text):
        '''指令解析
        
        \'run(select max(id) from animations)\''''
        sql_list=[]
        run=re.finditer(rule,sql_text)
        if run:
            for i in run:
                sql_list.append(i.group(1))
            for i in sql_list:
                sql_text=re.sub(rule,i,sql_text,count=1)
        return sql_text
    
    def universal_select_db(self,table:str,attribute:tuple | str,where:str="1=1",like:str=None,order:str=None,by:str="asc")->list[str]:
        '''通用查询
        - table：表
        - attribute：返回属性可以是聚合函数，比如run(sum(id))
        - where：条件
        - like：近似值
        - order：按哪一列排序
        - by：ASC（升序），DESC（降序）'''
        if isinstance(attribute,tuple):
            attribute=str(attribute)[1:-1].replace("'","")
        attribute=self.__run_command(r'run\((.*?\))\)',attribute)
        sql_text=f'''select {attribute} from {table} where {where} '''
        if like:
            sql_text+=f'''like "{like}"'''
        if order:
            sql_text+=f'''order by {order} {by}'''
        try:
            self.cursor.execute(sql_text)
            # enjoy_log.debug(f"执行的语句为:\n{sql_text}")
        except sqlite3.OperationalError:
            enjoy_log.error(f"{sql_text}语法错误")
        return self.__get_sql_redata()

    def __get_sql_redata(self):
        sql_re=self.cursor.fetchall()
        lock=True
        for i in sql_re:
            if len(i)>1:
                lock=False
                break
        if lock:
            seen=set()
            sql_re=[i for tup in sql_re for i in tup if i not in seen and not seen.add(i)]
        #sql_re=list(set(sql_re)) 虽然很方便但会改变顺序
        return sql_re
    
    @commit
    def universal_update_db(self,table:str,where:str=None,like:str=None,**kwargs):
        '''通用更新
        - table：表
        - where：条件
        - like：近似值
        - **kwargs：需要更新的属性：值的字典'''
        column_val=""
        for column,value in kwargs.items():
            if value is not None:
                column_val+=f'{str(column)}="{str(value)}",'
        sql_text=f'''
        update {table}
        set {column_val[:-1]}
        where {where} 
        '''
        if like:
            sql_text+=f"like '{like}'"
        try:
            self.cursor.execute(sql_text)
        except sqlite3.OperationalError:
            enjoy_log.error(f"{sql_text}语法错误")
    
    def close_db(self):
        '''关闭数据库'''
        self.cursor.close()
        self.conn.close()
    
    @commit
    def universal_delete_db(self,table:str,where:str=None):
        '''通用删除
        - table：表
        - where：条件
        '''
        sql_text = f'''
        delete from {table}
        where {where}
        '''
        self.cursor.execute(sql_text)
    
    @commit
    def alter_table_db(self,table:str,type:Literal["add","drop","alter"],col:str,datatype:Literal["text","interger","date"] = None):
        '''添加，删除，改变列（属性）
        - table：表
        - type：类型
        - col：列名
        - datatype：列的数据类型
        '''
        if type == "add":
            sql_text = f'''
                alter table {table}
                {type} {col} {datatype}
            '''
        elif type == "drop":
            sql_text = f'''
                alter table {table}
                {type} column {col}
            '''
        elif type == "alter":
            sql_text = f'''
                alter table {table}
                {type} column {col} {datatype}
            '''
        self.cursor.execute(sql_text)
    
    def get_colname(self,table:str) -> list[str]:
        '''获取表的列名
        - table：表'''
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [i[1] for i in self.__get_sql_redata()]