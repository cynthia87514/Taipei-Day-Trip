from fastapi import *
from pydantic import BaseModel
from typing import Optional
from enum import Enum, IntEnum
import jwt, ast
import dbconfig
from dotenv import dotenv_values
secrets = dotenv_values(".env")
# Secret key to sign JWT token
secret_key = secrets["JWT_SECRET_KEY"]

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
	
class OkResponse(BaseModel):
	ok: bool

class ErrorResponse(BaseModel):
	error: bool
	message: str

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

class BookingModel:
	async def booking(request: Request):
		token = request.headers.get("Authorization", "").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is None:
			raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
		else:
			con, cursor = dbconfig.get_db_connection()
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

	async def create_booking(request: Request, booking_data):
		token = request.headers.get("Authorization", "").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is None:
			raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
		else:
			con, cursor = dbconfig.get_db_connection()
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

	async def delete_booking(request: Request):
		token = request.headers.get("Authorization", "").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is None:
			raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
		else:
			con, cursor = dbconfig.get_db_connection()
			try:
				user_id = payload.get("sub")
				cursor.execute("DELETE FROM `booking` WHERE user_id = %s;", (user_id,))
				con.commit()
				return OkResponse(ok=True)
			finally:
				con.close()
				print("Successfully returned the connection to connection pool.")