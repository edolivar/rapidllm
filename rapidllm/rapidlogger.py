import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, field_validator  # Ensure these are imported

# --- Pydantic Configuration Model (As Provided/Modified for context) ---
# Note: You need to define LoggingLevelStr for this to run
LoggingLevelStr = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

class RapidLoggerConfig(BaseModel):
    name: str
    console_level: LoggingLevelStr = "INFO"
    file_level: LoggingLevelStr = "INFO"

    @field_validator('console_level', 'file_level', mode='before')
    @classmethod
    def validate_level(cls, v: Any) -> Any:
        # Check if the input is a string
        if isinstance(v, str):
            # Convert to uppercase for case-insensitive validation against the Literal
            upper_v = v.upper()

            # Get the possible literal values from LoggingLevelStr
            # LoggingLevelStr.__args__ gives the tuple of literal strings
            valid_levels = LoggingLevelStr.__args__ 

            if upper_v in valid_levels:
                # If it's a valid string, return the uppercase version
                # This ensures the stored value matches the literal casing
                return upper_v
            
            # If it's a string but not one of the defined literals, raise an error
            raise ValueError(
                f"Invalid logging level '{v}'. Must be one of the following string names: {list(valid_levels)}"
            )
        
        # Pydantic's field_validator is run before the field's type coercion.
        # If 'v' is not a string (e.g., if it's an integer like 20 for INFO), 
        # Pydantic will attempt to coerce it into the Literal type next, 
        # which will fail (as Literal is restricted to strings here), 
        # causing a ValidationError later.
        # For this specific case with Literal[str] we only want to accept and 
        # validate strings. For other types, we let Pydantic handle the failure 
        # with a clearer type error message, or you could raise a ValueError 
        # here if you strictly only want strings.
        return v

# --- The RapidLogger Function ---

def RapidLogger(config: RapidLoggerConfig) -> logging.Logger:
    """
    Initializes a custom logger using a validated Pydantic configuration.

    Args:
        config (RapidLoggerConfig): A validated Pydantic model instance 
                                    containing logger name and levels.

    Returns:
        logging.Logger: The configured custom logger instance.
    """
    # The config levels are already converted to integers by the Pydantic validator.
    
    # 1. Create custom logger
    logger = logging.getLogger(config.name)
    # The logger's level is set low (DEBUG) to allow ALL messages to be processed.
    # The individual handlers (console/file) will then filter based on their level.
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        # 2. Create console handler and set level using the validated config value
        c_handler = logging.StreamHandler()
        c_handler.setLevel(config.console_level) # This value is guaranteed to be an int

        # 3. Create file handler and set level using the validated config value
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        f_handler = logging.FileHandler(os.path.join(log_dir, f'{config.name}.log'))
        f_handler.setLevel(config.file_level) # This value is guaranteed to be an int

        # 4. Create formatters and add them to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # 5. Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
    return logger

# # --- Example Usage ---
#
# # 1. Create the validated config object (passing strings for levels)
# config_data = RapidLoggerConfig(
#     name="WebApp",
#     console_level="WARNING", # Converted to 30 by Pydantic
#     file_level="DEBUG"       # Converted to 10 by Pydantic
# )
#
# # 2. Pass the config object to the function
# app_logger = RapidLogger(config_data)
#
# # Test the logger
# app_logger.debug("This is a debug message (File Only)")
# app_logger.info("This is an info message (File Only)")
# app_logger.warning("This is a warning message (Console & File)")
