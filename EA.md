# 🤖 GAS Execution & Data Feed EA v3.0 – Fully Integrated

**Expert Advisor** yang menghubungkan MetaTrader 5 dengan seluruh ekosistem GAS.  
Fitur:
- **Eksekusi order** (market, limit, stop) dari antrean Redis (via gateway).
- **Pengiriman status eksekusi** kembali ke sistem.
- **Streaming tick** ke `gas-mt5-websocket`.
- **Streaming OHLC** (opsional) ke `gas-mt5-websocket`.
- **Heartbeat** periodik untuk monitoring.
- **Manajemen risiko** (spread, drawdown harian, trailing stop).
- **Polling sinyal** (jika diperlukan, opsional).

---

## 🚀 Fitur Baru v3.0

| Fitur | Deskripsi |
|-------|-----------|
| **Order Queue Polling** | Mengambil order dari antrean Redis via endpoint `/terminal/order/queue`. |
| **Order Status Report** | Mengirim status eksekusi ke endpoint `/terminal/order/status`. |
| **Gateway Base URL** | Semua endpoint dikonfigurasi relatif terhadap `GatewayURL`. |
| **Parsing JSON lebih baik** | Fungsi `GetJSONValue` ditingkatkan untuk menangani angka tanpa kutip. |
| **Logging lebih detail** | Menyertakan timestamp dan kode error. |

---

## ⚙️ Input Parameters

| Parameter | Deskripsi | Default |
|-----------|-----------|---------|
| `GatewayURL` | Base URL gateway (tanpa slash di akhir) | `http://35.197.97.60:8000` |
| `MagicNumber` | Magic number EA | `77705` |
| `MaxSpreadPoints` | Maks spread (poin), 0 = tidak dicek | `5000` |
| `RiskPercent` | % risiko per trade dari balance | `1.0` |
| `MaxDailyDrawdown` | % drawdown harian maks | `4.0` |
| `TrailingStop` | Trailing stop dalam poin (0 = nonaktif) | `50` |
| `EnableSignalPolling` | Aktifkan polling sinyal (dari signal service) | `false` |
| `SignalPollingInterval` | Interval polling sinyal (detik) | `1` |
| `EnableOrderExecution` | Aktifkan eksekusi order dari antrean | `true` |
| `OrderPollingInterval` | Interval polling order (detik) | `1` |
| `SendTickData` | Kirim data tick | `true` |
| `TickSendInterval` | Interval kirim batch tick (detik) | `1` |
| `MaxTicksPerBatch` | Maks tick per batch | `100` |
| `SendOHLCData` | Kirim data OHLC | `false` |
| `OHLCSendInterval` | Interval kirim OHLC (detik) | `60` |
| `OHLCPeriods` | Timeframe OHLC (pisah koma) | `M1,M5,M15` |
| `SendHeartbeat` | Kirim heartbeat | `true` |
| `HeartbeatInterval` | Interval heartbeat (detik) | `60` |
| `WebRequestTimeout` | Timeout WebRequest (ms) | `2000` |
| `MaxRetries` | Maks retry jika gagal | `3` |

---

## 🔌 Endpoint yang Digunakan (relatif terhadap GatewayURL)

| Fungsi | Endpoint | Service Tujuan |
|--------|----------|----------------|
| Polling sinyal | `/api/signal/` | `gas-signal-service` |
| Polling order | `/terminal/order/queue` | `gas-terminal-backend` |
| Kirim status order | `/terminal/order/status` | `gas-terminal-backend` |
| Kirim tick | `/mt5/tick` | `gas-mt5-websocket` |
| Kirim OHLC | `/mt5/ohlc` | `gas-mt5-websocket` |
| Kirim heartbeat | `/mt5/heartbeat` | `gas-mt5-websocket` |

---

## 📜 Kode EA Lengkap (v3.0)

//+------------------------------------------------------------------+
//|                                      GAS_Execution_Data_EA_v3.1.mq5
//|                        Fully integrated with GAS ecosystem
//|                                   Version 3.1 - 2025-03-06
//+------------------------------------------------------------------+
#property copyright "GAS Strategy"
#property version   "3.1"
#property strict

// --- Input Parameters ---
input string   GatewayURL           = "http://35.197.97.60:8000";   // Base URL Gateway (tanpa slash)
input int      MagicNumber           = 77705;                        // Magic number EA
input double   MaxSpreadPoints       = 5000;                         // Maks spread (poin)
input double   RiskPercent           = 1.0;                          // % risiko per trade
input double   MaxDailyDrawdown      = 4.0;                          // % drawdown harian max
input int      TrailingStop          = 50;                           // Trailing stop (poin)

