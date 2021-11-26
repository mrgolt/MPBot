import platform
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from bs4 import BeautifulSoup
import urllib3
import json
from concurrent.futures import ThreadPoolExecutor
from multipledispatch import dispatch

