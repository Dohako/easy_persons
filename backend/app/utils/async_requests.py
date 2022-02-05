import asyncio
import httpx
from ..utils import schemas
import json

FIRST_URL = "http://dohako.com:8001/"
SECOND_URL = "http://dohako.com:8002/"
THIRD_URL = "http://dohako.com:8003/"
BASE_URLS = (FIRST_URL, SECOND_URL, THIRD_URL)


def get_first_missing_number(sequence, start=1):
    uniques = set()
    maxitem = start - 1
    for e in sequence:
        if e >= start:
            uniques.add(e)
            if e > maxitem:
                maxitem = e
    return next(x for x in range(start, maxitem + 2) if x not in uniques)


def get_lowest_base(items) -> int:
    less_values_list = 0
    base_list_length = len(items[less_values_list])
    for i, values_list in enumerate(items):
        if len(values_list) < base_list_length:
            less_values_list = i
    return less_values_list


def make_single_list(list_of_list_of_ids) -> list:
    result = []
    for list_of_ids in list_of_list_of_ids:
        for id in list_of_ids:
            result.append(id)
    return result


async def get_first_missing_global_id():
    # change to json loads
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
    print(result_list)
    first_missing_number = get_first_missing_number(result_list)
    return lowest_base, first_missing_number


async def request_func(
    client,
    url: str,
    request_type: str,
    data: schemas.User | schemas.Person | None = None,
    person_id: str | None = None,
):
    if request_type == "put":
        response = await client.put(url, json=data.__dict__)
    elif request_type == "post":
        response = await client.post(url, json=data.__dict__)
    elif request_type == "delete":
        print(url)
        response = await client.delete(url)
    else:
        response = await client.get(url)
    return json.loads(response.text)


async def send_post_func(client, url, data):
    response = await client.post(url, json=data.__dict__)
    return response.text


async def get_global_id_lists(client, url):
    response = await client.get(url)
    return response.text


async def set_async_id_retrieve():
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
):

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
        elif request_type == "post":
            lowest_base, next_global_id = await get_first_missing_global_id()
            data.global_id = next_global_id
            tasks = [
                request_func(
                    client=client,
                    url=BASE_URLS[lowest_base] + "data",
                    request_type=request_type,
                    data=data,
                ),
            ]

        result = await asyncio.gather(return_exceptions="False", *tasks)
        # print(result)
    return result
