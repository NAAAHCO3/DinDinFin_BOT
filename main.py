import os
import logging
from threading import Thread
from flask import Flask, jsonify
from app import start_bot

# ============================
# LOGGING
# ============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("DinDinFin")


# ============================
# FLASK APP (Health Check)
# ============================
app = Flask(__name__)


@app.route("/", methods=["GET"])
def health_check():
    """
    Endpoint exigido pelo Cloud Run para verificar
    se o container está saudável.
    """
    return jsonify(
        status="ok",
        service="DinDinFinBOT"
    ), 200


def run_flask():
    """Roda o Flask em thread separada"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Iniciando Flask (health check) na porta {port}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


# ============================
# ENTRYPOINT
# ============================
if __name__ == "__main__":
    # 1️⃣ Flask em background (Cloud Run precisa disso)
    flask_thread = Thread(
        target=run_flask,
        name="FlaskThread",
        daemon=True
    )
    flask_thread.start()

    # 2️⃣ Bot na thread principal (OBRIGATÓRIO)
    try:
        logger.info("🚀 Iniciando Telegram Bot (thread principal)")
        start_bot()

    except KeyboardInterrupt:
        logger.info("⛔ Encerramento manual detectado")

    except Exception as e:
        logger.exception("🔥 Erro fatal no bot")

    finally:
        logger.info("🛑 Processo finalizado")
