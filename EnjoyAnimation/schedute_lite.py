import re,asyncio,threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from typing import Callable


class schedute_lite:
    '''定时任务设置'''
    def __init__(self) -> None: 
        self.job_list=set()
        # self.thread_local=threading.local()
        self.thread=threading.Thread(target=self.task_run)
    def add_job(self,type:str,time_str:str):
        '''type-->类型字符串:
            - （interval------------间隔执行）
            - （fixed----------固定时间执行）   
            - （date---规定时间仅执行一次）
            
            time_unit-->待解析的时间字符串(s-秒，m-分，h-时，d-天，w-周，M-月，Y-年):\\
            例子：
                - 2021Y7M5d21h31m25s ----> 2021年7月5日21时31分25秒
                - 7M23h20m ----------------------------------> 7月23时20分
                
            Use:
            >>> @schedute_lite.add_job(“date”,"2021Y7M5d21h31m25s") #在2021年7月5日21时31分25秒执行一次
            >>> @schedute_lite.add_job(“interval”,"7M23h20m") #每隔7个月23时20分执行一次
            >>> @schedute_lite.add_job(“fixed”,"23h20m") #在每天23时20分执行一次
            >>> @schedute_lite.add_job(“fixed”,"7M23h") #在每个7月23时执行一次
        '''
        time_units={"Y":0,
                    "M":0,
                    "w":0,
                    "d":0,
                    "h":0,
                    "m":0,
                    "s":0}
        for unit in time_units:
            Match=re.search(rf"(\d+){unit}",time_str)
            if Match:
                time_units[unit]=int(Match.group(1))
                
        year=time_units.get("Y")
        month=time_units.get("M")
        week=time_units.get("w")
        day=time_units.get("d")
        hour=time_units.get("h")
        minute=time_units.get("m")
        second=time_units.get("s")
        
        def add_job_1(func:Callable):
            async def add_job_2(*args, **kwargs):
                if type=="interval":
                    '''间隔'''
                    all_time_second=year*31536000+month*2592000+week*604800+day*86400+hour*3600+minute*60+second
                    while True:
                        await asyncio.sleep(all_time_second)
                        await func(*args, **kwargs)
                        
                elif type=="date":
                    '''一次性 固定时间'''
                    time_list=[f"{value}" if value>9 else f"0{value}" for key,value in time_units.items()]
                    while True:
                        now=datetime.strftime(datetime.now(),"%Yy%mM0%ww%dd%Hh%Mm%Ss")
                        now_list=re.finditer(r"(\d+)[a-zA-Z]",now)
                        tmp,lock=0,False
                        for j,i in zip(now_list,time_list):
                            tmp+=1
                            if not(i=="00" or i==j.group(1)):
                                break
                            if tmp==7:
                                lock=True
                        if lock:
                            await func(*args, **kwargs)
                            self.job_dict.pop(func.__name__)
                            break
                        await asyncio.sleep(1)
            self.job_list.add(add_job_2)
            return add_job_2
        return add_job_1
    
    def task_run(self):
        # self.thread_local.job_list=set([])
        job_list=set()
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            if job_list.__len__()==0:
                job_list={loop.create_task(i()) for i in self.job_list}
            else:
                done,job_list=loop.run_until_complete(asyncio.wait(job_list,return_when=asyncio.ALL_COMPLETED))
                # for i in done:
                #     if i.exception():
                #         return i.exception()
                #     else:
                #         return i.result()
            if job_list.__len__()==0:
                break
timetable=schedute_lite()
timetable.thread.start()