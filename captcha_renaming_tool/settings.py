class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Settings(metaclass=SingletonMeta):
    @classmethod
    def set_value(cls, key, value):
        setattr(cls, key, value)

        return value

    @classmethod
    def get_value(cls, key):
        return getattr(cls, key)
