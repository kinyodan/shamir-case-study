from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from fastapi import Request
from pydantic import BaseModel

class OAuth2EmailPasswordRequestForm:
    def __init__(self, request: Request):
        self.request = request
        self.form = None

    async def __call__(self):
        form = await self.request.form()
        self.form = form
        return form

    @property
    def username(self) -> str:
        return self.form.get("username")

    @property
    def password(self) -> str:
        return self.form.get("password")

    @property
    def email(self) -> str:
        return self.form.get("email")
