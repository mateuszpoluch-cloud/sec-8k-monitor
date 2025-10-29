import requests
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict

# Konfiguracja
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
USER_AGENT = "SEC-Monitor/1.0 (mateusz.poluch@gmail.com)"  # ZMIEŃ NA SWÓJ EMAIL

# Lista spółek z ekosystemu AI/półprzewodników
COMPANIES = {
    # Producenci chipów AI
    'NVDA': {'name': 'NVIDIA', 'cik': '0001045810'},
    'AMD': {'name': 'AMD', 'cik': '0000002488'},
    'INTC': {'name': 'Intel', 'cik': '0000050863'},
    'AVGO': {'name': 'Broadcom', 'cik': '0001730168'},
    'QCOM': {'name': 'Qualcomm', 'cik': '0000804328'},
    'MRVL': {'name': 'Marvell', 'cik': '0001058057'},
    
    # Półprzewodniki & sprzęt
    'ASML': {'name': 'ASML', 'cik': '0000937966'},
    'AMAT': {'name': 'Applied Materials', 'cik': '0000006951'},
    'LRCX': {'name': 'Lam Research', 'cik': '0000707549'},
    'KLAC': {'name': 'KLA Corporation', 'cik': '0000319201'},
    'TSM': {'name': 'TSMC', 'cik': '0001046179'},
    
    # Pamięci & storage
    'MU': {'name': 'Micron', 'cik': '0000723125'},
    'WDC': {'name': 'Western Digital', 'cik': '0000106040'},
    'STX': {'name': 'Seagate', 'cik': '0001137789'},
    
    # Materiały & komponenty
    'ENTG': {'name': 'Entegris', 'cik': '0001101302'},
    'MPWR': {'name': 'Monolithic Power', 'cik': '0001280452'},
    
    # Infrastruktura AI
    'ORCL': {'name': 'Oracle', 'cik': '0001341439'},
    'SNOW': {'name': 'Snowflake', 'cik': '0001640147'},
    'MDB': {'name': 'MongoDB', 'cik': '0001441404'},
    'PLTR': {'name': 'Palantir', 'cik': '0001321655'},
    
    # ARM & Design
    'ARM': {'name': 'Arm Holdings', 'cik': '0001996864'},
}

# Powiązania między spółkami
RELATIONSHIPS = {
    'ASML': ['TSM', 'INTC', 'AMAT', 'LRCX'],
    'TSM': ['NVDA', 'AMD', 'AAPL', 'QCOM', 'MRVL'],
    'NVDA': ['TSM', 'MU', 'MPWR', 'SNOW', 'ORCL'],
    'AMD': ['TSM', 'MU', 'MPWR'],
    'INTC': ['AMAT', 'LRCX', 'ASML'],
    'MU': ['NVDA', 'AMD', 'INTC'],
    'AMAT': ['TSM', 'INTC', 'ASML'],
    'LRCX': ['TSM', 'INTC', 'ASML'],
    'ENTG': ['TSM', 'INTC', 'AMAT'],
    'MPWR': ['NVDA', 'AMD'],
}

# Kategorie 8-K które nas interesują
IMPORTANT_ITEMS = {
    '1.01': 'Przejęcia/Fuzje/Akwizycje',
    '1.02': 'Zakup/Sprzedaż aktywów',
    '8.01': 'Inne istotne wydarzenia',
    '2.02': 'Wyniki finansowe'
}

# Słowa kluczowe wskazujące na ważne wydarzenia
KEYWORDS = [
    'acquisition', 'merger', 'partnership', 'agreement', 'contract',
    'collaboration', 'joint venture', 'strategic', 'ai', 'artificial intelligence',
    'chip', 'semiconductor', 'revenue', 'earnings', 'guidance'
]

def load_processed_filings():
    """Wczytaj listę przetworzonych raportów z pliku"""
    try:
        with open('processed_filings.json', 'r') as f:
            data = json.load(f)
            return set(data.get('filings', []))
    except FileNotFoundError:
        return set()

def save_processed_filings(processed):
    """Zapisz listę przetworzonych raportów do pliku"""
    with open('processed_filings.json', 'w') as f:
        json.dump({'filings': list(processed)}, f)

def get_recent_filings(cik: str, ticker: str) -> List[Dict]:
    """Pobiera ostatnie zgłoszenia 8-K dla danej spółki"""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        recent = data.get('filings', {}).get('recent', {})
        filings = []
        
        for i in range(len(recent.get('form', []))):
            form = recent['form'][i]
            if form == '8-K':
                filing = {
                    'accessionNumber': recent['accessionNumber'][i],
                    'filingDate': recent['filingDate'][i],
                    'primaryDocument': recent['primaryDocument'][i],
                    'ticker': ticker,
                    'company': COMPANIES[ticker]['name']
                }
                filings.append(filing)
        
        return filings[:5]
        
    except Exception as e:
        print(f"❌ Błąd pobierania danych dla {ticker}: {e}")
        return []

