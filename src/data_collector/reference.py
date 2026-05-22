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


def kuehne_nagel_reference() -> dict:
    r = _base("Kuehne+Nagel", "public")
    r["ticker"] = "KNIN.SW"
    r["self_description"]["tagline"] = "Global logistics with a human touch"
    r["self_description"]["industry_positioning"] = (
        "World's largest sea freight forwarder — integrated logistics across sea, air, road, and contract logistics"
    )
    r["self_description"]["public_statements"] = [
        "We move goods and deliver value for our customers worldwide.",
        "Leading in seafreight with digital supply chain solutions.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Freight Forwarding / 3PL",
        "hq_location": "Schindellegi, Switzerland",
        "employees": 80000,
        "founded_year": 1890,
        "description": "World's largest sea freight forwarder and one of the top integrated logistics providers globally",
    }
    r["financials"]["revenue"] = {"2023": "23.80B CHF"}
    r["growth_signals"] = {
        "revenue_trend": "Cyclical freight market with long-term volume growth",
        "employee_trend": "~80,000 employees across 100+ countries",
        "recent_acquisitions": ["City Zone Express (Asia road logistics)", "Multiple niche forwarders"],
        "expansion_indicators": ["Digital control towers", "Green logistics solutions", "Pharma logistics"],
    }
    r["market_position"] = {
        "competitors": ["DHL", "DSV", "DB Schenker", "Rhenus"],
        "market": "Global freight forwarding and contract logistics",
        "moat_description": "Scale in sea freight, digital platform, global network density",
    }
    return r


def dsv_reference() -> dict:
    r = _base("DSV", "public")
    r["ticker"] = "DSV.CO"
    r["self_description"]["tagline"] = "Global transport and logistics"
    r["self_description"]["industry_positioning"] = (
        "Danish global transport and logistics giant — road, sea, air, and solutions via disciplined M&A"
    )
    r["self_description"]["public_statements"] = [
        "We create value for our customers through efficient and sustainable supply chains.",
        "The best people, the best technology, the best network.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Freight Forwarding / 3PL",
        "hq_location": "Hvidovre, Denmark",
        "employees": 75000,
        "founded_year": 1976,
        "description": "Third-largest global freight forwarder, built through aggressive M&A (Panalpina, GIL, UTi)",
    }
    r["financials"]["revenue"] = {"2023": "15.40B EUR"}
    r["growth_signals"] = {
        "revenue_trend": "M&A-driven growth; recent DB Schenker acquisition (EUR 14.3B, 2024)",
        "employee_trend": "75,000+ employees (growing via integration)",
        "recent_acquisitions": ["DB Schenker (2024, EUR 14.3B)", "Global Integrated Logistics (2019)"],
        "expansion_indicators": ["Digital logistics platform", "Cross-selling post-acquisition", "Air freight expansion"],
    }
    r["market_position"] = {
        "competitors": ["DHL", "Kuehne+Nagel", "DB Schenker"],
        "market": "Global freight forwarding and contract logistics",
        "moat_description": "M&A integration engine, scale, post-Schenker network density",
    }
    return r


def fedex_reference() -> dict:
    r = _base("FedEx", "public")
    r["ticker"] = "FDX"
    r["self_description"]["tagline"] = "The world on time"
    r["self_description"]["industry_positioning"] = (
        "Global express transportation and logistics — air freight, ground delivery, freight forwarding"
    )
    r["self_description"]["public_statements"] = [
        "We connect people and possibilities through our global network.",
        "The world's most intelligent logistics network.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Express / Freight",
        "hq_location": "Memphis, Tennessee, USA",
        "employees": 350000,
        "founded_year": 1971,
        "description": "Global logistics giant with integrated air-ground network; massive US domestic parcel share",
    }
    r["financials"]["revenue"] = {"2024": "87.70B USD", "2023": "90.20B USD"}
    r["growth_signals"] = {
        "revenue_trend": "Post-pandemic normalization; cost restructuring underway (DRIVE program)",
        "employee_trend": "~350,000 employees (post-restructuring)",
        "recent_acquisitions": [],
        "expansion_indicators": ["FedEx Ground economy", "Automation in hubs", "Express network optimization"],
    }
    r["market_position"] = {
        "competitors": ["UPS", "DHL", "Amazon Logistics", "USPS"],
        "market": "Global express and US domestic parcel delivery",
        "moat_description": "Integrated air-ground network, brand, scale density in US domestic",
    }
    return r


