from fastapi.security import OAuth2PasswordBearer


class Keys:
    JWT_SECRET = "054mc9289fvmiiwnvnh5"
    OAUTH_URL = OAuth2PasswordBearer(tokenUrl="token")
