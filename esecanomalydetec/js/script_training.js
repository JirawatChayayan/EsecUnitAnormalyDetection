var HostIP = '192.168.137.159';




var jwt = localStorage.getItem("jwt");

if(jwt == null){
    window.location.href = '../index.html'
}

var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);
var menusignup = document.getElementById('signup');
var menuconfig = document.getElementById('menuconfig');
var userID = localStorage.getItem("user_id");
var level = localStorage.getItem("level");

menusignup.style.display = "none";
menuconfig.style.display = "none";

if(level == 'Engineer'){
    menusignup.style.display = "block";
    menuconfig.style.display = "block";
}

/////////////////progressBar////////////////////

var setprogressbar;
var progress = document.getElementById('custom-bar');
var btnstatus = document.getElementById('btn-status');

progress.style.display = "none";
btnstatus.style.display = "none";

function startwaiting(){
    setprogressbar = setInterval(progressbar, 400);
    progress.style.display = "block";
    btnstatus.style.display = "inline";
    btnstatus.textContent = 'Waiting';
    btnstatus.style.backgroundColor = "#008CFF";
    function progressbar(){
        if (progress.value < progress.max) {
            progress.value += 20;
        }
        else {
            progress.value = 0;
        }
    }
}

function stopwaiting(){
    progress.value = progress.max;
    btnstatus.textContent = 'Finish';
    btnstatus.style.backgroundColor = '#27d86c';
    clearInterval(setprogressbar);
    progress.style.display = "None";
}

function waitingerror(){
    progress.value = progress.max;
    btnstatus.textContent = 'Error';
    btnstatus.style.backgroundColor = '#FF0005';
    clearInterval(setprogressbar);
    progress.style.display = "None";
}

/////////////////canvasfunction////////////////////

var canvas = document.getElementById('myCanvas');
var ctx = canvas.getContext('2d');
var imageObj = new Image();
//var realsize = {};
var imgObjSize = []
var canvasSize = []

// var canvas2 = document.getElementById('testcanvas');
// var ctx2 = canvas2.getContext('2d');
// var imageObj2 = new Image();

// function testcanv(rectsave){
//     canvas2.height = imageObj.height;
//     canvas2.width = imageObj.width;
//     ctx2.drawImage(imageObj, 0, 0, imageObj.width, imageObj.height);
//     ctx2.strokeStyle = "#27EB16";
//     ctx2.lineWidth = "2";
//     ctx2.strokeRect(rectsave.saveX1, rectsave.saveY1, rectsave.saveX2-rectsave.saveX1, rectsave.saveY2-rectsave.saveY1);
// }


function showImg(img){
    var resolutionFactor = img.width/img.height;
    canvas.height =  parseInt(605/resolutionFactor);
    canvas.width = 605;
    //console.log([0, 0, canvas.width, canvas.height]);
    ctx.drawImage(imageObj, 0, 0, canvas.width, canvas.height);
    canvasSize = [canvas.width, canvas.height]
}


imageObj.onload = function() {
    
    showImg(imageObj);
    imgObjSize = [imageObj.width,imageObj.height];
    //realsize.x = imageObj.width/650;
    //realsize.y = 2;

    // canvas.height = imageObj.height/2;
    // canvas.width = 605;    userID = localStorage.getItem("user_id");
};

var rect = {};
var rectsave = {};
var rectsend = [];
var drag = false;
var rectStartXArray = new Array() ;
var rectStartYArray = new Array() ;
var rectWArray = new Array() ;
var rectHArray = new Array() ;
var btnsave = document.getElementById('btnroi');
var btnclear = document.getElementById('btnclearroi');

btnclear.style.display = "none";

function disroisave(ev){
    btnsave.disabled = ev;
    if(btnsave.disabled == true){
        btnsave.style.backgroundColor = "#b0b0b0"
    }
    else{
        btnsave.style.backgroundColor = "#5103d1"
    }
}

function clearroi(){
    ctx.clearRect(rect.startX, rect.startY, rect.w, rect.h);
    showImg(imageObj);
    disroisave(true);
    btnclear.style.display = "none";
}

