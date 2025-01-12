import os
from backend.app import app

if __name__ == "__main__":
    # Read the port from the environment variable, default to 5001 if not set
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)