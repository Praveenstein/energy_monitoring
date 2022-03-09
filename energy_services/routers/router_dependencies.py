# -*- coding: utf-8 -*-
"""
ROUTER DEPENDENCIES MODULE
==================================

This Module consists of variables and functions that are required for the functioning of various routers
defined in this subpackage "router"

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations

    *
"""

# Standard Imports
import logging
from typing import Optional
from datetime import datetime, timedelta

# External Imports
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# User Imports
from ..database import USER_DB

LOGGER = logging.getLogger(__name__)

# To get a string like this run:
# openssl rand -hex 32

# This is the secret key used for signing a token sent to the user for authentication
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/energy_meter/security/token")


class Token(BaseModel):
    """
    RESPONSE CLASS FOR TOKEN REQUEST
    ======================================

    This is a class (pydantic class) to represent the response body when a client request a token for an authentication
    token. so this works with the api route "/token"
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    TOKEN DATA FOR CURRENT USER
    ======================================

    This is a class (pydantic class) to represent the token data for a current user
    """

    username: Optional[str] = None


class User(BaseModel):
    """
    PYDANTIC MODEL FOR USER
    ======================================

    This is a class (pydantic class) to represent a user, for authentication purposes.
    """

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """
    PYDANTIC MODEL FOR ACTIVE USER
    ======================================

    This is a class (pydantic class) to represent a user currently active which extends USER class, for authentication
    purposes.
    """

    hashed_password: str


def verify_password(unhashed_password: str, hashed_password: str):
    """
    VERIFY PASSWORDS
    ======================

    This function is used to verify is the password from the client (un-hashed) is same as the hashed password
    stored in the database.

    :param unhashed_password: This is the un-hashed password from the client as a plain text
    :param hashed_password: The hashed password of the user stored in the database

    :return: Boolean stating whether the password matched or not
    :rtype: bool
    """

    return PASSWORD_CONTEXT.verify(unhashed_password, hashed_password)


def get_password_hash(password: str):
    """
    HASH A PASSWORD
    ==================

    This function is used to hash a given plain (un-hashed) password

    :param password: The plain un hashed password from the user

    :return: The hashed password
    :rtype: str
    """

    return PASSWORD_CONTEXT.hash(password)


def get_user(database: dict, username: str):
    """
    GET USER
    ===========

    This function is used to return a Pydantic model of (active - disable = False) user if the user is in the database

    :param database: The database consisting of all the users details (As of now it's just a dictionary with one user)
    :param username: The user name who wants to log in

    :return: Return a pydantic class of user
    :rtype: UserInDB
    """

    if username in database:
        user_dict = database[username]
        return UserInDB(**user_dict)


def authenticate_user(database: dict, username: str, password: str):
    """
    AUTHENTICATE USER
    ==================

    This function is used to authenticate a user by verifying if the password (un-hashed) sent by the client
    is same as the hashed password stored in the database.

    :param database: The database class thorough which we can access the database ( currently it is just a dictionary)
    :param username: The username of the user who wants to log in
    :param password: The plain un-hashed password of the user

    :return: Either "False" to indicate the user is not authenticated, or a pydantic user class model representing
    the authenticated user.
    :rtype: Union[UserInDB, bool]
    """

    user = get_user(database, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    CREATE ACCESS TOKEN
    ==========================

    This function is used to create an new access token for the user who wants to log in

    :param data: This data will be part of the access jwt token (specifically a field called "sub" which stores the
    username - yes the token will have username details, expiry time etc, for more info see fastapi security page)
    :param expires_delta: The time of expiry for the token

    :return: The JSON Web Token for the current user who wants to log in
    :rtype: str
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    """
    GET CURRENT USER
    ==================

    This function is used to decode the jwt token received from the client, check for authentication and return
    a pydantic model of the active user.

    :param token: The jwt token sent by the client

    :return: The pydantic model of the current user
    :rtype: UserInDB
    """

    # Creating an Http exception class to be sent if cannot authorize the user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decoding the jwt token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # This decoded payload will be a dictionary with various key value pair, one of which is key "sub"
        # Which has the username in it
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        # Creating a pydantic class for representing the token data (which is just a username in this case)
        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    # Creating pydantic user model
    user = get_user(USER_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    GET CURRENT ACTIVE USER
    =============================

    This function is used to get the current active user by checking if the user is disabled or not.

    :param current_user: The current user (who needs to be checked if active or not)

    :return: The current user if he is active else raises an http exception
    :rtype: User
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
