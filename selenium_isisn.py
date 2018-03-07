import os
import time
import string
import random
import pandas as pd
import subprocess as sp
from selenium import webdriver
from PIL import Image
from PIL import ImageEnhance

# 张书红 19711108
random.seed(1024)

os.environ["TESSDATA_PREFIX"] = os.path.join(os.getcwd(), "tesseract-4.0.0-alpha")


def orc(img, tesseract=os.path.join(os.getcwd(), 'tesseract-4.0.0-alpha/tesseract.exe')):
    if isinstance(img, str):
        img = Image.open(img)
    gray = img.convert('L')
    contrast = ImageEnhance.Contrast(gray)
    ctgray = contrast.enhance(3.0)
    bw = ctgray.point(lambda x: 0 if x < 1 else 255)
    bw.save('captcha_threasholded.png')
    process = sp.Popen(
        [tesseract, 'captcha_threasholded.png', 'out', '--psm 7', '--tessdata-dir ' + os.path.dirname(tesseract)],
        shell=True
    )
    process.wait()
    with open('out.txt', 'r') as f:
        words = ''.join(list(f.readlines())).rstrip()
    words = ''.join(c for c in words if c in string.ascii_letters + string.digits).lower()
    return words


def get_grant_info(year, subject_code, grant, driver, out_file):
    if driver.page_source.find('id="dataGrid"') > 0:
        # there are entries
        while True:
            with open(out_file, 'ab') as f:
                table_data = driver.find_element_by_xpath('//table[@id="dataGrid"]').text.split('\n')
                f.write(
                    '\n'.join(
                        ','.join(
                            [year, grant, subject_code] + x.split(' ')
                        ) for x in table_data
                    ).encode('utf-8')
                )
                f.write('\n'.encode('utf-8'))
            next_button_class = driver.find_element_by_id('next_t_TopBarMnt').get_attribute('class')
            # whether has next page
            if next_button_class.find('ui-state-disabled') != -1:
                break
            next_code_fail = 0
            next_code_wrong = True
            while next_code_wrong:
                # captcha loop
                # next page checkcode
                nextpage_checkcode_img = driver.find_element_by_id('img_checkcode')
                nextpage_checkcode_img.screenshot('captcha_page.png')
                try:
                    nextpage_captcha = orc('captcha_page.png')
                    captcha_entry = driver.find_element_by_xpath('//input[@id="checkCode"]')
                    driver.execute_script('arguments[0].value = arguments[1]', captcha_entry, nextpage_captcha)
                    driver.find_element_by_css_selector('#next_t_TopBarMnt').click()  # next page
                    next_table_data = driver.find_element_by_xpath('//table[@id="dataGrid"]').text.split('\n')
                    if table_data[0] != next_table_data[0]:
                        # if new page saved stop captcha loop
                        next_code_wrong = False
                    else:
                        next_code_fail += 1
                        if next_code_fail > 2:
                            time.sleep(random.uniform(5, 10))
                            next_code_fail = 0
                        else:
                            time.sleep(random.uniform(0, 3))
                            if random.randint(0, 10) > 5:
                                nextpage_checkcode_img.click()
                except UnicodeDecodeError:
                    # incase the orc have gbk codec
                    nextpage_checkcode_img.click()



def search_grant_info(year, subject_code, subject_name, grant,  driver, out_file):
    driver.get('https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?locale=zh_CN')
    element = dict()

    # 填写申请代码
    element['subjectCode'] = driver.find_element_by_id('f_subjectCode_hideId')
    driver.execute_script('arguments[0].value = arguments[1]', element['subjectCode'], subject_code)
    element['subjectName'] = driver.find_element_by_id('f_subjectCode_hideName')
    driver.execute_script(
        'arguments[0].value = arguments[1]',
        element['subjectName'],
        '.'.join([subject_code, subject_name])
    )

    # 选择资助类别
    element['grantCode'] = driver.find_element_by_xpath(
        '//select[@id="f_grantCode"]/option[text()="{0}"]'.format(grant)
    )
    element['grantCode'].click()

    # 选择年份
    element['year'] = driver.find_element_by_xpath(
        '//select[@id="f_year"]/option[text()="{0}"]'.format(year)
    )
    element['year'].click()
    codefail = 0

    while True:
        # checkcode
        element['captcha_image'] = driver.find_element_by_id('img_checkcode')
        element['captcha_image'].screenshot('captcha.png')
        captcha = orc('captcha.png')

        element['captcha'] = driver.find_element_by_xpath('//input[@id="f_checkcode"]')
        driver.execute_script('arguments[0].value = arguments[1]', element['captcha'], captcha)

        # click submit
        driver.find_element_by_css_selector('.button_an').click()
        if driver.page_source.find('检索结果') > 0:
            # successfully get result
            get_grant_info(year, subject_code, grant, driver, out_file)
            break
        else:
            # code wrong
            codefail += 1
            if codefail > 2:
                time.sleep(random.uniform(5, 10))
                codefail = 0
            else:
                time.sleep(random.uniform(0, 3))
            element['captcha_image'].click()


years = [str(x) for x in range(1997, 2019)]
grants = [
    '面上项目', '重点项目', '重大项目', '重大研究计划', '国家杰出青年科学基金', '创新研究群体项目',
    '国际(地区)合作与交流项目', '专项基金项目', '联合基金项目', '青年科学基金项目', '地区科学基金项目',
    '海外及港澳学者合作研究基金', '国家基础科学人才培养基金', '国家重大科研仪器设备研制专项', '国家重大科研仪器研制项目',
    '优秀青年科学基金项目', '应急管理项目', '科学中心项目'
]
subjects = pd.read_csv('subject.csv')

info = dict()
info['subjectCode'] = 'B0201'
info['grant'] = '重点项目'
info['year'] = '2016'

ff = webdriver.Firefox(executable_path=r'./geckodriver.exe')
# search_grant_info('2015', 'A01', '数学', '国际(地区)合作与交流项目', ff, 'gjdqhzyjl2015.csv')
# get_grant_info('2014', 'A01', '面上项目', ff, '2014面上.tsv')

for x in range(2002, 2009):
    search_grant_info('{0}'.format(x), 'A01', '数学', '项目', ff, 'hwjgaxzhzyj{0}.csv'.format(x))


ff = webdriver.Firefox(executable_path=r'./geckodriver.exe')

for x in[2001, 2002, 2003, 2004, 2005, 2006]:# range(2001, 2014):
    search_grant_info('{0}'.format(x), 'A01', '数学', '面上项目', ff, 'ms{0}--.csv'.format(x))