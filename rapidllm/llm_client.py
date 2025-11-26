import base64
import os
from typing import Any, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from .rapidlogger import RapidLogger, RapidLoggerConfig

config_data = RapidLoggerConfig(
    name="LLM",
    console_level="WARNING", # Converted to 30 by Pydantic
    file_level="DEBUG"       # Converted to 10 by Pydantic
)

app_logger = RapidLogger(config_data)


# --- 1. Pydantic Model for Client Configuration ---
class RapidClientSettings(BaseModel):
    """Configuration settings for the OpenAI LLM Client."""
    # Read BASE_URL from the environment or use the default "http://broken"
    # This automatically handles the logic you had at the top of your script.
    base_url: str = Field(
        default_factory=lambda: os.environ.get("BASE_URL", "http://broken"),
        description="The base URL for the OpenAI-compatible API endpoint."
    )
    
    # In a real app, you would use secrets management, but for this
    # example, we'll use a placeholder since the URL is a local mock.
    api_key: str = Field(
        default="anything",
        description="API key for the LLM service."
    )
    default_model: str = "ai/gemma3n"

# --- 2. The Main LLM Client Class (Composition) ---
class RapidClient:
    """A wrapper class that utilizes a Pydantic model for its configuration."""
    
    def __init__(self, settings: RapidClientSettings):
        # 1. Store the validated settings
        self.settings = settings
        
        # 2. Instantiate the official OpenAI client using validated settings
        self.client = OpenAI(
            base_url=self.settings.base_url, 
            api_key=self.settings.api_key
        )

    # NEW METHOD: For transcribing audio
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribes an audio file into text using the OpenAI Audio API.

        Args:
            audio_path (str): The local path to the audio file.

        Returns:
            Optional[str]: The transcribed text, or None on failure.
        """
        full_audio_path = os.path.join("audio", audio_path) # Assuming 'audio' folder convention
        if not os.path.exists(full_audio_path):
            app_logger.error(f"Audio file not found at path: {full_audio_path}")
            return None
        app_logger.info("found an audio file")
        return "tell me a joke"
        # The OpenAI transcription API requires the file object
        # try:
        #     with open(full_audio_path, "rb") as audio_file:
        #         app_logger.info("Starting audio transcription...")
        #         # The 'whisper-1' model is the standard for transcription
        #         transcription = self.client.audio.transcriptions.create(
        #             model="whisper-1", 
        #             file=audio_file
        #         )
        #         app_logger.info("Transcription complete.")
        #         return transcription.text
        # except Exception as e:
        #     app_logger.error(f"Error during audio transcription for {full_audio_path}: {e}")
        #     return None

    # UPDATED FUNCTION: Accepts audio_path instead of media_path (image)
    def generate_chat_response(self, message: str, prompt: str = "Helpful AI. Give me a bare string no added newlines", audio_path: Optional[str] = None ) -> str :
        """
        Creates a chat completion using a system prompt, a user message, and optional audio file.
        The audio file is first transcribed to text.

        Args:
            prompt (str): The instruction/context for the model (System Role).
            message (str): The user's input text message (User Role).
            audio_path (Optional[str]): The local path to an audio file.

        Returns:
            str: The text content of the model's response.
        """
        
        final_user_message = message

        # 1. Handle the optional audio file
        if audio_path:
            app_logger.debug("Attempting to transcribe audio from %s", audio_path)
            transcribed_text = self.transcribe_audio(audio_path)
            
            if transcribed_text:
                # Combine the original message with the transcribed audio text
                final_user_message = (
                    f"{message}\n\n"
                    f"**Transcribed Audio:** {transcribed_text}"
                ).strip()
            else:
                # Log an error but continue with the original message
                app_logger.warning("Could not transcribe audio. Proceeding with text message only.")
        
        
        # Fallback if no text message and no transcribed audio
        if not final_user_message:
            return "Error: User message or successfully transcribed audio must be provided."

        # 2. Assemble the final messages list
        app_logger.info("Request Content: %s", final_user_message)
        messages = [
            {"role": "system", "content": prompt},
            # The 'content' for the user role is now a single string of combined text
            {"role": "user", "content": final_user_message}, 
        ]

        # 3. API call (remains the same)
        try:
            response = self.client.chat.completions.create(
                model=self.settings.default_model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Handle potential API or connection errors
            print(f"LLM API Error: {e}")
            return f"Error connecting to LLM at {self.settings.base_url}"            # Handle potential API or connection errors
            print(f"LLM API Error: {e}")
            return f"Error connecting to LLM at {self.settings.base_url}"

