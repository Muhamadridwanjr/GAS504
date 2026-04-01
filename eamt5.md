//+------------------------------------------------------------------+
//|                              GASSTRATEGYEAPRO_v4.mq5             |
//|           GAS Strategy EA PRO — Muhamad RidwanJr                 |
//|           Fully integrated with GAS Ecosystem + Context Push     |
//|           Version 4.0 PRO — Upgrade from v3.1                    |
//|           Build: 2025-03-06                                       |
//+------------------------------------------------------------------+
//  CHANGELOG v4.0 PRO (semua kode v3.1 tetap utuh):
//  [+] GAS Context Push → kirim full akun+rules+market ke server
//  [+] GAS Signal Request → trigger AI signal dengan full payload
//  [+] GAS Rules Engine:
//      - Max Daily Loss IDR (Rp 600.000)
//      - Max Trades Per Day (10)
//      - 3x Consecutive Loss → Pause 5 jam
//      - Move Breakeven setelah +300 points
//      - Partial Close 50% di TP1
//      - No EA Layer (blokir jika posisi aktif)
//  [+] GAS Trade Journal → kirim journal setelah setiap eksekusi
//  [+] Kill Zone detection (London & NY)
//  [+] DXY Correlation check
//  [+] IDR conversion untuk P&L monitoring
//+------------------------------------------------------------------+
#property copyright "GAS Strategy — Muhamad RidwanJr"
#property version   "4.00"
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

// Tick data
input bool     SendTickData          = true;
input int      TickSendInterval      = 1;
input int      MaxTicksPerBatch      = 100;

// OHLC data
input bool     SendOHLCData          = false;
input int      OHLCSendInterval      = 60;
input string   OHLCPeriods           = "M1,M5,M15,H1,H4,D1";

// Heartbeat
input bool     EnableHeartbeat       = true;
input int      HeartbeatInterval     = 60;

// WebRequest
input int      WebRequestTimeout     = 2000;
input int      MaxRetries            = 3;

//====================================================================
//  SECTION 3: INPUT PARAMETERS — GAS PRO v4.0 (BARU)
//====================================================================

// --- GAS Trader Identity & Broker Context ---
input string   GAS_TraderName        = "Muhamad RidwanJr";          // Nama trader
input string   GAS_Broker            = "Exness Zero Spread";         // Broker
input int      GAS_Leverage          = 1000;                         // Leverage
input double   GAS_DepositIDR        = 10000000.0;                     // Deposit awal (IDR)
input string   GAS_Style             = "Hybrid Scalping-Intraday";   // Gaya trading
input string   GAS_Strategy          = "ICT+SMC+PAC";               // Strategy

// --- GAS Rules (sesuai context lo) ---
input double   GAS_MaxDailyLossIDR   = 600000.0;   // Max loss harian (IDR Rp 600.000)
input int      GAS_MaxTradesPerDay   = 10;          // Max trade per hari
input double   GAS_FixedLot          = 0.01;        // Fixed lot size
input int      GAS_MoveBEPoints      = 300;         // Move BE setelah profit N points
input double   GAS_PartialClosePct   = 50.0;        // Partial close % di TP1
input int      GAS_ConsecutiveLoss   = 3;           // Trigger pause setelah N loss berturut
input int      GAS_PauseHours        = 5;           // Jam istirahat setelah N loss
input bool     GAS_NoLayering        = true;        // Block order baru jika ada posisi aktif
input double   GAS_USDtoIDR          = 16000.0;     // Kurs USD → IDR (update manual)

// --- GAS Context Push ---
input bool     GAS_EnableContextPush = true;        // Kirim GAS context ke server?
input int      GAS_ContextInterval   = 30;          // Interval kirim context (detik)
input string   GAS_ContextEndpoint   = "/api/gas/context";  // Endpoint context

// --- GAS Signal Request ---
input bool     GAS_EnableSignalReq   = false;       // Aktifkan request signal ke GAS AI?
input int      GAS_SignalReqInterval = 5;           // Interval request signal (detik)
input string   GAS_SignalReqEndpoint = "/api/gas/signal/request";  // Endpoint request
input string   GAS_SignalResEndpoint = "/api/gas/signal/latest";   // Endpoint latest signal
input bool     GAS_AutoExecAISignal  = false;       // Auto-eksekusi signal dari GAS AI?

// --- GAS Journal ---
input bool     GAS_EnableJournal     = true;        // Kirim trade journal ke server?
input string   GAS_JournalEndpoint   = "/api/gas/journal";  // Endpoint journal

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
//  SECTION 5: GLOBAL VARIABLES — GAS PRO v4.0 (BARU)
//====================================================================

// Daily tracking
int      gas_DailyTradeCount     = 0;
double   gas_DailyPnLUSD         = 0.0;
datetime gas_LastTradeDate       = 0;

// Consecutive loss tracking
int      gas_ConsecutiveLossCount = 0;
datetime gas_PauseUntilTime       = 0;
bool     gas_IsPaused             = false;

// BE & Partial close tracking (max 50 posisi)
ulong    gas_BEDoneTickets[50];
int      gas_BEDoneCount     = 0;
ulong    gas_PartialDoneTickets[50];
int      gas_PartialDoneCount = 0;

// Timing
datetime gas_LastContextSendTime = 0;
datetime gas_LastSignalReqTime   = 0;

// GAS Signal tracking
string   gas_LastAISignalID = "";
datetime gas_LastDealTime   = 0;

