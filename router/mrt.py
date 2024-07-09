from fastapi import *
from model.mrt import MrtModel, MrtList, ErrorResponse

MrtRouter = APIRouter(
    prefix = "/api",
    tags = ["MRT Station"]
)

# 取得捷運站名稱列表
@MrtRouter.get(
    "/mrts",
    response_model = MrtList,
    responses = {
        500: {"model": ErrorResponse}
    }
)
async def mrtslist():
    result = await MrtModel.mrtslist()
    return result