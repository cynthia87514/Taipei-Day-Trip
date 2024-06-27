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

// 取得尚未確認下單的預定行程(此 fetch 僅 booking 頁面需要) ////////////////////////////////
async function fetchBookingData(){
    try{
        const response = await fetch("/api/booking", {
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

// 載入頁面時確認使用者狀態
document.addEventListener("DOMContentLoaded", async function(){
    try {
        const userStatus = await fetchUserData();
        if (userStatus.data === null){
            window.location.href = "/";
            return;
        }else {
            const name = userStatus["data"]["name"];
            const email = userStatus["data"]["email"];
            updatePage(userStatus);
            const bookingData = await fetchBookingData();
            if (bookingData.data === null){
                renderUnbookingPage(name);
            }else{
                renderBookingPage(bookingData, name, email);
            }
        }
    } catch(error) {
        console.log(error);
    }
})

// 有預定行程的 booking 頁面
function renderBookingPage(bookingData, name, email){
    const booked = document.querySelector(".booked");
    const footerBoxbooked = document.querySelector(".footerBoxbooked");
    const footerDivbooked = document.querySelector(".footerDivbooked");
    const headlineText = document.querySelector(".headlineText");

    const infoDateText = document.querySelector(".infoDateText");
    const infoTimeText = document.querySelector(".infoTimeText");
    const infoPriceText = document.querySelector(".infoPriceText");
    const totalPriceText = document.querySelector(".totalPriceText");
    const bookingDate = bookingData["data"]["date"];
    let bookingTime = bookingData["data"]["time"];
    const bookingPrice = bookingData["data"]["price"];
    if (bookingTime === "morning"){
        bookingTime = "早上 9 點到下午 4 點";
    }
    if (bookingTime === "afternoon"){
        bookingTime = "下午 2 點到晚上 9 點";
    }
    
    const picture = document.querySelector(".picture");
    const infoTitleText = document.querySelector(".infoTitleText");
    const infoAddressText = document.querySelector(".infoAddressText");
    const attractionData = bookingData["data"]["attraction"]
    const attractionName = attractionData["name"];
    const attractionAddress = attractionData["address"];
    const attractionImage = attractionData["image"];

    const nameInput = document.querySelector(".nameInput");
    const emailInput = document.querySelector(".emailInput");

    booked.classList.add("active");
    footerBoxbooked.classList.add("active");
    footerDivbooked.classList.add("active");

    infoDateText.textContent = bookingDate;
    infoTimeText.textContent = bookingTime;
    infoPriceText.textContent = "新台幣 " + bookingPrice + " 元";
    totalPriceText.textContent = "總價：新台幣 " + bookingPrice + " 元";

    headlineText.textContent = "您好，" + name + "，待預訂的行程如下：";
    picture.style.backgroundImage = "url(" + attractionImage + ")";
    infoTitleText.textContent = "台北一日遊：" + attractionName;
    infoAddressText.textContent = attractionAddress;

    nameInput.value = name;
    emailInput.value = email;
}

// 沒有預定行程的 booking 頁面
function renderUnbookingPage(name){
    const body = document.querySelector("body");
    const unbooked = document.querySelector(".unbooked");
    const footerBoxunbooked = document.querySelector(".footerBoxunbooked");
    const footerDivunbooked = document.querySelector(".footerDivunbooked");
    const headlineUnbookedText = document.querySelector(".headlineUnbookedText");
    body.style.overflowY = "hidden";
    unbooked.classList.add("active");
    footerBoxunbooked.classList.add("active");
    footerDivunbooked.classList.add("active");
    headlineUnbookedText.textContent = "您好，" + name + "，待預訂的行程如下：";
}

// 刪除預定的行程
document.querySelector(".deleteButton").addEventListener("click", function(){
    fetchDeleteBooking();
    location.reload();
})

async function fetchDeleteBooking(){
    try{
        const response = await fetch("/api/booking", {
            method: "DELETE",
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