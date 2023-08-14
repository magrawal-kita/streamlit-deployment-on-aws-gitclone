from os import getcwd
from os.path import join, abspath
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

tmpFolder = abspath(join(getcwd(), '..', 'Dataset', 'Tmp'))
def CreateDriver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'download.default_directory':tmpFolder})
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

    return driver