def ups_reference() -> dict:
    r = _base("UPS", "public")
    r["ticker"] = "UPS"
    r["self_description"]["tagline"] = "Moving our world forward by delivering what matters"
    r["self_description"]["industry_positioning"] = (
        "World's largest package delivery company — logistics, supply chain, and freight"
    )
    r["self_description"]["public_statements"] = [
        "We deliver packages and values that shape our world.",
        "Best service, best people, best innovation in logistics.",
    ]
    r["core_data"] = {
        "sector": "Logistics",
        "industry": "Parcel / Supply Chain",
        "hq_location": "Atlanta, Georgia, USA",
        "employees": 500000,
        "founded_year": 1907,
        "description": "World's largest package delivery company; unionized workforce, massive US ground network",
    }
    r["financials"]["revenue"] = {"2024": "91.10B USD", "2023": "94.60B USD"}
    r["growth_signals"] = {
        "revenue_trend": "Post-pandemic normalization; healthcare and SMB focus",
        "employee_trend": "~500,000 employees (union workforce)",
        "recent_acquisitions": [],
        "expansion_indicators": ["Healthcare logistics", "UPS SurePost redesign", "Automation in sorting"],
    }
    r["market_position"] = {
        "competitors": ["FedEx", "DHL", "Amazon Logistics", "USPS"],
        "market": "Global parcel and US domestic delivery",
        "moat_description": "Unionized workforce stability, network density, brand in B2B parcel",
    }
    return r


def mongodb_reference() -> dict:
    r = _base("MongoDB", "public")
    r["ticker"] = "MDB"
    r["self_description"]["tagline"] = "Build the way you want"
    r["self_description"]["industry_positioning"] = (
        "Leading modern document database platform — developer data platform for transactional, search, and analytical workloads"
    )
    r["self_description"]["public_statements"] = [
        "We empower developers to build the next generation of applications.",
        "The most popular document database in the world.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "Database / Data Platform",
        "hq_location": "New York City, USA",
        "employees": 5100,
        "founded_year": 2007,
        "description": "Publicly traded developer data platform; known for MongoDB Atlas cloud database",
    }
    r["financials"]["revenue"] = {"2025": "2.40B USD (est.)", "2024": "1.68B USD"}
    r["growth_signals"] = {
        "revenue_trend": "Atlas cloud revenue growing 30%+ YoY; land-and-expand model",
        "employee_trend": "5,100+ employees, growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["Atlas cloud (60%+ of revenue)", "Search and vector capabilities", "Industry-specific solutions"],
    }
    r["market_position"] = {
        "competitors": ["AWS DynamoDB", "Google Firestore", "Couchbase", "PostgreSQL ecosystem"],
        "market": "Document databases and developer data platforms",
        "moat_description": "Developer mindshare, document data model, Atlas cloud stickiness",
    }
    return r


