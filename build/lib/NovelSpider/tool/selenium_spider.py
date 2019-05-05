

from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Firefox(executable_path="C:/Users/zw/Downloads/geckodriver.exe")

browser.get("https://www.zhihu.com/signin")
import time
time.sleep(15)
browser.find_element_by_css_selector(".Login-content input[name='username']").send_keys("13698194931")
browser.find_element_by_css_selector(".Login-content input[name='password']").send_keys("zw246998--")

browser.find_element_by_css_selector(".Login-content button.Button:nth-child(5)").click()

# t_selector = Selector(text=browser.page_source)
# print(t_selector.css("#main > .novellist a::attr(href)").extract_first(""))
# browser.quit()