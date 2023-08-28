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
                        token=result["tmps"];
                        localStorage.setItem("token",token);
                        fetch("/User",{
                            method:"POST",
                            headers:{"Content-Type":'application/json'},
                            body:JSON.stringify(
                                {
                                    "token":token
                                }   
                            )
                        })
                            .then(Response => Response.json())
                            .then(res => {
                                if (res["status"]=="success"){
                                    eval(res["tmps"])
                                }
                            })
                    }
                })
                .catch(Error => console.log(Error));
        }
    }