import requests
import json
from datetime import datetime, timedelta
import os
import time
from typing import List, Dict, Set

# ============================================
# KONFIGURACJA
# ============================================

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')  # Kanal #1 (pozostaje bez zmian)
DISCORD_WEBHOOK_AI = os.environ.get('DISCORD_WEBHOOK_AI', '')   # Kanal #2 (NOWY - AI analizy)
GIST_TOKEN = os.environ.get('GIST_TOKEN', '')
GIST_ID = os.environ.get('GIST_ID', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')  # NOWY - Google Gemini
USER_AGENT = "SEC-Monitor/2.0 (your-email@example.com)"

# ============================================
# LISTA SPOLEK (51 spolek)
# ============================================

COMPANIES = {
    # QUANTUM COMPUTING
    'IONQ': {'name': 'IonQ', 'cik': '0001852179', 'desc': 'Komputery kwantowe oparte na jonach'},
    'RGTI': {'name': 'Rigetti Computing', 'cik': '0001846163', 'desc': 'Quantum computing as a service'},
    'QUBT': {'name': 'Quantum Computing Inc', 'cik': '0001635004', 'desc': 'Rozwiazania kwantowe dla biznesu'},
    'QBTS': {'name': 'D-Wave Quantum', 'cik': '0001808665', 'desc': 'Quantum annealing systems'},
    
    # BIG TECH & CLOUD
    'IBM': {'name': 'IBM', 'cik': '0000051143', 'desc': 'Quantum computing, AI, cloud infrastructure'},
    'MSFT': {'name': 'Microsoft', 'cik': '0000789019', 'desc': 'Azure cloud, AI, quantum research'},
    'AMZN': {'name': 'Amazon', 'cik': '0001018724', 'desc': 'AWS cloud, AI services, infrastructure'},
    'GOOGL': {'name': 'Alphabet', 'cik': '0001652044', 'desc': 'Google Cloud, AI, quantum computing'},
    
    # SEMICONDUCTORS
    'NVDA': {'name': 'NVIDIA', 'cik': '0001045810', 'desc': 'Producent chipow GPU dla AI i datacenter'},
    'AMD': {'name': 'AMD', 'cik': '0000002488', 'desc': 'Procesory, GPU i chipy dla datacenter'},
    'INTC': {'name': 'Intel', 'cik': '0000050863', 'desc': 'Procesory CPU i komponenty polprzewodnikowe'},
    'AVGO': {'name': 'Broadcom', 'cik': '0001730168', 'desc': 'Chipy komunikacyjne i polprzewodniki'},
    'QCOM': {'name': 'Qualcomm', 'cik': '0000804328', 'desc': 'Chipy mobilne i technologie bezprzewodowe'},
    'MRVL': {'name': 'Marvell', 'cik': '0001058057', 'desc': 'Polprzewodniki dla datacenter i 5G'},
    'TSM': {'name': 'TSMC', 'cik': '0001046179', 'desc': 'Najwieksza fabryka chipow (foundry)'},
    'SNPS': {'name': 'Synopsys', 'cik': '0000883241', 'desc': 'Narzedzia EDA do projektowania chipow'},
    'ARM': {'name': 'Arm Holdings', 'cik': '0001996864', 'desc': 'Architektura procesorow ARM'},
    
    # SEMICONDUCTOR EQUIPMENT
    'ASML': {'name': 'ASML', 'cik': '0000937966', 'desc': 'Maszyny litograficzne do produkcji chipow'},
    'AMAT': {'name': 'Applied Materials', 'cik': '0000006951', 'desc': 'Sprzet do produkcji polprzewodnikow'},
    'LRCX': {'name': 'Lam Research', 'cik': '0000707549', 'desc': 'Technologie trawienia i depozycji chipow'},
    'KLAC': {'name': 'KLA Corporation', 'cik': '0000319201', 'desc': 'Kontrola jakosci w produkcji chipow'},
    'ENTG': {'name': 'Entegris', 'cik': '0001101302', 'desc': 'Materialy chemiczne do produkcji chipow'},
    
    # MEMORY & STORAGE
    'MU': {'name': 'Micron', 'cik': '0000723125', 'desc': 'Pamieci RAM i storage dla AI'},
    'WDC': {'name': 'Western Digital', 'cik': '0000106040', 'desc': 'Dyski twarde i pamieci flash'},
    'STX': {'name': 'Seagate', 'cik': '0001137789', 'desc': 'Dyski twarde i rozwiazania storage'},
    
    # POWER & COMPONENTS
    'MPWR': {'name': 'Monolithic Power', 'cik': '0001280452', 'desc': 'Uklady zarzadzania energia'},
    
    # DATA CENTERS & INFRASTRUCTURE
    'EQIX': {'name': 'Equinix', 'cik': '0001101239', 'desc': 'Globalne data centers i colocation'},
    'DLR': {'name': 'Digital Realty', 'cik': '0001297996', 'desc': 'Data center REITs dla cloud/AI'},
    'AMT': {'name': 'American Tower', 'cik': '0001053507', 'desc': 'Infrastruktura telekomunikacyjna'},
    'VRT': {'name': 'Vertiv Holdings', 'cik': '0001839992', 'desc': 'Infrastruktura IT i chlodzenie'},
    'EME': {'name': 'EMCOR Group', 'cik': '0000105634', 'desc': 'Konstrukcja i serwis data centers'},
    'PWR': {'name': 'Quanta Services', 'cik': '0001050915', 'desc': 'Infrastruktura energetyczna'},
    
    # NETWORKING & CONNECTIVITY
    'IRDM': {'name': 'Iridium', 'cik': '0001418819', 'desc': 'Komunikacja satelitarna'},
    
    # AI INFRASTRUCTURE & SERVERS
    'HPE': {'name': 'Hewlett Packard Enterprise', 'cik': '0001645590', 'desc': 'Serwery i infrastruktura AI'},
    'SMCI': {'name': 'Super Micro Computer', 'cik': '0001375365', 'desc': 'Serwery AI i high-performance computing'},
    'APLD': {'name': 'Applied Digital', 'cik': '0001144879', 'desc': 'Data centers dla AI i HPC'},
    
    # CLOUD & SOFTWARE
    'ORCL': {'name': 'Oracle', 'cik': '0001341439', 'desc': 'Bazy danych i cloud computing'},
    'SNOW': {'name': 'Snowflake', 'cik': '0001640147', 'desc': 'Platforma analityki danych w chmurze'},
    'MDB': {'name': 'MongoDB', 'cik': '0001441404', 'desc': 'Bazy danych NoSQL'},
    'PLTR': {'name': 'Palantir', 'cik': '0001321655', 'desc': 'Analityka AI i big data'},
    
    # BIOTECH & PHARMA
    'REGN': {'name': 'Regeneron', 'cik': '0000872589', 'desc': 'Biotechnologia i terapie biologiczne'},
    'BMRN': {'name': 'BioMarin', 'cik': '0001048477', 'desc': 'Terapie genowe i rzadkie choroby'},
    'MRNA': {'name': 'Moderna', 'cik': '0001682852', 'desc': 'Terapie mRNA i szczepionki'},
    'HALO': {'name': 'Halozyme', 'cik': '0001029881', 'desc': 'Technologie dostarczania lekow'},
    'KNSA': {'name': 'Kiniksa Pharma', 'cik': '0001714607', 'desc': 'Leki na choroby autoimmunologiczne'},
    'GILD': {'name': 'Gilead Sciences', 'cik': '0000882095', 'desc': 'Leki przeciwwirusowe i onkologia'},
    'EXEL': {'name': 'Exelixis', 'cik': '0000939767', 'desc': 'Terapie onkologiczne'},
    'TECH': {'name': 'Bio-Techne', 'cik': '0000206643', 'desc': 'Narzedzia biotechnologiczne'},
    'INCY': {'name': 'Incyte', 'cik': '0000879169', 'desc': 'Onkologia i choroby zapalne'},
    'LLY': {'name': 'Eli Lilly', 'cik': '0000059478', 'desc': 'Farmaceutyki, cukrzyca, onkologia'},
}

RELATIONSHIPS = {
    'IONQ': {'IBM': 'konkurencja w quantum computing', 'GOOGL': 'rynek quantum cloud'},
    'MSFT': {'NVDA': 'kupuje GPU dla Azure AI', 'AMZN': 'konkurencja cloud'},
    'GOOGL': {'NVDA': 'GCP kupuje GPU', 'TSM': 'projektuje wlasne chipy TPU'},
    'NVDA': {'TSM': 'TSMC produkuje chipy', 'MU': 'Micron dostarcza pamieci', 'SMCI': 'serwery z GPU'},
    'EQIX': {'NVDA': 'data centers dla AI', 'MSFT': 'colocation dla Azure'},
    'LLY': {'NVDA': 'AI drug discovery', 'MSFT': 'Azure dla R&D'},
}

IMPORTANT_ITEMS = {
    '1.01': 'Przejecia/Fuzje/Akwizycje',
    '1.02': 'Zakup/Sprzedaz aktywow',
    '2.02': 'Wyniki finansowe (Earnings)',
    '2.03': 'Zobowiazania/Material Obligations',
    '2.05': 'Restrukturyzacja/Costs',
    '3.03': 'Split akcji (Stock Split)',
    '4.02': 'Restatement (korekta wynikow)',
    '5.02': 'Zmiany w zarzadzie (CEO/CFO)',
    '7.01': 'Regulacje/SEC Regulations',
    '8.01': 'Inne istotne wydarzenia'
}

# Impact Score - waga waznosci kazdego Item (1-10)
# Im wyzszy score, tym wiekszy potencjalny wplyw na cene akcji
IMPACT_SCORE = {
    '2.02': 10,  # Earnings - NAJWAZNIEJSZE
    '1.01': 9,   # M&A/Acquisitions - duzy impact
    '4.02': 9,   # Restatement - czesto niedoceniany, bardzo cenotwórczy
    '5.02': 8,   # Zmiany w zarzadzie (CEO/CFO) - natychmiastowa reakcja
    '2.05': 7,   # Restrukturyzacja - pozytywny przy oszczednosciach
    '8.01': 7,   # Inne istotne - zalezy od tresci
    '3.03': 6,   # Stock split - katalizator po wzrostach
    '1.02': 5,   # Zakup/Sprzedaz aktywow
    '2.03': 5,   # Zobowiazania
    '7.01': 5,   # Regulacje
    '1.02': 4    # Zakup/Sprzedaz aktywow
}

KEYWORDS = ['acquisition', 'merger', 'partnership', 'agreement', 'contract', 'collaboration', 
            'joint venture', 'strategic', 'ai', 'artificial intelligence', 'chip', 'semiconductor', 
            'revenue', 'earnings', 'guidance', 'quantum', 'cloud', 'datacenter', 'biotech']

# ============================================
# FUNKCJE GIST (bez zmian)
# ============================================

def load_processed_filings_from_gist() -> Set[str]:
    if not GIST_TOKEN or not GIST_ID:
        print("WARNING: Brak GIST_TOKEN lub GIST_ID - uzywam lokalnego pliku")
        return set()
    
    try:
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/gists/{GIST_ID}'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        gist_data = response.json()
        
        if 'files' in gist_data and 'processed_filings.json' in gist_data['files']:
            content = gist_data['files']['processed_filings.json']['content']
            data = json.loads(content)
            filings_set = set(data.get('filings', []))
            print(f"✓ Zaladowano {len(filings_set)} przetworzonych zgloszen z Gist")
            return filings_set
        else:
            return set()
            
    except Exception as e:
        print(f"ERROR: Nie udalo sie pobrac danych z Gist: {e}")
        return set()

def save_processed_filings_to_gist(processed: Set[str]):
    if not GIST_TOKEN or not GIST_ID:
        return
    
    try:
        headers = {
            'Authorization': f'token {GIST_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data_to_save = {
            'filings': list(processed),
            'last_updated': datetime.now().isoformat(),
            'total_count': len(processed)
        }
        
        payload = {
            'files': {
                'processed_filings.json': {
                    'content': json.dumps(data_to_save, indent=2)
                }
            }
        }
        
        url = f'https://api.github.com/gists/{GIST_ID}'
        response = requests.patch(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"✓ Zapisano {len(processed)} zgloszen do Gist")
        
    except Exception as e:
        print(f"ERROR: Nie udalo sie zapisac do Gist: {e}")

# ============================================
# NOWE: YAHOO FINANCE INTEGRATION
# ============================================

def get_yahoo_finance_data(ticker: str) -> Dict:
    """Pobiera dane z Yahoo Finance: konsensus EPS, revenue, target price"""
    try:
        # Yahoo Finance nie ma oficjalnego API, ale mozemy uzyc publicznego endpointu
        # Alternatywnie mozna uzyc yfinance library, ale dla prostoty uzywamy requests
        
        # Symulowane dane (w prawdziwej wersji pobierasz z Yahoo/Alpha Vantage/FMP)
        # W produkcji uzyj: import yfinance as yf; stock = yf.Ticker(ticker)
        
        yahoo_data = {
            'consensus_eps': None,
            'consensus_revenue': None,
            'target_price': None,
            'analyst_ratings': {'buy': 0, 'hold': 0, 'sell': 0},
            'previous_quarter': {}
        }
        
        print(f"   → Pobieranie danych Yahoo Finance dla {ticker}...")
        
        # Tutaj w prawdziwej wersji byłby request do Yahoo Finance API
        # Dla demo zwracamy podstawową strukturę
        
        return yahoo_data
        
    except Exception as e:
        print(f"   → Błąd Yahoo Finance dla {ticker}: {e}")
        return {}

# ============================================
# NOWE: GEMINI AI INTEGRATION
# ============================================

def analyze_with_gemini(document_text: str, ticker: str, company: str, yahoo_data: Dict) -> Dict:
    """Analizuje dokument 8-K używając Gemini AI"""
    
    if not GEMINI_API_KEY:
        print("   → Brak GEMINI_API_KEY - pomijam analizę AI")
        return None
    
    try:
        print(f"   → Wysyłanie do Gemini AI...")
        
        # Przygotuj prompt
        prompt = f"""Jesteś ekspertem analizy finansowej specjalizującym się w raportach SEC i ocenie wyników kwartalnych spółek giełdowych.

Otrzymujesz pełny tekst raportu 8-K dla spółki {company} (Ticker: {ticker}).

KONTEKST RYNKOWY:
{json.dumps(yahoo_data, indent=2) if yahoo_data else "Brak danych Yahoo Finance"}

DOKUMENT 8-K:
{document_text[:50000]}

WYKONAJ PEŁNĄ ANALIZĘ w formacie:

**VERDICT:** [STRONG BEAT / BEAT / MEET / MISS / STRONG MISS]

**WAGA ZDARZENIA:** [1-10]

**KIERUNEK CENY:** [BULLISH / BEARISH / NEUTRALNY]

**SIŁA RUCHU:** [X/10]

**POTENCJALNY RUCH:**
- Pre-market/AH: [+/-X%]
- 1-3 dni: [+/-X%]  
- 1-2 tygodnie: [+/-X%]

**BEAT/MEET/MISS BREAKDOWN:**
- EPS: [opis]
- Revenue: [opis]
- Guidance: [opis]

**KLUCZOWE DANE:**
[Konkretne liczby z raportu]

**ANALIZA MOMENTUM:**
[Czy akceleracja? Trend]

**JAKOŚĆ WYNIKÓW:**
[Organiczny wzrost? FCF? Marże?]

**TON ZARZĄDU:**
[Optymistyczny/Ostrożny/Pesymistyczny + cytaty]

**PRAWDOPODOBNA REAKCJA:**
[Dlaczego rynek zareaguje tak a nie inaczej]

**RYZYKA:**
[2-3 główne zagrożenia]

**CONFIDENCE LEVEL:** [X/10]

Bądź konkretny i używaj liczb z dokumentu."""

        # Wywołaj Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(url, json=payload, timeout=45)
        response.raise_for_status()
        
        result = response.json()
        
        # Wyciągnij tekst z odpowiedzi
        if 'candidates' in result and len(result['candidates']) > 0:
            analysis_text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"   → Otrzymano analizę AI ({len(analysis_text)} znaków)")
            return {'analysis': analysis_text, 'raw_response': result}
        else:
            print("   → Gemini nie zwrócił analizy")
            return None
            
    except Exception as e:
        print(f"   → Błąd Gemini API: {e}")
        return None