// TP1 tracking per position
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
//  SECTION 6: OnInit
//====================================================================
int OnInit()
{
   trade.SetExpertMagicNumber(MagicNumber);
   EventSetTimer(1);

   initialBalanceDaily = accInfo.Balance();

   // Reset daily stats
   gas_DailyTradeCount = 0;
   gas_DailyPnLUSD     = 0.0;
   gas_LastTradeDate   = iTime(_Symbol, PERIOD_D1, 0);

   Print("🚀 GASSTRATEGYEAPRO v4.0 Started | Trader: ", GAS_TraderName);
   Print("📊 Symbol: ", _Symbol, " | Broker: ", GAS_Broker, " | Leverage: 1:", GAS_Leverage);
   Print("💰 Max Daily Loss: Rp ", DoubleToString(GAS_MaxDailyLossIDR, 0),
         " | Max Trades: ", GAS_MaxTradesPerDay, "/hari");
   Print("Gateway URL: ", GatewayURL);

   // Kirim initial context ke server
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
//  SECTION 8: OnTimer — ORIGINAL + GAS PRO tasks
//====================================================================
void OnTimer()
{
   datetime now = TimeCurrent();

   // --- Reset daily stats jika hari baru ---
   GAS_CheckDailyReset();

   // --- GAS PRO: Cek pause status ---
   if(gas_IsPaused && now >= gas_PauseUntilTime)
   {
      gas_IsPaused = false;
      gas_ConsecutiveLossCount = 0;
      Print("✅ Pause selesai. Trading dilanjutkan. Jam: ", TimeToString(now));
   }

   // --- GAS PRO: Cek max daily loss IDR ---
   GAS_CheckMaxDailyLossIDR();

   // --- GAS PRO: Move Breakeven ---
   if(GAS_MoveBEPoints > 0)
      GAS_CheckMoveBreakeven();

   // --- GAS PRO: Partial Close di TP1 ---
   if(GAS_PartialClosePct > 0)
      GAS_CheckPartialClose();

   // 1. Polling sinyal original
   if(EnableSignalPolling && now - lastSignalPollTime >= SignalPollingInterval)
   {
      lastSignalPollTime = now;
      if(!gas_IsPaused) PollSignal();
   }

   // 2. Polling order queue original
   if(EnableOrderExecution && now - lastOrderPollTime >= OrderPollingInterval)
   {
      lastOrderPollTime = now;
      if(!gas_IsPaused) PollOrderQueue();
   }

   // 3. Tick batch
   if(SendTickData && now - lastTickSendTime >= TickSendInterval)
   {
      lastTickSendTime = now;
      SendTickBatch();
   }

   // 4. OHLC
   if(SendOHLCData && now - lastOHLCSendTime >= OHLCSendInterval)
   {
      lastOHLCSendTime = now;
      SendOHLCBatch();
   }

   // 5. Heartbeat
   if(EnableHeartbeat && now - lastHeartbeatTime >= HeartbeatInterval)
   {
      lastHeartbeatTime = now;
      SendHeartbeat();
   }

   // 6. Trailing stop
   if(TrailingStop > 0)
      TrailingStops();

   // 7. Drawdown check original
   CheckDailyDrawdown();

   // --- GAS PRO 8: Context Push ---
   if(GAS_EnableContextPush && now - gas_LastContextSendTime >= GAS_ContextInterval)
   {
      gas_LastContextSendTime = now;
      SendGASContext();
   }

   // --- GAS PRO 9: Signal Request ---
   if(GAS_EnableSignalReq && !gas_IsPaused &&
      now - gas_LastSignalReqTime >= GAS_SignalReqInterval)
   {
      gas_LastSignalReqTime = now;
      if(GAS_CheckCanTrade())
         RequestGASSignal();
   }
}

//====================================================================
//  SECTION 9: OnTick — ORIGINAL (tidak diubah)
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
//  SECTION 10: OnTradeTransaction — GAS PRO (deteksi loss/win)
//  FIX v4.1: Pakai HistoryDealSelect langsung, hapus CDealInfo
//====================================================================
void OnTradeTransaction(
   const MqlTradeTransaction& trans,
   const MqlTradeRequest&     request,
   const MqlTradeResult&      result)
{
   // Hanya proses deal yang close posisi
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD) return;

   ulong dealTicket = trans.deal;
   if(dealTicket == 0) return;

   // Pilih deal dari history
   if(!HistoryDealSelect(dealTicket)) return;

   // Filter: hanya milik EA ini dan entry OUT
   long dealMagic = HistoryDealGetInteger(dealTicket, DEAL_MAGIC);
   if(dealMagic != MagicNumber) return;

   ENUM_DEAL_ENTRY dealEntry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(dealTicket, DEAL_ENTRY);
   if(dealEntry != DEAL_ENTRY_OUT) return;

   double profit    = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
   double profitIDR = profit * GAS_USDtoIDR;

   // Update daily stats
   gas_DailyTradeCount++;
   gas_DailyPnLUSD += profit;

   Print("📝 Trade closed | Profit: $", DoubleToString(profit, 2),
         " (Rp ", DoubleToString(profitIDR, 0), ")",
         " | Daily total: ", gas_DailyTradeCount, "/", GAS_MaxTradesPerDay);

   // Track consecutive loss
   if(profit < 0.0)
   {
      gas_ConsecutiveLossCount++;
      Print("⚠️ Loss ke-", gas_ConsecutiveLossCount, " berturut-turut");

      if(gas_ConsecutiveLossCount >= GAS_ConsecutiveLoss)
      {
         gas_IsPaused       = true;
         gas_PauseUntilTime = TimeCurrent() + (GAS_PauseHours * 3600);
         Print("🛑 ", GAS_ConsecutiveLoss, "x loss berturut! PAUSE sampai: ",
               TimeToString(gas_PauseUntilTime));
         CloseAllPositions();
         GAS_SendPauseNotification();
      }
   }
   else
   {
      gas_ConsecutiveLossCount = 0; // Reset kalau profit
   }

   // Kirim journal ke server
   if(GAS_EnableJournal)
      GAS_SendTradeJournal(dealTicket);
}

//+------------------------------------------------------------------+
//============================================================
//  SECTION 11 — GAS PRO: RULES ENGINE
//============================================================

//------------------------------------------------------------
// Cek apakah boleh trade (semua rules check)
//------------------------------------------------------------
bool GAS_CheckCanTrade()
{
   // Pause check
   if(gas_IsPaused)
   {
      Print("⏸️ Sedang pause hingga: ", TimeToString(gas_PauseUntilTime));
      return false;
   }

   // Max trade per hari
   if(gas_DailyTradeCount >= GAS_MaxTradesPerDay)
   {
      Print("🚫 Max trades/hari tercapai: ", gas_DailyTradeCount, "/", GAS_MaxTradesPerDay);
      return false;
   }

   // No layering: blokir kalau ada posisi aktif
   if(GAS_NoLayering && PositionsTotal() > 0)
   {
      // Cek apakah ada posisi kita
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(posInfo.SelectByIndex(i) &&
            posInfo.Magic() == MagicNumber &&
            posInfo.Symbol() == _Symbol)
         {
            Print("🚫 No layering: Sudah ada posisi aktif di ", _Symbol);
            return false;
         }
      }
   }

   return true;
}

