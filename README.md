# nonebot-plugin-EnjoyAnimation
这是一个基于nonebot的qq-bot动漫番剧插件

### 插件依赖
插件：nonebot-plugin-apscheduler nonebot-plugin-htmlrender

库：bs4 requests

### 安装插件
由于并没有上传至PyPI，只能手动安装

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

配置文件为.env.dev（默认为此文件，.env中可以修改）文件
```
animation_admin=123456789            #管理员qq号
animation_time= [8,30]               #订阅提醒时间，[0~23,0~59]
animation_default_return_img=false   #一些番剧信息是否以图片发送（配置为false时，检测到风控会自动以图片进行发送）
```
