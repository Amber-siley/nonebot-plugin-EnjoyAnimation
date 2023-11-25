function login(event)
    {
        event.preventDefault();
        var token=localStorage.getItem("token")
        var username=document.forms["loginForm"]["username"].value;
        var password=document.forms["loginForm"]["password"].value;
        console.log("username:"+username+"  password:"+password);
        if (username == "" || password == "" || username== null || password==null)
        {
            alert("请输入账号和密码");
        }
        else
        {
            fetch("/login",{
                method:"POST",
                headers:{"Content-Type":'application/json'},
                body:JSON.stringify(
                    {
                        "username":username,
                        "password":password,
                        "token":token
                    }
                )
            })
                .then(Response => Response.json())
                .then(result => {
                    if (result['status']=='lost'){
                        eval(result["tmps"]);
                    }
                    else{
                        rember_pw(username,password)
                        token=result["tmps"];
                        localStorage.setItem("token",token);
                        fetch("/User",{
                            method:"POST",
                            headers:{"Content-Type":'application/json'},
                            body:JSON.stringify(
                                {
                                    "username":username,
                                    "password":password,
                                    "token":token
                                }   
                            )
                        })
                        window.location.href='/User?username='+username+'&password='+password
                    }
                })
                .catch(Error => console.log(Error));
        }
    }

function add_new_user(){
    //跳转到注册用户页面
    window.location.href="/new_user"
}

function rember_pw(username,password){
    //记住账号与密码
    var rm=document.getElementById("rm");
    var bool_rm=rm.checked;
    if (bool_rm){
        localStorage.setItem("username",username);
        localStorage.setItem("password",password);
    }
}

function write_pw(username,password){
    //自动输入账号与密码
    var username_ele=document.getElementById("username");
    var password_ele=document.getElementById("password");
    username_ele.defaultValue=username;
    password_ele.defaultValue=password;
}
// function 