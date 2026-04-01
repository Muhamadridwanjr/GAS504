//+------------------------------------------------------------------+
//|                    GAS_StrategyScanner_v5.mq5                    |
//|       GAS Strategy EA PRO + Multi-Symbol Scanner                 |
//|       Muhamad RidwanJr — Based on GASSTRATEGYEAPRO v4.0          |
//|       v5.0 — Multi-Symbol Tick & OHLCV Scanner                   |
//|       1 EA di 1 Chart = SCAN SEMUA PAIR EXNESS                   |
//+------------------------------------------------------------------+
//  CHANGELOG v5.0:
//  [+] SECTION 3B — Input scanner multi-symbol
//  [+] SECTION 5B — Global vars scanner
//  [+] SECTION 17 — Scanner engine:
//        GetSymbolList()         → ambil semua pair dari Market Watch
//        ScanAndSendMultiTick()  → kirim current bid/ask SEMUA pair
//        ScanAndSendMultiOHLC()  → kirim OHLCV SEMUA pair per timeframe
//        GetSymbolCategory()     → kategorisasi Forex/Commodity/Index/Stock
//  [!] Semua kode v4.0 asli TIDAK DIUBAH
//+------------------------------------------------------------------+
#property copyright "GAS Strategy — Muhamad RidwanJr"
#property version   "5.00"
#property strict

//====================================================================
//  SECTION 1: INCLUDES
//====================================================================
#include <Trade/Trade.mqh>
#include <Trade/PositionInfo.mqh>
#include <Trade/AccountInfo.mqh>

CTrade         trade;
CPositionInfo  posInfo;
CAccountInfo   accInfo;

//====================================================================
//  SECTION 2: INPUT PARAMETERS — ORIGINAL v3.1 (TIDAK DIUBAH)
//====================================================================
input string   GatewayURL           = "https://gasstrategyai.xyz";
input int      MagicNumber           = 77705;
input double   MaxSpreadPoints       = 5000;
input double   RiskPercent           = 1.0;
input double   MaxDailyDrawdown      = 4.0;
input int      TrailingStop          = 50;

// Signal polling
input bool     EnableSignalPolling   = false;
input int      SignalPollingInterval = 1;

// Order execution
input bool     EnableOrderExecution  = true;
input int      OrderPollingInterval  = 1;

// Tick data (chart symbol only)
input bool     SendTickData          = true;
input int      TickSendInterval      = 1;
input int      MaxTicksPerBatch      = 100;

// OHLC data (chart symbol only)
input bool     SendOHLCData          = false;
input int      OHLCSendInterval      = 60;
input string   OHLCPeriods           = "M1,M5,M15,H1,H4,D1";

// Heartbeat
input bool     EnableHeartbeat       = true;
input int      HeartbeatInterval     = 60;

// WebRequest
input int      WebRequestTimeout     = 3000;
input int      MaxRetries            = 2;

//====================================================================
//  SECTION 3: INPUT PARAMETERS — GAS PRO v4.0 (TIDAK DIUBAH)
//====================================================================

input string   GAS_TraderName        = "Muhamad RidwanJr";
input string   GAS_Broker            = "Exness Zero Spread";
input int      GAS_Leverage          = 1000;
input double   GAS_DepositIDR        = 10000000.0;
input string   GAS_Style             = "Hybrid Scalping-Intraday";
input string   GAS_Strategy          = "ICT+SMC+PAC";

input double   GAS_MaxDailyLossIDR   = 600000.0;
input int      GAS_MaxTradesPerDay   = 10;
input double   GAS_FixedLot          = 0.01;
input int      GAS_MoveBEPoints      = 300;
input double   GAS_PartialClosePct   = 50.0;
input int      GAS_ConsecutiveLoss   = 3;
input int      GAS_PauseHours        = 5;
input bool     GAS_NoLayering        = true;
input double   GAS_USDtoIDR          = 16000.0;

input bool     GAS_EnableContextPush = true;
input int      GAS_ContextInterval   = 30;
input string   GAS_ContextEndpoint   = "/api/gas/context";

input bool     GAS_EnableSignalReq   = false;
input int      GAS_SignalReqInterval = 5;
input string   GAS_SignalReqEndpoint = "/api/gas/signal/request";
input string   GAS_SignalResEndpoint = "/api/gas/signal/latest";
input bool     GAS_AutoExecAISignal  = false;

input bool     GAS_EnableJournal     = true;
input string   GAS_JournalEndpoint   = "/api/gas/journal";

//====================================================================
//  SECTION 3B: INPUT PARAMETERS — SCANNER v5.0 (BARU)
//====================================================================

input string   SCANNER_SEPARATOR     = "=== SCANNER SETTINGS ==="; // ──────────────────

// Toggle scanner
input bool     EnableScanner         = true;        // Aktifkan scanner semua pair?
input bool     ScanMarketWatchOnly   = true;        // true=Market Watch, false=Semua broker

// Tick snapshot — current bid/ask semua pair
input int      ScanTickInterval      = 5;           // Seberapa sering kirim tick snapshot (detik)

// OHLCV scanner — latest bars semua pair
input bool     ScanSendOHLC          = true;        // Kirim OHLCV semua pair?
input int      ScanOHLCInterval      = 60;          // Interval kirim OHLCV (detik)
input string   ScanOHLCTimeframes    = "M1,M5,M15,H1"; // Timeframes yang di-scan
input int      ScanOHLCBarsPerSymbol = 3;           // Jumlah bar per symbol per TF

// Filter
input bool     SkipSpreadsOver       = false;       // Skip pair dengan spread terlalu besar?
input double   MaxScanSpread         = 200;         // Max spread poin untuk di-scan (0=off)

//====================================================================
//  SECTION 4: GLOBAL VARIABLES — ORIGINAL v3.1
//====================================================================
double initialBalanceDaily;
string lastSignalID  = "";
string lastOrderID   = "";

struct TickData
{
   double time;
   double bid;
   double ask;
   long   volume;
};
TickData tickBuffer[];
int tickCount = 0;

datetime lastSignalPollTime  = 0;
datetime lastOrderPollTime   = 0;
datetime lastTickSendTime    = 0;
datetime lastHeartbeatTime   = 0;
datetime lastOHLCSendTime    = 0;

