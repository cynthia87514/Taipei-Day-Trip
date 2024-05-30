from fastapi import *
from fastapi.responses import FileResponse
from fastapi_pagination import paginate
from pydantic import BaseModel
import mysql.connector
from mysql.connector import pooling

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
		cursor = con.cursor()
		return con, cursor
	else:
		print("Failed to connect to MySQL database.")

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

@app.get("/api/attractions")
async def attractionslist(request: Request, response: Response, page: int = Query(0), keyword: str = Query(None)):
	con, cursor = get_db_connection()
	try:
		offset = page * 12
		limit = 12
		if keyword == None:
			cursor.execute("""
				SELECT `attractions`.*, `categorys`.name, `mrts`.name
				FROM `attractions`
				LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
				LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
				LIMIT %s, %s
				""", (offset, limit))
			attractions_data = cursor.fetchall()
			datalst = []
			for attraction_data in attractions_data:
				data = {
				"id": attraction_data[0],
				"name": attraction_data[1],
				"category": attraction_data[11],
				# "category_id": attraction_data[2],
				"description": attraction_data[3],
				"address": attraction_data[4],
				"transport": attraction_data[5],
				"mrt": attraction_data[12],
				# "mrt_id": attraction_data[6],
				"lat": attraction_data[7],
				"lng": attraction_data[8],
				"images": eval(attraction_data[9])
				}
				datalst.append(data)
			
			cursor.execute("SELECT COUNT(*) FROM `attractions`")
			total = cursor.fetchone()[0]
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
				SELECT `attractions`.*, `categorys`.name, `mrts`.name
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
				"id": attraction_data[0],
				"name": attraction_data[1],
				"category": attraction_data[11],
				# "category_id": attraction_data[2],
				"description": attraction_data[3],
				"address": attraction_data[4],
				"transport": attraction_data[5],
				"mrt": attraction_data[12],
				# "mrt_id": attraction_data[6],
				"lat": attraction_data[7],
				"lng": attraction_data[8],
				"images": eval(attraction_data[9])
				}
				datalst.append(data)

			cursor.execute("""
				SELECT COUNT(*) FROM `attractions`
				LEFT JOIN `categorys` ON `attractions`.category_id = `categorys`.id
				LEFT JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
				WHERE `mrts`.name = %s OR `attractions`.name LIKE %s
				""", (keyword, '%' + keyword + '%'))
			total = cursor.fetchone()[0]
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
				"id": attraction_data[0],
				"name": attraction_data[1],
				"category": category_data[0],
				"description": attraction_data[2],
				"address": attraction_data[3],
				"transport": attraction_data[4],
				"mrt": mrt_data[0],
				"lat": attraction_data[5],
				"lng": attraction_data[6],
				"images": eval(attraction_data[7])
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

@app.get("/api/mrts")
async def mrtslist(request: Request, response: Response):
	con, cursor = get_db_connection()
	try:
		cursor.execute("""
			SELECT `mrts`.name AS mrt_name,
			COUNT(*) AS mrt_num
			FROM attractions
			JOIN `mrts` ON `attractions`.mrt_id = `mrts`.id
			GROUP BY `attractions`.mrt_id, `mrts`.name
			ORDER BY mrt_num DESC
			""")
		mrt_data = cursor.fetchall()
		data = []
		for i in mrt_data:
			data.append(i[0])
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