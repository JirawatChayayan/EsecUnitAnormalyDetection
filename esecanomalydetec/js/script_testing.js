var HostIP = '192.168.137.159';





var jwt = localStorage.getItem("jwt");
if(jwt == null){
    window.location.href = '../index.html'
}

var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);

/////////////////progressBar////////////////////

var setprogressbar;
var btnstatus = document.getElementById('btn-status');
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

function startwaiting(){
    btnstatus.style.display = "block";
    btnstatus.textContent = 'Waiting';
    btnstatus.style.backgroundColor = "#008CFF";
}

function stopwaiting(){
    btnstatus.textContent = 'Finish';
    btnstatus.style.backgroundColor = '#27d86c';
}

function waitingerror(){
    btnstatus.textContent = 'Error';
    btnstatus.style.backgroundColor = '#FF0005';
}

/////////////////slideshowImage////////////////////

var imagelist = [];
var imageIndex = 0;
var imagelistlength;
var imageshow = document.getElementById('imagedisplay');
var cbautotest = document.getElementById('autotest');

function imagelistXHR(a){
    var xhr = new XMLHttpRequest();
    var apiurl = 'http://'+HostIP+':8082/filecontrol/images/SetupTest';
    xhr.open("GET", apiurl, false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            imagelist = JSON.parse(xhr.responseText);
            imagelistlength = imagelist.imgList.length - 1;
            if(a == 'lastimage'){
                if(imagelistlength == -1){
                    imageshow.src = "../img/no-image.jpg";
                    imagecount.textContent = "";
                }
                else{
                    currentImage(imagelistlength);
                }
            }
            else{
                if(imagelistlength == -1){
                    imageshow.src = "../img/no-image.jpg";
                    imagecount.textContent = "";
                }
                else{
                    currentImage(imageIndex);
                }
            }
        }
    }
    xhr.send(imagelist);
}

function changeImage(n){
    if(cbautotest.checked == true){
        currentImage(imageIndex += n);
        testingAnomaly();
    }
    else{
        currentImage(imageIndex += n);
    }
}

var imagenametest;
var imagecount = document.getElementById('imagecount');

function currentImage(n){
    if(n < 0) {imageIndex = imagelistlength;n = imagelistlength;}
    if(n > imagelistlength) {imageIndex = 0;n = 0;}
    var imagename = imagelist.imgList[n].replace(/^.*[\\\/]/, '');
    imagenametest = imagelist.imgList[n];
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://'+HostIP+':8082/filecontrol/getimage', true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            imageshow.src = JSON.parse(xhr.responseText);
        }
    }
    var body = JSON.stringify({"mode": "SetupTest","imgfilename": imagename});
    xhr.send(body);
    imagecount.textContent = "("+(n+1)+"/"+(imagelistlength+1)+")";
}

/////////////////captureImage////////////////////

function captureimageTest(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8081/camcontrol/saveImageTest', false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
        }
    }
    xhr.send(response);
    setTimeout(function() {imagelistXHR('lastimage')},50); 
}

/////////////////callboxConfig////////////////////

var boxcrop;
var rejectthreshold;

function callConfig(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8084/config', false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            boxcrop = response.bboxCrop;
            rejectthreshold = response.rejectThreshold;
        }
        else if(xhr.status === 500){
            alert("Config Server Not Response");
        }
    }
    xhr.send(response);
}

/////////////////testingAPI////////////////////
var imageres = document.getElementById('imageresult');
var imageheat = document.getElementById('imageheat');

function testingAnomaly(){
    var response;
    var xhr = new XMLHttpRequest();
    startwaiting();
    callConfig();
    xhr.open("POST", 'http://'+HostIP+':8083/ai/infer_disp', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            score = [];
            response = JSON.parse(xhr.responseText);
            score = response[0];
            stopwaiting();
            scoreResult(score.scoreMin , score.scoreMax);
            imageres.src = score.resultImgInput;
            imageheat.src = score.resultImgHeat;
            console.log(score);
        }
        else if(xhr.status === 500){
            alert("Test Server Not Response");
            waitingerror();
        }
        else if(xhr.status !== 200){
            alert("No Model for Testing");
            waitingerror();
        }
    }
    var body = JSON.stringify({"imgList": [imagenametest],"bbox": boxcrop});
    xhr.send(body);
}

/////////////////scoreResult////////////////////

score = [];
var scoremin = document.getElementById('scoremin');
var scoremax = document.getElementById('scoremax');

scoremin.style.display = "inline-block";
scoremax.style.display = "inline-block";

function scoreResult(a,b){
    scoremin.textContent = "Score Min : " + a;
    scoremax.textContent = "Score Max : " + b;
    console.log(rejectthreshold);
    if(b<=rejectthreshold){
        btnstatus.textContent = "Good";
        btnstatus.style.backgroundColor = "#27d86c";
    }
    else{
        btnstatus.textContent = "Reject";
        btnstatus.style.backgroundColor = "#FF0000";
    }
}

/////////////////deleteImage////////////////////

function deletecurrentImage(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", 'http://'+HostIP+':8082/filecontrol/images/', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
        }
    }
    var body = JSON.stringify({"mode": "SetupTest","imgList": [imagenametest]});
    xhr.send(body);
    imagelistXHR('lastimage'); 
}

function deleteallImage(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", 'http://'+HostIP+':8082/filecontrol/images/', true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
            if(response == true){
                imageshow.src = "../img/no-image.jpg";
                imagecount.textContent = "";
            }
        }
    }
    var body = JSON.stringify({"mode": "SetupTest","imgList": imagelist.imgList});
    xhr.send(body);
}

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

/////////////////sequenceFunction////////////////////

callConfig();
imagelistXHR();
