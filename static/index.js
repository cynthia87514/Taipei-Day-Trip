document.addEventListener("DOMContentLoaded", function(){
    // 點擊左右箭頭按鈕的 function
    const arrowLeft = document.querySelector(".arrowLeft");
    const arrowRight = document.querySelector(".arrowRight");
    const listItemContainer = document.querySelector(".listItemContainer");

    arrowLeft.addEventListener("click", function(){
        listItemContainer.scrollBy({left: -500, behavior: "smooth"});
        console.log("左邊左邊");
    })
    arrowRight.addEventListener("click", function(){
        listItemContainer.scrollBy({left: 500, behavior: "smooth"});
        console.log("右邊右邊");
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
    fetch("http://127.0.0.1:8000/api/mrts").then(function(response){
        return response.json();
    }).then(function(data){
        const mrts = data.data;
        // 裝捷運站的盒子
        const listItemContainer = document.querySelector(".listItemContainer");
        // console.log(mrts);
        // console.log(mrts.length);
        for (let i = 0 ; i < mrts.length ; i++){
            const listItem = document.createElement("div");
            listItem.setAttribute("class", "listItem");
            listItemContainer.appendChild(listItem);
        
            const listItemText = document.createElement("div");
            listItemText.textContent = mrts[i];
            listItemText.setAttribute("class", "listItemText");
            listItemText.style.width = mrts[i].length * 16 + "px";
            listItem.appendChild(listItemText);

            // 點擊捷運站名，會將該站名顏色變黑、並送入搜尋框
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
    fetch("http://127.0.0.1:8000/api/attractions?page=0").then(function(response){
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
                detailsNameText.textContent = attractions[i].name;
                detailsNameText.setAttribute("class", "detailsNameText");
                detailsNameInfo.appendChild(detailsNameText);

                // 放入捷運站名
                const detailsMrtText = document.createElement("div");
                detailsMrtText.textContent = attractions[i].mrt;
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
            rootMargin: "0px", // 預先載入多少 px
            threshold: 0.05 // 目標元素的多少 % 進入畫面中才會被觀察
        };

        const callback = (entries, observer) => { // entries 陣列包含多筆被觀察的元素
            entries.forEach(entry => { //對每一筆 entry 做事
                // console.log(entry); // entry 為 entries 陣列中的其中一筆資料，內含觀察的多個項目
                // console.log(observer);
                // console.log(entry.isIntersecting); // 該元素是否有被觀察到 (是否有出現在畫面中)，為一布林值
                // console.log(entry.target); // 被觀察的元素本身，可用來對元素編輯，如：加上 class
                if (entry.isIntersecting && nextPage !== null){
                    // observer.unobserve(entry.target); // 當該元素已被觀察過，即取消關注，避免重複執行
                    if (keyword === null){
                        const baseURL = "http://127.0.0.1:8000/api/attractions";
                        modifiedURL = `${baseURL}?page=${nextPage}`;
                        // 如果偵測到 scroll 到頁面最下方，再 fetch 新的資料進來
                        fetch(modifiedURL).then(function(response){
                            return response.json();
                        }).then(function(data){
                            attractions = data.data;
                            nextPage = data.nextPage;
                            loadData();
                    })
                    }else{
                        const baseURL = "http://127.0.0.1:8000/api/attractions";
                        modifiedURL = `${baseURL}?page=${nextPage}&keyword=${keyword}`;
                        // 如果偵測到 scroll 到頁面最下方，再 fetch 新的資料進來
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

                const URL = "http://127.0.0.1:8000/api/attractions?page=0&keyword=" + encodeURIComponent(keyword);

                fetch(URL).then(function(response){
                    return response.json(); 
                }).then(function(data){
                    attractions = data.data;
                    nextPage = data.nextPage;
                    loadData();
                    })
                }
            })
        })
    })






