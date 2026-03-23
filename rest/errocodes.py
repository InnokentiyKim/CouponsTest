from rest_framework.exceptions import APIException
from rest_framework import status


class GeneralException(APIException):
    """Base exception class for general API errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal Server Error."
    code: str = "internal_server_error"


class ItemNotFoundException(GeneralException):
    """Error when a requested item is not found in the database."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Requested item not found."
    code = "item_not_found"


class ItemAlreadyExistsException(GeneralException):
    """Error when trying to create an item that already exists in the database."""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Item with given attributes already exists."
    code = "item_already_exists"


class InvalidItemsDataException(GeneralException):
    """Error when provided items data is invalid, such as missing required fields or incorrect formats."""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid items data provided."
    code = "invalid_items_data"
