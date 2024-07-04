// 畫面加載
let URL = window.location.href;
URL = URL.split("/");
const attractionId = URL[URL.length - 1];
if (1 <= attractionId && attractionId <= 58){
    fetch(`/api/attraction/${attractionId}`).then(function(response){
        return response.json();
    }).then(function(data){
        const attraction = data.data;
        const attractionImage = attraction.images;

        // 渲染景點圖片
        const pictures = document.querySelector(".pictures");
        const amount =  attractionImage.length;
        const picture = document.createElement("div");
        picture.setAttribute("class", "picture");
        picture.style.backgroundImage = "url(" + attractionImage[0] + ")";
        pictures.appendChild(picture);

        // 定義目前所在的圖片位置，預設為 0
        let current = 0;
        let targetId = "circle0";

        // 渲染景點圖片上的圓點
        const circleBar = document.querySelector(".circleBar");
        for (let i = 0 ; i < amount ; i++){
            const circleBox = document.createElement("div");
            circleBox.setAttribute("class", "circleBox");
            const circle = document.createElement("div");
            circle.setAttribute("class", "circle");
            circle.setAttribute("id", "circle" + i);
            circleBar.appendChild(circleBox);
            circleBox.appendChild(circle);

            // 點擊 圖片上的圓點 切換圖片
            circle.addEventListener("click", function(){
                current = i;
                targetId = "circle" + i;
                changeCircle();
                picture.style.backgroundImage = "url(" + attractionImage[i] + ")";
            })
        }

        // 點擊 圖片上的左右箭頭 切換圖片
        const leftArrow = document.querySelector(".leftArrow");
        const rightArrow = document.querySelector(".rightArrow");
        const circles = document.querySelectorAll(".circle");
        changeCircle();

        leftArrow.addEventListener("click", function(){
            picture.classList.add("fade-out");
            if (current === 0){
                picture.style.backgroundImage = "url(" + attractionImage[amount-1] + ")";
                current = amount - 1;
                targetId = "circle" + current;
                changeCircle();
            }
            else if (current > 0){
                picture.style.backgroundImage = "url(" + attractionImage[current-1] + ")";
                current--;
                targetId = "circle" + current;
                changeCircle();
            }
            picture.classList.remove("fade-out");
        })
        rightArrow.addEventListener("click", function(){
            picture.classList.add("fade-out");
            if (current === amount-1){
                picture.style.backgroundImage = "url(" + attractionImage[0] + ")";
                current = 0;
                targetId = "circle" + current;
                changeCircle();
            }
            else if (current < amount-1){
                picture.style.backgroundImage = "url(" + attractionImage[current+1] + ")";
                current++;
                targetId = "circle" + current;
                changeCircle();
            }
            picture.classList.remove("fade-out");
        })

        // 圓點變化顯示目前所在的圖片位置
        function changeCircle(){
            circles.forEach(function(circle){
                if (circle.id === targetId){
                    circle.classList.add("change");
                }
                else{
                    circle.classList.remove("change");
                }
            })
        }

        // 若僅有一張圖片，不顯示箭頭
        const arrows = document.querySelector(".arrows");
        if (amount === 1){
            arrows.remove();
            leftArrow.remove();
            rightArrow.remove();
        }

        // 若圖片多於 15 張，RWD 時會調整圓點排列
        if (amount > 15){
            circleBar.classList.add("scroll");
        }

        // 渲染景點名稱
        const name = document.querySelector(".name");
        name.textContent = attraction.name;
        // 渲染景點類別及捷運站名
        const catMRT = document.querySelector(".catMRT");
        if (attraction.mrt === null){
            catMRT.textContent = attraction.category;
        }
        else{
            catMRT.textContent = attraction.category + " at " + attraction.mrt;
        }
        // 渲染景點介紹
        const description = document.querySelector(".description");
        description.textContent = attraction.description;
        // 渲染景點地址
        const address = document.querySelector(".addressContent");
        address.textContent = attraction.address;
        // 渲染交通方式
        const transport = document.querySelector(".transportContent");
        transport.textContent = attraction.transport;
    })
}
else{
    window.location.href = "/";
}

// 點擊 不同時段(上 / 下半天) 切換導覽費用
const upRadio = document.querySelector("#upRadio");
const downRadio = document.querySelector("#downRadio");
const priceDollars = document.querySelector(".priceDollars");
upRadio.addEventListener("change", function(){
    priceDollars.textContent = "新台幣 2000 元";
    priceDollars.setAttribute("class", "priceDollars");
})
downRadio.addEventListener("change", function(){
    priceDollars.textContent = "新台幣 2500 元";
    priceDollars.setAttribute("class", "priceDollars");
})



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

// 載入頁面時確認使用者狀態
document.addEventListener("DOMContentLoaded", async function(){
    const userStatus = await fetchUserData();
    updatePage(userStatus);
})

// 建立新的預定行程
// 按下 開始預約行程
const bookingForm = document.querySelector(".booking");
bookingForm.addEventListener("submit", async function(event){
    event.preventDefault();
    bookingTrip();
})

function bookingTrip(){
    const {date, time, price} = getBookingData();
    const jsonObject = {
        attractionId: parseInt(attractionId),
        date: date,
        time: time,
        price: parseInt(price)
    };
    if (date === ""){
        alert("請選擇欲訂購的日期");
        return;
    }else{
        createBooking(jsonObject);
    }
}

function createBooking(jsonObject){
    const token = localStorage.getItem("token")
    if (!token){
        showSignIn();
        return;
    }
    fetch("/api/booking", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(jsonObject)
    }).then(function(response){
        if (response.status === 403){
            showSignIn();
            return Promise.reject();
        }
        return response.json();
    }).then(function(data){
        if (data.ok === true){
            window.location.href = "/booking";
        }
        if (data.error === true){
            alert("預約失敗，請再次嘗試");
        }
    }).catch(function(error){
        console.log(error);
    });
}

// 獲得預定表單內的資料
function getBookingData(){
    const date = document.querySelector(".dateInput").value;
    const radioButtons = document.querySelectorAll("input[name = 'time']");
    let selected = "";
    let time = "";
    radioButtons.forEach(function(button){
        if (button.checked){
            selected = button.value;
        }
    })
    if (selected === "上半天"){
        time = "morning";
    }
    if (selected === "下半天"){
        time = "afternoon";
    }
    let priceText = document.querySelector(".priceDollars").textContent;
    priceText = priceText.split(" ");
    price = priceText[1];
    return {date, time, price};
}

function showSignIn(){
    dialogSignin.style.display = "block";
    dialogSignup.style.display = "none";
    overlay.style.display = "block";
}