//====================================================================
//  SECTION 5: GLOBAL VARIABLES — GAS PRO v4.0
//====================================================================

int      gas_DailyTradeCount     = 0;
double   gas_DailyPnLUSD         = 0.0;
datetime gas_LastTradeDate       = 0;

int      gas_ConsecutiveLossCount = 0;
datetime gas_PauseUntilTime       = 0;
bool     gas_IsPaused             = false;

ulong    gas_BEDoneTickets[50];
int      gas_BEDoneCount     = 0;
ulong    gas_PartialDoneTickets[50];
int      gas_PartialDoneCount = 0;

datetime gas_LastContextSendTime = 0;
datetime gas_LastSignalReqTime   = 0;

string   gas_LastAISignalID = "";
datetime gas_LastDealTime   = 0;

struct TP1Track
{
   ulong  ticket;
   double tp1;
   bool   partialDone;
   bool   beDone;
};
TP1Track gas_TP1Tracker[50];
int      gas_TP1Count = 0;

//====================================================================
//  SECTION 5B: GLOBAL VARIABLES — SCANNER v5.0 (BARU)
//====================================================================

datetime scan_LastTickSendTime = 0;
datetime scan_LastOHLCSendTime = 0;
int      scan_TotalSymbols     = 0;   // Update di OnInit

//====================================================================
//  SECTION 6: OnInit
//====================================================================
int OnInit()
{
   trade.SetExpertMagicNumber(MagicNumber);
   EventSetTimer(1);

   initialBalanceDaily = accInfo.Balance();
   gas_DailyTradeCount = 0;
   gas_DailyPnLUSD     = 0.0;
   gas_LastTradeDate   = iTime(_Symbol, PERIOD_D1, 0);

   Print("🚀 GAS StrategyScanner v5.0 | Trader: ", GAS_TraderName);
   Print("📊 Chart: ", _Symbol, " | Broker: ", GAS_Broker);

   // Hitung symbol count
   if(EnableScanner)
   {
      string syms[];
      scan_TotalSymbols = GetSymbolList(syms);
      Print("🔍 Scanner aktif | Total symbols: ", scan_TotalSymbols,
            " | Market Watch only: ", ScanMarketWatchOnly ? "YES" : "NO");
      Print("⏱ Tick interval: ", ScanTickInterval, "s | OHLC interval: ", ScanOHLCInterval, "s");
      Print("📈 OHLC Timeframes: ", ScanOHLCTimeframes);
   }

   if(GAS_EnableContextPush)
      SendGASContext();

   return(INIT_SUCCEEDED);
}

//====================================================================
//  SECTION 7: OnDeinit
//====================================================================
void OnDeinit(const int reason)
{
   EventKillTimer();
}

//====================================================================
//  SECTION 8: OnTimer — ORIGINAL + GAS PRO + SCANNER
//====================================================================
void OnTimer()
{
   datetime now = TimeCurrent();

   // --- Reset daily ---
   GAS_CheckDailyReset();

   // --- Unpause ---
   if(gas_IsPaused && now >= gas_PauseUntilTime)
   {
      gas_IsPaused = false;
      gas_ConsecutiveLossCount = 0;
      Print("✅ Pause selesai. Jam: ", TimeToString(now));
   }

   // --- GAS PRO Rules ---
   GAS_CheckMaxDailyLossIDR();
   if(GAS_MoveBEPoints > 0)      GAS_CheckMoveBreakeven();
   if(GAS_PartialClosePct > 0)   GAS_CheckPartialClose();

   // 1. Signal polling (chart symbol)
   if(EnableSignalPolling && now - lastSignalPollTime >= SignalPollingInterval)
   { lastSignalPollTime = now; if(!gas_IsPaused) PollSignal(); }

   // 2. Order queue (chart symbol)
   if(EnableOrderExecution && now - lastOrderPollTime >= OrderPollingInterval)
   { lastOrderPollTime = now; if(!gas_IsPaused) PollOrderQueue(); }

   // 3. Tick batch (chart symbol — high frequency via OnTick)
   if(SendTickData && now - lastTickSendTime >= TickSendInterval)
   { lastTickSendTime = now; SendTickBatch(); }

   // 4. OHLC (chart symbol)
   if(SendOHLCData && now - lastOHLCSendTime >= OHLCSendInterval)
   { lastOHLCSendTime = now; SendOHLCBatch(); }

   // 5. Heartbeat
   if(EnableHeartbeat && now - lastHeartbeatTime >= HeartbeatInterval)
   { lastHeartbeatTime = now; SendHeartbeat(); }

   // 6. Trailing stop
   if(TrailingStop > 0) TrailingStops();

   // 7. Drawdown check
   CheckDailyDrawdown();

   // 8. GAS Context Push
   if(GAS_EnableContextPush && now - gas_LastContextSendTime >= GAS_ContextInterval)
   { gas_LastContextSendTime = now; SendGASContext(); }

   // 9. GAS Signal Request
   if(GAS_EnableSignalReq && !gas_IsPaused &&
      now - gas_LastSignalReqTime >= GAS_SignalReqInterval)
   { gas_LastSignalReqTime = now; if(GAS_CheckCanTrade()) RequestGASSignal(); }

   // ─────────────────────────────────────────────────────
   // SECTION 8B — SCANNER TASKS (BARU v5.0)
   // ─────────────────────────────────────────────────────

   // 10. Multi-Symbol Tick Snapshot (semua pair)
   if(EnableScanner && now - scan_LastTickSendTime >= ScanTickInterval)
   {
      scan_LastTickSendTime = now;
      ScanAndSendMultiTick();
   }

   // 11. Multi-Symbol OHLCV (semua pair, per timeframe)
   if(EnableScanner && ScanSendOHLC && now - scan_LastOHLCSendTime >= ScanOHLCInterval)
   {
      scan_LastOHLCSendTime = now;
      ScanAndSendMultiOHLC();
   }
}

