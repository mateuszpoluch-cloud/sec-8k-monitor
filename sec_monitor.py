import requests
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict

# Konfiguracja
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
USER_AGENT = "SEC-Monitor/1.0 (your-email@example.com)"

# Lista spółek
COMPANIES = {
    'NVDA': {'name': 'NVIDIA', 'cik': '0001045810', 'desc': 'Producent chipów GPU dla AI i datacenter'},
    'AMD': {'name': 'AMD', 'cik': '0000002488', 'desc': 'Procesory, GPU i chipy dla datacenter'},
    'INTC': {'name': 'Intel', 'cik': '0000050863', 'desc': 'Procesory CPU i komponenty półprzewodnikowe'},
    'ASML': {'name': 'ASML', 'cik': '0000937966', 'desc': 'Maszyny litograficzne do produkcji chipów'},
    'TSM': {'name': 'TSMC', 'cik': '0001046179', 'desc': 'Największa fabryka chipów (foundry)'},
    'MU': {'name': 'Micron', 'cik': '0000723125', 'desc': 'Pamięci RAM i storage dla AI'},
    'STX': {'name': 'Seagate', 'cik': '0001137789', 'desc': 'Dyski twarde i rozwiązania storage'},
}

# Powiązania
RELATIONSHIPS = {
    'NVDA': {'TSM': 'TSMC produkuje ich chipy', 'MU': 'Micron dostarcza pamięci'},
    'AMD': {'TSM': 'TSMC produkuje ich procesory i GPU', 'MU': 'Micron dostarcza pamięci'},
    'TSM': {'NVDA': 'produkuje chipy GPU dla NVIDIA', 'AMD': 'produkuje procesory i GPU dla AMD'},
    'STX': {'NVDA': 'storage dla AI/datacenter'},
}

IMPORTANT_ITEMS = {
    '1.01': 'Przejęcia/Fuzje/Akwizycje',
    '1.02': 'Zakup/Sprzedaż aktywów',
    '8.01': 'Inne istotne wydarzenia',
    '2.02': 'Wyniki finansowe'
}

KEYWORDS = ['acquisition', 'merger', 'partnership', 'agreement', 'contract', 'revenue', 'earnings']

def load_processed_filings():
    try:
        with open('processed_filings.json', 'r') as f:
            data = json.load(f)
            return set(data.get('filings', []))
    except FileNotFoundError:
        return set()

def save_processed_filings(processed):
    with open('processed_filings.json', 'w') as f:
        json.dump({'filings': list(processed)}, f)

def get_recent_filings(cik: str, ticker: str) -> List[Dict]:
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
                    'acceptanceDateTime': recent.get('acceptanceDateTime', [None] * len(recent['form']))[i],
                    'ticker': ticker,
                    'company': COMPANIES[ticker]['name']
                }
                filings.append(filing)
        
        return filings[:5]
        
    except Exception as e:
        print(f"Error getting filings for {ticker}: {e}")
        return []

def translate_text(text: str) -> str:
    import re
    translations = {
        'revenue': 'przychody', 'revenues': 'przychody',
        'earnings': 'zyski', 'billion': 'miliardów', 'million': 'milionów',
        'quarter': 'kwartał', 'FISCAL': 'FISKALNY', 'REPORTS': 'RAPORTUJE',
    }
    
    result = text
    for eng, pl in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(eng) + r'\b'
        result = re.sub(pattern, pl, result, flags=re.IGNORECASE)
    
    return result

def extract_key_numbers(text: str) -> str:
    import re
    summary = []
    
    rev_match = re.search(r'(?:revenue|przychody).*?\$?\s*(\d+[\.,]\d+)\s*(?:billion|miliardów)', text, re.I)
    if rev_match:
        summary.append(f"Przychody: ${rev_match.group(1)} mld")
    
    margin_match = re.search(r'(?:margin|marża).*?(\d+[\.,]\d+)%', text, re.I)
    if margin_match:
        summary.append(f"Marża: {margin_match.group(1)}%")
    
    return "\n".join(summary) if summary else "Brak danych liczbowych"