def snowflake_reference() -> dict:
    r = _base("Snowflake", "public")
    r["ticker"] = "SNOW"
    r["self_description"]["tagline"] = "Let's solve the world's data problems"
    r["self_description"]["industry_positioning"] = (
        "AI Data Cloud platform — unified storage, analytics, and AI/ML workloads on a single cross-cloud platform"
    )
    r["self_description"]["public_statements"] = [
        "We make data simple, accessible, and valuable for every organization.",
        "The world's data is moving to the Data Cloud.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "Cloud Data Platform / AI",
        "hq_location": "Bozeman, Montana, USA",
        "employees": 7200,
        "founded_year": 2012,
        "description": "Cloud-native data platform; massive IPO (2020); AI/ML workload expansion",
    }
    r["financials"]["revenue"] = {"2025": "3.70B USD (est.)", "2024": "2.81B USD"}
    r["growth_signals"] = {
        "revenue_trend": "Product revenue growing >30% YoY; consumption-based model",
        "employee_trend": "~7,200 employees",
        "recent_acquisitions": ["Neeva (AI search, 2023)", "Streamlit (data apps, 2022)"],
        "expansion_indicators": ["Snowpark ML", "Cortex AI", "Cross-cloud data sharing", "Unistore (transactional)"],
    }
    r["market_position"] = {
        "competitors": ["Databricks", "Amazon Redshift", "Google BigQuery", "Microsoft Fabric"],
        "market": "Cloud data warehousing and AI data platforms",
        "moat_description": "Cross-cloud architecture, data sharing network effects, semi-structured data handling",
    }
    return r


def datadog_reference() -> dict:
    r = _base("Datadog", "public")
    r["ticker"] = "DDOG"
    r["self_description"]["tagline"] = "Cloud monitoring as one"
    r["self_description"]["industry_positioning"] = (
        "Observability and security platform for cloud applications — infrastructure, APM, logs, and SIEM"
    )
    r["self_description"]["public_statements"] = [
        "We help organizations see inside any stack, any app, at any scale.",
        "The standard for cloud monitoring and security.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "Observability / DevOps",
        "hq_location": "New York City, USA",
        "employees": 6500,
        "founded_year": 2010,
        "description": "Leading observability platform; Land-and-expand model with 23+ product categories",
    }
    r["financials"]["revenue"] = {"2024": "2.60B USD", "2023": "2.10B USD"}
    r["growth_signals"] = {
        "revenue_trend": ">25% YoY revenue growth; platform land-and-expand",
        "employee_trend": "~6,500 employees, growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["Cloud SIEM", "Database monitoring", "LLM observability", "Log management"],
    }
    r["market_position"] = {
        "competitors": ["New Relic", "Dynatrace", "Splunk", "Grafana Labs"],
        "market": "Cloud observability and security monitoring",
        "moat_description": "Platform breadth (23+ products), single agent, land-and-expand go-to-market",
    }
    return r


def cloudflare_reference() -> dict:
    r = _base("Cloudflare", "public")
    r["ticker"] = "NET"
    r["self_description"]["tagline"] = "Help build a better Internet"
    r["self_description"]["industry_positioning"] = (
        "Cloud connectivity platform — content delivery, security, zero-trust, and edge computing"
    )
    r["self_description"]["public_statements"] = [
        "We make the Internet faster, safer, and more reliable for everyone.",
        "The global network that powers the next generation of applications.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "CDN / Security / Edge Computing",
        "hq_location": "San Francisco, California, USA",
        "employees": 3900,
        "founded_year": 2009,
        "description": "Cloud connectivity platform running 20%+ of web traffic; expanding into zero-trust and developer platform",
    }
    r["financials"]["revenue"] = {"2025": "2.00B USD (est.)", "2024": "1.60B USD"}
    r["growth_signals"] = {
        "revenue_trend": ">25% YoY revenue growth; large enterprise land-and-expand",
        "employee_trend": "~3,900 employees",
        "recent_acquisitions": [],
        "expansion_indicators": [
            "Cloudflare Workers (edge compute)",
            "Zero-Trust network access",
            "R2 object storage",
            "AI inference at edge",
            "Global network across 310+ cities in 120+ countries across North America, Europe, Asia, and Middle East",
        ],
    }
    r["market_position"] = {
        "competitors": ["Akamai", "Fastly", "Amazon CloudFront", "Zscaler"],
        "market": "Global CDN, security, and edge computing across 310+ cities worldwide",
        "moat_description": "Global network scale (310+ cities across NA, EU, Asia, ME), developer platform, integrated security suite",
    }
    return r


