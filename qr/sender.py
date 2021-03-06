from time import sleep
import os

from vk_api.utils import get_random_id
from vk_api import VkApi, VkUpload, VkUserPermissions

USER_ID = os.getenv('USER_ID')
TOKEN = os.getenv('TOKEN')
PUSH_RPS = 20


class Sender:
    class Stop:
        pass

    def __init__(self, queue):
        self.queue = queue
        vk_session = VkApi(token=TOKEN, scope=VkUserPermissions.PHOTOS + VkUserPermissions.MESSAGES)
        self.vk = vk_session.get_api()
        self.upload = VkUpload(vk_session)

    def send(self):
        while True:
            msg = self.queue.get()
            if isinstance(msg, Sender.Stop):
                break

            photo = self.upload.photo_messages(photos=msg)[0]
            self.vk.messages.send(user_id=USER_ID,
                                  attachment=f'photo{photo["owner_id"]}_{photo["id"]}',
                                  random_id=get_random_id())
            sleep(1 / PUSH_RPS)
