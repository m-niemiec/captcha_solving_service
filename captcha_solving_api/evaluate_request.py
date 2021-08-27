import re
import uuid
from io import BytesIO

from PIL import Image
from fastapi import UploadFile, HTTPException


class EvaluateRequest:
    @staticmethod
    async def analyze_image(captcha_image: UploadFile) -> tuple[str, str]:
        accepted_formats = ['jpg', 'jpeg', 'png']

        try:
            image_format = re.findall(r'.+\.(.+)', captcha_image.filename)[0].lower()
        except (IndexError, TypeError):
            raise HTTPException(status_code=400, detail='Oops! Missing extension after "." in your image!')

        if image_format.lower() not in accepted_formats:
            raise HTTPException(status_code=400, detail=f'Oops! Image format not supported. Our accepted formats are'
                                                        f'here - {accepted_formats}')

        stream = BytesIO(await captcha_image.read())
        image = Image.open(stream).convert('RGB')
        stream.close()

        image_name = uuid.uuid4().hex

        image_path = f'temp_captchas/{image_name}.{image_format}'

        image.save(image_path)

        return image_format, image_path
