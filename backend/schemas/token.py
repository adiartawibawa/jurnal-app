from sqlmodel import SQLModel

class Token(SQLModel):
    """Respons login: token yang dipakai klien di header Authorization."""

    access_token: str
    token_type: str = "bearer"