import os
import sys
import datetime
import time
import json

from selenium import webdriver
from selenium import common
from bs4 import BeautifulSoup

def nowtime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d-%H-%M-%S")

def log_info(message):
    print(f"[{nowtime()}]: {message}\n")
    log = open("log.txt","a",encoding = 'utf-8')
    log.write(f"[{nowtime()}]: {message}\n")
    log.close()

directory = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
if os.path.isfile(f"{directory}/config.json"):
    with open(f"{directory}/config.json", "r", encoding="utf-8") as file1:
        info = json.load(file1)
else:
    log_info("설정파일(config.json)을 찾을수 없습니다.")
    quit()

with open(f"{directory}/data/Regional Local Government.json", "r", encoding="utf-8") as file2:
    RLG = json.load(file2)
with open(f"{directory}/data/Type.json", "r", encoding="utf-8") as file3:
    school_type = json.load(file3)

log_info("자동 자가진단을 시작합니다!")

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

driver = webdriver.Chrome('chromedriver.exe',chrome_options=options)

driver.get('https://hcs.eduro.go.kr/#/loginHome')
driver.find_element_by_xpath('//div[@class="group"]/button').click()

time.sleep(0.5)
#정보 입력창
log_info("학교정보를 입력합니다.")
driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr[1]/td/button').click()

driver.find_element_by_xpath(f'//table[@class="layerSchoolTable"]/tbody/tr[1]/td/select/option[@value="{RLG[info["RLP"]]}"]').click()
driver.find_element_by_xpath(f'//table[@class="layerSchoolTable"]/tbody/tr[2]/td/select/option[@value="{school_type[info["SCHOOL_TYPE"]]}"]').click()

driver.find_element_by_xpath('//table[@class="layerSchoolTable"]/tbody/tr[3]/td[1]/input').send_keys(info['SCHOOL_NAME'])
driver.find_element_by_xpath('//table[@class="layerSchoolTable"]/tbody/tr[3]/td[2]/button').click()

time.sleep(0.5)
log_info("개인정보를 입력합니다.")
driver.find_element_by_xpath('//ul[@class="layerSchoolArea"]/li/p/a').click()
driver.find_element_by_xpath('//div[@class="layerBtnWrap"]/input').click()

driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr[2]/td/input').send_keys(info['NAME'])
driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr[3]/td/input').send_keys(info['BIRTHDAY'])

driver.find_element_by_xpath('//input[@id="btnConfirm"]').click()

time.sleep(0.5)
#비밀번호 등록창
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
if soup.find('p',{'class':'guide_user'}) != None:
    msg = soup.find('p',{'class':'guide_user'})
    if msg.text.find("로그인 시 사용할 비밀번호를 설정하세요.") != -1:
        log_info("비밀번호가 등록되어있지 않습니다. 설정된 비밀번호로 등록합니다.")
        driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr[1]/td/input').send_keys(info['PASSWORD'])
        driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr[2]/td/input').send_keys(info['PASSWORD'])

        driver.find_element_by_xpath('//input[@id="btnConfirm"]').click()
        time.sleep(0.5)
#비밀번호 인증창
log_info("설정된 비밀번호로 인증합니다.")
driver.find_element_by_xpath('//div[@id="WriteInfoForm"]/table/tbody/tr/td/input').send_keys(info['PASSWORD'])
driver.find_element_by_xpath('//input[@id="btnConfirm"]').click()
time.sleep(1)

#사람 선택창
log_info("로그인에 성공하였습니다.")
driver.find_element_by_xpath('//section[@class="memberWrap"]/div[2]/ul/li/a/span').click()
time.sleep(1.25)

#선택창
try:
    driver.find_element_by_xpath('//div[@class="survey_question"]/dl[1]/dd/ul/li/label').click()
except common.exceptions.UnexpectedAlertPresentException:
    log_info(f"에러발생: 자가진단에 실패하였습니다.")
    quit()
driver.find_element_by_xpath('//div[@class="survey_question"]/dl[2]/dd/ul/li/label').click()
driver.find_element_by_xpath('//div[@class="survey_question"]/dl[3]/dd/ul/li/label').click()
driver.find_element_by_xpath('//div[@class="survey_question"]/dl[4]/dd/ul/li/label').click()
driver.find_element_by_xpath('//div[@class="survey_question"]/dl[5]/dd/ul/li/label').click()
driver.find_element_by_xpath('//input[@id="btnConfirm"]').click()

if not os.path.exists(f"{directory}/screenshot"):
    os.mkdir(f"{directory}/screenshot")
driver.save_screenshot(f"{directory}/screenshot/{nowtime()}.png")
log_info("제출을 완료하였습니다.")
driver.quit()