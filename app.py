from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
# from mysql.connector import pooling
import ast, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, conint
from typing import Optional, List
from enum import Enum, IntEnum
import tappay

# 設置環境變數
from dotenv import dotenv_values
secrets = dotenv_values(".env")

app = FastAPI()
cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "mypool",
    pool_size = 32,
    pool_reset_session = True,
	host = secrets["MYSQL_HOST"],
    port = secrets["MYSQL_PORT"],
    user = secrets["MYSQL_USER"],
    password = secrets["MYSQL_PASSWORD"],
    database = secrets["MYSQL_DATABASE"]
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
secret_key = secrets["JWT_SECRET_KEY"]

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

# 建立 Model #########################################
# User APIs
class SignUpInfo(BaseModel):
	name: str
	email: EmailStr
	password: str

class SignInInfo(BaseModel):
	email: EmailStr
	password: str

class UserInfo(BaseModel):
	id: Optional[int]
	name: Optional[str]
	email: Optional[EmailStr]

class UserData(BaseModel):
	data: Optional[UserInfo] = None

class Token(BaseModel):
	token: str

# Attraction APIs
class Attraction(BaseModel):
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: Optional[str] = None
	lat: float
	lng: float
	images: List[str]

class Attractions(BaseModel):
	nextPage: Optional[int] = None
	data: List[Attraction]

class AttractionId(BaseModel):
	data: Attraction

# MRT APIs
class MrtList(BaseModel):
	data: List[str]

# Booking APIs
class BookingAttraction(BaseModel):
	id: int
	name: str
	address: str
	image: str

class BookingData(BaseModel):
	attraction: BookingAttraction
	date: str
	time: str
	price: int

class BookingPage(BaseModel):
	data: Optional[BookingData] = None

class TimeEnum(str, Enum):
	morning = "morning"
	afternoon = "afternoon"

class PriceEnum(IntEnum):
	morning = 2000
	afternoon = 2500

class CreateBooking(BaseModel):
	attractionId: int
	date: str
	time: TimeEnum
	price: PriceEnum

# Order APIs
class TripInfo(BaseModel):
	attraction: BookingAttraction
	date: str
	time: TimeEnum

class ContactInfo(BaseModel):
	name: str
	email: EmailStr
	phone: str

class OrderInput(BaseModel):
	price: PriceEnum
	trip: TripInfo
	contact: ContactInfo

class CreateOrder(BaseModel):
	prime: str
	order: OrderInput

class StatusEnum(IntEnum):
    PAID = 0
    UNPAID = 1

class MessageEnum(str, Enum):
	PAID = "付款成功"
	UNPAID = "付款失敗"

class PaymentStatus(BaseModel):
	status: StatusEnum
	message: MessageEnum

class OrderResult(BaseModel):
	number: str
	payment: PaymentStatus

class OrderData(BaseModel):
	data: OrderResult

class Order(BaseModel):
	number: str
	price: PriceEnum
	trip: TripInfo
	contact: ContactInfo
	status: StatusEnum

class GetOrderInfo(BaseModel):
	data: Optional[Order] = None

# Ok 回應
class OkResponse(BaseModel):
	ok: bool

# Error 回應
class ErrorResponse(BaseModel):
	error: bool
	message: str

