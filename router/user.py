from fastapi import *
from model.user import UserModel, OkResponse, ErrorResponse, SignUpInfo, UserData, Token, SignInInfo

UserRouter = APIRouter(
    prefix = "/api",
    tags = ["User"]
)

# 註冊一個新的會員
@UserRouter.post(
    "/user",
    response_model = OkResponse,
    responses = {
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def signup(
    user_data: SignUpInfo = Body(...)
):
    result = await UserModel.signup(user_data)
    return result

# 取得當前登入的會員資訊
@UserRouter.get(
    "/user/auth",
    response_model = UserData
)
async def user_data(request: Request):
    result = await UserModel.user_data(request)
    return result

# 登入會員帳戶
@UserRouter.put(
    "/user/auth",
    response_model = Token,
    responses = {
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def signin(
    user_data: SignInInfo = Body(...)
):
    result = await UserModel.signin(user_data)
    return result