function startroi(){
    var startw = (rectsend[2]-canvas.offsetLeft)-rectsend[0];
    var starth = (rectsend[3]-canvas.offsetTop)-rectsend[1];
    console.log(rectsend[0],rectsend[1],rectsend[2],rectsend[3]);
    ctx.beginPath();
    ctx.strokeStyle = "#27EB16";
    ctx.lineWidth = "1";
    ctx.strokeRect(rectsend[0], rectsend[1], startw, starth);
}

function init() {
    canvas.addEventListener('mousedown', mouseDown, false);
    canvas.addEventListener('mouseup', mouseUp, false);
    canvas.addEventListener('mousemove', mouseMove, false);
    disroisave(true);
}

function mouseDown(e) {
    rect.startX = e.pageX - this.offsetLeft;
    rect.startY = e.pageY - this.offsetTop;
    drag = true;
}
function mouseUp(e) {
    rect.endX = e.pageX - this.offsetLeft;
    rect.endY = e.pageY - this.offsetTop;
    drag = false;
    console.log(rect.startX,rect.startY,rect.endX,rect.endY);
    console.log('imgSize ' +imgObjSize);
    console.log('canvasSize '+canvasSize);

    var sizefactor = imgObjSize[0]/canvasSize[0];


    if(rect.startX == rect.endX && rect.startY == rect.endY){
        return;
    }
    else{
        rectsend = [];
        var x1 = rect.startX;
        var y1 = rect.startY;

        var x2 = rect.endX;
        var y2 = rect.endY;
        
        var normalRect = [];


        //x1,y1
        //  |------|
        //  |      |
        //  |______|
        //        x2,y2
        if(x2>x1 && y2>y1)
        {
            normalRect = [x1,y1,x2,y2];
        }
        //x2,y2
        //  |------|
        //  |      |
        //  |______|
        //        x1,y1
        else if(x1>x2 && y1>y2)
        {
            normalRect = [x2,y2,x1,y1];
        }
        //       x2,y2
        //  |------|
        //  |      |
        //  |______|
        //x1,y1
        else if(x2>x1 && y1>y2)
        {
            normalRect = [x1,y2,x2,y1];
        }
        //       x1,y1
        //  |------|
        //  |      |
        //  |______|
        //x2,y2
        else if(x1>x2 && y2>y1)
        {
            normalRect = [x2,y1,x1,y1];
        }
        for (var i = 0; i < normalRect.length; i++) 
        {
            normalRect[i] = parseInt(normalRect[i]*sizefactor);
        } 
        rectsend.push(normalRect[0],normalRect[1],normalRect[2],normalRect[3])
        
        console.log('normalize '+ rectsend);
        
        rect.roistartx = rect.startX;
        rect.roistarty = rect.startY;
        rect.roiw = (e.pageX - this.offsetLeft) - rect.startX;
        rect.roih = (e.pageY - this.offsetTop) - rect.startY;
        console.log(rect.roiw,rect.roih);


        ///bottomright to topleft
        // if(rect.endX < rect.startX && rect.endY < rect.startY ){
        //     rectsave.saveX1 = rect.endX*realsize.x;
        //     rectsave.saveY1 = rect.endY*realsize.y;
        //     rectsave.saveX2 = ((rect.startX-rect.endX)*realsize.x)+rectsave.saveX1;
        //     rectsave.saveY2 = ((rect.startY-rect.endY)*realsize.y)+rectsave.saveY1;
        //     rectsend.push(rectsave.saveX1,rectsave.saveY1,rectsave.saveX2,rectsave.saveY2)
        // }
        // ///topright to bottomleft
        // if (rect.endX < rect.startX && rect.endY > rect.startY){
        //     rectsave.saveX1 = rect.endX*realsize.x;
        //     rectsave.saveY1 = rect.startY*realsize.y;
        //     rectsave.saveX2 = ((rect.startX-rect.endX)*realsize.x)+rectsave.saveX1;
        //     rectsave.saveY2 = ((rect.endY-rect.startY)*realsize.y)+rectsave.saveY1;
        //     rectsend.push(rectsave.saveX1,rectsave.saveY1,rectsave.saveX2,rectsave.saveY2)
        // }
        // ///bottomleft to top right
        // if(rect.endX > rect.startX && rect.endY < rect.startY){
        //     rectsave.saveX1 = rect.startX*realsize.x;
        //     rectsave.saveY1 = rect.endY*realsize.y;
        //     rectsave.saveX2 = ((rect.endX-rect.startX)*realsize.x)+rectsave.saveX1;
        //     rectsave.saveY2 = ((rect.startY-rect.endY)*realsize.y)+rectsave.saveY1;
        //     rectsend.push(rectsave.saveX1,rectsave.saveY1,rectsave.saveX2,rectsave.saveY2)
        // }
        // ///topleft to bottomright
        // if(rect.endX > rect.startX && rect.endY > rect.startY){
        //     rectsave.saveX1 = rect.startX*realsize.x;
        //     rectsave.saveY1 = rect.startY*realsize.y;
        //     rectsave.saveX2 = ((rect.endX-rect.startX)*realsize.x)+rectsave.saveX1;
        //     rectsave.saveY2 = ((rect.endY-rect.startY)*realsize.y)+rectsave.saveY1;
        //     rectsend.push(rectsave.saveX1,rectsave.saveY1,rectsave.saveX2,rectsave.saveY2)
        // }
    }
}