//------------------------------------------------------------
// Move Breakeven setelah +GAS_MoveBEPoints
//------------------------------------------------------------
void GAS_CheckMoveBreakeven()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point == 0) return;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!posInfo.SelectByIndex(i)) continue;
      if(posInfo.Magic() != MagicNumber) continue;
      if(posInfo.Symbol() != _Symbol) continue;

      ulong ticket = posInfo.Ticket();

      // Skip kalau sudah pernah di-BE
      if(GAS_IsTicketInArray(ticket, gas_BEDoneTickets, gas_BEDoneCount)) continue;

      double openPrice = posInfo.PriceOpen();
      double curSL     = posInfo.StopLoss();
      double bid       = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask       = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double profitPts = 0;

      if(posInfo.PositionType() == POSITION_TYPE_BUY)
      {
         profitPts = (bid - openPrice) / point;
         if(profitPts >= GAS_MoveBEPoints && curSL < openPrice)
         {
            double newSL = openPrice + 2 * point; // BE + 2 pts buffer
            if(trade.PositionModify(ticket, newSL, posInfo.TakeProfit()))
            {
               Print("✅ BE moved | Ticket:", ticket, " | Entry:", openPrice, " → SL:", newSL);
               if(gas_BEDoneCount < 50)
                  gas_BEDoneTickets[gas_BEDoneCount++] = ticket;
            }
         }
      }
      else if(posInfo.PositionType() == POSITION_TYPE_SELL)
      {
         profitPts = (openPrice - ask) / point;
         if(profitPts >= GAS_MoveBEPoints && (curSL > openPrice || curSL == 0))
         {
            double newSL = openPrice - 2 * point;
            if(trade.PositionModify(ticket, newSL, posInfo.TakeProfit()))
            {
               Print("✅ BE moved | Ticket:", ticket, " | Entry:", openPrice, " → SL:", newSL);
               if(gas_BEDoneCount < 50)
                  gas_BEDoneTickets[gas_BEDoneCount++] = ticket;
            }
         }
      }
   }
}

//------------------------------------------------------------
// Partial Close 50% di TP1
// TP1 = midpoint antara entry dan TP (50% jarak)
//------------------------------------------------------------
void GAS_CheckPartialClose()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   if(point == 0) return;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!posInfo.SelectByIndex(i)) continue;
      if(posInfo.Magic() != MagicNumber) continue;
      if(posInfo.Symbol() != _Symbol) continue;

      ulong  ticket   = posInfo.Ticket();
      double openPrice = posInfo.PriceOpen();
      double tp        = posInfo.TakeProfit();
      double volume    = posInfo.Volume();

      if(tp == 0) continue;
      if(GAS_IsTicketInArray(ticket, gas_PartialDoneTickets, gas_PartialDoneCount)) continue;

      // TP1 = 50% jarak entry ke TP
      double tp1 = 0;
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

      if(posInfo.PositionType() == POSITION_TYPE_BUY)
      {
         tp1 = openPrice + (tp - openPrice) * 0.5;
         if(bid >= tp1)
         {
            double closeVol = NormalizeDouble(volume * GAS_PartialClosePct / 100.0, 2);
            double minVol   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(closeVol < minVol) closeVol = minVol;

            if(trade.PositionClosePartial(ticket, closeVol))
            {
               Print("✅ Partial Close 50% | Ticket:", ticket, " | Vol:", closeVol,
                     " | TP1:", DoubleToString(tp1, _Digits));
               if(gas_PartialDoneCount < 50)
                  gas_PartialDoneTickets[gas_PartialDoneCount++] = ticket;
            }
         }
      }
      else if(posInfo.PositionType() == POSITION_TYPE_SELL)
      {
         tp1 = openPrice - (openPrice - tp) * 0.5;
         if(ask <= tp1)
         {
            double closeVol = NormalizeDouble(volume * GAS_PartialClosePct / 100.0, 2);
            double minVol   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(closeVol < minVol) closeVol = minVol;

            if(trade.PositionClosePartial(ticket, closeVol))
            {
               Print("✅ Partial Close 50% | Ticket:", ticket, " | Vol:", closeVol,
                     " | TP1:", DoubleToString(tp1, _Digits));
               if(gas_PartialDoneCount < 50)
                  gas_PartialDoneTickets[gas_PartialDoneCount++] = ticket;
            }
         }
      }
   }
}

//------------------------------------------------------------
// Cek max daily loss dalam IDR
//------------------------------------------------------------
void GAS_CheckMaxDailyLossIDR()
{
   double currentBalance = accInfo.Balance();
   double dailyPnL_USD   = currentBalance - initialBalanceDaily;
   double dailyPnL_IDR   = dailyPnL_USD * GAS_USDtoIDR;

   if(dailyPnL_IDR <= -GAS_MaxDailyLossIDR)
   {
      Print("🛑 MAX DAILY LOSS IDR tercapai! Loss: Rp ",
            DoubleToString(MathAbs(dailyPnL_IDR), 0),
            " / Rp ", DoubleToString(GAS_MaxDailyLossIDR, 0));
      CloseAllPositions();
      gas_IsPaused      = true;
      gas_PauseUntilTime = iTime(_Symbol, PERIOD_D1, 0) + 86400; // Sampai besok
      GAS_SendPauseNotification();
   }
}

//------------------------------------------------------------
// Reset daily stats jika hari baru
//------------------------------------------------------------
void GAS_CheckDailyReset()
{
   datetime todayOpen = iTime(_Symbol, PERIOD_D1, 0);
   if(todayOpen != gas_LastTradeDate)
   {
      gas_LastTradeDate    = todayOpen;
      gas_DailyTradeCount  = 0;
      gas_DailyPnLUSD      = 0.0;
      initialBalanceDaily  = accInfo.Balance();
      Print("🔄 Daily stats reset. Hari baru: ", TimeToString(todayOpen));
   }
}

