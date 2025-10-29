import requests
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict

# Konfiguracja
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
USER_AGENT = "SEC-Monitor/1.0 (your-email@example.com)"  # ZMIEŃ NA SWÓJ EMAIL

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

# Powiązania między spółkami z wyjaśnieniami
RELATIONSHIPS = {
    'ASML': {
        'TSM': 'produkuje maszyny litograficzne dla TSMC',
        'INTC': 'dostarcza sprzęt produkcyjny',
        'AMAT': 'konkurent w sprzęcie półprzewodnikowym',
        'LRCX': 'konkurent w sprzęcie półprzewodnikowym'
    },
    'TSM': {
        'NVDA': 'produkuje chipy GPU dla NVIDIA',
        'AMD': 'produkuje procesory i GPU dla AMD',
        'QCOM': 'produkuje chipy mobilne',
        'MRVL': 'produkuje chipy dla Marvell'
    },
    'NVDA': {
        'TSM': 'TSMC produkuje ich chipy',
        'MU': 'Micron dostarcza pamięci do kart graficznych',
        'MPWR': 'układy zasilające do GPU',
        'SNOW': 'klient używający GPU do AI',
        'ORCL': 'klient kupujący serwery z GPU'
    },
    'AMD': {
        'TSM': 'TSMC produkuje ich procesory i GPU',
        'MU': 'Micron dostarcza pamięci',
        'MPWR': 'układy zasilające do procesorów'
    },
    'INTC': {
        'AMAT': 'kupuje sprzęt do produkcji chipów',
        'LRCX': 'kupuje sprzęt litograficzny',
        'ASML': 'kupuje maszyny EUV'
    },
    'MU': {
        'NVDA': 'dostarcza pamięć dla kart graficznych',
        'AMD': 'dostarcza pamięć dla GPU/CPU',
        'INTC': 'konkurent w pamięciach'
    },
    'AMAT': {
        'TSM': 'dostarcza sprzęt produkcyjny',
        'INTC': 'dostarcza narzędzia do fabryk',
        'ASML': 'partner w ekosystemie produkcji'
    },
    'LRCX': {
        'TSM': 'sprzęt do trawienia i depozycji',
        'INTC': 'sprzęt produkcyjny',
        'ASML': 'uzupełniający sprzęt litograficzny'
    },
    'ENTG': {
        'TSM': 'dostarcza chemikalia produkcyjne',
        'INTC': 'materiały do produkcji chipów',
        'AMAT': 'materiały do procesów produkcyjnych'
    },
    'MPWR': {
        'NVDA': 'zarządzanie energią dla GPU',
        'AMD': 'układy zasilające procesory/GPU'
    },
    'AVGO': {
        'AAPL': 'dostarcza komponenty RF',
        'TSM': 'produkują ich chipy'
    },
    'QCOM': {
        'TSM': 'TSMC produkuje ich chipy mobilne',
        'AAPL': 'konkurent w chipach mobilnych'
    },
    'MRVL': {
        'TSM': 'produkują ich chipy',
        'NVDA': 'konkurent w chipach datacenter'
    },
    'KLAC': {
        'TSM': 'sprzęt kontroli jakości',
        'INTC': 'narzędzia inspekcyjne',
        'ASML': 'komplementarny sprzęt'
    },
    'WDC': {
        'NVDA': 'storage dla systemów AI',
        'ORCL': 'storage dla datacenter'
    },
    'STX': {
        'NVDA': 'storage dla AI/datacenter',
        'ORCL': 'storage dla baz danych'
    },
    'ORCL': {
        'NVDA': 'kupuje GPU do cloud',
        'INTC': 'kupuje procesory serwerowe'
    },
    'SNOW': {
        'NVDA': 'używa GPU do analityki AI',
        'ORCL': 'konkurent w cloud data'
    },
    'MDB': {
        'NVDA': 'używa GPU dla AI/ML',
        'ORCL': 'konkurent w bazach danych'
    },
    'PLTR': {
        'NVDA': 'używa GPU do AI analytics',
        'ORCL': 'partner w rozwiązaniach enterprise'
    },
    'ARM': {
        'NVDA': 'próba przejęcia (zablokowana)',
        'AAPL': 'licencja na architekturę ARM',
        'QCOM': 'licencja ARM dla chipów mobilnych'
    }
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

def extract_key_facts(content: str, ticker: str) -> str:
    """Wyciąga kluczowe fakty z treści raportu 8-K"""
    import re
    
    content_lower = content.lower()
    facts = []
    
    # Szukaj konkretnych partnerstw/umów
    partnership_patterns = [
        r'partnership with ([a-z\s]+)',
        r'agreement with ([a-z\s]+)',
        r'collaboration with ([a-z\s]+)',
        r'contract with ([a-z\s]+)'
    ]
    
    for pattern in partnership_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            partner = matches[0].strip().title()
            if len(partner) > 2 and len(partner) < 30:
                facts.append(f"Partnerstwo z {partner}")
                break
    
    # Szukaj wartości finansowych (miliony, miliardy)
    money_patterns = [
        r'\$\s?(\d+(?:,\d{3})*(?:\.\d+)?)\s?(million|billion)',
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s?(million|billion)\s?(?:dollar|usd|\$)'
    ]
    
    for pattern in money_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            amount = matches[0][0].replace(',', '')
            unit = matches[0][1]
            unit_pl = "mln" if unit == "million" else "mld"
            facts.append(f"Wartość: ${amount} {unit_pl}")
            break
    
    # Szukaj liczby produktów/jednostek
    quantity_patterns = [
        r'(\d+(?:,\d{3})*)\s?(?:million|thousand)?\s?(?:processors|chips|units|devices)',
        r'(\d+(?:,\d{3})*)\s?(?:million|thousand)?\s?(?:procesorów|chipów|jednostek)'
    ]
    
    for pattern in quantity_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            quantity = matches[0].replace(',', '')
            facts.append(f"Ilość: {quantity} jednostek")
            break
    
    # Szukaj wzrostu przychodów/zysków
    growth_patterns = [
        r'revenue (?:increased|grew|growth) (?:by )?(\d+)%',
        r'(\d+)% (?:increase|growth) in revenue',
        r'earnings (?:increased|grew) (?:by )?(\d+)%'
    ]
    
    for pattern in growth_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            percentage = matches[0]
            facts.append(f"Wzrost przychodów o {percentage}%")
            break
    
    # Szukaj nowych produktów/technologii
    if 'new product' in content_lower or 'product launch' in content_lower:
        facts.append("Wprowadzenie nowego produktu")
    
    if 'ai chip' in content_lower or 'ai processor' in content_lower:
        facts.append("Technologia: AI chips/procesory")
    
    # Szukaj przejęć
    acquisition_patterns = [
        r'acquire(?:d|s)?\s+([a-z\s]+)\s+for',
        r'acquisition of ([a-z\s]+)'
    ]
    
    for pattern in acquisition_patterns:
        matches = re.findall(pattern, content_lower)
        if matches:
            target = matches[0].strip().title()
            if len(target) > 2 and len(target) < 30:
                facts.append(f"Przejęcie: {target}")
                break
    
    return " | ".join(facts) if facts else "Brak szczegółowych danych liczbowych w raporcie"

def analyze_8k_content(accession_number: str, ticker: str) -> Dict:
    """Analizuje treść raportu 8-K"""
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
        
        # Wyciągnij kluczowe fakty
        key_facts = extract_key_facts(content, ticker)
        
        return {
            'items': detected_items,
            'keywords': found_keywords[:5],
            'importance': importance_score,
            'key_facts': key_facts,
            'url': f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}"
        }
        
    except Exception as e:
        print(f"⚠️ Nie można przeanalizować treści {accession_number}: {e}")
        return {
            'items': [], 
            'keywords': [], 
            'importance': 0, 
            'key_facts': 'Błąd pobierania danych',
            'url': filing_url
        }

