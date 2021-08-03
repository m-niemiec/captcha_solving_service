import logging

from scrapy import Request, spiders
from scrapy.pipelines.media import MediaPipeline
from scrapy.utils.defer import mustbe_deferred
from scrapy.utils.log import failure_to_exc_info
from scrapy.utils.request import request_fingerprint
from twisted.internet.defer import Deferred

from items import CaptchaImageItem

# Declared logger for overwritten MediaPipeline method.
logger = logging.getLogger(__name__)


# We need to overwrite method _process_request from MediaPipeline because this method is checking if image url was
# visited before. Captcha from this spider has always the same url therefore we need to comment out filtering code.
def _process_request(self, request, info, item):
    fp = request_fingerprint(request)
    cb = request.callback or (lambda _: _)
    eb = request.errback
    request.callback = None
    request.errback = None

    # Return cached result if request was already seen
    # if fp in info.downloaded:
    #     return defer_result(info.downloaded[fp]).addCallbacks(cb, eb)

    # Otherwise, wait for result
    wad = Deferred().addCallbacks(cb, eb)
    info.waiting[fp].append(wad)

    # Check if request is downloading right now to avoid doing it twice
    if fp in info.downloading:
        return wad

    # Download request checking media_to_download hook output first
    info.downloading.add(fp)
    dfd = mustbe_deferred(self.media_to_download, request, info, item=item)
    dfd.addCallback(self._check_media_to_download, request, info, item=item)
    dfd.addBoth(self._cache_result_and_execute_waiters, fp, info)
    dfd.addErrback(lambda f: logger.error(
        f.value, exc_info=failure_to_exc_info(f), extra={'spider': info.spider})
                   )
    return dfd.addBoth(lambda _: wad)  # it must return wad at last


MediaPipeline._process_request = _process_request


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
