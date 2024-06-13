document.addEventListener("DOMContentLoaded", function(){
    // 畫面加載
    let URL = window.location.href;
    URL = URL.split("/");
    const attractionId = URL[URL.length - 1];
    if (1 <= attractionId && attractionId <= 58){
        fetch(`/api/attraction/${attractionId}`).then(function(response){
            return response.json();
        }).then(function(data){
            const attraction = data.data;

            // 渲染景點圖片
            const pictures = document.querySelector(".pictures");
            const amount =  attraction.images.length;
            const picture = document.createElement("div");
            picture.setAttribute("class", "picture");
            picture.style.backgroundImage = "url(" + attraction.images[0] + ")";
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
                    picture.style.backgroundImage = "url(" + attraction.images[i] + ")";
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
                    picture.style.backgroundImage = "url(" + attraction.images[amount-1] + ")";
                    current = amount - 1;
                    targetId = "circle" + current;
                    changeCircle();
                }
                else if (current > 0){
                    picture.style.backgroundImage = "url(" + attraction.images[current-1] + ")";
                    current--;
                    targetId = "circle" + current;
                    changeCircle();
                }
                picture.classList.remove("fade-out");
            })
            rightArrow.addEventListener("click", function(){
                picture.classList.add("fade-out");
                if (current === amount-1){
                    picture.style.backgroundImage = "url(" + attraction.images[0] + ")";
                    current = 0;
                    targetId = "circle" + current;
                    changeCircle();
                }
                else if (current < amount-1){
                    picture.style.backgroundImage = "url(" + attraction.images[current+1] + ")";
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

    // 點擊 台北一日遊 回到首頁
    const navigationText = document.querySelector(".navigationText");
    navigationText.addEventListener("click", function(){
        window.location.href = "/";
    })

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
})