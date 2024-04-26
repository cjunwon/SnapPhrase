from typing import Optional
import functools
import json
import os
import time
import reflex as rx
from db_model import User, Game, League
CLIENT_ID = '453147289562-jkgjib093hs0c0r61n6nkgbbp47kgr2m.apps.googleusercontent.com'
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from sqlmodel import Field, SQLModel, create_engine 
from sqlmodel import Session,select,func

from cv_language.gemini_theme_count import generate_theme_and_count

from urllib.request import urlopen
from PIL import Image

from cv_language.gemini_image_checker import image_checker

import asyncio


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
            self.last_screenshot.save(f"assets/{self.tokeninfo['email']}.jpg")
            user = session.exec(
                User.select().where(
                    (User.email == self.tokeninfo['email'])
                )
            ).first()
            user.photo_url = f"{self.tokeninfo['email']}.jpg"
            


            session.add(user)
            session.commit()

# ----------------- Form State -----------------

    form_data: dict = {}
    game_settings: bool = False
    find_game: bool = False
    theme: str = ""
    # current_game: Optional[Game] = None
    # current_league: Optional[League] = None

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
        self.theme = generate_theme_and_count()
        print (f"Theme: {self.theme}")

    def selected_game(self):
        with rx.session() as session:
            user = session.exec(
                User.select().where(
                    User.email.contains(self.tokeninfo['email'])
                )
            ).first()
        if not user.photo_url:
            return None
        # self.gen_theme_count()
        # Create a new league
        if self.form_data.keys() == {"Languages"}:
            print("Hosted game with language: ", self.form_data["Languages"])
            with rx.session() as session:
                current_game = Game(
                        language=self.form_data["Languages"], theme=self.theme
                    )
                current_league = League(
                        current_game_id=current_game.id
                    )
                session.add(
                    # Make a new game session
                    current_game,
                    # Make a new league
                    current_league
                )

                user = session.exec(
                    User.select().where(
                        (User.email == self.tokeninfo['email'])
                    )
                ).first()
                user.league_id = current_league.id
                user.game_id = current_game.id
                session.add(user)
                session.commit()

        # Join an existing league
        elif self.form_data.keys() == {"PLeague Code"}:
            print("Joined game with code: ", self.form_data["PLeague Code"])
            with rx.session() as session:
                user = session.exec(
                    User.select().where(
                        (User.email == self.tokeninfo['email'])
                        )
                    ).first()
                user.game_id = self.form_data["PLeague Code"]
                session.add(user)
                session.commit()
        return None

    


# ----------------- Refresh Pics State -----------------
    count: int = 0
    progress: int = 0

    async def run(self):
        # Reset the count.
        self.set_progress(0)
        yield

        # Count to 10 while showing progress.
        for i in range(10):
            # Wait and increment.
            await asyncio.sleep(0.5)
            self.count += 1
            print(f"Count: {self.count}")
            # Update the progress.
            self.set_progress(i + 1)

            # Yield to send the update.
            yield
        print("Done!")
    gallery: list[str]
    gallery_size: int
    def gallery_refresh(self):
        # Start the run coroutine.
        with rx.session() as session:
            self.gallery_size = session.exec(select(func.count()).where(User.photo_url != None)).one()
            self.gallery = session.exec(select(User.photo_url).where(User.email != self.tokeninfo['email'])).all()
            for i in range(len(self.gallery)):
                self.gallery[i] = self.gallery[i][6:]
                # print(self.gallery[i])
            # print(total)
            # if total >= 3:
                # return True
        # return False
    
    


# class FormState(rx.State):
