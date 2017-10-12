import scrapy
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

class HeartSpider(scrapy.Spider):
    base_path = "/home/ian/Downloads/"
    name = 'heart'
    reseller = "https://customer.heartinternet.uk/manage/reseller/index.cgi"
    backupsUrl = "https://customer.heartinternet.uk/manage/mysql-backups.cgi"
    loginUrl = "https://customer.heartinternet.uk/manage/login.cgi"
    identityProvider = "https://customer.heartinternet.uk/manage/login-via-identity-postback.cgi?provider=HI;provider-details={%22volatile_key%22:%221507674931:207570:5edf07171344cd65b9621e0170c5bc835ea5f6c8%22};destination=;permanent=;json=0;sitedesigner_trial="
    start_urls = [loginUrl]
    email = "THE_USERNAME"
    password = "THE_PASSWORD"
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
            limited_item_configs['packages'].selectedIds.push(this_id);
        }

        if(limited_item_configs['packages'].selectedIds.length == 0) {
            alert("Nothing is selected.");
            return;
        } else {
            for(var i = 0; i < limited_item_configs['packages'].selectedIds.length; i++) {
            args += 'pid='+limited_item_configs['packages'].selectedIds[i]+';';
            }
        }    
        args += 'loader=1';
        return args;"""

    def __init__(self):
        self.driver = webdriver.PhantomJS("bin/phantomjs")

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
        self.driver.execute_script("toggle_all_selected();")
        self.query = self.driver.execute_script(self.findBackupsScript)
        print(self.query)

    def afterLogin(self, response):
        print("Starting download...")
        return scrapy.Request(self.mysqlRoute + self.query, self.downloadBackups)

    def downloadBackups(self, response):
        curr_date = datetime.datetime.now()
        dir_name = curr_date.strftime("%d-%m-%Y")
        file_name = "mysql-backups.zip"

        if(os.path.exists(self.base_path + dir_name) == False):
            os.makedirs(self.base_path + dir_name)

        path = dir_name + "/" + file_name
        dest = self.base_path + path
        f = open(dest, 'wb')
        f.write(response.body)
        f.close()
        file_size = len(response.body)
        print("Download complete! " + str(file_size) + " bytes written to " + dest)