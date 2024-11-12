import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "trading_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Import trading components
from trading.oanda_client import OandaClient
from trading.lorentzian import LorentzianClassifier
from trading.risk_manager import RiskManager
from trading.technical_indicators import TechnicalIndicators

# Initialize performance tracking
performance_history = {
    'dates': [],
    'balances': []
}

@app.route('/')
def dashboard():
    """Main dashboard route"""
    try:
        oanda_client = OandaClient()  # Create new instance for each request
        trades = oanda_client.get_open_trades()
        account_info = oanda_client.get_account_info()
        return render_template('dashboard.html', 
                            trades=trades or [],
                            account_info=account_info or {'balance': 0, 'unrealizedPL': 0, 'marginUsed': 0})
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html',
                            trades=[],
                            account_info={'balance': 0, 'unrealizedPL': 0, 'marginUsed': 0})

with app.app_context():
    import models
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