// Signal polling
input bool     EnableSignalPolling   = false;                        // Aktifkan polling sinyal
input int      SignalPollingInterval = 1;                            // Interval polling sinyal (detik)

// Order execution
input bool     EnableOrderExecution  = true;                         // Aktifkan eksekusi order
input int      OrderPollingInterval  = 1;                            // Interval polling order (detik)

// Tick data
input bool     SendTickData          = true;                         // Kirim data tick?
input int      TickSendInterval      = 1;                            // Interval kirim batch tick (detik)
input int      MaxTicksPerBatch      = 100;                          // Maks tick per batch

// OHLC data
input bool     SendOHLCData          = false;                        // Kirim data OHLC?
input int      OHLCSendInterval      = 60;                           // Interval kirim OHLC (detik)
input string   OHLCPeriods           = "M1,M5,M15";                  // Timeframe OHLC (pisah koma)

// Heartbeat
input bool     EnableHeartbeat       = true;                         // Kirim heartbeat?
input int      HeartbeatInterval     = 60;                           // Interval heartbeat (detik)

// WebRequest
input int      WebRequestTimeout     = 2000;                         // Timeout (ms)
input int      MaxRetries            = 3;                            // Maks retry jika gagal

// --- Global Variables ---
#include <Trade/Trade.mqh>
#include <Trade/PositionInfo.mqh>
#include <Trade/AccountInfo.mqh>

CTrade         trade;
CPositionInfo  posInfo;
CAccountInfo   accInfo;

double initialBalanceDaily;
string lastSignalID = "";
string lastOrderID = "";  // untuk menghindari eksekusi order ganda

// Tick buffer
struct TickData
{
   double time;
   double bid;
   double ask;
   long   volume;
};
TickData tickBuffer[];
int tickCount = 0;

// Timing
datetime lastSignalPollTime = 0;
datetime lastOrderPollTime = 0;
datetime lastTickSendTime = 0;
datetime lastHeartbeatTime = 0;
datetime lastOHLCSendTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(MagicNumber);
   EventSetTimer(1); // Timer setiap 1 detik untuk semua tugas
   
   initialBalanceDaily = accInfo.Balance();
   Print("🚀 GAS Execution & Data Feed EA v3.1 Started. Symbol: ", _Symbol);
   Print("Gateway URL: ", GatewayURL);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
   datetime now = TimeCurrent();
   
   // 1. Polling sinyal (jika diaktifkan)
   if(EnableSignalPolling && now - lastSignalPollTime >= SignalPollingInterval)
   {
      lastSignalPollTime = now;
      PollSignal();
   }
   
   // 2. Polling order dari antrean (jika diaktifkan)
   if(EnableOrderExecution && now - lastOrderPollTime >= OrderPollingInterval)
   {
      lastOrderPollTime = now;
      PollOrderQueue();
   }
   
   // 3. Kirim tick batch
   if(SendTickData && now - lastTickSendTime >= TickSendInterval)
   {
      lastTickSendTime = now;
      SendTickBatch();
   }
   
   // 4. Kirim OHLC (jika diaktifkan)
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
   
   // 6. Trailing stop (setiap detik)
   if(TrailingStop > 0)
      TrailingStops();
   
   // 7. Cek drawdown harian
   CheckDailyDrawdown();
}

//+------------------------------------------------------------------+
//| Tick function - mengumpulkan tick                               |
//+------------------------------------------------------------------+
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
   
   // Kirim segera jika mencapai batas
   if(tickCount >= MaxTicksPerBatch)
      SendTickBatch();
}

//+------------------------------------------------------------------+
//| Kirim batch tick ke server                                      |
//+------------------------------------------------------------------+
void SendTickBatch()
{
   if(tickCount == 0) return;
   
   string json = BuildTickJSON();
   string url = GatewayURL + "/mt5/tick";
   
   for(int retry = 0; retry < MaxRetries; retry++)
   {
      if(WebRequestPost(url, json))
         break;
      Sleep(100);
   }
   
   // Reset buffer
   tickCount = 0;
   ArrayResize(tickBuffer, 0, 100);
}

//+------------------------------------------------------------------+
//| Bangun JSON untuk tick batch                                    |
//+------------------------------------------------------------------+
string BuildTickJSON()
{
   string json = "{\"symbol\":\"" + _Symbol + "\",\"ticks\":[";
   for(int i = 0; i < tickCount; i++)
   {
      if(i > 0) json += ",";
      json += "{";
      json += "\"time\":" + DoubleToString(tickBuffer[i].time, 0) + ",";
      json += "\"bid\":" + DoubleToString(tickBuffer[i].bid, _Digits) + ",";
      json += "\"ask\":" + DoubleToString(tickBuffer[i].ask, _Digits) + ",";
      json += "\"volume\":0";
      json += "}";
   }
   json += "]}";
   return json;
}

