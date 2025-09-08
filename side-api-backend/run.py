# run.py

import uvicorn
from configuration.configuration_settings import (
    MODULE_NAME,
    APP_NAME,
    HOST,
    PORT,
    RELOAD,
)

if __name__ == "__main__":
    # Costruisco il path corretto "modulo:attributo"
    app_location = f"{MODULE_NAME}:{APP_NAME}"

    uvicorn.run(app_location, host=HOST, port=PORT, reload=RELOAD)
