# flake8: noqa E501
from asyncio import get_event_loop
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Set, Tuple, Union

from pydantic.json import ENCODERS_BY_TYPE
from pydantic.main import BaseModel

from example.client import models as m

SetIntStr = Set[Union[int, str]]
DictIntStrAny = Dict[Union[int, str], Any]


def generate_encoders_by_class_tuples(type_encoder_map: Dict[Any, Callable]) -> Dict[Callable, Tuple]:
    encoders_by_classes: Dict[Callable, List] = {}
    for type_, encoder in type_encoder_map.items():
        encoders_by_classes.setdefault(encoder, []).append(type_)
    encoders_by_class_tuples: Dict[Callable, Tuple] = {}
    for encoder, classes in encoders_by_classes.items():
        encoders_by_class_tuples[encoder] = tuple(classes)
    return encoders_by_class_tuples


encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)


def jsonable_encoder(
    obj: Any,
    include: Union[SetIntStr, DictIntStrAny] = None,
    exclude=None,
    by_alias: bool = True,
    skip_defaults: bool = None,
    exclude_unset: bool = False,
    include_none: bool = True,
    custom_encoder=None,
    sqlalchemy_safe: bool = True,
) -> Any:
    if exclude is None:
        exclude = set()
    if custom_encoder is None:
        custom_encoder = {}
    if include is not None and not isinstance(include, set):
        include = set(include)
    if exclude is not None and not isinstance(exclude, set):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.Config, "json_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            include=include, exclude=exclude, by_alias=by_alias, exclude_unset=bool(exclude_unset or skip_defaults),
        )

        return jsonable_encoder(
            obj_dict, include_none=include_none, custom_encoder=encoder, sqlalchemy_safe=sqlalchemy_safe,
        )
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if (
                (not sqlalchemy_safe or (not isinstance(key, str)) or (not key.startswith("_sa")))
                and (value is not None or include_none)
                and ((include and key in include) or key not in exclude)
            ):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    include_none=include_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list

    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            for encoder_type, encoder in custom_encoder.items():
                if isinstance(obj, encoder_type):
                    return encoder(obj)

    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)

    errors: List[Exception] = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return jsonable_encoder(
        data,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        include_none=include_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )


if TYPE_CHECKING:
    from example.client.api_client import ApiClient


class _UserApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_create_user(self, body: m.User) -> Awaitable[None]:
        """
        This can only be done by the logged in user.
        """
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user", json=body)

    def _build_for_create_users_with_array_input(self, body: List[m.User]) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user/createWithArray", json=body)

    def _build_for_create_users_with_list_input(self, body: List[m.User]) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/user/createWithList", json=body)

    def _build_for_delete_user(self, username: str) -> Awaitable[None]:
        """
        This can only be done by the logged in user.
        """
        path_params = {"username": str(username)}

        return self.api_client.request(type_=None, method="DELETE", url="/user/{username}", path_params=path_params,)

    def _build_for_get_user_by_name(self, username: str) -> Awaitable[m.User]:
        path_params = {"username": str(username)}

        return self.api_client.request(type_=m.User, method="GET", url="/user/{username}", path_params=path_params,)

    def _build_for_login_user(self, username: str, password: str) -> Awaitable[str]:
        query_params = {"username": str(username), "password": str(password)}

        return self.api_client.request(type_=str, method="GET", url="/user/login", params=query_params,)

    def _build_for_logout_user(self,) -> Awaitable[None]:
        return self.api_client.request(type_=None, method="GET", url="/user/logout",)

    def _build_for_update_user(self, username: str, body: m.User) -> Awaitable[None]:
        """
        This can only be done by the logged in user.
        """
        path_params = {"username": str(username)}

        body = jsonable_encoder(body)

        return self.api_client.request(
            type_=None, method="PUT", url="/user/{username}", path_params=path_params, json=body
        )


class AsyncUserApi(_UserApi):
    async def create_user(self, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_create_user(body=body)

    async def create_users_with_array_input(self, body: List[m.User]) -> None:
        return await self._build_for_create_users_with_array_input(body=body)

    async def create_users_with_list_input(self, body: List[m.User]) -> None:
        return await self._build_for_create_users_with_list_input(body=body)

    async def delete_user(self, username: str) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_delete_user(username=username)

    async def get_user_by_name(self, username: str) -> m.User:
        return await self._build_for_get_user_by_name(username=username)

    async def login_user(self, username: str, password: str) -> str:
        return await self._build_for_login_user(username=username, password=password)

    async def logout_user(
        self,
    ) -> None:
        return await self._build_for_logout_user()

    async def update_user(self, username: str, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        return await self._build_for_update_user(username=username, body=body)


class SyncUserApi(_UserApi):
    def create_user(self, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self._build_for_create_user(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def create_users_with_array_input(self, body: List[m.User]) -> None:
        coroutine = self._build_for_create_users_with_array_input(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def create_users_with_list_input(self, body: List[m.User]) -> None:
        coroutine = self._build_for_create_users_with_list_input(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def delete_user(self, username: str) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self._build_for_delete_user(username=username)
        return get_event_loop().run_until_complete(coroutine)

    def get_user_by_name(self, username: str) -> m.User:
        coroutine = self._build_for_get_user_by_name(username=username)
        return get_event_loop().run_until_complete(coroutine)

    def login_user(self, username: str, password: str) -> str:
        coroutine = self._build_for_login_user(username=username, password=password)
        return get_event_loop().run_until_complete(coroutine)

    def logout_user(
        self,
    ) -> None:
        coroutine = self._build_for_logout_user()
        return get_event_loop().run_until_complete(coroutine)

    def update_user(self, username: str, body: m.User) -> None:
        """
        This can only be done by the logged in user.
        """
        coroutine = self._build_for_update_user(username=username, body=body)
        return get_event_loop().run_until_complete(coroutine)
