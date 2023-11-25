from flask import Flask, request, jsonify,render_template,session,redirect,url_for
from os import path
from .schedule_lite import timetable
from .classes import db_lite
from .variable import(
    enjoy_log,
    ani_config,
    animation_path,
    random_str
)

web_db=db_lite(animation_path)
admin=ani_config.admin
admin_pw=ani_config.admin_pw
file=path.dirname(path.realpath(__file__))
template=path.join(file,"EnjoyAnimation_web")
static=path.join(template,"static")
app = Flask(__name__,template_folder=template,static_folder=static)

def find_user(username,password)-> list or False:
    '''查询用户'''
    return web_db.universal_select_db(table="enjoy_users",attribute=("username","password"),where=f'''username="{username}"and password="{password}"''')

def find_admin()->list:
    '''查询管理员'''
    admin=web_db.universal_select_db(table="enjoy_users",attribute=("username","password"))
    try:
        admin_name=admin[0]
        admin_pw=admin[1]
        return [admin_name,admin_pw]
    except IndexError:
        return False
        

def upgrade_user(user,new_pw):
    '''更新密码'''
    updata={
        "username":user,
        "password":new_pw
    }
    web_db.universal_update_db(table="enjoy_users",where=f'''username="{user}"''',**updata)
    
def insert_user(user:str,pw:str):
    '''插入用户'''
    insert_data={
        "username":user,
        "password":pw
    }
    web_db.universal_insert_db(table="enjoy_users",**insert_data)

def admin_manage():
    '''管理员账户管理'''
    admin=find_admin()
    if admin:
        insert_user(ani_config.admin,ani_config.admin_pw)
    if [ani_config.admin,ani_config.admin_pw] != admin:
        upgrade_user(ani_config.admin,ani_config.admin_pw)
    
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
re_data={"status":None,"tmps":None}
@app.route('/',methods=["GET"])
def index_html():
    return redirect(url_for("login_index"))

@app.route('/login', methods=['GET', 'POST'])
def login_index():
    if request.method=="POST":
        data=request.get_json()
        username=data["username"]
        password=data["password"]
        token=data["token"]
        if find_user(username,password):
            #返回用户页面
            re_data["status"]="success"
            token=random_str(ani_config.web_token_length)
            re_data["tmps"]=token
        else:
            re_data["status"]="lost"
            re_data["tmps"]="alert('账号或者密码错误')"
        return re_data
    return render_template("login.html")

@app.route('/new_user',methods=['GET'])
def new_user():
    return render_template('new_user.html')
    
@app.route('/User',methods=["POST","GET"])
def user():
    if request.method=="GET":
        username=request.args.get("username")
        password=request.args.get("password")
        if find_user(username,password):
            return render_template("user.html")
    return "0"
        
def web_run():
    admin_manage()
    app.run(host="0.0.0.0",port=5555)
if ani_config.web_ui:
    timetable.add_job()(web_run)
    enjoy_log.info(f"Web UI {__name__} start")