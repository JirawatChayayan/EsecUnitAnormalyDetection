var HostIP = '192.168.137.159';





var jwt = localStorage.getItem("jwt");
if(jwt == null){
    window.location.href = '../index.html'
}

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

//////////////////////callrejectResult//////////////////////

var tableresult = document.getElementById('tb_result').getElementsByTagName('tbody')[0];
var data_length;
var thead = document.getElementById('tb_result').getElementsByTagName('thead')[0];
var tfoot = document.getElementById('tb_result').getElementsByTagName('tfoot')[0];

function listrejectresult(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8085/reject_result', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            data_length = response.length;
            insertrow(response);
        }
    }
    xhr.send(response);
}

function insertrow(data){

    for(i = 1; i < data_length; i++){
        var row = tableresult.insertRow(-1);
        for(j = 0; j < 5; j++){
            var cell = row.insertCell(j);
            if(j == 0){
                var text = document.createTextNode(data[i-1].imgFileName);
                cell.appendChild(text);
            }
            else if(j == 1){
                var text = document.createTextNode(data[i-1].scoreMin);
                cell.appendChild(text);
            }
            else if(j == 2){
                var text = document.createTextNode(data[i-1].scoreMax);
                cell.appendChild(text);
            }
            else if(j == 3){
                var text = document.createTextNode(data[i-1].rejectThreshold);
                cell.appendChild(text);
            }
            else if(j == 4){
                var date = data[i-1].createDate;
                var text = document.createTextNode(date.replace("T", " "));
                cell.appendChild(text);
            }
        }
    }
    addhandleRow();
}

function addhandleRow(){
    var rows = tableresult.getElementsByTagName("tr");
    for (i = 0; i < rows.length; i++) {
        var currentRow = tableresult.rows[i];
        var createClickHandler = function(row) {
            return function() {
                Array.from(this.parentElement.children).forEach(function(el){
                    el.classList.remove('selected-row');
                });
                this.classList.add('selected-row');
                //row.style.backgroundColor = '#6495ED';
                var cell = row.getElementsByTagName("td")[0];
                var cell_2 = row.getElementsByTagName("td")[1];
                var cell_3 = row.getElementsByTagName("td")[2];
                var cell_4 = row.getElementsByTagName("td")[3];
                var cell_5 = row.getElementsByTagName("td")[4];
                callimage(cell.innerHTML);
                tfoot.rows[0].cells[0].innerHTML = cell.innerHTML;
                tfoot.rows[0].cells[1].innerHTML = cell_2.innerHTML;
                tfoot.rows[0].cells[2].innerHTML = cell_3.innerHTML;
                tfoot.rows[0].cells[3].innerHTML = cell_4.innerHTML;
                tfoot.rows[0].cells[4].innerHTML = cell_5.innerHTML;
            };

        };
        currentRow.onclick = createClickHandler(currentRow);
        tableresult.rows[i].cells[0].style.width = '100px';
        tableresult.rows[i].cells[1].style.width = '30px';
        tableresult.rows[i].cells[2].style.width = '30px';
        tableresult.rows[i].cells[3].style.width = '30px';
        tableresult.rows[i].cells[4].style.width = '100px';
    }
}

function cellrejectresultsize(){
    thead.rows[0].cells[0].style.width = '99.5px';
    thead.rows[0].cells[1].style.width = '30px';
    thead.rows[0].cells[2].style.width = '30px';
    thead.rows[0].cells[3].style.width = '30px';
    thead.rows[0].cells[4].style.width = '105px';
    //////////////////////////////////////////////
    tfoot.rows[0].cells[0].style.width = '99.5px';
    tfoot.rows[0].cells[1].style.width = '30px';
    tfoot.rows[0].cells[2].style.width = '30px';
    tfoot.rows[0].cells[3].style.width = '30px';
    tfoot.rows[0].cells[4].style.width = '105px';
}

var imageresult = document.getElementById('imageresult');
var imageheat = document.getElementById('imageheat');

function callimage(imagename){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8085/reject_resultimage/'+imagename, false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            console.log(response);
            imageresult.src = response.imgRaw;
            imageheat.src = response.imgHeatMap;
        }
    }
    xhr.send(response);
}

