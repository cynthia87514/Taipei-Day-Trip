from fastapi import *
from model.booking import BookingModel, BookingPage, ErrorResponse, OkResponse, CreateBooking

BookingRouter = APIRouter(
    prefix = "/api",
    tags = ["Booking"]
)

# 取得尚未確認下單的預定行程
@BookingRouter.get(
    "/booking",
    response_model = BookingPage,
    responses = {
        403: {"model": ErrorResponse}
    }
)
async def booking(request: Request):
    result = await BookingModel.booking(request)
    return result

# 建立新的預定行程
@BookingRouter.post(
    "/booking",
    response_model = OkResponse,
    responses = {
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_booking(
    request: Request,
    booking_data: CreateBooking = Body(...)
):
    result = await BookingModel.create_booking(request, booking_data)
    return result

# 刪除目前的預定行程
@BookingRouter.delete(
    "/booking",
    response_model = OkResponse,
    responses = {
        403: {"model": ErrorResponse}
    }
)
async def delete_booking(request: Request):
    result = await BookingModel.delete_booking(request)
    return result