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
    response = None
    cookies = None
    try:
        response = manager.request("POST", url, headers=headers, body=payload2)
        if response.status == 504:
            i = 0
            while response.status == 504 and i < 3:
                response = manager.request("POST", url, headers=headers, body=payload2)
                i += 1
                sleep(0.1)

        cookies = response.headers["Set-Cookie"].replace("httponly", '').replace("path=/", '').replace(", ", '').replace("HttpOnly", '').replace('Path=/', '').split("; ")
        res = []
        for n, cookie in enumerate(cookies):
            for nc in needed_cookies:
                if nc in cookie:
                    if nc == "__pricemargin":
                        cookie_value = cookie.split("=")[1].split('-')[0]
                    else:
                        cookie_value = cookie.split("=")[1]
                    cookie_value = cookie_value.replace("_", ",")
                    res.append(f"{needed_cookies[nc]}={cookie_value}")
                    break
        res = '&'.join(res)
    except:
        if response:
            print("response code from cookies:", response.status)
            if response.status != 200:
                print("response from cookies:", response.data.decode("utf-8"))
        else:
            print("no response from cookies")
        if cookies:
            print("cookies:", cookies)
        else:
            print("no cookies")
        res = None
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
    response = None
    try:
        response = manager.request("GET", url, headers=request_headers)
        if response.status == 504:
            i = 0
            while response.status == 504 and i < 3:
                response = manager.request("GET", url, headers=request_headers)
                i += 1
        decoded_response = response.data.decode("utf-8")[:-1]
        # print("response:", response)
        response1 = eval(decoded_response)
        return response1["query"], response1["shardKey"]
    except:
        print("url from query:", url)
        print("keyphrase from query:", keyphrase)
        if response:
            print("response code from query:", response.status)
            if response.status != 200:
                print("response from query:", response.data.decode("utf-8"))
        else:
            print("no response from query")
        return None


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
    response = None
    try:
        response = manager.request("GET", url, headers=request_headers)
        if response.status == 504:
            i = 0
            while response.status == 504 and i < 3:
                response = manager.request("GET", url, headers=request_headers)
                i += 1
        decoded_response = response.data.decode("utf-8")
        response1 = eval(decoded_response)
        for i in range(4):
            for f in response1["data"]["filters"][i]["items"]:
                filters[filters_keys[i]].append(f["id"])
        for key in filters_keys:
            filters[key] = list(map(str, filters[key]))
    except:
        print("url from get_filters:", url)
        filters = None
        if response:
            print("response code from filters:", response.status)
            if response.status != 200:
                print("response from filters:", response.data.decode("utf-8"))

        else:
            print("no response from filters")
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
    response = None
    try:
        response = manager.request("GET", url, headers=request_headers, body=payload)
        if response.status == 504:
            i = 0
            while response.status == 504 and i < 3:
                response = manager.request("GET", url, headers=request_headers, body=payload)
                i += 1
        decoded_response = response.data.decode("utf-8").replace("true", "True").replace("false", "False").replace("null", "None")
        response1 = eval(decoded_response)
    except:
        print("payload from get_search_res:", payload)
        print("url from get_search_res:", url)
        if response:
            print("response code from get_search:", response.status)
            if response.status != 200:
                print("response from get_search:", response.data.decode("utf-8"))
        else:
            print("no response from get_search")
        response1 = None
    return response1


def add_search_vendors(search_res, vendors):
    #  print("add_search_vendors", search_res, vendors)
    for res in search_res:
        vendors.insert(res["position"], res["id"])
    return vendors


def get_page_vendors(request, page):
    #  print("get_page_vendors", request, page)
    request += f"&page={page+1}"
    # print("request:", request)
    https = urllib3.PoolManager()
    response = None
    json_response = None
    products = None
    arr = None
    try:
        response = https.request("GET", request)
        soup = BeautifulSoup(response.data, "html.parser")
        if response.status != 200:
            i = 0
            while response.status != 200 and i < 5:
                sleep(1)
                response = https.request("GET", request)
                i += 1
        str_response = str(soup)
        # print("str_response:", str_response)
        json_response = json.loads(str_response)
        products = json_response["data"]["products"]
        arr = []
        for product in products:
            arr.append(product["id"])
    except:
        if response:
            print("response code from get_page_vendors:", response.status)
        else:
            print("no response from get_page_vendors")
        if json_response:
            print("json response from get_page_vendord:", json_response)
        else:
            print("no json response from get_page_vendors")
        if products:
            print("products from get_page_vendors:", products)
        else:
            print("no products from get_page_vandors")
        if arr:
            print("ids from get_page_vendors:", arr)
        else:
            print("no ids from get_page_vendors")
        arr = None
    return arr


def get_vendors(region, keyphrase, pages):
    #  print("get_vendors", region, keyphrase, pages)
    res = []
    cookies = get_cookies(region)
    if not cookies:
        return "Ошибка при получении параметров запроса"
    raw_query = get_query(keyphrase)
    if raw_query:
        query, shard_key = raw_query
    else:
        return "Ошибка при получении запроса и осколка"
    request = f"https://wbxcatalog-ru.wildberries.ru/{shard_key}/catalog?spp=0&{cookies}&{query}&locale=ru&lang=ru&curr=rub&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0"
    pages_arr = [page for page in range(0, pages+1)]
    requests = [request for _ in range(0, pages+1)]
    with ThreadPoolExecutor(8) as executor:
        arr = list(executor.map(get_page_vendors, requests, pages_arr))
    if type(arr[0]) == str:
        return arr[0]
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
    if type(vendor_arr) == str:
        return vendor_arr
    try:
        return vendor_arr.index(vendor)
    except:
        return None
