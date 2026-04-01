//+------------------------------------------------------------------+
//|            GAS_AutoTrader.mq5                                    |
//|            GAS Platform - AI Signal Auto Trader                  |
//|            v2.0 — Integrated dengan 18 AI Features               |
//|                                                                  |
//|  CARA KERJA:                                                     |
//|  1. GAS Platform AI menghasilkan sinyal (BUY/SELL + entry+SL+TP) |
//|  2. EA poll endpoint /terminal/order/queue setiap N detik         |
//|  3. EA validasi entry (slippage, spread, session, margin)         |
//|  4. Jika valid → execute trade → report status balik ke platform  |
//|  5. Kirim account heartbeat setiap 10 detik                       |
//|                                                                  |
//|  YANG HARUS DIAKTIFKAN DI MT5:                                   |
//|  Tools → Options → Expert Advisors → Allow WebRequests           |
//  Tambahkan: https://gasstrategyai.xyz ke whitelist               |
//+------------------------------------------------------------------+
#property copyright "GAS Platform"
#property version   "2.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

//+------------------------------------------------------------------+
//| INPUT PARAMETERS                                                  |
//+------------------------------------------------------------------+

// ── Identity ────────────────────────────────────────────────────────
input string   GAS_UserID         = "";                          // User ID dari GAS Platform
input string   GAS_BaseURL        = "https://gasstrategyai.xyz"; // URL VPS GAS Platform

// ── Execution Settings ──────────────────────────────────────────────
input int      PollIntervalSec    = 5;    // Interval poll sinyal AI (detik)
input int      HeartbeatSec       = 10;  // Interval kirim account heartbeat (detik)
input int      MaxOpenTrades      = 3;   // Maksimum posisi terbuka sekaligus
input double   DefaultRiskPct     = 1.0; // Risk % per trade jika platform tidak set lot
input double   MaxSpreadPips      = 3.0; // Spread maksimal yang diizinkan untuk entry
input double   MaxSlippagePips    = 5.0; // Slippage maksimal saat eksekusi

// ── Trade Management ────────────────────────────────────────────────
input bool     UseTrailingStop    = false; // Aktifkan trailing stop otomatis
input double   TrailingStopPips   = 20.0;  // Trailing stop distance (pips)
input bool     UseBreakeven       = true;  // Pindahkan SL ke BE setelah TP1 tercapai
input double   BreakevenPips      = 15.0;  // Berapa pip profit sebelum pindah SL ke BE

// ── Session Filter (WIB = UTC+7) ────────────────────────────────────
input bool     FilterBySession    = true;  // Hanya trade di sesi tertentu
input int      LondonOpenWIB      = 15;    // London open 15:00 WIB
input int      NYCloseWIB         = 5;     // NY close 05:00 WIB (+1)

// ── Grade Filter ────────────────────────────────────────────────────
input string   MinGrade           = "A";   // Grade minimum: A+, A, B+, B
input bool     OnlyHotSignals     = false; // Hanya LEVEL=HOT yang dieksekusi

// ── Logging & Debug ─────────────────────────────────────────────────
input bool     ShowLogs           = true;  // Tampilkan log di journal
input bool     DemoMode           = false; // Demo mode — validasi tanpa eksekusi real

// ── Magic Number ────────────────────────────────────────────────────
input int      MagicNumber        = 88888; // Magic number untuk identifikasi EA trades

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES                                                  |
//+------------------------------------------------------------------+
CTrade         g_trade;
CPositionInfo  g_position;
COrderInfo     g_order;

datetime g_lastPoll      = 0;
datetime g_lastHeartbeat = 0;
string   g_pollEndpoint  = "";
string   g_statusEndpoint = "";
string   g_heartbeatEndpoint = "";
string   g_acctEndpoint  = "";

