from PIL import Image
from io import BytesIO


# To validate image on uploading
def validate_image(image):
    allowed_formats = ["JPEG", "PNG", "GIF"]

    try:
        img = Image.open(BytesIO(image.read()))
        if img.format in allowed_formats:
            return True
    except IOError:
        pass

    return False
