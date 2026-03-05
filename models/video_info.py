from pydantic import BaseModel


class VideoInfo(BaseModel):

    Id : str
    title : str