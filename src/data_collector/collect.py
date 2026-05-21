"""
CIT Data Collector - Layer 1 (public positioning) + Layer 2 (financials)
Takes a company name, returns structured JSON with both layers.
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CompanyProfile:
    name: str
    hq_location: str = ""
    sector: str = ""
    description: str = ""
    employees: str = ""
    founded: str = ""
    website: str = ""


@dataclass
class FinancialSnapshot:
    revenue: str = ""
    revenue_growth: str = ""
    funding_stage: str = ""  # for startups: seed/Series A/B etc.
    total_funding: str = ""
    valuation: str = ""
    key_metrics: list = None

    def __post_init__(self):
        if self.key_metrics is None:
            self.key_metrics = []


@dataclass
class PublicPositioning:
    tagline: str = ""
    target_audience: str = ""
    key_messages: list = None
    recent_press: list = None

    def __post_init__(self):
        if self.key_messages is None:
            self.key_messages = []
        if self.recent_press is None:
            self.recent_press = []


@dataclass
class ReframingGap:
    what_company_says: str = ""
    what_data_shows: str = ""
    interview_insight: str = ""


@dataclass
class CompanyReport:
    company: CompanyProfile
    financials: FinancialSnapshot
    positioning: PublicPositioning
    reframing: ReframingGap
    collected_at: str = ""
    data_sources: list = None

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat()


def build_rhenus_report() -> CompanyReport:
    """Reference implementation for Rhenus Group based on manual analysis."""
    return CompanyReport(
        company=CompanyProfile(
            name="Rhenus Group",
            hq_location="Holzwickede, near Dortmund, Germany",
            sector="Logistics / Supply Chain",
            description="Global logistics provider, mid-transformation into a 4PL platform",
            employees="40,000+",
            founded="1912",
            website="https://www.rhenus.com",
        ),
        financials=FinancialSnapshot(
            revenue="~EUR 7.5 billion (2023)",
            revenue_growth="~15-20% YoY (acquisition-driven)",
            key_metrics=[
                "Operates across 1000+ locations worldwide",
                "Growing warehousing and contract logistics faster than forwarding",
                "Acquisition spree: multiple targets per year in Europe, Asia, Americas",
            ],
        ),
        positioning=PublicPositioning(
            tagline="Reliable traditional logistics partner with 100+ years of history",
            target_audience="Enterprise logistics managers, B2B",
            key_messages=[
                "Family-owned, reliable, traditional",
                "Full-service logistics provider",
                "Global footprint from German roots",
            ],
            recent_press=[
                "Multiple 2023-2024 acquisitions in contract logistics",
                "Expanding 4PL and supply chain orchestration offerings",
            ],
        ),
        reframing=ReframingGap(
            what_company_says="We are a reliable, traditional logistics company with 100+ years of heritage, serving global clients with end-to-end solutions.",
            what_data_shows="Aggressive acquisition pattern (10+ in 2 years), heavy investment in 4PL platform capabilities, warehousing growing faster than forwarding. This is a company in mid-transformation, not a stable traditional operator.",
            interview_insight="Rhenus is actively reshaping itself from a traditional forwarder into a 4PL orchestrator. They're buying capability faster than they're building it. An interviewer would be impressed by someone who sees the acquisition strategy as a deliberate platform play, not random expansion.",
        ),
        data_sources=[
            "Manual analysis (Rhenus annual report, press releases, acquisition tracker)"
        ],
    )


def build_buynomics_report() -> CompanyReport:
    """Reference implementation for Buynomics based on manual analysis."""
    return CompanyReport(
        company=CompanyProfile(
            name="Buynomics",
            hq_location="Cologne, Germany",
            sector="Fintech / SaaS — Consumer Behavior Simulation",
            description="AI-powered consumer behavior simulation for CPG and retail",
            employees="~100-200 (fast growing)",
            founded="2018",
            website="https://www.buynomics.com",
        ),
        financials=FinancialSnapshot(
            funding_stage="Series B (raised EUR 30M in 2023)",
            total_funding="~EUR 45M+",
            revenue_growth="Strong (precise figure private, but headcount doubling annually)",
            key_metrics=[
                "Series B led by Eight Roads Ventures, with existing investors",
                "Expanding from Europe into North America",
                "Building AI that automates the analyst role itself",
            ],
        ),
        positioning=PublicPositioning(
            tagline="Consumer behavior simulation platform",
            target_audience="CPG companies, retailers, market research teams",
            key_messages=[
                "We help brands understand consumer decisions through simulation",
                "Replace expensive, slow market research with AI-powered predictions",
                "Data-driven pricing and assortment optimization",
            ],
            recent_press=[
                "EUR 30M Series B announced 2023",
                "North American expansion push",
                "Partnerships with major CPG brands",
            ],
        ),
        reframing=ReframingGap(
            what_company_says="We are a consumer behavior platform that helps brands simulate and understand purchasing decisions.",
            what_data_shows="Post-Series B growth phase, aggressively expanding into North America, building AI that directly replaces the traditional market analyst role. The company sells to analysts but its product automates their jobs. Critical inflection point: can they land enough enterprise clients before cash runway runs out?",
            interview_insight="Buynomics is at a classic post-Series B inflection: growth or bust. They're selling to the very people whose roles their product could make obsolete. An interviewer would be struck by someone who understands this tension — and can position themselves as the bridge between the old analyst world and the new simulation paradigm.",
        ),
        data_sources=[
            "Manual analysis (Buynomics pitch deck, Crunchbase, press, job postings analysis)"
        ],
    )


def collect_company(name: str) -> CompanyReport:
    """Main entry point: collects data for a company.
    For now returns reference data. Will connect to live data sources."""
    name_lower = name.lower()
    if "rhenus" in name_lower:
        return build_rhenus_report()
    elif "buynomics" in name_lower:
        return build_buynomics_report()
    else:
        raise ValueError(
            f"Unknown company: {name}. Reference data only for 'Rhenus' and 'Buynomics'."
        )


def main():
    parser = argparse.ArgumentParser(description="CIT Data Collector")
    parser.add_argument("company", help="Company name to analyze")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    report = collect_company(args.company)
    report_dict = asdict(report)

    indent = 2 if args.pretty else None
    output = json.dumps(report_dict, indent=indent, default=str)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