def extract_document_excerpt(content: str, detected_items: list) -> Dict:
    import re
    import html
    
    for item in ['1.01', '1.02', '8.01', '2.02']:
        if any(item in d for d in detected_items):
            pattern = rf'Item\s+{re.escape(item)}[^\n]*\n(.*?)(?=Item\s+\d|\Z)'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            
            if match:
                excerpt = match.group(1).strip()
                excerpt = re.sub(r'<[^>]+>', '', excerpt)
                excerpt = html.unescape(excerpt)
                excerpt = re.sub(r'EX-\d+\.\d+.*?\.htm\s*', '', excerpt, flags=re.I)
                excerpt = re.sub(r'Investor Relations Contact:.*?@\S+', '', excerpt, flags=re.I)
                excerpt = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', excerpt)
                excerpt = re.sub(r'\s+', ' ', excerpt).strip()
                
                words = excerpt.split()
                start_idx = 0
                for i, word in enumerate(words):
                    if len(word) > 4 and any(c.isalpha() for c in word):
                        start_idx = i
                        break
                excerpt = ' '.join(words[start_idx:])
                
                if len(excerpt) > 800:
                    end = excerpt[:800].rfind('.')
                    if end > 300:
                        excerpt = excerpt[:end+1]
                    else:
                        excerpt = excerpt[:800]
                
                excerpt_pl = translate_text(excerpt)
                key_numbers = extract_key_numbers(excerpt_pl)
                
                return {'excerpt': excerpt_pl, 'key_numbers': key_numbers}
    
    return {'excerpt': 'Brak fragmentu', 'key_numbers': 'N/A'}

def analyze_8k_content(accession_number: str, ticker: str) -> Dict:
    acc_no_dashes = accession_number.replace('-', '')
    cik = COMPANIES[ticker]['cik'].lstrip('0') or '0'
    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_dashes}/{accession_number}.txt"
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(filing_url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.text
        content_lower = content.lower()
        
        detected_items = []
        for item_num, item_desc in IMPORTANT_ITEMS.items():
            if f"item {item_num}" in content_lower:
                detected_items.append(f"Item {item_num} - {item_desc}")
        
        found_keywords = [kw for kw in KEYWORDS if kw in content_lower]
        importance_score = len(detected_items) * 2 + len(found_keywords)
        document_excerpt = extract_document_excerpt(content, detected_items)
        
        return {
            'items': detected_items,
            'keywords': found_keywords[:5],
            'importance': importance_score,
            'document_excerpt': document_excerpt,
            'url': f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}"
        }
        
    except Exception as e:
        print(f"Error analyzing {accession_number}: {e}")
        return {
            'items': [], 'keywords': [], 'importance': 0,
            'document_excerpt': {'excerpt': 'Błąd', 'key_numbers': 'N/A'},
            'url': filing_url
        }

def analyze_sentiment(analysis: Dict) -> Dict:
    keywords = analysis.get('keywords', [])
    bullish_kw = ['partnership', 'revenue', 'earnings', 'growth']
    bearish_kw = ['loss', 'decline', 'lawsuit']
    
    bullish_score = sum(1 for kw in keywords if kw in bullish_kw)
    bearish_score = sum(1 for kw in keywords if kw in bearish_kw)
    
    if bullish_score > bearish_score:
        return {'sentiment': 'BULLISH', 'color': 5763719, 'interpretation': 'Pozytywne wiadomości mogą wspierać wzrost ceny.'}
    elif bearish_score > bullish_score:
        return {'sentiment': 'BEARISH', 'color': 15158332, 'interpretation': 'Negatywne wiadomości mogą wywrzeć presję na cenę.'}
    else:
        return {'sentiment': 'NEUTRALNY', 'color': 15844367, 'interpretation': 'Wiadomości mają mieszany charakter.'}

