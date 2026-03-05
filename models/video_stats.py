from pydantic import BaseModel


class VideoStats(BaseModel):

    id : str
    views : int
    subs_gained : int