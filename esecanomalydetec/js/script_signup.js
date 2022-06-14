var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

//////////////////////senddataSignup//////////////////////

var userid = document.getElementById('username');
var password = document.getElementById('password');
var repassword = document.getElementById('repassword');
var select_val = document.querySelector('#userlevel');

function send_signup(){
    if(userid.value.length < 6){
        alert("Please fill User ID 6 digit");
        userid.value = "";
        password.value = "";
        repassword.value = "";
        return;
    }
    if (password.value != repassword.value){
        alert("Please check Re-Password");
        repassword.value = "";
        return;
    }
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://10.151.27.1:8086/users/signup', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
            if (response == "SignUp Success"){
                alert("SignUp Success");
                window.location.href = "../home.html";
            }
            else if(response == "User ID has exists"){
                alert("User ID has exists");
                userid.value = "";
                password.value = "";
                repassword.value = "";
            }
        }
        else if(xhr.status === 500){
            alert("SignUp Server Not Response")
            userid.value = "";
            password.value = "";
            repassword.value = "";
        }
    }
    var body = JSON.stringify({"user_Id": userid.value,"user_Password": password.value,
                                "user_Level": select_val.value});
    xhr.send(body);
}

function numonly(){
    this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\..*/g, '$1');
}

userid.addEventListener('input', numonly);

//////////////////////getLevel//////////////////////

var select = document.getElementById('userlevel');
var hold = document.createDocumentFragment();
var option = '';

function get_level(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://10.151.27.1:8086/users/level', false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            select_append(response.leveluser);
        }
    }
    xhr.send(response);
}

function select_append(a){
    for(var i = 0; i < a.length; i++){
        option += "<option value='"+a[i]+"'>"+a[i]+"</option>";
    }
    select.innerHTML = option;
}

/////////////////sequenceFunction////////////////////

get_level();