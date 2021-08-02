from scrapy import Item, Field


class CaptchaImageItem(Item):
    image_urls = Field()
    images = Field()
    image_name = Field()


class CaptchaImageFileItem(Item):
    file_urls = Field()
    files = Field
