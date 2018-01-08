# ------------------
# Import Libraries
# ------------------
import os
import scrapy
import string
from io import BytesIO
from PIL import Image
from PIL import ImageEnhance
import subprocess as sp
import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = FirefoxBinary("C:/Program Files/Mozilla Firefox/")

os.environ["TESSDATA_PREFIX"] = "C:/Users/lib/Downloads/tesseract-4.0.0-alpha"
time.strftime('%a %b %d %Y %H:%M:%S GMT%z')

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "en-US,en;q=0.7,zh-CN;q=0.3",
    'Host': 'isisn.nsfc.gov.cn',
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    'Referer': 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?locale=zh_CN'
}

captcha_request_headers = {
    ** headers,
    'DNT': 1
}


def orc(img, tesseract='C:/Users/lib/Downloads/tesseract-4.0.0-alpha/tesseract.exe'):
    if isinstance(img, str):
        img = Image.open(img)
    gray = img.convert('L')
    contrast = ImageEnhance.Contrast(gray)
    ctgray = contrast.enhance(3.0)
    bw = ctgray.point(lambda x: 0 if x < 1 else 255)
    bw.save('captcha_threasholded.jpg')
    process = sp.Popen(
        [tesseract, 'captcha_threasholded.jpg', 'out', '--psm 7', '--tessdata-dir ' + os.path.dirname(tesseract)],
        shell=True
    )
    process.wait()
    with open('out.txt', 'r') as f:
        words = ''.join(list(f.readlines())).rstrip()
    words = ''.join(c for c in words if c in string.ascii_letters + string.digits).lower()
    return words


# ------------------
# Class
# ------------------
class SpiderISISN(scrapy.Spider):
    name = 'SpiderISISN'

    def __init__(self):
        super().__init__(self)
        self.driver = webdriver.Firefox(executable_path=r'D:/analysis/scrapy_isisn/geckodriver.exe')

    def start_requests(self):
        urls = ['https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?locale=zh_CN']
        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        # response.xpath('//img[@id="img_checkcode"]/@src')[0].extract()
        session_id = response.headers.getlist('Set-Cookie')[0].decode('utf-8').split('; ')[0]
        code = yield scrapy.Request(
            'https://isisn.nsfc.gov.cn/egrantindex/validatecode.jpg',
            headers={
                ** captcha_request_headers,
                'Cookie': '; '.join([
                    session_id,
                    'isisn=98184645'
                ])
            },
            callback=lambda x: self.get_captcha(x, response)
        )
        # yield

    def get_captcha(self, response, origin):
        with open('validatecode.jpg', 'wb') as f:
            f.write(response.body)
        code = orc('validatecode.jpg')
        body = origin.body.decode('utf-8').replace(
            origin.xpath('//input[@name="f_subjectCode_hideId"]').extract_first(),
            origin.xpath('//input[@name="f_subjectCode_hideId"]').extract_first().replace('value=""', 'value="C0301"')
        ).replace(
            origin.xpath('//input[@name="checkcode"]').extract_first(),
            origin.xpath('//input[@name="checkcode"]').extract_first().replace(
                'type="text"',
                'type="text" value="' + code + '"'
            )
        ).replace(
            origin.xpath('//input[@name="resultDate"]').extract_first(),
            origin.xpath('//input[@name="resultDate"]').extract_first().replace(
                'name="resultDate"',
                'name="resultDate" value="prjNo:,ctitle:,psnName:,orgName:,subjectCode:C0301.分子与进化生态学,f_subjectCode_hideId:C0301,subjectCode_hideName:C0301.分子与进化生态学,keyWords:,checkcode:' +
                code + ',grantCode:218,subGrantCode:,helpGrantCode:,year:2017,sqdm:C0301"'
            )
        ).replace(
            origin.xpath('//input[@name="checkcode"]').extract_first()[1],
            origin.xpath('//input[@name="checkcode"]').extract_first()[1].replace(
                'type="hidden"',
                'type="hidden" value="' + code + '"'
            )
        )

        new_response = origin.replace(body=body)
        yield scrapy.FormRequest.from_response(
            new_response,
            formdata={
                'resultDate': "prjNo:,ctitle:,psnName:,orgName:,subjectCode:C0301.分子与进化生态学,f_subjectCode_hideId:C0301,subjectCode_hideName:C0301.分子与进化生态学,keyWords:,checkcode:" +
                              code + ",grantCode:218,subGrantCode:,helpGrantCode:,year:2017,sqdm:C0301",
                'checkcode': code
            },
            clickdata={'id': 'searchBt'},
            callback=self.get_result
        )

    def get_result(self, response):
        self.driver.get(response.url)
        content = self.dirver.page_source
        with open('tmp.html', 'wb') as f:
            f.write(content)
        self.driver.close()


