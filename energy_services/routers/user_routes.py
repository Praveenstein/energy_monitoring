# -*- coding: utf-8 -*-
"""
USER ROUTES MODULE
==================================

This Module consists of api routes for accessing user information.

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations

    *
"""

# Standard Imports
import logging

# External Imports
from fastapi import APIRouter, Depends

# User Imports
from .router_dependencies import User, get_current_active_user

LOGGER = logging.getLogger(__name__)

# Depends(get_current_active_user)
ROUTER = APIRouter(
    prefix="/energy_meter/users",
    tags=["User Routes"],
    dependencies=[],
    responses={404: {"description": "Not found"}},)


@ROUTER.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    READ CURRENT USER DETAILS
    =============================

    This api route reads the current user details and sends

    :param current_user: The current user which depends on the get current active user, which
    gets the current user details (username) from the access token sent during the login time.

    :return: The current user as pydantic model
    :rtype: dict
    """
    return current_user


@ROUTER.get("/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """
    READ CURRENT USERS ID AND NAME
    ==================================

    This api route reads the current user and returns just the id and his name

    :param current_user: The current user which depends on the get current active user, which
    gets the current user details (username) from the access token sent during the login time.

    :return: Dictionary consisting of item id and owner
    :rtype: list
    """
    return [{"item_id": "Foo", "owner": current_user.username}]
