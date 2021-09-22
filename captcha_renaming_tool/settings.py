class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Settings(metaclass=SingletonMeta):
    def __init__(self):
        self.captcha_solution_text = None
        self.current_captcha_image = None
        self.total_images_amount = None
        self.current_size = None
        self.root = None
        self.renamed_total_images_amount = None
        self.current_captcha_name = None
        self.image_index = None
        self.image_list = None
        self.update_captcha_image_method = None