//====================================================================
//  SECTION 9: OnTick — chart symbol high-frequency tick capture
//====================================================================
void OnTick()
{
   if(!SendTickData) return;

   TickData tick;
   tick.time   = (double)TimeCurrent();
   tick.bid    = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   tick.ask    = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   tick.volume = 0;

   int size = ArraySize(tickBuffer);
   if(tickCount >= size)
      ArrayResize(tickBuffer, size + 100, 100);

   tickBuffer[tickCount] = tick;
   tickCount++;

   if(tickCount >= MaxTicksPerBatch)
      SendTickBatch();
}

//====================================================================
//  SECTION 10: OnTradeTransaction (TIDAK DIUBAH)
//====================================================================
void OnTradeTransaction(
   const MqlTradeTransaction& trans,
   const MqlTradeRequest&     request,
   const MqlTradeResult&      result)
{
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD) return;

   ulong dealTicket = trans.deal;
   if(dealTicket == 0) return;
   if(!HistoryDealSelect(dealTicket)) return;

   long dealMagic = HistoryDealGetInteger(dealTicket, DEAL_MAGIC);
   if(dealMagic != MagicNumber) return;

   ENUM_DEAL_ENTRY dealEntry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(dealTicket, DEAL_ENTRY);
   if(dealEntry != DEAL_ENTRY_OUT) return;

   double profit    = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
   double profitIDR = profit * GAS_USDtoIDR;

   gas_DailyTradeCount++;
   gas_DailyPnLUSD += profit;

   Print("📝 Trade closed | Profit: $", DoubleToString(profit, 2),
         " (Rp ", DoubleToString(profitIDR, 0), ")",
         " | Daily: ", gas_DailyTradeCount, "/", GAS_MaxTradesPerDay);

   if(profit < 0.0)
   {
      gas_ConsecutiveLossCount++;
      Print("⚠️ Loss ke-", gas_ConsecutiveLossCount);

      if(gas_ConsecutiveLossCount >= GAS_ConsecutiveLoss)
      {
         gas_IsPaused       = true;
         gas_PauseUntilTime = TimeCurrent() + (GAS_PauseHours * 3600);
         Print("🛑 PAUSE sampai: ", TimeToString(gas_PauseUntilTime));
         CloseAllPositions();
         GAS_SendPauseNotification();
      }
   }
   else
      gas_ConsecutiveLossCount = 0;

   if(GAS_EnableJournal)
      GAS_SendTradeJournal(dealTicket);
}

//====================================================================
//  SECTION 11: GAS PRO RULES (TIDAK DIUBAH)
//====================================================================
bool GAS_CheckCanTrade()
{
   if(gas_IsPaused) { Print("⏸️ Pause hingga: ", TimeToString(gas_PauseUntilTime)); return false; }
   if(gas_DailyTradeCount >= GAS_MaxTradesPerDay) { Print("🚫 Max trades/hari"); return false; }
   if(GAS_NoLayering && PositionsTotal() > 0)
   {
      for(int i = 0; i < PositionsTotal(); i++)
         if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber && posInfo.Symbol() == _Symbol)
         { Print("🚫 No layering: ada posisi aktif"); return false; }
   }
   return true;
}

void GAS_CheckMoveBreakeven()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point == 0) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!posInfo.SelectByIndex(i)) continue;
      if(posInfo.Magic() != MagicNumber || posInfo.Symbol() != _Symbol) continue;
      ulong ticket = posInfo.Ticket();
      if(GAS_IsTicketInArray(ticket, gas_BEDoneTickets, gas_BEDoneCount)) continue;
      double openPrice = posInfo.PriceOpen();
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(posInfo.PositionType() == POSITION_TYPE_BUY)
      {
         if((bid - openPrice) / point >= GAS_MoveBEPoints && posInfo.StopLoss() < openPrice)
         {
            if(trade.PositionModify(ticket, openPrice + 2*point, posInfo.TakeProfit()))
            { Print("✅ BE moved Buy | Ticket:", ticket); if(gas_BEDoneCount<50) gas_BEDoneTickets[gas_BEDoneCount++]=ticket; }
         }
      }
      else if(posInfo.PositionType() == POSITION_TYPE_SELL)
      {
         if((openPrice - ask) / point >= GAS_MoveBEPoints && (posInfo.StopLoss() > openPrice || posInfo.StopLoss() == 0))
         {
            if(trade.PositionModify(ticket, openPrice - 2*point, posInfo.TakeProfit()))
            { Print("✅ BE moved Sell | Ticket:", ticket); if(gas_BEDoneCount<50) gas_BEDoneTickets[gas_BEDoneCount++]=ticket; }
         }
      }
   }
}

void GAS_CheckPartialClose()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point == 0) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!posInfo.SelectByIndex(i)) continue;
      if(posInfo.Magic() != MagicNumber || posInfo.Symbol() != _Symbol) continue;
      ulong  ticket   = posInfo.Ticket();
      double openPrice = posInfo.PriceOpen();
      double tp = posInfo.TakeProfit();
      double volume = posInfo.Volume();
      if(tp == 0) continue;
      if(GAS_IsTicketInArray(ticket, gas_PartialDoneTickets, gas_PartialDoneCount)) continue;
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double closeVol, minVol;
      if(posInfo.PositionType() == POSITION_TYPE_BUY)
      {
         double tp1 = openPrice + (tp - openPrice) * 0.5;
         if(bid >= tp1)
         {
            closeVol = NormalizeDouble(volume * GAS_PartialClosePct / 100.0, 2);
            minVol   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(closeVol < minVol) closeVol = minVol;
            if(trade.PositionClosePartial(ticket, closeVol))
            { Print("✅ Partial BUY | Ticket:", ticket, " Vol:", closeVol); if(gas_PartialDoneCount<50) gas_PartialDoneTickets[gas_PartialDoneCount++]=ticket; }
         }
      }
      else if(posInfo.PositionType() == POSITION_TYPE_SELL)
      {
         double tp1 = openPrice - (openPrice - tp) * 0.5;
         if(ask <= tp1)
         {
            closeVol = NormalizeDouble(volume * GAS_PartialClosePct / 100.0, 2);
            minVol   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(closeVol < minVol) closeVol = minVol;
            if(trade.PositionClosePartial(ticket, closeVol))
            { Print("✅ Partial SELL | Ticket:", ticket, " Vol:", closeVol); if(gas_PartialDoneCount<50) gas_PartialDoneTickets[gas_PartialDoneCount++]=ticket; }
         }
      }
   }
}