# ============================================
# FUNKCJE SEC (bez zmian - Twoje oryginalne)
# ============================================

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
        print(f"Error for {ticker}: {e}")
        return []

def analyze_8k_content(accession_number: str, ticker: str) -> Dict:
    """Analizuje zawartość 8-K i zwraca Items + pełny tekst dokumentu"""
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
        max_impact = 0
        
        for item_num, item_desc in IMPORTANT_ITEMS.items():
            if f"item {item_num}" in content_lower:
                impact = IMPACT_SCORE.get(item_num, 5)
                detected_items.append({
                    'code': item_num,
                    'description': item_desc,
                    'impact': impact
                })
                max_impact = max(max_impact, impact)
        
        found_keywords = [kw for kw in KEYWORDS if kw in content_lower]
        
        # Importance score bazuje na najwyzszym impact score + keywords
        importance_score = max_impact + len(found_keywords)
        
        return {
            'items': detected_items,
            'keywords': found_keywords[:5],
            'importance': importance_score,
            'max_impact': max_impact,
            'full_document': content,
            'url': f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}"
        }
        
    except Exception as e:
        print(f"Error analyzing {accession_number}: {e}")
        return {
            'items': [], 
            'keywords': [], 
            'importance': 0,
            'max_impact': 0,
            'full_document': '',
            'url': filing_url
        }

