import numpy as np
import pandas as pd
from typing import Dict, List, Any

def calculate_metrics(trades: List[Dict[str, Any]], equity_curve: List[Dict[str, float]], initial_capital: float) -> Dict[str, Any]:
    if not trades:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0
        }
    
    # Win Rate
    winning_trades = [t for t in trades if t['pnl'] > 0]
    win_rate = len(winning_trades) / len(trades)
    
    # Profit Factor
    gross_profit = sum(t['pnl'] for t in winning_trades)
    gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    
    # Returns
    final_equity = equity_curve[-1]['equity'] if equity_curve else initial_capital
    total_return = (final_equity - initial_capital) / initial_capital
    
    # Assuming approx 1 year for annualized, normally this uses timestamps
    # For a stub, we'll rough it:
    annualized_return = total_return # stub
    
    # Eq Curve df
    df = pd.DataFrame(equity_curve)
    
    if not df.empty and len(df) > 1:
        # Drawdown
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['peak'] - df['equity']) / df['peak']
        max_drawdown = float(df['drawdown'].max())
        
        # Sharpe (simplified, assumed daily equiv frequency)
        df['returns'] = df['equity'].pct_change()
        mean_ret = df['returns'].mean()
        std_ret = df['returns'].std()
        
        # very rough approximation, assuming hourly data
        sharpe_ratio = (mean_ret / std_ret) * np.sqrt(252 * 24) if std_ret > 0 else 0.0
    else:
        max_drawdown = 0.0
        sharpe_ratio = 0.0
        
    return {
        "total_return": float(total_return),
        "annualized_return": float(annualized_return),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": float(max_drawdown),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "total_trades": len(trades)
    }
