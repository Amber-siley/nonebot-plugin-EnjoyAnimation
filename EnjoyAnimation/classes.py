import json,sqlite3,re,difflib,requests
from datetime import datetime,timedelta
from urllib.parse import unquote
from typing import List
from .variable import (
    header,
    enjoy_log
)

class json_files:
    '''json管道'''
    def __init__(self,json_path) -> None:
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
    '''时间字符格式转换'''
    def __init__(self,time_str:str) -> None:
        self.iso_time_str=time_str
        self.__time_str_list=self.iso_time_str.replace(".","!.").replace('/',"/!").split("!")
        for i in self.__time_str_list:
            try:
                self.time_datetime=datetime.fromisoformat(i)
                break
            except ValueError:
                continue
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
    
class db_lite:
    '''动漫数据库管道'''
    def commit(func):
        '''数据修改后，向数据库提交修改的装饰器'''
        def commit_1(self,*args, **kwargs):
            func(self,*args, **kwargs)
            self.conn.commit()
        return commit_1
    
    @commit
    def __init__(self,db_path) -> None:
        self.__db_path=db_path
        self.conn=sqlite3.connect(self.__db_path)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''
                            create table if not exists animations(
                                id integer primary key,
                                pic_path text,
                                video_path text,
                                start_date date,
                                JP_start_date_UTC8 date,
                                CN_start_date date,
                                status,
                                qb_uid,
                                official_url text
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
                                name text not null primary key,
                                relation integer,
                                foreign key (relation) references animations(id)
                            )
                            ''')

    def test_name_db(self,names:list | str) -> bool:
        '''检测动漫信息是否存在数据库中'''
        back=False
        if isinstance(names,str):
            names=[names]
        tmp_list=self.universal_select_db(table="names",attribute="name")
        for i in names:
            if i in tmp_list:
                back=True
                break
        return back
    
    @commit
    def __universal_insert_db(self,table:str,**kwargs):
        '''通用插入数据库
            
            Kwargs：
                key 表示表中的列，
                
                value 表示insert into values()中的值，可以是sql语句“run(sql语句)”
                
            例：在animations中插入数据'animations',{"path":path,"JP_start_date_UTC8":JP_start_date_UTC8,"status":status,"official_url":official}
                插入sql语句’names‘,{"name":item,"relation":"run(select max(id) from animations)"}'''
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
                                 names:list[str],
                                 pic_path:str,
                                 video_path:str=None,
                                 start_date=None,
                                 JP_start_date_UTC8=None,
                                 CN_start_date=None,
                                 status=None,
                                 urls:list=None,
                                 official:str=None):
        '''插入animations数据'''
        really=True
        tmp_list=self.universal_select_db(table="names",attribute="name")
        
        def test_name(name_list:list | str)->tuple[bool,int]:
            '''检测是否不近似存在于names表中'''
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
                        enjoy_log.debug(f"{j} 的别称为 {i} 其中 {rou} 置信度为 {Match.ratio()}")
                        return False,num
            return True,None
        
        really,num=test_name(names)
        
        if pic_path and really:
            for i in names:
                i=re.sub(r"第\d期","",i)
                tmp=requests.get(url=f"https://zh.moegirl.org.cn/{i}",headers=header)
                Match=re.search(r'"title":\s*"([^"]*)"',tmp.text)
                if Match:
                    name=Match.group(1)
                    really,num=test_name(name)
                    if not really:
                        enjoy_log.debug(f"别称存在 {i}")

        if really:
            tmp_data={
                "pic_path":pic_path,
                "video_path":video_path,
                "start_date":start_date,
                "JP_start_date_UTC8":JP_start_date_UTC8,
                "CN_start_date":CN_start_date,
                "status":status,
                "official_url":official
            }
            self.__universal_insert_db('animations',**tmp_data)
            for i in names:
                if i not in self.universal_select_db("names","name",f'name="{i}"'):
                    tmp_data={
                        "name":i,
                        "relation":"run(select max(id) from animations)"
                    }
                    self.__universal_insert_db('names',**tmp_data)
                    enjoy_log.debug(f"{i} 未找到别称 已添加进数据库")
            for i in urls:
                if i not in self.universal_select_db("urls","url",f'url="{i}"'):
                    tmp_data={
                        "url":i,
                        "relation":"run(select max(id) from animations)"
                    }
                    self.__universal_insert_db('urls',**tmp_data)
        else:
            for i in names:
                if i not in self.universal_select_db("names","name",f'name="{i}"'):
                    tmp_data={
                        "name":i,
                        "relation":num
                    }
                    self.__universal_insert_db("names",**tmp_data)
            for i in urls:
                if i not in self.universal_select_db("urls","url",f'url="{i}"'):
                    tmp_data={
                        "url":i,
                        "relation":num
                    }
                    self.__universal_insert_db('urls',**tmp_data)
            tmp_data={
                "pic_path":pic_path
            }
            self.__universal_update_db("animations",f"id={num}",None,**tmp_data)
    
    @commit
    def update_animation_info_db(self,
                                 names:list,
                                 pic_path:str,
                                 video_path:str=None,
                                 start_date=None,
                                 JP_start_date_UTC8=None,
                                 CN_start_date=None,
                                 status=None,
                                 urls:list=None,
                                 official:str=None):
        '''更新animations数据'''
        tmp_data={
            "pic_path":pic_path,
            "video_path":video_path,
            "start_date":start_date,
            "JP_start_date_UTC8":JP_start_date_UTC8,
            "CN_start_date":CN_start_date,
            "status":status,
            "official_url":official
        }
        tmp_name=f"\"{names[0]}\""
        index=self.universal_select_db("names","relation",f"name={tmp_name}")[0]
        self.__universal_update_db("animations",f"id={index}",**tmp_data)
    
    @commit 
    def reset_table(self,table):
        '''重置表'''
        self.cursor.execute('''
                            truncate table ?
                            ''',(table))
    
    @commit
    def testafter_insert_db(self,**kwargs):
        '''检测是否存在，不存在则添加，存在则更新'''
        if not self.test_name_db(names=kwargs["names"]):
            #添加
            self.insert_animation_info_db(**kwargs)
        else:
            #更新
            self.update_animation_info_db(**kwargs)
    
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
    
    def universal_select_db(self,table:str,attribute:tuple | str,where:str="1=1",like:str=None)->list[tuple] | list:
        '''通用查询
        - table：表
        - attribute：返回属性可以是聚合函数，比如run(sum(id))
        - where：条件
        - like：近似值'''
        if isinstance(attribute,tuple):
            attribute=str(attribute)[1:-1].replace("'","")
        attribute=self.__run_command(r'run\((.*?\))\)',attribute)
        sql_text=f'''select {attribute} from {table} where {where} '''
        if like:
            sql_text+=f"like '{like}'"
        try:
            self.cursor.execute(sql_text)
        except sqlite3.OperationalError:
            enjoy_log.error(f"{sql_text}语法错误")
        sql_re=self.cursor.fetchall()
        lock=True
        for i in sql_re:
            if len(i)>1:
                lock=False
                break
        if lock:
            sql_re=[i for tup in sql_re for i in tup]
        return sql_re
    
    @commit
    def __universal_update_db(self,table:str,where:str=None,like:str=None,**kwargs):
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