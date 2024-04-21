from sqlmodel import Field
from typing import Optional 

import reflex as rx


class UserGame(rx.Model, table=True):
    """A table of Follows. This is a many-to-many join table.

    See https://sqlmodel.tiangolo.com/tutorial/many-to-many/ for more information.
    """

    user_email: str = Field(primary_key=True)
    game_id: str = Field(primary_key=True)


class User(rx.Model, table=True):
    """A table of Users."""

    name: str
    email: str = Field(primary_key=True)
    photo_url: Optional[str] = None
    score: Optional[int] = 0
    in_lobby: Optional[bool] = False   # If user is in a game already
    # league_id: Optional[int] = Field(default=None, primary_key=True)   # If user is in a league already
    league_id: Optional[int] = None   # If user is in a league already

class Game(rx.Model, table=True):
    """A table of Game."""

    # game_id: Optional[int] = Field(primary_key=True)
    theme: str  # Current theme of the game
    submit_num: str # How many images are required
    game_state: Optional[str] = 0   # Store state of the game
    league_id: Optional[int] = Field(primary_key=True)   # which league this game in

class League(rx.Model, table=True):
    """A table of Users."""

    # users: list[str]    # List of users in the league
    # game_session: Game
    league_name: str
    # league_id: Optional[int] = Field(primary_key=True)
    # leaderboard: list[str]  # List of users in order of score
    rounds: Optional[int] = 0