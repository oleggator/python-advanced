from io import BytesIO

from qrcode import QRCode, constants

from PIL import Image


class QRGenerator:
    def __init__(self, queue):
        self.queue = queue
        self.qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )

    def generate(self, code):
        try:
            self.qr.clear()
            self.qr.add_data(code)
            self.qr.make(fit=True)
            img = self.qr.make_image(fill_color="black", back_color="white")
            img.thumbnail((200, 200))

            tmp = Image.open('template.png')
            tmp.paste(img, (50, 50))

            buffered = BytesIO()
            tmp.save(buffered, format="PNG")
            buffered.seek(0)

            self.queue.put_nowait(buffered)

        except Exception as e:
            print(e)
