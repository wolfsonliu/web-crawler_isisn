# ------------------
# Import Libraries
# ------------------
import scrapy
import string
from PIL import Image
from PIL import ImageEnhance
import subprocess as sp
import time


time.strftime('%a %b %d %Y %H:%M:%S GMT%z')

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "en-US,en;q=0.7,zh-CN;q=0.3",
    'Host': 'isisn.nsfc.gov.cn',
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
}

captcha_request_headers = {
    **headers,
    'DNT': 1,
    'Referer': 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?locale=zh_CN'
}


def orc(img, tesseract='C:/Users/lib/Downloads/tesseract-4.0.0-alpha/tesseract.exe'):
    if isinstance(img, str):
        img = Image.open(img)
    gray = img.convert('L')
    contrast = ImageEnhance.Contrast(gray)
    ctgray = contrast.enhance(3.0)
    bw = ctgray.point(lambda x: 0 if x < 1 else 255)
    bw.save('captcha_threasholded.jpg')
    sp.run(
        [tesseract, '-psm 7', 'captcha_threasholded.jpg', 'out', '--tessdata-dir', os.path.dirname(tesseract)],
        shell=True
    )
    with open('out.txt', 'r') as f:
        words = ''.join(list(f.readlines())).rstrip()

    words = ''.join(c for c in words if c in string.ascii_letters + string.digits).lower()
    return words


# ------------------
# Class
# ------------------
class SpiderISISN(scrapy.Spider):
    name = 'SpiderISISN'

    def start_requests(self):
        urls = ['https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list?locale=zh_CN']
        for url in urls:
            yield scrapy.Request(url=url, meta={'cookiejar': url}, callback=self.parse)

    def parse(self, response):
        # response.xpath('//img[@id="img_checkcode"]/@src')[0].extract()
        pass

    def _get_captcha(self, response):
        self.captcha_image = response.xpath('//img[@id="img_checkcode"]/@src')[0].extract()

