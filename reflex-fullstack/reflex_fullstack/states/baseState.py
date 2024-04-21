from typing import Optional
import functools
import json
import os
import time
import reflex as rx
from db_model import User
CLIENT_ID = '453147289562-jkgjib093hs0c0r61n6nkgbbp47kgr2m.apps.googleusercontent.com'
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from sqlmodel import Field, SQLModel, create_engine 

from cv_language.gemini_theme_count import generate_theme_and_count

from urllib.request import urlopen
from PIL import Image


class State(rx.State):
    id_token_json: str = rx.LocalStorage()

    def find_user(self, email: str):
        with rx.session() as session:
            print("\n"*5 + f"email: {email}" + "\n"*5)
            return session.get(User, self.tokeninfo["email"])

    def on_success(self, id_token: dict):
        self.id_token_json = json.dumps(id_token)
        if not self.find_user(self.tokeninfo["email"]):
            with rx.session() as session:
                user = User(
                    name=self.tokeninfo["name"],
                    email=self.tokeninfo["email"],
                    score=0,
                )
                session.add(user)
                session.commit()
        print(f"Logged in as {self.tokeninfo['name']}")
        return None


    @rx.cached_var
    def tokeninfo(self) -> dict[str, str]:
        try:
            return verify_oauth2_token(
                json.loads(self.id_token_json)["credential"],
                requests.Request(),
                CLIENT_ID,
            )
        except Exception as exc:
            if self.id_token_json:
                print(f"Error verifying token: {exc}")
        return {}

    def logout(self):
        self.id_token_json = ""

    @rx.var
    def token_is_valid(self) -> bool:
        try:
            return bool(
                self.tokeninfo
                and int(self.tokeninfo.get("exp", 0)) > time.time()
            )
        except Exception:
            return False

    @rx.cached_var
    def protected_content(self) -> str:
        if self.token_is_valid:
            return f"This content can only be viewed by a logged in User. Nice to see you {self.tokeninfo['name']}"
        return "Not logged in."
    
# ----------------- Webcam State -----------------

    
    # Upload state stuff
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: str = ""
    loading: bool = False

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
        with rx.session() as session:
            self.last_screenshot.save(f"assets/{self.tokeninfo["email"]}.jpg")
            user = session.exec(
                User.select().where(
                    (User.email == self.tokeninfo['email'])
                )
            ).first()
            user.photo_url = f"assets/{self.tokeninfo["email"]}.jpg"
            session.add(user)
            session.commit()

# ----------------- Form State -----------------

    form_data: dict = {}
    game_settings: bool = False
    find_game: bool = False
    submit_num: int = 1
    theme: str = ""

    def handle_submit(self, form_data:dict):
        """Handle the form submit."""
        self.form_data = form_data

    def new_game(self):
        self.game_settings = True
        self.find_game = False
        return None
    
    def search_game(self):
        self.game_settings = False
        self.find_game = True
        return None
    
    def gen_theme_count(self):
        self.theme =  generate_theme_and_count()
        print (f"Theme: {self.theme}")

