from passlib.context import CryptContext
import secrets
from models import User
from pymongo import MongoClient
from helpers import parse_json
from fastapi import HTTPException, Depends
from keys import Keys

SECRET_KEY = "98cee09029df607732e82bf5b1851772f221c6b67864abc123d4fc9959ada30b"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import jwt

# Database Connection
myclient = MongoClient(
    "mongodb+srv://zjohnson:Coopalex0912@cluster0.2amvb.mongodb.net/mtptcmiyamoto?retryWrites=true&w=majority"
)


# database
db = myclient["mtptcmiyamoto"]

# Assessment collection
collection = db["users"]


def generate_api_key():
    return secrets.token_urlsafe(25)


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    organization: str,
    admin: bool = False,
):
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=get_password_hash(password),
        organization=organization,
        api_key=generate_api_key(),
        admin=admin,
    )
    collection.insert_one(new_user.dict())
    return new_user


async def get_user_by_api_key(auth):
    user = collection.find_one({"api_key": auth})

    if user and user["active"]:
        json_user = parse_json(user)
        return User(**json_user)
    else:
        raise HTTPException(status_code=404, detail="Invalid API Key")


async def admin_route(auth):
    user = collection.find_one({"api_key": auth})

    if user:
        json_user = parse_json(user)
        parsed_user = User(**json_user)
        if parsed_user:
            if parsed_user.admin:
                return parsed_user
            else:
                raise HTTPException(
                    status_code=404, detail="You do not have permission to do this."
                )

    else:
        raise HTTPException(status_code=404, detail="Invalid API Key")


async def authenticate_user(email, password):
    user = collection.find_one({"email": email})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return User(**user)


def get_current_user(token: str = Depends(Keys.OAUTH_URL)):
    try:
        payload = jwt.decode(token, Keys.JWT_SECRET, algorithms=["HS256"])
        user = collection.find_one({"email": payload.get("email")})
        return User(**user)
    except:
        raise HTTPException(status_code=404, detail="Invalid API Key")
