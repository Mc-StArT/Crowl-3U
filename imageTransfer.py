import base64 as b64
# with open("image.jpg", "rb") as image:
#     image_read = image.read()

# with open("image.b64", "wb") as image:
#     image.write(b64.encodebytes(image_read))


with open("newimage.b64", "rb") as image:
    image_read = image.read()

with open("newimage.jpg", "wb") as image:
    image.write(b64.decodebytes(image_read))