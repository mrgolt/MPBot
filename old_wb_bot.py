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

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def driver_init(region, headless=True):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    request_driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options, desired_capabilities=caps)
    set_driver_region(request_driver, region)
    request_driver.set_window_size(1800, 1080)
    return request_driver


def set_driver_region(driver, region):
    coords = regions[region]
    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "accuracy": 100
    }
    driver.execute_cdp_cmd("Page.setGeolocationOverride", params)


def set_wb_region(driver):
    region_selector = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/header/div/div/ul/li[2]/span")))
    region_selector.click()
    store = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"pooList\"]/div[1]")))
    store.click()
    submit_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ymaps/div/div/button")))
    submit_btn.click()


def get_request(request_driver, keyphrase):
    request_driver.get(f"https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=popular&search={keyphrase}")
    set_wb_region(request_driver)
    sleep(0.5)
    request_driver.get(f"https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=popular&search={keyphrase}")
    products = WebDriverWait(request_driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "j-card-item")))
    arr = []
    for product in products:
        arr.append(int(product.get_attribute("id")[1:]))
    network = request_driver.get_log("performance")
    request = None
    for entry in network:
        msg = json.loads(entry["message"])
        params = msg["message"]["params"]
        if "request" in params.keys():
            url = params["request"]["url"]
            if "spp" in url and "filters" not in url and "search" not in url:
                request = url
    return request, arr


def get_page_vendors(request, page):
    request += f"&page={page+1}"
    https = urllib3.PoolManager()
    response = https.request("GET", request)
    soup = BeautifulSoup(response.data, "html.parser")
    str_response = str(soup)
    json_response = json.loads(str_response)
    products = json_response["data"]["products"]
    arr = []
    for product in products:
        arr.append(product["id"])
    return arr


def get_vendors(region, keyphrase, pages):
    request_driver = driver_init(region)
    res = []
    pages_arr = [page for page in range(1, pages+1)]
    request = None
    while not request:
        request, arr = get_request(request_driver, keyphrase)
    request_driver.close()
    res.extend(arr)
    requests = [request for _ in range(1, pages+1)]
    with ThreadPoolExecutor(8) as executor:
        arr = executor.map(get_page_vendors, requests, pages_arr)
    arr = [item for sublist in arr for item in sublist]
    res.extend(arr)
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


