//////////////////////senddataLogin//////////////////////
// var jwt = localStorage.getItem("jwt");

// if(jwt != null){
//     window.location.href = '../page/login.html'
// }

var userid = document.getElementById('username');
var password = document.getElementById('password');

function send_login(){
    var response;
    if(userid.value == "" || password.value == ""){
        alert("Please fill out User ID and Password please");
        return;
    }
    var xhr = new XMLHttpRequest();
    var base64pass = btoa(String(password.value));
    xhr.open("POST", 'http://10.151.27.1:8086/users/login', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            set_localjwt(response);
        }
        else if(xhr.status === 401){
            alert("Check User ID or Password");
            password.value = "";
        }
        else if(xhr.status === 500){
            alert("Server Not Response");
        }
    }
    var body = JSON.stringify({"user_Id": userid.value,"user_Password": base64pass});
    xhr.send(body);
}

function numonly(){
    this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\..*/g, '$1');
}

userid.addEventListener('input', numonly);

function set_localjwt(token){
    var re = null
    try{
        var decoded = decode(token.accesstoken);
        var level = decoded.user_level;
        var expires = decoded.exprires;
        var userID = userid;
        // var time = Date.now()/1000;
        // var timeexpires = (expires - time)*1000;
        console.log(expires);
        localStorage.setItem("jwt", token);
        localStorage.setItem("level", level);
        localStorage.setItem("expires", expires);
        localStorage.setItem("user_id", userid.value);
        window.location.href = "../home.html"
        re = true
    }
    catch(err){
        re = false
        userid.value = "";
        password.value = "";
        alert("Login fail");
    }

    return re
}

function decode(token){
    var base64url = token.split('.')[1];
    var base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonpayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%'+ ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonpayload);
}