def analyze_sentiment(analysis: Dict, ticker: str) -> Dict:
    """Analizuje sentyment raportu 8-K"""
    keywords = analysis.get('keywords', [])
    items = analysis.get('items', [])
    
    # Pozytywne słowa kluczowe
    bullish_keywords = ['partnership', 'collaboration', 'strategic', 'agreement', 'contract', 
                        'revenue', 'earnings', 'growth', 'expansion', 'joint venture']
    # Negatywne słowa kluczowe
    bearish_keywords = ['loss', 'decline', 'lawsuit', 'investigation', 'bankruptcy', 
                        'restructuring', 'termination', 'failure']
    
    bullish_score = sum(1 for kw in keywords if kw in bullish_keywords)
    bearish_score = sum(1 for kw in keywords if kw in bearish_keywords)
    
    # Określ sentyment
    if bullish_score > bearish_score:
        sentiment = "📈 BULLISH"
        color = 5763719  # Zielony
        interpretation = "Pozytywne wiadomości mogą wspierać wzrost ceny. "
        
        if 'partnership' in keywords or 'collaboration' in keywords:
            interpretation += "Nowe partnerstwo może otworzyć dodatkowe źródła przychodów."
        elif 'acquisition' in keywords or 'merger' in keywords:
            interpretation += "Przejęcie/fuzja może zwiększyć wartość rynkową spółki."
        elif 'revenue' in keywords or 'earnings' in keywords:
            interpretation += "Dobre wyniki finansowe mogą przyciągnąć inwestorów."
        else:
            interpretation += "Rynek może zareagować pozytywnie na te wiadomości."
            
    elif bearish_score > bullish_score:
        sentiment = "📉 BEARISH"
        color = 15158332  # Czerwony
        interpretation = "Negatywne wiadomości mogą wywrzeć presję na cenę akcji. "
        interpretation += "Zaleca się ostrożność i monitorowanie sytuacji."
        
    else:
        sentiment = "➡️ NEUTRALNY"
        color = 15844367  # Żółty
        interpretation = "Wiadomości mają mieszany charakter. "
        interpretation += "Wpływ na cenę zależeć będzie od reakcji rynku i dodatkowych szczegółów."
    
    return {
        'sentiment': sentiment,
        'color': color,
        'interpretation': interpretation
    }