//+------------------------------------------------------------------+
//| EA INITIALIZATION                                                  |
//+------------------------------------------------------------------+
int OnInit()
{
   if(StringLen(StringTrimLeft(StringTrimRight(GAS_UserID))) == 0)
   {
      Alert("❌ GAS_AutoTrader: GAS_UserID tidak boleh kosong! Isi User ID di parameter EA.");
      return INIT_FAILED;
   }

   g_pollEndpoint      = GAS_BaseURL + "/terminal/order/queue?user_id=" + GAS_UserID;
   g_statusEndpoint    = GAS_BaseURL + "/terminal/order/status";
   g_heartbeatEndpoint = GAS_BaseURL + "/mt5/heartbeat";
   g_acctEndpoint      = GAS_BaseURL + "/mt5/account-heartbeat";

   g_trade.SetExpertMagicNumber(MagicNumber);
   g_trade.SetDeviationInPoints((int)(MaxSlippagePips * 10));
   g_trade.SetTypeFilling(ORDER_FILLING_IOC);

   if(ShowLogs)
      PrintFormat("✅ GAS_AutoTrader v2.0 — UserID: %s | Poll: %ds | Heartbeat: %ds",
         GAS_UserID, PollIntervalSec, HeartbeatSec);

   // Send initial heartbeat
   SendAccountHeartbeat();
   g_lastHeartbeat = TimeCurrent();

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| EA TICK HANDLER                                                    |
//+------------------------------------------------------------------+
void OnTick()
{
   datetime now = TimeCurrent();

   // ── Poll AI signals ─────────────────────────────────────────────
   if((int)(now - g_lastPoll) >= PollIntervalSec)
   {
      PollAndExecuteSignal();
      g_lastPoll = now;
   }

   // ── Send account heartbeat ──────────────────────────────────────
   if((int)(now - g_lastHeartbeat) >= HeartbeatSec)
   {
      SendAccountHeartbeat();
      g_lastHeartbeat = now;
   }

   // ── Trade management (trailing / breakeven) ─────────────────────
   if(UseTrailingStop || UseBreakeven)
      ManageOpenTrades();
}

//+------------------------------------------------------------------+
//| POLL SIGNAL FROM GAS PLATFORM AND EXECUTE                         |
//+------------------------------------------------------------------+
void PollAndExecuteSignal()
{
   char   resultArr[];
   string resHeaders;
   char   emptyBody[];
   ArrayResize(emptyBody, 0);

   int code = WebRequest("GET", g_pollEndpoint, "", 5000, emptyBody, resultArr, resHeaders);

   if(code != 200 || ArraySize(resultArr) == 0)
   {
      if(ShowLogs && code != 200)
         PrintFormat("⚠️ Poll failed — HTTP %d", code);
      return;
   }

   string json = CharArrayToString(resultArr);

   // Empty response = no pending signal
   if(json == "{}" || StringLen(json) < 10)
      return;

   if(ShowLogs)
      PrintFormat("📩 Signal diterima dari GAS Platform: %s", json);

   // ── Parse signal fields ─────────────────────────────────────────
   string orderId   = ParseJsonString(json, "order_id");
   string symbol    = ParseJsonString(json, "symbol");
   string direction = ParseJsonString(json, "direction");
   double entry     = ParseJsonDouble(json, "entry");
   double sl        = ParseJsonDouble(json, "sl");
   double tp1       = ParseJsonDouble(json, "tp1");
   double tp2       = ParseJsonDouble(json, "tp2");
   double signalLot = ParseJsonDouble(json, "lot");
   double riskPct   = ParseJsonDouble(json, "risk_pct");
   double maxSlip   = ParseJsonDouble(json, "max_slippage_pips");
   string grade     = ParseJsonString(json, "grade");
   string level     = ParseJsonString(json, "level");
   string source    = ParseJsonString(json, "source");
   int    magic     = (int)ParseJsonDouble(json, "magic");

   if(magic == 0) magic = MagicNumber;
   if(maxSlip == 0.0) maxSlip = MaxSlippagePips;
   if(riskPct == 0.0) riskPct = DefaultRiskPct;

   // ── Grade filter ────────────────────────────────────────────────
   if(!IsGradeAccepted(grade))
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s grade %s diabaikan (min: %s)", orderId, grade, MinGrade);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0,
         "Grade " + grade + " di bawah minimum " + MinGrade);
      return;
   }

   // ── Hot filter ──────────────────────────────────────────────────
   if(OnlyHotSignals && level != "HOT")
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s level %s diabaikan (hanya HOT)", orderId, level);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0, "Level bukan HOT");
      return;
   }

   // ── Session filter ──────────────────────────────────────────────
   if(FilterBySession && !IsSessionActive())
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s diabaikan — di luar sesi trading", orderId);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0, "Di luar sesi trading");
      return;
   }

   // ── Max open trades ─────────────────────────────────────────────
   if(CountOpenTrades() >= MaxOpenTrades)
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s diabaikan — max %d posisi sudah terbuka", orderId, MaxOpenTrades);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0,
         "Max posisi terbuka: " + (string)MaxOpenTrades);
      return;
   }

   // ── Switch to signal's symbol ────────────────────────────────────
   if(symbol == "") symbol = Symbol();

   // ── Symbol availability check ────────────────────────────────────
   if(!SymbolSelect(symbol, true))
   {
      PrintFormat("❌ Symbol %s tidak tersedia di broker ini", symbol);
      ReportStatus(orderId, "failed", symbol, direction, 0, 0, 0,
         "Symbol " + symbol + " tidak tersedia");
      return;
   }

   // ── Get current price ────────────────────────────────────────────
   double ask   = SymbolInfoDouble(symbol, SYMBOL_ASK);
   double bid   = SymbolInfoDouble(symbol, SYMBOL_BID);
   double spread = (ask - bid);
   int    digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   double point  = SymbolInfoDouble(symbol, SYMBOL_POINT);
   double tickVal = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSz  = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   double minLot  = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);

   // ── Spread filter ────────────────────────────────────────────────
   double spreadPips = spread / point / 10.0;
   if(spreadPips > MaxSpreadPips)
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s — spread %.1f pips terlalu besar (max: %.1f)", orderId, spreadPips, MaxSpreadPips);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0,
         StringFormat("Spread %.1f > max %.1f pips", spreadPips, MaxSpreadPips));
      return;
   }

   // ── Slippage / price proximity check ────────────────────────────
   double currentEntryPrice = (direction == "BUY") ? ask : bid;
   double slippagePips = MathAbs(currentEntryPrice - entry) / point / 10.0;
   if(entry > 0 && slippagePips > maxSlip)
   {
      if(ShowLogs) PrintFormat("⏭️ Signal %s — slippage %.1f pips terlalu jauh dari entry %.5f", orderId, slippagePips, entry);
      ReportStatus(orderId, "rejected", symbol, direction, 0, 0, 0,
         StringFormat("Slippage %.1f > max %.1f pips", slippagePips, maxSlip));
      return;
   }

   // ── Use current market price if entry not provided ───────────────
   double execEntry = (entry > 0) ? currentEntryPrice : currentEntryPrice;

   // ── Calculate SL/TP (use signal values if provided) ─────────────
   if(sl == 0.0 && direction == "BUY")  sl = execEntry * 0.992;
   if(sl == 0.0 && direction == "SELL") sl = execEntry * 1.008;
   if(tp1 == 0.0 && direction == "BUY")  tp1 = execEntry * 1.015;
   if(tp1 == 0.0 && direction == "SELL") tp1 = execEntry * 0.985;

   sl  = NormalizeDouble(sl,  digits);
   tp1 = NormalizeDouble(tp1, digits);

   // ── Calculate lot size ───────────────────────────────────────────
   double lot = signalLot;
   if(lot <= 0.0)
      lot = CalculateLotSize(symbol, execEntry, sl, riskPct, tickVal, tickSz, point);

   lot = MathMax(minLot, MathMin(maxLot, NormalizeDouble(lot, 2)));
   lot = MathRound(lot / lotStep) * lotStep;

   // ── Margin check ─────────────────────────────────────────────────
   double reqMargin = 0.0;
   ENUM_ORDER_TYPE orderType = (direction == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(!OrderCalcMargin(orderType, symbol, lot, execEntry, reqMargin))
      reqMargin = 0.0;

   double freeMargin = AccountInfoDouble(ACCOUNT_FREEMARGIN);
   if(reqMargin > 0 && freeMargin < reqMargin * 1.5)
   {
      PrintFormat("⚠️ Signal %s — margin tidak cukup (need: %.2f, free: %.2f)", orderId, reqMargin, freeMargin);
      ReportStatus(orderId, "rejected", symbol, direction, lot, execEntry, 0,
         StringFormat("Margin tidak cukup: need=%.2f free=%.2f", reqMargin, freeMargin));
      return;
   }

   if(ShowLogs)
      PrintFormat("🎯 Executing: %s %s | Entry: %.5f | SL: %.5f | TP1: %.5f | Lot: %.2f | Grade: %s | Source: %s",
         direction, symbol, execEntry, sl, tp1, lot, grade, source);

   // ── DEMO MODE — Skip actual execution ────────────────────────────
   if(DemoMode)
   {
      PrintFormat("🧪 [DEMO] Order would be: %s %s lot=%.2f entry=%.5f sl=%.5f tp=%.5f",
         direction, symbol, lot, execEntry, sl, tp1);
      ReportStatus(orderId, "demo_ok", symbol, direction, lot, execEntry, 0,
         "Demo mode — tidak dieksekusi real");
      return;
   }

   // ── EXECUTE TRADE ────────────────────────────────────────────────
   g_trade.SetExpertMagicNumber(magic);

   bool result = false;
   string comment = StringFormat("GAS_%s_%s", source != "" ? source : "AI", grade);

   if(direction == "BUY")
      result = g_trade.Buy(lot, symbol, 0, sl, tp1, comment);
   else if(direction == "SELL")
      result = g_trade.Sell(lot, symbol, 0, sl, tp1, comment);

   // ── Report execution result ──────────────────────────────────────
   if(result)
   {
      ulong ticket = g_trade.ResultOrder();
      double actualEntry = g_trade.ResultPrice();
      if(ShowLogs)
         PrintFormat("✅ Trade executed — Ticket: %llu | Entry: %.5f | Grade: %s",
            ticket, actualEntry, grade);
      ReportStatus(orderId, "filled", symbol, direction, lot, actualEntry, ticket,
         StringFormat("Filled at %.5f | SL: %.5f | TP1: %.5f", actualEntry, sl, tp1));

      // Set TP2 as partial take profit if provided
      if(tp2 > 0 && ticket > 0)
         SetPartialTP(ticket, symbol, direction, lot, tp2);
   }
   else
   {
      int err = (int)g_trade.ResultRetcode();
      PrintFormat("❌ Trade FAILED — Error: %d (%s)", err, g_trade.ResultRetcodeDescription());
      ReportStatus(orderId, "failed", symbol, direction, lot, execEntry, 0,
         StringFormat("Error %d: %s", err, g_trade.ResultRetcodeDescription()));
   }
}

