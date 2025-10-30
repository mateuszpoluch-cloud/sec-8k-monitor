import requests
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Set

# Konfiguracja
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
GIST_TOKEN = os.environ.get('GIST_TOKEN', '')
GIST_ID = os.environ.get('GIST_ID', '')
USER_AGENT = "SEC-Monitor/2.0 (your-email@example.com)"  # ZMIEN NA SWOJ EMAIL

# Lista spolek - ROZSZERZONA do 51 spolek!
COMPANIES = {
    # === QUANTUM COMPUTING ===
    'IONQ': {'name': 'IonQ', 'cik': '0001852179', 'desc': 'Komputery kwantowe oparte na jonach'},
    'RGTI': {'name': 'Rigetti Computing', 'cik': '0001846163', 'desc': 'Quantum computing as a service'},
    'QUBT': {'name': 'Quantum Computing Inc', 'cik': '0001635004', 'desc': 'Rozwiazania kwantowe dla biznesu'},
    'QBTS': {'name': 'D-Wave Quantum', 'cik': '0001808665', 'desc': 'Quantum annealing systems'},
    
    # === BIG TECH & CLOUD ===
    'IBM': {'name': 'IBM', 'cik': '0000051143', 'desc': 'Quantum computing, AI, cloud infrastructure'},
    'MSFT': {'name': 'Microsoft', 'cik': '0000789019', 'desc': 'Azure cloud, AI, quantum research'},
    'AMZN': {'name': 'Amazon', 'cik': '0001018724', 'desc': 'AWS cloud, AI services, infrastructure'},
    'GOOGL': {'name': 'Alphabet', 'cik': '0001652044', 'desc': 'Google Cloud, AI, quantum computing'},
    
    # === SEMICONDUCTORS (EXISTING + NEW) ===
    'NVDA': {'name': 'NVIDIA', 'cik': '0001045810', 'desc': 'Producent chipow GPU dla AI i datacenter'},
    'AMD': {'name': 'AMD', 'cik': '0000002488', 'desc': 'Procesory, GPU i chipy dla datacenter'},
    'INTC': {'name': 'Intel', 'cik': '0000050863', 'desc': 'Procesory CPU i komponenty polprzewodnikowe'},
    'AVGO': {'name': 'Broadcom', 'cik': '0001730168', 'desc': 'Chipy komunikacyjne i polprzewodniki'},
    'QCOM': {'name': 'Qualcomm', 'cik': '0000804328', 'desc': 'Chipy mobilne i technologie bezprzewodowe'},
    'MRVL': {'name': 'Marvell', 'cik': '0001058057', 'desc': 'Polprzewodniki dla datacenter i 5G'},
    'TSM': {'name': 'TSMC', 'cik': '0001046179', 'desc': 'Najwieksza fabryka chipow (foundry)'},
    'SNPS': {'name': 'Synopsys', 'cik': '0000883241', 'desc': 'Narzedzia EDA do projektowania chipow'},
    'ARM': {'name': 'Arm Holdings', 'cik': '0001996864', 'desc': 'Architektura procesorow ARM'},
    
    # === SEMICONDUCTOR EQUIPMENT ===
    'ASML': {'name': 'ASML', 'cik': '0000937966', 'desc': 'Maszyny litograficzne do produkcji chipow'},
    'AMAT': {'name': 'Applied Materials', 'cik': '0000006951', 'desc': 'Sprzet do produkcji polprzewodnikow'},
    'LRCX': {'name': 'Lam Research', 'cik': '0000707549', 'desc': 'Technologie trawienia i depozycji chipow'},
    'KLAC': {'name': 'KLA Corporation', 'cik': '0000319201', 'desc': 'Kontrola jakosci w produkcji chipow'},
    'ENTG': {'name': 'Entegris', 'cik': '0001101302', 'desc': 'Materialy chemiczne do produkcji chipow'},
    
    # === MEMORY & STORAGE ===
    'MU': {'name': 'Micron', 'cik': '0000723125', 'desc': 'Pamieci RAM i storage dla AI'},
    'WDC': {'name': 'Western Digital', 'cik': '0000106040', 'desc': 'Dyski twarde i pamieci flash'},
    'STX': {'name': 'Seagate', 'cik': '0001137789', 'desc': 'Dyski twarde i rozwiazania storage'},
    
    # === POWER & COMPONENTS ===
    'MPWR': {'name': 'Monolithic Power', 'cik': '0001280452', 'desc': 'Uklady zarzadzania energia'},
    
    # === DATA CENTERS & INFRASTRUCTURE ===
    'EQIX': {'name': 'Equinix', 'cik': '0001101239', 'desc': 'Globalne data centers i colocation'},
    'DLR': {'name': 'Digital Realty', 'cik': '0001297996', 'desc': 'Data center REITs dla cloud/AI'},
    'AMT': {'name': 'American Tower', 'cik': '0001053507', 'desc': 'Infrastruktura telekomunikacyjna'},
    'VRT': {'name': 'Vertiv Holdings', 'cik': '0001839992', 'desc': 'Infrastruktura IT i chlodzenie'},
    'EME': {'name': 'EMCOR Group', 'cik': '0000105634', 'desc': 'Konstrukcja i serwis data centers'},
    'PWR': {'name': 'Quanta Services', 'cik': '0001050915', 'desc': 'Infrastruktura energetyczna'},
    
    # === NETWORKING & CONNECTIVITY ===
    'IRDM': {'name': 'Iridium', 'cik': '0001418819', 'desc': 'Komunikacja satelitarna'},
    
    # === AI INFRASTRUCTURE & SERVERS ===
    'HPE': {'name': 'Hewlett Packard Enterprise', 'cik': '0001645590', 'desc': 'Serwery i infrastruktura AI'},
    'SMCI': {'name': 'Super Micro Computer', 'cik': '0001375365', 'desc': 'Serwery AI i high-performance computing'},
    'APLD': {'name': 'Applied Digital', 'cik': '0001144879', 'desc': 'Data centers dla AI i HPC'},
    
    # === CLOUD & SOFTWARE ===
    'ORCL': {'name': 'Oracle', 'cik': '0001341439', 'desc': 'Bazy danych i cloud computing'},
    'SNOW': {'name': 'Snowflake', 'cik': '0001640147', 'desc': 'Platforma analityki danych w chmurze'},
    'MDB': {'name': 'MongoDB', 'cik': '0001441404', 'desc': 'Bazy danych NoSQL'},
    'PLTR': {'name': 'Palantir', 'cik': '0001321655', 'desc': 'Analityka AI i big data'},
    
    # === BIOTECH & PHARMA ===
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

# Powiazania miedzy spolkami - ROZSZERZONE
RELATIONSHIPS = {
    # === QUANTUM ECOSYSTEM ===
    'IONQ': {'IBM': 'konkurencja w quantum computing', 'GOOGL': 'rynek quantum cloud'},
    'RGTI': {'IBM': 'konkurencja quantum', 'MSFT': 'Azure quantum partnership'},
    'IBM': {'NVDA': 'GPU dla quantum simulations', 'GOOGL': 'konkurencja w quantum'},
    
    # === CLOUD GIANTS ===
    'MSFT': {'NVDA': 'kupuje GPU dla Azure AI', 'AMZN': 'konkurencja cloud'},
    'AMZN': {'NVDA': 'AWS kupuje GPU', 'MSFT': 'konkurencja cloud'},
    'GOOGL': {'NVDA': 'GCP kupuje GPU', 'TSM': 'projektuje wlasne chipy TPU'},
    
    # === SEMICONDUCTOR CHAIN ===
    'ASML': {'TSM': 'produkuje maszyny litograficzne dla TSMC', 'INTC': 'dostarcza sprzet produkcyjny'},
    'TSM': {'NVDA': 'produkuje chipy GPU', 'AMD': 'produkuje procesory i GPU', 'GOOGL': 'produkuje TPU'},
    'NVDA': {'TSM': 'TSMC produkuje ich chipy', 'MU': 'Micron dostarcza pamieci', 'SMCI': 'serwery z GPU'},
    'AMD': {'TSM': 'TSMC produkuje procesory/GPU', 'MU': 'Micron dostarcza pamieci'},
    'INTC': {'AMAT': 'kupuje sprzet produkcyjny', 'ASML': 'kupuje maszyny EUV'},
    'SNPS': {'TSM': 'narzedzia do projektowania chipow', 'NVDA': 'wspolpraca w chip design'},
    
    # === MEMORY & COMPUTE ===
    'MU': {'NVDA': 'pamieci HBM dla GPU', 'AMD': 'pamieci dla procesorow', 'SMCI': 'RAM dla serwer ow AI'},
    'STX': {'NVDA': 'storage dla AI/datacenter', 'ORCL': 'storage dla baz danych'},
    'WDC': {'AMZN': 'storage dla AWS', 'MSFT': 'storage dla Azure'},
    
    # === DATA CENTER ECOSYSTEM ===
    'EQIX': {'NVDA': 'data centers dla AI', 'MSFT': 'colocation dla Azure', 'GOOGL': 'space dla GCP'},
    'DLR': {'AMZN': 'data centers dla AWS', 'ORCL': 'hosting dla Oracle Cloud'},
    'SMCI': {'NVDA': 'integruje GPU w serwery', 'AMD': 'serwery z EPYC', 'INTC': 'serwery z Xeon'},
    'APLD': {'NVDA': 'HPC clusters z GPU', 'SMCI': 'kupuje serwery AI'},
    'HPE': {'NVDA': 'serwery AI z GPU', 'AMD': 'serwery z EPYC'},
    
    # === POWER & INFRASTRUCTURE ===
    'VRT': {'EQIX': 'chlodzenie dla data centers', 'NVDA': 'cooling dla GPU clusters'},
    'MPWR': {'NVDA': 'power management dla GPU', 'AMD': 'zasilanie procesorow'},
    'PWR': {'EQIX': 'budowa infrastruktury', 'DLR': 'elektryka data centers'},
    'EME': {'EQIX': 'konstrukcja data centers', 'DLR': 'inzynieria obiektow'},
    
    # === BIOTECH CONNECTIONS ===
    'REGN': {'NVDA': 'AI drug discovery', 'GOOGL': 'AI w badaniach'},
    'MRNA': {'MSFT': 'AI w projektowaniu RNA', 'IBM': 'quantum dla farmacji'},
    'LLY': {'NVDA': 'AI w badaniach', 'MSFT': 'Azure dla R&D'},
}

IMPORTANT_ITEMS = {
    '1.01': 'Przejecia/Fuzje/Akwizycje',
    '1.02': 'Zakup/Sprzedaz aktywow',
    '8.01': 'Inne istotne wydarzenia',
    '2.02': 'Wyniki finansowe'
}

KEYWORDS = ['acquisition', 'merger', 'partnership', 'agreement', 'contract', 'collaboration', 
            'joint venture', 'strategic', 'ai', 'artificial intelligence', 'chip', 'semiconductor', 
            'revenue', 'earnings', 'guidance', 'quantum', 'cloud', 'datacenter', 'biotech']

# === FUNKCJE GIST (bez zmian) ===

def load_processed_filings_from_gist() -> Set[str]:
    """Pobiera liste przetworzonych zgloszen z GitHub Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("WARNING: Brak GIST_TOKEN lub GIST_ID - uzywam lokalnego pliku")
        return load_processed_filings_local()
    
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
            print("Gist nie zawiera pliku processed_filings.json - tworze nowy")
            return set()
            
    except Exception as e:
        print(f"ERROR: Nie udalo sie pobrac danych z Gist: {e}")
        print("Uzywam lokalnego pliku jako fallback")
        return load_processed_filings_local()

def save_processed_filings_to_gist(processed: Set[str]):
    """Zapisuje liste przetworzonych zgloszen do GitHub Gist"""
    if not GIST_TOKEN or not GIST_ID:
        print("WARNING: Brak GIST_TOKEN lub GIST_ID - zapisuje lokalnie")
        save_processed_filings_local(processed)
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
        print("Zapisuje lokalnie jako fallback")
        save_processed_filings_local(processed)

def load_processed_filings_local() -> Set[str]:
    """Lokalne ladowanie z pliku (fallback)"""
    try:
        with open('processed_filings.json', 'r') as f:
            data = json.load(f)
            return set(data.get('filings', []))
    except FileNotFoundError:
        return set()

def save_processed_filings_local(processed: Set[str]):
    """Lokalne zapisywanie do pliku (fallback)"""
    with open('processed_filings.json', 'w') as f:
        json.dump({'filings': list(processed), 'last_updated': datetime.now().isoformat()}, f)

# === POZOSTALE FUNKCJE (bez zmian) ===

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

def translate_to_polish_full(text: str) -> str:
    import re
    translations = {
        'FINANCIAL RESULTS': 'WYNIKI FINANSOWE', 'financial results': 'wyniki finansowe',
        'year-over-year': 'rok do roku', 'compared to': 'w porownaniu do',
        'cash flow from operations': 'przeplywy pieniezne z operacji',
        'free cash flow': 'wolne przeplywy pieniezne',
        'returned to shareholders': 'zwrocono akcjonariuszom',
        'diluted EPS': 'rozwodniony zysk na akcje', 'per share': 'na akcje',
        'gross margin': 'marza brutto', 'net income': 'zysk netto',
        'TECHNOLOGY': 'TECHNOLOGIA', 'REPORTS': 'RAPORTUJE',
        'FISCAL': 'FISKALNY', 'Quarter': 'Kwartal', 'quarter': 'kwartal',
        'Highlights': 'Najwazniejsze', 'Revenue': 'Przychody', 'revenue': 'przychody',
        'billion': 'miliardow', 'million': 'milionow', 'earnings': 'zyski',
        'approximately': 'okolo', 'dividends': 'dywidendy', 'shares': 'akcji',
        'shareholders': 'akcjonariuszy', 'partnership': 'partnerstwo',
    }
    
    result = text
    for eng, pl in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        if ' ' in eng:
            result = result.replace(eng, pl)
        else:
            pattern = r'\b' + re.escape(eng) + r'\b'
            result = re.sub(pattern, pl, result)
    return result

def extract_key_numbers(text: str) -> str:
    import re
    summary = []
    
    rev_match = re.search(r'(?:revenue|revenues|przychody).*?\$?\s*(\d+[\.,]\d+)\s*(?:billion|miliardow|mld)', text, re.I)
    if rev_match:
        amount = rev_match.group(1).replace(',', '.')
        summary.append(f"Przychody: ${amount} mld")
    
    earn_match = re.search(r'(?:net income|zysk netto|earnings|zyski).*?\$?\s*(\d+[\.,]?\d*)\s*(?:million|billion|milionow|miliardow|mln|mld)', text, re.I)
    if earn_match:
        amount = earn_match.group(1).replace(',', '.')
        unit = 'mld' if 'billion' in earn_match.group(0).lower() or 'miliardow' in earn_match.group(0).lower() else 'mln'
        summary.append(f"Zysk netto: ${amount} {unit}")
    
    margin_match = re.search(r'(?:gross margin|marza brutto).*?(\d+[\.,]\d+)%', text, re.I)
    if margin_match:
        margin = margin_match.group(1).replace(',', '.')
        summary.append(f"Marza brutto: {margin}%")
    
    eps_match = re.search(r'(?:EPS|zysk na akcje|per share).*?\$?\s*(\d+[\.,]\d+)', text, re.I)
    if eps_match:
        eps = eps_match.group(1).replace(',', '.')
        summary.append(f"EPS: ${eps}")
    
    growth_match = re.search(r'(?:wzrost|growth|increased).*?(\d+)%', text, re.I)
    if growth_match:
        growth = growth_match.group(1)
        summary.append(f"Wzrost r/r: +{growth}%")
    
    cf_match = re.search(r'(?:free cash flow|wolne przeplywy).*?\$?\s*(\d+)\s*(?:million|milionow|mln)', text, re.I)
    if cf_match:
        cf = cf_match.group(1)
        summary.append(f"Free Cash Flow: ${cf} mln")
    
    if summary:
        return "\n".join(summary)
    else:
        return "Brak kluczowych danych liczbowych"

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
                excerpt = re.sub(r'Investor Relations Contact:.*?(?=\w{5,}\s+\w{5,})', '', excerpt, flags=re.I | re.DOTALL)
                excerpt = re.sub(r'Contact:.*?@\S+', '', excerpt, flags=re.I)
                excerpt = re.sub(r'\(\d{3}\)\s*\d{3}-\d{4}', '', excerpt)
                excerpt = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', excerpt)
                excerpt = excerpt.replace('&nbsp;', ' ')
                excerpt = re.sub(r'[•◦▪□■►▶]', '', excerpt)
                excerpt = re.sub(r'\s+', ' ', excerpt).strip()
                
                words = excerpt.split()
                start_idx = 0
                for i, word in enumerate(words):
                    if len(word) > 4 and any(c.isalpha() for c in word):
                        start_idx = i
                        break
                excerpt = ' '.join(words[start_idx:])
                
                if len(excerpt) > 1000:
                    end = excerpt[:1000].rfind('.')
                    if end > 400:
                        excerpt = excerpt[:end+1]
                    else:
                        excerpt = excerpt[:1000]
                
                excerpt_pl = translate_to_polish_full(excerpt)
                key_numbers = extract_key_numbers(excerpt_pl)
                
                return {'excerpt': excerpt_pl, 'key_numbers': key_numbers}
    
    return {'excerpt': 'Nie udalo sie wyodrebnic fragmentu dokumentu', 'key_numbers': 'N/A'}

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
            'document_excerpt': {'excerpt': 'Blad pobierania', 'key_numbers': 'N/A'},
            'url': filing_url
        }

def analyze_sentiment(analysis: Dict, ticker: str) -> Dict:
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
    
    if analysis['importance'] >= 5:
        priority = "🔴 BARDZO WAZNE"
    elif analysis['importance'] >= 3:
        priority = "🟡 WAZNE"
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
    
    items_text = "\n".join([f"{item}" for item in analysis['items']]) if analysis['items'] else "Brak wykrytych Items"
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
            {"name": "Ocena waznosci", "value": f"{analysis['importance']}/10", "inline": True},
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
        print(f"✓ Alert sent: {ticker} - {date}")
    except Exception as e:
        print(f"✗ Error sending alert: {e}")

def check_new_filings():
    print(f"\n{'='*60}")
    print(f"Checking new 8-K filings... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"{'='*60}")
    
    processed_filings = load_processed_filings_from_gist()
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
            
            print(f"🆕 NEW FILING: {ticker} - {filing['filingDate']}")
            
            analysis = analyze_8k_content(filing['accessionNumber'], ticker)
            
            if analysis['items']:
                send_discord_alert(filing, analysis)
                new_filings_count += 1
            else:
                print(f"   ↳ Pominieto (brak istotnych Items)")
            
            processed_filings.add(filing_id)
    
    save_processed_filings_to_gist(processed_filings)
    
    print(f"\n{'='*60}")
    if new_filings_count == 0:
        print("✓ No new filings requiring alerts")
    else:
        print(f"✓ Sent {new_filings_count} new alert(s)")
    print(f"{'='*60}\n")

def main():
    print("\n" + "="*60)
    print("SEC 8-K Monitor v2.0 - EXTENDED EDITION")
    print("="*60)
    print(f"Companies monitored: {len(COMPANIES)}")
    print(f"Categories: Quantum, Cloud, Semiconductors, DataCenter, Biotech")
    print(f"Important items: {', '.join(IMPORTANT_ITEMS.keys())}")
    print(f"Gist storage: {'✓ ENABLED' if GIST_TOKEN and GIST_ID else '✗ DISABLED (using local file)'}")
    print("="*60)
    
    if not DISCORD_WEBHOOK_URL:
        print("\n⚠️  WARNING: DISCORD_WEBHOOK_URL not set in GitHub Secrets!")
        return
    
    check_new_filings()
    print("\n✓ Monitor run completed\n")

if __name__ == "__main__":
    main()
