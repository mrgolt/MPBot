from imports import *

current_platform = platform.system()
if current_platform == "Linux":
    s = Service(os.path.dirname(os.path.realpath(__file__))+"/linux_geckodriver")
    os.chmod(os.path.dirname(os.path.realpath(__file__))+"/linux_geckodriver", 0o755)
elif current_platform == "Darwin":
    s = Service(os.path.dirname(os.path.realpath(__file__))+"/mac_geckodriver")
elif current_platform == "Windows":
    s = Service("windows_geckodriver.exe")
else:
    raise Exception("Your OS is not supported")

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
request_driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)


def get_request(keyphrase):
    request_driver.get(f"https://www.wildberries.ru/catalog/0/search.aspx?page=2&sort=popular&search={keyphrase}")
    products = WebDriverWait(request_driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "j-card-item")))
    arr = []
    for product in products:
        arr.append(int(product.get_attribute("id")[1:]))
    network = request_driver.execute_script(
        "var performance = window.performance || window.mozPerformance || window.msPerformance "
        "|| window.webkitPerformance || {}; var network = performance.getEntries() || {}; return"
        " network;")
    request = None
    for entry in network:
        if "name" in entry.keys():
            name = entry["name"]
            if "spp" in name and "filters" not in name:
                request = name
    return request, arr


def get_page_vendors(request, page):
    request = request.split('&')
    for n, param in enumerate(request):
        if "page" in param:
            request[n] = f"page={2+page}"
    request = '&'.join(request)
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


def get_vendors(keyphrase, pages):
    res = []
    pages_arr = [page for page in range(1, pages+1)]
    request = None
    while not request:
        request, arr = get_request(keyphrase)
    res.extend(arr)
    requests = [request for i in range(1, pages+1)]
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


@dispatch(int, str, int)
def get_vendor_pos(vendor, keyphrase, pages):
    vendor_arr = get_vendors(keyphrase, pages)
    try:
        return vendor_arr.index(vendor)
    except:
        return None


print(get_vendor_pos(43915761, "контейнер для линз", 20))