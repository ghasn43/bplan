"""Outline suggestion engine + ready-to-use business plan templates.

Detects the business type from the project setup and offers professionally
structured outlines (sections + topics + guidance) the user can apply in one
click. No external AI is used — the structure is curated and rule-matched.
"""
from __future__ import annotations

from ..models import BusinessPlanProject
from ..models.text_plan import TextPlanSection, TextPlanTopic
from ..storage.base import StorageBackend


# --------------------------------------------------------------------------
# template authoring helpers
# --------------------------------------------------------------------------
def _t(title, guidance="", topic_type="paragraph", sample=""):
    return {"title": title, "topic_type": topic_type, "guidance_text": guidance, "sample_html": sample}


def _s(title, section_type, description, guidance, topics):
    return {"title": title, "section_type": section_type, "description": description,
            "guidance_text": guidance, "topics": topics}


G = {
    "business_concept": "Summarise what the business does, who it serves, and why it exists in two or three sentences.",
    "market_opportunity": "Describe the target market, the customer pain point, the size of the opportunity, and why the timing is right. Include evidence where available.",
    "revenue_model": "Explain how the business earns revenue. Link the narrative to the revenue streams defined in the financial model.",
    "funding_requirement": "State how much funding is required, how it will be used, and how it supports growth. The amount should reconcile with the financing assumptions.",
    "financial_highlights": "Summarise projected revenue, profitability, and cash position. Keep it to the headline figures from the financial study.",
    "competitive_advantage": "Explain what makes the business defensible: technology, cost, brand, exclusivity, network effects, or know-how.",
    "risks": "List the main commercial, operational, financial, and regulatory risks and the mitigation for each.",
    "team": "Introduce the founders and key team members, their relevant experience, and the hiring plan.",
    "operations": "Describe the day-to-day operating workflow, facilities, systems, and suppliers.",
}


# --------------------------------------------------------------------------
# templates
# --------------------------------------------------------------------------
def build_template_general():
    return _s_list([
        _s("Executive Summary", "executive_summary", "A one-page summary of the entire plan.",
           "Write this last. It must stand alone and hook the reader.",
           [_t("Business concept", G["business_concept"]), _t("Market opportunity", G["market_opportunity"]),
            _t("Products and services"), _t("Revenue model", G["revenue_model"]),
            _t("Financial highlights", G["financial_highlights"]), _t("Funding requirement", G["funding_requirement"]),
            _t("Key success factors")]),
        _s("Company Overview", "company_overview", "Who the company is and how it is structured.", "",
           [_t("Company background"), _t("Legal structure"), _t("Location"),
            _t("Mission and vision"), _t("Strategic objectives")]),
        _s("Products and Services", "products_services", "What the company sells and why it matters.", "",
           [_t("Product/service description"), _t("Customer problem"), _t("Value proposition"),
            _t("Competitive advantage", G["competitive_advantage"]), _t("Development roadmap")]),
        _s("Market Analysis", "market_analysis", "The market, customers, and competition.", "",
           [_t("Target market", G["market_opportunity"]), _t("Customer segments"), _t("Market size"),
            _t("Industry trends"), _t("Competitive landscape"), _t("Market entry strategy")]),
        _s("Business Model", "business_model", "How the business creates and captures value.", "",
           [_t("Revenue streams", G["revenue_model"]), _t("Pricing model"), _t("Customer acquisition model"),
            _t("Sales channels"), _t("Partnership model")]),
        _s("Operations Plan", "operations_plan", "How the business runs day to day.", "",
           [_t("Operating workflow", G["operations"]), _t("Suppliers"), _t("Facilities"),
            _t("Technology systems"), _t("Quality control"), _t("Regulatory requirements")]),
        _s("Marketing and Sales Plan", "marketing_sales", "How the business attracts and keeps customers.", "",
           [_t("Brand positioning"), _t("Marketing channels"), _t("Sales process"),
            _t("Customer retention"), _t("Growth strategy")]),
        _s("Management and Staffing", "management_team", "The people behind the plan.", "",
           [_t("Management structure", G["team"]), _t("Key roles"), _t("Hiring plan"), _t("Advisors and partners")]),
        _s("Financial Plan", "financial_plan", "The financial study narrative.",
           "Link this narrative to the income statement, balance sheet, and cash flow generated by the app.",
           [_t("Projection basis"), _t("Revenue assumptions", G["revenue_model"]), _t("Cost assumptions"),
            _t("Profitability outlook"), _t("Cash flow outlook"), _t("Balance sheet outlook"), _t("Scenario analysis")]),
        _s("Funding Requirement", "funding_request", "What is needed and how it is used.", "",
           [_t("Required funding", G["funding_requirement"]), _t("Use of funds"),
            _t("Proposed funding structure"), _t("Repayment or investor return plan")]),
        _s("Risk Analysis", "risk_analysis", "What could go wrong and how it is managed.", "",
           [_t("Commercial risks", G["risks"]), _t("Operational risks"), _t("Financial risks"),
            _t("Regulatory risks"), _t("Mitigation strategies")]),
        _s("Implementation Plan", "implementation_plan", "From plan to execution.", "",
           [_t("Milestones"), _t("Timeline"), _t("Critical path"), _t("Management priorities")]),
        _s("Appendices", "appendix", "Supporting detail and the financial study.",
           "The financial statements, charts and detailed assumptions are appended automatically by the report generator.",
           [_t("Detailed assumptions"), _t("Financial statements"), _t("Charts"), _t("Supporting documents")]),
    ])