def sap_reference() -> dict:
    r = _base("SAP", "public")
    r["ticker"] = "SAP"
    r["self_description"]["tagline"] = "The best-run businesses run SAP"
    r["self_description"]["industry_positioning"] = (
        "World's largest enterprise application software company — ERP, cloud, AI, and business technology platform"
    )
    r["self_description"]["public_statements"] = [
        "We help the world run better and improve people's lives.",
        "The leading enterprise technology platform for intelligent, sustainable businesses.",
    ]
    r["core_data"] = {
        "sector": "Enterprise Software",
        "industry": "ERP / Business Software",
        "hq_location": "Walldorf, Germany",
        "employees": 105000,
        "founded_year": 1972,
        "description": "European software giant; dominant in ERP with massive SAP S/4HANA cloud transition underway",
    }
    r["financials"]["revenue"] = {"2024": "34.20B EUR", "2023": "31.20B EUR"}
    r["growth_signals"] = {
        "revenue_trend": "Cloud revenue growing >20% YoY; S/4HANA migration driving multi-year transition",
        "employee_trend": "105,000+ employees globally",
        "recent_acquisitions": ["WalkMe (digital adoption, 2024)", "LeanIX (enterprise architecture, 2023)"],
        "expansion_indicators": ["Business AI (Joule)", "SAP Business Technology Platform", "Industry cloud", "Sustainability management"],
    }
    r["market_position"] = {
        "competitors": ["Oracle", "Workday", "Microsoft Dynamics", "Salesforce"],
        "market": "Global enterprise application software",
        "moat_description": "Massive ERP installed base (400K+ customers), switching costs, S/4HANA ecosystem",
    }
    return r


