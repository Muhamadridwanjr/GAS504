//+------------------------------------------------------------------+
//|            GAS_AccountHeartbeat.mq5                              |
//|            GAS Platform - Per-User Account EA                    |
//|            v1.0 — Kirim data akun ke GAS Terminal                |
//|                                                                  |
//|  ⚠️  EA INI HANYA KIRIM DATA AKUN (balance, equity, posisi)      |
//|     BUKAN data harga — data harga dari EA Utama.                 |
//|                                                                  |
//|  Setup:                                                          |
//|   1. Drag EA ini ke chart (pair apapun, e.g. EURUSD H1)         |
//|   2. Isi UserID = user ID kamu dari GAS Platform               |
//|   3. Isi GAS_URL = URL VPS GAS Platform kamu                   |
//|   4. Allow WebRequest di MT5 Tools → Options → Expert Advisors  |
//|      Tambahkan: https://gasstrategyai.xyz ke whitelist           |
//+------------------------------------------------------------------+
#property copyright "GAS Platform"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Input Parameters                                                  |
//+------------------------------------------------------------------+
input string  UserID         = "";            // GAS User ID (dari profile halaman)
input string  GAS_URL        = "https://gasstrategyai.xyz"; // VPS URL
input int     SendInterval   = 10;           // Interval kirim data (detik)
input bool    SendPositions  = true;         // Kirim detail posisi terbuka?
input bool    ShowLogs       = true;         // Tampilkan log di journal?

//+------------------------------------------------------------------+
//| Global Variables                                                  |
//+------------------------------------------------------------------+
datetime g_lastSent = 0;
string   g_endpoint = "";

//+------------------------------------------------------------------+
//| EA Initialization                                                 |
//+------------------------------------------------------------------+
int OnInit()
{
   // Validasi UserID
   if(StringLen(StringTrimLeft(StringTrimRight(UserID))) == 0)
   {
      Alert("❌ GAS_AccountHeartbeat: UserID tidak boleh kosong! Isi UserID di parameter EA.");
      return INIT_FAILED;
   }

   g_endpoint = GAS_URL + "/mt5/account-heartbeat";

   if(ShowLogs)
      PrintFormat("✅ GAS_AccountHeartbeat v1.0 — UserID: %s — Endpoint: %s", UserID, g_endpoint);

   // Kirim heartbeat pertama langsung
   SendAccountHeartbeat();
   g_lastSent = TimeCurrent();

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| EA Tick Handler                                                   |
//+------------------------------------------------------------------+
void OnTick()
{
   datetime now = TimeCurrent();
   if((int)(now - g_lastSent) >= SendInterval)
   {
      SendAccountHeartbeat();
      g_lastSent = now;
   }
}

//+------------------------------------------------------------------+
//| Kirim data akun ke GAS Platform                                  |
//+------------------------------------------------------------------+
void SendAccountHeartbeat()
{
   double balance       = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity        = AccountInfoDouble(ACCOUNT_EQUITY);
   double margin        = AccountInfoDouble(ACCOUNT_MARGIN);
   double freeMargin    = AccountInfoDouble(ACCOUNT_FREEMARGIN);
   double marginLevel   = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   double floatingPnl   = equity - balance;
   string currency      = AccountInfoString(ACCOUNT_CURRENCY);
   long   accountId     = AccountInfoInteger(ACCOUNT_LOGIN);
   string broker        = AccountInfoString(ACCOUNT_COMPANY);
   string server        = AccountInfoString(ACCOUNT_SERVER);
   long   leverage      = AccountInfoInteger(ACCOUNT_LEVERAGE);
   string chartSymbol   = Symbol();

   // ── Build positions JSON ──────────────────────────────────────
   string positionsJson = "[]";
   int posCount = 0;

   if(SendPositions)
   {
      string posArr = "[";
      bool first = true;
      int total = PositionsTotal();
      posCount = total;

      for(int i = 0; i < total; i++)
      {
         ulong ticket = PositionGetTicket(i);
         if(ticket == 0) continue;

         string sym       = PositionGetString(POSITION_SYMBOL);
         int    dir       = (int)PositionGetInteger(POSITION_TYPE); // 0=BUY,1=SELL
         double lot       = PositionGetDouble(POSITION_VOLUME);
         double entryPx   = PositionGetDouble(POSITION_PRICE_OPEN);
         double currentPx = PositionGetDouble(POSITION_PRICE_CURRENT);
         double pnl       = PositionGetDouble(POSITION_PROFIT);
         double swap      = PositionGetDouble(POSITION_SWAP);
         long   magic     = PositionGetInteger(POSITION_MAGIC);
         string comment   = PositionGetString(POSITION_COMMENT);
         datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);

         string dirStr = (dir == POSITION_TYPE_BUY) ? "BUY" : "SELL";
         string openTimeStr = TimeToString(openTime, TIME_DATE|TIME_MINUTES);

         if(!first) posArr += ",";
         first = false;

         posArr += StringFormat(
            "{\"ticket\":%llu,\"symbol\":\"%s\",\"direction\":\"%s\","
            "\"lot\":%.2f,\"entry_price\":%.5f,\"current_price\":%.5f,"
            "\"pnl\":%.2f,\"swap\":%.2f,\"magic\":%ld,\"comment\":\"%s\","
            "\"open_time\":\"%s\"}",
            ticket, sym, dirStr,
            lot, entryPx, currentPx,
            pnl, swap, magic, comment, openTimeStr
         );
      }
      posArr += "]";
      positionsJson = posArr;
   }
   else
   {
      // Count positions even if not sending details
      posCount = PositionsTotal();
   }

   // ── Build JSON body ───────────────────────────────────────────
   string body = StringFormat(
      "{"
      "\"user_id\":\"%s\","
      "\"account_id\":%ld,"
      "\"broker\":\"%s\","
      "\"server\":\"%s\","
      "\"currency\":\"%s\","
      "\"leverage\":%ld,"
      "\"balance\":%.2f,"
      "\"equity\":%.2f,"
      "\"margin\":%.2f,"
      "\"free_margin\":%.2f,"
      "\"margin_level\":%.2f,"
      "\"floating_pnl\":%.2f,"
      "\"positions_count\":%d,"
      "\"positions\":%s,"
      "\"symbol\":\"%s\","
      "\"ea_version\":\"1.0\""
      "}",
      UserID,
      (long)accountId,
      broker,
      server,
      currency,
      (long)leverage,
      balance,
      equity,
      margin,
      freeMargin,
      (marginLevel > 0 ? marginLevel : 0.0),
      floatingPnl,
      posCount,
      positionsJson,
      chartSymbol
   );

   // ── Send HTTP POST ────────────────────────────────────────────
   char   bodyArr[];
   char   result[];
   string headers    = "Content-Type: application/json\r\n";
   string resHeaders = "";

   StringToCharArray(body, bodyArr, 0, StringLen(body));
   ArrayResize(result, 0);

   int httpCode = WebRequest("POST", g_endpoint, headers, 5000, bodyArr, result, resHeaders);

   if(httpCode == 200)
   {
      if(ShowLogs)
         PrintFormat("✅ Heartbeat sent — Balance: %.2f | Equity: %.2f | Positions: %d", balance, equity, posCount);
   }
   else
   {
      if(ShowLogs)
         PrintFormat("❌ Heartbeat failed — HTTP %d — Check URL: %s", httpCode, g_endpoint);
   }
}

//+------------------------------------------------------------------+
//| EA Deinitialization                                               |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(ShowLogs)
      PrintFormat("🛑 GAS_AccountHeartbeat stopped — reason: %d", reason);
}