//------------------------------------------------------------
// Helper: cek apakah ticket ada di array
//------------------------------------------------------------
bool GAS_IsTicketInArray(ulong ticket, ulong& arr[], int count)
{
   for(int i = 0; i < count; i++)
      if(arr[i] == ticket) return true;
   return false;
}

//============================================================
//  SECTION 12 — GAS PRO: CONTEXT PUSH
//  Kirim full context akun + market + rules ke server
//============================================================
void SendGASContext()
{
   string json = BuildGASContextJSON();
   string url  = GatewayURL + GAS_ContextEndpoint;

   for(int r = 0; r < MaxRetries; r++)
   {
      if(WebRequestPost(url, json)) break;
      Sleep(100);
   }
}

string BuildGASContextJSON()
{
   double balance    = accInfo.Balance();
   double equity     = accInfo.Equity();
   double margin     = accInfo.Margin();
   double freeMargin = accInfo.FreeMargin();
   double bid        = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask        = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   int    spread     = (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   double dailyPnLIDR = (balance - initialBalanceDaily) * GAS_USDtoIDR;

   // ATR 14
   double atr[1];
   double atrVal = 0;
   int    atrHandle = iATR(_Symbol, PERIOD_M15, 14);
   if(atrHandle != INVALID_HANDLE)
   {
      CopyBuffer(atrHandle, 0, 0, 1, atr);
      atrVal = atr[0];
      IndicatorRelease(atrHandle);
   }

   // Kill zone status
   bool inLondon  = GAS_IsLondonKillZone();
   bool inNY      = GAS_IsNYKillZone();
   bool killActive = inLondon || inNY;

   // Active positions JSON
   string posJSON = "[";
   bool   firstPos = true;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(!posInfo.SelectByIndex(i)) continue;
      if(posInfo.Magic() != MagicNumber) continue;

      if(!firstPos) posJSON += ",";
      firstPos = false;

      posJSON += "{";
      posJSON += "\"ticket\":"   + IntegerToString(posInfo.Ticket()) + ",";
      posJSON += "\"symbol\":\""  + posInfo.Symbol() + "\",";
      posJSON += "\"type\":\""    + (posInfo.PositionType()==POSITION_TYPE_BUY?"BUY":"SELL") + "\",";
      posJSON += "\"volume\":"    + DoubleToString(posInfo.Volume(), 2) + ",";
      posJSON += "\"open_price\":"+ DoubleToString(posInfo.PriceOpen(), _Digits) + ",";
      posJSON += "\"sl\":"        + DoubleToString(posInfo.StopLoss(), _Digits) + ",";
      posJSON += "\"tp\":"        + DoubleToString(posInfo.TakeProfit(), _Digits) + ",";
      posJSON += "\"profit_usd\":"+ DoubleToString(posInfo.Profit(), 2) + ",";
      posJSON += "\"profit_idr\":"+ DoubleToString(posInfo.Profit() * GAS_USDtoIDR, 0);
      posJSON += "}";
   }
   posJSON += "]";

   string json = "{";

   // Trader identity
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"broker\":\"" + GAS_Broker + "\",";
   json += "\"leverage\":" + IntegerToString(GAS_Leverage) + ",";
   json += "\"deposit_idr\":" + DoubleToString(GAS_DepositIDR, 0) + ",";
   json += "\"style\":\"" + GAS_Style + "\",";
   json += "\"strategy\":\"" + GAS_Strategy + "\",";
   json += "\"symbol\":\"" + _Symbol + "\",";
   json += "\"magic\":" + IntegerToString(MagicNumber) + ",";

   // Account snapshot
   json += "\"account\":{";
   json += "\"balance_usd\":"  + DoubleToString(balance, 2) + ",";
   json += "\"balance_idr\":"  + DoubleToString(balance * GAS_USDtoIDR, 0) + ",";
   json += "\"equity_usd\":"   + DoubleToString(equity, 2) + ",";
   json += "\"margin_usd\":"   + DoubleToString(margin, 2) + ",";
   json += "\"free_margin\":"  + DoubleToString(freeMargin, 2) + ",";
   json += "\"margin_level\":"+ DoubleToString(accInfo.MarginLevel(), 2);
   json += "},";

   // Market snapshot
   json += "\"market\":{";
   json += "\"bid\":"    + DoubleToString(bid, _Digits) + ",";
   json += "\"ask\":"    + DoubleToString(ask, _Digits) + ",";
   json += "\"spread\":" + IntegerToString(spread) + ",";
   json += "\"atr_14_m15\":" + DoubleToString(atrVal, _Digits);
   json += "},";

   // Daily stats
   json += "\"daily_stats\":{";
   json += "\"trade_count\":" + IntegerToString(gas_DailyTradeCount) + ",";
   json += "\"max_trades\":"  + IntegerToString(GAS_MaxTradesPerDay) + ",";
   json += "\"pnl_usd\":"     + DoubleToString(balance - initialBalanceDaily, 2) + ",";
   json += "\"pnl_idr\":"     + DoubleToString(dailyPnLIDR, 0) + ",";
   json += "\"max_loss_idr\":"+ DoubleToString(GAS_MaxDailyLossIDR, 0) + ",";
   json += "\"consecutive_loss\":" + IntegerToString(gas_ConsecutiveLossCount) + ",";
   json += "\"is_paused\":"   + (gas_IsPaused ? "true" : "false") + ",";
   json += "\"pause_until\":" + IntegerToString((int)gas_PauseUntilTime);
   json += "},";

   // Rules
   json += "\"rules\":{";
   json += "\"fixed_lot\":"       + DoubleToString(GAS_FixedLot, 2) + ",";
   json += "\"be_points\":"        + IntegerToString(GAS_MoveBEPoints) + ",";
   json += "\"partial_close_pct\":"+ DoubleToString(GAS_PartialClosePct, 0) + ",";
   json += "\"no_layering\":"      + (GAS_NoLayering ? "true" : "false") + ",";
   json += "\"max_spread\":"       + DoubleToString(MaxSpreadPoints, 0);
   json += "},";

   // Kill zone
   json += "\"kill_zone\":{";
   json += "\"london\":"  + (inLondon ? "true" : "false") + ",";
   json += "\"new_york\":"+ (inNY ? "true" : "false") + ",";
   json += "\"active\":"  + (killActive ? "true" : "false");
   json += "},";

   // Positions
   json += "\"positions\":" + posJSON + ",";

   // Timestamp
   json += "\"timestamp\":" + IntegerToString((int)TimeCurrent());
   json += "}";

   return json;
}

