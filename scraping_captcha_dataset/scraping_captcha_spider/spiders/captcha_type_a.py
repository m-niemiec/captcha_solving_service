from scrapy import FormRequest, Request
from scrapy import spiders

from items import CaptchaImageItem


class CaptchaTypeA(spiders.CrawlSpider):
    name = 'Captcha_Type_A'
    start_urls = ['http://state.sor.dps.ms.gov/conditionsofuse.aspx']

    # How much images you want to download
    captchas_amount = 10
    captchas_counter = 1

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'IMAGES_STORE': f'downloaded_captchas/{name}',
        'ITEM_PIPELINES': {
            'scraping_captcha_spider.pipelines.CustomImagesPipeline': 1
        }
    }

    def start_new_session(self):
        return Request(self.start_urls[0], callback=self.parse_start_url)

    def parse_start_url(self, response, **kwargs):
        formdata = {
            'ctl00$ContentPlaceHolder1$btnAgree': 'I agree'
        }

        return FormRequest.from_response(response, formdata=formdata, callback=self.parse_download_captcha)

    def parse_download_captcha(self, response):
        captcha_image_url = response.xpath('//img[@id="captcha_contentplaceholder1_botdetectcaptcha_CaptchaImage"]/@src').get()

        captcha_image = CaptchaImageItem()
        captcha_image['image_name'] = f'captcha_type_c_{self.captchas_counter}'
        captcha_image['image_urls'] = [response.urljoin(captcha_image_url)]

        yield captcha_image

        if self.captchas_counter < self.captchas_amount:
            self.captchas_counter += 1

            yield self.start_new_session()
