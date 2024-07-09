from fastapi import *
from pydantic import BaseModel
from typing import List
import dbconfig

class MrtList(BaseModel):
	data: List[str]
	
class ErrorResponse(BaseModel):
	error: bool
	message: str

class MrtModel:
	async def mrtslist():
		con, cursor = dbconfig.get_db_connection()
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