def build_template_saas():
    return _s_list([
        _s("Executive Summary", "executive_summary", "One-page summary.", "",
           [_t("Business concept", G["business_concept"]), _t("Market opportunity", G["market_opportunity"]),
            _t("Subscription revenue model", G["revenue_model"]), _t("Funding requirement", G["funding_requirement"])]),
        _s("Product and Platform Overview", "products_services", "What the platform does.", "",
           [_t("Platform overview"), _t("Core features"), _t("Product roadmap")]),
        _s("Problem and Solution", "products_services", "The job-to-be-done.", "",
           [_t("Customer problem"), _t("Our solution"), _t("Why now")]),
        _s("Market and Customer Segments", "market_analysis", "Who buys and why.", "",
           [_t("Target segments"), _t("Market size"), _t("Competitive landscape")]),
        _s("Subscription Revenue Model", "business_model", "Recurring revenue economics.", "",
           [_t("Pricing tiers", G["revenue_model"]), _t("Unit economics (CAC, LTV)"), _t("Expansion revenue")]),
        _s("Technology Architecture", "operations_plan", "How it is built and scaled.", "",
           [_t("Architecture overview"), _t("Security and compliance"), _t("Scalability")]),
        _s("Go-to-Market Strategy", "marketing_sales", "How customers are reached.", "",
           [_t("Acquisition channels"), _t("Sales motion"), _t("Partnerships")]),
        _s("Customer Acquisition and Retention", "marketing_sales", "Growth and churn.", "",
           [_t("Acquisition funnel"), _t("Onboarding"), _t("Retention and churn")]),
        _s("Team and Development Roadmap", "management_team", "People and delivery.", "",
           [_t("Team", G["team"]), _t("Hiring plan"), _t("Engineering roadmap")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Cost structure"), _t("Profitability and cash outlook")]),
        _s("Funding Requirement", "funding_request", "The ask.", "",
           [_t("Required funding", G["funding_requirement"]), _t("Use of funds")]),
        _s("Risks and Mitigation", "risk_analysis", "Key risks.", "",
           [_t("Risks and mitigation", G["risks"])]),
        _s("Appendices", "appendix", "Financial study and detail.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def build_template_trading():
    return _s_list([
        _s("Executive Summary", "executive_summary", "One-page summary.", "",
           [_t("Business concept", G["business_concept"]), _t("Market opportunity", G["market_opportunity"]),
            _t("Financial highlights", G["financial_highlights"]), _t("Funding requirement", G["funding_requirement"])]),
        _s("Company Overview", "company_overview", "The trading entity.", "",
           [_t("Company background"), _t("Legal structure"), _t("Location and licences")]),
        _s("Product Portfolio", "products_services", "What is traded.", "",
           [_t("Product categories"), _t("Brands and exclusivity"), _t("Margins by category")]),
        _s("Supplier and Import Strategy", "operations_plan", "Sourcing and import.", "",
           [_t("Key suppliers"), _t("Import logistics"), _t("Customs and duties")]),
        _s("Target Customers and Sales Channels", "marketing_sales", "Who buys.", "",
           [_t("Customer segments"), _t("Sales channels"), _t("Key accounts")]),
        _s("Logistics and Inventory Model", "operations_plan", "Moving and holding stock.", "",
           [_t("Warehousing"), _t("Inventory policy"), _t("Distribution")]),
        _s("Pricing and Margin Strategy", "business_model", "How margins are made.", "",
           [_t("Pricing strategy", G["revenue_model"]), _t("Margin management")]),
        _s("Working Capital Plan", "financial_plan", "Cash conversion cycle.", "",
           [_t("Receivables and payables"), _t("Inventory financing")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Cost assumptions"), _t("Profitability and cash outlook")]),
        _s("Funding Requirement", "funding_request", "The ask.", "",
           [_t("Required funding", G["funding_requirement"]), _t("Use of funds")]),
        _s("Risks and Mitigation", "risk_analysis", "Key risks.", "", [_t("Risks and mitigation", G["risks"])]),
        _s("Appendices", "appendix", "Financial study.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def build_template_manufacturing():
    return _s_list([
        _s("Executive Summary", "executive_summary", "One-page summary.", "",
           [_t("Business concept", G["business_concept"]), _t("Market opportunity", G["market_opportunity"]),
            _t("Financial highlights", G["financial_highlights"]), _t("Funding requirement", G["funding_requirement"])]),
        _s("Company Overview", "company_overview", "The manufacturer.", "",
           [_t("Company background"), _t("Legal structure"), _t("Location")]),
        _s("Product Description", "products_services", "What is made.", "",
           [_t("Product range"), _t("Specifications"), _t("Value proposition")]),
        _s("Production Process", "operations_plan", "How it is made.", "",
           [_t("Production workflow", G["operations"]), _t("Capacity"), _t("Lead times")]),
        _s("Raw Materials and Suppliers", "operations_plan", "Inputs.", "",
           [_t("Key raw materials"), _t("Suppliers"), _t("Procurement strategy")]),
        _s("Machinery and CapEx", "operations_plan", "Plant and equipment.", "",
           [_t("Machinery list"), _t("CapEx plan"), _t("Maintenance")]),
        _s("Quality Control", "operations_plan", "Standards.", "", [_t("QC process"), _t("Certifications")]),
        _s("Market and Distribution", "marketing_sales", "Selling output.", "",
           [_t("Target market", G["market_opportunity"]), _t("Distribution channels")]),
        _s("Cost Structure and Margins", "financial_plan", "Unit economics.", "",
           [_t("Cost of production"), _t("Gross margins")]),
        _s("Staffing and Operations", "management_team", "People.", "", [_t("Org structure", G["team"]), _t("Hiring plan")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Cost assumptions"), _t("Profitability and cash outlook")]),
        _s("Funding Requirement", "funding_request", "The ask.", "",
           [_t("Required funding", G["funding_requirement"]), _t("Use of funds")]),
        _s("Risk Analysis", "risk_analysis", "Key risks.", "", [_t("Risks and mitigation", G["risks"])]),
        _s("Appendices", "appendix", "Financial study.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def build_template_service():
    return _s_list([
        _s("Executive Summary", "executive_summary", "One-page summary.", "",
           [_t("Business concept", G["business_concept"]), _t("Market opportunity", G["market_opportunity"]),
            _t("Funding requirement", G["funding_requirement"])]),
        _s("Company Overview", "company_overview", "The firm.", "", [_t("Company background"), _t("Legal structure")]),
        _s("Service Offering", "products_services", "What is delivered.", "",
           [_t("Services"), _t("Value proposition"), _t("Service tiers")]),
        _s("Customer Segments", "market_analysis", "Who is served.", "",
           [_t("Target segments"), _t("Market size")]),
        _s("Delivery Model", "operations_plan", "How service is delivered.", "",
           [_t("Delivery workflow", G["operations"]), _t("Capacity and utilisation")]),
        _s("Pricing Strategy", "business_model", "How fees are set.", "", [_t("Pricing model", G["revenue_model"])]),
        _s("Marketing and Sales", "marketing_sales", "Winning work.", "",
           [_t("Marketing channels"), _t("Sales process")]),
        _s("Staffing Plan", "management_team", "People.", "", [_t("Team", G["team"]), _t("Hiring plan")]),
        _s("Operating Expenses", "financial_plan", "Running costs.", "", [_t("Cost assumptions")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Profitability and cash outlook")]),
        _s("Risks and Mitigation", "risk_analysis", "Key risks.", "", [_t("Risks and mitigation", G["risks"])]),
        _s("Appendices", "appendix", "Financial study.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def build_template_water_treatment(sample=False):
    def s(html):
        return html if sample else ""
    return _s_list([
        _s("Executive Summary", "executive_summary", "A one-page summary of the plan.",
           "Write this last; it must stand alone for investors and lenders.",
           [_t("Business concept", G["business_concept"],
               sample=s("<p>AquaPure Smart Filters FZE imports, assembles, installs and maintains smart water "
                        "filtration systems for residential and commercial customers in the UAE, backed by an "
                        "IoT water-quality monitoring subscription.</p>")),
            _t("Market opportunity", G["market_opportunity"],
               sample=s("<p>Rising concern over water quality, hard water damage to appliances, and sustainability "
                        "awareness are driving demand for point-of-use filtration across the Gulf.</p>")),
            _t("Revenue model", G["revenue_model"],
               sample=s("<p>Revenue is generated from system sales, installation fees, recurring filter "
                        "replacement, maintenance contracts, and monthly monitoring subscriptions.</p>")),
            _t("Financial highlights", G["financial_highlights"]),
            _t("Funding requirement", G["funding_requirement"])]),
        _s("Company Overview", "company_overview", "Who the company is.", "",
           [_t("Company background", sample=s("<p>Established as a UAE free-zone entity to combine imported "
                                              "filtration technology with local assembly and service.</p>")),
            _t("Legal structure and licensing"), _t("Mission and vision"), _t("Strategic objectives")]),
        _s("Environmental Problem and Market Need", "market_analysis", "Why this matters now.",
           "Quantify the water-quality problem and the regulatory/sustainability drivers.",
           [_t("Water quality challenges", G["market_opportunity"],
               sample=s("<p>Hard water and high total dissolved solids across the UAE damage household appliances, "
                        "affect taste, and drive heavy reliance on bottled water. Households and businesses are "
                        "actively seeking reliable point-of-use treatment.</p>")),
            _t("Regulatory drivers",
               sample=s("<p>National water-quality standards and sustainability targets encourage reduced bottled-water "
                        "consumption and safer drinking water at the point of use.</p>")),
            _t("Sustainability awareness"), _t("Market size and growth")]),
        _s("Products and Technology", "products_services", "What the company offers.", "",
           [_t("Filtration product range",
               sample=s("<p>The range spans residential under-sink smart filtration systems, whole-home solutions, and "
                        "commercial units, each paired with multi-stage cartridges.</p>"
                        "<ul><li>Residential smart filtration system</li><li>Whole-home treatment unit</li>"
                        "<li>Commercial / light-industrial system</li></ul>")),
            _t("Smart monitoring technology",
               sample=s("<p>An IoT module continuously monitors water quality and filter life, pushing alerts to the "
                        "customer app and scheduling proactive maintenance.</p>")),
            _t("Competitive advantage", G["competitive_advantage"]), _t("Product roadmap")]),
        _s("Customer Segments", "market_analysis", "Who buys.", "",
           [_t("Residential customers",
               sample=s("<p>Quality-conscious villa and apartment households seeking safe, great-tasting water and lower "
                        "bottled-water spending.</p>")),
            _t("Commercial customers"), _t("Channel partners")]),
        _s("Installation and Service Model", "operations_plan", "How systems are deployed.", "",
           [_t("Installation workflow", G["operations"],
               sample=s("<p>Certified technicians survey the site, install the system, commission the IoT module, and "
                        "onboard the customer to the monitoring app, typically within a single visit.</p>")),
            _t("Service team and coverage"), _t("Scheduling and SLAs")]),
        _s("Maintenance and Consumables Revenue", "business_model", "The recurring engine.", "",
           [_t("Filter replacement programme", G["revenue_model"],
               sample=s("<p>Replacement cartridges are sold on a scheduled cycle, creating predictable recurring revenue "
                        "and high customer lifetime value.</p>")),
            _t("Maintenance contracts"), _t("Monitoring subscriptions")]),
        _s("Supplier and Inventory Plan", "operations_plan", "Sourcing and stock.", "",
           [_t("Key suppliers"), _t("Import and logistics"), _t("Inventory policy")]),
        _s("Marketing and Sales Strategy", "marketing_sales", "Reaching customers.", "",
           [_t("Brand positioning",
               sample=s("<p>AquaPure is positioned as the trusted, technology-led water specialist combining premium "
                        "hardware with proactive service.</p>")),
            _t("Marketing channels"), _t("Sales process"), _t("Customer retention")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.",
           "Link this to the income statement, balance sheet and cash flow generated by the app.",
           [_t("Projection basis",
               sample=s("<p>The plan is modelled over five years on a monthly basis in AED, combining hardware sales, "
                        "installation, recurring consumables, maintenance and subscriptions.</p>")),
            _t("Revenue assumptions", G["revenue_model"]), _t("Cost assumptions"),
            _t("Profitability outlook"), _t("Cash flow outlook")]),
        _s("Funding Requirement", "funding_request", "What is needed.", "",
           [_t("Required funding", G["funding_requirement"],
               sample=s("<p>Funding is required to finance opening inventory, assembly tooling, working capital, and the "
                        "first phase of market development; the amount reconciles with the financing assumptions in the "
                        "financial model.</p>")),
            _t("Use of funds"), _t("Repayment / investor return")]),
        _s("Sustainability Impact", "custom", "Environmental contribution.",
           "Describe reductions in plastic bottle use, water waste, and energy, and any ESG alignment.",
           [_t("Environmental benefits",
               sample=s("<p>Each installed system displaces thousands of single-use plastic bottles per year and reduces "
                        "water waste through efficient multi-stage filtration.</p>")),
            _t("Plastic and waste reduction"), _t("ESG alignment")]),
        _s("Risk Analysis", "risk_analysis", "Key risks.", "",
           [_t("Commercial risks", G["risks"],
               sample=s("<p>Key risks include slower-than-planned customer adoption, price competition, and supplier "
                        "lead times; each is mitigated through recurring-revenue contracts, differentiated technology, "
                        "and buffer inventory.</p>")),
            _t("Operational risks"), _t("Regulatory risks"),
            _t("Mitigation strategies")]),
        _s("Implementation Plan", "implementation_plan", "Execution roadmap.", "",
           [_t("Milestones"), _t("Timeline"), _t("Management priorities")]),
        _s("Appendices", "appendix", "Supporting detail and the financial study.",
           "Financial statements and charts are appended automatically by the report generator.",
           [_t("Detailed assumptions"), _t("Financial statements"), _t("Charts")]),
    ])


def build_template_bank_financing():
    return _s_list([
        _s("Executive Summary", "executive_summary", "Summary for the lender.", "",
           [_t("Business concept", G["business_concept"]), _t("Loan purpose"),
            _t("Financial highlights", G["financial_highlights"])]),
        _s("Company Overview", "company_overview", "The borrower.", "",
           [_t("Company background"), _t("Ownership and management", G["team"])]),
        _s("Loan Purpose and Use of Funds", "funding_request", "Why the financing is needed.",
           "Be specific about the purpose and reconcile with the financing assumptions.",
           [_t("Loan purpose", G["funding_requirement"]), _t("Use of funds"), _t("Proposed structure")]),
        _s("Market and Business Model", "market_analysis", "Commercial context.", "",
           [_t("Market overview", G["market_opportunity"]), _t("Revenue model", G["revenue_model"])]),
        _s("Collateral and Security", "custom", "What secures the loan.",
           "Describe assets offered as collateral and their indicative value.",
           [_t("Collateral offered"), _t("Guarantees")]),
        _s("Debt Repayment Capacity", "financial_plan", "Ability to service debt.",
           "Show cash flow available for debt service and the coverage ratio.",
           [_t("Cash flow coverage"), _t("Debt service coverage ratio"), _t("Sensitivity")]),
        _s("Financial Plan", "financial_plan", "Financial narrative.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Cost assumptions"), _t("Cash flow outlook")]),
        _s("Risk Mitigation", "risk_analysis", "How risks are controlled.", "",
           [_t("Key risks", G["risks"]), _t("Mitigation and contingency")]),
        _s("Appendices", "appendix", "Financial study.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def build_template_investor_pitch():
    return _s_list([
        _s("Executive Summary", "executive_summary", "The hook.", "",
           [_t("Business concept", G["business_concept"]), _t("The ask", G["funding_requirement"])]),
        _s("Problem and Solution", "products_services", "Why you exist.", "",
           [_t("Customer problem"), _t("Our solution"), _t("Why now")]),
        _s("Market Opportunity", "market_analysis", "How big this can be.", "",
           [_t("Market size", G["market_opportunity"]), _t("Customer segments"), _t("Timing")]),
        _s("Product", "products_services", "What you've built.", "",
           [_t("Product overview"), _t("Traction"), _t("Roadmap")]),
        _s("Business Model", "business_model", "How you make money.", "",
           [_t("Revenue model", G["revenue_model"]), _t("Unit economics")]),
        _s("Competitive Advantage", "custom", "Why you win.", "",
           [_t("Competitive advantage", G["competitive_advantage"]), _t("Moat")]),
        _s("Go-to-Market", "marketing_sales", "How you scale.", "",
           [_t("Acquisition strategy"), _t("Scalability")]),
        _s("Team", "management_team", "Why you.", "", [_t("Founding team", G["team"]), _t("Advisors")]),
        _s("Financial Plan", "financial_plan", "The numbers.", "",
           [_t("Revenue assumptions", G["revenue_model"]), _t("Profitability and cash outlook")]),
        _s("The Ask and Exit Potential", "funding_request", "The deal.", "",
           [_t("Funding requirement", G["funding_requirement"]), _t("Use of funds"), _t("Investor return / exit potential")]),
        _s("Risks", "risk_analysis", "What could go wrong.", "", [_t("Risks and mitigation", G["risks"])]),
        _s("Appendices", "appendix", "Financial study.", "", [_t("Financial statements"), _t("Charts")]),
    ])


def _s_list(sections):
    return sections


TEMPLATES: dict[str, dict] = {
    "general": {"name": "General Business Plan", "build": build_template_general,
                "business_types": ["general"],
                "description": "A complete, all-purpose business plan structure suitable for most companies."},
    "saas": {"name": "SaaS / Software", "build": build_template_saas,
             "business_types": ["saas"],
             "description": "Subscription software plan focused on recurring revenue, product and go-to-market."},
    "trading": {"name": "Trading / Distribution", "build": build_template_trading,
                "business_types": ["trading"],
                "description": "Import, distribution and trading plan focused on sourcing, channels and working capital."},
    "manufacturing": {"name": "Manufacturing", "build": build_template_manufacturing,
                      "business_types": ["manufacturing"],
                      "description": "Production-led plan covering process, raw materials, CapEx and cost structure."},
    "service": {"name": "Service Business", "build": build_template_service,
                "business_types": ["service"],
                "description": "Service firm plan focused on delivery model, staffing and utilisation."},
    "water_treatment": {"name": "Water Treatment / Environmental", "build": build_template_water_treatment,
                        "business_types": ["water_treatment"],
                        "description": "Environmental / water treatment plan with installation, maintenance and sustainability."},
    "bank_financing": {"name": "Bank Financing Plan", "build": build_template_bank_financing,
                       "business_types": ["bank"],
                       "description": "Lender-focused plan emphasising loan purpose, collateral and repayment capacity."},
    "investor_pitch": {"name": "Investor Pitch Plan", "build": build_template_investor_pitch,
                       "business_types": ["investor"],
                       "description": "Investor-focused plan emphasising market, traction, team and the ask."},
}


# --------------------------------------------------------------------------
# detection
# --------------------------------------------------------------------------
def detect_business_type(project: BusinessPlanProject) -> str:
    setup = project.setup
    industry = (setup.industry or "").lower() if setup else ""
    model = (setup.business_model.value if setup and setup.business_model else "").lower()
    rt = {p.revenue_type.value.lower() for p in project.products if getattr(p, "revenue_type", None)}
    text = f"{industry} {model}"

    def has(*words):
        return any(w in text for w in words)

    if has("water", "filtration", "environment", "sustainab", "treatment", "waste"):
        return "water_treatment"
    if "subscription" in rt or has("saas", "software", "platform", "app", "tech startup"):
        return "saas"
    if has("import", "distribut", "trading", "wholesale", "reseller"):
        return "trading"
    if has("manufactur", "factory", "production", "assembly", "industrial", "materials"):
        return "manufacturing"
    if has("consult", "service", "agency", "professional", "advisory", "healthcare", "education"):
        return "service"
    return "general"


def _report_style(project: BusinessPlanProject) -> str | None:
    setup = project.setup
    if not setup:
        return None
    std = setup.reporting_standard.value.lower() if setup.reporting_standard else ""
    if "bank" in std or "ifrs for sme" in std:
        return "bank"
    if "investor" in std:
        return "investor"
    return None


def recommend_template_id(project: BusinessPlanProject) -> tuple[str, str]:
    """Return (template_id, detected_business_type)."""
    btype = detect_business_type(project)
    style = _report_style(project)
    # business-type match wins; otherwise fall back to report style.
    if btype != "general":
        return btype, btype
    if style == "bank":
        return "bank_financing", btype
    if style == "investor":
        return "investor_pitch", btype
    return "general", btype


# --------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------
def _template_info(template_id: str):
    from ..schemas.text_plan import OutlineTemplateInfo, TemplateSectionInfo, TemplateTopicInfo
    spec = TEMPLATES[template_id]
    sections = spec["build"]()
    section_infos = [
        TemplateSectionInfo(
            title=s["title"], section_type=s["section_type"], description=s["description"],
            guidance_text=s["guidance_text"],
            topics=[TemplateTopicInfo(title=t["title"], topic_type=t["topic_type"], guidance_text=t["guidance_text"])
                    for t in s["topics"]],
        )
        for s in sections
    ]
    return OutlineTemplateInfo(
        id=template_id, name=spec["name"], description=spec["description"],
        business_types=spec["business_types"], section_count=len(section_infos),
        topic_count=sum(len(s.topics) for s in section_infos), sections=section_infos,
    )


def list_outline_templates():
    return [_template_info(tid) for tid in TEMPLATES]


def generate_outline_suggestions(project: BusinessPlanProject):
    from ..schemas.text_plan import OutlineSuggestionResponse
    template_id, btype = recommend_template_id(project)
    style = _report_style(project)
    name = TEMPLATES[template_id]["name"]
    industry = project.setup.industry if project.setup else "your business"
    explanation = (
        f"Based on your industry ({industry}), revenue model and business setup, "
        f"we recommend the {name} outline."
    )
    return OutlineSuggestionResponse(
        detected_business_type=btype, recommended_template_id=template_id,
        explanation=explanation, report_style=style, templates=list_outline_templates(),
    )


def apply_outline_template(storage: StorageBackend, project_id: str, request):
    """Create sections + topics from a template into the project's text plan."""
    from .text_plan_service import _reindex
    project = storage.get_project(project_id)
    if request.template_id not in TEMPLATES:
        raise KeyError(f"Unknown template {request.template_id!r}")
    spec = TEMPLATES[request.template_id]
    build = spec["build"]
    try:
        section_specs = build(sample=request.with_sample_content)
    except TypeError:
        section_specs = build()

    doc = project.text_plan
    if request.mode == "replace":
        doc.sections = []
    doc.template_id = request.template_id
    doc.business_type = detect_business_type(project)

    sel_sections = set(request.selected_section_titles) if request.selected_section_titles else None
    sel_topics = set(request.selected_topic_titles) if request.selected_topic_titles else None

    for sspec in section_specs:
        if sel_sections is not None and sspec["title"] not in sel_sections:
            continue
        section = TextPlanSection(
            title=sspec["title"], section_type=sspec["section_type"],
            description=sspec["description"], guidance_text=sspec["guidance_text"],
        )
        for tspec in sspec["topics"]:
            if sel_topics is not None and tspec["title"] not in sel_topics:
                continue
            topic = TextPlanTopic(
                section_id=section.id, title=tspec["title"], topic_type=tspec["topic_type"],
                guidance_text=tspec["guidance_text"], content_html=tspec.get("sample_html", ""),
            )
            if topic.content_html:
                from .text_plan_service import _recompute_topic_metrics
                _recompute_topic_metrics(topic)
            section.topics.append(topic)
        _reindex(section.topics)
        doc.sections.append(section)
    _reindex(doc.sections)
    doc.touch()
    project.touch()
    storage.save_project(project)
    return doc
