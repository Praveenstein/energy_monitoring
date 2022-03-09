# -*- coding: utf-8 -*-
"""
SECURITY ROUTES MODULE
==================================

This Module consists of api routes for basic login, security and other requirements

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations

    *
"""

# Standard Imports
import logging
from datetime import timedelta

# External Imports
from fastapi import APIRouter, HTTPException, status, Depends

# User Imports
from ..database import USER_DB
from .router_dependencies import Token, authenticate_user, \
    create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

LOGGER = logging.getLogger(__name__)

ROUTER = APIRouter(
    prefix="/energy_meter/security",
    tags=["Security Routes"],
    responses={404: {"description": "Not found"}},)


@ROUTER.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    LOGIN API ROUTE
    =====================

    This api route is used to authenticate the user trying to login, create an access token to be used for later
    communications

    :param form_data: This is the html form data from which user information such as name, password are sent
    as part of the html body.

    :return: A dictionary consisting of access token and token type
    :rtype: dict
    """

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
