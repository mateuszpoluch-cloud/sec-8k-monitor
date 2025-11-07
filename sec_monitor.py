#!/usr/bin/env python3
"""
SEC 8-K Monitor v2.1 - MULTI-ITEM ANALYSIS + AI (Groq)
- Dedykowane prompty dla każdego Item type
- Analiza kombinacji multiple Items
- Combined verdict uwzględniający interakcje między Items
"""

import requests
import json
from datetime import datetime, timedelta
import os
import time
import re
from typing import List, Dict, Set

# ============================================
# KONFIGURACJA
# ============================================

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '').strip()
DISCORD_WEBHOOK_AI = os.environ.get('DISCORD_WEBHOOK_AI', '').strip()
GIST_TOKEN = os.environ.get('GIST_TOKEN', '').strip()
GIST_ID = os.environ.get('GIST_ID', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
USER_AGENT = "SEC-Monitor/2.1 (your-email@example.com)"

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

IMPACT_SCORE = {
    '2.02': 10,
    '1.01': 9,
    '4.02': 9,
    '5.02': 8,
    '2.05': 7,
    '8.01': 7,
    '3.03': 6,
    '1.02': 5,
    '2.03': 5,
    '7.01': 5,
}

KEYWORDS = ['acquisition', 'merger', 'partnership', 'agreement', 'contract', 'collaboration', 
            'joint venture', 'strategic', 'ai', 'artificial intelligence', 'chip', 'semiconductor', 
            'revenue', 'earnings', 'guidance', 'quantum', 'cloud', 'datacenter', 'biotech']

# ============================================
# ✅ ITEM-SPECIFIC PROMPTS FOR GROQ
# ============================================

ITEM_PROMPTS = {
    '2.02': {  # EARNINGS
        'focus': 'wyniki finansowe, beat/meet/miss, guidance',
        'questions': """
- EPS: actual vs consensus vs prior quarter (beat by X%?)
- Revenue: actual vs consensus vs YoY growth
- Guidance: raised/lowered/maintained?
- Margins: gross/operating/net margins trend
- Key growth metrics and KPIs
- Free Cash Flow generation
- Management outlook and tone
"""
    },
    
    '1.01': {  # ACQUISITION/MERGER
        'focus': 'przejęcia, fuzje, akwizycje',
        'questions': """
- Target company & acquisition price
- Strategic fit (does it make sense?)
- Expected synergies (cost savings + revenue growth)
- Accretive or dilutive to EPS?
- Expected closing date
- Financing structure (cash/stock/debt)
- Market reaction likely?
"""
    },
    
    '5.02': {  # EXECUTIVE CHANGES
        'focus': 'zmiany w zarządzie, CEO, CFO',
        'questions': """
- Who's leaving/joining and which position?
- Reason for departure (retirement/resignation/fired?)
- New executive's track record and experience
- Timing - why now? (red flag or planned succession?)
- Impact on company strategy
- Market typically reacts how to such changes?
"""
    },
    
    '1.02': {  # ASSET PURCHASE/SALE
        'focus': 'zakup/sprzedaż aktywów',
        'questions': """
- What asset was bought/sold?
- Transaction price and terms
- Strategic rationale (expansion/divestiture/optimization?)
- Impact on balance sheet (leverage, cash position)
- Multiple paid (reasonable valuation?)
"""
    },
    
    '2.05': {  # RESTRUCTURING
        'focus': 'restrukturyzacja, koszty',
        'questions': """
- Total restructuring costs (one-time charges)
- Expected annual savings once complete
- Layoffs - how many people affected?
- Timeline - when will savings materialize?
- Is this a red flag (company in trouble) or proactive move?
"""
    },
    
    '4.02': {  # RESTATEMENT
        'focus': 'korekta wyników finansowych - RED FLAG!',
        'questions': """
⚠️ RESTATEMENT IS SERIOUS - USUALLY MAJOR RED FLAG!

- Which periods are being restated?
- Magnitude of the error (material or minor?)
- Reason: accounting error, fraud, or rule change?
- Impact on investor trust and credibility
- Potential legal/SEC investigation consequences
"""
    },
    
    '2.03': {  # MATERIAL OBLIGATIONS
        'focus': 'nowe zobowiązania finansowe, dług, obligacje',
        'questions': """
- Type of obligation (bonds, credit facility, loan)
- Amount and terms (interest rate, maturity date)
- Purpose - what will they finance with this capital?
- Impact on leverage (new debt/equity ratio)
- Credit rating implications
- Restrictive covenants?
"""
    },
    
    '3.03': {  # STOCK SPLIT
        'focus': 'split akcji',
        'questions': """
- Split ratio (2-for-1, 3-for-1, etc.)
- Reason: stock price too high? Increase liquidity?
- Historical impact of splits in this sector
- Sentiment - usually positive signal
- Timing - why now?
"""
    },
    
    '7.01': {  # SEC REGULATIONS
        'focus': 'regulacje SEC, compliance',
        'questions': """
- What regulation was introduced/updated?
- Impact on financial reporting or operations
- Compliance costs (material or minor?)
- Implementation timeline
- Company-specific or industry-wide issue?
"""
    },
    
    '8.01': {  # OTHER MATERIAL EVENTS
        'focus': 'inne istotne wydarzenia',
        'questions': """
- What event occurred?
- Why is it considered material?
- Impact on business (short-term and long-term)
- Potential financial implications
"""
    },
}

# ============================================
# ✅ ITEM INTERACTION EXAMPLES
# ============================================

ITEM_INTERACTION_EXAMPLES = """
PRZYKŁADY INTERAKCJI MIĘDZY ITEMS:

1. Earnings BEAT + CEO Departure = MIXED/BEARISH
   → Pozytywne wyniki, ale niepewność przywództwa przeważa

2. Earnings BEAT + Acquisition = STRONG BULLISH
   → Wzrost organiczny + strategiczne przejęcie = momentum

3. Earnings MISS + Restructuring = MOŻE BYĆ POZYTYWNE
   → Zarząd reaguje na problemy, obniża koszty = future improvement

4. Good Earnings + Restatement = STRONG BEARISH 🔴
   → Nawet dobre wyniki NIE RATUJĄ - zaufanie zniszczone!

5. Earnings + Stock Split = BULLISH
   → Już dobre wyniki + split = increased accessibility

6. Acquisition + New Debt = NEUTRAL TO BEARISH
   → Zależy od ceny przejęcia i poziomu zadłużenia

7. CEO Change + Restructuring = RED FLAG
   → Zwykle oznacza poważne problemy w firmie

8. Earnings + New Regulations = DEPENDS
   → Jeśli regulation industry-wide = neutral
   → Jeśli tylko ta firma = potential red flag
"""

# ============================================
# FUNKCJE GIST
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
# YAHOO FINANCE INTEGRATION
# ============================================

def get_yahoo_finance_data(ticker: str) -> Dict:
    """Pobiera dane z Yahoo Finance: konsensus EPS, revenue, target price, previous quarter"""
    try:
        import yfinance as yf
        
        print(f"   → Pobieranie danych Yahoo Finance dla {ticker}...")
        
        stock = yf.Ticker(ticker)
        
        # Inicjalizuj strukturę danych
        yahoo_data = {
            'current_price': None,
            'market_cap': None,
            'consensus_eps': None,
            'consensus_revenue': None,
            'target_price': None,
            'target_high': None,
            'target_low': None,
            'analyst_ratings': {'strong_buy': 0, 'buy': 0, 'hold': 0, 'sell': 0, 'strong_sell': 0},
            'previous_quarter': {},
            'pe_ratio': None,
            'forward_pe': None,
            '52week_high': None,
            '52week_low': None,
            'beta': None
        }
        
        # ✅ 1. BASIC INFO
        info = stock.info
        
        yahoo_data['current_price'] = info.get('currentPrice') or info.get('regularMarketPrice')
        yahoo_data['market_cap'] = info.get('marketCap')
        yahoo_data['pe_ratio'] = info.get('trailingPE')
        yahoo_data['forward_pe'] = info.get('forwardPE')
        yahoo_data['52week_high'] = info.get('fiftyTwoWeekHigh')
        yahoo_data['52week_low'] = info.get('fiftyTwoWeekLow')
        yahoo_data['beta'] = info.get('beta')
        
        # ✅ 2. ANALYST ESTIMATES (Forward Looking)
        yahoo_data['consensus_eps'] = info.get('forwardEps')
        yahoo_data['consensus_revenue'] = info.get('revenueEstimate')
        
        # ✅ 3. PRICE TARGETS
        yahoo_data['target_price'] = info.get('targetMeanPrice')
        yahoo_data['target_high'] = info.get('targetHighPrice')
        yahoo_data['target_low'] = info.get('targetLowPrice')
        
        # ✅ 4. ANALYST RECOMMENDATIONS
        recommendations = info.get('recommendationKey')
        yahoo_data['recommendation_key'] = recommendations
        
        # Detailed ratings breakdown
        num_analysts = info.get('numberOfAnalystOpinions', 0)
        yahoo_data['num_analysts'] = num_analysts
        
        # Rating distribution (if available)
        yahoo_data['analyst_ratings']['strong_buy'] = info.get('recommendationMean', 0)  # 1.0 = Strong Buy, 5.0 = Strong Sell
        
        # ✅ 5. PREVIOUS QUARTER DATA (trailing)
        financials = stock.quarterly_financials
        
        if not financials.empty and len(financials.columns) > 0:
            # Ostatni kwartał (most recent)
            latest_quarter = financials.columns[0]
            
            try:
                total_revenue = financials.loc['Total Revenue', latest_quarter] if 'Total Revenue' in financials.index else None
                net_income = financials.loc['Net Income', latest_quarter] if 'Net Income' in financials.index else None
                
                yahoo_data['previous_quarter'] = {
                    'date': str(latest_quarter.date()) if hasattr(latest_quarter, 'date') else str(latest_quarter),
                    'revenue': float(total_revenue) if total_revenue is not None else None,
                    'net_income': float(net_income) if net_income is not None else None,
                }
            except Exception as e:
                print(f"   → Błąd parsowania financials: {e}")
        
        # ✅ 6. EARNINGS DATES
        earnings_dates = stock.get_earnings_dates(limit=2)
        if earnings_dates is not None and not earnings_dates.empty:
            # Najbliższa data earnings
            next_earnings = earnings_dates.index[0]
            yahoo_data['next_earnings_date'] = str(next_earnings.date()) if hasattr(next_earnings, 'date') else str(next_earnings)
        
        # ✅ 7. FORMATOWANIE DLA GROQ (czytelny string)
        formatted_data = format_yahoo_data_for_display(yahoo_data)
        
        print(f"   ✓ Yahoo Finance data retrieved for {ticker}")
        print(f"      • Current price: ${yahoo_data['current_price']}")
        print(f"      • Target price: ${yahoo_data['target_price']}")
        print(f"      • Analysts: {yahoo_data['num_analysts']}")
        
        return {'raw': yahoo_data, 'formatted': formatted_data}
        
    except ImportError:
        print(f"   ✗ yfinance not installed - Yahoo Finance unavailable")
        print(f"   → Bot will use standard market reactions without real-time data")
        return {}
    except Exception as e:
        print(f"   ✗ Błąd Yahoo Finance dla {ticker}: {e}")
        print(f"   → Bot will use standard market reactions without real-time data")
        return {}

def format_yahoo_data_for_display(data: Dict) -> str:
    """Formatuje dane Yahoo Finance do czytelnego stringa dla Groq"""
    
    lines = ["=== YAHOO FINANCE DATA ===\n"]
    
    # Current trading data
    if data.get('current_price'):
        lines.append(f"Current Price: ${data['current_price']:.2f}")
    
    if data.get('market_cap'):
        market_cap_b = data['market_cap'] / 1e9
        lines.append(f"Market Cap: ${market_cap_b:.2f}B")
    
    # Valuation metrics
    if data.get('pe_ratio'):
        lines.append(f"P/E Ratio: {data['pe_ratio']:.2f}")
    
    if data.get('forward_pe'):
        lines.append(f"Forward P/E: {data['forward_pe']:.2f}")
    
    # 52-week range
    if data.get('52week_high') and data.get('52week_low'):
        lines.append(f"52-Week Range: ${data['52week_low']:.2f} - ${data['52week_high']:.2f}")
    
    lines.append("")  # Empty line
    
    # Analyst expectations
    lines.append("--- ANALYST CONSENSUS ---")
    
    if data.get('consensus_eps'):
        lines.append(f"Expected EPS (forward): ${data['consensus_eps']:.2f}")
    
    if data.get('num_analysts'):
        lines.append(f"Number of Analysts: {data['num_analysts']}")
    
    # Price targets
    if data.get('target_price'):
        lines.append(f"Target Price (mean): ${data['target_price']:.2f}")
        
        if data.get('current_price'):
            upside = ((data['target_price'] - data['current_price']) / data['current_price']) * 100
            lines.append(f"Implied Upside: {upside:+.1f}%")
    
    if data.get('target_high') and data.get('target_low'):
        lines.append(f"Target Range: ${data['target_low']:.2f} - ${data['target_high']:.2f}")
    
    # Previous quarter
    if data.get('previous_quarter') and data['previous_quarter'].get('revenue'):
        lines.append("")
        lines.append("--- PREVIOUS QUARTER ---")
        prev_q = data['previous_quarter']
        lines.append(f"Date: {prev_q.get('date', 'N/A')}")
        
        if prev_q.get('revenue'):
            revenue_m = prev_q['revenue'] / 1e6
            lines.append(f"Revenue: ${revenue_m:.2f}M")
        
        if prev_q.get('net_income'):
            income_m = prev_q['net_income'] / 1e6
            lines.append(f"Net Income: ${income_m:.2f}M")
    
    # Next earnings date
    if data.get('next_earnings_date'):
        lines.append("")
        lines.append(f"Next Earnings Date: {data['next_earnings_date']}")
    
    return "\n".join(lines)

# ============================================
# ✅ EKSTRAKCJA KLUCZOWYCH SEKCJI Z 8-K
# ============================================

def extract_key_sections(document_text: str, detected_items: List[Dict]) -> str:
    """
    Wyciąga najważniejsze sekcje z dokumentu 8-K:
    - Items (2.02, 1.01, etc.)
    - Tabele z liczbami
    - Kluczowe fragmenty z guidance/outlook
    """
    doc_lower = document_text.lower()
    sections = []
    
    # 1. Wyciągnij sekcje Items
    for item in detected_items:
        item_code = item['code']
        item_marker = f"item {item_code}"
        
        if item_marker in doc_lower:
            start_idx = doc_lower.find(item_marker)
            # Weź 3000 znaków od tego miejsca
            section = document_text[start_idx:start_idx+3000]
            sections.append(f"\n=== ITEM {item_code}: {item['description']} ===\n{section}")
    
    # 2. Szukaj tabel finansowych (GAAP, Non-GAAP, Revenue, EPS)
    financial_keywords = [
        'revenue', 'net income', 'earnings per share', 'eps', 'gaap', 'non-gaap',
        'operating income', 'gross profit', 'guidance', 'outlook', 'forecast'
    ]
    
    for keyword in financial_keywords:
        if keyword in doc_lower:
            idx = doc_lower.find(keyword)
            # Weź kontekst wokół słowa kluczowego
            start = max(0, idx - 500)
            end = min(len(document_text), idx + 1500)
            snippet = document_text[start:end]
            sections.append(f"\n=== FRAGMENT: {keyword.upper()} ===\n{snippet}")
    
    # 3. Wyciągnij liczby (revenue, EPS, margins)
    numbers_section = extract_financial_numbers(document_text)
    if numbers_section:
        sections.append(f"\n=== KLUCZOWE LICZBY ===\n{numbers_section}")
    
    # Połącz wszystkie sekcje i ogranicz do 12000 znaków
    combined = "\n".join(sections)
    
    if len(combined) > 12000:
        combined = combined[:12000]
    
    return combined if combined else document_text[:12000]

def extract_financial_numbers(text: str) -> str:
    """Wyciąga kluczowe liczby finansowe z dokumentu"""
    lines = text.split('\n')
    relevant_lines = []
    
    # Szukaj linii z liczbami i kluczowymi słowami
    patterns = [
        r'\$[\d,]+\.?\d*\s*(million|billion|thousand)?',
        r'(revenue|earnings|eps|income|profit|margin).*\$?[\d,]+\.?\d*',
        r'[\d,]+\.?\d*%',
        r'(q[1-4]|quarter|fy|fiscal year).*[\d,]+',
    ]
    
    for line in lines:
        line_lower = line.lower()
        if any(re.search(pattern, line_lower) for pattern in patterns):
            if any(kw in line_lower for kw in ['revenue', 'eps', 'income', 'guidance', 'outlook', 'margin']):
                relevant_lines.append(line.strip())
    
    return "\n".join(relevant_lines[:30])  # Max 30 linii

# ============================================
# ✅ HELPER: GENERUJ PYTANIA DLA KAŻDEGO ITEM
# ============================================

def generate_item_specific_questions(sorted_items: List[Dict]) -> str:
    """Generuje pytania specyficzne dla każdego wykrytego Item"""
    questions_list = []
    
    for item in sorted_items:
        item_code = item['code']
        item_config = ITEM_PROMPTS.get(item_code)
        
        if item_config:
            questions_list.append(f"### ITEM {item_code} - {item['description']}:\n{item_config['questions']}")
        else:
            questions_list.append(f"### ITEM {item_code} - {item['description']}:\n- What happened?\n- Why is it material?\n- Impact on business")
    
    return "\n".join(questions_list)

# ============================================
# ✅ GROQ AI INTEGRATION - MULTI-ITEM ANALYSIS
# ============================================

def analyze_with_groq(document_text: str, ticker: str, company: str, yahoo_data: str, detected_items: List[Dict]) -> Dict:
    """Analizuje dokument 8-K używając Groq AI - MULTIPLE ITEMS + COMBINED VERDICT"""
    
    if not GROQ_API_KEY:
        print("   → Brak GROQ_API_KEY - pomijam analizę AI")
        return None
    
    if not detected_items:
        print("   → Brak wykrytych Items - pomijam Groq")
        return None
    
    try:
        # ✅ SORTUJ ITEMS PO IMPACT (najważniejsze pierwsze)
        sorted_items = sorted(detected_items, key=lambda x: x['impact'], reverse=True)
        
        print(f"   → Wykryto {len(sorted_items)} Items do analizy:")
        for item in sorted_items:
            print(f"      • Item {item['code']}: {item['description']} (Impact: {item['impact']}/10)")
        
        # ✅ PRZYGOTUJ SEKCJE DOKUMENTU
        key_sections = extract_key_sections(document_text, detected_items)
        print(f"   → Długość fragmentu: {len(key_sections)} znaków")
        
        # ✅ ZBUDUJ MULTI-ITEM ANALYSIS PROMPT
        items_description = "\n".join([
            f"- Item {item['code']}: {item['description']} (Impact: {item['impact']}/10)"
            for item in sorted_items
        ])
        
        # ✅ Generuj pytania dla każdego Item
        analysis_questions = generate_item_specific_questions(sorted_items)
        
        # ✅ GŁÓWNY PROMPT - MULTI-ITEM ANALYSIS + ANTI-HALLUCINATION
        full_prompt = f"""Jesteś ekspertem analizy finansowej SEC z 20-letnim doświadczeniem. Analizujesz filing 8-K który zawiera WIELE równoczesnych wydarzeń.

🚨 CRITICAL ANTI-HALLUCINATION RULES (MUST FOLLOW):

1. ✅ Use ONLY numbers that appear LITERALLY in the 8-K document below
2. ❌ If "consensus", "analyst estimates", or "street expectations" are NOT in the document → Write "Not available in 8-K document"
3. ❌ If deal value says "undisclosed", "not disclosed", or "to be determined" → Write "Undisclosed" - DO NOT estimate or guess
4. ✅ Mark ALL price predictions as "ESTIMATED based on typical market reactions"
5. ✅ When citing numbers, verify they exist in DOCUMENT TEXT below
6. ❌ DO NOT invent premiums, multiples, or valuations if not explicitly stated
7. ✅ If you're uncertain about ANY number → Say "Not explicitly stated in document"

EXAMPLES:
✅ CORRECT: "Revenue: $35.082B (stated in document)"
❌ WRONG: "Revenue: $35.1B vs $33.2B consensus" (if consensus NOT in document)
✅ CORRECT: "Deal value: Undisclosed"
❌ WRONG: "Deal value: Estimated $500M" (if document says "undisclosed")

═══════════════════════════════════════════════════════════════

SPÓŁKA: {company} (Ticker: {ticker})

WYKRYTE ITEMS (od najważniejszego):
{items_description}

KONTEKST RYNKOWY:
{yahoo_data if yahoo_data else "⚠️ BRAK DANYCH YAHOO FINANCE - Używaj standardowych reakcji rynku na tego typu Items"}

KLUCZOWE SEKCJE DOKUMENTU:
{key_sections}

---

## CZĘŚĆ 1: ANALIZA KAŻDEGO ITEM OSOBNO

{analysis_questions}

---

## CZĘŚĆ 2: COMBINED VERDICT (NAJWAŻNIEJSZE!)

Teraz oceń ŁĄCZNY WPŁYW wszystkich Items na cenę akcji:

**OVERALL VERDICT:** [STRONG BULLISH / BULLISH / MIXED / BEARISH / STRONG BEARISH]

**FINALNE KIERUNEK CENY:** [BULLISH / BEARISH / NEUTRALNY]
*WAŻNE: Uwzględnij WSZYSTKIE Items i ich interakcje. Np. dobre earnings mogą być zniwelowane przez odejście CEO lub restatement.*

**POTENCJALNY RUCH AKCJI:**
- Pre-market/After-hours: [+/-X% do +/-Y%]
- 1-3 dni: [+/-X% do +/-Y%]
- 1-2 tygodnie: [+/-X% do +/-Y%]

{"**⚠️ UWAGA:** Brak danych Yahoo Finance - prognozy oparte na typowych reakcjach rynku dla tego typu Items" if not yahoo_data else ""}

**DOMINUJĄCY CZYNNIK:**
[Który Item ma NAJWIĘKSZY wpływ na cenę? Dlaczego?]

**INTERAKCJE MIĘDZY ITEMS:**
[Jak te wydarzenia wpływają na siebie nawzajem? Czy się wzmacniają czy neutralizują?]

{ITEM_INTERACTION_EXAMPLES}

**GŁÓWNE RYZYKA:**
1. [Największe zagrożenie wynikające z tych Items]
2. [Drugie zagrożenie]
3. [Trzecie zagrożenie]

**MARKET PSYCHOLOGY:**
[Jak rynek zinterpretuje tę KOMBINACJĘ wydarzeń? Co będzie górą - fear czy greed?]

**CONFIDENCE LEVEL:** [1-10]
*Uwaga: Niższy confidence jeśli Items są sprzeczne (np. beat + CEO departure){"lub jeśli brak danych Yahoo Finance" if not yahoo_data else ""}*

---

## CZĘŚĆ 3: KONKRETNE LICZBY (jeśli dostępne)

**KLUCZOWE DANE Z DOKUMENTU:**
[Wyciągnij KONKRETNE liczby: revenue, EPS, guidance, ceny przejęć, koszty, etc.]
⚠️ ONLY numbers that are LITERALLY in the document text above!

**TON ZARZĄDU:**
[Optymistyczny/Neutralny/Ostrożny/Pesymistyczny - z cytatami jeśli są]

---

🚨 FINAL VERIFICATION BEFORE RESPONDING:
- Are ALL numbers I'm reporting actually in the document? YES/NO
- Did I mark predictions as "ESTIMATED"? YES/NO
- Did I avoid inventing consensus/estimates not in document? YES/NO

UŻYWAJ KONKRETNYCH LICZB Z DOKUMENTU. Bądź bezpośredni i praktyczny. Nie bój się jednoznacznych werdyktów.
{"Bez danych Yahoo Finance opieraj się na standardowych reakcjach rynku dla poszczególnych Items (np. earnings beat zwykle = +5-8%, CEO departure = -3-5%, etc.) i ZAWSZE oznaczaj to jako 'ESTIMATED'." if not yahoo_data else ""}

REMEMBER: Better to say "Not in document" than to invent numbers!
"""

        # ✅ Wywołaj Groq API
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "Jesteś ekspertem analizy SEC z 20-letnim doświadczeniem. Potrafisz ocenić jak KOMBINACJA różnych Items wpływa na cenę akcji. CRITICAL: Use ONLY numbers that appear literally in the document - never invent consensus, estimates, or deal values. If information is not in the document, say 'Not available in document'. Mark all predictions as 'ESTIMATED'. Twoje analizy są konkretne, używasz liczb z dokumentu i nie boisz się jednoznacznych werdyktów. Odpowiadasz w strukturalnym formacie."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 3072  # ✅ Zwiększony limit dla multiple items
        }
        
        print(f"   → Wysyłanie do Groq AI (multiple items analysis)...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            analysis_text = result['choices'][0]['message']['content']
            print(f"   ✓ Otrzymano multi-item analizę AI ({len(analysis_text)} znaków)")
            return {
                'analysis': analysis_text, 
                'items_analyzed': [item['code'] for item in sorted_items],
                'item_count': len(sorted_items),
                'raw_response': result
            }
        else:
            print("   → Groq nie zwrócił analizy")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"   ✗ Groq API HTTP error: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text[:500]}")
        return None
    except Exception as e:
        print(f"   ✗ Błąd Groq API: {e}")
        return None

