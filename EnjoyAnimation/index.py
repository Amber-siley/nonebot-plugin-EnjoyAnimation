from flask import Flask, request, jsonify,render_template,session,redirect,url_for
from os import path
from .schedule_lite import timetable
from .variable import(
    enjoy_log
)

file=path.dirname(path.realpath(__file__))
template=path.join(file,"EnjoyAnimation_web")
static=path.join(template,"static")
app = Flask(__name__,template_folder=template,static_folder=static)

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
        if username =="admin" and password =="123456":
            if token!=None:
                token="test"
                re_data["status"]="success"
                re_data["tmps"]=token
                return re_data
            else:
                token=123456
                re_data["status"]="success"
                re_data["tmps"]=token
                return re_data
        else:
            re_data["status"]="lost"
            re_data["tmps"]="alert('账号或者密码错误')"
            return re_data
    else:
        return render_template("login.html")

@app.route('/User',methods=["POST","GET"])
def user():
    if request.method=="POST":
        data=request.get_json()
        token=data["token"]
        if token in [123456,'test']:
            re_data["status"]="success"
            re_data["tmps"]='alert("登录成功")'
            return re_data
        
def web_run():
    app.run(host="0.0.0.0")
    
timetable.add_job()(web_run)
enjoy_log.info(f"Web UI {__name__} start")