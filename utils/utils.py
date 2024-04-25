import magic


# To validate image
def validate_image(image):
    mime = magic.Magic(mime=True)
    image_mime = mime.from_buffer(image.read())

    allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

    if image_mime not in allowed_mimes:
        return False
    return True