//+------------------------------------------------------------------+
//| Kirim OHLC batch                                                 |
//+------------------------------------------------------------------+
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
         json += "\"symbol\":\"" + _Symbol + "\",";
         json += "\"timeframe\":\"" + tf_array[i] + "\",";
         json += "\"time\":" + IntegerToString(rates[0].time) + ",";
         json += "\"open\":" + DoubleToString(rates[0].open, _Digits) + ",";
         json += "\"high\":" + DoubleToString(rates[0].high, _Digits) + ",";
         json += "\"low\":" + DoubleToString(rates[0].low, _Digits) + ",";
         json += "\"close\":" + DoubleToString(rates[0].close, _Digits) + ",";
         json += "\"volume\":" + IntegerToString(rates[0].tick_volume);
         json += "}";
         
         string url = GatewayURL + "/mt5/ohlc";
         WebRequestPost(url, json);
      }
   }
}

//+------------------------------------------------------------------+
//| Kirim heartbeat                                                  |
//+------------------------------------------------------------------+
void SendHeartbeat()
{
   string json = "{";
   json += "\"symbol\":\"" + _Symbol + "\",";
   json += "\"balance\":" + DoubleToString(accInfo.Balance(), 2) + ",";
   json += "\"equity\":" + DoubleToString(accInfo.Equity(), 2) + ",";
   json += "\"positions\":" + IntegerToString(PositionsTotal()) + ",";
   json += "\"magic\":" + IntegerToString(MagicNumber);
   json += "}";
   
   string url = GatewayURL + "/mt5/heartbeat";
   WebRequestPost(url, json);
}

//+------------------------------------------------------------------+
//| Polling order dari antrean                                      |
//+------------------------------------------------------------------+
void PollOrderQueue()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   
   string url = GatewayURL + "/terminal/order/queue";
   uchar data[];
   uchar result[];
   string headers = "";
   
   int res = WebRequest("GET", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1)
   {
      int err = GetLastError();
      if(err != 0) Print("❌ WebRequest order queue error: ", err);
      return;
   }
   
   string json = CharArrayToString(result);
   if(StringLen(json) < 5) return; // kosong atau tidak ada order
   
   // Cek apakah order ini sudah diproses (berdasarkan ID)
   string order_id = GetJSONValue(json, "order_id");
   if(order_id == "" || order_id == lastOrderID) return;
   
   ParseAndExecuteOrder(json);
}

//+------------------------------------------------------------------+
//| Parse dan eksekusi order dari JSON                              |
//+------------------------------------------------------------------+
void ParseAndExecuteOrder(string json)
{
   string order_id = GetJSONValue(json, "order_id");
   string action   = GetJSONValue(json, "action");
   string symbol   = GetJSONValue(json, "symbol");
   string order_type = GetJSONValue(json, "order_type");
   double volume   = StringToDouble(GetJSONValue(json, "volume"));
   double price    = StringToDouble(GetJSONValue(json, "price"));
   double sl       = StringToDouble(GetJSONValue(json, "stop_loss"));
   double tp       = StringToDouble(GetJSONValue(json, "take_profit"));
   int magic       = (int)StringToInteger(GetJSONValue(json, "magic_number"));
   
   if(order_id == "" || action == "") return;
   
   // Validasi magic number
   if(magic != MagicNumber)
   {
      Print("⚠️ Magic number tidak cocok: ", magic, " vs ", MagicNumber);
      SendOrderStatus(order_id, "rejected", "Invalid magic number");
      return;
   }
   
   // Validasi simbol
   if(symbol != _Symbol)
   {
      Print("⚠️ Order untuk simbol berbeda: ", symbol);
      SendOrderStatus(order_id, "rejected", "Wrong symbol");
      return;
   }
   
   // Validasi spread
   if(MaxSpreadPoints > 0)
   {
      double spread = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
      if(spread > MaxSpreadPoints)
      {
         Print("⏸️ Spread terlalu besar: ", spread, " > ", MaxSpreadPoints);
         SendOrderStatus(order_id, "rejected", "Spread too high");
         return;
      }
   }
   
   // Hitung lot (gunakan volume dari order)
   double lotSize = volume;
   // Opsional: bisa hitung ulang berdasarkan risk
   
   bool success = false;
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
   else
   {
      SendOrderStatus(order_id, "rejected", "Invalid action");
      return;
   }
   
   if(success)
   {
      Print("🔥 Eksekusi order berhasil. Order ID: ", order_id, " Lot: ", lotSize);
      lastOrderID = order_id;
      
      // Ambil fill price dari order yang baru dieksekusi (tidak langsung tersedia)
      // Untuk sederhana, kita gunakan harga saat ini
      double fill_price = (action == "BUY") ? SymbolInfoDouble(symbol, SYMBOL_ASK) : SymbolInfoDouble(symbol, SYMBOL_BID);
      
      SendOrderStatus(order_id, "filled", "", fill_price);
   }
   else
   {
      int retcode = trade.ResultRetcode();
      string desc = trade.ResultRetcodeDescription();
      Print("❌ Eksekusi gagal. Kode: ", retcode, " - ", desc);
      SendOrderStatus(order_id, "failed", desc);
   }
}

