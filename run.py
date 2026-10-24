# Copyright (c) 2026 Naman-devio
# Licensed under the MIT License.
# KittuBot Render Web Service entry point.

import threading
from health_server import start_health_server
from KITTUBOT.__main__ import main


if __name__ == "__main__":
    # Render requires a web process listening on 0.0.0.0:$PORT.
    # Run the HTTP health server in a daemon thread so Telegram polling
    # can continue in the main thread without changing the bot lifecycle.
    start_health_server()
    main()
