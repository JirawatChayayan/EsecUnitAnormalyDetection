/////////////////logIn////////////////////

var jwt = localStorage.getItem("jwt");

if(jwt == null){
    window.location.href = '../index.html'
}

var menusignup = document.getElementById('signup');
var menuconfig = document.getElementById('menuconfig');

menusignup.style.display = "none";
menuconfig.style.display = "none";

var level = localStorage.getItem("level");
if(level == 'Engineer'){
    menusignup.style.display = "block";
    menuconfig.style.display = "block";
}

var expires = localStorage.getItem("expires");
var expriesInterval = setInterval(logout, expires);

/////////////////logOut////////////////////

function logout(){
    localStorage.clear()
    window.location.href = "../index.html"
}