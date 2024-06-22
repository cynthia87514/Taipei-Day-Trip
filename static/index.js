// 點擊 台北一日遊 回到首頁
const navigationText = document.querySelector(".navigationText");
navigationText.addEventListener("click", function(){
window.location.href = "/";
})

// 點擊左右箭頭按鈕的 function
const arrowLeft = document.querySelector(".arrowLeft");
const arrowRight = document.querySelector(".arrowRight");
const listItemContainer = document.querySelector(".listItemContainer");

arrowLeft.addEventListener("click", function(){
listItemContainer.scrollBy({left: -500, behavior: "smooth"});
})
arrowRight.addEventListener("click", function(){
listItemContainer.scrollBy({left: 500, behavior: "smooth"});
})
arrowLeft.addEventListener("mouseover", function(){
arrowLeft.style.opacity = "100%";
})
arrowLeft.addEventListener("mouseout", function(){
arrowLeft.style.opacity = "50%";
})
arrowRight.addEventListener("mouseover", function(){
arrowRight.style.opacity = "100%";
})
arrowRight.addEventListener("mouseout", function(){
arrowRight.style.opacity = "50%";
})


// 捷運站列表
fetch("./api/mrts").then(function(response){
return response.json();
}).then(function(data){
const mrts = data.data;
const listItemContainer = document.querySelector(".listItemContainer");
for (let i = 0 ; i < mrts.length ; i++){
    const listItem = document.createElement("div");
    listItem.setAttribute("class", "listItem");
    listItemContainer.appendChild(listItem);

    const listItemText = document.createElement("div");
    listItemText.textContent = mrts[i];
    listItemText.setAttribute("class", "listItemText");
    listItemText.style.width = mrts[i].length * 16 + "px";
    listItem.appendChild(listItemText);

    // 點擊捷運站名，送入搜尋框
    listItemText.addEventListener("click", function(){
        listItemText.style.color = "#000000";
        const input = document.querySelector("input");
        input.value = mrts[i];
        const searchBtn = document.querySelector(".searchBtn");
        searchBtn.click();
    })
    listItemText.addEventListener("mouseover", function(){
        listItemText.style.color = "#000000";
    })
    listItemText.addEventListener("mouseout", function(){
        listItemText.style.color = "#666666";
    })
}

})


let keyword = null;

// 景點圖片、名稱、種類、對應的捷運站
fetch("./api/attractions?page=0").then(function(response){
return response.json();
}).then(function(data){
let attractions = data.data;
let nextPage = data.nextPage;

// 載入景點資料的 function
const loadData = () => {
    const attractionsGroup = document.querySelector(".attractionsGroup");
    for (let i = 0 ; i < attractions.length ; i++){
        const attraction = document.createElement("div");
        attraction.setAttribute("class", "attraction");
        attractionsGroup.appendChild(attraction);
        
        // 點擊圖片會將畫面導到相應景點頁面
        const id = attractions[i].id;
        attraction.addEventListener("click", function(){
            window.location.href = `/attraction/${id}`;
        })

        // 放入景點圖片
        const attractionImg = document.createElement("div");
        attractionImg.style.backgroundImage = "url(" + attractions[i].images[0] + ")";
        attractionImg.setAttribute("class", "attractionImg");
        attraction.appendChild(attractionImg);

        const detailsName = document.createElement("div");
        detailsName.setAttribute("class", "detailsName");
        attractionImg.appendChild(detailsName);

        const detailsMrtCat = document.createElement("div");
        detailsMrtCat.setAttribute("class", "detailsMrtCat");
        attraction.appendChild(detailsMrtCat);

        const detailsMrtCatInfo = document.createElement("div");
        detailsMrtCatInfo.setAttribute("class", "detailsMrtCatInfo");
        detailsMrtCat.appendChild(detailsMrtCatInfo);
        const detailsNameInfo = document.createElement("div");
        detailsNameInfo.setAttribute("class", "detailsNameInfo");
        detailsName.appendChild(detailsNameInfo);

        // 放入景點名稱
        const detailsNameText = document.createElement("div");
        if (attractions[i].name.length > 15){
            detailsNameText.textContent = attractions[i].name.substring(0, 14) + "...";
        }
        else{
            detailsNameText.textContent = attractions[i].name;
        }
        detailsNameText.setAttribute("class", "detailsNameText");
        detailsNameInfo.appendChild(detailsNameText);

        // 放入捷運站名
        const detailsMrtText = document.createElement("div");
        if (attractions[i].mrt === null){
            detailsMrtText.textContent = "無";
        }
        else{
            detailsMrtText.textContent = attractions[i].mrt;
        }
        detailsMrtText.setAttribute("class", "detailsMrtText");
        detailsMrtCatInfo.appendChild(detailsMrtText);

        // 放入景點類別
        const detailsCatText = document.createElement("div");
        detailsCatText.textContent = attractions[i].category;
        detailsCatText.setAttribute("class", "detailsCatText");
        detailsMrtCatInfo.appendChild(detailsCatText);
    }
};
// 呼叫 function，載入首頁畫面
loadData();

// 使用 IntersectionObserver 物件，實現 Infinite Scroll
const options = {
    root: null,
    rootMargin: "0px",
    threshold: 0.05
};

const callback = (entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && nextPage !== null){
            if (keyword === null){
                const baseURL = "./api/attractions";
                modifiedURL = `${baseURL}?page=${nextPage}`;
                fetch(modifiedURL).then(function(response){
                    return response.json();
                }).then(function(data){
                    attractions = data.data;
                    nextPage = data.nextPage;
                    loadData();
            })
            }else{
                const baseURL = "./api/attractions";
                modifiedURL = `${baseURL}?page=${nextPage}&keyword=${keyword}`;
                fetch(modifiedURL).then(function(response){
                    return response.json();
                }).then(function(data){
                    attractions = data.data;
                    nextPage = data.nextPage;
                    loadData();
                })
            }
            
        }
    });
}
const observer = new IntersectionObserver(callback, options);

