from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field("bearer", description="The type of the token")


class TokenDataSchema(BaseModel):
    username: str = Field(..., description="The username")
