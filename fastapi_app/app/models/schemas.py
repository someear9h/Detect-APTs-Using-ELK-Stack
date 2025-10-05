from pydantic import BaseModel
from typing import Optional


class LoginIn(BaseModel):
    username: str
    password: str


class ExecIn(BaseModel):
    command_line: str
    user: Optional[str] = None
    client_ip: Optional[str] = None
    bytes_out: Optional[int] = 0