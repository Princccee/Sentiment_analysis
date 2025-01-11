from backend.app import app

if __name__ == "__main__":
    app.run(debug=True)
# This file is the entry point for the WSGI server. It imports the Flask app instance from backend/app.py and runs the app with debug mode enabled. This file is used to start the Flask server when deploying the application.