// 定義欲觀察的元素
const target = document.querySelector("footer");
observer.observe(target);

// Keyword Search Function
document.querySelector(".searchBtn").addEventListener("click", function(){
    keyword = document.querySelector("input").value;
    if (keyword.trim() === ""){
        return;
    }
    if (keyword != null){
        let attractionsGroup = document.querySelector(".attractionsGroup");
        while (attractionsGroup.firstChild){
            attractionsGroup.removeChild(attractionsGroup.firstChild);
        }

        const URL = "./api/attractions?page=0&keyword=" + encodeURIComponent(keyword);

        fetch(URL).then(function(response){
            return response.json(); 
        }).then(function(data){
            // 若 keyword 搜尋結果為空，則返回 "查無相關資料"
            if (data.data.length === 0){
                const nonattraction = document.createElement("div");
                nonattraction.textContent = "查無相關資料";
                nonattraction.setAttribute("class", "nonattraction");
                attractionsGroup.appendChild(nonattraction);
            }
            else{
                attractions = data.data;
                nextPage = data.nextPage;
                loadData();
            }
            })
        }
    })
})

// 設定按下 Enter 鍵時，觸發按下搜尋鍵的效果
document.querySelector("input").addEventListener("keypress", function(event){
    if (event.key === "Enter"){
        document.querySelector(".searchBtn").click();
    }
})

// Pop-Up Dialog for User Sign Up/In
const dialogSignin = document.querySelector(".dialogSignin");
const dialogSignup = document.querySelector(".dialogSignup");
const overlay = document.querySelector(".overlay");
const signupResultOk = document.querySelector(".signupResultOk");
const signupResultFailed = document.querySelector(".signupResultFailed");

// 點按 登入/註冊 開啟 Dialog SignIn (Default)
document.querySelector(".navigationButtonRightText").addEventListener("click", function(){
    dialogSignin.style.display = "block";
    dialogSignup.style.display = "none";
    overlay.style.display = "block";
})
// 點按 註冊 開啟 Dialog SignUp
document.querySelector(".toSignupBtn").addEventListener("click", function(){
    dialogSignup.style.display = "block";
    dialogSignin.style.display = "none";
})
// 點按 登入 開啟 Dialog SignIn
document.querySelector(".toSigninBtn").addEventListener("click", function(){
    dialogSignin.style.display = "block";
    dialogSignup.style.display = "none";
    signupResultOk.classList.remove("active");
    signupResultFailed.classList.remove("active");
    signupForm.reset();
})
// 點按 cross 關閉 Dialog
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

// User Sign-In Status Checking Procedure
async function fetchUserData(){
    try{
        const token = localStorage.getItem("token");
        if (!token){
            const data = null;
            return data;
        }
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

async function updatePage(){
    const signin = document.querySelector(".navigationButtonRight");
    const signout = document.querySelector(".navigationButtonRightSignout");
    try{
        const userData = await fetchUserData();
        if (userData === null){
            return;
        }
        else if(userData.data){
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

// Sign Up Procedure
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

// Sign In Procedure
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

// 載入頁面時確認使用者狀態
document.addEventListener("DOMContentLoaded", function(){
    updatePage();
})

// Sign Out Procedure
document.querySelector(".navigationButtonRightSignoutText").addEventListener("click", function(){
    localStorage.removeItem("token");
    location.reload();
})