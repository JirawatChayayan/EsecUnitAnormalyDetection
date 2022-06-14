var HostIP = '192.168.137.159';




var jwt = localStorage.getItem("jwt");

if(jwt == null){
    window.location.href = '../index.html'
}

var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);

//////////////////////callConfig//////////////////////

var machineid = document.getElementById('machineID');
var rejectthreshold = document.getElementById('rejectThreshold');
var stoprejectCount = document.getElementById('stopWhenRejectCount');
var changemodeprocesstrigcount = document.getElementById('changeModeWhenProcessTrigCount');
var maxprocesstimeperunit = document.getElementById('maxProcessTimePerUnit');
var useaitrue = document.getElementById('useAI-true');
var useaifalse = document.getElementById('useAI-false');
var inferencerate = document.getElementById('inferenceRate');
var equipopn = document.getElementById('equipOpn');
var cimequipid = document.getElementById('cimEquipId');
var secsgem = document.getElementById('secs/gem');
var io = document.getElementById('io');
var both = document.getElementById('both');
var boxcrop;

function callConfig(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8084/config', false);
    xhr.onreadystatechange = function() {
        console.log(xhr.status);
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            boxcrop = response.bboxCrop;
        }
        else if(xhr.status === 500){
            alert("Config Server Not Response");
        }
    }
    xhr.send(response);
    listconfig(response);
}

function listconfig(a){
    machineid.value = a.machineId;
    rejectthreshold.value = a.rejectThreshold;
    stoprejectCount.value = a.stopWhenRejectCount;
    changemodeprocesstrigcount.value = a.changeModeWhenProcessTrigCount;
    maxprocesstimeperunit.value = a.maxProcessTimePerUnit;
    if(a.useAI == true){
        useaitrue.checked = true;
    }
    else{
        useaifalse.checked = true;
    }
    inferencerate.value = a.inferenceRate;
    equipopn.value = a.equipOpn;
    cimequipid.value = a.cimEquipID;
    if(a.stopMachine == 'SECS/GEM'){
        secsgem.checked = true;
    }
    else if(a.stopMachine == 'IO'){
        io.checked = true;
    }
    else if(a.stopMachine == 'BOTH'){
        both.checked = true;
    }
}

function sendConfig(){
    var response;
    var useai;
    var stopmachine;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://'+HostIP+':8084/config', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
            checksendres(response);
            sendcolorInput();
        }
        else if(xhr.status === 500){
            alert("Config Server Not Response");
            sendcolorInputError()
        }
    }
    if(useaitrue.checked){
        useai = useaitrue.value;
    }
    else if(useaifalse.checked){
        useai = useaifalse.value;
    }
    if(secsgem.checked){
        stopmachine = secsgem.value;
    }
    else if(io.checked){
        stopmachine = io.value;
    }
    else if(both.checked){
        stopmachine = both.value;
    }
    console.log(stopmachine);
    var body = JSON.stringify({"machineId": machineid.value.trim(),"rejectThreshold": rejectthreshold.value.trim(),
                                "stopWhenRejectCount": stoprejectCount.value.trim(),"changeModeWhenProcessTrigCount": changemodeprocesstrigcount.value.trim(),
                                "maxProcessTimePerUnit" : maxprocesstimeperunit.value.trim(),
                                "useAI": useai,"inferenceRate": inferencerate.value.trim(),"equipOpn": equipopn.value.trim(),"cimEquipID": cimequipid.value.trim(),"stopMachine":stopmachine});
    xhr.send(body);
}

//////////////////////inputConfig//////////////////////

function checksendres(a){
    if(a == true){
        alert("Save Complete");
    }
    else{
        alert("Save Fail");
    }
}

function sendcolorInput(){
    machineid.style.backgroundColor = '#85F57C';
    rejectthreshold.style.backgroundColor = '#85F57C';
    stoprejectCount.style.backgroundColor = '#85F57C';
    changemodeprocesstrigcount.style.backgroundColor = '#85F57C';
    maxprocesstimeperunit.style.backgroundColor = '#85F57C';
    inferencerate.style.backgroundColor = '#85F57C';
    equipopn.style.backgroundColor = '#85F57C';
    cimequipid.style.backgroundColor = '#85F57C';
}

function sendcolorInputError(){
    machineid.style.backgroundColor = '#FF0005';
    rejectthreshold.style.backgroundColor = '#FF0005';
    stoprejectCount.style.backgroundColor = '#FF0005';
    changemodeprocesstrigcount.style.backgroundColor = '#FF0005';
    maxprocesstimeperunit.style.backgroundColor = '#FF0005';
    inferencerate.style.backgroundColor = '#FF0005';
    equipopn.style.backgroundColor = '#FF0005';
    cimequipid.style.backgroundColor = '#FF0005';
}

function changcolorInput(){
    machineid.style.backgroundColor = '#fff';
    equipopn.style.backgroundColor = '#fff';
    cimequipid.style.backgroundColor = '#fff';
    rejectthreshold.style.backgroundColor = '#fff';
    stoprejectCount.style.backgroundColor = '#fff';
    changemodeprocesstrigcount.style.backgroundColor = '#fff';
    maxprocesstimeperunit.style.backgroundColor = '#fff';
    inferencerate.style.backgroundColor = '#fff';
}

function numonly(){
    this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\..*/g, '$1');
}

machineid.addEventListener('propertychange', changcolorInput);
rejectthreshold.addEventListener('propertychange', changcolorInput);
stoprejectCount.addEventListener('propertychange', changcolorInput);
changemodeprocesstrigcount.addEventListener('propertychange', changcolorInput);
maxprocesstimeperunit.addEventListener('propertychange', changcolorInput);
inferencerate.addEventListener('propertychange', changcolorInput);
equipopn.addEventListener('propertychange', changcolorInput);
cimequipid.addEventListener('propertychange', changcolorInput);


machineid.addEventListener('input', changcolorInput);
rejectthreshold.addEventListener('input', numonly);
rejectthreshold.addEventListener('input', changcolorInput);
stoprejectCount.addEventListener('input', numonly);
stoprejectCount.addEventListener('input', changcolorInput);
changemodeprocesstrigcount.addEventListener('input', numonly);
changemodeprocesstrigcount.addEventListener('input', changcolorInput);
maxprocesstimeperunit.addEventListener('input', numonly);
maxprocesstimeperunit.addEventListener('input', changcolorInput);
inferencerate.addEventListener('input', numonly);
inferencerate.addEventListener('input', changcolorInput);
equipopn.addEventListener('input', changcolorInput);
cimequipid.addEventListener('input', changcolorInput);

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

//////////////////////sequenceFunction//////////////////////

callConfig();
