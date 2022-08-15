# flake8: noqa E501
from asyncio import get_event_loop
from enum import Enum
from pathlib import PurePath
from types import GeneratorType
from typing import IO, TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Set, Tuple, Union

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


class _PetApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_add_pet(self, body: m.Pet) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="POST", url="/pet", json=body)

    def _build_for_delete_pet(self, pet_id: int, api_key: str = None) -> Awaitable[None]:
        path_params = {"petId": str(pet_id)}

        headers = {}
        if api_key is not None:
            headers["api_key"] = str(api_key)

        return self.api_client.request(
            type_=None, method="DELETE", url="/pet/{petId}", path_params=path_params, headers=headers,
        )

    def _build_for_find_pets_by_status(self, status: List[str]) -> Awaitable[List[m.Pet]]:
        """
        Multiple status values can be provided with comma separated strings
        """
        query_params = {"status": str(status)}
        return self.api_client.request(type_=List[m.Pet], method="GET", url="/pet/findByStatus", params=query_params,)

    def _build_for_find_pets_by_tags(self, tags: List[str]) -> Awaitable[List[m.Pet]]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        query_params = {"tags": str(tags)}
        return self.api_client.request(type_=List[m.Pet], method="GET", url="/pet/findByTags", params=query_params,)

    def _build_for_get_pet_by_id(self, pet_id: int) -> Awaitable[m.Pet]:
        """
        Returns a single pet
        """
        path_params = {"petId": str(pet_id)}
        return self.api_client.request(type_=m.Pet, method="GET", url="/pet/{petId}", path_params=path_params,)

    def _build_for_update_pet(self, body: m.Pet) -> Awaitable[None]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=None, method="PUT", url="/pet", json=body)

    def _build_for_update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> Awaitable[None]:
        path_params = {"petId": str(pet_id)}

        files: Dict[str, IO[Any]] = {}  # noqa F841
        data: Dict[str, Any] = {}  # noqa F841
        if name is not None:
            data["name"] = name
        if status is not None:
            data["status"] = status

        return self.api_client.request(
            type_=None, method="POST", url="/pet/{petId}", path_params=path_params, data=data, files=files or None
        )

    def _build_for_upload_file(
        self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None
    ) -> Awaitable[m.ApiResponse]:
        path_params = {"petId": str(pet_id)}

        files: Dict[str, IO[Any]] = {}  # noqa F841
        data: Dict[str, Any] = {}  # noqa F841
        if additional_metadata is not None:
            data["additionalMetadata"] = additional_metadata
        if file is not None:
            files["file"] = file

        return self.api_client.request(
            type_=m.ApiResponse,
            method="POST",
            url="/pet/{petId}/uploadImage",
            path_params=path_params,
            data=data,
            files=files,
        )


class AsyncPetApi(_PetApi):
    async def add_pet(self, body: m.Pet) -> None:
        return await self._build_for_add_pet(body=body)

    async def delete_pet(self, pet_id: int, api_key: str = None) -> None:
        return await self._build_for_delete_pet(pet_id=pet_id, api_key=api_key)

    async def find_pets_by_status(self, status: List[str]) -> List[m.Pet]:
        """
        Multiple status values can be provided with comma separated strings
        """
        return await self._build_for_find_pets_by_status(status=status)

    async def find_pets_by_tags(self, tags: List[str]) -> List[m.Pet]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        return await self._build_for_find_pets_by_tags(tags=tags)

    async def get_pet_by_id(self, pet_id: int) -> m.Pet:
        """
        Returns a single pet
        """
        return await self._build_for_get_pet_by_id(pet_id=pet_id)

    async def update_pet(self, body: m.Pet) -> None:
        return await self._build_for_update_pet(body=body)

    async def update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> None:
        return await self._build_for_update_pet_with_form(pet_id=pet_id, name=name, status=status)

    async def upload_file(self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None) -> m.ApiResponse:
        return await self._build_for_upload_file(pet_id=pet_id, additional_metadata=additional_metadata, file=file)


class SyncPetApi(_PetApi):
    def add_pet(self, body: m.Pet) -> None:
        coroutine = self._build_for_add_pet(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def delete_pet(self, pet_id: int, api_key: str = None) -> None:
        coroutine = self._build_for_delete_pet(pet_id=pet_id, api_key=api_key)
        return get_event_loop().run_until_complete(coroutine)

    def find_pets_by_status(self, status: List[str]) -> List[m.Pet]:
        """
        Multiple status values can be provided with comma separated strings
        """
        coroutine = self._build_for_find_pets_by_status(status=status)
        return get_event_loop().run_until_complete(coroutine)

    def find_pets_by_tags(self, tags: List[str]) -> List[m.Pet]:
        """
        Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.
        """
        coroutine = self._build_for_find_pets_by_tags(tags=tags)
        return get_event_loop().run_until_complete(coroutine)

    def get_pet_by_id(self, pet_id: int) -> m.Pet:
        """
        Returns a single pet
        """
        coroutine = self._build_for_get_pet_by_id(pet_id=pet_id)
        return get_event_loop().run_until_complete(coroutine)

    def update_pet(self, body: m.Pet) -> None:
        coroutine = self._build_for_update_pet(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def update_pet_with_form(self, pet_id: int, name: str = None, status: str = None) -> None:
        coroutine = self._build_for_update_pet_with_form(pet_id=pet_id, name=name, status=status)
        return get_event_loop().run_until_complete(coroutine)

    def upload_file(self, pet_id: int, additional_metadata: str = None, file: IO[Any] = None) -> m.ApiResponse:
        coroutine = self._build_for_upload_file(pet_id=pet_id, additional_metadata=additional_metadata, file=file)
        return get_event_loop().run_until_complete(coroutine)
