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
let attractionId;
let attractionName = "";
let attractionAddress = "";
let attractionImage = "";
let bookingDate = "";
let bookingTime = "";
let bookingPrice;

document.addEventListener("DOMContentLoaded", async function(){
    try{
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
    }catch(error){
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
    bookingDate = bookingData["data"]["date"];
    bookingTime = bookingData["data"]["time"];
    let bookingTimeRange = "";
    bookingPrice = bookingData["data"]["price"];
    if (bookingTime === "morning"){
        bookingTimeRange = "早上 9 點到下午 4 點";
    }
    if (bookingTime === "afternoon"){
        bookingTimeRange = "下午 2 點到晚上 9 點";
    }
    
    const picture = document.querySelector(".picture");
    const infoTitleText = document.querySelector(".infoTitleText");
    const infoAddressText = document.querySelector(".infoAddressText");
    const attractionData = bookingData["data"]["attraction"]
    attractionId = attractionData["id"];
    attractionName = attractionData["name"];
    attractionAddress = attractionData["address"];
    attractionImage = attractionData["image"];

    const nameInput = document.querySelector(".nameInput");
    const emailInput = document.querySelector(".emailInput");

    booked.classList.add("active");
    footerBoxbooked.classList.add("active");
    footerDivbooked.classList.add("active");

    infoDateText.textContent = bookingDate;
    infoTimeText.textContent = bookingTimeRange;
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


// Front-End Process for Credit Card Payment
TPDirect.setupSDK(151796, "app_oknLWLCFpfqWUuQI72Rvm6b4wtMtSc9WCwOSxMDpl9pYGylbZgXxDG4JmqWQ", "sandbox");

TPDirect.card.setup({
    fields: {
        number: {
            element: document.getElementById("cardNumber"),
            placeholder: "**** **** **** ****"
        },
        expirationDate: {
            element: document.getElementById("cardExpirationDate"),
            placeholder: "MM / YY"
        },
        ccv: {
            element: document.getElementById("cardCCV"),
            placeholder: "CCV"
        }
    },
    styles: {
        "input": {
            "width": "180px",
            "height": "18px",
            "font-family": "Noto Sans TC, sans-serif",
            "font-size": "16px",
            "font-weight": 500,
            "line-height": "13.3px",
            "color": "#000000"
        },
        ".valid": {
            "color": "green"
        },
        ".invalid": {
            "color": "red"
        }
    },
    // 卡號輸入正確後，顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
    }
})

TPDirect.card.onUpdate(function(update) {
    const submitButton = document.getElementById("submitButton");

    if (update.canGetPrime){
        submitButton.removeAttribute("disabled");
    }else{
        submitButton.setAttribute("disabled", true);
    }

    handleFieldStatus("cardNumber", update.status.number);
    handleFieldStatus("cardExpirationDate", update.status.expiry);
    handleFieldStatus("cardCCV", update.status.ccv);
});

function handleFieldStatus(fieldId, status){
    if (status === 2){
        showError(fieldId);
    }else if (status === 0){
        showSuccess(fieldId);
    }else{
        clearStatus(fieldId);
    }
}

function showError(fieldId){
    const field = document.getElementById(fieldId);
    clearStatus(fieldId);
    const errorDiv = document.createElement("div");
    errorDiv.className = "errorMessage";
    errorDiv.textContent = "✖";
    field.parentNode.appendChild(errorDiv);
}

function showSuccess(fieldId){
    const field = document.getElementById(fieldId);
    clearStatus(fieldId);
    const successDiv = document.createElement("div");
    successDiv.className = "successMessage";
    successDiv.textContent = "✔";
    field.parentNode.appendChild(successDiv);
}

function clearStatus(fieldId){
    const field = document.getElementById(fieldId);
    const errorDiv = field.parentNode.querySelector(".errorMessage");
    if (errorDiv){
        errorDiv.remove();
    }
    const successDiv = field.parentNode.querySelector(".successMessage");
    if (successDiv){
        successDiv.remove();
    }
}

function getPrime(){
    return new Promise((resolve, reject) => {
        TPDirect.card.getPrime(function(result){
            if (result.status !== 0) {
                alert("付款錯誤，請再次嘗試 " + result.msg);
                reject(result.msg);
            }else{
                resolve(result.card.prime);
            }
        });
    });
}

// 監聽 確認訂購並付款 按鈕，被點擊時提交表單
document.getElementById("submitButton").addEventListener("click", async function(event){
    event.preventDefault();

    // 取得 TapPay Fields 的 status
    const tappayStatus = TPDirect.card.getTappayFieldsStatus();

    // 確認是否可以 getPrime
    if (!tappayStatus.canGetPrime){
        alert("請確認信用卡付款資訊");
        return;
    }

    // Get prime
    try{
        const prime = await getPrime();
        if (prime){
            const orderInput = GetOrderInput();
            const result = await createOrder(prime, orderInput);
            if (result["data"]["payment"]["status"] === 0){
                const orderNumber = result["data"]["number"];
                window.location.href = `/thankyou?number=${orderNumber}`;
            }else{
                alert("付款失敗，請聯絡信用卡公司或稍後再嘗試");
                window.location.href = "/";
            }
            fetchDeleteBooking();
        }
    }catch(error){
        console.error(error);
    }
})

function GetOrderInput(){
    const trip = {
        "attraction": {
            "id": attractionId,
            "name": attractionName,
            "address": attractionAddress,
            "image": attractionImage
        },
        "date": bookingDate,
        "time": bookingTime,
    }
    const contact = {
        "name": document.querySelector(".nameInput").value,
        "email": document.querySelector(".emailInput").value,
        "phone": document.querySelector(".phoneInput").value
    }
    const orderInput = {
        "price": bookingPrice,
        "trip": trip,
        "contact": contact}
    
    return orderInput
}

async function createOrder(prime, orderInput){
    try{
        const token = localStorage.getItem("token")
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                prime: prime,
                order: orderInput
            })
        });
        const data = await response.json();
        return data;
    }catch(error){
        console.log(error);
    }
}