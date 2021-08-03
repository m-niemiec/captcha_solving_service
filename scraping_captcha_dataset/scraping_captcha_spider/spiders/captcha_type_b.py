from scrapy import Request, spiders
from items import CaptchaImageItem


class CaptchaTypeB(spiders.CrawlSpider):
    name = 'Captcha_Type_B'
    start_urls = ['https://public.escambiaclerk.com/BMWebLatest/Home.aspx/Search']

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
        meta = {
            'dont_merge_cookies': True
        }
        return Request(self.start_urls[0], meta=meta, callback=self.parse_start_url)

    def parse_start_url(self, response, **kwargs):
        captcha_image_url = response.xpath('//img[@alt="Captcha"]/@src').get()

        captcha_image = CaptchaImageItem()
        captcha_image['image_name'] = f'captcha_type_c_{self.captchas_counter}'
        captcha_image['image_urls'] = [response.urljoin(captcha_image_url)]

        yield captcha_image

        if self.captchas_counter < self.captchas_amount:
            self.captchas_counter += 1

            yield self.start_new_session()