def send_discord_alert(filing: Dict, analysis: Dict):
    """Wysyła alert na Discord"""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Brak DISCORD_WEBHOOK_URL - pomijam wysyłanie alertu")
        return
    
    ticker = filing['ticker']
    company = filing['company']
    date = filing['filingDate']
    
    # Analiza sentymentu
    sentiment_data = analyze_sentiment(analysis, ticker)
    
    # Link do TradingView
    tradingview_link = f"https://www.tradingview.com/chart/?symbol={ticker}"
    
    if analysis['importance'] >= 5:
        priority = "🔴 BARDZO WAŻNE"
    elif analysis['importance'] >= 3:
        priority = "🟡 WAŻNE"
    else:
        priority = "🟢 INFORMACYJNE"
    
    related = RELATIONSHIPS.get(ticker, [])
    related_text = ", ".join(related[:5]) if related else "Brak bezpośrednich powiązań"
    items_text = "\n".join([f"• {item}" for item in analysis['items']]) if analysis['items'] else "Brak wykrytych Items"
    keywords_text = ", ".join(analysis['keywords']) if analysis['keywords'] else "Brak"
    
    embed = {
        "title": f"{priority} - Nowy raport 8-K",
        "description": f"**{company} ({ticker})**\n\n{sentiment_data['sentiment']}\n*{sentiment_data['interpretation']}*",
        "color": sentiment_data['color'],
        "fields": [
            {"name": "📅 Data zgłoszenia", "value": date, "inline": True},
            {"name": "📊 Ocena ważności", "value": f"{analysis['importance']}/10", "inline": True},
            {"name": "📋 Wykryte kategorie", "value": items_text, "inline": False},
            {"name": "🔍 Kluczowe słowa", "value": keywords_text, "inline": False},
            {"name": "🔗 Potencjalny wpływ na", "value": related_text, "inline": False},
            {"name": "📈 Wykres", "value": f"[Otwórz na TradingView]({tradingview_link})", "inline": True},
            {"name": "📄 Dokument SEC", "value": f"[Otwórz raport]({analysis['url']})", "inline": True},
            {"name": "📌 KLUCZOWE FAKTY", "value": f"```{analysis['key_facts']}```", "inline": False}
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
