// 左上角 台北一日遊 按鈕：點擊回到首頁 ////////////////////////////////////////////////////
const navigationText = document.querySelector(".navigationText");
navigationText.addEventListener("click", function(){
    window.location.href = "/";
})

// 右上角 預定行程 按鈕：登入狀態點擊導到 booking 頁面，未登入狀態點擊顯示登入/註冊框 /////////
document.querySelector(".navigationButtonLeftText").addEventListener("click", function(){
    bookingButton();
})

// 右上角 登入/註冊 按鈕：點擊顯示登入/註冊框 //////////////////////////////////////////////
const dialogSignin = document.querySelector(".dialogSignin");
const dialogSignup = document.querySelector(".dialogSignup");
const overlay = document.querySelector(".overlay");
const signupResultOk = document.querySelector(".signupResultOk");
const signupResultFailed = document.querySelector(".signupResultFailed");

// 預設開啟登入框
document.querySelector(".navigationButtonRightText").addEventListener("click", function(){
    showSignIn();
})

// 點擊註冊開啟註冊框
document.querySelector(".toSignupBtn").addEventListener("click", function(){
    showSignUp();
})

// 點擊登入開啟登入框
document.querySelector(".toSigninBtn").addEventListener("click", function(){
    showSignIn();
    signupResultOk.classList.remove("active");
    signupResultFailed.classList.remove("active");
    signupForm.reset();
})

// 點擊叉叉關閉登入/註冊框
document.querySelectorAll(".cross").forEach(function(item){
    item.addEventListener("click", function(){
        dialogSignin.style.display = "none";
        dialogSignup.style.display = "none";
        signupResultOk.classList.remove("active");
        signupResultFailed.classList.remove("active");
        overlay.style.display = "none";
        signupForm.reset();
    })
})

// 點擊框框外的畫面也可關閉框框
overlay.addEventListener("click", function(event){
    if (event.target === overlay){
        dialogSignin.style.display = "none";
        dialogSignup.style.display = "none";
        signupResultOk.classList.remove("active");
        signupResultFailed.classList.remove("active");
        overlay.style.display = "none";
        signupForm.reset();
    }
})

// 註冊流程 /////////////////////////////////////////////////////////////////////////////
const signupForm = document.querySelector(".signupForm");
signupForm.addEventListener("submit", function(event){
    event.preventDefault();
    const name = document.querySelector(".nameSignup").value;
    const email = document.querySelector(".emailSignup").value;
    const password = document.querySelector(".passwordSignup").value;
    let jsonObject = {};
    jsonObject["name"] = name;
    jsonObject["email"] = email;
    jsonObject["password"] = password;
    if (name.trim() === "" || email.trim() === "" || password.trim() === ""){
        alert("請確認填寫所有欄位");
        return;
    }else{
        fetch("/api/user", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jsonObject)
        }).then(function(response){
            return response.json();
        }).then(function(data){
            if (data.ok){
                signupResultOk.classList.add("active");
                signupResultFailed.classList.remove("active");
            }else{
                signupResultFailed.classList.add("active");
                signupResultOk.classList.remove("active");
            }
        }).catch(function(error){
            console.log(error);
        })
    }
})

// 登入流程 /////////////////////////////////////////////////////////////////////////////
const signinForm = document.querySelector(".signinForm");
signinForm.addEventListener("submit", function(event){
    event.preventDefault();
    const email = document.querySelector(".emailSignin").value;
    const password = document.querySelector(".passwordSignin").value;
    const signinResultFailed = document.querySelector(".signinResultFailed");
    let jsonObject = {};
    jsonObject["email"] = email;
    jsonObject["password"] = password;
    if (email.trim() === "" || password.trim() === ""){
        alert("請確認填寫所有欄位");
        return;
    }else{
        fetch("/api/user/auth", {
            method: "PUT",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jsonObject)
        }).then(function(response){
            return response.json();
        }).then(function(data){ 
            if (data.token){
                localStorage.setItem("token", data.token);
                location.reload();
            }else{
                signinResultFailed.classList.add("active");
            }
        }).catch(function(error){
            console.log(error);
        })
    }
})

// 登出流程 /////////////////////////////////////////////////////////////////////////////
document.querySelector(".navigationButtonRightSignoutText").addEventListener("click", function(){
    localStorage.removeItem("token");
    location.reload();
})

// Function Part ///////////////////////////////////////////////////////////////////////
async function bookingButton(){
    try{
        const token = localStorage.getItem("token");
        if (token){
            window.location.href = "/booking";
        }else{
            showSignIn();
        }
    }catch(error){
        console.log(error);
    }
}

function showSignIn(){
    dialogSignin.style.display = "block";
    dialogSignup.style.display = "none";
    overlay.style.display = "block";
}

function showSignUp(){
    dialogSignup.style.display = "block";
    dialogSignin.style.display = "none";
    overlay.style.display = "block";
}