# ============================================
# FUNKCJE SEC
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
# FUNKCJE DISCORD
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
    """KANAŁ #1 - Podstawowy alert"""
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
    
    if analysis['items']:
        items_list = []
        for item in analysis['items']:
            impact = item['impact']
            if impact >= 9:
                emoji = "🔴"
            elif impact >= 7:
                emoji = "🟠"
            elif impact >= 5:
                emoji = "🟡"
            else:
                emoji = "🟢"
            
            items_list.append(f"{emoji} Item {item['code']} - {item['description']} (Impact: {impact}/10)")
        items_text = "\n".join(items_list)
    else:
        items_text = "Brak wykrytych Items"
    
    keywords_text = ", ".join(analysis['keywords']) if analysis['keywords'] else "Brak"
    
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
            {"name": "Publikacja na SEC", "value": publication_time, "inline": False}
        ],
        "footer": {"text": f"SEC EDGAR Monitor v2.1 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✓ Alert sent to Channel #1: {ticker} - {date}")
    except Exception as e:
        print(f"✗ Error sending alert to Channel #1: {e}")

def send_ai_analysis_alert(filing: Dict, groq_analysis: Dict):
    """✅ KANAŁ #2 - Multi-Item AI Analysis"""
    if not DISCORD_WEBHOOK_AI:
        print("   → Brak DISCORD_WEBHOOK_AI - pomijam wysyłkę AI")
        return
    
    if not groq_analysis or 'analysis' not in groq_analysis:
        print("   → Brak analizy Groq - pomijam wysyłkę AI")
        return
    
    ticker = filing['ticker']
    company = filing['company']
    
    analysis_text = groq_analysis['analysis']
    items_analyzed = groq_analysis.get('items_analyzed', [])
    item_count = groq_analysis.get('item_count', 0)
    
    # ✅ Emoji based on item count
    if item_count >= 3:
        title_emoji = "🔥"  # Complex situation
    elif item_count == 2:
        title_emoji = "⚡"  # Dual event
    else:
        title_emoji = "🤖"  # Single item
    
    # ✅ Lista Items w title
    items_list = ", ".join([f"Item {code}" for code in items_analyzed])
    
    # Discord ma limit 2000 znaków na embed description
    if len(analysis_text) > 1800:
        description = analysis_text[:1800] + "..."
        remaining = analysis_text[1800:]
        
        # Split długich analiz na multiple fields
        fields = []
        while remaining and len(fields) < 5:  # Max 5 dodatkowych fields
            chunk = remaining[:1000]
            remaining = remaining[1000:]
            fields.append({
                "name": f"Kontynuacja analizy (część {len(fields) + 1})",
                "value": chunk,
                "inline": False
            })
    else:
        description = analysis_text
        fields = []
    
    # ✅ Dodaj info o Items na początku
    fields.insert(0, {
        "name": "📊 Analyzed Items",
        "value": items_list if items_list else "Brak Items",
        "inline": False
    })
    
    embed = {
        "title": f"{title_emoji} MULTI-ITEM ANALYSIS - {company} ({ticker})",
        "description": description,
        "color": 5814783,  # Purple dla multi-item
        "fields": fields,
        "footer": {
            "text": f"SEC AI Analyst v2.1 | Powered by Groq (Llama 3.3) | {item_count} Items analyzed | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_AI, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✓ Multi-Item AI Analysis sent to Channel #2: {ticker} ({item_count} items)")
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
                # KROK 1: Wyślij zwykły alert (kanał #1)
                send_discord_alert(filing, analysis)
                new_filings_count += 1
                
                # KROK 2: Pobierz dane Yahoo Finance
                yahoo_response = get_yahoo_finance_data(ticker)
                yahoo_formatted = yahoo_response.get('formatted', 'Brak danych Yahoo Finance') if yahoo_response else 'Brak danych Yahoo Finance'
                time.sleep(1)
                
                # KROK 3: Multi-Item AI Analysis z Groq
                if analysis.get('full_document'):
                    groq_analysis = analyze_with_groq(
                        analysis['full_document'],
                        ticker,
                        filing['company'],
                        yahoo_formatted,
                        analysis['items']  # ✅ Przekaż WSZYSTKIE wykryte Items
                    )
                    
                    # KROK 4: Wyślij AI analysis (kanał #2)
                    if groq_analysis:
                        send_ai_analysis_alert(filing, groq_analysis)
                        ai_analysis_count += 1
                        time.sleep(2)
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
    print("SEC 8-K Monitor v2.1 - MULTI-ITEM ANALYSIS + AI (Groq)")
    print("="*60)
    print(f"Companies monitored: {len(COMPANIES)}")
    print(f"Gist storage: {'✓ ENABLED' if GIST_TOKEN and GIST_ID else '✗ DISABLED'}")
    print(f"AI Analysis: {'✓ ENABLED (Groq Llama 3.3 - Multi-Item)' if GROQ_API_KEY else '✗ DISABLED'}")
    print("="*60)
    
    if not DISCORD_WEBHOOK_URL:
        print("\n⚠️  WARNING: DISCORD_WEBHOOK_URL not set!")
        return
    
    check_new_filings()
    print("\n✓ Monitor run completed\n")

if __name__ == "__main__":
    main()
