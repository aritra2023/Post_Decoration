from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "telegram_bot"}

def run():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logging.error(f"Keep alive server error: {e}")

def keep_alive():
    """Start the keep alive server in a separate thread"""
    try:
        t = Thread(target=run)
        t.daemon = True
        t.start()
        logging.info("Keep alive server started on port 5000")
    except Exception as e:
        logging.error(f"Failed to start keep alive server: {e}")
