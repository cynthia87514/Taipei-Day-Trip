let userName = "";
let URL = window.location.href;
URL = URL.split("=");
const orderNumber = URL[1];
// 確認登入狀態
async function fetchUserData(){
    try{
        const token = localStorage.getItem("token");
        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        const data = await response.json();
        return data;
    }catch(error){
        console.log(error);
    }
}

// 依照使用者登入狀態調整右上角顯示：登入/註冊 或 登出系統
async function updatePage(userStatus){
    const signin = document.querySelector(".navigationButtonRight");
    const signout = document.querySelector(".navigationButtonRightSignout");
    try{
        if (userStatus === null){
            return;
        }
        else if(userStatus.data){
            signin.style.display = "none";
            signout.style.display = "block";
        }else{
            signin.style.display = "block";
            signout.style.display = "none";
        }
    }catch(error){
        console.log(error);
    }
}

const showResult = document.querySelector(".showResult");
const orderNumberBox = document.querySelector(".orderNumberBox");
const orderInfoBox = document.querySelector(".orderInfoBox");
const crossOrder = orderInfoBox.querySelector(".crossOrder");

let userStatus;
// 載入頁面時確認使用者狀態
document.addEventListener("DOMContentLoaded", async function(){
    try{
        userStatus = await fetchUserData();
        if (userStatus.data === null){
            window.location.href = "/";
            return;
        }else {
            userName = userStatus["data"]["name"];
            updatePage(userStatus);
            showResult.textContent = userName + "，恭喜行程預定成功";
            orderNumberBox.textContent = orderNumber;
        }
    }catch(error){
        console.log(error);
    }
});

orderNumberBox.addEventListener("click", async function(){
    const orderData = await fetchOrderData(orderNumber);
    renderOrderInfo(orderData);
    orderInfoBox.style.display = "flex";
    overlay.style.display = "block";
});

crossOrder.addEventListener("click", function(){
    orderInfoBox.style.display = "none";
    overlay.style.display = "none";
});

overlay.addEventListener("click", function(event){
    if (event.target === overlay){
      orderInfoBox.style.display = "none";
      overlay.style.display = "none";
    }
})

async function fetchOrderData(orderNumber){
    try{
        const response = await fetch(`/api/order/${orderNumber}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
        const data = await response.json();
        return data;
    }catch(error){
        console.log(error);
    }
}

const picture = document.querySelector(".picture");
const infoDateText = document.querySelector(".infoDateText");
const infoTimeText = document.querySelector(".infoTimeText");
const infoPriceText = document.querySelector(".infoPriceText");
const infoTitleText = document.querySelector(".infoTitleText");
const infoAddressText = document.querySelector(".infoAddressText");
const nameText = document.querySelector(".nameText");
const emailText = document.querySelector(".emailText");
const phoneText = document.querySelector(".phoneText");

function renderOrderInfo(orderData){
    let bookingTimeRange = "";
    if (orderData["data"]["trip"]["time"] === "morning"){
        bookingTimeRange = "早上 9 點到下午 4 點";
    }
    if (orderData["data"]["trip"]["time"] === "afternoon"){
        bookingTimeRange = "下午 2 點到晚上 9 點";
    }
    picture.style.backgroundImage = "url(" + orderData["data"]["trip"]["attraction"]["image"] + ")";
    infoTitleText.textContent = orderData["data"]["trip"]["attraction"]["name"];
    infoDateText.textContent = orderData["data"]["trip"]["date"];
    infoTimeText.textContent = bookingTimeRange;
    infoPriceText.textContent = orderData["data"]["price"];
    infoAddressText.textContent = orderData["data"]["trip"]["attraction"]["address"];
    nameText.textContent = orderData["data"]["contact"]["name"];
    emailText.textContent = orderData["data"]["contact"]["email"];
    phoneText.textContent = orderData["data"]["contact"]["phone"];
}