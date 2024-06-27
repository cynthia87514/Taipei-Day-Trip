import json, mysql.connector, re

with open("./data/taipei-attractions.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    result = data["result"]
    results = result["results"]

con = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="19980514",
    database="taipei-day-trip"
)

try:
    cursor = con.cursor()
    category = {}
    mrt = {}
    for i in results:
        name = i["name"]
        CAT = i["CAT"]
        description = i["description"]
        address = i["address"]
        direction = i["direction"]
        MRT = i["MRT"]
        latitude = i["latitude"]
        longitude = i["longitude"]
        file = i["file"]
        images = re.findall(r'(.*?\.(?:jpg|JPG|png|PNG))', file)
        images = str(images)
        # 建立 categorys table 並取出對應的 category_id
        if CAT not in category:
            cursor.execute("INSERT INTO `categorys` (name) VALUES (%s)", (CAT,))
            con.commit()
            category[CAT] = 1
        cursor.execute("SELECT id FROM `categorys` WHERE name = %s", (CAT,))
        category_result = cursor.fetchall()[0]
        category_id = category_result[0]
        # 建立 mrts table 並取出對應的 mrt_id
        if MRT not in mrt:
            cursor.execute("INSERT INTO `mrts` (name) VALUES (%s)", (MRT,))
            con.commit()
            mrt[MRT] = 1
        if MRT != None:
            cursor.execute("SELECT id FROM `mrts` WHERE name = %s", (MRT,))
            mrt_result = cursor.fetchall()[0]
            mrt_id = mrt_result[0]
        else:
            mrt_id = None
        # 根據上述參數將資料加入 attractions table 的對應欄位
        cursor.execute("INSERT INTO `attractions` (name, category_id, description, address, transport, mrt_id, latitude, longitude, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, category_id, description, address, direction, mrt_id, latitude, longitude, images))
        # 添加外鍵，將對應表格及欄位做關聯
        cursor.execute("ALTER TABLE `attractions` ADD FOREIGN KEY (category_id) REFERENCES categorys(id)")
        cursor.execute("ALTER TABLE `attractions` ADD FOREIGN KEY (mrt_id) REFERENCES mrts(id)")
        # 完成資料庫變更
        con.commit()
finally:
    con.close()