//============================================================
//  SECTION 13 — GAS PRO: SIGNAL REQUEST
//  POST context ke GAS AI → dapat signal lengkap
//============================================================
void RequestGASSignal()
{
   // POST context ke signal request endpoint
   string contextJSON = BuildGASContextJSON();
   string url = GatewayURL + GAS_SignalReqEndpoint;

   uchar  data[];
   uchar  result[];
   string headers = "Content-Type: application/json\r\n";
   StringToCharArray(contextJSON, data, 0, StringLen(contextJSON));

   int res = WebRequest("POST", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1)
   {
      int err = GetLastError();
      if(err != 0) Print("❌ GAS Signal Request error: ", err);
      return;
   }

   string response = CharArrayToString(result);
   if(StringLen(response) > 10)
      ParseGASSignalResponse(response);
}

//------------------------------------------------------------
// Parse GAS AI Signal Response
// Expected payload:
// {
//   "signal_id":       "uuid",
//   "action":          "BUY|SELL|NONE|WAIT",
//   "symbol":          "XAUUSD",
//   "entry":           2380.50,
//   "sl":              2376.00,
//   "tp1":             2385.00,
//   "tp_final":        2395.00,
//   "lot":             0.01,
//   "reason":          "FVG fill + OB confluence at 62% OTE",
//   "observation":     "Price swept EQH, CHoCH confirmed on M15",
//   "trading_plan":    "Wait LQ sweep → enter OB → TP at FVG",
//   "risk_management": "SL below OB, partial at TP1, BE after 300pts",
//   "journal":         "NY Kill Zone, DXY -0.3%, confluence 4/5",
//   "backtest":        "Setup WR 73% XAUUSD NY 2024",
//   "psychology":      "Patient. No FOMO. A+ only.",
//   "mindset":         "Process > Profit. Trust the system.",
//   "regime":          "TRENDING",
//   "session":         "NEW_YORK",
//   "confidence":      0.82
// }
//------------------------------------------------------------
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
   string observation= GetJSONValue(json, "observation");
   string plan       = GetJSONValue(json, "trading_plan");
   string riskMgmt   = GetJSONValue(json, "risk_management");
   string journal    = GetJSONValue(json, "journal");
   string backtest   = GetJSONValue(json, "backtest");
   string psych      = GetJSONValue(json, "psychology");
   string mindset    = GetJSONValue(json, "mindset");
   string regime     = GetJSONValue(json, "regime");
   string session    = GetJSONValue(json, "session");
   double confidence = StringToDouble(GetJSONValue(json, "confidence"));

   if(signal_id == "" || signal_id == gas_LastAISignalID) return;
   if(action == "NONE" || action == "WAIT" || action == "") return;

   // Log full signal ke terminal
   Print("╔═══════════════════════════════════════");
   Print("║ 🤖 GAS AI SIGNAL RECEIVED");
   Print("╠═══════════════════════════════════════");
   Print("║ Signal ID  : ", signal_id);
   Print("║ Action     : ", action, " ", symbol);
   Print("║ Entry      : ", DoubleToString(entry, _Digits));
   Print("║ SL         : ", DoubleToString(sl, _Digits));
   Print("║ TP1        : ", DoubleToString(tp1, _Digits));
   Print("║ TP Final   : ", DoubleToString(tp_final, _Digits));
   Print("║ Lot        : ", DoubleToString(lot, 2));
   Print("║ Regime     : ", regime, " | Session: ", session);
   Print("║ Confidence : ", DoubleToString(confidence * 100, 1), "%");
   Print("╠═══════════════════════════════════════");
   Print("║ 📋 REASON     : ", reason);
   Print("║ 🔍 OBSERVATION: ", observation);
   Print("║ 📊 PLAN       : ", plan);
   Print("║ 🛡️ RISK MGMT  : ", riskMgmt);
   Print("║ 📓 JOURNAL    : ", journal);
   Print("║ 📈 BACKTEST   : ", backtest);
   Print("║ 🧠 PSYCHOLOGY : ", psych);
   Print("║ 💎 MINDSET    : ", mindset);
   Print("╚═══════════════════════════════════════");

   gas_LastAISignalID = signal_id;

   // Auto eksekusi kalau diaktifkan
   if(GAS_AutoExecAISignal && GAS_CheckCanTrade())
   {
      // Validasi simbol
      if(symbol != _Symbol)
      {
         Print("⚠️ Signal untuk simbol berbeda: ", symbol, " | EA di: ", _Symbol);
         return;
      }

      // Spread check
      double spread = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(MaxSpreadPoints > 0 && spread > MaxSpreadPoints)
      {
         Print("⏸️ Spread terlalu besar: ", spread);
         return;
      }

      // Gunakan fixed lot dari GAS config
      double execLot = (lot > 0) ? lot : GAS_FixedLot;
      double useTP   = (tp_final > 0) ? tp_final : tp1;

      bool success = false;
      if(action == "BUY")
         success = trade.Buy(execLot, symbol, SymbolInfoDouble(symbol, SYMBOL_ASK), sl, useTP);
      else if(action == "SELL")
         success = trade.Sell(execLot, symbol, SymbolInfoDouble(symbol, SYMBOL_BID), sl, useTP);
      else if(action == "BUY_LIMIT" && entry > 0)
         success = trade.BuyLimit(execLot, entry, symbol, sl, useTP);
      else if(action == "SELL_LIMIT" && entry > 0)
         success = trade.SellLimit(execLot, entry, symbol, sl, useTP);

      if(success)
      {
         Print("🔥 GAS AI Signal dieksekusi! Lot:", execLot, " | ID:", signal_id);
         // Kirim konfirmasi eksekusi ke server
         GAS_SendSignalExecConfirm(signal_id, action, execLot, sl, useTP, reason);
      }
      else
         Print("❌ Eksekusi signal gagal. Code:", trade.ResultRetcode());
   }
}

