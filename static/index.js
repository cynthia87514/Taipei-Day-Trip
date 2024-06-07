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
                    attractions = data.data;
                    nextPage = data.nextPage;
                    loadData();
                    })
                }
            })
        })
    })