def analyze_8k_content(accession_number: str, ticker: str) -> Dict:
    """Analizuje treść raportu 8-K"""
    acc_no_dashes = accession_number.replace('-', '')
    cik = COMPANIES[ticker]['cik'].lstrip('0') or '0'
    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_dashes}/{accession_number}.txt"
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(filing_url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text.lower()
        
        detected_items = []
        for item_num, item_desc in IMPORTANT_ITEMS.items():
            if f"item {item_num}" in content:
                detected_items.append(f"Item {item_num} - {item_desc}")
        
        found_keywords = [kw for kw in KEYWORDS if kw in content]
        importance_score = len(detected_items) * 2 + len(found_keywords)
        
        return {
            'items': detected_items,
            'keywords': found_keywords[:5],
            'importance': importance_score,
            'url': f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}"
        }
        
    except Exception as e:
        print(f"⚠️ Nie można przeanalizować treści {accession_number}: {e}")
        return {'items': [], 'keywords': [], 'importance': 0, 'url': filing_url}

def send_discord_alert(filing: Dict, analysis: Dict):
    """Wysyła alert na Discord"""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Brak DISCORD_WEBHOOK_URL - pomijam wysyłanie alertu")
        return
    
    ticker = filing['ticker']
    company = filing['company']
    date = filing['filingDate']
    
    if analysis['importance'] >= 5:
        priority = "🔴 BARDZO WAŻNE"
        color = 15158332
    elif analysis['importance'] >= 3:
        priority = "🟡 WAŻNE"
        color = 15844367
    else:
        priority = "🟢 INFORMACYJNE"
        color = 3066993
    
    related = RELATIONSHIPS.get(ticker, [])
    related_text = ", ".join(related[:5]) if related else "Brak bezpośrednich powiązań"
    items_text = "\n".join([f"• {item}" for item in analysis['items']]) if analysis['items'] else "Brak wykrytych Items"
    keywords_text = ", ".join(analysis['keywords']) if analysis['keywords'] else "Brak"
    
    embed = {
        "title": f"{priority} - Nowy raport 8-K",
        "description": f"**{company} ({ticker})**",
        "color": color,
        "fields": [
            {"name": "📅 Data zgłoszenia", "value": date, "inline": True},
            {"name": "📊 Ocena ważności", "value": f"{analysis['importance']}/10", "inline": True},
            {"name": "📋 Wykryte kategorie", "value": items_text, "inline": False},
            {"name": "🔍 Kluczowe słowa", "value": keywords_text, "inline": False},
            {"name": "🔗 Potencjalny wpływ na", "value": related_text, "inline": False},
            {"name": "🌐 Link do dokumentu", "value": f"[Otwórz raport SEC]({analysis['url']})", "inline": False}
        ],
        "footer": {"text": f"SEC EDGAR Monitor • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Alert wysłany: {ticker} - {date}")
    except Exception as e:
        print(f"❌ Błąd wysyłania alertu Discord: {e}")

def check_new_filings():
    """Sprawdza nowe zgłoszenia dla wszystkich spółek"""
    print(f"\n🔍 Sprawdzam nowe raporty 8-K... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    
    processed_filings = load_processed_filings()
    new_filings_count = 0
    
    for ticker, info in COMPANIES.items():
        filings = get_recent_filings(info['cik'], ticker)
        
        for filing in filings:
            filing_id = f"{ticker}_{filing['accessionNumber']}"
            
            if filing_id in processed_filings:
                continue
            
            filing_date = datetime.strptime(filing['filingDate'], '%Y-%m-%d')
            if datetime.now() - filing_date > timedelta(hours=48):
                processed_filings.add(filing_id)
                continue
            
            print(f"📄 Nowy raport: {ticker} - {filing['filingDate']}")
            
            analysis = analyze_8k_content(filing['accessionNumber'], ticker)
            
            if analysis['items']:
                send_discord_alert(filing, analysis)
                new_filings_count += 1
            
            processed_filings.add(filing_id)
    
    save_processed_filings(processed_filings)
    
    if new_filings_count == 0:
        print("✓ Brak nowych raportów")
    else:
        print(f"✓ Wysłano {new_filings_count} alertów")

def main():
    """Główna funkcja"""
    print("=" * 60)
    print("🚀 SEC 8-K Monitor - GitHub Actions")
    print("=" * 60)
    print(f"📊 Monitorowane spółki: {len(COMPANIES)}")
    print(f"📋 Kategorie: {', '.join(IMPORTANT_ITEMS.keys())}")
    print("=" * 60)
    
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ UWAGA: Ustaw DISCORD_WEBHOOK_URL w GitHub Secrets!")
        return
    
    check_new_filings()
    print("\n✅ Zakończono sprawdzanie")

if __name__ == "__main__":
    main()