void GAS_CheckMaxDailyLossIDR()
{
   double dailyPnL_IDR = (accInfo.Balance() - initialBalanceDaily) * GAS_USDtoIDR;
   if(dailyPnL_IDR <= -GAS_MaxDailyLossIDR)
   {
      Print("🛑 MAX DAILY LOSS IDR: Rp", DoubleToString(MathAbs(dailyPnL_IDR), 0));
      CloseAllPositions();
      gas_IsPaused       = true;
      gas_PauseUntilTime = iTime(_Symbol, PERIOD_D1, 0) + 86400;
      GAS_SendPauseNotification();
   }
}

void GAS_CheckDailyReset()
{
   datetime todayOpen = iTime(_Symbol, PERIOD_D1, 0);
   if(todayOpen != gas_LastTradeDate)
   {
      gas_LastTradeDate   = todayOpen;
      gas_DailyTradeCount = 0;
      gas_DailyPnLUSD     = 0.0;
      initialBalanceDaily = accInfo.Balance();
      Print("🔄 Daily reset: ", TimeToString(todayOpen));
   }
}

bool GAS_IsTicketInArray(ulong ticket, ulong& arr[], int count)
{
   for(int i = 0; i < count; i++) if(arr[i] == ticket) return true;
   return false;
}

//====================================================================
//  SECTION 12: CONTEXT PUSH (TIDAK DIUBAH)
//====================================================================
void SendGASContext()
{
   string json = BuildGASContextJSON();
   string url  = GatewayURL + GAS_ContextEndpoint;
   for(int r = 0; r < MaxRetries; r++) { if(WebRequestPost(url, json)) break; Sleep(100); }
}

string BuildGASContextJSON()
{
   double balance    = accInfo.Balance();
   double equity     = accInfo.Equity();
   double bid        = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask        = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   int    spread     = (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   double dailyPnLIDR = (balance - initialBalanceDaily) * GAS_USDtoIDR;

   double atr[1]; double atrVal = 0;
   int atrHandle = iATR(_Symbol, PERIOD_M15, 14);
   if(atrHandle != INVALID_HANDLE) { CopyBuffer(atrHandle, 0, 0, 1, atr); atrVal = atr[0]; IndicatorRelease(atrHandle); }

   bool inLondon = GAS_IsLondonKillZone(), inNY = GAS_IsNYKillZone();

   string posJSON = "["; bool firstPos = true;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(!posInfo.SelectByIndex(i) || posInfo.Magic() != MagicNumber) continue;
      if(!firstPos) posJSON += ","; firstPos = false;
      posJSON += "{\"ticket\":" + IntegerToString(posInfo.Ticket()) +
                 ",\"symbol\":\"" + posInfo.Symbol() + "\"" +
                 ",\"type\":\"" + (posInfo.PositionType()==POSITION_TYPE_BUY?"BUY":"SELL") + "\"" +
                 ",\"volume\":" + DoubleToString(posInfo.Volume(), 2) +
                 ",\"open_price\":" + DoubleToString(posInfo.PriceOpen(), _Digits) +
                 ",\"sl\":" + DoubleToString(posInfo.StopLoss(), _Digits) +
                 ",\"tp\":" + DoubleToString(posInfo.TakeProfit(), _Digits) +
                 ",\"profit_usd\":" + DoubleToString(posInfo.Profit(), 2) +
                 ",\"profit_idr\":" + DoubleToString(posInfo.Profit()*GAS_USDtoIDR, 0) + "}";
   }
   posJSON += "]";

   string json = "{";
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"broker\":\"" + GAS_Broker + "\",";
   json += "\"leverage\":" + IntegerToString(GAS_Leverage) + ",";
   json += "\"symbol\":\"" + _Symbol + "\",";
   json += "\"account\":{\"balance_usd\":" + DoubleToString(balance,2) +
           ",\"equity_usd\":" + DoubleToString(equity,2) +
           ",\"balance_idr\":" + DoubleToString(balance*GAS_USDtoIDR,0) +
           ",\"free_margin\":" + DoubleToString(accInfo.FreeMargin(),2) +
           ",\"margin_level\":" + DoubleToString(accInfo.MarginLevel(),2) + "},";
   json += "\"market\":{\"bid\":" + DoubleToString(bid,_Digits) +
           ",\"ask\":" + DoubleToString(ask,_Digits) +
           ",\"spread\":" + IntegerToString(spread) +
           ",\"atr_14_m15\":" + DoubleToString(atrVal,_Digits) + "},";
   json += "\"daily_stats\":{\"trade_count\":" + IntegerToString(gas_DailyTradeCount) +
           ",\"max_trades\":" + IntegerToString(GAS_MaxTradesPerDay) +
           ",\"pnl_idr\":" + DoubleToString(dailyPnLIDR,0) +
           ",\"max_loss_idr\":" + DoubleToString(GAS_MaxDailyLossIDR,0) +
           ",\"consecutive_loss\":" + IntegerToString(gas_ConsecutiveLossCount) +
           ",\"is_paused\":" + (gas_IsPaused?"true":"false") + "},";
   json += "\"rules\":{\"fixed_lot\":" + DoubleToString(GAS_FixedLot,2) +
           ",\"be_points\":" + IntegerToString(GAS_MoveBEPoints) +
           ",\"no_layering\":" + (GAS_NoLayering?"true":"false") + "},";
   json += "\"kill_zone\":{\"london\":" + (inLondon?"true":"false") +
           ",\"new_york\":" + (inNY?"true":"false") + "},";
   json += "\"positions\":" + posJSON + ",";
   json += "\"timestamp\":" + IntegerToString((int)TimeCurrent());
   json += "}";
   return json;
}

//====================================================================
//  SECTION 13: SIGNAL REQUEST (TIDAK DIUBAH)
//====================================================================
void RequestGASSignal()
{
   string contextJSON = BuildGASContextJSON();
   string url = GatewayURL + GAS_SignalReqEndpoint;
   uchar data[], result[];
   string headers = "Content-Type: application/json\r\n";
   StringToCharArray(contextJSON, data, 0, StringLen(contextJSON));
   int res = WebRequest("POST", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1) return;
   string response = CharArrayToString(result);
   if(StringLen(response) > 10) ParseGASSignalResponse(response);
}

