from pydantic import BaseModel


class VideoMetadata(BaseModel):

    id : str
    title : str