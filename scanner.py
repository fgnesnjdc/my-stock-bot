import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 你的觀察名單
WATCH_LIST = ['2330.TW', '2317.TW', '2454.TW', '2603.TW', '2610.TW', 
              '3481.TW', '6505.TW', '2449.TW', '2313.TW', '3711.TW']

def daily_scanner():
    results = []
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M')
    
    for symbol in WATCH_LIST:
        try:
            df = yf.download(symbol, period="2mo", progress=False)
            if len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)

            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA10'] = df['Close'].rolling(window=10).mean()
            
            today = df.iloc[-1]; yesterday = df.iloc[-2]
            p = today['Close']; vol = today['Volume']; p_vol = yesterday['Volume']
            ma5, ma10 = today['MA5'], today['MA10']
            
            # 你的條件：雙均線 + 成交量翻倍 + 乖離限制
            bias_5 = ((p - ma5) / ma5) * 100
            if p > ma5 and p > ma10 and vol > (p_vol * 2) and bias_5 < 3.0:
                results.append(f"| {symbol} | {p:.2f} | {vol/p_vol:.1f}x | {bias_5:.1f}% | ✨ 符合 |")
        except: continue

    # 產生 Markdown 格式表格
    report = f"## 📈 台股自動偵察報 - {now}\n\n"
    if results:
        report += "| 代碼 | 現價 | 量增倍數 | 5MA乖離 | 狀態 |\n|---|---|---|---|---|\n"
        report += "\n".join(results)
    else:
        report += "今天名單內無符合標的，維持現金預備金。"
    
    # 將結果存成檔案
    with open("REPORTS.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    daily_scanner()