def send_discord_alert(filing: Dict, analysis: Dict):
    if not DISCORD_WEBHOOK_URL:
        print("Brak DISCORD_WEBHOOK_URL")
        return
    
    ticker = filing['ticker']
    company = filing['company']
    company_desc = COMPANIES[ticker]['desc']
    date = filing['filingDate']
    
    acceptance_datetime = filing.get('acceptanceDateTime')
    if acceptance_datetime:
        try:
            from datetime import datetime as dt
            dt_obj = dt.strptime(acceptance_datetime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            publication_time = dt_obj.strftime('%Y-%m-%d o %H:%M:%S UTC')
        except:
            publication_time = acceptance_datetime
    else:
        publication_time = f"{date}"
    
    sentiment_data = analyze_sentiment(analysis)
    tradingview_link = f"https://www.tradingview.com/chart/?symbol={ticker}"
    
    if analysis['importance'] >= 5:
        priority = "BARDZO WAŻNE"
    elif analysis['importance'] >= 3:
        priority = "WAŻNE"
    else:
        priority = "INFORMACYJNE"
    
    related_companies = RELATIONSHIPS.get(ticker, {})
    if related_companies:
        related_list = []
        for rt, reason in list(related_companies.items())[:3]:
            tv_link = f"https://www.tradingview.com/chart/?symbol={rt}"
            related_list.append(f"[{rt}]({tv_link}) - {reason}")
        related_text = "\n".join(related_list)
    else:
        related_text = "Brak powiązań"
    
    items_text = "\n".join([f"• {item}" for item in analysis['items']]) if analysis['items'] else "Brak"
    keywords_text = ", ".join(analysis['keywords']) if analysis['keywords'] else "Brak"
    
    doc_data = analysis.get('document_excerpt', {})
    if isinstance(doc_data, dict):
        document_excerpt = doc_data.get('excerpt', 'Brak')
        key_numbers = doc_data.get('key_numbers', 'N/A')
    else:
        document_excerpt = str(doc_data)
        key_numbers = 'N/A'
    
    embed = {
        "title": f"{priority} - Nowy raport 8-K",
        "description": f"**{company} ({ticker})**\n*{company_desc}*\n\n{sentiment_data['sentiment']}\n*{sentiment_data['interpretation']}*",
        "color": sentiment_data['color'],
        "fields": [
            {"name": "Data", "value": date, "inline": True},
            {"name": "Ocena", "value": f"{analysis['importance']}/10", "inline": True},
            {"name": "Kategorie", "value": items_text, "inline": False},
            {"name": "Słowa kluczowe", "value": keywords_text, "inline": False},
            {"name": "Wpływ na", "value": related_text, "inline": False},
            {"name": "Wykres", "value": f"[TradingView]({tradingview_link})", "inline": True},
            {"name": "Dokument SEC", "value": f"[Raport]({analysis['url']})", "inline": True},
            {"name": "FRAGMENT", "value": f"```{document_excerpt[:800]}```", "inline": False},
            {"name": "KLUCZOWE DANE", "value": key_numbers, "inline": False},
            {"name": "Publikacja SEC", "value": publication_time, "inline": False}
        ],
        "footer": {"text": f"SEC Monitor {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Alert sent: {ticker} - {date}")
    except Exception as e:
        print(f"Error sending alert: {e}")

def check_new_filings():
    print(f"\nChecking for new 8-K filings... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    
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
            
            print(f"New filing: {ticker} - {filing['filingDate']}")
            
            analysis = analyze_8k_content(filing['accessionNumber'], ticker)
            
            if analysis['items']:
                send_discord_alert(filing, analysis)
                new_filings_count += 1
            
            processed_filings.add(filing_id)
    
    save_processed_filings(processed_filings)
    
    if new_filings_count == 0:
        print("No new filings")
    else:
        print(f"Sent {new_filings_count} alerts")

def main():
    print("=" * 60)
    print("SEC 8-K Monitor - GitHub Actions")
    print("=" * 60)
    print(f"Companies: {len(COMPANIES)}")
    print(f"Categories: {', '.join(IMPORTANT_ITEMS.keys())}")
    print("=" * 60)
    
    if not DISCORD_WEBHOOK_URL:
        print("WARNING: Set DISCORD_WEBHOOK_URL in GitHub Secrets!")
        return
    
    check_new_filings()
    print("\nDone")

if __name__ == "__main__":
    main()