void ParseGASSignalResponse(string json)
{
   string signal_id  = GetJSONValue(json, "signal_id");
   string action     = GetJSONValue(json, "action");
   string symbol     = GetJSONValue(json, "symbol");
   double entry      = StringToDouble(GetJSONValue(json, "entry"));
   double sl         = StringToDouble(GetJSONValue(json, "sl"));
   double tp1        = StringToDouble(GetJSONValue(json, "tp1"));
   double tp_final   = StringToDouble(GetJSONValue(json, "tp_final"));
   double lot        = StringToDouble(GetJSONValue(json, "lot"));
   string reason     = GetJSONValue(json, "reason");
   double confidence = StringToDouble(GetJSONValue(json, "confidence"));

   if(signal_id == "" || signal_id == gas_LastAISignalID) return;
   if(action == "NONE" || action == "WAIT" || action == "") return;

   Print("🤖 GAS AI Signal | ", action, " ", symbol, " | Conf:", DoubleToString(confidence*100,1), "%");
   Print("   Reason: ", reason);
   gas_LastAISignalID = signal_id;

   if(GAS_AutoExecAISignal && GAS_CheckCanTrade() && symbol == _Symbol)
   {
      double spread = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(MaxSpreadPoints > 0 && spread > MaxSpreadPoints) return;
      double execLot = (lot > 0) ? lot : GAS_FixedLot;
      double useTP   = (tp_final > 0) ? tp_final : tp1;
      bool success = false;
      if(action == "BUY")        success = trade.Buy(execLot, symbol, SymbolInfoDouble(symbol, SYMBOL_ASK), sl, useTP);
      else if(action == "SELL")  success = trade.Sell(execLot, symbol, SymbolInfoDouble(symbol, SYMBOL_BID), sl, useTP);
      if(success) { Print("🔥 AI Signal dieksekusi | Lot:", execLot); GAS_SendSignalExecConfirm(signal_id, action, execLot, sl, useTP, reason); }
      else          Print("❌ Eksekusi signal gagal. Code:", trade.ResultRetcode());
   }
}

//====================================================================
//  SECTION 14: JOURNAL & NOTIFICATION (TIDAK DIUBAH)
//====================================================================
void GAS_SendTradeJournal(ulong dealTicket)
{
   double profit    = HistoryDealGetDouble(dealTicket,  DEAL_PROFIT);
   double volume    = HistoryDealGetDouble(dealTicket,  DEAL_VOLUME);
   double dealPrice = HistoryDealGetDouble(dealTicket,  DEAL_PRICE);
   string sym       = HistoryDealGetString(dealTicket,  DEAL_SYMBOL);
   long   dealType  = HistoryDealGetInteger(dealTicket, DEAL_TYPE);

   string json = "{";
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"symbol\":\"" + sym + "\",";
   json += "\"direction\":\"" + ((dealType==DEAL_TYPE_BUY)?"BUY":"SELL") + "\",";
   json += "\"volume\":"    + DoubleToString(volume, 2) + ",";
   json += "\"deal_price\":"+ DoubleToString(dealPrice, _Digits) + ",";
   json += "\"profit_usd\":"+ DoubleToString(profit, 2) + ",";
   json += "\"profit_idr\":"+ DoubleToString(profit*GAS_USDtoIDR, 0) + ",";
   json += "\"result\":\"" + (profit >= 0 ? "WIN" : "LOSS") + "\",";
   json += "\"balance_after\":"+ DoubleToString(accInfo.Balance(), 2) + ",";
   json += "\"timestamp\":" + IntegerToString((int)TimeCurrent());
   json += "}";
   WebRequestPost(GatewayURL + GAS_JournalEndpoint, json);
}

void GAS_SendSignalExecConfirm(string signal_id, string action, double lot, double sl, double tp, string reason)
{
   string json = "{\"signal_id\":\""+signal_id+"\",\"action\":\""+action+"\",\"symbol\":\""+_Symbol+
                 "\",\"lot\":"+DoubleToString(lot,2)+",\"sl\":"+DoubleToString(sl,_Digits)+
                 ",\"tp\":"+DoubleToString(tp,_Digits)+",\"executed_by\":\""+GAS_TraderName+
                 "\",\"reason\":\""+reason+"\",\"timestamp\":"+IntegerToString((int)TimeCurrent())+"}";
   WebRequestPost(GatewayURL + "/api/gas/signal/confirm", json);
}

void GAS_SendPauseNotification()
{
   string json = "{\"trader\":\""+GAS_TraderName+"\",\"event\":\"PAUSE_TRIGGERED\","+
                 "\"consecutive_loss\":"+IntegerToString(gas_ConsecutiveLossCount)+","+
                 "\"pause_until\":"+IntegerToString((int)gas_PauseUntilTime)+","+
                 "\"timestamp\":"+IntegerToString((int)TimeCurrent())+"}";
   WebRequestPost(GatewayURL + "/api/gas/alert/pause", json);
}

//====================================================================
//  SECTION 15: KILL ZONE (TIDAK DIUBAH)
//====================================================================
bool GAS_IsLondonKillZone()
{ MqlDateTime t; TimeToStruct(TimeGMT(), t); return (t.hour >= 8 && t.hour < 11); }

bool GAS_IsNYKillZone()
{ MqlDateTime t; TimeToStruct(TimeGMT(), t); return (t.hour >= 13 && t.hour < 16); }

//====================================================================
//  SECTION 16: ORIGINAL v3.1 FUNCTIONS (TIDAK DIUBAH)
//====================================================================
void SendTickBatch()
{
   if(tickCount == 0) return;
   string json = BuildTickJSON();
   string url  = GatewayURL + "/mt5/tick";
   for(int retry = 0; retry < MaxRetries; retry++) { if(WebRequestPost(url, json)) break; Sleep(100); }
   tickCount = 0;
   ArrayResize(tickBuffer, 0, 100);
}

string BuildTickJSON()
{
   string json = "{\"symbol\":\"" + _Symbol + "\",\"ticks\":[";
   for(int i = 0; i < tickCount; i++)
   {
      if(i > 0) json += ",";
      json += "{\"time\":"   + DoubleToString(tickBuffer[i].time, 0) +
              ",\"bid\":"    + DoubleToString(tickBuffer[i].bid, _Digits) +
              ",\"ask\":"    + DoubleToString(tickBuffer[i].ask, _Digits) +
              ",\"volume\":0}";
   }
   json += "]}";
   return json;
}

