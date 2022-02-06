import asyncio
import httpx
import json

from ..utils import schemas
from ..utils.d_utils import get_lowest_base, get_first_missing_number, make_single_list

FIRST_URL = "http://dohako.com:8001/"
SECOND_URL = "http://dohako.com:8002/"
THIRD_URL = "http://dohako.com:8003/"
BASE_URLS = (FIRST_URL, SECOND_URL, THIRD_URL)


async def get_first_missing_global_id():
    """
    here I'm geting something like
    ['", 1, 4, 7, 10, 13, 16"', '", 3, 6, 9, 12, 15, 18"', '", 2, 5, 8, 11, 14, 17"']
    and want to get
    [1, 4, 7, 10, 13, 16, 3, 6, 9, 12, 15, 18, 2, 5, 8, 11, 14, 17]
    and from it I need to find Global ID that is missing to fill the db with new
    GlobalID

    This way may be too rude, need to think it through
    """
    # change to json loads ?
    id_from_bases = await set_async_id_retrieve()
    new_id_list = []
    for id_list in id_from_bases:
        new_list = []
        id_list = id_list.replace('"', "")
        id_list = id_list.split(", ")
        for id in id_list:
            if id.isdecimal():
                new_list.append(int(id))
        new_id_list.append(new_list)

    lowest_base = get_lowest_base(new_id_list)
    result_list = make_single_list(new_id_list)
    first_missing_number = get_first_missing_number(result_list)
    return lowest_base, first_missing_number


async def request_func(
    client,
    url: str,
    request_type: str,
    data: schemas.User | schemas.Person | None = None,
    person_id: str | None = None,
    username: str | None = None,
):
    """
    this func is like a router for requests in asyncio way Mb it is not as it is suppose to be
    will look closely on this part latter on
    """
    if request_type == "put":
        response = await client.put(url, json=data.__dict__)
    elif request_type == "post" or request_type == "register":
        response = await client.post(url, json=data.__dict__)
    elif request_type == "delete":
        response = await client.delete(url)
    elif request_type == "auth":
        response = await client.post(url, json={"username": username})
    else:
        response = await client.get(url)
    return json.loads(response.text)


async def get_global_id_lists(client, url):
    """
    async getting id lists from working bases
    """
    response = await client.get(url)
    return response.text


async def set_async_id_retrieve():
    """
    start async gather info for Global ID with 2 secs timeout
    """
    async with httpx.AsyncClient(timeout=2) as client:
        tasks = [
            get_global_id_lists(client=client, url=url + "global_id")
            for url in BASE_URLS
        ]
        result = await asyncio.gather(return_exceptions="False", *tasks)
    return result


async def set_async_request(
    request_type: str,
    data: schemas.User | schemas.Person | None = None,
    person_id: str | None = None,
    username: str | None = None,
):
    """
    start async gather all info with 2 secs timeout
    """

    async with httpx.AsyncClient(timeout=2) as client:
        request_type = request_type.lower()
        if request_type == "get":
            tasks = [
                request_func(client=client, url=url + "data", request_type=request_type)
                for url in BASE_URLS
            ]
        elif request_type == "delete":
            tasks = [
                request_func(
                    client=client,
                    url=url + f"data/{person_id}",
                    request_type=request_type,
                )
                for url in BASE_URLS
            ]
        elif request_type == "auth":
            tasks = [
                request_func(
                    client=client,
                    url=url + f"get_by_user_id",
                    request_type="auth",
                    username=username,
                )
                for url in BASE_URLS
            ]
        elif request_type == "put":
            tasks = [
                request_func(
                    client=client,
                    url=url + "data",
                    request_type=request_type,
                    data=data,
                )
                for url in BASE_URLS
            ]
        elif request_type == "post" or request_type == "register":
            if request_type == "post":
                add_to_uri = "data"
            else:
                add_to_uri = "register"
            lowest_base, next_global_id = await get_first_missing_global_id()
            data.global_id = next_global_id
            tasks = [
                request_func(
                    client=client,
                    url=BASE_URLS[lowest_base] + add_to_uri,
                    request_type=request_type,
                    data=data,
                ),
            ]

        result = await asyncio.gather(return_exceptions="False", *tasks)
    return result