# ============================================
# FUNKCJE DISCORD (Twoje oryginalne + nowa)
# ============================================

def analyze_sentiment(analysis: Dict, ticker: str) -> Dict:
    """Analiza sentymentu na podstawie słów kluczowych"""
    keywords = analysis.get('keywords', [])
    bullish_kw = ['partnership', 'collaboration', 'strategic', 'agreement', 'contract', 
                  'revenue', 'earnings', 'growth', 'expansion', 'joint venture']
    bearish_kw = ['loss', 'decline', 'lawsuit', 'investigation', 'bankruptcy', 
                  'restructuring', 'termination', 'failure']
    
    bullish_score = sum(1 for kw in keywords if kw in bullish_kw)
    bearish_score = sum(1 for kw in keywords if kw in bearish_kw)
    
    if bullish_score > bearish_score:
        sentiment = "BULLISH"
        color = 5763719
        interpretation = "Pozytywne wiadomosci moga wspierac wzrost ceny."
        if 'partnership' in keywords or 'collaboration' in keywords:
            interpretation += " Nowe partnerstwo moze otworzyc dodatkowe zrodla przychodow."
        elif 'revenue' in keywords or 'earnings' in keywords:
            interpretation += " Dobre wyniki finansowe moga przyciagnac inwestorow."
    elif bearish_score > bullish_score:
        sentiment = "BEARISH"
        color = 15158332
        interpretation = "Negatywne wiadomosci moga wywrzec presje na cene akcji."
    else:
        sentiment = "NEUTRALNY"
        color = 15844367
        interpretation = "Wiadomosci maja mieszany charakter."
    
    return {'sentiment': sentiment, 'color': color, 'interpretation': interpretation}

