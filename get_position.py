from init import *

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
browser = webdriver.Remote("http://selenium:4444/wd/hub", options=options)


def get_keyword_position(limit: int=1000, query: str="", artikul: str=""):
    page = 1
    next_button = [1]
    res = []
    index = None

    query = query.replace(" ","+")

    while len(next_button) > 0 and len(res) <= limit:
        browser.get(
            'https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search=' + query + '&sort=popular&page=' + str(
                page))
        sleep(2)
        html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

        soup = BeautifulSoup(html, 'html.parser')

        res += re.findall(r'data-popup-nm-id=\"(\d+)\"', str(soup))
        next_button = re.findall(r"pagination-next", str(soup))
        page += 1
        try:
            if res.index(artikul):
                index = res.index(artikul)+1
                break
        except:
            continue

    return index


#print(get_keyword_position(1000, "солнцезащитные очки","31199709"))