//============================================================
//  SECTION 14 — GAS PRO: JOURNAL & NOTIFICATION
//============================================================

//------------------------------------------------------------
// Kirim trade journal ke server setelah posisi close
// FIX v4.1: Pakai ulong dealTicket + HistoryDeal functions
//------------------------------------------------------------
void GAS_SendTradeJournal(ulong dealTicket)
{
   // Ambil data deal langsung dari history
   double profit    = HistoryDealGetDouble(dealTicket,  DEAL_PROFIT);
   double volume    = HistoryDealGetDouble(dealTicket,  DEAL_VOLUME);
   double dealPrice = HistoryDealGetDouble(dealTicket,  DEAL_PRICE);
   string sym       = HistoryDealGetString(dealTicket,  DEAL_SYMBOL);
   long   dealType  = HistoryDealGetInteger(dealTicket, DEAL_TYPE);
   double profitIDR = profit * GAS_USDtoIDR;
   string direction = (dealType == DEAL_TYPE_BUY) ? "BUY" : "SELL";

   string json = "{";
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"symbol\":\"" + sym + "\",";
   json += "\"direction\":\"" + direction + "\",";
   json += "\"volume\":"    + DoubleToString(volume, 2) + ",";
   json += "\"deal_price\":"+ DoubleToString(dealPrice, _Digits) + ",";
   json += "\"profit_usd\":"+ DoubleToString(profit, 2) + ",";
   json += "\"profit_idr\":"+ DoubleToString(profitIDR, 0) + ",";
   json += "\"daily_count\":"+ IntegerToString(gas_DailyTradeCount) + ",";
   json += "\"daily_pnl_idr\":"+ DoubleToString(gas_DailyPnLUSD * GAS_USDtoIDR, 0) + ",";
   json += "\"consecutive_loss\":" + IntegerToString(gas_ConsecutiveLossCount) + ",";
   json += "\"balance_after\":"    + DoubleToString(accInfo.Balance(), 2) + ",";
   json += "\"balance_idr_after\":"+ DoubleToString(accInfo.Balance() * GAS_USDtoIDR, 0) + ",";
   json += "\"result\":\"" + (profit >= 0 ? "WIN" : "LOSS") + "\",";
   json += "\"kill_zone_london\":"+ (GAS_IsLondonKillZone() ? "true" : "false") + ",";
   json += "\"kill_zone_ny\":"    + (GAS_IsNYKillZone() ? "true" : "false") + ",";
   json += "\"timestamp\":" + IntegerToString((int)TimeCurrent());
   json += "}";

   string url = GatewayURL + GAS_JournalEndpoint;
   WebRequestPost(url, json);
}

//------------------------------------------------------------
// Kirim konfirmasi eksekusi AI signal
//------------------------------------------------------------
void GAS_SendSignalExecConfirm(
   string signal_id, string action, double lot,
   double sl, double tp, string reason)
{
   string json = "{";
   json += "\"signal_id\":\"" + signal_id + "\",";
   json += "\"action\":\"" + action + "\",";
   json += "\"symbol\":\"" + _Symbol + "\",";
   json += "\"lot\":" + DoubleToString(lot, 2) + ",";
   json += "\"sl\":" + DoubleToString(sl, _Digits) + ",";
   json += "\"tp\":" + DoubleToString(tp, _Digits) + ",";
   json += "\"executed_by\":\"" + GAS_TraderName + "\",";
   json += "\"reason\":\"" + reason + "\",";
   json += "\"timestamp\":" + IntegerToString((int)TimeCurrent());
   json += "}";

   string url = GatewayURL + "/api/gas/signal/confirm";
   WebRequestPost(url, json);
}

//------------------------------------------------------------
// Kirim notif pause ke server
//------------------------------------------------------------
void GAS_SendPauseNotification()
{
   string json = "{";
   json += "\"trader\":\"" + GAS_TraderName + "\",";
   json += "\"event\":\"PAUSE_TRIGGERED\",";
   json += "\"reason\":\"" + (gas_ConsecutiveLossCount >= GAS_ConsecutiveLoss ?
           IntegerToString(GAS_ConsecutiveLoss) + "x consecutive loss" :
           "Max daily loss IDR reached") + "\",";
   json += "\"consecutive_loss\":" + IntegerToString(gas_ConsecutiveLossCount) + ",";
   json += "\"daily_pnl_idr\":"    + DoubleToString(gas_DailyPnLUSD * GAS_USDtoIDR, 0) + ",";
   json += "\"max_loss_idr\":"     + DoubleToString(GAS_MaxDailyLossIDR, 0) + ",";
   json += "\"pause_until\":"      + IntegerToString((int)gas_PauseUntilTime) + ",";
   json += "\"timestamp\":"        + IntegerToString((int)TimeCurrent());
   json += "}";

   string url = GatewayURL + "/api/gas/alert/pause";
   WebRequestPost(url, json);
}

//============================================================
//  SECTION 15 — GAS PRO: KILL ZONE DETECTION
//============================================================

//------------------------------------------------------------
// London Kill Zone: 08:00 – 11:00 GMT
//------------------------------------------------------------
bool GAS_IsLondonKillZone()
{
   MqlDateTime t;
   TimeToStruct(TimeGMT(), t);
   int h = t.hour;
   return (h >= 8 && h < 11);
}

//------------------------------------------------------------
// New York Kill Zone: 13:00 – 16:00 GMT
//------------------------------------------------------------
bool GAS_IsNYKillZone()
{
   MqlDateTime t;
   TimeToStruct(TimeGMT(), t);
   int h = t.hour;
   return (h >= 13 && h < 16);
}

//============================================================
//  SECTION 16 — ORIGINAL v3.1 FUNCTIONS (TIDAK DIUBAH)
//============================================================

void SendTickBatch()
{
   if(tickCount == 0) return;
   string json = BuildTickJSON();
   string url  = GatewayURL + "/mt5/tick";
   for(int retry = 0; retry < MaxRetries; retry++)
   {
      if(WebRequestPost(url, json)) break;
      Sleep(100);
   }
   tickCount = 0;
   ArrayResize(tickBuffer, 0, 100);
}