def figma_reference() -> dict:
    r = _base("Figma", "private")
    r["self_description"]["tagline"] = "The collaborative interface design tool"
    r["self_description"]["industry_positioning"] = (
        "Web-first collaborative design platform — UI/UX, prototyping, design systems, and whiteboarding"
    )
    r["self_description"]["public_statements"] = [
        "We make design accessible to everyone, not just designers.",
        "Nothing great is made alone — design together in real time.",
    ]
    r["core_data"] = {
        "sector": "Design Software",
        "industry": "Collaborative Design / UI/UX",
        "hq_location": "San Francisco, California, USA",
        "employees": 2000,
        "founded_year": 2012,
        "description": "Category-defining collaborative design platform; blocked Adobe acquisition ($20B); growing into dev tools",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 12B+ valuation (2024 secondary)",
        "last_funding_round": "Secondary (2024)",
        "notable_investors": ["a16z", "Index Ventures", "Greylock", "Sequoia"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Strong ARR growth; enterprise land-and-expand from design to product/engineering",
        "employee_trend": "~2,000 employees, growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["Figma Dev Mode", "FigJam (whiteboarding)", "AI design features", "Enterprise SSO/permissions"],
    }
    r["market_position"] = {
        "competitors": ["Sketch", "Adobe XD", "Canva", "Miro (adjacent)"],
        "market": "Collaborative design and prototyping",
        "moat_description": "Real-time collaboration, plugin ecosystem, browser-native; network effects via design systems",
    }
    return r


def canva_reference() -> dict:
    r = _base("Canva", "private")
    r["self_description"]["tagline"] = "Empowering everyone to design"
    r["self_description"]["industry_positioning"] = (
        "World's leading online visual communication platform — democratizing design through templates and AI"
    )
    r["self_description"]["public_statements"] = [
        "We give everyone the power to design anything.",
        "Making design simple for everyone, everywhere.",
    ]
    r["core_data"] = {
        "sector": "Design Software",
        "industry": "Visual Communication / Design Platform",
        "hq_location": "Sydney, Australia",
        "employees": 4500,
        "founded_year": 2013,
        "description": "Design platform for non-designers; massive user base (190M+ monthly active); growing into enterprise",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 40B+ valuation (2024)",
        "last_funding_round": "Secondary (2024)",
        "notable_investors": ["Bond", "General Catalyst", "Sequoia", "Felicis"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Strong organic growth; Canva Enterprise and Visual Suite expanding TAM",
        "employee_trend": "~4,500 employees, growing",
        "recent_acquisitions": ["Krikey (AI video, 2024)", "Pixlr (photo editor, 2024)", "Affinity (creative suite, 2024)"],
        "expansion_indicators": ["AI design (Magic Studio)", "Enterprise features", "Printed products", "Video and docs"],
    }
    r["market_position"] = {
        "competitors": ["Adobe", "Figma", "Microsoft Designer"],
        "market": "Visual communication and online design",
        "moat_description": "190M+ MAU, template library, freemium-to-enterprise flywheel, AI integrations",
    }
    return r


def flix_reference() -> dict:
    r = _base("Flix", "private")
    r["self_description"]["tagline"] = "Travel. Together."
    r["self_description"]["industry_positioning"] = (
        "Global mobility platform — FlixBus and FlixTrain connecting cities via asset-light intercity travel"
    )
    r["self_description"]["public_statements"] = [
        "We make sustainable and affordable travel accessible to everyone.",
        "The leading green travel technology platform in Europe and beyond.",
    ]
    r["core_data"] = {
        "sector": "Mobility",
        "industry": "Intercity Bus / Rail / Travel Tech",
        "hq_location": "Munich, Germany",
        "employees": 1500,
        "founded_year": 2013,
        "description": "Asset-light intercity mobility platform (FlixBus, FlixTrain); expanded to Americas, Asia via FlixMobility",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 3B+ valuation (2022)",
        "last_funding_round": "Series I (2022)",
        "notable_investors": ["KKR", "General Atlantic", "TPG"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Post-COVID demand recovery and international expansion",
        "employee_trend": "~1,500 employees (plus partner drivers)",
        "recent_acquisitions": ["Greyhound Lines (2021)", "Kamil Koc (Turkey, 2021)"],
        "expansion_indicators": ["US market (FlixBus USA)", "Latin America expansion", "FlixTrain in Europe", "Dynamic pricing"],
    }
    r["market_position"] = {
        "competitors": ["BlaBlaCar", "National Express", "DB Fernverkehr (trains)"],
        "market": "European intercity bus and budget train travel",
        "moat_description": "Asset-light model, density in DACH, brand as green travel alternative, technology platform",
    }
    return r


def trade_republic_reference() -> dict:
    r = _base("Trade Republic", "private")
    r["self_description"]["tagline"] = "The brokerage for Europe"
    r["self_description"]["industry_positioning"] = (
        "Neobroker platform — zero-commission stock, ETF, crypto trading and savings plans for retail investors"
    )
    r["self_description"]["public_statements"] = [
        "We make investing accessible to everyone in Europe.",
        "Save and invest from your smartphone — simple, low-cost, and secure.",
    ]
    r["core_data"] = {
        "sector": "Fintech",
        "industry": "Brokerage / Investing",
        "hq_location": "Berlin, Germany",
        "employees": 600,
        "founded_year": 2015,
        "description": "Europe's largest neobroker; 4M+ users; known for zero-commission trades and 4% interest on cash",
    }
    r["financials"] = {
        "revenue": None,
        "funding_total": "USD 5B+ valuation (2023)",
        "last_funding_round": "Series C (2023)",
        "notable_investors": ["Accel", "Sequoia", "Founders Fund", "Peter Thiel"],
    }
    r["growth_signals"] = {
        "revenue_trend": "Strong user growth (4M+); monetization via payment-for-order-flow and interest margin",
        "employee_trend": "~600 employees, growing",
        "recent_acquisitions": [],
        "expansion_indicators": ["Crypto trading", "Interest on cash (4%)", "European expansion", "New asset classes"],
    }
    r["market_position"] = {
        "competitors": ["Scalable Capital", "eToro", "Robinhood", "ING/DKB"],
        "market": "European retail brokerage and investing",
        "moat_description": "User base (4M+), BaFin license, zero-commission model, savings plan market leader",
    }
    return r


def mckinsey_reference() -> dict:
    r = _base("McKinsey & Company", "private")
    r["self_description"]["tagline"] = "The world's leading management consulting firm"
    r["self_description"]["industry_positioning"] = (
        "Prestigious strategy and management consulting — serving top executives at Fortune 500, governments, and institutions"
    )
    r["self_description"]["public_statements"] = [
        "We help organizations create change that matters.",
        "The trusted advisor to the world's leading businesses and institutions.",
    ]
    r["core_data"] = {
        "sector": "Consulting",
        "industry": "Management Consulting / Strategy",
        "hq_location": "New York City, USA",
        "employees": 45000,
        "founded_year": 1926,
        "description": "Most prestigious management consulting firm; MBB; known for exit opportunities, network, and alumni",
    }
    r["financials"]["revenue"] = {"2024": "16.50B USD (est.)", "2023": "15.80B USD (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Steady growth driven by digital, sustainability, and AI practices",
        "employee_trend": "~45,000 employees (partners, consultants, and staff)",
        "recent_acquisitions": [],
        "expansion_indicators": ["McKinsey Digital", "Sustainability practice", "AI/Quantum Black", "Implementation arm"],
    }
    r["market_position"] = {
        "competitors": ["BCG", "Bain", "Deloitte S&O", "Strategy&"],
        "market": "Global strategy and management consulting",
        "moat_description": "Brand prestige, C-suite access, alumni network, scale of knowledge assets",
    }
    return r


def bcg_reference() -> dict:
    r = _base("Boston Consulting Group", "private")
    r["self_description"]["tagline"] = "Transforming business for a better world"
    r["self_description"]["industry_positioning"] = (
        "Top-tier strategy consulting — growth, corporate finance, digital, and AI for global enterprises"
    )
    r["self_description"]["public_statements"] = [
        "We help clients achieve total societal and business impact.",
        "Pioneers in business strategy since 1963 — growth-share matrix and beyond.",
    ]
    r["core_data"] = {
        "sector": "Consulting",
        "industry": "Management Consulting / Strategy",
        "hq_location": "Boston, Massachusetts, USA",
        "employees": 32000,
        "founded_year": 1963,
        "description": "MBB strategy consulting firm; known for BCG Matrix, thought leadership, and strong corporate culture",
    }
    r["financials"]["revenue"] = {"2024": "12.50B USD (est.)", "2023": "12.00B USD (est.)"}
    r["growth_signals"] = {
        "revenue_trend": "Strong growth in digital, AI, and sustainability consulting",
        "employee_trend": "~32,000 employees (including BCG X and Platinion)",
        "recent_acquisitions": [],
        "expansion_indicators": ["BCG X (formerly BCG Digital Ventures)", "BCG Platinion (tech implementation)", "AI/GenAI practice", "Climate & sustainability"],
    }
    r["market_position"] = {
        "competitors": ["McKinsey", "Bain", "Deloitte S&O", "Strategy&"],
        "market": "Global strategy and management consulting",
        "moat_description": "Brand prestige, proprietary frameworks (BCG Matrix), thought leadership, alumni network",
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
    "kuehne-nagel": kuehne_nagel_reference,
    "dsv": dsv_reference,
    "fedex": fedex_reference,
    "ups": ups_reference,
    "mongodb": mongodb_reference,
    "snowflake": snowflake_reference,
    "datadog": datadog_reference,
    "cloudflare": cloudflare_reference,
    "sap": sap_reference,
    "figma": figma_reference,
    "canva": canva_reference,
    "flix": flix_reference,
    "trade-republic": trade_republic_reference,
    "mckinsey": mckinsey_reference,
    "bcg": bcg_reference,
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