//+------------------------------------------------------------------+
//| Kirim status order ke server                                    |
//+------------------------------------------------------------------+
void SendOrderStatus(string order_id, string status, string message, double fill_price = 0)
{
   string json = "{";
   json += "\"order_id\":\"" + order_id + "\",";
   json += "\"status\":\"" + status + "\"";
   
   if(status == "filled")
   {
      json += ",\"fill_price\":" + DoubleToString(fill_price, _Digits);
      json += ",\"fill_time\":" + IntegerToString(TimeCurrent());
      json += ",\"commission\":0,\"swap\":0,\"profit\":0";
   }
   else if(message != "")
   {
      json += ",\"message\":\"" + message + "\"";
   }
   json += "}";
   
   string url = GatewayURL + "/terminal/order/status";
   WebRequestPost(url, json);
}

//+------------------------------------------------------------------+
//| Polling sinyal (dari signal service) - opsional                 |
//+------------------------------------------------------------------+
void PollSignal()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   
   string url = GatewayURL + "/api/signal/";
   uchar data[];
   uchar result[];
   string headers = "";
   
   int res = WebRequest("GET", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1)
   {
      int err = GetLastError();
      if(err != 0) Print("❌ WebRequest sinyal error: ", err);
      return;
   }
   
   string json = CharArrayToString(result);
   ParseAndExecuteSignal(json);
}

//+------------------------------------------------------------------+
//| Parse sinyal dan eksekusi                                       |
//+------------------------------------------------------------------+
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
   
   Print("📥 Sinyal: ", action, " ", symbol, " ID: ", signal_id);
   
   if(symbol != _Symbol)
   {
      Print("⚠️ Sinyal untuk simbol berbeda: ", symbol);
      return;
   }
   
   double sym_point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   if(sym_point == 0) return;
   
   double entry_ref = 0;
   if(action == "BUY" || action == "SELL")
   {
      if(action == "BUY")
         entry_ref = SymbolInfoDouble(symbol, SYMBOL_ASK);
      else
         entry_ref = SymbolInfoDouble(symbol, SYMBOL_BID);
   }
   else
      entry_ref = price;
   
   double stopLossPoints = MathAbs(entry_ref - sl) / sym_point;
   double lotSize = CalculateLotSize(symbol, stopLossPoints);
   
   bool success = false;
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
   
   if(success)
   {
      Print("🔥 Eksekusi sinyal berhasil. Lot: ", lotSize);
      lastSignalID = signal_id;
   }
   else
   {
      Print("❌ Gagal. Kode: ", trade.ResultRetcode());
   }
}

//+------------------------------------------------------------------+
//| Helper: ambil nilai JSON (mendukung string dan angka)           |
//+------------------------------------------------------------------+
string GetJSONValue(string json, string key)
{
   // Coba format dengan kutip: "key":"value"
   string search = "\"" + key + "\":\"";
   int start = StringFind(json, search);
   if(start >= 0)
   {
      start += StringLen(search);
      int end = StringFind(json, "\"", start);
      if(end > start) return StringSubstr(json, start, end - start);
   }
   
   // Coba format tanpa kutip untuk angka: "key":value
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

//+------------------------------------------------------------------+
//| Hitung lot berdasarkan risk                                     |
//+------------------------------------------------------------------+
double CalculateLotSize(string sym, double sl_points)
{
   if(sl_points <= 0) return SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   
   double riskAmount = accInfo.Balance() * (RiskPercent / 100.0);
   double tickValue = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);
   double step = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   
   if(tickValue == 0 || step == 0) return SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   
   double calcLot = riskAmount / (sl_points * tickValue);
   calcLot = MathFloor(calcLot / step) * step;
   
   double minLot = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   if(calcLot < minLot) calcLot = minLot;
   if(calcLot > maxLot) calcLot = maxLot;
   
   return calcLot;
}

