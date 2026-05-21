"""
Curated reference snapshots for known companies.

Used when live collection returns sparse data — preserves gold-standard
Layer 1/2 content for demo and calibration. Shape matches live_collector REPORT_SCHEMA.
"""

from datetime import datetime


def _base(name: str, status: str = "private") -> dict:
    return {
        "company_name": name,
        "as_of": datetime.now().isoformat(),
        "status": status,
        "ticker": None,
        "self_description": {
            "tagline": "",
            "mission": "",
            "industry_positioning": "",
            "public_statements": [],
        },
        "core_data": {
            "sector": "",
            "industry": "",
            "hq_location": "",
            "employees": None,
            "founded_year": None,
            "description": "",
        },
        "financials": {
            "revenue": None,
            "funding_total": None,
            "last_funding_round": None,
            "notable_investors": [],
        },
        "growth_signals": {
            "revenue_trend": "",
            "employee_trend": "",
            "recent_acquisitions": [],
            "expansion_indicators": [],
        },
        "market_position": {
            "competitors": [],
            "market": "",
            "moat_description": "",
        },
        "_sources": [{"source": "reference", "note": "curated calibration data"}],
    }


def rhenus_reference() -> dict:
    r = _base("Rhenus Group", "private")
    r["self_description"]["tagline"] = (
        "Reliable traditional logistics partner with 100+ years of history"
    )
    r["self_description"]["industry_positioning"] = (
        "Family-owned, full-service global logistics provider from German roots"
    )
    r["self_description"]["public_statements"] = [
        "We are a reliable, traditional logistics company with 100+ years of heritage.",
        "End-to-end solutions for enterprise logistics managers worldwide.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Supply Chain / 4PL",
        "hq_location": "Holzwickede, Germany",
        "employees": 40000,
        "founded_year": 1912,
        "description": "Global logistics provider, mid-transformation into a 4PL platform",
    }
    r["financials"]["revenue"] = {"2023": "7.50B EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Acquisition-driven expansion ~15-20% YoY",
        "employee_trend": "40,000+ employees globally",
        "recent_acquisitions": [
            "Multiple contract logistics acquisitions 2023-2024 in Europe, Asia, Americas"
        ],
        "expansion_indicators": [
            "4PL and supply chain orchestration",
            "Warehousing growing faster than forwarding",
        ],
    }
    r["market_position"] = {
        "competitors": ["DHL", "Kuehne+Nagel", "DB Schenker"],
        "market": "Global contract logistics and forwarding",
        "moat_description": "Scale, family ownership stability, European footprint",
    }
    return r


