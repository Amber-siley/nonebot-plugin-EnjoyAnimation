import json,sqlite3,re
from datetime import datetime,timedelta

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
    def datatime_operation(self,oper:str,unit:str,var:int):
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
    '''数据库管道'''
    def __init__(self,db_path) -> None:
        self.__db_path=db_path
        self.conn=sqlite3.connect(self.__db_path)
        self.cursor=self.conn.cursor()
        self.cursor.execute('''
                            create table if not exists animations(
                                id integer primary key,
                                path text not null,
                                start_date date,
                                JP_start_date_UTC8 date,
                                CN_start_date,
                                end_date date,
                                official_url text
                            )
                            ''')
        self.cursor.execute(''' 
                            create table if not exists urls(
                                id integer primary key,
                                url text not null,
                                relation integer,
                                foreign key (relation) references animations(id)
                            )
                            ''')
        self.cursor.execute('''
                            create table if not exists names(
                                id integer primary key,
                                name text not null,
                                relation integer,
                                foreign key (relation) references animations(id)
                            )
                            ''')
        self.conn.commit()
    def test_name_db(self,names:list) -> bool:
        '''检测动漫名字存在数据库中'''
        back=False
        self.cursor.execute('''
                            select name from names
                            ''')
        tmp_list=self.cursor.fetchall()
        for i in names:
            if i in [all_list for sublist in tmp_list for all_list in sublist]:
                back=True
                break
        return back
    def __universal_insert_db(self,table:str,**kwargs):
        '''通用插入数据库
            
            Kwargs：
                key 表示表中的列，
                
                value 表示insert into values()中的值，可以是sql语句“run(sql语句)”
                
            例：在animations中插入数据'animations',{"path":path,"JP_start_date_UTC8":JP_start_date_UTC8,"end_date":end_date,"official_url":official}
                插入sql语句’names‘,{"name":item,"relation":"run(select max(id) from animations)"}'''
        attrbute=str(tuple(kwargs.keys()))
        value=str(tuple(i if i is not None else 'NULL' for i in list(kwargs.values()))).replace("'NULL'","NULL")
        sql_text=f'''
        insert into {table} {attrbute}
        values{value}
        ''' 
        run=r"'run(.*?)'"
        run_command=re.search(run,sql_text)
        if run_command:
            sql_text=re.sub(run,run_command.group(1),sql_text)
        try:
            self.cursor.execute(sql_text)
        except sqlite3.OperationalError:
            print(sql_text)
        self.conn.commit()
        
    def insert_animation_info_db(self,names:list,
                                 path:str,
                                 start_date=None,
                                 JP_start_date_UTC8=None,
                                 CN_start_date=None,
                                 end_date=None,
                                 urls:list=None,
                                 official:str=None):
        '''插入数据'''
        tmp_data={
            "path":path,
            "start_date":start_date,
            "JP_start_date_UTC8":JP_start_date_UTC8,
            "CN_start_date":CN_start_date,
            "end_date":end_date,
            "official_url":official
        }
        self.__universal_insert_db('animations',**tmp_data)
        for i in names:
            tmp_data={
                "name":i,
                "relation":"run(select max(id) from animations)"
            }
            self.__universal_insert_db('names',**tmp_data)
        for i in urls:
            tmp_data={
                "url":i,
                "relation":"run(select max(id) from animations)"
            }
            self.__universal_insert_db('urls',**tmp_data)
        self.conn.commit()
        
    # def testafter_insert_db(self,names:list,path:str,JP_start_date_UTC8=None,CN_start_date=None,end_date=None,urls:list=None,official:str=None):
    def testafter_insert_db(self,**kwargs):
        '''检测是否存在，不存在则添加，存在则更新'''
        if not self.test_name_db(names=kwargs["names"]):
            #添加
            self.insert_animation_info_db(**kwargs)
        else:
            #更新
            pass
    def read_db(self):
        pass
    def close_db(self):
        '''关闭数据库'''
        self.cursor.close()
        self.conn.close()