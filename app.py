from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import pooling
import ast, jwt
from datetime import datetime, timedelta

app = FastAPI()
cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "mypool",
    pool_size = 32,
    pool_reset_session = True,
	host="localhost",
    port="3306",
    user="root",
    password="19980514",
    database="taipei-day-trip"
)

def get_db_connection():
	con = cnxpool.get_connection()
	if con.is_connected():
		print("Successfully connected to MySQL database.")
		cursor = con.cursor(dictionary = True)
		return con, cursor
	else:
		print("Failed to connect to MySQL database.")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Secret key to sign JWT token
secret_key = "mysecretkey"

# Create JWT token
def create_jwt_token(id: int, name: str, email: str) -> str:
	expiration_time = datetime.utcnow() + timedelta(days=7)
	payload = {
		"sub": id,
		"name": name,
		"email": email,
		"iat": datetime.utcnow(),
        "exp": expiration_time
	}
	token = jwt.encode(payload, secret_key, algorithm="HS256")
	return token

# Decode and Verify JWT token
def verify_jwt_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, secret_key, algorithms=["HS256"])
		return payload
	except jwt.ExpiredSignatureError:
		print("Token has expired")
		return None
	except jwt.InvalidTokenError as e:
		print("Invalid token:", e)
		return None

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

# User APIs
# 註冊一個新的會員
@app.post("/api/user")
async def signup(request: Request, response: Response, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
	con, cursor = get_db_connection()
	try:
		cursor.execute("SELECT * FROM `users` WHERE email = %s;", (email,))
		existing_user = cursor.fetchone()
		if existing_user is None:
			cursor.execute("INSERT INTO `users` (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
			con.commit()
			response = {
				"ok": True
				}
			return response
		else:
			# response.status_code = 400
			response = {
				"error": True,
				"message": "註冊失敗，重複的 Email 或其他原因"
				}
			return response
	except:
		response.status_code = 500
		response = {
			"error": True,
			"message": "伺服器內部錯誤"
			}
		return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")

# 取得當前登入的會員資訊
@app.get("/api/user/auth")
async def user_data(request: Request, response: Response):
	con, cursor = get_db_connection()
	try:
		token = request.headers.get("Authorization").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is not None:
			id = payload.get("sub")
			cursor.execute("SELECT id, name, email FROM `users` WHERE id = %s", (id,))
			user = cursor.fetchone()
			response = {
				"data": {
					"id": user["id"],
					"name": user["name"],
					"email": user["email"]
				}
			}
			return response
		else:
			response = {
				"data": None
			}
			return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")

# 登入會員帳戶
@app.put("/api/user/auth")
async def signin(request: Request, response: Response, email: str = Form(...), password: str = Form(...)):
	con, cursor = get_db_connection()
	try:
		cursor.execute("SELECT id, name, email FROM `users` WHERE email = %s AND password = %s", (email, password))
		user = cursor.fetchone()
		if user:
			id = user["id"]
			name = user["name"]
			email = user["email"]
			token = create_jwt_token(id, name, email)
			response = {
				"token": token
				}
			return response
		else:
			response.status_code = 400
			response = {
				"error": True,
				"message": "登入失敗，帳號或密碼錯誤或其他原因"
				}
			return response
	except:
		response.status_code = 500
		response = {
			"error": True,
			"message": "伺服器內部錯誤"
			}
		return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")


# Attraction APIs
# 取得景點資料列表
@app.get("/api/attractions")
async def attractionslist(request: Request, response: Response, page: int = Query(0), keyword: str = Query(None)):
	con, cursor = get_db_connection()
	try:
		offset = page * 12
		limit = 12
		if keyword == None:
			cursor.execute("""
				SELECT `attractions`.*, `categorys`.name AS category, `mrts`.name AS mrt
				FROM `attractions`
				LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
				LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
				LIMIT %s, %s
				""", (offset, limit))
			attractions_data = cursor.fetchall()
			datalst = []
			for attraction_data in attractions_data:
				data = {
				"id": attraction_data["id"],
				"name": attraction_data["name"],
				"category": attraction_data["category"],
				# "category_id": attraction_data["category_id"],
				"description": attraction_data["description"],
				"address": attraction_data["address"],
				"transport": attraction_data["transport"],
				"mrt": attraction_data["mrt"],
				# "mrt_id": attraction_data["mrt_id"],
				"lat": attraction_data["latitude"],
				"lng": attraction_data["longitude"],
				"images":ast.literal_eval(attraction_data["images"])
				}
				datalst.append(data)
			cursor.execute("SELECT COUNT(*) FROM `attractions`")
			total = cursor.fetchone()["COUNT(*)"]
			totalpage = total // limit + 1
			if page < totalpage - 1:
				nextpage = page + 1
			else:
				nextpage = None
			
			return {
				"nextPage": nextpage,
				"data": datalst,
				}

		if keyword != None:
			cursor.execute("""
				SELECT `attractions`.*, `categorys`.name AS category, `mrts`.name AS mrt
				FROM `attractions`
				LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
				LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
				WHERE `mrts`.name = %s OR `attractions`.name LIKE %s
				LIMIT %s, %s
				""", (keyword, '%' + keyword + '%', offset, limit))
			attractions_data = cursor.fetchall()
			datalst = []
			for attraction_data in attractions_data:
				data = {
				"id": attraction_data["id"],
				"name": attraction_data["name"],
				"category": attraction_data["category"],
				# "category_id": attraction_data["category_id"],
				"description": attraction_data["description"],
				"address": attraction_data["address"],
				"transport": attraction_data["transport"],
				"mrt": attraction_data["mrt"],
				# "mrt_id": attraction_data["mrt_id"],
				"lat": attraction_data["latitude"],
				"lng": attraction_data["longitude"],
				"images":ast.literal_eval(attraction_data["images"])
				}
				datalst.append(data)

			cursor.execute("""
				SELECT COUNT(*) FROM `attractions`
				LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
				LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
				WHERE `mrts`.name = %s OR `attractions`.name LIKE %s
				""", (keyword, '%' + keyword + '%'))
			total = cursor.fetchone()["COUNT(*)"]
			totalpage = total // limit + 1
			if page < totalpage - 1:
				nextpage = page + 1
			else:
				nextpage = None
			
			return {
				"nextPage": nextpage,
				"data": datalst,
				}
	except:
		response.status_code = 500
		response = {
			"error": True,
			"message": "伺服器內部錯誤"
			}
		return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")

# 根據景點編號取得景點資料
@app.get("/api/attraction/{attractionId}")
async def attractiondata(request: Request, response: Response, attractionId: int = Path(...)):
	con, cursor = get_db_connection()
	try:
		cursor.execute("SELECT id, name, description, address, transport, latitude, longitude, images FROM `attractions` WHERE id = %s", (attractionId,))
		attraction_data = cursor.fetchone()
		cursor.execute("SELECT `categorys`.name FROM `attractions` JOIN `categorys` ON `attractions`.category_id = `categorys`.id WHERE `attractions`.id = %s", (attractionId,))
		category_data = cursor.fetchone()
		cursor.execute("SELECT `mrts`.name FROM `attractions` LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id WHERE `attractions`.id = %s", (attractionId,))
		mrt_data = cursor.fetchone()
		if attraction_data and category_data and mrt_data:
			data = {
				"id": attraction_data["id"],
				"name": attraction_data["name"],
				"category": category_data["name"],
				"description": attraction_data["description"],
				"address": attraction_data["address"],
				"transport": attraction_data["transport"],
				"mrt": mrt_data["name"],
				"lat": attraction_data["latitude"],
				"lng": attraction_data["longitude"],
				"images":ast.literal_eval(attraction_data["images"])
			}
			return {"data": data}
		else:
			response.status_code = 400
			response = {
				"error": True,
				"message": "景點編號不正確"
				}
			return response
	except:
		response.status_code = 500
		response = {
			"error": True,
			"message": "伺服器內部錯誤"
			}
		return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")

# MRT Station APIs
# 取得捷運站名稱列表
@app.get("/api/mrts")
async def mrtslist(request: Request, response: Response):
	con, cursor = get_db_connection()
	try:
		cursor.execute("""
			SELECT `mrts`.name,
			COUNT(*) AS mrt_num
			FROM attractions
			JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
			GROUP BY `attractions`.mrt_id, `mrts`.name
			ORDER BY mrt_num DESC
			""")
		mrts_data = cursor.fetchall()
		data = []
		for mrt_data in mrts_data:
			data.append(mrt_data["name"])
		return {"data": data}
	except:
		response.status_code = 500
		response = {
			"error": True,
			"message": "伺服器內部錯誤"
			}
		return response
	finally:
		print("--------------------------------------------------------")
		con.close()
		print("Successfully returned the connection to connection pool.")