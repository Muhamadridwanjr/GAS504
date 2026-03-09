from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class StrategyCondition(BaseModel):
    type: str  # indicator, smc, price, market_structure, macro, etc
    name: Optional[str] = None
    period: Optional[int] = None
    operator: Optional[str] = None
    value: Optional[Union[float, int, str]] = None
    direction: Optional[str] = None
    lookback: Optional[int] = None
    timeframe: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None
    position: Optional[str] = None
    assets: Optional[List[str]] = None

class StopLossConfig(BaseModel):
    type: str
    source: Optional[str] = None
    logic: Optional[List[str]] = None
    offset: Optional[float] = 0.0
    offset_points: Optional[float] = 0.0
    atr_multiplier: Optional[float] = 0.0

class TargetLevel(BaseModel):
    level: str
    portion: float

class TakeProfitConfig(BaseModel):
    type: str
    source: Optional[str] = None
    targets: Optional[List[TargetLevel]] = None
    risk_reward_ratio: Optional[float] = None

class SessionFilter(BaseModel):
    enabled: bool = False
    sessions: Optional[List[str]] = None
    avoid_sessions: Optional[List[str]] = None
    killzone: Optional[List[str]] = None

class RiskManagement(BaseModel):
    risk_per_trade: Optional[float] = 1.0
    max_trades_per_day: Optional[int] = None
    max_open_positions: Optional[int] = None
    max_sector_exposure: Optional[float] = None
    max_drawdown: Optional[float] = None
    session_stop_after_loss: Optional[int] = None

class SellConditions(BaseModel):
    invert_all: bool = False

class ExtraFilter(BaseModel):
    type: str
    max_spread: Optional[float] = None
    avoid_high_impact: Optional[bool] = None
    min_volume_threshold: Optional[str] = None
    min_atr: Optional[bool] = None

class AIOutputConfig(BaseModel):
    include_summary: bool = False
    include_session: bool = False
    include_killzone: bool = False
    include_pivots: bool = False
    include_liquidity: bool = False
    include_htf_bias: bool = False
    include_macro_bias: bool = False
    include_structure: bool = False
    include_targets: bool = False
    include_liquidity_zones: bool = False
    include_multi_tf_bias: bool = False

class StrategyModel(BaseModel):
    name: str
    version: str
    description: str = ""
    author: Optional[str] = None
    timeframes: List[str] = []
    
    # Assets can now be completely flat OR grouped categorically
    assets: Union[List[str], Dict[str, List[str]]] = []
    
    # Split engines
    trend_conditions: Optional[List[StrategyCondition]] = None
    smc_conditions: Optional[List[StrategyCondition]] = None
    liquidity_conditions: Optional[List[StrategyCondition]] = None
    poi_conditions: Optional[List[StrategyCondition]] = None
    momentum_conditions: Optional[List[StrategyCondition]] = None
    correlation_conditions: Optional[List[StrategyCondition]] = None
    entry_trigger: Optional[List[StrategyCondition]] = None
    
    # Backwards compatibility
    entry_conditions: Optional[List[StrategyCondition]] = None
    
    combination: str = "AND"
    action: str = "BUY"
    
    stop_loss: Optional[StopLossConfig] = None
    take_profit: Optional[TakeProfitConfig] = None
    
    session_filter: Optional[SessionFilter] = None
    risk_management: Optional[RiskManagement] = None
    sell_conditions: Optional[SellConditions] = None
    filters: Optional[List[ExtraFilter]] = None
    ai_output: Optional[AIOutputConfig] = None
    
    @property
    def all_conditions(self) -> List[StrategyCondition]:
        """Combine all the split out engine conditions for simple evaluation"""
        conds = []
        if self.entry_conditions: conds.extend(self.entry_conditions)
        if self.trend_conditions: conds.extend(self.trend_conditions)
        if self.smc_conditions: conds.extend(self.smc_conditions)
        if self.liquidity_conditions: conds.extend(self.liquidity_conditions)
        if self.poi_conditions: conds.extend(self.poi_conditions)
        if self.momentum_conditions: conds.extend(self.momentum_conditions)
        if self.correlation_conditions: conds.extend(self.correlation_conditions)
        if self.entry_trigger: conds.extend(self.entry_trigger)
        return conds