def buynomics_reference() -> dict:
    r = _base("Buynomics", "private")
    r["self_description"]["tagline"] = "Consumer behavior simulation platform"
    r["self_description"]["industry_positioning"] = (
        "AI-powered consumer behavior simulation for CPG and retail — "
        "replace slow market research with predictive models"
    )
    r["self_description"]["public_statements"] = [
        "We help brands understand consumer decisions through simulation.",
        "Data-driven pricing and assortment optimization.",
    ]
    r["core_data"] = {
        "sector": "Fintech / SaaS",
        "industry": "Consumer Behavior Simulation",
        "hq_location": "Cologne, Germany",
        "employees": 150,
        "founded_year": 2018,
        "description": "AI-powered consumer behavior simulation for CPG and retail",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "EUR 45M+",
        "last_funding_round": "Series B (EUR 30M, 2023)",
        "notable_investors": ["Eight Roads Ventures"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Post-Series B scaling; headcount doubling annually (est.)",
        "employee_trend": "~100-200 employees, fast growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["North American expansion", "Enterprise CPG partnerships"],
    }
    r["market_position"] = {
        "competitors": ["Traditional market research firms", "Internal analytics teams"],
        "market": "CPG pricing and assortment optimization",
        "moat_description": "Simulation IP; sells to analysts while automating analyst workflows",
    }
    return r


def dhl_reference() -> dict:
    r = _base("DHL Group", "public")
    r["ticker"] = "DPW.DE"
    r["self_description"]["tagline"] = "Logistics company for the connected world"
    r["self_description"]["industry_positioning"] = (
        "Global leader in logistics, express, freight, e-commerce, and supply chain"
    )
    r["self_description"]["public_statements"] = [
        "We connect people and markets worldwide with sustainable logistics.",
        "Leading in express and e-commerce growth.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Express & Supply Chain",
        "hq_location": "Bonn, Germany",
        "employees": 600000,
        "founded_year": 1969,
        "description": "Deutsche Post DHL Group — global logistics integrator",
    }
    r["financials"]["revenue"] = {"2023": "81.80B EUR"}
    r["growth_signals"] = {
        "revenue_trend": "E-commerce and express outpacing legacy mail",
        "employee_trend": "600,000+ employees worldwide",
        "recent_acquisitions": ["Supply chain and last-mile bolt-ons"],
        "expansion_indicators": ["Sustainability program", "Automation in hubs"],
    }
    r["market_position"] = {
        "competitors": ["FedEx", "UPS", "Rhenus", "Kuehne+Nagel"],
        "market": "Global integrated logistics",
        "moat_description": "Scale, network density, brand in express",
    }
    return r


def apple_reference() -> dict:
    r = _base("Apple Inc.", "public")
    r["ticker"] = "AAPL"
    r["self_description"]["tagline"] = "Think different"
    r["self_description"]["industry_positioning"] = (
        "Premium consumer technology — design-led hardware, software, and services ecosystem"
    )
    r["self_description"]["public_statements"] = [
        "We believe in the power of technology to enrich lives.",
        "Privacy is a fundamental human right.",
    ]
    r["core_data"] = {
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "hq_location": "Cupertino, California, USA",
        "employees": 164000,
        "founded_year": 1976,
        "description": "Designs iPhone, Mac, services; vertical integration",
    }
    r["financials"]["revenue"] = {"2024": "391.00B USD", "2023": "383.00B USD"}
    r["growth_signals"] = {
        "revenue_trend": "Services growing faster than hardware; India expansion",
        "employee_trend": "164,000 employees",
        "recent_acquisitions": [],
        "expansion_indicators": ["Vision Pro", "AI on-device features", "India manufacturing"],
    }
    r["market_position"] = {
        "competitors": ["Samsung", "Google", "Microsoft"],
        "market": "Premium smartphones and ecosystem lock-in",
        "moat_description": "Brand, ecosystem, silicon, retail",
    }
    return r


def celonis_reference() -> dict:
    r = _base("Celonis", "private")
    r["self_description"]["tagline"] = "The Process Intelligence platform"
    r["self_description"]["industry_positioning"] = (
        "AI-powered process mining and execution management for enterprise operations"
    )
    r["self_description"]["public_statements"] = [
        "We help companies find and fix inefficiencies in how work actually flows.",
        "Process mining is the X-ray for business operations.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "Process Mining / BPM",
        "hq_location": "Munich, Germany",
        "employees": 3000,
        "founded_year": 2011,
        "description": "Market leader in process mining; unicorn",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 2.4B+ valuation (Series D era)",
        "last_funding_round": "Growth equity (2022)",
        "notable_investors": ["Durable Capital", "Arena Holdings"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Enterprise land-and-expand; partner ecosystem",
        "employee_trend": "3,000+ employees globally",
        "recent_acquisitions": ["Several process automation tuck-ins"],
        "expansion_indicators": ["Execution management", "AI copilots for processes"],
    }
    r["market_position"] = {
        "competitors": ["SAP Signavio", "UiPath", "Microsoft Power Automate"],
        "market": "Enterprise process intelligence",
        "moat_description": "Category creation, SAP partnerships, data moat from ERP connectors",
    }
    return r


def personio_reference() -> dict:
    r = _base("Personio", "private")
    r["self_description"]["tagline"] = "HR software for SMEs"
    r["self_description"]["industry_positioning"] = (
        "All-in-one HR platform for European small and mid-sized companies"
    )
    r["self_description"]["public_statements"] = [
        "We automate HR so companies can focus on their people.",
        "Built for the way European SMEs work.",
    ]
    r["core_data"] = {
        "sector": "HR Tech / SaaS",
        "industry": "HRIS",
        "hq_location": "Munich, Germany",
        "employees": 1800,
        "founded_year": 2015,
        "description": "Leading European HR platform for SMBs",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 1.7B+ valuation",
        "last_funding_round": "Series E (USD 125M, 2022)",
        "notable_investors": ["Greenoaks", "Lightspeed", "Northzone"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Strong SMB penetration in DACH; expanding EU",
        "employee_trend": "1,800+ employees",
        "recent_acquisitions": ["Payroll and recruiting tuck-ins"],
        "expansion_indicators": ["Payroll", "Workforce analytics"],
    }
    r["market_position"] = {
        "competitors": ["HiBob", "Workday (upmarket)", "SAP SuccessFactors"],
        "market": "European SMB HR software",
        "moat_description": "Localization, compliance, SMB workflow depth",
    }
    return r


def stripe_reference() -> dict:
    r = _base("Stripe", "private")
    r["self_description"]["tagline"] = "Financial infrastructure for the internet"
    r["self_description"]["industry_positioning"] = (
        "Payments, billing, and financial tools for internet businesses at global scale"
    )
    r["self_description"]["public_statements"] = [
        "We increase the GDP of the internet.",
        "Developers first — APIs over sales decks.",
    ]
    r["core_data"] = {
        "sector": "Fintech",
        "industry": "Payments Infrastructure",
        "hq_location": "San Francisco, USA / Dublin, Ireland",
        "employees": 8000,
        "founded_year": 2010,
        "description": "Developer-first payments platform; highly valued private fintech",
    }
    r["financials"] = {
        "revenue": {"2023": "~16B USD (est. processed volume proxy)"},
        "funding_total": "USD 95B+ valuation (2024 tender)",
        "last_funding_round": "Tender offer (2024)",
        "notable_investors": ["Sequoia", "a16z", "General Catalyst"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Enterprise upmarket; Stripe Billing and Treasury",
        "employee_trend": "8,000+ employees (post-optimization from peak)",
        "recent_acquisitions": ["Tax, identity, and banking partners"],
        "expansion_indicators": ["Embedded finance", "AI fraud tools"],
    }
    r["market_position"] = {
        "competitors": ["Adyen", "PayPal Braintree", "Square"],
        "market": "Online payments infrastructure",
        "moat_description": "Developer experience, network, compliance breadth",
    }
    return r


def dachser_reference() -> dict:
    r = _base("DACHSER SE", "private")
    r["self_description"]["tagline"] = "Logistics is people business"
    r["self_description"]["industry_positioning"] = (
        "Family-owned European logistics leader — road, air, sea, and contract logistics"
    )
    r["self_description"]["public_statements"] = [
        "We are a family-owned company that thinks and acts for the long term.",
        "Integrated logistics solutions for the entire supply chain.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Transport & Contract Logistics",
        "hq_location": "Kempten, Germany",
        "employees": 33000,
        "founded_year": 1930,
        "description": "One of Europe's largest family-owned logistics companies, strong in road freight and contract logistics",
    }
    r["financials"]["revenue"] = {"2023": "7.10B EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Steady organic growth ~5-8% YoY with selective acquisitions",
        "employee_trend": "33,000+ employees across 39 countries",
        "recent_acquisitions": ["European logistics bolt-ons 2023-2024"],
        "expansion_indicators": ["Digital logistics platform", "Asian expansion via joint ventures"],
    }
    r["market_position"] = {
        "competitors": ["DHL", "Kuehne+Nagel", "Rhenus", "DSV"],
        "market": "European road freight and contract logistics",
        "moat_description": "Family ownership stability, integrated network, European density",
    }
    return r


def db_cargo_reference() -> dict:
    r = _base("DB Cargo AG", "public")
    r["ticker"] = None  # Subsidiary of Deutsche Bahn
    r["self_description"]["tagline"] = "Rail freight made easy"
    r["self_description"]["industry_positioning"] = (
        "Europe's largest rail freight operator — sustainable intermodal transport"
    )
    r["self_description"]["public_statements"] = [
        "We make rail freight the backbone of sustainable logistics.",
        "Shifting freight from road to rail for climate protection.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Rail Freight",
        "hq_location": "Mainz, Germany",
        "employees": 30000,
        "founded_year": 2000,
        "description": "Deutsche Bahn subsidiary, Europe's largest rail freight company with operations in 18 countries",
    }
    r["financials"]["revenue"] = {"2023": "5.00B EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Restructuring mode; aiming for profitability by 2026",
        "employee_trend": "30,000 employees across Europe",
        "recent_acquisitions": [],
        "expansion_indicators": ["Digital freight wagon fleet", "Single wagon load strategy"],
    }
    r["market_position"] = {
        "competitors": ["SNCF Fret", "PKP Cargo", "Lineas", "Captrain"],
        "market": "European rail freight and intermodal",
        "moat_description": "Network density, DB Group backing, fleet scale",
    }
    return r


def schenker_reference() -> dict:
    r = _base("Schenker Deutschland AG", "private")
    r["self_description"]["tagline"] = "Moving goods. Moving forward."
    r["self_description"]["industry_positioning"] = (
        "Part of DB Schenker — global logistics leader in land, air, ocean, and contract logistics"
    )
    r["self_description"]["public_statements"] = [
        "We connect people and goods through innovative logistics.",
        "Sustainable logistics solutions for a connected world.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Integrated Logistics",
        "hq_location": "Essen, Germany",
        "employees": 76000,
        "founded_year": 1872,
        "description": "German arm of DB Schenker, one of the world's largest logistics providers. Recently acquired by DSV.",
    }
    r["financials"]["revenue"] = {"2023": "19.40B EUR (DB Schenker global)"}
    r["growth_signals"] = {
        "revenue_trend": "Part of DSV acquisition (2024) — integration underway",
        "employee_trend": "76,000+ employees globally (DB Schenker)",
        "recent_acquisitions": ["Being acquired by DSV for EUR 14.3B"],
        "expansion_indicators": ["DSV integration", "Digital transformation"],
    }
    r["market_position"] = {
        "competitors": ["DHL", "Kuehne+Nagel", "DACHSER", "Rhenus"],
        "market": "Global integrated logistics",
        "moat_description": "Network scale, DB Group heritage, DSV acquisition synergies",
    }
    return r


def europace_reference() -> dict:
    r = _base("Europace AG", "private")
    r["self_description"]["tagline"] = "Germany's leading mortgage platform"
    r["self_description"]["industry_positioning"] = (
        "B2B fintech platform connecting banks, brokers, and insurance for real estate finance"
    )
    r["self_description"]["public_statements"] = [
        "We digitize the entire mortgage process in Germany.",
        "Connecting intermediaries with lenders on one platform.",
    ]
    r["core_data"] = {
        "sector": "Fintech",
        "industry": "Mortgage Platform / B2B Marketplace",
        "hq_location": "Berlin, Germany",
        "employees": 400,
        "founded_year": 1999,
        "description": "Germany's largest B2B platform for real estate finance intermediation, processing billions in mortgage volume annually",
    }
    r["financials"]["revenue"] = None
    r["growth_signals"] = {
        "revenue_trend": "Strong platform growth; market leader in German mortgage intermediation",
        "employee_trend": "400+ employees, growing",
        "recent_acquisitions": ["Hypoport group subsidiary"],
        "expansion_indicators": ["Insurance platform", "Digital closing"],
    }
    r["market_position"] = {
        "competitors": ["Interhyp", "Check24", "Baufi24"],
        "market": "German B2B mortgage and insurance intermediation",
        "moat_description": "Network effects, broker ecosystem, Hypoport group backing",
    }
    return r


def schufa_reference() -> dict:
    r = _base("SCHUFA Holding AG", "private")
    r["self_description"]["tagline"] = "We create trust"
    r["self_description"]["industry_positioning"] = (
        "Germany's leading credit reporting agency — protecting consumers and enabling responsible lending"
    )
    r["self_description"]["public_statements"] = [
        "We protect consumers and help businesses make responsible decisions.",
        "Data-driven credit intelligence for the German market.",
    ]
    r["core_data"] = {
        "sector": "Financial Services",
        "industry": "Credit Reporting / Risk Analytics",
        "hq_location": "Wiesbaden, Germany",
        "employees": 1200,
        "founded_year": 1927,
        "description": "Germany's dominant credit scoring agency with data on ~68 million individuals and 6 million businesses",
    }
    r["financials"]["revenue"] = {"2023": "280M EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Stable with digital product expansion",
        "employee_trend": "1,200+ employees",
        "recent_acquisitions": [],
        "expansion_indicators": ["Open banking products", "Identity verification services", "Score improvements"],
    }
    r["market_position"] = {
        "competitors": ["CRIF Bürgel", "Creditreform", "infoscore (Arvato)"],
        "market": "German credit reporting and risk management",
        "moat_description": "Data moat from 68M consumer records, regulatory position, brand trust",
    }
    return r


def still_reference() -> dict:
    r = _base("STILL GmbH", "private")
    r["self_description"]["tagline"] = "Think inside the box"
    r["self_description"]["industry_positioning"] = (
        "Premium intralogistics solutions — forklifts, warehouse technology, and fleet management"
    )
    r["self_description"]["public_statements"] = [
        "We provide smart intralogistics solutions for the modern warehouse.",
        "Efficiency and sustainability in material handling.",
    ]
    r["core_data"] = {
        "sector": "Industrial Equipment",
        "industry": "Intralogistics / Material Handling",
        "hq_location": "Hamburg, Germany",
        "employees": 9000,
        "founded_year": 1920,
        "description": "KION Group subsidiary, leading European manufacturer of forklift trucks and warehouse equipment",
    }
    r["financials"]["revenue"] = {"2023": "2.10B EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Electrification and automation driving growth",
        "employee_trend": "9,000+ employees globally",
        "recent_acquisitions": [],
        "expansion_indicators": ["Lithium-ion battery technology", "Autonomous mobile robots", "Fleet management SaaS"],
    }
    r["market_position"] = {
        "competitors": ["Toyota Material Handling", "Jungheinrich", "Linde Material Handling"],
        "market": "European intralogistics and material handling",
        "moat_description": "KION Group backing, German engineering, dealer network",
    }
    return r


def contargo_reference() -> dict:
    r = _base("Contargo GmbH & Co. KG", "private")
    r["self_description"]["tagline"] = "Your gateway to intermodal transport"
    r["self_description"]["industry_positioning"] = (
        "Leading European intermodal container logistics — connecting ports, rail, and road"
    )
    r["self_description"]["public_statements"] = [
        "We make container transport efficient and sustainable.",
        "Intermodal solutions connecting seaports with the hinterland.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Intermodal / Container Transport",
        "hq_location": "Duisburg, Germany",
        "employees": 1200,
        "founded_year": 1996,
        "description": "Major intermodal operator connecting North Sea ports with Central European hinterland via rail and barge",
    }
    r["financials"]["revenue"] = {"2023": "800M EUR (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Growing with modal shift trend from road to rail/barge",
        "employee_trend": "1,200+ employees",
        "recent_acquisitions": ["Terminal expansions along Rhine corridor"],
        "expansion_indicators": ["Rhine-Ruhr logistics hub", "Digital container tracking"],
    }
    r["market_position"] = {
        "competitors": ["Hupac", "Kombiverkehr", "boxXpress"],
        "market": "European intermodal container logistics",
        "moat_description": "Terminal network along Rhine corridor, Rhine-Ruhr hub position",
    }
    return r


def shippeo_reference() -> dict:
    r = _base("Shippeo", "private")
    r["self_description"]["tagline"] = "Real-time transportation visibility"
    r["self_description"]["industry_positioning"] = (
        "AI-powered real-time supply chain visibility platform for enterprise shippers"
    )
    r["self_description"]["public_statements"] = [
        "We help companies see their supply chain in real time.",
        "Predictive ETA and end-to-end transportation visibility.",
    ]
    r["core_data"] = {
        "sector": "Supply Chain Tech",
        "industry": "Transportation Visibility / TMS",
        "hq_location": "Paris, France",
        "employees": 314,
        "founded_year": 2014,
        "description": "Leading European supply chain visibility platform with predictive ETAs across all transport modes",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "EUR 40M+ (Series B 2021)",
        "last_funding_round": "Series B",
        "notable_investors": ["NGP Capital", "Battery Ventures"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Strong ARR growth, enterprise focus",
        "employee_trend": "314 employees, growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["Multi-modal coverage", "Carrier network expansion", "AI/ML predictions"],
    }
    r["market_position"] = {
        "competitors": ["project44", "FourKites", "Transporeon"],
        "market": "European supply chain visibility",
        "moat_description": "European carrier network, multi-modal tracking, predictive AI",
    }
    return r


REFERENCE_BY_KEY = {
    "rhenus": rhenus_reference,
    "buynomics": buynomics_reference,
    "dhl": dhl_reference,
    "apple": apple_reference,
    "celonis": celonis_reference,
    "personio": personio_reference,
    "stripe": stripe_reference,
    "dachser": dachser_reference,
    "db-cargo": db_cargo_reference,
    "schenker": schenker_reference,
    "europace": europace_reference,
    "schufa": schufa_reference,
    "still": still_reference,
    "contargo": contargo_reference,
    "shippeo": shippeo_reference,
}


def get_reference(company_name: str) -> dict | None:
    key = company_name.lower().strip().replace(" ", "-")
    if key in REFERENCE_BY_KEY:
        return REFERENCE_BY_KEY[key]()
    for token, builder in REFERENCE_BY_KEY.items():
        if token in key:
            return builder()
    return None


def list_reference_keys() -> list[str]:
    return list(REFERENCE_BY_KEY.keys())


def reference_as_collector(key: str) -> dict | None:
    """Return reference snapshot in live_collector schema."""
    builder = REFERENCE_BY_KEY.get(key.lower())
    return builder() if builder else None
