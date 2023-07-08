import re,asyncio,threading
from datetime import datetime,timedelta
from typing import Callable,List
import time

class task_infor:
    def __init__(self,type:str,time_units:dict,func_name:str,func,run_time=None,task_id=None) -> None:
        self.type=type
        self.time_units=time_units
        self.run_time=run_time         #下次运行时间
        self.all_tick=None
        self.func_name=func_name
        self.func=func
        if task_id:
            self.task_id=task_id
        else:
            self.task_id=id(func)
        
class schedute_lite:
    '''定时任务设置'''
    def __init__(self) -> None: 
        self.job_list:List[task_infor]=[]
        self.run_job_list=[]
        self.stop_tag=False
        self.look=asyncio.Lock()
        self.thread=threading.Thread(target=self.task_run(),name="timetable")
        self.thread.start()
        
    def add_job(self,type:str,time_str:str,task_id:int=None):
        '''type-->类型字符串:
            - （interval------------间隔执行）
            - （fixed----------固定时间执行）   
            - （date---规定时间仅执行一次）
            
            time_unit-->待解析的时间字符串(s-秒，m-分，h-时，d-天，w-周，M-月，Y-年):\\
            例子：
                - 2021Y7M5d21h31m25s ----> 2021年7月5日21时31分25秒
                - 7M23h20m ----------------------------------> 7月23时20分
                
            task_id-->添加任务的id
                - 默认为对象id，比如id(func),但是当若干个任务引用同一个函数后重写时，则只返回最新的id
                - 可自定义id
                
            Use:
            >>> @schedute_lite.add_job(“date”,"2021Y7M5d21h31m25s") #在2021年7月5日21时31分25秒执行一次
            >>> @schedute_lite.add_job(“interval”,"7M23h20m") #每隔7个月23时20分执行一次
            >>> @schedute_lite.add_job(“fixed”,"23h20m") #在每天23时20分执行一次
            >>> @schedute_lite.add_job(“fixed”,"7M23h") #在每个7月23时执行一次
        '''
        time_units={"Y":0,
                    "m":0,
                    "w":0,
                    "d":0,
                    "H":0,
                    "M":0,
                    "S":0}
        zip_list=["Y","M","w","d","h","m","s"]
        for new_unit,old_unit in zip(time_units,zip_list):
            Match=re.search(rf"(\d+){old_unit}",time_str)
            if Match:
                time_units[new_unit]=int(Match.group(1))

        def add_job_1(func:Callable):
            '''函数装饰器'''
            async def add_job_2(*args, **kwargs):
                return await func(*args, **kwargs)
            self.job_list.append(task_infor(type,time_units,func.__name__,add_job_2,task_id=task_id))
            return add_job_2
        return add_job_1

    async def appened_job_list(self):
        '''准备运行列表'''
        while True:
            pop_list=[]
            if self.stop_tag:
                for t in self.job_list:
                    t.run_time=None
                break
            for item_i in range(len(self.job_list)):
                task=self.job_list[item_i]
                if not task.run_time:
                    year=task.time_units.get("Y")
                    month=task.time_units.get("m")
                    week=task.time_units.get("w")
                    day=task.time_units.get("d")
                    hour=task.time_units.get("H")
                    minute=task.time_units.get("M")
                    second=task.time_units.get("S")
                    
                if task.type=="interval":
                    if not task.run_time:
                        task.all_tick=year*31536000+month*2592000+week*604800+day*86400+hour*3600+minute*60+second
                        task.run_time=datetime.now()+timedelta(seconds=task.all_tick)
                        task.run_time=task.run_time.strftime("%Y%m%w%d%H%M%S")
                    if datetime.now().strftime("%Y%m%w%d%H%M%S")==task.run_time:
                        async with self.look:
                            self.run_job_list.append(task.func)
                        task.run_time=datetime.now()+timedelta(seconds=task.all_tick)
                        task.run_time=task.run_time.strftime("%Y%m%w%d%H%M%S")
                        
                elif task.type=="date" or task.type=="fixed":
                    if 0 in task.time_units.values():
                        task.time_units={i:j for i,j in task.time_units.items() if j !=0}
                    lock=True
                    for i,j in task.time_units.items():
                        if j != int(datetime.now().strftime(f"%{i}")):
                            lock=False
                            break
                    if lock and task.run_time!=datetime.now().strftime("%Y%m%w%d%H%M%S"):
                        async with self.look:
                            self.run_job_list.append(task.func)
                        task.run_time=datetime.now().strftime("%Y%m%w%d%H%M%S")
                        if task.type=="date":
                            pop_list.append(task)
            self.job_list=[i for i in self.job_list if i not in pop_list]
            await asyncio.sleep(0.1)
            
    async def start_run_job_list(self):
        '''运行列表'''
        while True:
            if self.stop_tag:
                break
            for task in self.run_job_list:
                await task()
            async with self.look:
                self.run_job_list=[]
            await asyncio.sleep(0.1)
            
    def task_run(self):
        '''线程运行'''
        def _task_run():
            self.stop_tag=False
            loop=asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks=[loop.create_task(self.appened_job_list()),loop.create_task(self.start_run_job_list())]
            loop.run_until_complete(asyncio.gather(*tasks))
        if self.stop_tag:
            self.thread=threading.Thread(target=_task_run,name="timetable")
            self.thread.start()
        else:
            return _task_run
    def task_stop(self):
        '''停止任务'''
        self.stop_tag=True
    def remove_task(self,task_id:list | int):
        '''移除任务'''
        if isinstance(task_id,int):
            task_id=[task_id]
        for i in task_id:
            if i not in [j.task_id for j in self.job_list]:
                raise IndexError(f"无task_id为{i}的任务")
        self.job_list=[i for i in self.job_list if i.task_id not in task_id]
timetable=schedute_lite()