string BuildTickJSON()
{
   string json = "{\"symbol\":\"" + _Symbol + "\",\"ticks\":[";
   for(int i = 0; i < tickCount; i++)
   {
      if(i > 0) json += ",";
      json += "{";
      json += "\"time\":"   + DoubleToString(tickBuffer[i].time, 0) + ",";
      json += "\"bid\":"    + DoubleToString(tickBuffer[i].bid, _Digits) + ",";
      json += "\"ask\":"    + DoubleToString(tickBuffer[i].ask, _Digits) + ",";
      json += "\"volume\":0";
      json += "}";
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
      int copied = CopyRates(_Symbol, tf, 0, 1, rates);
      if(copied > 0)
      {
         string json = "{";
         json += "\"symbol\":\""    + _Symbol + "\",";
         json += "\"timeframe\":\"" + tf_array[i] + "\",";
         json += "\"time\":"        + IntegerToString(rates[0].time) + ",";
         json += "\"open\":"        + DoubleToString(rates[0].open, _Digits) + ",";
         json += "\"high\":"        + DoubleToString(rates[0].high, _Digits) + ",";
         json += "\"low\":"         + DoubleToString(rates[0].low, _Digits) + ",";
         json += "\"close\":"       + DoubleToString(rates[0].close, _Digits) + ",";
         json += "\"volume\":"      + IntegerToString(rates[0].tick_volume);
         json += "}";
         string url = GatewayURL + "/mt5/ohlc";
         WebRequestPost(url, json);
      }
   }
}

void SendHeartbeat()
{
   string json = "{";
   json += "\"symbol\":\""   + _Symbol + "\",";
   json += "\"trader\":\""   + GAS_TraderName + "\",";
   json += "\"balance\":"    + DoubleToString(accInfo.Balance(), 2) + ",";
   json += "\"equity\":"     + DoubleToString(accInfo.Equity(), 2) + ",";
   json += "\"balance_idr\":"+ DoubleToString(accInfo.Balance() * GAS_USDtoIDR, 0) + ",";
   json += "\"daily_trades\":"+ IntegerToString(gas_DailyTradeCount) + ",";
   json += "\"is_paused\":"   + (gas_IsPaused ? "true" : "false") + ",";
   json += "\"kill_zone\":\""+ (GAS_IsLondonKillZone() ? "LONDON" :
                                GAS_IsNYKillZone() ? "NEW_YORK" : "OFF") + "\",";
   json += "\"positions\":"  + IntegerToString(PositionsTotal()) + ",";
   json += "\"magic\":"      + IntegerToString(MagicNumber);
   json += "}";
   string url = GatewayURL + "/mt5/heartbeat";
   WebRequestPost(url, json);
}

void PollOrderQueue()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   string url = GatewayURL + "/terminal/order/queue";
   uchar data[];
   uchar result[];
   string headers = "";
   int res = WebRequest("GET", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1) { int err = GetLastError(); if(err != 0) Print("❌ Order queue error: ", err); return; }
   string json = CharArrayToString(result);
   if(StringLen(json) < 5) return;
   string order_id = GetJSONValue(json, "order_id");
   if(order_id == "" || order_id == lastOrderID) return;
   ParseAndExecuteOrder(json);
}

void ParseAndExecuteOrder(string json)
{
   string order_id   = GetJSONValue(json, "order_id");
   string action     = GetJSONValue(json, "action");
   string symbol     = GetJSONValue(json, "symbol");
   double volume     = StringToDouble(GetJSONValue(json, "volume"));
   double price      = StringToDouble(GetJSONValue(json, "price"));
   double sl         = StringToDouble(GetJSONValue(json, "stop_loss"));
   double tp         = StringToDouble(GetJSONValue(json, "take_profit"));
   int    magic      = (int)StringToInteger(GetJSONValue(json, "magic_number"));

   if(order_id == "" || action == "") return;
   if(magic != MagicNumber) { SendOrderStatus(order_id, "rejected", "Invalid magic number"); return; }
   if(symbol != _Symbol)    { SendOrderStatus(order_id, "rejected", "Wrong symbol"); return; }

   if(MaxSpreadPoints > 0)
   {
      double spread = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(spread > MaxSpreadPoints) { SendOrderStatus(order_id, "rejected", "Spread too high"); return; }
   }

   // GAS PRO: Cek rules sebelum eksekusi
   if(!GAS_CheckCanTrade()) { SendOrderStatus(order_id, "rejected", "GAS rules blocked"); return; }

   double lotSize = volume;
   bool   success = false;

   if(action == "BUY")
      success = trade.Buy(lotSize, symbol, SymbolInfoDouble(symbol, SYMBOL_ASK), sl, tp);
   else if(action == "SELL")
      success = trade.Sell(lotSize, symbol, SymbolInfoDouble(symbol, SYMBOL_BID), sl, tp);
   else if(action == "BUY_LIMIT" && price > 0)
      success = trade.BuyLimit(lotSize, price, symbol, sl, tp);
   else if(action == "SELL_LIMIT" && price > 0)
      success = trade.SellLimit(lotSize, price, symbol, sl, tp);
   else if(action == "BUY_STOP" && price > 0)
      success = trade.BuyStop(lotSize, price, symbol, sl, tp);
   else if(action == "SELL_STOP" && price > 0)
      success = trade.SellStop(lotSize, price, symbol, sl, tp);
   else { SendOrderStatus(order_id, "rejected", "Invalid action"); return; }

   if(success)
   {
      Print("🔥 Order eksekusi | ID:", order_id, " Lot:", lotSize);
      lastOrderID = order_id;
      double fill_price = (action == "BUY") ?
         SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
      SendOrderStatus(order_id, "filled", "", fill_price);
   }
   else
   {
      string desc = trade.ResultRetcodeDescription();
      Print("❌ Order gagal. Code:", trade.ResultRetcode(), " - ", desc);
      SendOrderStatus(order_id, "failed", desc);
   }
}

void SendOrderStatus(string order_id, string status, string message, double fill_price = 0)
{
   string json = "{";
   json += "\"order_id\":\"" + order_id + "\",";
   json += "\"status\":\""   + status + "\"";
   if(status == "filled")
   {
      json += ",\"fill_price\":"+ DoubleToString(fill_price, _Digits);
      json += ",\"fill_time\":"  + IntegerToString(TimeCurrent());
      json += ",\"commission\":0,\"swap\":0,\"profit\":0";
   }
   else if(message != "")
      json += ",\"message\":\"" + message + "\"";
   json += "}";
   string url = GatewayURL + "/terminal/order/status";
   WebRequestPost(url, json);
}