function mouseMove(e) {
    if(!drag){
        return;
    }
    
    ctx.clearRect(rect.startX, rect.startY, rect.w, rect.h);
    showImg(imageObj);
    //ctx.drawImage(imageObj, 0, 0, 605, imageObj.height/2);
    rect.w = (e.pageX - this.offsetLeft) - rect.startX;
    rect.h = (e.pageY - this.offsetTop) - rect.startY;
    draw();
    disroisave(false);
    btnclear.style.display = "block";
}
function draw() {
    ctx.beginPath();
    ctx.strokeStyle = "red";
    ctx.lineWidth = "1";
    ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
}

function saveROI() {
    send = sendROI();
    if(send == true){
        ctx.clearRect(rect.roistartx, rect.roistarty, rect.roiw, rect.roih);
        showImg(imageObj);
        ctx.beginPath();
        ctx.strokeStyle = "#27EB16";
        ctx.lineWidth = "1";
        ctx.strokeRect(rect.roistartx, rect.roistarty, rect.roiw, rect.roih);
        console.log(rectsend);
        console.log(send);
        alert("ROI Save");
    }
    else{
        return;
    }
    // testcanv(rectsave);
}

/////////////////imagePOST////////////////////

function imagedisplayXHR(){
    var xhr = new XMLHttpRequest();
    var obj;
    var imagename = imagelist.imgList[0].replace(/^.*[\\\/]/, '');
    xhr.open("POST", 'http://'+HostIP+':8082/filecontrol/getimage', true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            obj = JSON.parse(xhr.responseText);
            imageObj.src = obj;
        }
        else if(xhr.readyState === 500){
            alert("Image Server Not Response");
        }
    }
    var body = JSON.stringify({"mode": "SetupTrain","imgfilename": imagename});
    xhr.send(body);
}

/////////////////slideshowImage////////////////////

// import HostIP from './script_serverip';

var imagelist = [];
var imageIndex = 0;
var imagelistlength;


function imagelistXHR(a){
    var xhr = new XMLHttpRequest();
    var apiurl = 'http://'+HostIP+':8082/filecontrol/images/SetupTrain';
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
            imagedisplayXHR();
        }
        else if(xhr.readyState === 500){
            alert("Image List Not Response");
        }
    }
    xhr.send(imagelist);
}

function changeImage(n){
    currentImage(imageIndex += n);
}

var imagedir;
var imageshow = document.getElementById('imagedisplay');
var imagecount = document.getElementById('imagecount');

function currentImage(n){
    if(n < 0) {imageIndex = imagelistlength;n = imagelistlength;}
    if(n > imagelistlength) {imageIndex = 0;n = 0;}
    var imagename = imagelist.imgList[n].replace(/^.*[\\\/]/, '');
    imagedir = imagelist.imgList[n];
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://'+HostIP+':8082/filecontrol/getimage', true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            imageshow.src = JSON.parse(xhr.responseText);
        }
    }
    var body = JSON.stringify({"mode": "SetupTrain","imgfilename": imagename});
    xhr.send(body);
    imagecount.textContent = "("+(n+1)+"/"+(imagelistlength+1)+")";
}