def send_discord_alert(filing: Dict, analysis: Dict):
    """ORYGINALNA FUNKCJA - POZOSTAJE BEZ ZMIAN!"""
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
        publication_time = f"{date} (brak dokladnej godziny)"
    
    sentiment_data = analyze_sentiment(analysis, ticker)
    tradingview_link = f"https://www.tradingview.com/chart/?symbol={ticker}"
    
    # Priority based on max impact score
    max_impact = analysis.get('max_impact', 0)
    if max_impact >= 9:
        priority = "🔴 BARDZO WAZNE"
    elif max_impact >= 7:
        priority = "🟠 WAZNE"
    elif max_impact >= 5:
        priority = "🟡 SREDNIE"
    else:
        priority = "🟢 INFORMACYJNE"
    
    related_companies = RELATIONSHIPS.get(ticker, {})
    if related_companies:
        related_list = []
        count = 0
        for related_ticker, reason in related_companies.items():
            if count >= 4:
                break
            tv_link = f"https://www.tradingview.com/chart/?symbol={related_ticker}"
            related_list.append(f"[{related_ticker}]({tv_link}) - {reason}")
            count += 1
        related_text = "\n".join(related_list)
    else:
        related_text = "Brak bezposrednich powiazan"
    
    # Format items with impact scores and emoji indicators
    if analysis['items']:
        items_list = []
        for item in analysis['items']:
            impact = item['impact']
            # Emoji based on impact score
            if impact >= 9:
                emoji = "🔴"  # Critical
            elif impact >= 7:
                emoji = "🟠"  # High
            elif impact >= 5:
                emoji = "🟡"  # Medium
            else:
                emoji = "🟢"  # Low
            
            items_list.append(f"{emoji} Item {item['code']} - {item['description']} (Impact: {impact}/10)")
        items_text = "\n".join(items_list)
    else:
        items_text = "Brak wykrytych Items"
    
    keywords_text = ", ".join(analysis['keywords']) if analysis['keywords'] else "Brak"
    
    doc_data = analysis.get('document_excerpt', {})
    if isinstance(doc_data, dict):
        document_excerpt = doc_data.get('excerpt', 'Brak fragmentu')
        key_numbers = doc_data.get('key_numbers', 'Brak danych')
    else:
        document_excerpt = str(doc_data)
        key_numbers = 'Brak danych'
    
    embed = {
        "title": f"{priority} - Nowy raport 8-K",
        "description": f"**{company} ({ticker})**\n*{company_desc}*\n\n{sentiment_data['sentiment']}\n*{sentiment_data['interpretation']}*",
        "color": sentiment_data['color'],
        "fields": [
            {"name": "Data zgloszenia", "value": date, "inline": True},
            {"name": "Impact Score", "value": f"{analysis.get('max_impact', 0)}/10 (Waznosc: {analysis['importance']})", "inline": True},
            {"name": "Wykryte kategorie", "value": items_text, "inline": False},
            {"name": "Kluczowe slowa", "value": keywords_text, "inline": False},
            {"name": "Potencjalny wplyw na", "value": related_text, "inline": False},
            {"name": "Wykres", "value": f"[Otworz na TradingView]({tradingview_link})", "inline": True},
            {"name": "Dokument SEC", "value": f"[Otworz raport]({analysis['url']})", "inline": True},
            {"name": "FRAGMENT DOKUMENTU (tlumaczenie)", "value": f"```{document_excerpt[:900]}```", "inline": False},
            {"name": "KLUCZOWE DANE", "value": key_numbers, "inline": False},
            {"name": "Publikacja na SEC", "value": publication_time, "inline": False}
        ],
        "footer": {"text": f"SEC EDGAR Monitor v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✓ Alert sent to Channel #1: {ticker} - {date}")
    except Exception as e:
        print(f"✗ Error sending alert to Channel #1: {e}")

def send_ai_analysis_alert(filing: Dict, gemini_analysis: Dict):
    """NOWA FUNKCJA - tylko dla kanału #2"""
    if not DISCORD_WEBHOOK_AI:
        print("   → Brak DISCORD_WEBHOOK_AI - pomijam wysyłkę AI")
        return
    
    if not gemini_analysis or 'analysis' not in gemini_analysis:
        print("   → Brak analizy Gemini - pomijam wysyłkę AI")
        return
    
    ticker = filing['ticker']
    company = filing['company']
    
    # Format jak w przykładzie Google
    analysis_text = gemini_analysis['analysis']
    
    # Discord ma limit 2000 znaków na embed description
    # Podziel na wiele pól jeśli potrzeba
    
    embed = {
        "title": f"🤖 PEŁNA ANALIZA AI - {company} ({ticker})",
        "description": analysis_text[:1800],  # Pierwsze 1800 znaków
        "color": 5814783,  # Niebieski kolor
        "footer": {
            "text": f"SEC AI Analyst v2.0 | Powered by Gemini | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_AI, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✓ AI Analysis sent to Channel #2: {ticker}")
    except Exception as e:
        print(f"✗ Error sending AI analysis: {e}")

# ============================================
# GŁÓWNA FUNKCJA
# ============================================

def check_new_filings():
    print(f"\n{'='*60}")
    print(f"Checking new 8-K filings... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"{'='*60}")
    
    processed_filings = load_processed_filings_from_gist()
    new_filings_count = 0
    ai_analysis_count = 0
    
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
            
            print(f"\n🆕 NEW FILING: {ticker} - {filing['filingDate']}")
            
            # Analiza podstawowa
            analysis = analyze_8k_content(filing['accessionNumber'], ticker)
            
            if analysis['items']:
                # KROK 1: Wyślij zwykły alert (kanał #1) - Twoja oryginalna funkcja
                send_discord_alert(filing, analysis)
                new_filings_count += 1
                
                # KROK 2: Pobierz dane Yahoo Finance
                yahoo_data = get_yahoo_finance_data(ticker)
                time.sleep(1)  # Rate limiting
                
                # KROK 3: Analiza AI z Gemini
                if analysis.get('full_document'):
                    gemini_analysis = analyze_with_gemini(
                        analysis['full_document'],
                        ticker,
                        filing['company'],
                        yahoo_data
                    )
                    
                    # KROK 4: Wyślij AI analysis (kanał #2)
                    if gemini_analysis:
                        send_ai_analysis_alert(filing, gemini_analysis)
                        ai_analysis_count += 1
                        time.sleep(2)  # Rate limiting
            else:
                print(f"   ↳ Pominieto (brak istotnych Items)")
            
            processed_filings.add(filing_id)
    
    save_processed_filings_to_gist(processed_filings)
    
    print(f"\n{'='*60}")
    if new_filings_count == 0:
        print("✓ No new filings requiring alerts")
    else:
        print(f"✓ Sent {new_filings_count} alert(s) to Channel #1")
        print(f"✓ Sent {ai_analysis_count} AI analysis to Channel #2")
    print(f"{'='*60}\n")

def main():
    print("\n" + "="*60)
    print("SEC 8-K Monitor v2.0 - EXTENDED + AI")
    print("="*60)
    print(f"Companies monitored: {len(COMPANIES)}")
    print(f"Gist storage: {'✓ ENABLED' if GIST_TOKEN and GIST_ID else '✗ DISABLED'}")
    print(f"AI Analysis: {'✓ ENABLED' if GEMINI_API_KEY else '✗ DISABLED'}")
    print("="*60)
    
    if not DISCORD_WEBHOOK_URL:
        print("\n⚠️  WARNING: DISCORD_WEBHOOK_URL not set!")
        return
    
    check_new_filings()
    print("\n✓ Monitor run completed\n")

if __name__ == "__main__":
    main()
