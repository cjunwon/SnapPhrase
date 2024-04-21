from urllib.request import urlopen
from PIL import Image
from typing import Optional
import functools
import json
import os
import time
import reflex as rx
from db_model import User

# from .baseState import State

class UploadState(rx.State):
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    loading: bool = False

    email: str
    photo_url: str


    def handle_screenshot(self, img_data_uri: str):
        """Webcam screenshot upload handler.
        Args:
            img_data_uri: The data uri of the screenshot (from upload_screenshot).
        """
        if self.loading:
            return
        self.last_screenshot_timestamp = time.strftime("%H:%M:%S")
        with urlopen(img_data_uri) as img:
            self.last_screenshot = Image.open(img)
            self.last_screenshot.load()
            # convert to webp during serialization for smaller size
            self.last_screenshot.format = "WEBP"  # type: ignore
            print(State.user_email())
            
            # with rx.session() as session:
            #     user = session.exec(
            #     User.select().where(
            #         (User.name == State)
            #     )
            # ).first()
            #     print(session.exec(statement))
            #     user = session.exec(
            #     User.select().where(
            #         (User.email == State.tokeninfo['email'])
            #     )
            # ).first()
            # user.photo_url = img_data_uri
            # session.add(user)
            # session.commit()
            # State.tokeninfo['photo_url'] = img_data_uri