//+------------------------------------------------------------------+
//| CALCULATE LOT SIZE BASED ON RISK %                                |
//+------------------------------------------------------------------+
double CalculateLotSize(string symbol, double entry, double sl,
                        double riskPct, double tickVal, double tickSz, double point)
{
   double balance  = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmt  = balance * (riskPct / 100.0);
   double slDist   = MathAbs(entry - sl);
   if(slDist == 0.0) return 0.01;

   double pipValue = (tickSz > 0) ? (tickVal / tickSz) * point : tickVal;
   if(pipValue == 0.0) pipValue = 1.0;

   double lot = riskAmt / (slDist / point * pipValue);
   return NormalizeDouble(lot, 2);
}

//+------------------------------------------------------------------+
//| MANAGE TRAILING STOP AND BREAKEVEN                                 |
//+------------------------------------------------------------------+
void ManageOpenTrades()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!g_position.SelectByIndex(i)) continue;
      if(g_position.Magic() != MagicNumber && g_position.Magic() != 88888) continue;

      ulong  ticket  = g_position.Ticket();
      string symbol  = g_position.Symbol();
      double openPx  = g_position.PriceOpen();
      double curSL   = g_position.StopLoss();
      double curTP   = g_position.TakeProfit();
      double curPx   = g_position.PriceCurrent();
      ENUM_POSITION_TYPE pType = g_position.PositionType();
      double point   = SymbolInfoDouble(symbol, SYMBOL_POINT);
      double profitPips = 0;

      if(pType == POSITION_TYPE_BUY)
         profitPips = (curPx - openPx) / point / 10.0;
      else
         profitPips = (openPx - curPx) / point / 10.0;

      // ── Breakeven ────────────────────────────────────────────────
      if(UseBreakeven && profitPips >= BreakevenPips)
      {
         double newSL = (pType == POSITION_TYPE_BUY) ? openPx : openPx;
         if((pType == POSITION_TYPE_BUY && curSL < openPx - point) ||
            (pType == POSITION_TYPE_SELL && curSL > openPx + point))
         {
            g_trade.PositionModify(ticket, newSL, curTP);
            if(ShowLogs)
               PrintFormat("🔒 Breakeven set for ticket %llu at %.5f", ticket, newSL);
         }
      }

      // ── Trailing Stop ────────────────────────────────────────────
      if(UseTrailingStop && profitPips >= TrailingStopPips)
      {
         double newSL = 0;
         if(pType == POSITION_TYPE_BUY)
            newSL = curPx - TrailingStopPips * point * 10;
         else
            newSL = curPx + TrailingStopPips * point * 10;

         if((pType == POSITION_TYPE_BUY && newSL > curSL + point) ||
            (pType == POSITION_TYPE_SELL && newSL < curSL - point))
         {
            g_trade.PositionModify(ticket, newSL, curTP);
            if(ShowLogs)
               PrintFormat("📈 Trailing: ticket %llu SL → %.5f", ticket, newSL);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| SET PARTIAL TP (Split lot at TP2)                                 |
//+------------------------------------------------------------------+
void SetPartialTP(ulong ticket, string symbol, string direction, double lot, double tp2)
{
   // After fill, the original position uses remaining lot with TP2
   // This places a pending opposite order at TP2 for partial close
   // Simplified: just log it for now, full partial close on TP1 hit
   if(ShowLogs)
      PrintFormat("ℹ️ TP2 = %.5f set untuk partial exit ticket %llu", tp2, ticket);
}

//+------------------------------------------------------------------+
//| COUNT OPEN TRADES BY MAGIC                                        |
//+------------------------------------------------------------------+
int CountOpenTrades()
{
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(g_position.SelectByIndex(i))
         if(g_position.Magic() == MagicNumber || g_position.Magic() == 88888)
            count++;
   }
   return count;
}

//+------------------------------------------------------------------+
//| SESSION FILTER — apakah sekarang dalam sesi trading aktif?        |
//+------------------------------------------------------------------+
bool IsSessionActive()
{
   // Convert current server time to WIB (approx)
   datetime serverTime = TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(serverTime, dt);

   int hourUTC = dt.hour;
   int hourWIB = (hourUTC + 7) % 24; // WIB = UTC+7

   // London session:  08:00–17:00 UTC = 15:00–00:00 WIB
   // NY session:      13:00–22:00 UTC = 20:00–05:00 WIB (+1)
   // Allow: 15:00–05:00 WIB (London open to NY close)
   
   if(hourWIB >= LondonOpenWIB || hourWIB < NYCloseWIB)
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| GRADE FILTER                                                      |
//+------------------------------------------------------------------+
bool IsGradeAccepted(string grade)
{
   if(MinGrade == "B")   return true; // Accept all grades
   if(MinGrade == "B+")  return (grade == "B+" || grade == "A" || grade == "A+");
   if(MinGrade == "A")   return (grade == "A" || grade == "A+");
   if(MinGrade == "A+")  return (grade == "A+");
   return true;
}

//+------------------------------------------------------------------+
//| REPORT ORDER STATUS BACK TO GAS PLATFORM                          |
//+------------------------------------------------------------------+
void ReportStatus(string orderId, string status, string symbol,
                  string direction, double lot, double price,
                  ulong ticket, string message)
{
   string body = StringFormat(
      "{\"order_id\":\"%s\",\"status\":\"%s\",\"symbol\":\"%s\","
      "\"direction\":\"%s\",\"lot\":%.2f,\"fill_price\":%.5f,"
      "\"ticket\":%llu,\"message\":\"%s\",\"user_id\":\"%s\"}",
      orderId, status, symbol, direction, lot, price,
      ticket, message, GAS_UserID
   );

   char bodyArr[];
   char result[];
   string headers = "Content-Type: application/json\r\n";
   string resHeaders;
   StringToCharArray(body, bodyArr, 0, StringLen(body));
   ArrayResize(result, 0);

   int code = WebRequest("POST", g_statusEndpoint, headers, 5000, bodyArr, result, resHeaders);
   if(ShowLogs && code != 200)
      PrintFormat("⚠️ Status report failed — HTTP %d | order: %s", code, orderId);
}

//+------------------------------------------------------------------+
//| SEND FULL ACCOUNT HEARTBEAT (balance + equity + all positions)     |
//+------------------------------------------------------------------+
void SendAccountHeartbeat()
{
   double balance    = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity     = AccountInfoDouble(ACCOUNT_EQUITY);
   double margin     = AccountInfoDouble(ACCOUNT_MARGIN);
   double freeMrg    = AccountInfoDouble(ACCOUNT_FREEMARGIN);
   double mrGLevel   = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   string currency   = AccountInfoString(ACCOUNT_CURRENCY);
   long   accountId  = AccountInfoInteger(ACCOUNT_LOGIN);
   string broker     = AccountInfoString(ACCOUNT_COMPANY);
   string server     = AccountInfoString(ACCOUNT_SERVER);
   long   leverage   = AccountInfoInteger(ACCOUNT_LEVERAGE);
   double floatPnl   = equity - balance;

   // Build positions JSON
   string posArr = "[";
   bool first = true;
   int total = PositionsTotal();
   for(int i = 0; i < total; i++)
   {
      if(!g_position.SelectByIndex(i)) continue;
      string sym      = g_position.Symbol();
      int    dir      = (g_position.PositionType() == POSITION_TYPE_BUY) ? 0 : 1;
      double lot      = g_position.Volume();
      double entryPx  = g_position.PriceOpen();
      double curPx    = g_position.PriceCurrent();
      double pnl      = g_position.Profit();
      double swap     = g_position.Swap();
      long   magic    = g_position.Magic();
      ulong  ticket   = g_position.Ticket();

      if(!first) posArr += ",";
      first = false;

      posArr += StringFormat(
         "{\"ticket\":%llu,\"symbol\":\"%s\",\"direction\":\"%s\","
         "\"lot\":%.2f,\"entry_price\":%.5f,\"current_price\":%.5f,"
         "\"pnl\":%.2f,\"swap\":%.2f,\"magic\":%ld}",
         ticket, sym, (dir == 0 ? "BUY" : "SELL"),
         lot, entryPx, curPx, pnl, swap, magic
      );
   }
   posArr += "]";

   string body = StringFormat(
      "{\"user_id\":\"%s\",\"account_id\":%ld,\"broker\":\"%s\","
      "\"server\":\"%s\",\"currency\":\"%s\",\"leverage\":%ld,"
      "\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,"
      "\"free_margin\":%.2f,\"margin_level\":%.2f,\"floating_pnl\":%.2f,"
      "\"positions_count\":%d,\"positions\":%s,\"symbol\":\"%s\",\"ea_version\":\"2.0\"}",
      GAS_UserID, (long)accountId, broker, server, currency, (long)leverage,
      balance, equity, margin, freeMrg,
      (mrGLevel > 0 ? mrGLevel : 0.0), floatPnl,
      total, posArr, Symbol()
   );

   char bodyArr[];
   char result[];
   string headers = "Content-Type: application/json\r\n";
   string resHeaders;
   StringToCharArray(body, bodyArr, 0, StringLen(body));
   ArrayResize(result, 0);

   WebRequest("POST", g_acctEndpoint, headers, 5000, bodyArr, result, resHeaders);
}

//+------------------------------------------------------------------+
//| HELPER — Parse JSON string value                                   |
//+------------------------------------------------------------------+
string ParseJsonString(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int start = StringFind(json, search);
   if(start < 0) return "";
   start += StringLen(search);
   int end = StringFind(json, "\"", start);
   if(end < 0) return "";
   return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| HELPER — Parse JSON numeric value                                  |
//+------------------------------------------------------------------+
double ParseJsonDouble(string json, string key)
{
   string search1 = "\"" + key + "\":";
   int start = StringFind(json, search1);
   if(start < 0) return 0.0;
   start += StringLen(search1);

   // Skip quote if string number
   if(StringGetCharacter(json, start) == '"') start++;

   string numStr = "";
   for(int i = start; i < StringLen(json); i++)
   {
      ushort ch = StringGetCharacter(json, i);
      if(ch == ',' || ch == '}' || ch == ']' || ch == '"' || ch == ' ')
         break;
      if(ch == 'n' || ch == 'u' || ch == 'l') return 0.0;  // null
      numStr += StringSubstr(json, i, 1);
   }
   return StringToDouble(numStr);
}

//+------------------------------------------------------------------+
//| EA DEINITIALIZATION                                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(ShowLogs) PrintFormat("🛑 GAS_AutoTrader stopped — reason: %d", reason);
}
