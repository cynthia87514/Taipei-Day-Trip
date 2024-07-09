from fastapi import *
from pydantic import BaseModel, EmailStr
from typing import Optional
import dbconfig
import jwt
from datetime import datetime, timedelta
from dotenv import dotenv_values
secrets = dotenv_values(".env")

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
	
class OkResponse(BaseModel):
	ok: bool

class ErrorResponse(BaseModel):
	error: bool
	message: str

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

class UserModel:
    async def signup(user_data):
        con, cursor = dbconfig.get_db_connection()
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
	
    async def user_data(request: Request):
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
		
    async def signin(user_data):
        con, cursor = dbconfig.get_db_connection()
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