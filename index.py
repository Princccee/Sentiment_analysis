import os
from backend.app import app

if __name__ == "__main__":
    # Use environment variable for port, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_ENV") == "development", port=port)
