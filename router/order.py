from fastapi import *
from model.order import OrderModel, OrderData, ErrorResponse, GetOrderInfo, CreateOrder

OrderRouter = APIRouter(
    prefix = "/api",
    tags = ["Order"]
)

# 建立新的訂單，並完成付款程序
@OrderRouter.post(
    "/orders",
    response_model = OrderData,
    responses = {
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_order(
    request: Request,
    create_order: CreateOrder = Body(...)
):
    result = await OrderModel.create_order(request, create_order)
    return result

# 根據訂單編號取得訂單資訊
@OrderRouter.get(
    "/order/{orderNumber}",
    response_model = GetOrderInfo,
    responses = {
        403: {"model": ErrorResponse}
    }
)
async def get_order_data(
    request: Request,
    orderNumber: str = Path(...)
):
    result = await OrderModel.get_order_data(request, orderNumber)
    return result