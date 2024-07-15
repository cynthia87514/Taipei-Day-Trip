from fastapi import *
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum, IntEnum
from datetime import datetime
import dbconfig
import jwt, ast
import tappay
from dotenv import dotenv_values
secrets = dotenv_values(".env")
# Secret key to sign JWT token
secret_key = secrets["JWT_SECRET_KEY"]

class BookingAttraction(BaseModel):
	id: int
	name: str
	address: str
	image: str

class TimeEnum(str, Enum):
	morning = "morning"
	afternoon = "afternoon"

class PriceEnum(IntEnum):
	morning = 2000
	afternoon = 2500

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
	
class OrderModel:
	async def create_order(request: Request, create_order):
		token = request.headers.get("Authorization", "").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is None:
			raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
		else:
			con, cursor = dbconfig.get_db_connection()
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

	async def get_order_data(request: Request, orderNumber: str):
		token = request.headers.get("Authorization", "").replace("Bearer ", "")
		payload = verify_jwt_token(token)
		if payload is None:
			raise HTTPException(status_code=403, detail={"error": True, "message": "未登入系統，拒絕存取"})
		else:
			con, cursor = dbconfig.get_db_connection()
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