//+------------------------------------------------------------------+
//|  GAS AI Agent — Grok 4.2                                        |
//|  Golden AI Strategy — gasstrategyai.xyz                         |
//|  EA polls signal from GAS API every 10s, auto-executes orders   |
//+------------------------------------------------------------------+
#property copyright "Golden AI Strategy"
#property link      "https://gasstrategyai.xyz"
#property version   "1.00"
#property description "GAS AI Agent: Grok 4.2 — Fast Momentum"

#include <Trade\Trade.mqh>

//--- Inputs
input string   GAS_API_URL      = "https://gasstrategyai.xyz/web/api/v1/agent/run";
input string   GAS_JWT_TOKEN    = "";           // Paste your GAS JWT token here
input string   AGENT_ID         = "";           // Your agent ID from dashboard
input string   TRADE_PAIR       = "";           // Leave empty = current chart symbol
input string   TRADE_STYLE      = "scalping";   // scalping | intraday | swing
input int      MIN_CONFIDENCE   = 65;           // Minimum confidence to execute
input double   LOT_SIZE         = 0.01;
input int      MAGIC_NUMBER     = 20260004;
input int      POLL_INTERVAL    = 10;           // Seconds between signal checks
input bool     AUTO_TRADE       = true;         // false = signal only (no orders)
input bool     SHOW_PANEL       = true;

//--- Global vars
CTrade trade;
datetime lastPollTime = 0;
string  lastSignal    = "";
double  lastEntry     = 0;
double  lastSL        = 0;
double  lastTP        = 0;
int     lastConf      = 0;
string  agentStatus   = "INITIALIZING";
int     tradeCount    = 0;
double  totalPnL      = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(MAGIC_NUMBER);
   trade.SetDeviationInPoints(10);
   agentStatus = "ACTIVE";
   Print("GAS Agent Grok 4.2 initialized. Poll every ", POLL_INTERVAL, "s");
   EventSetTimer(POLL_INTERVAL);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   EventKillTimer();
   Comment("");
}

//+------------------------------------------------------------------+
void OnTimer()
{
   PollSignal();
}

void OnTick()
{
   if(SHOW_PANEL) DrawPanel();
}

//+------------------------------------------------------------------+
void PollSignal()
{
   string symbol = TRADE_PAIR == "" ? Symbol() : TRADE_PAIR;

   // Build JSON payload
   string payload = StringFormat(
      "{\"agent_id\":\"%s\",\"pair\":\"%s\",\"style\":\"%s\","
      "\"model\":\"grok\",\"min_confidence\":%d,\"max_trades\":2}",
      AGENT_ID, symbol, TRADE_STYLE, MIN_CONFIDENCE
   );

   // HTTP headers
   string headers = "Content-Type: application/json\r\n"
                  + "Authorization: Bearer " + GAS_JWT_TOKEN + "\r\n";

   char   post_data[];
   char   result_data[];
   string result_headers;

   StringToCharArray(payload, post_data, 0, StringLen(payload));
   ArrayResize(post_data, ArraySize(post_data)-1); // remove null terminator

   int res = WebRequest("POST", GAS_API_URL, headers, 30000, post_data, result_data, result_headers);

   if(res == 200) {
      string json = CharArrayToString(result_data);
      ParseAndAct(json, symbol);
   } else {
      agentStatus = "API_ERROR_" + IntegerToString(res);
      Print("GAS Agent: HTTP error ", res);
   }

   lastPollTime = TimeCurrent();
}

//+------------------------------------------------------------------+
void ParseAndAct(string json, string symbol)
{
   // Simple JSON parser for known fields
   lastSignal = ExtractString(json, "signal");
   lastConf   = (int)ExtractDouble(json, "confidence");
   lastEntry  = ExtractDouble(json, "entry");
   lastSL     = ExtractDouble(json, "sl");
   lastTP     = ExtractDouble(json, "tp");

   Print("GAS Signal: ", lastSignal, " | Conf: ", lastConf, "% | Entry:", lastEntry, " SL:", lastSL, " TP:", lastTP);

   if(lastConf < MIN_CONFIDENCE || lastSignal == "NO TRADE" || lastSignal == "") {
      Print("GAS: No trade. Confidence ", lastConf, "% < ", MIN_CONFIDENCE, "% threshold");
      agentStatus = "WAITING";
      return;
   }

   if(!AUTO_TRADE) {
      agentStatus = "SIGNAL_ONLY: " + lastSignal;
      return;
   }

   // Check existing positions
   if(PositionsTotal() > 0) {
      for(int i = PositionsTotal()-1; i >= 0; i--) {
         if(PositionSelectByTicket(PositionGetTicket(i))) {
            if(PositionGetString(POSITION_SYMBOL) == symbol &&
               PositionGetInteger(POSITION_MAGIC) == MAGIC_NUMBER) {
               Print("GAS: Position already open for ", symbol, ". Skipping.");
               return;
            }
         }
      }
   }

   double price = (lastSignal == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
   double sl    = lastSL  > 0 ? lastSL  : (lastSignal == "BUY" ? price - 150*_Point : price + 150*_Point);
   double tp    = lastTP  > 0 ? lastTP  : (lastSignal == "BUY" ? price + 300*_Point : price - 300*_Point);

   bool ok = false;
   if(lastSignal == "BUY") {
      ok = trade.Buy(LOT_SIZE, symbol, price, sl, tp, "GAS-Grok-Agent");
   } else if(lastSignal == "SELL") {
      ok = trade.Sell(LOT_SIZE, symbol, price, sl, tp, "GAS-Grok-Agent");
   }

   if(ok) {
      tradeCount++;
      agentStatus = "EXECUTED: " + lastSignal;
      Print("GAS: Order executed. ", lastSignal, " ", LOT_SIZE, " lots @ ", price);
   } else {
      agentStatus = "ORDER_FAILED";
      Print("GAS: Order failed. Error: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
void DrawPanel()
{
   string panel = StringFormat(
      "╔═══════════════════════════╗\n"
      "║ GAS AGENT — GROK 4.2    ║\n"
      "║═══════════════════════════║\n"
      "║ Status : %-17s ║\n"
      "║ Signal : %-17s ║\n"
      "║ Conf   : %-3d%%              ║\n"
      "║ Entry  : %-17.5f ║\n"
      "║ SL     : %-17.5f ║\n"
      "║ TP     : %-17.5f ║\n"
      "║ Trades : %-17d ║\n"
      "║ Poll   : %-17s ║\n"
      "╚═══════════════════════════╝",
      agentStatus, lastSignal, lastConf,
      lastEntry, lastSL, lastTP,
      tradeCount,
      TimeToString(lastPollTime, TIME_SECONDS)
   );
   Comment(panel);
}

//+------------------------------------------------------------------+
string ExtractString(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int pos = StringFind(json, search);
   if(pos < 0) return "";
   pos += StringLen(search);
   int end = StringFind(json, "\"", pos);
   if(end < 0) return "";
   return StringSubstr(json, pos, end-pos);
}

double ExtractDouble(string json, string key)
{
   string search = "\"" + key + "\":";
   int pos = StringFind(json, search);
   if(pos < 0) return 0;
   pos += StringLen(search);
   // skip null
   if(StringSubstr(json, pos, 4) == "null") return 0;
   int end = pos;
   while(end < StringLen(json)) {
      string c = StringSubstr(json, end, 1);
      if(c == "," || c == "}" || c == "]" || c == " ") break;
      end++;
   }
   return StringToDouble(StringSubstr(json, pos, end-pos));
}
