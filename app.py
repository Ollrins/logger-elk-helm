import json
import logging
import os
import random
import sys
import time
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)


class JsonFormatter(logging.Formatter):
    """Форматирует логи в JSON — чтобы ELK парсил их без Grok."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "@timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "logger-elk",
            "host": os.uname().nodename,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("logger-elk")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@app.route("/")
def index():
    logger.info("Health check OK")
    return jsonify({"status": "ok", "service": "logger-elk"})


@app.route("/order/<int:order_id>")
def order(order_id: int):
    user_id = request.args.get("user_id", "unknown")
    logger.info(f"Processing order {order_id} for user {user_id}")
    time.sleep(0.1)
    logger.info(f"Order {order_id} completed")
    return jsonify({"order_id": order_id, "status": "completed"})


@app.route("/error")
def error():
    logger.error("Simulated error: database connection failed")
    return jsonify({"error": "internal server error"}), 500


@app.route("/warning")
def warning():
    logger.warning("High memory usage detected: 85%")
    return jsonify({"status": "warned"})


@app.route("/slow")
def slow():
    delay = random.uniform(2, 5)
    logger.info(f"Slow request started, delay {delay:.2f}s")
    time.sleep(delay)
    logger.warning(f"Slow request finished in {delay:.2f}s (threshold 1s)")
    return jsonify({"delay": delay})


@app.route("/crash")
def crash():
    try:
        1 / 0
    except ZeroDivisionError as exc:
        logger.exception(f"Unhandled exception: {exc}")
    return jsonify({"error": "crashed"}), 500


@app.route("/random")
def random_endpoint():
    r = random.random()
    if r < 0.6:
        logger.info("Random request OK")
        return jsonify({"result": "ok"})
    if r < 0.85:
        logger.warning("Random request warning: cache miss")
        return jsonify({"result": "warn"}), 200
    logger.error("Random request error: upstream timeout")
    return jsonify({"result": "error"}), 500


if __name__ == "__main__":
    logger.info("Starting logger-elk on port 8000")
    app.run(host="0.0.0.0", port=8000)
