import scrapy
import os
import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from ..helpers.Maintainer import Maintainer

class HeartSpider(scrapy.Spider):
    name = 'heart'
    reseller = "https://customer.heartinternet.uk/manage/reseller/index.cgi"
    backupsUrl = "https://customer.heartinternet.uk/manage/mysql-backups.cgi"
    loginUrl = "https://customer.heartinternet.uk/manage/login.cgi"
    start_urls = [loginUrl]
    query = ""
    mysqlRoute = "https://customer.heartinternet.uk/manage/perform-mysql-backups.cgi?"
    otherRoute = "https://customer.heartinternet.uk/manage/mysql-backups.cgi"
    findBackupsScript = """var args = "";
        var backups = document.getElementsByClassName('backup_checkbox');
        for(var i = 0; i < backups.length; i++) {
            if(!backups[i].checked) {
            continue;
            }
            var this_id = backups[i].name;
            this_id = this_id.replace(/backup-/, '');
            args += 'pid=' + this_id + ';';
        }  
        args += 'loader=1';
        return args;"""

    def __init__(self):
        with open("config.json", "r") as config:
            configJson = json.load(config)
            self.email = configJson["username"]
            self.password = configJson["password"]
            self.base_path = configJson["baseUrl"]

        self.maintainer = Maintainer(self.base_path)

        #debug driver
        #self.driver = webdriver.Firefox("/usr/bin/")

        self.driver = webdriver.PhantomJS("HeartSpider/bin/phantomjs")

    def parse(self, response):
        #use selenium now
        self.driver.get(response.url)
        email = self.driver.find_elements_by_css_selector("#hi-login-form input[name='email']")[0]
        passw = self.driver.find_elements_by_css_selector("#hi-login-form input[name='password']")[0]
        email.send_keys(self.email)
        passw.send_keys(self.password)
        self.driver.find_element_by_id("hi-login-form").submit()
        #return scrapy.Request(self.backupsUrl, self.backups)
        self.backups()

        return scrapy.FormRequest.from_response(
            response,
            formid="hi-login-form",
            formdata={"email": "heart@1pcs.co.uk", "password": "RedSky!2!2"},
            callback=self.afterLogin
        )

    def backups(self):
        self.driver.get(self.backupsUrl)
        pages = int(self.driver.find_element_by_id("page-count").text)

        for p in range(0, pages):
            if p > 0:
                self.driver.find_element_by_xpath('//*[@id="content-only"]/p[3]/a[3]').click()
                time.sleep(2)

            self.driver.execute_script("set_all_backup_selections('checked');")
            self.query += self.driver.execute_script(self.findBackupsScript)

            #if p is less than page limit then remove any unwanted loader strings
            if p < pages - 1:
                self.query = self.query.replace("loader=1", "")
                
        print(self.query)

    def afterLogin(self, response):
        print("Starting download...")
        return scrapy.Request(self.mysqlRoute + self.query, self.downloadBackups)

    def runChecks(self):
        self.maintainer.maintain()

    def downloadBackups(self, response):
        curr_date = datetime.datetime.now()
        dir_name = curr_date.strftime("%d-%m-%Y")
        file_name = dir_name + "-mysql-backups.zip"

        if(os.path.exists(self.base_path + dir_name) == False):
            os.makedirs(self.base_path + dir_name)

        path = dir_name + "/" + file_name
        dest = self.base_path + path
        f = open(dest, 'wb')
        f.write(response.body)
        f.close()
        file_size = len(response.body)
        print("Download complete! " + str(file_size) + " bytes written to " + dest)

        #finally run checks with our maintainer
        self.runChecks()
