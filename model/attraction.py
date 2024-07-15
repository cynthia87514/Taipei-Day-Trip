from fastapi import *
from pydantic import BaseModel
from typing import Optional, List
import dbconfig
import ast

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

class ErrorResponse(BaseModel):
	error: bool
	message: str

class AttractionModel:
    async def attractionslist(page: int, keyword: str):
        con, cursor = dbconfig.get_db_connection()
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

    async def attractiondata(attractionId: int):
        con, cursor = dbconfig.get_db_connection()
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