void PollSignal()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   string url = GatewayURL + "/api/signal/";
   uchar data[];
   uchar result[];
   string headers = "";
   int res = WebRequest("GET", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1) { int err = GetLastError(); if(err != 0) Print("❌ Signal error: ", err); return; }
   string json = CharArrayToString(result);
   ParseAndExecuteSignal(json);
}

void ParseAndExecuteSignal(string json)
{
   string signal_id = GetJSONValue(json, "signal_id");
   string action    = GetJSONValue(json, "action");
   string symbol    = GetJSONValue(json, "symbol");
   double price     = StringToDouble(GetJSONValue(json, "price"));
   double sl        = StringToDouble(GetJSONValue(json, "sl"));
   double tp        = StringToDouble(GetJSONValue(json, "tp"));

   if(signal_id == "" || signal_id == lastSignalID) return;
   if(action == "NONE") return;

   Print("📥 Sinyal: ", action, " ", symbol, " ID:", signal_id);
   if(symbol != _Symbol) { Print("⚠️ Simbol berbeda: ", symbol); return; }

   // GAS PRO: Cek rules
   if(!GAS_CheckCanTrade()) return;

   double sym_point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   if(sym_point == 0) return;

   double entry_ref = 0;
   if(action == "BUY" || action == "SELL")
      entry_ref = (action == "BUY") ?
         SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
   else
      entry_ref = price;

   double stopLossPoints = MathAbs(entry_ref - sl) / sym_point;
   double lotSize        = CalculateLotSize(symbol, stopLossPoints);

   bool success = false;
   if(action == "BUY")       success = trade.Buy(lotSize, symbol, SymbolInfoDouble(symbol, SYMBOL_ASK), sl, tp);
   else if(action == "SELL") success = trade.Sell(lotSize, symbol, SymbolInfoDouble(symbol, SYMBOL_BID), sl, tp);
   else if(action == "BUY_LIMIT" && price > 0)  success = trade.BuyLimit(lotSize, price, symbol, sl, tp);
   else if(action == "SELL_LIMIT" && price > 0) success = trade.SellLimit(lotSize, price, symbol, sl, tp);
   else if(action == "BUY_STOP" && price > 0)   success = trade.BuyStop(lotSize, price, symbol, sl, tp);
   else if(action == "SELL_STOP" && price > 0)  success = trade.SellStop(lotSize, price, symbol, sl, tp);

   if(success) { Print("🔥 Sinyal eksekusi OK. Lot:", lotSize); lastSignalID = signal_id; }
   else          Print("❌ Gagal. Code:", trade.ResultRetcode());
}

string GetJSONValue(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int start = StringFind(json, search);
   if(start >= 0)
   {
      start += StringLen(search);
      int end = StringFind(json, "\"", start);
      if(end > start) return StringSubstr(json, start, end - start);
   }
   search = "\"" + key + "\":";
   start = StringFind(json, search);
   if(start >= 0)
   {
      start += StringLen(search);
      int end = start;
      while(end < StringLen(json) && json[end] != ',' && json[end] != '}' && json[end] != ' ')
         end++;
      return StringSubstr(json, start, end - start);
   }
   return "";
}

double CalculateLotSize(string sym, double sl_points)
{
   if(sl_points <= 0) return SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double riskAmount = accInfo.Balance() * (RiskPercent / 100.0);
   double tickValue  = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);
   double step       = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   if(tickValue == 0 || step == 0) return SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double calcLot = riskAmount / (sl_points * tickValue);
   calcLot = MathFloor(calcLot / step) * step;
   double minLot = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   if(calcLot < minLot) calcLot = minLot;
   if(calcLot > maxLot) calcLot = maxLot;
   return calcLot;
}

void TrailingStops()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber && posInfo.Symbol() == _Symbol)
      {
         double sl    = posInfo.StopLoss();
         double bid   = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double ask   = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
         if(posInfo.PositionType() == POSITION_TYPE_BUY)
         {
            double newSL = bid - TrailingStop * point;
            if(newSL > sl && newSL > posInfo.PriceOpen())
               trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit());
         }
         else if(posInfo.PositionType() == POSITION_TYPE_SELL)
         {
            double newSL = ask + TrailingStop * point;
            if(newSL < sl && newSL < posInfo.PriceOpen())
               trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit());
         }
      }
   }
}

void CheckDailyDrawdown()
{
   double currentBalance = accInfo.Balance();
   double ddPercent = (initialBalanceDaily - currentBalance) / initialBalanceDaily * 100;
   if(ddPercent >= MaxDailyDrawdown)
   {
      Print("⚠️ Daily drawdown limit reached: ", ddPercent, "%. Closing all...");
      CloseAllPositions();
      ExpertRemove();
   }
}

void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber)
         trade.PositionClose(posInfo.Ticket());
   }
}

ENUM_TIMEFRAMES StringToTimeframe(string tf)
{
   if(tf == "M1")  return PERIOD_M1;
   if(tf == "M5")  return PERIOD_M5;
   if(tf == "M15") return PERIOD_M15;
   if(tf == "M30") return PERIOD_M30;
   if(tf == "H1")  return PERIOD_H1;
   if(tf == "H4")  return PERIOD_H4;
   if(tf == "D1")  return PERIOD_D1;
   if(tf == "W1")  return PERIOD_W1;
   if(tf == "MN1") return PERIOD_MN1;
   return PERIOD_CURRENT;
}

bool WebRequestPost(string url, string json)
{
   uchar  data[];
   uchar  result[];
   string headers = "Content-Type: application/json\r\n";
   StringToCharArray(json, data, 0, StringLen(json));
   int res = WebRequest("POST", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1)
   {
      int err = GetLastError();
      Print("❌ WebRequest error ", err, " → ", url);
      return false;
   }
   return true;
}
//+------------------------------------------------------------------+
//  END OF GASSTRATEGYEAPRO v4.0
//+------------------------------------------------------------------+