void SendOHLCBatch()
{
   string tf_array[];
   int tf_count = StringSplit(OHLCPeriods, ',', tf_array);
   for(int i = 0; i < tf_count; i++)
   {
      ENUM_TIMEFRAMES tf = StringToTimeframe(tf_array[i]);
      if(tf == PERIOD_CURRENT) continue;
      MqlRates rates[];
      if(CopyRates(_Symbol, tf, 0, 1, rates) > 0)
      {
         string json = "{\"symbol\":\""+_Symbol+"\",\"timeframe\":\""+tf_array[i]+
                       "\",\"time\":"+IntegerToString(rates[0].time)+
                       ",\"open\":"+DoubleToString(rates[0].open, _Digits)+
                       ",\"high\":"+DoubleToString(rates[0].high, _Digits)+
                       ",\"low\":"+DoubleToString(rates[0].low, _Digits)+
                       ",\"close\":"+DoubleToString(rates[0].close, _Digits)+
                       ",\"volume\":"+IntegerToString(rates[0].tick_volume)+"}";
         WebRequestPost(GatewayURL + "/mt5/ohlc", json);
      }
   }
}

void SendHeartbeat()
{
   string json = "{\"symbol\":\""+_Symbol+"\",\"trader\":\""+GAS_TraderName+
                 "\",\"balance\":"+DoubleToString(accInfo.Balance(),2)+
                 ",\"equity\":"+DoubleToString(accInfo.Equity(),2)+
                 ",\"balance_idr\":"+DoubleToString(accInfo.Balance()*GAS_USDtoIDR,0)+
                 ",\"daily_trades\":"+IntegerToString(gas_DailyTradeCount)+
                 ",\"is_paused\":"+(gas_IsPaused?"true":"false")+
                 ",\"kill_zone\":\""+(GAS_IsLondonKillZone()?"LONDON":GAS_IsNYKillZone()?"NEW_YORK":"OFF")+
                 "\",\"positions\":"+IntegerToString(PositionsTotal())+
                 ",\"magic\":"+IntegerToString(MagicNumber)+"}";
   WebRequestPost(GatewayURL + "/mt5/heartbeat", json);
}

void PollOrderQueue()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   uchar data[], result[]; string headers = "";
   int res = WebRequest("GET", GatewayURL+"/terminal/order/queue", headers, WebRequestTimeout, data, result, headers);
   if(res == -1) return;
   string json = CharArrayToString(result);
   if(StringLen(json) < 5) return;
   string order_id = GetJSONValue(json, "order_id");
   if(order_id == "" || order_id == lastOrderID) return;
   ParseAndExecuteOrder(json);
}

void ParseAndExecuteOrder(string json)
{
   string order_id = GetJSONValue(json, "order_id");
   string action   = GetJSONValue(json, "action");
   string symbol   = GetJSONValue(json, "symbol");
   double volume   = StringToDouble(GetJSONValue(json, "volume"));
   double price    = StringToDouble(GetJSONValue(json, "price"));
   double sl       = StringToDouble(GetJSONValue(json, "stop_loss"));
   double tp       = StringToDouble(GetJSONValue(json, "take_profit"));
   int    magic    = (int)StringToInteger(GetJSONValue(json, "magic_number"));

   if(order_id == "" || action == "") return;
   if(magic != MagicNumber) { SendOrderStatus(order_id, "rejected", "Invalid magic"); return; }
   if(symbol != _Symbol)    { SendOrderStatus(order_id, "rejected", "Wrong symbol"); return; }
   if(!GAS_CheckCanTrade()) { SendOrderStatus(order_id, "rejected", "Rules blocked"); return; }

   bool success = false;
   if(action == "BUY")            success = trade.Buy(volume, symbol, SymbolInfoDouble(symbol, SYMBOL_ASK), sl, tp);
   else if(action == "SELL")      success = trade.Sell(volume, symbol, SymbolInfoDouble(symbol, SYMBOL_BID), sl, tp);
   else if(action == "BUY_LIMIT"  && price > 0) success = trade.BuyLimit(volume, price, symbol, sl, tp);
   else if(action == "SELL_LIMIT" && price > 0) success = trade.SellLimit(volume, price, symbol, sl, tp);
   else if(action == "BUY_STOP"   && price > 0) success = trade.BuyStop(volume, price, symbol, sl, tp);
   else if(action == "SELL_STOP"  && price > 0) success = trade.SellStop(volume, price, symbol, sl, tp);
   else { SendOrderStatus(order_id, "rejected", "Invalid action"); return; }

   if(success)
   { lastOrderID = order_id; SendOrderStatus(order_id, "filled", "", (action=="BUY"?SymbolInfoDouble(symbol,SYMBOL_ASK):SymbolInfoDouble(symbol,SYMBOL_BID))); }
   else
   { SendOrderStatus(order_id, "failed", trade.ResultRetcodeDescription()); }
}

void SendOrderStatus(string order_id, string status, string message, double fill_price = 0)
{
   string json = "{\"order_id\":\""+order_id+"\",\"status\":\""+status+"\"";
   if(status == "filled")
      json += ",\"fill_price\":"+DoubleToString(fill_price,_Digits)+",\"fill_time\":"+IntegerToString(TimeCurrent());
   else if(message != "")
      json += ",\"message\":\""+message+"\"";
   json += "}";
   WebRequestPost(GatewayURL + "/terminal/order/status", json);
}

void PollSignal()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   uchar data[], result[]; string headers = "";
   int res = WebRequest("GET", GatewayURL+"/api/signal/", headers, WebRequestTimeout, data, result, headers);
   if(res == -1) return;
   ParseAndExecuteSignal(CharArrayToString(result));
}