/////////////////captureImage////////////////////

function captureimageTrain(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8081/camcontrol/saveImageTrain', false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
        }
        else if(xhr.readyState === 500){
            alert("Save Image Server Not Response");
        }
    }
    xhr.send(response);
    setTimeout(function(){imagelistXHR('lastimage')},50); 
}

/////////////////traininagAI////////////////////


var boxcropCon = [];

function getDate(){
    var current_datetime = new Date();
    var formatted_date = current_datetime.getFullYear() + "-" + (current_datetime.getMonth() + 1) + "-" + current_datetime.getDate() + " " + current_datetime.getHours() + ":" + current_datetime.getMinutes() + ":" + current_datetime.getSeconds(); 
    return formatted_date;
    //return Date();
}

var remarknote = document.getElementById('remark_note');

function trainingAnomaly(){
    if(level == "" || level == null || userID == "" || userID == null)
    {
        alert("Please check login.");
        return;
    }
    if(imagelist.imgList.length < 20){
        alert("Image Train less than 20 pictures");
        return;
    }
    var response;
    var xhr = new XMLHttpRequest();
    startwaiting();
    callConfig();
    console.log(boxcropCon);
    var st = getDate()
    xhr.open("POST", 'http://'+HostIP+':8083/ai/train', true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            stopwaiting();
            saveLogAI(st,getDate(),boxcropCon,remarknote.value);
        }
        else if(xhr.status === 500){
            alert("Train Server Not Response");
            waitingerror();
        }
    }
    var body = JSON.stringify({"imgList": imagelist.imgList,"bbox": boxcropCon});
    xhr.send(body);
}


function saveLogAI(startime,endTime,roi,remark){
    if(level == "" || level == null || userID == "" || userID == null)
    {
        alert("Please check login.");
        return;
    }
    var mark = null;
    if(remark !== ""){
        mark = remark;
    }
    var body = JSON.stringify({
        "userTraining":userID,
        "userLevel":level,
        "nImgTrain" : imagelistlength+1,
        "roiCropImg": roi,
        "startTrain": startime,
        "finishTrain": endTime,
        "remark": mark
    });
    console.log(body);
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://'+HostIP+':8085/ai_training_log', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
        }
    }

    xhr.send(body);
}
/////////////////Config////////////////////

var listConfig;

function callConfig(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8084/config', false);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            listConfig = response;
            rectsend = listConfig.bboxCrop;
            boxcropCon = listConfig.bboxCrop;
            // console.log(rectsend);
        }
        else if(xhr.readyState === 500){
            alert("Config Server Not Response");
        }
    }
    xhr.send(response);
}

function sendROI(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://'+HostIP+':8084/config/roi', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
        }
        else if(xhr.readyState === 500){
            alert("Send ROI Error");
            response = false;
        }
    }
    // var body = JSON.stringify({"machineId": listConfig.machineId,"rejectThreshold": listConfig.rejectThreshold,
    //                             "stopWhenRejectCount": listConfig.stopWhenRejectCount,"changeModeWhenProcessTrigCount": listConfig.changeModeWhenProcessTrigCount,
    //                             "useAI": listConfig.useAI,"inferenceRate": listConfig.inferenceRate,"bboxCrop": [rectsend]});
    var body = JSON.stringify([rectsend[1],rectsend[0],rectsend[3],rectsend[2]]);
    console.log(body);
    xhr.send(body);
    return response;
}

/////////////////devareImage////////////////////

function deletecurrentImage(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", 'http://'+HostIP+':8082/filecontrol/images/', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            console.log(response);
        }
    }
    var body = JSON.stringify({"mode": "SetupTrain","imgList": [imagedir]});
    xhr.send(body);
    setTimeout(function(){imagelistXHR('lastimage')},50); 
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
    var body = JSON.stringify({"mode": "SetupTrain","imgList": imagelist.imgList});
    xhr.send(body);
}

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

/////////////////sequenceFunction////////////////////

init();
imagelistXHR();
callConfig();
startroi();