//////////////////////callstopLog//////////////////////

var tablestoplog = document.getElementById('tb_log').getElementsByTagName('tbody')[0];
var data_stoplog_length;
var theadstoplog = document.getElementById('tb_log').getElementsByTagName('thead')[0];

function liststopreleaselog(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8085/stop_release_log', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            data_stoplog_length = response.length;
            insertrowstoplog(response);
        }
    }
    xhr.send(response);
}

function insertrowstoplog(data){

    for(i = 1; i < data_stoplog_length; i++){
        var row = tablestoplog.insertRow(-1);
        for(j = 0; j < 2; j++){
            var cell = row.insertCell(j);
            if(j == 0){
                var text = document.createTextNode(data[i-1].remark);
                cell.appendChild(text);
            }
            else if(j == 1){
                var date = data[i-1].timestamp;
                var text = document.createTextNode(date.replace("T", " "));
                cell.appendChild(text);
            }
        }
    }
    addhandlestoplogRow();
}

function addhandlestoplogRow(){
    var rows = tablestoplog.getElementsByTagName("tr");
    for (i = 0; i < rows.length; i++) {
        theadstoplog.rows[0].cells[1].style.width = '404.5px'
    };
}

//////////////////////callAItrainingLog//////////////////////

var tableailog = document.getElementById('tb_ai_log').getElementsByTagName('tbody')[0];
var data_ailog_length;
var theadailog = document.getElementById('tb_ai_log').getElementsByTagName('thead')[0];

function listailog(){
    var response;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'http://'+HostIP+':8085/ai_training_log', false);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UFT-8");
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200){
            response = JSON.parse(xhr.responseText);
            data_ailog_length = response.length;
            insertrowailog(response);
        }
    }
    xhr.send(response);
}

function insertrowailog(data){

    for(i = 1; i < data_ailog_length; i++){
        var row = tableailog.insertRow(-1);
        for(j = 0; j < 7; j++){
            var cell = row.insertCell(j);
            if(j == 0){
                var text = document.createTextNode(data[i-1].userTraining);
                cell.appendChild(text);
            }
            else if(j == 1){
                var text = document.createTextNode(data[i-1].userLevel);
                cell.appendChild(text);
            }
            else if(j == 2){
                var text = document.createTextNode(data[i-1].nImgTrain);
                cell.appendChild(text);
            }
            else if(j == 3){
                var text = document.createTextNode(data[i-1].roiCropImg);
                cell.appendChild(text);
            }
            else if(j == 4){
                var date = data[i-1].startTrain;
                var text = document.createTextNode(date.replace("T", " "));
                cell.appendChild(text);
            }
            else if(j == 5){
                var date = data[i-1].finishTrain;
                var text = document.createTextNode(date.replace("T", " "));
                cell.appendChild(text);
            }
            else if(j == 6){
                var text = document.createTextNode(data[i-1].remark);
                cell.appendChild(text);
            }
        }
    }
    addhandleailogRow();
}

function addhandleailogRow(){
    var rows = tableailog.getElementsByTagName("tr");
    for (i = 0; i < rows.length; i++) {
        for (i = 0; i < rows.length; i++) {
            tableailog.rows[i].cells[0].style.width = '35px';
            tableailog.rows[i].cells[1].style.width = '30px';
            tableailog.rows[i].cells[2].style.width = '30px';
            tableailog.rows[i].cells[3].style.width = '50px';
            tableailog.rows[i].cells[4].style.width = '50px';
            tableailog.rows[i].cells[5].style.width = '50px';
            tableailog.rows[i].cells[6].style.width = '100px';
        }
        theadailog.rows[0].cells[0].style.width = '35px';
        theadailog.rows[0].cells[1].style.width = '30px';
        theadailog.rows[0].cells[2].style.width = '30px';
        theadailog.rows[0].cells[3].style.width = '50px';
        theadailog.rows[0].cells[4].style.width = '50px';
        theadailog.rows[0].cells[5].style.width = '50px';
        theadailog.rows[0].cells[6].style.width = '105.5px';
    };
}

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}

//////////////////////sequencefunction//////////////////////

listrejectresult();
liststopreleaselog();
listailog();
cellrejectresultsize();