void ParseAndExecuteSignal(string json)
{
   string signal_id = GetJSONValue(json, "signal_id");
   string action    = GetJSONValue(json, "action");
   string symbol    = GetJSONValue(json, "symbol");
   double sl        = StringToDouble(GetJSONValue(json, "sl"));
   double tp        = StringToDouble(GetJSONValue(json, "tp"));
   double price     = StringToDouble(GetJSONValue(json, "price"));

   if(signal_id == "" || signal_id == lastSignalID || action == "NONE") return;
   if(symbol != _Symbol || !GAS_CheckCanTrade()) return;

   double entry_ref = (action=="BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) :
                      (action=="SELL")? SymbolInfoDouble(symbol, SYMBOL_BID) : price;
   double sym_point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double lotSize   = CalculateLotSize(symbol, sym_point > 0 ? MathAbs(entry_ref-sl)/sym_point : 10);

   bool success = false;
   if(action == "BUY")            success = trade.Buy(lotSize, symbol, SymbolInfoDouble(symbol,SYMBOL_ASK), sl, tp);
   else if(action == "SELL")      success = trade.Sell(lotSize, symbol, SymbolInfoDouble(symbol,SYMBOL_BID), sl, tp);
   else if(action == "BUY_LIMIT"  && price > 0) success = trade.BuyLimit(lotSize, price, symbol, sl, tp);
   else if(action == "SELL_LIMIT" && price > 0) success = trade.SellLimit(lotSize, price, symbol, sl, tp);

   if(success) { Print("🔥 Signal exec OK | Lot:", lotSize); lastSignalID = signal_id; }
   else          Print("❌ Signal exec fail. Code:", trade.ResultRetcode());
}

string GetJSONValue(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int start = StringFind(json, search);
   if(start >= 0) { start += StringLen(search); int end = StringFind(json, "\"", start); if(end > start) return StringSubstr(json, start, end-start); }
   search = "\"" + key + "\":";
   start = StringFind(json, search);
   if(start >= 0) { start += StringLen(search); int end = start; while(end < StringLen(json) && json[end] != ',' && json[end] != '}' && json[end] != ' ') end++; return StringSubstr(json, start, end-start); }
   return "";
}

double CalculateLotSize(string sym, double sl_points)
{
   if(sl_points <= 0) return SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double calcLot = (accInfo.Balance() * RiskPercent / 100.0) / (sl_points * SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE));
   double step = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   if(step > 0) calcLot = MathFloor(calcLot / step) * step;
   double minL = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), maxL = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   return MathMax(minL, MathMin(maxL, calcLot));
}

void TrailingStops()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!posInfo.SelectByIndex(i) || posInfo.Magic() != MagicNumber || posInfo.Symbol() != _Symbol) continue;
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(posInfo.PositionType() == POSITION_TYPE_BUY)
      { double newSL = bid - TrailingStop*point; if(newSL > posInfo.StopLoss() && newSL > posInfo.PriceOpen()) trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit()); }
      else
      { double newSL = ask + TrailingStop*point; if(newSL < posInfo.StopLoss() && newSL < posInfo.PriceOpen()) trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit()); }
   }
}

void CheckDailyDrawdown()
{
   double ddPct = (initialBalanceDaily - accInfo.Balance()) / initialBalanceDaily * 100;
   if(ddPct >= MaxDailyDrawdown) { Print("⚠️ Drawdown limit: ", ddPct, "%"); CloseAllPositions(); ExpertRemove(); }
}

void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber) trade.PositionClose(posInfo.Ticket());
}

ENUM_TIMEFRAMES StringToTimeframe(string tf)
{
   if(tf=="M1")  return PERIOD_M1;  if(tf=="M5")  return PERIOD_M5;
   if(tf=="M15") return PERIOD_M15; if(tf=="M30") return PERIOD_M30;
   if(tf=="H1")  return PERIOD_H1;  if(tf=="H4")  return PERIOD_H4;
   if(tf=="D1")  return PERIOD_D1;  if(tf=="W1")  return PERIOD_W1;
   if(tf=="MN1") return PERIOD_MN1; return PERIOD_CURRENT;
}

bool WebRequestPost(string url, string json)
{
   uchar data[], result[];
   string headers = "Content-Type: application/json\r\n";
   StringToCharArray(json, data, 0, StringLen(json));
   int res = WebRequest("POST", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1) { int err = GetLastError(); if(err != 0) Print("❌ WebRequest err ", err, " → ", url); return false; }
   return true;
}

//====================================================================
//  SECTION 17: MULTI-SYMBOL SCANNER ENGINE (BARU v5.0)
//  1 EA di 1 chart → scan SEMUA pair Exness sekaligus
//====================================================================

//--------------------------------------------------------------------
// GetSymbolList — ambil daftar semua symbol
// ScanMarketWatchOnly = true  → hanya yang ada di Market Watch
// ScanMarketWatchOnly = false → semua symbol di broker (bisa ratusan)
//--------------------------------------------------------------------
int GetSymbolList(string& symbols[])
{
   int total = SymbolsTotal(ScanMarketWatchOnly);
   ArrayResize(symbols, total);
   int count = 0;

   for(int i = 0; i < total; i++)
   {
      string sym = SymbolName(i, ScanMarketWatchOnly);
      if(sym == "") continue;

      // Pastikan symbol bisa di-select untuk data
      if(!SymbolSelect(sym, true)) continue;

      // Skip jika tidak bisa di-trade (optional)
      ENUM_SYMBOL_TRADE_MODE tradeMode = (ENUM_SYMBOL_TRADE_MODE)SymbolInfoInteger(sym, SYMBOL_TRADE_MODE);
      if(tradeMode == SYMBOL_TRADE_MODE_DISABLED) continue;

      symbols[count++] = sym;
   }

   ArrayResize(symbols, count);
   return count;
}

