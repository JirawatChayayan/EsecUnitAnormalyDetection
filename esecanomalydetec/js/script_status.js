var HostIP = '192.168.137.159';


is_machinestop();
is_loglast();
var myInterval = setInterval(myTimer, 1000);

var currentStatusStopMc = false;

var jwt = localStorage.getItem("jwt");
if(jwt == null){
    window.location.href = '../index.html'
}

var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);

//////////////////////callStatusMachine//////////////////////

// var btn_status = document.getElementById('btnstatus');
var label_status = document.getElementById('labelstatus');
var img_status = document.getElementById('statusImg');
var menusignup = document.getElementById('signup');
var menuconfig = document.getElementById('menuconfig');

// btnstatus.style.display = "none";
menusignup.style.display = "none";
menuconfig.style.display = "none";

var level = localStorage.getItem("level");
if(level == 'Engineer'){
    menusignup.style.display = "block";
    menuconfig.style.display = "block";
}


// btn_status.style.backgroundColor = "#b0b0b0";
// btn_status.textContent = '';
img_status.src= "../img/release.png";

function changedisbtn(ev){
    if(ev == true){
        // btn_status.style.backgroundColor = "#05C905";
        // btn_status.textContent = "Release";
        img_status.src= "../img/stop.png";
        label_status.textContent = "Stop";
        label_status.style.color = "#ED6F0E";
        
    }
    else{
        // btn_status.style.backgroundColor = "#FF0005";
        // btn_status.textContent = "Stop";
        img_status.src= "../img/release.png";
        label_status.textContent = "Release";
        label_status.style.color = "#05C905"
    }
}

function is_machinestop(){
    var resp;
    var xhr2 = new XMLHttpRequest();
    xhr2.timeout = 2000;
    xhr2.open("GET", 'http://'+HostIP+':8081/camcontrol/is_stopMachine/',true);
    xhr2.onreadystatechange = function() {
        if(xhr2.readyState === 4 && xhr2.status === 200){
            resp = JSON.parse(xhr2.responseText);

            console.log(resp);
            currentStatusStopMc = resp;
            changedisbtn(currentStatusStopMc);
        }
        else if(xhr2.status === 500){
            alert("Machine Server Not Response");
        }
    }
    xhr2.send(resp);
}

function is_loglast(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.timeout = 2000;
    xhr.open("GET", 'http://'+HostIP+':8085/stop_release_log/last', true);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
            changedloglast(response);
        }
        else if(xhr.status === 500){
            alert("Machine Server Not Response");
        }
    }
    xhr.send(response);
}

var labelloglast = document.getElementById('laststopmsg');

function changedloglast(msg){
    labelloglast.textContent = "Last Stop Machine Message : "+msg.remark +" , "+msg.timestamp.replace("T", " ");
}
/////////////////sendrequestMachine////////////////////

function send_request_machine(){
    userID = localStorage.getItem("user_id");
    userLevel = localStorage.getItem("level");
    if(userLevel == "" || userLevel == null || userID == "" || userID == null)
    {
        alert("Please check login.");
        return;
    }
    var response;
    var xhr = new XMLHttpRequest();
    xhr.timeout = 2000;
    var msg = "";
    if(!currentStatusStopMc){
        msg = "Stop machine by "+userLevel+" EN "+userID;
    }
    else{
        msg = "Release machine by "+userLevel+" EN "+userID;
    }

    xhr.open("GET", 'http://'+HostIP+':8081/camcontrol/stopMC/'+!currentStatusStopMc+'/msg/'+msg, true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            is_machinestop();
            is_machinestop();
            is_machinestop();
        }
        else if(xhr.status === 500){
            alert("Machine Server Not Response");
        }
    }
    xhr.send(response);
}

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

/////////////////sequenceFunction////////////////////


function myTimer() 
{
    // const d = new Date();
    // document.getElementById("demo").innerHTML = d.toLocaleTimeString();
    is_loglast();
    is_machinestop();
}
function myStop() 
{
    clearInterval(myInterval);
}


// 
