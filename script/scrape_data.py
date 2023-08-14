#!/bin/python3.10

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
from DriverInit import tmpFolder, CreateDriver
from os.path import join, exists, abspath, dirname
from os import remove, getcwd
from shutil import copy

OUTPUT_CSV_FILENAME = "scraped_data.csv"

def Download(driver, object, dsn):
    links = {
        'Projects': 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=111',
        'Credits': 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=206',
        'Issuances': 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=112',
        'Accounts': 'https://acr2.apx.com/myModule/rpt/myrpt.asp?r=1&TabName=Generator'
        }
    filename = {
        'Source': {
            'Projects': 'temp.csv',
            'Credits': 'temp.csv',
            'Issuances': 'temp.csv',
            'Accounts': 'temp.csv'
        },
        'Destination': {
            'Projects': f'{str(datetime.now().date())}_ACR_ProjectsList.csv',
            'Credits': f'{str(datetime.now().date())}_ACR_RetiredCredits.csv',
            'Issuances': f'{str(datetime.now().date())}_ACR_IssuedCredits.csv',
            'Accounts': f'{str(datetime.now().date())}_ACR_AccountHolders.csv'
        }
    }

    driver.get(links[object])
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/table/tbody/tr/td/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]')))
    driver.execute_script('downloadnow(1);')

    downloadedPath = join(tmpFolder, filename['Source'][object])
    copyPath = join(dsn, OUTPUT_CSV_FILENAME)

    while not exists(downloadedPath):
        sleep(1)

    print('Downloaded file exists in Temporary Folder')
    copy(downloadedPath, copyPath)
    print(f'Successfully downloaded to {copyPath}')
    remove(downloadedPath)

class ACRScraper:
    def DownloadProjects(driver, dsn):
        Download(driver, 'Projects', dsn)

    def DownloadCredits(driver, dsn):
        Download(driver, 'Credits', dsn)

    def DownloadIssuances(driver, dsn):
        Download(driver, 'Issuances', dsn)

    def DownloadAccounts(driver, dsn):
        Download(driver, 'Accounts', dsn)

class Scraper:
    def __init__(self):
        self.driver = CreateDriver()
        self.scraper = {
            'ACR': ACRScraper,
        }

    def Scrape(self, registry, object, dsn):
        if object == 'Projects':
            self.scraper[registry].DownloadProjects(self.driver, dsn)
        elif object == 'Credits':
            self.scraper[registry].DownloadCredits(self.driver, dsn)
        elif object == 'Issuances':
            self.scraper[registry].DownloadIssuances(self.driver, dsn)
        elif object == 'Accounts':
            self.scraper[registry].DownloadAccounts(self.driver, dsn)
        elif registry not in self.scraper.keys():
            print(f'Registry not available, please use one of the following: {", ".join(self.scraper.keys())}')


scraper = Scraper()

downloadFolder = getcwd()

scraper.Scrape('ACR', 'Projects', downloadFolder)