//--------------------------------------------------------------------
// GetSymbolCategory — kategorisasi symbol berdasarkan nama
//--------------------------------------------------------------------
string GetSymbolCategory(string sym)
{
   // Precious & Industrial metals
   if(StringFind(sym,"XAU")>=0 || StringFind(sym,"XAG")>=0 ||
      StringFind(sym,"XPD")>=0 || StringFind(sym,"XPT")>=0) return "Precious";
   if(StringFind(sym,"XAL")>=0 || StringFind(sym,"XCU")>=0 ||
      StringFind(sym,"XNI")>=0 || StringFind(sym,"XPB")>=0 || StringFind(sym,"XZN")>=0) return "Industrial";
   // Energy
   if(StringFind(sym,"OIL")>=0 || StringFind(sym,"XNG")>=0 || sym=="USOIL" || sym=="UKOIL") return "Energy";
   // Indices
   if(sym=="US30"||sym=="US500"||sym=="USTEC"||sym=="DE30"||sym=="UK100"||
      sym=="JP225"||sym=="HK50"||sym=="AUS200"||sym=="FR40"||sym=="STOXX50"||
      sym=="DXY"||StringFind(sym,"_x")>=0) return "Index";
   // Crypto
   if(StringFind(sym,"BTC")>=0||StringFind(sym,"ETH")>=0||StringFind(sym,"XRP")>=0||
      StringFind(sym,"LTC")>=0||StringFind(sym,"BNB")>=0) return "Crypto";
   // Stocks (biasanya 4+ chars, ada # atau langsung ticker)
   if(sym=="AAPL"||sym=="MSFT"||sym=="GOOGL"||sym=="AMZN"||sym=="TSLA"||
      sym=="META"||sym=="NVDA"||sym=="NFLX"||sym=="AMD"||sym=="JPM"||
      sym=="BAC"||sym=="WMT"||sym=="BABA"||sym=="TSM"||sym=="SONY") return "Stock";
   // Forex (default 6 chars semua huruf)
   if(StringLen(sym) == 6) return "Forex";
   return "Other";
}

//--------------------------------------------------------------------
// ScanAndSendMultiTick
// Ambil bid/ask SEMUA symbol sekarang, kirim 1 HTTP call ke /mt5/multitick
// Format: {"scanner_id":"GAS_v5","symbols":[{sym,bid,ask,spread,time,category},...]}
//--------------------------------------------------------------------
void ScanAndSendMultiTick()
{
   string symbols[];
   int count = GetSymbolList(symbols);
   if(count == 0) return;

   string json = "{\"scanner_id\":\"GAS_v5\",";
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"symbols\":[";

   bool first = true;
   int  sent  = 0;

   for(int i = 0; i < count; i++)
   {
      string sym = symbols[i];

      // Spread filter
      if(SkipSpreadsOver && MaxScanSpread > 0)
      {
         double spd = (double)SymbolInfoInteger(sym, SYMBOL_SPREAD);
         if(spd > MaxScanSpread) continue;
      }

      MqlTick tick;
      if(!SymbolInfoTick(sym, tick)) continue;

      int    digits   = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
      double spread   = (double)SymbolInfoInteger(sym, SYMBOL_SPREAD);
      string category = GetSymbolCategory(sym);

      if(!first) json += ",";
      first = false;

      json += "{";
      json += "\"symbol\":\"" + sym + "\",";
      json += "\"bid\":"      + DoubleToString(tick.bid, digits) + ",";
      json += "\"ask\":"      + DoubleToString(tick.ask, digits) + ",";
      json += "\"last\":"     + DoubleToString(tick.last, digits) + ",";
      json += "\"spread\":"   + DoubleToString(spread, 1) + ",";
      json += "\"volume\":"   + IntegerToString(tick.volume) + ",";
      json += "\"time\":"     + IntegerToString((int)tick.time) + ",";
      json += "\"category\":\"" + category + "\"";
      json += "}";
      sent++;
   }

   json += "]}";

   if(sent == 0) return;

   string url = GatewayURL + "/mt5/multitick";
   if(WebRequestPost(url, json))
      Print("📡 MultiTick: ", sent, " symbols dikirim");
   else
      Print("⚠️ MultiTick gagal. Cek URL whitelist di MT5 Tools→Options→Expert Advisors");
}

//--------------------------------------------------------------------
// ScanAndSendMultiOHLC
// Ambil OHLCV terbaru untuk SEMUA symbol per timeframe
// Kirim 1 HTTP call per TF ke /mt5/multiohlc
// Format: {"timeframe":"M15","bars":[{symbol,time,open,high,low,close,volume},...]}
//--------------------------------------------------------------------
void ScanAndSendMultiOHLC()
{
   string symbols[];
   int sym_count = GetSymbolList(symbols);
   if(sym_count == 0) return;

   string tf_array[];
   int tf_count = StringSplit(ScanOHLCTimeframes, ',', tf_array);

   for(int t = 0; t < tf_count; t++)
   {
      ENUM_TIMEFRAMES tf = StringToTimeframe(tf_array[t]);
      if(tf == PERIOD_CURRENT) continue;

      string json = "{\"timeframe\":\"" + tf_array[t] + "\",";
      json += "\"trader\":\"" + GAS_TraderName + "\",";
      json += "\"bars\":[";

      bool first = true;
      int  bars_sent = 0;

      for(int i = 0; i < sym_count; i++)
      {
         string sym = symbols[i];
         MqlRates rates[];
         int copied = CopyRates(sym, tf, 0, ScanOHLCBarsPerSymbol, rates);
         if(copied <= 0) continue;

         int digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);

         // Kirim dari bar terlama ke terbaru
         for(int b = copied - 1; b >= 0; b--)
         {
            if(!first) json += ",";
            first = false;

            json += "{";
            json += "\"symbol\":\"" + sym + "\",";
            json += "\"time\":"   + IntegerToString(rates[b].time) + ",";
            json += "\"open\":"   + DoubleToString(rates[b].open, digits) + ",";
            json += "\"high\":"   + DoubleToString(rates[b].high, digits) + ",";
            json += "\"low\":"    + DoubleToString(rates[b].low, digits) + ",";
            json += "\"close\":"  + DoubleToString(rates[b].close, digits) + ",";
            json += "\"volume\":" + IntegerToString(rates[b].tick_volume);
            json += "}";
            bars_sent++;
         }
      }

      json += "]}";

      if(bars_sent == 0) continue;

      string url = GatewayURL + "/mt5/multiohlc";
      if(WebRequestPost(url, json))
         Print("📊 MultiOHLC [", tf_array[t], "]: ", bars_sent, " bars dari ", sym_count, " symbols");
   }
}

//+------------------------------------------------------------------+
//  END — GAS_StrategyScanner v5.0
//  Attach ke 1 chart → scan SEMUA pair di Exness otomatis
//+------------------------------------------------------------------+
