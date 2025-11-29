from enum import Enum
from typing import Annotated, Optional

from fastapi import FastAPI
from fastapi.params import Query

from rapidllm import RapidClient, RapidClientSettings, RapidLogger, RapidLoggerConfig

# TODO:Create audio depedency so that it's transcribed beforehand and path function just recieves text(str).

config_data = RapidLoggerConfig(
    name="WebApp",
    console_level="WARNING",  # Converted to 30 by Pydantic
    file_level="DEBUG",  # Converted to 10 by Pydantic
)

app_logger = RapidLogger(config_data)
settings = RapidClientSettings()
client = RapidClient(settings=settings)


class Tags(Enum):
    example = "example"


app = FastAPI()


@app.get("/", tags=[Tags.example])
async def root():
    return {"message": "Hello World"}


@app.get("/rapid/exampleai", tags=[Tags.example])
def simple_prompt(
    message: Annotated[Optional[str], Query()] = None,
    prompt: Annotated[Optional[str], Query()] = None,
    audio_path: Annotated[Optional[str], Query()] = None,
):
    app_logger.info("Message Recieved: %s and a media_path of %s", message, audio_path)
    result = client.generate_chat_response(
        message=message, prompt=prompt, audio_path=audio_path
    )
    return {"result": result}
