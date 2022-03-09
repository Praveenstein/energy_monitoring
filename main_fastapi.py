# -*- coding: utf-8 -*-
"""

Main Module
========================

Main Module for doing basic operation with database

This script requires the following modules be installed in the python environment

    * logging - to perform logging operations

This script contains the following function

    * main - main function to call appropriate functions to perform the read operation to get the top customers

"""

# Standard imports
import logging
from datetime import datetime, timedelta
from typing import Optional

# External Imports
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.engine.base import Engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# User Imports
import energy_services.utils as helper
import energy_services.database as db

LOGGER = logging.getLogger(__name__)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

USER_DB = {
    "cmti": {
        "username": "cmti",
        "full_name": "CMTI SMDDC",
        "email": "cmti@cmti.res.in",
        "hashed_password": "$2b$12$RCuPSrRoK15qgq14ShruqeRg0i2s4zuw2UHX80DBqewdqICHtdw2u",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

APP = FastAPI()
DATABASE_ENGINE = None

origins = ["*"]

APP.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(database, username: str):
    if username in database:
        user_dict = database[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(USER_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@APP.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(USER_DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@APP.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@APP.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


def get_engine():
    """

    GET ENGINE
    ============

    This function is used as the generator function that is required (to send the engine) for a parameter(engine)
    inside the read_root api.

    :return: SqlAlchemy Engine
    :rtype: Engine

    """
    try:
        yield DATABASE_ENGINE
    except Exception as error:
        LOGGER.error(error)


@APP.get("/energy_meter/current_update")
async def read_all_current_values(engine: Engine = Depends(get_engine)):
    """

    GET CURRENT PARAMETERS DATA
    ===============================

    This api is used to query the latest data from the database

    :param engine: The SqlAlchemy engine used to connect to the database
    :param current_user: We need to always get the current user so that we could always authenticate the users (even if
    we're not going to use the user or his/her details.

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.LATEST_ALL_PARAMETER_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.current_parameters_to_dictionary(database_records)
    return data


@APP.get("/energy_meter/total_energy_today")
async def read_total_energy(engine: Engine = Depends(get_engine),
                            current_user: User = Depends(get_current_active_user)):
    """

    GET TOTAL ENERGY FOR TODAY
    ===============================

    This api is used to query the total energy consumed today (from today morning until now)

    :param engine: The SqlAlchemy engine used to connect to the database
    :param current_user: We need to always get the current user so that we could always authenticate the users (even if
    we're not going to use the user or his/her details.

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.TOTAL_ENERGY_CONSUMED_TODAY_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.total_energy_to_dictionary(database_records)
    return data


@APP.get("/energy_meter/read_parameter_multiple")
async def read_parameter_multiple(parameter: str, date_1: str, date_2: str, engine: Engine = Depends(get_engine),
                                  current_user: User = Depends(get_current_active_user)):
    """

    GET PARAMETER VALUES FOR GIVEN DATE
    =======================================

    This api is used to query the all the values of a given parameter for a given date(s). Which will be used
    for displaying a graph to compare the trend for the given 5 days.

    :param date_1: Date 1 for which all parameter values need to be sent
    :param date_2: Date 2 for which all parameter values need to be sent
    :param parameter: The parameter that needs to be read from the database ( such as power, energy etc)
    :param engine: The SqlAlchemy engine used to connect to the database
    :param current_user: We need to always get the current user so that we could always authenticate the users (even if
    we're not going to use the user or his/her details.

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """

    # TODO: Change the parameter date_1, date_2 to something of array type

    dates = [date_1, date_2]
    statements = [db.statement_for_date_query(parameter, date) for date in dates]
    records = db.read_rows_multiple(engine, statements)

    data = db.date_wise_parameters_to_dictionary(dates, records)
    return data


if __name__ == "__main__":
    # Getting the path for logging config using arparse
    log_config_file = helper.ARGUMENTS.logfile

    # Configuring logging
    helper.configure_logging(log_config_file)

    LOGGER.info("Creating Engine")

    # Getting a new engine
    DATABASE_ENGINE = db.create_new_engine(helper.ARGUMENTS.dialect, helper.ARGUMENTS.driver,
                                           helper.ARGUMENTS.user, helper.ARGUMENTS.password,
                                           helper.ARGUMENTS.host, helper.ARGUMENTS.database)

    uvicorn.run(APP, host="172.18.7.27", port=8000)