//+------------------------------------------------------------------+
//| Trailing stop                                                   |
//+------------------------------------------------------------------+
void TrailingStops()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber && posInfo.Symbol() == _Symbol)
      {
         double sl = posInfo.StopLoss();
         double newSL = 0;
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
         
         if(posInfo.PositionType() == POSITION_TYPE_BUY)
         {
            newSL = bid - TrailingStop * point;
            if(newSL > sl && newSL > posInfo.PriceOpen())
               trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit());
         }
         else if(posInfo.PositionType() == POSITION_TYPE_SELL)
         {
            newSL = ask + TrailingStop * point;
            if(newSL < sl && newSL < posInfo.PriceOpen())
               trade.PositionModify(posInfo.Ticket(), newSL, posInfo.TakeProfit());
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Cek drawdown harian                                             |
//+------------------------------------------------------------------+
void CheckDailyDrawdown()
{
   double currentBalance = accInfo.Balance();
   double ddPercent = (initialBalanceDaily - currentBalance) / initialBalanceDaily * 100;
   if(ddPercent >= MaxDailyDrawdown)
   {
      Print("⚠️ Daily drawdown limit reached: ", ddPercent, "%. Closing all positions...");
      CloseAllPositions();
      ExpertRemove();
   }
}

//+------------------------------------------------------------------+
//| Tutup semua posisi                                              |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(posInfo.SelectByIndex(i) && posInfo.Magic() == MagicNumber)
         trade.PositionClose(posInfo.Ticket());
   }
}

//+------------------------------------------------------------------+
//| Konversi string timeframe ke ENUM_TIMEFRAMES                    |
//+------------------------------------------------------------------+
ENUM_TIMEFRAMES StringToTimeframe(string tf)
{
   if(tf == "M1") return PERIOD_M1;
   if(tf == "M5") return PERIOD_M5;
   if(tf == "M15") return PERIOD_M15;
   if(tf == "M30") return PERIOD_M30;
   if(tf == "H1") return PERIOD_H1;
   if(tf == "H4") return PERIOD_H4;
   if(tf == "D1") return PERIOD_D1;
   if(tf == "W1") return PERIOD_W1;
   if(tf == "MN1") return PERIOD_MN1;
   return PERIOD_CURRENT;
}

//+------------------------------------------------------------------+
//| Fungsi WebRequest POST dengan penanganan error                  |
//+------------------------------------------------------------------+
bool WebRequestPost(string url, string json)
{
   uchar data[];
   uchar result[];
   string headers = "Content-Type: application/json\r\n";
   StringToCharArray(json, data, 0, StringLen(json));
   
   int res = WebRequest("POST", url, headers, WebRequestTimeout, data, result, headers);
   if(res == -1)
   {
      int err = GetLastError();
      Print("❌ WebRequest error ", err, " ke ", url);
      return false;
   }
   return true;
}
//+------------------------------------------------------------------+

## ✅ Cara Menggunakan

1. **Kompilasi EA** di MetaEditor.
2. **Tempelkan EA** pada chart simbol yang diinginkan (misal XAUUSD).
3. **Atur input parameters** sesuai kebutuhan, terutama `GatewayURL`.
4. **Aktifkan AutoTrading**.
5. **Pastikan WebRequest diizinkan** untuk domain gateway (Tools → Options → Expert Advisors → Allow WebRequest for listed URLs).

EA akan mulai mengirim tick, heartbeat, dan jika diaktifkan, melakukan polling order dan sinyal.

---

## 🔥 Fitur Lengkap

- **Order Execution**: EA mengambil order dari antrean dan mengeksekusi.
- **Status Report**: Mengirim hasil eksekusi ke server.
- **Tick Streaming**: Mengirim tick real-time ke `gas-mt5-websocket`.
- **OHLC Streaming**: (Opsional) Mengirim candle ke `gas-mt5-websocket`.
- **Heartbeat**: Memonitor kesehatan EA.
- **Risk Management**: Spread check, drawdown limit, trailing stop.
- **Signal Polling**: (Opsional) Mendukung sinyal dari `gas-signal-service`.

Dengan EA ini, MT5 menjadi **terminal eksekusi** yang terintegrasi penuh dengan seluruh ekosistem GAS.

---

**🔥 GAS EA v3.0 – Jembatan MT5 ke Dunia Kuantitatif**