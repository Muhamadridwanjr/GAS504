import pandas as pd
from typing import Dict, Any, List
from src.api.models import StrategyConfig

class Simulator:
    def __init__(self, initial_capital: float, commission: float, slippage: float):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.position = 0 # 0 = flat, 1 = long, -1 = short
        self.entry_price = 0.0
        self.entry_time = None
        self.trades = []
        self.equity_curve = []
        
        self.equity_curve.append({"time": 0, "equity": self.initial_capital}) # T0 element, updated in run
        
    def execute(self, df: pd.DataFrame, strategy: StrategyConfig) -> tuple[List[Dict], List[Dict]]:
        # A very simplified simulator for demonstration
        # Assumes df has technical indicators pre-calculated by feature_engine
        
        # In this stub we just assume the dataframe has standard fields + RSI as an example to match the rule
        if "rsi_14" not in df.columns:
            # mock it up
            df['rsi_14'] = 50.0
            
        for index, row in df.iterrows():
            current_time = row['time'].timestamp() if hasattr(row['time'], 'timestamp') else index
            current_price = row['close']
            
            # Record Equity
            unrealized_pnl = 0
            if self.position == 1:
                unrealized_pnl = (current_price - self.entry_price) * strategy.position_size * self.initial_capital / self.entry_price
            elif self.position == -1:
                unrealized_pnl = (self.entry_price - current_price) * strategy.position_size * self.initial_capital / self.entry_price
            
            self.equity_curve.append({"time": current_time, "equity": self.capital + unrealized_pnl})
            
            # Determine Signals (Mocking rule evaluation for speed)
            signal = "NEUTRAL"
            if row.get('rsi_14', 50) < 30:
                signal = "BUY"
            elif row.get('rsi_14', 50) > 70:
                signal = "SELL"
                
            # Execute logic
            if self.position == 0:
                if signal == "BUY":
                    self._enter(1, current_price, current_time)
                elif signal == "SELL":
                    self._enter(-1, current_price, current_time)
            elif self.position == 1:
                # Check exit
                if signal == "SELL" or (current_price <= self.entry_price - strategy.stop_loss) or (current_price >= self.entry_price + strategy.take_profit):
                    self._exit(current_price, current_time)
            elif self.position == -1:
                # Check exit
                if signal == "BUY" or (current_price >= self.entry_price + strategy.stop_loss) or (current_price <= self.entry_price - strategy.take_profit):
                    self._exit(current_price, current_time)
                    
        # Close any open positions at the end
        if self.position != 0:
            self._exit(df.iloc[-1]['close'], df.iloc[-1]['time'].timestamp() if hasattr(df.iloc[-1]['time'], 'timestamp') else len(df)-1)
            
        return self.trades, self.equity_curve
        
    def _enter(self, direction: int, price: float, time: float):
        exec_price = price * (1 + self.slippage) if direction == 1 else price * (1 - self.slippage)
        self.position = direction
        self.entry_price = exec_price
        self.entry_time = time
        
        # Deduct commision from capital
        self.capital -= self.capital * self.commission
        
    def _exit(self, price: float, time: float):
        exec_price = price * (1 - self.slippage) if self.position == 1 else price * (1 + self.slippage)
        
        if self.position == 1:
            pnl_pct = (exec_price - self.entry_price) / self.entry_price
        else:
            pnl_pct = (self.entry_price - exec_price) / self.entry_price
            
        # Hardcoding bet size ratio 1.0 for simplicity in stub
        pnl_abs = self.capital * pnl_pct
        
        self.capital += pnl_abs
        self.capital -= self.capital * self.commission
        
        self.trades.append({
            "entry_time": self.entry_time,
            "exit_time": time,
            "action": "BUY" if self.position == 1 else "SELL",
            "entry_price": self.entry_price,
            "exit_price": exec_price,
            "pnl": pnl_abs,
            "pnl_percent": pnl_pct
        })
        
        self.position = 0
        self.entry_price = 0.0
        self.entry_time = None
