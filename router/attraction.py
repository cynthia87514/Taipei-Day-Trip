from fastapi import *
from model.attraction import AttractionModel, Attractions, ErrorResponse, AttractionId

AttractionRouter = APIRouter(
    prefix = "/api",
    tags = ["Attraction"]
)

# 取得景點資料列表
@AttractionRouter.get(
    "/attractions",
    response_model = Attractions,
    responses = {
        500: {"model": ErrorResponse}
    }
)
async def attractionslist(
    page: int = Query(0), 
    keyword: str = Query(None)
):
    result = await AttractionModel.attractionslist(page, keyword)
    return result

# 根據景點編號取得景點資料
@AttractionRouter.get(
    "/attraction/{attractionId}",
    response_model = AttractionId,
    responses = {
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def attractiondata(
    attractionId: int = Path(...)
):
    result = await AttractionModel.attractiondata(attractionId)
    return result