from imports import *

regions = {
    "Москва": [55.7521, 37.6241],  # [lat, long]
    "Санкт-Петербург": [59.931055, 30.360984],
    "Казань": [55.7887, 49.1221],
    "Екатеринбург": [56.8519, 60.6122],
    "Новосибирск": [55.0415, 82.9346],
    "Хабаровск": [48.4827, 135.084],
    "Краснодар": [45.0448, 38.976],
    "Омск": [54.9924, 73.3686],
    "Красноярск": [56.0184, 92.8672],
    "Уфа": [54.7431, 55.9678]
}
needed_cookies = {
    "__store": "stores",
    "__region": "regions",
    "__pricemargin": "pricemarginCoeff",
    "__cpns": "couponsGeo",
    "__dst": "dest"
}


def get_cookies(region):
    #  print("get_cookies", region)
    alt, long = regions[region]
    manager = urllib3.PoolManager()
    url = "https://www.wildberries.ru/geo/saveprefereduserloc"
    payload2 = urlencode({
        "address": region,
        "longitude": str(long),
        "latitude": str(alt)
    })
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Host': 'www.wildberries.ru'
    }
    response = manager.request("POST", url, headers=headers, body=payload2)
    cookies = response.headers["Set-Cookie"].replace("httponly", '').replace("path=/", '').replace(", ", '').replace("HttpOnly", '').replace('Path=/', '').split("; ")
    res = []
    for n, cookie in enumerate(cookies):
        for nc in needed_cookies:
            if nc in cookie:
                if nc == "__pricemargin":
                    cookie_value = cookie_value = cookie.split("=")[1][:-2]
                else:
                    cookie_value = cookie.split("=")[1]
                cookie_value = cookie_value.replace("_", ",")
                res.append(f"{needed_cookies[nc]}={cookie_value}")
                break
    res = '&'.join(res)
    return res


def get_query(keyphrase):
    #  print("get_query", keyphrase)
    manager = urllib3.PoolManager()
    url = f"https://wbxsearch.wildberries.ru/exactmatch/v2/common?query={urllib.parse.quote(keyphrase)}"
    request_headers = {
        "Host": "wbxsearch.wildberries.ru",
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    response = manager.request("GET", url, headers=request_headers).data.decode("utf-8")[:-1]
    print("response:", response)
    response = eval(response)
    return response["query"], response["shardKey"]


def get_filters(cookies, query, shard_key):
    #  print("get_filters", cookies, query, shard_key)
    filters = {
        "xsubject": [],
        "fkind": [],
        "fcolor": [],
        "fbrand": []
    }
    filters_keys = list(filters.keys())
    url = f"https://wbxcatalog-ru.wildberries.ru/{shard_key}/filters?filters=xsubject;fkind;fcolor;fbrand&{cookies}&{query}&locale=ru&lang=ru&curr=rub&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0"
    manager = urllib3.PoolManager()
    request_headers = {
        "Host": "wbxsearch.wildberries.ru",
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    response = eval(manager.request("GET", url, headers=request_headers).data.decode("utf-8"))
    for i in range(4):
        for f in response["data"]["filters"][i]["items"]:
            filters[filters_keys[i]].append(f["id"])
    for key in filters_keys:
        filters[key] = list(map(str, filters[key]))
    return filters


def get_search_res(filters, query, cookies, keyphrase):
    #  print("get_search_res", filters, query, cookies, keyphrase)
    manager = urllib3.PoolManager()
    url = f"https://catalog-ads.wildberries.ru/api/v4/search?ssubject={','.join(filters['xsubject'])}&skind={','.join(filters['fkind'])}&scolor={','.join(filters['fcolor'])}&spp=0&search={urllib.parse.quote(keyphrase)}&{cookies}&{query}&locale=ru&lang=ru&curr=rub&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0"
    request_headers = {
        "Host": "catalog-ads.wildberries.ru",
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    payload = "{\"brands\":[" + ','.join(filters["fbrand"]) + "]}"
    response = eval(manager.request("GET", url, headers=request_headers, body=payload).data.decode("utf-8").replace("true", "True").replace("false", "False").replace("null", "None"))
    return response


def add_search_vendors(search_res, vendors):
    #  print("add_search_vendors", search_res, vendors)
    for res in search_res:
        vendors.insert(res["position"], res["id"])
    return vendors


def get_page_vendors(request, page):
    #  print("get_page_vendors", request, page)
    request += f"&page={page+1}"
    https = urllib3.PoolManager()
    response = https.request("GET", request)
    soup = BeautifulSoup(response.data, "html.parser")
    str_response = str(soup)
    json_response = json.loads(str_response)
    print("json response:", json_response)
    products = json_response["data"]["products"]
    arr = []
    for product in products:
        arr.append(product["id"])
    return arr


def get_vendors(region, keyphrase, pages):
    #  print("get_vendors", region, keyphrase, pages)
    res = []
    cookies = get_cookies(region)
    query, shard_key = get_query(keyphrase)
    request = f"https://wbxcatalog-ru.wildberries.ru/{shard_key}/catalog?spp=0&{cookies}&{query}&locale=ru&lang=ru&curr=rub&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0"
    pages_arr = [page for page in range(0, pages+1)]
    requests = [request for _ in range(0, pages+1)]
    with ThreadPoolExecutor(8) as executor:
        arr = executor.map(get_page_vendors, requests, pages_arr)
    arr = [item for sublist in arr for item in sublist]
    res.extend(arr)
    filters = get_filters(cookies, query, shard_key)
    search_res = get_search_res(filters, query, cookies, keyphrase)
    res = add_search_vendors(search_res, res)
    return res


@dispatch(int, list)
def get_vendor_pos(vendor, vendor_arr):
    try:
        return vendor_arr.index(vendor)
    except:
        return None


@dispatch(int, str, str, int)
def get_vendor_pos(vendor, region, keyphrase, pages):
    vendor_arr = get_vendors(region, keyphrase, pages)
    try:
        return vendor_arr.index(vendor)
    except:
        return None
