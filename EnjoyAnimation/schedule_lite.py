import re,asyncio,threading,inspect
from datetime import datetime,timedelta
from typing import Callable,List,Literal

class task_infor:
    def __init__(self,type:str,time_units:dict,func_name:str,func,first_run,run_time=None,task_id=None) -> None:
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
        self.first_run=first_run
        
class schedule_lite:
    '''定时任务设置'''
    def __init__(self) -> None: 
        self.job_list:List[task_infor]=[]
        self.run_job_list=[]
        self.stop_tag=False
        self.lock=asyncio.Lock()
        self.thread=threading.Thread(target=self.task_run(),name="timetable")
        self.thread_list:list[threading.Thread]=[]
        self.thread.start()
    
    @property
    def status(self):
        return self.thread.is_alive()
    
    def add_job(self,type:Literal["interval","fixed","date"]=None,time_str:str=None,task_id:int=None,first_run:bool=False):
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
                
            first_run->是否立即运行一次
            
            Use_1:
            >>> @schedule_lite.add_job(“date”,"2021Y7M5d21h31m25s") #在2021年7月5日21时31分25秒执行一次
                async def func():...
            >>> @schedule_lite.add_job(“interval”,"7w23h20m") #每隔7个周23时20分执行一次
                async def func():...
            Use_2:
            >>> schedule_lite.add_job(“fixed”,"0w23h20m",123,True)(func) #先运行一次，在每周日23时20分执行一次，任务id为123
            >>> schedule_lite.add_job(“fixed”,"7M2w")(func,*args, **kwargs) #在每个7月周2的0时0分0秒执行一次
            >>> schedule_lite.add_job()(func)   #仅仅在多线程中立即执行一次
        '''
        time_units={"Y":None,
                    "m":None,
                    "w":None,
                    "d":None,
                    "H":None,
                    "M":None,
                    "S":None}
        zip_list={"Y":"Y","M":"m","w":"w","d":"d","h":"H","m":"M","s":"S"}
        if time_str:
            Matches=re.findall(r"(\d+)([a-zA-Z])",time_str)
            for Match in Matches:
                val,unit=Match
                if unit not in zip_list.keys():
                    raise ValueError(f"time_str中{unit}错误，格式不存在{unit}")
                else:
                    time_units[zip_list[unit]]=int(val)
        if type==None and time_str==None:
            first_run=True

        def add_job_1(func:Callable,*args, **kwargs):
            '''函数装饰器'''
            async def add_job_2():
                if inspect.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
            self.job_list.append(task_infor(type,time_units,func.__name__,add_job_2,task_id=task_id,first_run=first_run))
            return add_job_2
        return add_job_1

    async def append_job_list(self):
        '''准备运行列表'''
        while True:
            pop_list=[]
            if self.stop_tag:
                for t in self.job_list:
                    #重置运行时间
                    t.run_time=None
                break
            for item_i in range(len(self.job_list)):
                task=self.job_list[item_i]

                if task.first_run:
                    async with self.lock:
                        self.run_job_list.append(task.func)
                    if task.type==None:
                        pop_list.append(task)
                    task.first_run=False
                    
                    
                if task.type=="interval":
                    if not task.run_time:
                        task.time_units={unit:(val if val is not None else 0) for unit,val in task.time_units.items()}
                        year=task.time_units.get("Y")
                        month=task.time_units.get("m")
                        week=task.time_units.get("w")
                        day=task.time_units.get("d")
                        hour=task.time_units.get("H")
                        minute=task.time_units.get("M")
                        second=task.time_units.get("S")
                        task.all_tick=year*31536000+month*2592000+week*604800+day*86400+hour*3600+minute*60+second
                        task.run_time=datetime.now()+timedelta(seconds=task.all_tick)
                        task.run_time=task.run_time.strftime("%Y%m%w%d%H%M%S")
                    if datetime.now().strftime("%Y%m%w%d%H%M%S")==task.run_time:
                        async with self.lock:
                            self.run_job_list.append(task.func)
                        task.run_time=datetime.now()+timedelta(seconds=task.all_tick)
                        task.run_time=task.run_time.strftime("%Y%m%w%d%H%M%S")
                        
                elif task.type=="date" or task.type=="fixed":
                    if None in task.time_units.values():
                        None_0=False
                        for i,j in task.time_units.items():
                            if None_0 and j is None:
                                task.time_units[i]=0
                                continue
                            if j is not None:
                                None_0=True
                        task.time_units={i:j for i,j in task.time_units.items() if j !=None}
                    lock=True
                    for i,j in task.time_units.items():
                        if j != int(datetime.now().strftime(f"%{i}")):
                            lock=False
                            break
                    if lock and task.run_time!=datetime.now().strftime("%Y%m%w%d%H%M%S"):
                        async with self.lock:
                            self.run_job_list.append(task.func)
                        task.run_time=datetime.now().strftime("%Y%m%w%d%H%M%S")
                        if task.type=="date":
                            pop_list.append(task)
            self.job_list=[i for i in self.job_list if i not in pop_list]
            await asyncio.sleep(0.1)
            
    async def start_run_job_list(self):
        '''运行任务线程管理'''
        while True:
            if self.stop_tag:
                break
            async with self.lock:
                if self.run_job_list:
                    self.thread_list.append(threading.Thread(target=self.thread_run_func(*self.run_job_list)))
            pop_list=[]
            for i in self.thread_list:
                if not i.is_alive():
                    i.start()
                    pop_list.append(i)
            for i in pop_list:
                index=self.thread_list.index(i)
                self.thread_list.pop(index)
            async with self.lock:
                self.run_job_list=[]
            await asyncio.sleep(0.1)

    def task_run(self):
        '''副线程运行'''
        def _task_run():
            self.stop_tag=False
            self.thread_run_func(self.append_job_list,self.start_run_job_list)()
        if self.stop_tag:
            self.thread=threading.Thread(target=_task_run,name="timetable")
            self.thread.start()
        else:
            return _task_run
        
    def thread_run_func(self,*args):
        '''任务线程创建与运行'''
        def _():
            loop=asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks=[loop.create_task(task()) for task in args]
            loop.run_until_complete(asyncio.gather(*tasks))
            loop.stop()
            loop.close()
        return _
    
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
timetable=schedule_lite()
'''提供一个任务管理类的实例，使用时主要是函数'''