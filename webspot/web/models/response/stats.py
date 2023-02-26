from pydantic import BaseModel


class StatsResponse(BaseModel):
    entropy: float
    score: float
