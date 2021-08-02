from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class ScrapingCaptchaDatasetPipeline:
    def process_item(self, item, spider):
        return item


class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'image_name': item['image_name']}) for x in item.get(self.images_urls_field, [])]

    def file_path(self, request, response=None, info=None, item=None):
        image_name = request.meta.get('image_name', '')

        return f'{image_name}.jpeg'
