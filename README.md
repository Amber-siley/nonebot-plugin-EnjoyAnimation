# nonebot-plugin-EnjoyAnimation
这是一个基于nonebot，gocqhttp的qq-bot动漫番剧插件

### 插件依赖
插件：```nonebot-plugin-apscheduler nonebot-plugin-htmlrender```

库：```bs4 requests```

### 安装插件
#### 自动安装

安装此插件：
```
pip install EnjoyAnimation
（若镜像站没有则使用以下指令进行安装）
pip install --index-url https://pypi.org/simple EnjoyAnimation
```
安装第三方插件依赖：
请在bot根目录运行此指令
```
nb plugin install nonebot-plugin-apscheduler
```
```
nb plugin install nonebot-plugin-htmlrender
```
添加插件：
```
在pyproject.toml文件中将EnjoyAnimation添加进plugins中
plugins = ["EnjoyAnimation"]
```
#### 手动安装

1. 安装第三方库
```
pip install bs4
```
```
pip install requests
```
2. 安装第三方插件

请在bot根目录运行此指令
```
nb plugin install nonebot-plugin-apscheduler
```
```
nb plugin install nonebot-plugin-htmlrender
```
3. 安装此插件

将```EnjoyAnimation.py```放在```bot根目录\插件文件夹名（默认src）\plugins\```下，进行本地加载，如未加载此插件，检查```pyproject.toml```文件中是否存在配置项，无则添加
```
plugin_dirs = ["src/plugins"]
```
### 配置插件

插件有三项必须配置项

配置文件为.env.X（默认为[初学者模式创建时]```.env.prof```或者[插件作者创建时]```.env.dev```，具体```.env```中可以修改）文件
```
animation_admin=123456789            #管理员qq号
animation_time= [8,30]               #订阅提醒时间，[0~23,0~59]
animation_default_return_img=false   #一些番剧信息是否以图片发送（配置为false时，检测到风控会自动以图片进行发送）
```
### 插件使用
```
    Commands:【可选参数】
    #番剧信息 【当前季度的番剧】
    #番剧更新 【强制更新番剧信息】
    #今日新番 【今日更新的番剧】
    #新增订阅 【订阅=追番提醒】
    #取消订阅
    ==================== 
    #番剧查询 【番剧信息中的序号】
    #新增追番 【番剧信息中的序号】
    #我的追番 【查看追番列表】
    #取消追番
```
