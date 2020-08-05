"""Entry point for gunicorn wsgi server. Calls the actual webapplication"""
from .webapplication import app

if __name__ == "__main__":
    app.run()
