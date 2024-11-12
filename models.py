from app import db
from datetime import datetime

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oanda_trade_id = db.Column(db.String(50), unique=True)
    instrument = db.Column(db.String(10))
    units = db.Column(db.Float)
    entry_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    direction = db.Column(db.String(10))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    pnl = db.Column(db.Float)

class TradingMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    win_count = db.Column(db.Integer, default=0)
    loss_count = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Float, default=0)
    max_drawdown = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