# User APIs
# 註冊一個新的會員
@app.post("/api/user", response_model = OkResponse, responses = {400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def signup(request: Request, response: Response, user_data: SignUpInfo = Body(...)):
	con, cursor = get_db_connection()
	try:
		name = user_data.name
		email = user_data.email
		password = user_data.password
		cursor.execute("SELECT * FROM `users` WHERE email = %s;", (email,))
		existing_user = cursor.fetchone()
		if existing_user is None:
			cursor.execute("INSERT INTO `users` (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
			con.commit()
			return OkResponse(ok=True)
		else:
			raise HTTPException(status_code=400, detail={"error": True, "message": "註冊失敗，重複的 Email 或其他原因"})
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	finally:
		con.close()
		print("Successfully returned the connection to connection pool.")

# 取得當前登入的會員資訊
@app.get("/api/user/auth", response_model = UserData)
async def user_data(request: Request, response: Response):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	if not token:
		return UserData(data=None)
	try:
		payload = verify_jwt_token(token)
		if payload:
			user_info = UserInfo(
                id = payload.get("sub"),
                name = payload.get("name"),
                email = payload.get("email")
            )
			return UserData(data=user_info)
		else:
			return UserData(data=None)
	except HTTPException:
		return UserData(data=None)

# 登入會員帳戶
@app.put("/api/user/auth", response_model = Token, responses = {400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def signin(request: Request, response: Response, user_data: SignInInfo = Body(...)):
	con, cursor = get_db_connection()
	try:
		email = user_data.email
		password = user_data.password
		cursor.execute("SELECT id, name, email FROM `users` WHERE email = %s AND password = %s", (email, password))
		user = cursor.fetchone()
		if user:
			token = create_jwt_token(user["id"], user["name"], user["email"])
			return Token(token=token)
		else:
			raise HTTPException(status_code=400, detail={"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"})
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	finally:
		con.close()
		print("Successfully returned the connection to connection pool.")


# Attraction APIs
# 取得景點資料列表
@app.get("/api/attractions", response_model = Attractions, responses = {500: {"model": ErrorResponse}})
async def attractionslist(request: Request, response: Response, page: int = Query(0), keyword: str = Query(None)):
	con, cursor = get_db_connection()
	try:
		offset = page * 12
		limit = 12

		base_query = """
			SELECT
				`attractions`.id,
				`attractions`.name,
				`categorys`.name AS category,
				`attractions`.description,
				`attractions`.address,
				`attractions`.transport,
				`mrts`.name AS mrt,
				`attractions`.latitude AS lat,
				`attractions`.longitude AS lng,
				`attractions`.images
			FROM `attractions`
			LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
			LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id 
		"""

		if keyword:
			query = f"""
				{base_query}
				WHERE `mrts`.name = %s OR `attractions`.name LIKE %s
				LIMIT %s, %s 
			"""
			params = (keyword, '%' + keyword + '%', offset, limit)
		else:
			query = f"""
				{base_query}
                GROUP BY `attractions`.id
                LIMIT %s, %s
			"""
			params = (offset, limit)
		
		cursor.execute(query, params)
		attractions_data = cursor.fetchall()
		for attraction_data in attractions_data:
			attraction_data["images"] = ast.literal_eval(attraction_data["images"])
		
		count_query = """
            SELECT COUNT(*) AS count 
            FROM `attractions`
            LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
            LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
        """
		if keyword:
			count_query += "WHERE `mrts`.name = %s OR `attractions`.name LIKE %s"
			count_params = (keyword, '%' + keyword + '%')
		else:
			count_params = ()

		cursor.execute(count_query, count_params)
		total = cursor.fetchone()["count"]
		totalpage = (total + limit - 1) // limit
		nextpage = page + 1 if page < totalpage - 1 else None
		
		data = [Attraction(**attraction) for attraction in attractions_data]
		return Attractions(nextPage=nextpage, data=data)
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	finally:
		con.close()
		print("Successfully returned the connection to connection pool.")

# 根據景點編號取得景點資料
@app.get("/api/attraction/{attractionId}", response_model = AttractionId, responses = {400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def attractiondata(request: Request, response: Response, attractionId: int = Path(...)):
	con, cursor = get_db_connection()
	try:
		cursor.execute("""
            SELECT 
                `attractions`.id AS id,
                `attractions`.name AS name,
				`categorys`.name AS category,
                `attractions`.description AS description, 
                `attractions`.address AS address, 
                `attractions`.transport AS transport,
				`mrts`.name AS mrt,
                `attractions`.latitude AS lat, 
                `attractions`.longitude AS lng, 
                `attractions`.images AS images
            FROM `attractions`
            LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
            LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
            WHERE `attractions`.id = %s
        """, (attractionId,))
		attraction_data = cursor.fetchone()
		if attraction_data:
			attraction_data["images"] = ast.literal_eval(attraction_data["images"])
			data = Attraction(**attraction_data)
			return AttractionId(data=data)
		else:
			raise HTTPException(status_code=400, detail={"error": True, "message": "景點編號不正確"})
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	finally:
		con.close()
		print("Successfully returned the connection to connection pool.")

# MRT Station APIs
# 取得捷運站名稱列表
@app.get("/api/mrts", response_model = MrtList, responses = {500: {"model": ErrorResponse}})
async def mrtslist(request: Request, response: Response):
	con, cursor = get_db_connection()
	try:
		cursor.execute("""
			SELECT `mrts`.name
			FROM `attractions`
			JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
			GROUP BY `attractions`.mrt_id, `mrts`.name
			ORDER BY COUNT(*) DESC
		""")
		mrts_data = cursor.fetchall()
		data = [mrt["name"] for mrt in mrts_data]
		return MrtList(data=data)
	except Exception as e:
		print(e)
		raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
	finally:
		con.close()
		print("Successfully returned the connection to connection pool.")

# 取得尚未確認下單的預定行程
@app.get("/api/booking", response_model = BookingPage, responses = {403: {"model": ErrorResponse}})
async def booking(request: Request, response: Response):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	payload = verify_jwt_token(token)
	if payload is None:
		raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
	else:
		con, cursor = get_db_connection()
		try:
			user_id = payload.get("sub")
			cursor.execute("SELECT * FROM `booking` WHERE user_id = %s", (user_id,))
			existing_booking = cursor.fetchone()
			if existing_booking:
				attraction_id = existing_booking["attraction_id"]
				cursor.execute("SELECT name, address, images FROM `attractions` WHERE id = %s", (attraction_id,))
				attraction_data = cursor.fetchone()
				attraction_data["image"] = ast.literal_eval(attraction_data["images"])[0]
				data = BookingData(
					attraction = BookingAttraction(
						id = attraction_id,
						**attraction_data
					),
					date = existing_booking["date"],
                    time = existing_booking["time"],
                    price = existing_booking["price"]
				)
				return BookingPage(data=data)
			else:
				return BookingPage(data=None)
		finally:
			con.close()
			print("Successfully returned the connection to connection pool.")

# 建立新的預定行程
@app.post("/api/booking", response_model = OkResponse, responses = {400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_booking(request: Request, response: Response, booking_data: CreateBooking = Body(...)):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	payload = verify_jwt_token(token)
	if payload is None:
		raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
	else:
		con, cursor = get_db_connection()
		try:
			user_id = payload.get("sub")
			attractionId = booking_data.attractionId
			date = booking_data.date
			time = booking_data.time.value
			price = booking_data.price

			if not attractionId or not date or not time or not price:
				raise HTTPException(status_code=400, detail={"error": True, "message": "建立失敗，輸入不正確或其他原因"})
	
			cursor.execute("SELECT * FROM `booking` WHERE user_id = %s;", (user_id,))
			existing_booking = cursor.fetchone()

			if existing_booking:
				sql = "UPDATE `booking` SET attraction_id = %s, date = %s, time = %s, price = %s WHERE user_id = %s"
				val = (attractionId, date, time, price, user_id)
			else:
				sql = "INSERT INTO `booking` (user_id, attraction_id, date, time, price) VALUES (%s, %s, %s, %s, %s)"
				val = (user_id, attractionId, date, time, price)
				
			cursor.execute(sql, val)
			con.commit()
			return OkResponse(ok=True)
		
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
		finally:
			con.close()
			print("Successfully returned the connection to connection pool.")

# 刪除目前的預定行程
@app.delete("/api/booking", response_model = OkResponse, responses = {403: {"model": ErrorResponse}})
async def delete_booking(request: Request, response: Response):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	payload = verify_jwt_token(token)
	if payload is None:
		raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
	else:
		con, cursor = get_db_connection()
		try:
			user_id = payload.get("sub")
			cursor.execute("DELETE FROM `booking` WHERE user_id = %s;", (user_id,))
			con.commit()
			return OkResponse(ok=True)
		finally:
			con.close()
			print("Successfully returned the connection to connection pool.")

# Order APIs
# 建立新的訂單，並完成付款程序
@app.post("/api/orders", response_model = OrderData, responses = {400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_order(request: Request, response: Response, create_order: CreateOrder = Body(...)):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	payload = verify_jwt_token(token)
	if payload is None:
		raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
	else:
		con, cursor = get_db_connection()
		try:
			user_id = payload.get("sub")
			prime = create_order.prime
			order_input = create_order.order
			total_price = order_input.price.value
			trip_info = order_input.trip
			booking_attraction = trip_info.attraction
			attraction_id = booking_attraction.id
			attraction_name = booking_attraction.name
			# attraction_address = booking_attraction.address
			# attraction_image = booking_attraction.image
			trip_date = trip_info.date
			trip_time = trip_info.time.value
			contact_info = order_input.contact
			contact_name = contact_info.name
			contact_email = contact_info.email
			contact_phone = contact_info.phone
			if not prime or not order_input:
				raise HTTPException(status_code=400, detail={"error": True, "message": "訂單建立失敗，輸入不正確或其他原因"})
			cursor.execute("""
                INSERT INTO `order` (user_id, prime, total_price, contact_name, contact_email, contact_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, prime, total_price, contact_name, contact_email, contact_phone))
			order_id = cursor.lastrowid
			cursor.execute("""
                INSERT INTO `orderItems` (order_id, attraction_id, trip_date, trip_time, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, attraction_id, trip_date, trip_time, total_price))
			con.commit()

			current_date = datetime.now().strftime("%Y%m%d")
			formatted_order_id = f"{order_id:06d}"
			formatted_user_id = f"{user_id:06d}"
			order_number = f"{current_date}{formatted_order_id}{formatted_user_id}"

			# calling TapPay Pay By Prime API
			client = tappay.Client(True, secrets["TAPPAY_PARTNER_KEY"], secrets["TAPPAY_MERCHANT_ID"])

			card_holder_data = tappay.Models.CardHolderData(contact_phone, contact_name, contact_email)
			payment_response = client.pay_by_prime(
				prime = prime,
				amount = total_price,
				details = attraction_name,
				card_holder_data = card_holder_data,
				order_number = order_number
			)

			if payment_response["status"] == 0:
				payment_status = "SUCCESS"
				status_response = StatusEnum.PAID
				message_response = MessageEnum.PAID
				cursor.execute("UPDATE `order` SET payment_status = 'PAID' WHERE id = %s", (order_id,))
			else:
				payment_status = "FAILURE"
				status_response = StatusEnum.UNPAID
				message_response = MessageEnum.UNPAID
			
			payment_sql = "INSERT INTO `payment` (order_id, payment_amount, payment_status) VALUES (%s, %s, %s)"
			payment_val = (order_id, total_price, payment_status)
			cursor.execute(payment_sql, payment_val)
			con.commit()

			return OrderData(
                data=OrderResult(
                    number=order_number,
                    payment=PaymentStatus(
                        status=status_response,
                        message=message_response
                    )
                )
            )
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail={"error": True, "message": "伺服器內部錯誤"})
		finally:
			con.close()
			print("Successfully returned the connection to connection pool.")

# 根據訂單編號取得訂單資訊
@app.get("/api/order/{orderNumber}", response_model = GetOrderInfo, responses = {403: {"model": ErrorResponse}})
async def get_order_data(request: Request, response: Response, orderNumber: str = Path(...)):
	token = request.headers.get("Authorization", "").replace("Bearer ", "")
	payload = verify_jwt_token(token)
	if payload is None:
		raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
	else:
		con, cursor = get_db_connection()
		try:
			order_id = int(orderNumber[8:14])
			cursor.execute("""
				SELECT 
					`order`.total_price AS price,
				  	`order`.contact_name AS name,
				  	`order`.contact_email AS email,
				  	`order`.contact_phone AS phone,
				  	`orderItems`.trip_date AS date,
				  	`orderItems`.trip_time AS time,
				  	`attractions`.id AS attraction_id,
					`attractions`.name AS attraction_name,
					`attractions`.address AS attraction_address,
					`attractions`.images AS attraction_images
				FROM `order`
				JOIN `orderItems` ON `order`.id = `orderItems`.order_id
				JOIN `attractions` ON `orderItems`.attraction_id = `attractions`.id
            	WHERE `order`.id = %s
        	""", (order_id,))

			result = cursor.fetchone()

			if result:
				result["image"] = ast.literal_eval(result["attraction_images"])[0]
				data = Order(
					number = orderNumber,
					price = result["price"],
					trip = TripInfo(
						attraction =  BookingAttraction(
							id = result["attraction_id"],
							name = result["attraction_name"],
							address = result["attraction_address"],
							image = result["image"]
						),
						date = result["date"],
						time = result["time"]
					),
					contact = ContactInfo(
						name = result["name"],
						email = result["email"],
						phone = result["phone"]
					),
					status = StatusEnum.PAID
				)
				return GetOrderInfo(data=data)
			else:
				return GetOrderInfo(data=None)
		finally:
			con.close()
			print("Successfully returned the connection to connection pool.")