"""AquaPure Smart Filters FZE — full demo company builder.

Constructs a complete, schema-valid :class:`BusinessPlanProject` with stable
string IDs across every section. This is the canonical source used to generate
``app/seeds/demo_aquapure_smart_filters.json`` (the runtime source of truth).
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from ..models import (
    BusinessPlanProject,
    CostAllocation,
    DirectCostItem,
    EquityFunding,
    Financing,
    FixedAsset,
    GrantFunding,
    KPIAssumption,
    LoanFunding,
    OperatingExpense,
    ProductService,
    ProjectSetup,
    RevenueAssumption,
    RevenueMilestone,
    ScenarioAssumption,
    SeasonalityMonth,
    StaffRole,
    StartupCost,
    TaxAssumption,
    WorkingCapitalAssumption,
)
from ..models.enums import (
    BusinessModel,
    CostAllocationMethod,
    CostBehavior,
    CostCalculationMethod,
    Department,
    DepreciationMethod,
    DirectCostCategory,
    ExpenseCategory,
    ExpenseFrequency,
    FinancingSource,
    FixedAssetCategory,
    PaymentTerms,
    ProjectionFrequency,
    ProjectionPeriod,
    RepaymentType,
    ReportingStandard,
    RevenueType,
    ScenarioType,
    StartupCostCategory,
    StockPurchaseCycle,
    TaxFrequency,
)

DEMO_PROJECT_ID = "demo_aquapure"
_TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _stamp(model):
    """Force stable created/updated timestamps for deterministic seed output."""
    model.created_at = _TS
    model.updated_at = _TS
    return model


def _seasonality(key: str, values: list[int]) -> list[SeasonalityMonth]:
    return [
        _stamp(SeasonalityMonth(id=f"seas_{key}_{m}", month=m, adjustment_percent=float(v)))
        for m, v in enumerate(values, start=1)
    ]


# Product IDs (referenced across revenue, direct costs, etc.)
P_RES = "prod_residential_filter"
P_COM = "prod_commercial_filter"
S_INSTALL = "service_installation"
S_MAINT = "service_maintenance_contract"
P_REPL = "prod_replacement_filters"
S_IOT = "service_iot_monitoring"


def build_demo_project() -> BusinessPlanProject:
    # ----------------------------------------------------------------- Setup
    setup = ProjectSetup(
        id="setup_aquapure",
        business_name="AquaPure Smart Filters FZE",
        project_name="Dubai Smart Water Filtration Expansion Plan",
        business_description=(
            "AquaPure Smart Filters FZE imports high-quality water filtration "
            "components, assembles smart filtration systems locally, installs them "
            "for residential and commercial customers, and provides ongoing "
            "maintenance, filter replacement, and IoT-based water quality "
            "monitoring subscriptions."
        ),
        industry="Water Treatment & Smart Home Services",
        business_model=BusinessModel.OTHER,
        country="United Arab Emirates",
        city="Dubai",
        currency="AED",
        projection_start_date=date(2026, 1, 1),
        projection_period=ProjectionPeriod.FIVE_YEARS,
        projection_frequency=ProjectionFrequency.MONTHLY,
        tax_jurisdiction="United Arab Emirates Corporate Tax",
        reporting_standard=ReportingStandard.INVESTOR,
        scenario_mode_enabled=True,
        notes="Hybrid model: product sales, installation, maintenance, consumables, and subscription monitoring.",
    )

    # -------------------------------------------------------------- Products
    products = [
        ProductService(id=P_RES, name="Residential Smart Filtration System", category="Product Sale",
                       description="Smart under-sink and villa water filtration unit with basic IoT water quality indicator.",
                       revenue_type=RevenueType.UNIT_SALES, selling_price=2800, unit_of_sale="System",
                       launch_date=date(2026, 1, 1), active=True),
        ProductService(id=P_COM, name="Commercial Smart Filtration System", category="Product Sale",
                       description="Larger-capacity filtration system for restaurants, offices, clinics, and small commercial facilities.",
                       revenue_type=RevenueType.UNIT_SALES, selling_price=8500, unit_of_sale="System",
                       launch_date=date(2026, 2, 1), active=True),
        ProductService(id=S_INSTALL, name="Standard Installation Service", category="Service",
                       description="Installation, setup, water-flow test, and customer handover for residential and commercial systems.",
                       revenue_type=RevenueType.SERVICE_CONTRACT, selling_price=650, unit_of_sale="Installation",
                       launch_date=date(2026, 1, 1), active=True),
        ProductService(id=S_MAINT, name="Annual Maintenance Contract", category="Recurring Service",
                       description="Annual maintenance package including inspection, cleaning, minor adjustments, and priority support.",
                       revenue_type=RevenueType.SUBSCRIPTION, selling_price=1200, unit_of_sale="Annual contract",
                       launch_date=date(2026, 3, 1), active=True),
        ProductService(id=P_REPL, name="Replacement Filter Pack", category="Consumables",
                       description="Replacement cartridge and membrane filter pack for existing AquaPure customers.",
                       revenue_type=RevenueType.UNIT_SALES, selling_price=480, unit_of_sale="Filter pack",
                       launch_date=date(2026, 4, 1), active=True),
        ProductService(id=S_IOT, name="Smart Water Monitoring Subscription", category="SaaS / Monitoring",
                       description="Monthly digital monitoring service for water quality alerts, maintenance reminders, and customer dashboard.",
                       revenue_type=RevenueType.SUBSCRIPTION, selling_price=55, unit_of_sale="Monthly subscription",
                       launch_date=date(2026, 6, 1), active=True),
    ]

    # -------------------------------------------------------------- Revenue
    revenue = [
        RevenueAssumption(
            id="rev_residential", product_id=P_RES, starting_monthly_volume=25, annual_growth_rate=28,
            monthly_growth_rate=2.1, number_of_customers=25, customer_growth_rate=25, average_order_value=2800,
            purchase_frequency=1, repeat_purchase_rate=5, discount_percent=6, refund_percent=1,
            seasonality_enabled=True, payment_terms=PaymentTerms.NET_30,
            seasonality=_seasonality("res", [90, 95, 105, 100, 105, 110, 85, 80, 105, 115, 120, 110]),
            notes="Split terms: 30% cash on delivery, 70% within 30 days (mapped to Net 30).",
        ),
        RevenueAssumption(
            id="rev_commercial", product_id=P_COM, starting_monthly_volume=6, annual_growth_rate=35,
            monthly_growth_rate=2.5, number_of_customers=6, customer_growth_rate=30, average_order_value=8500,
            purchase_frequency=1, repeat_purchase_rate=8, discount_percent=8, refund_percent=1,
            seasonality_enabled=True, payment_terms=PaymentTerms.NET_45,
            seasonality=_seasonality("com", [85, 90, 100, 105, 110, 110, 90, 85, 105, 115, 120, 115]),
            notes="Split terms: 20% cash on delivery, 80% within 45 days (mapped to Net 45).",
        ),
        RevenueAssumption(
            id="rev_installation", product_id=S_INSTALL, starting_monthly_volume=31, annual_growth_rate=30,
            monthly_growth_rate=2.2, number_of_customers=31, average_order_value=650, purchase_frequency=1,
            discount_percent=0, refund_percent=0.5, seasonality_enabled=True, payment_terms=PaymentTerms.CASH,
            seasonality=_seasonality("ins", [90, 95, 105, 100, 105, 110, 85, 80, 105, 115, 120, 110]),
            notes="Installations track total system sales; seasonality mirrors residential systems.",
        ),
        RevenueAssumption(
            id="rev_maintenance", product_id=S_MAINT, starting_monthly_volume=15, annual_growth_rate=45,
            monthly_growth_rate=3.1, subscription_price=1200, churn_rate=8, repeat_purchase_rate=65,
            discount_percent=5, refund_percent=1, seasonality_enabled=False, payment_terms=PaymentTerms.NET_30,
            notes="Annual contracts. 50% cash, 50% within 30 days (mapped to Net 30). Churn 8% annually.",
        ),
        RevenueAssumption(
            id="rev_replacement", product_id=P_REPL, starting_monthly_volume=40, annual_growth_rate=55,
            monthly_growth_rate=3.7, average_order_value=480, purchase_frequency=2, repeat_purchase_rate=70,
            discount_percent=3, refund_percent=1, seasonality_enabled=True, payment_terms=PaymentTerms.CASH,
            seasonality=_seasonality("rep", [95, 95, 100, 105, 110, 115, 105, 100, 105, 110, 110, 105]),
            notes="~2 packs per active customer per year.",
        ),
        RevenueAssumption(
            id="rev_iot", product_id=S_IOT, starting_monthly_volume=40, annual_growth_rate=60,
            monthly_growth_rate=4, number_of_customers=40, customer_growth_rate=60, subscription_price=55,
            churn_rate=3, discount_percent=0, refund_percent=0.5, seasonality_enabled=False,
            payment_terms=PaymentTerms.CASH,
            notes="Monthly prepaid subscription. Churn 3% monthly.",
        ),
    ]

    # --------------------------------------------------------- Direct costs
    direct_costs = [
        DirectCostItem(id="dc_residential_imported_components", name="Imported Residential Filter Components",
                       category=DirectCostCategory.PURCHASED_GOODS, product_ids=[P_RES],
                       cost_behavior=CostBehavior.VARIABLE, calculation_method=CostCalculationMethod.FIXED_PER_UNIT,
                       amount=1250, supplier_name="Shenzhen PureTech Components Ltd.",
                       supplier_payment_terms=PaymentTerms.NET_45, cost_inflation_rate=4, vat_applicable=False,
                       start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_residential_packaging", name="Residential Packaging and Labels",
                       category=DirectCostCategory.PACKAGING, product_ids=[P_RES],
                       calculation_method=CostCalculationMethod.FIXED_PER_UNIT, amount=85,
                       supplier_payment_terms=PaymentTerms.NET_30, cost_inflation_rate=3, vat_applicable=True,
                       start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_commercial_imported_components", name="Imported Commercial Filter Components",
                       category=DirectCostCategory.PURCHASED_GOODS, product_ids=[P_COM],
                       calculation_method=CostCalculationMethod.FIXED_PER_UNIT, amount=4200,
                       supplier_name="Shenzhen PureTech Components Ltd.", supplier_payment_terms=PaymentTerms.NET_45,
                       cost_inflation_rate=4, vat_applicable=False, start_date=date(2026, 2, 1), active=True),
        DirectCostItem(id="dc_commercial_packaging", name="Commercial Crating and Packaging",
                       category=DirectCostCategory.PACKAGING, product_ids=[P_COM],
                       calculation_method=CostCalculationMethod.FIXED_PER_UNIT, amount=260,
                       supplier_payment_terms=PaymentTerms.NET_30, cost_inflation_rate=3, vat_applicable=True,
                       start_date=date(2026, 2, 1), active=True),
        DirectCostItem(id="dc_installation_labor", name="Technician Direct Installation Labor",
                       category=DirectCostCategory.DIRECT_LABOR, product_ids=[S_INSTALL],
                       calculation_method=CostCalculationMethod.PER_SERVICE_DELIVERY, amount=210,
                       cost_inflation_rate=5, vat_applicable=False, start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_installation_consumables", name="Installation Consumables and Fittings",
                       category=DirectCostCategory.INSTALLATION, product_ids=[S_INSTALL],
                       calculation_method=CostCalculationMethod.PER_SERVICE_DELIVERY, amount=95,
                       supplier_payment_terms=PaymentTerms.NET_30, cost_inflation_rate=4, vat_applicable=True,
                       start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_maintenance_visit_cost", name="Maintenance Visit Direct Cost",
                       category=DirectCostCategory.MAINTENANCE, product_ids=[S_MAINT],
                       calculation_method=CostCalculationMethod.PER_CONTRACT, amount=360, cost_inflation_rate=5,
                       vat_applicable=False, start_date=date(2026, 3, 1), active=True),
        DirectCostItem(id="dc_replacement_filter_pack_cost", name="Replacement Filter Pack Purchase Cost",
                       category=DirectCostCategory.PURCHASED_GOODS, product_ids=[P_REPL],
                       calculation_method=CostCalculationMethod.FIXED_PER_UNIT, amount=190,
                       supplier_payment_terms=PaymentTerms.NET_45, cost_inflation_rate=4, vat_applicable=False,
                       start_date=date(2026, 4, 1), active=True),
        DirectCostItem(id="dc_iot_platform_cost", name="IoT Cloud Platform Cost",
                       category=DirectCostCategory.HOSTING, product_ids=[S_IOT],
                       calculation_method=CostCalculationMethod.PER_CUSTOMER, amount=12,
                       supplier_name="Cloud IoT Platform Provider", supplier_payment_terms=PaymentTerms.NET_15,
                       cost_inflation_rate=3, vat_applicable=True, start_date=date(2026, 6, 1), active=True),
        DirectCostItem(id="dc_payment_gateway_fees", name="Payment Gateway Fees",
                       category=DirectCostCategory.PAYMENT_GATEWAY, apply_to_all=True,
                       cost_behavior=CostBehavior.VARIABLE, calculation_method=CostCalculationMethod.PERCENT_OF_REVENUE,
                       percent=2.4, allocation_method=CostAllocationMethod.REVENUE_SHARE, vat_applicable=True,
                       start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_sales_commission", name="Sales Commission",
                       category=DirectCostCategory.SALES_COMMISSION, product_ids=[P_RES, P_COM, S_MAINT],
                       calculation_method=CostCalculationMethod.PERCENT_OF_REVENUE, percent=5,
                       allocation_method=CostAllocationMethod.REVENUE_SHARE, start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_warranty_provision", name="Warranty Provision",
                       category=DirectCostCategory.WARRANTY, product_ids=[P_RES, P_COM],
                       calculation_method=CostCalculationMethod.PERCENT_OF_SELLING_PRICE, percent=2,
                       allocation_method=CostAllocationMethod.REVENUE_SHARE, start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_import_customs", name="Import Duty and Clearance Cost",
                       category=DirectCostCategory.CUSTOMS, product_ids=[P_RES, P_COM, P_REPL],
                       calculation_method=CostCalculationMethod.PERCENT_OF_PURCHASE_COST, percent=5,
                       allocation_method=CostAllocationMethod.REVENUE_SHARE, start_date=date(2026, 1, 1), active=True),
        DirectCostItem(id="dc_unassigned_future_supplier", name="Future Local Assembly Outsourcing Cost",
                       category=DirectCostCategory.SUBCONTRACTOR, calculation_method=CostCalculationMethod.FIXED_PER_UNIT,
                       amount=0, start_date=date(2027, 1, 1), active=False,
                       notes="Placeholder for possible local assembly partner in Year 2."),
    ]

    # ------------------------------------------------------------- Staffing
    staffing = [
        StaffRole(id="staff_general_manager", department=Department.MANAGEMENT, job_title="General Manager",
                  number_of_employees=1, monthly_salary=24000, hiring_start_date=date(2026, 1, 1),
                  annual_increase_percent=5, benefits_percent=12, health_insurance_amount=7500, visa_permit_cost=6000,
                  bonus_percent=10, employer_social_security_percent=0, gratuity_percent=5, active=True),
        StaffRole(id="staff_sales_manager", department=Department.SALES, job_title="Sales Manager",
                  number_of_employees=1, monthly_salary=16000, hiring_start_date=date(2026, 1, 1),
                  annual_increase_percent=5, benefits_percent=10, bonus_percent=8, sales_commission_percent=1.5,
                  active=True),
        StaffRole(id="staff_sales_executives", department=Department.SALES, job_title="Sales Executive",
                  number_of_employees=2, monthly_salary=8000, hiring_start_date=date(2026, 1, 1),
                  annual_increase_percent=5, benefits_percent=10, sales_commission_percent=3, active=True),
        StaffRole(id="staff_technicians", department=Department.OPERATIONS,
                  job_title="Installation & Maintenance Technician", number_of_employees=3, monthly_salary=6500,
                  hiring_start_date=date(2026, 1, 1), annual_increase_percent=5, benefits_percent=10,
                  health_insurance_amount=4500, visa_permit_cost=5000, active=True),
        StaffRole(id="staff_customer_support", department=Department.CUSTOMER_SUPPORT,
                  job_title="Customer Support Coordinator", number_of_employees=1, monthly_salary=6000,
                  hiring_start_date=date(2026, 3, 1), annual_increase_percent=4, benefits_percent=8, active=True),
        StaffRole(id="staff_accountant", department=Department.FINANCE, job_title="Accountant / Admin Officer",
                  number_of_employees=1, monthly_salary=7500, hiring_start_date=date(2026, 1, 1),
                  annual_increase_percent=4, benefits_percent=8, active=True),
        StaffRole(id="staff_iot_specialist", department=Department.TECHNOLOGY, job_title="IoT Platform Specialist",
                  number_of_employees=1, monthly_salary=14000, hiring_start_date=date(2026, 6, 1),
                  annual_increase_percent=5, benefits_percent=10, active=True),
    ]

    # --------------------------------------------------- Operating expenses
    M, Y = ExpenseFrequency.MONTHLY, ExpenseFrequency.YEARLY
    operating_expenses = [
        OperatingExpense(id="opex_rent", name="Office and Small Warehouse Rent", category=ExpenseCategory.RENT,
                         amount=18000, frequency=M, start_date=date(2026, 1, 1), inflation_percent=5,
                         vat_applicable=True, is_fixed=True),
        OperatingExpense(id="opex_utilities", name="Utilities", category=ExpenseCategory.UTILITIES, amount=3200,
                         frequency=M, start_date=date(2026, 1, 1), inflation_percent=4, vat_applicable=True,
                         is_fixed=False, notes="Semi-variable."),
        OperatingExpense(id="opex_internet", name="Internet and Telecom", category=ExpenseCategory.INTERNET,
                         amount=1800, frequency=M, start_date=date(2026, 1, 1), inflation_percent=3,
                         vat_applicable=True, is_fixed=True),
        OperatingExpense(id="opex_digital_marketing", name="Digital Marketing", category=ExpenseCategory.MARKETING,
                         amount=22000, frequency=M, start_date=date(2026, 1, 1), inflation_percent=8,
                         vat_applicable=True, is_fixed=False),
        OperatingExpense(id="opex_ads", name="Google Ads and Social Ads", category=ExpenseCategory.ADVERTISING,
                         amount=15000, frequency=M, start_date=date(2026, 1, 1), inflation_percent=8,
                         vat_applicable=True, is_fixed=False),
        OperatingExpense(id="opex_accounting", name="Accounting and Audit", category=ExpenseCategory.ACCOUNTING,
                         amount=36000, frequency=Y, start_date=date(2026, 12, 1), inflation_percent=5,
                         vat_applicable=True, is_fixed=True),
        OperatingExpense(id="opex_legal", name="Legal and Compliance", category=ExpenseCategory.LEGAL, amount=24000,
                         frequency=Y, start_date=date(2026, 1, 1), inflation_percent=5, vat_applicable=True,
                         is_fixed=True),
        OperatingExpense(id="opex_insurance", name="Business Insurance", category=ExpenseCategory.INSURANCE,
                         amount=28000, frequency=Y, start_date=date(2026, 1, 1), inflation_percent=4,
                         vat_applicable=True, is_fixed=True),
        OperatingExpense(id="opex_vehicle", name="Vehicle Fuel and Maintenance", category=ExpenseCategory.MAINTENANCE,
                         amount=4500, frequency=M, start_date=date(2026, 1, 1), inflation_percent=5,
                         vat_applicable=True, is_fixed=False, notes="Semi-variable."),
        OperatingExpense(id="opex_software", name="CRM and Business Software", category=ExpenseCategory.SOFTWARE,
                         amount=3800, frequency=M, start_date=date(2026, 1, 1), inflation_percent=4,
                         vat_applicable=True, is_fixed=True),
        OperatingExpense(id="opex_office_supplies", name="Office Supplies", category=ExpenseCategory.OFFICE_SUPPLIES,
                         amount=1500, frequency=M, start_date=date(2026, 1, 1), inflation_percent=3,
                         vat_applicable=True, is_fixed=False, notes="Semi-variable."),
        OperatingExpense(id="opex_bank_charges", name="Bank Charges", category=ExpenseCategory.BANK_CHARGES, amount=900,
                         frequency=M, start_date=date(2026, 1, 1), inflation_percent=2, vat_applicable=False,
                         is_fixed=False, notes="Semi-variable."),
        OperatingExpense(id="opex_trade_shows", name="Trade Shows and Exhibitions", category=ExpenseCategory.MARKETING,
                         amount=65000, frequency=Y, start_date=date(2026, 10, 1), inflation_percent=5,
                         vat_applicable=True, is_fixed=False),
    ]

    # ----------------------------------------------------------- Startup costs
    SC = StartupCostCategory
    startup_costs = [
        StartupCost(id="startup_registration", name="Company Registration", category=SC.REGISTRATION, amount=18000,
                    payment_date=date(2025, 12, 15), capitalized=False),
        StartupCost(id="startup_trade_license", name="Trade License", category=SC.TRADE_LICENSE, amount=32000,
                    payment_date=date(2025, 12, 20), capitalized=False),
        StartupCost(id="startup_legal_setup", name="Legal Setup", category=SC.LEGAL_SETUP, amount=15000,
                    payment_date=date(2025, 12, 20), capitalized=False),
        StartupCost(id="startup_branding", name="Initial Branding", category=SC.BRANDING, amount=28000,
                    payment_date=date(2025, 12, 25), capitalized=False),
        StartupCost(id="startup_website", name="Website and E-commerce Setup", category=SC.WEBSITE, amount=45000,
                    payment_date=date(2025, 12, 28), capitalized=True),
        StartupCost(id="startup_iot_mvp", name="IoT Dashboard MVP", category=SC.SOFTWARE_DEV, amount=85000,
                    payment_date=date(2025, 12, 28), capitalized=True),
        StartupCost(id="startup_marketing_launch", name="Initial Marketing Launch Campaign",
                    category=SC.INITIAL_MARKETING, amount=70000, payment_date=date(2026, 1, 1), capitalized=False),
        StartupCost(id="startup_recruitment", name="Recruitment Fees", category=SC.RECRUITMENT, amount=25000,
                    payment_date=date(2025, 12, 30), capitalized=False),
        StartupCost(id="startup_office_deposit", name="Office and Warehouse Deposit", category=SC.OFFICE_DEPOSIT,
                    amount=54000, payment_date=date(2025, 12, 15), capitalized=True),
        StartupCost(id="startup_rent_advance", name="Rent Advance", category=SC.RENT_ADVANCE, amount=54000,
                    payment_date=date(2025, 12, 15), capitalized=False),
        StartupCost(id="startup_inventory_residential", name="Initial Residential Inventory",
                    category=SC.INITIAL_INVENTORY, amount=180000, payment_date=date(2025, 12, 30), capitalized=True),
        StartupCost(id="startup_inventory_commercial", name="Initial Commercial Inventory",
                    category=SC.INITIAL_INVENTORY, amount=210000, payment_date=date(2025, 12, 30), capitalized=True),
        StartupCost(id="startup_inventory_replacement", name="Initial Replacement Filters Inventory",
                    category=SC.INITIAL_INVENTORY, amount=55000, payment_date=date(2026, 1, 5), capitalized=True),
        StartupCost(id="startup_tools", name="Tools and Installation Kits", category=SC.EQUIPMENT, amount=38000,
                    payment_date=date(2025, 12, 28), capitalized=True),
        StartupCost(id="startup_consultancy", name="Consultancy and Launch Advisory", category=SC.CONSULTANCY,
                    amount=40000, payment_date=date(2025, 12, 25), capitalized=False),
    ]

    # ----------------------------------------------------------- Fixed assets
    FC = FixedAssetCategory
    _d = date(2026, 1, 1)
    fixed_assets = [
        FixedAsset(id="asset_tools", name="Assembly Tools and Workbench Equipment", category=FC.EQUIPMENT,
                   description="Workbench, hand tools and assembly jigs for local filter assembly.",
                   purchase_amount=85000, purchase_date=_d, ready_for_use_date=_d, useful_life_years=5,
                   depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=5000, capitalized=True,
                   replacement_cycle_years=5, maintenance_cost_percent=3,
                   financing_source=FinancingSource.FOUNDER_CAPITAL, supplier_name="Gulf Tools Trading",
                   vat_applicable=True, active=True),
        FixedAsset(id="asset_van", name="Delivery and Service Van", category=FC.VEHICLE, purchase_amount=145000,
                   description="Sign-written van for delivery, installation and service visits.",
                   purchase_date=_d, ready_for_use_date=_d, useful_life_years=5,
                   depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=25000, capitalized=True,
                   replacement_cycle_years=5, maintenance_cost_percent=6, financing_source=FinancingSource.LOAN,
                   supplier_name="Al Futtaim Motors", vat_applicable=True, active=True),
        FixedAsset(id="asset_furniture", name="Office Furniture and Fit-out", category=FC.FURNITURE,
                   purchase_amount=95000, purchase_date=_d, ready_for_use_date=_d, useful_life_years=5,
                   depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=10000, capitalized=True,
                   replacement_cycle_years=5, maintenance_cost_percent=2,
                   financing_source=FinancingSource.FOUNDER_CAPITAL, vat_applicable=True, active=True),
        FixedAsset(id="asset_computers", name="Computers and Devices", category=FC.COMPUTERS, purchase_amount=42000,
                   purchase_date=_d, ready_for_use_date=_d, useful_life_years=3,
                   depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=3000, capitalized=True,
                   replacement_cycle_years=3, maintenance_cost_percent=2,
                   financing_source=FinancingSource.FOUNDER_CAPITAL, vat_applicable=True, active=True),
        FixedAsset(id="asset_iot_platform", name="IoT Monitoring Platform Development", category=FC.SOFTWARE_DEV,
                   description="Capitalised development of the smart water-monitoring platform.",
                   purchase_amount=125000, purchase_date=date(2026, 6, 1), ready_for_use_date=date(2026, 6, 1),
                   useful_life_years=4, depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=0,
                   capitalized=True, replacement_cycle_years=4, maintenance_cost_percent=8,
                   financing_source=FinancingSource.INVESTOR, active=True),
        FixedAsset(id="asset_shelving", name="Warehouse Shelving and Storage System", category=FC.LEASEHOLD,
                   purchase_amount=60000, purchase_date=_d, ready_for_use_date=_d, useful_life_years=5,
                   depreciation_method=DepreciationMethod.STRAIGHT_LINE, residual_value=5000, capitalized=True,
                   replacement_cycle_years=5, maintenance_cost_percent=3,
                   financing_source=FinancingSource.FOUNDER_CAPITAL, supplier_name="Storite Systems",
                   vat_applicable=True, active=True),
    ]

    # ------------------------------------------------------- Working capital
    working_capital = WorkingCapitalAssumption(
        id="wc_aquapure", accounts_receivable_days=35, percent_sales_on_credit=55, accounts_payable_days=40,
        inventory_days=70, minimum_cash_balance=150000, safety_stock_percent=15, bad_debt_percent=1.5,
        customer_deposit_percent=15, supplier_advance_percent=20, stock_purchase_cycle=StockPurchaseCycle.MONTHLY,
        collection_warning_threshold_days=60,
        notes=("Blended assumptions across revenue streams. Commercial systems carry longer receivable (45d) and "
               "inventory (75d) cycles than residential; imported components are paid in 45 days with a 20% advance. "
               "Inventory planning is critical due to supplier lead times."),
    )

    # ------------------------------------------------------------ Financing
    financing = Financing(
        id="financing_aquapure",
        equity=EquityFunding(
            id="equity_aquapure", founder_capital=650000, investor_equity=350000, investment_date=date(2026, 1, 1),
            shareholding_percent=25, investor_name="Gulf Seed Growth Investor",
            use_of_funds="Inventory purchase, marketing launch, IoT platform development, working capital buffer, and hiring.",
            dividend_policy_percent=20,
            notes="Founder 75% / Investor 25%. Investor funds drawn 2026-03-01. No dividends Years 1-2; up to 20% of net profit from Year 3.",
        ),
        loans=[
            LoanFunding(id="loan_vehicle", name="Vehicle and Equipment Finance", lender="Emirates Commercial Bank",
                        amount=250000, drawdown_date=date(2026, 1, 1), interest_rate=8.5, repayment_period_months=48,
                        grace_period_months=3, repayment_type=RepaymentType.EQUAL_INSTALLMENTS,
                        collateral="Vehicle and equipment", arrangement_fee=3750,
                        notes="1.5% arrangement fee (3,750 AED). Used for service van and equipment."),
            LoanFunding(id="loan_working_capital", name="Working Capital Facility", lender="UAE SME Finance Partner",
                        amount=300000, drawdown_date=date(2026, 4, 1), interest_rate=10, repayment_period_months=36,
                        grace_period_months=6, repayment_type=RepaymentType.INTEREST_ONLY,
                        collateral="Receivables and inventory", arrangement_fee=6000,
                        notes="2% arrangement fee (6,000 AED). Supports inventory growth and receivables cycle."),
        ],
        grants=[
            GrantFunding(id="grant_sustainability", name="Sustainability Innovation Support Grant", amount=100000,
                         expected_date=date(2026, 9, 1), scenario_dependent=True,
                         restrictions="Must be used for smart monitoring, water-efficiency awareness, and customer education.",
                         notes="Not guaranteed; include in optimistic scenario only."),
        ],
    )

    # ----------------------------------------------------------------- Tax
    tax = TaxAssumption(
        id="tax_aquapure", corporate_tax_rate=9, vat_rate=5, vat_registration_threshold=375000, customs_duty_rate=5,
        municipality_fees=10000, license_renewal_fees=32000, withholding_tax_rate=0, zakat_rate=0,
        employer_social_security_rate=0, employee_social_security_rate=0, tax_payment_frequency=TaxFrequency.YEARLY,
        vat_payment_frequency=TaxFrequency.QUARTERLY, tax_loss_carryforward_enabled=True, corporate_tax_enabled=True,
        vat_enabled=True,
        notes="UAE corporate tax (9%) and VAT (5%). Social security 0% for expatriate staff. Keep flexible for free-zone qualifying income.",
    )

    # ------------------------------------------------------------- Scenarios
    scenarios = [
        ScenarioAssumption(id="scenario_base", scenario_type=ScenarioType.BASE, label="Base Case"),
        ScenarioAssumption(
            id="scenario_conservative", scenario_type=ScenarioType.CONSERVATIVE, label="Conservative Case",
            sales_volume_adjustment=-20, selling_price_adjustment=-5, direct_cost_adjustment=8, salary_adjustment=3,
            rent_adjustment=5, marketing_adjustment=-10, customer_growth_adjustment=-25, collection_days_adjustment=20,
            inventory_days_adjustment=15, interest_rate_adjustment=2, tax_rate_adjustment=0, inflation_adjustment=3),
        ScenarioAssumption(
            id="scenario_optimistic", scenario_type=ScenarioType.OPTIMISTIC, label="Optimistic Case",
            sales_volume_adjustment=25, selling_price_adjustment=3, direct_cost_adjustment=-5, salary_adjustment=5,
            rent_adjustment=0, marketing_adjustment=20, customer_growth_adjustment=30, collection_days_adjustment=-10,
            inventory_days_adjustment=-10, interest_rate_adjustment=-1, tax_rate_adjustment=0, inflation_adjustment=-1,
            notes="Includes the 100,000 AED Sustainability Innovation Support Grant (optimistic scenario only)."),
    ]

    # ----------------------------------------------------------------- KPIs
    kpis = KPIAssumption(
        id="kpi_aquapure", target_gross_margin_percent=45, target_ebitda_margin_percent=18,
        target_net_profit_margin_percent=10, break_even_target_date=date(2027, 6, 30), min_monthly_revenue_target=350000,
        min_cash_balance_target=150000, cac_target=650, ltv_target=4500, payback_period_target_months=36,
        roi_target_percent=25, dscr_target=1.4, current_ratio_target=1.5,
        milestones=[
            RevenueMilestone(id="ms_rev_y1", label="Year 1 Revenue", target_date=date(2026, 12, 31), target_amount=3500000),
            RevenueMilestone(id="ms_rev_y2", label="Year 2 Revenue", target_date=date(2027, 12, 31), target_amount=5200000),
            RevenueMilestone(id="ms_rev_y3", label="Year 3 Revenue", target_date=date(2028, 12, 31), target_amount=7200000),
            RevenueMilestone(id="ms_rev_y4", label="Year 4 Revenue", target_date=date(2029, 12, 31), target_amount=9400000),
            RevenueMilestone(id="ms_rev_y5", label="Year 5 Revenue", target_date=date(2030, 12, 31), target_amount=12000000),
            RevenueMilestone(id="ms_profit_y1", label="Year 1 Profit (break-even)", target_date=date(2026, 12, 31), target_amount=0, is_profit_milestone=True),
            RevenueMilestone(id="ms_profit_y2", label="Year 2 Net Profit", target_date=date(2027, 12, 31), target_amount=300000, is_profit_milestone=True),
            RevenueMilestone(id="ms_profit_y3", label="Year 3 Net Profit", target_date=date(2028, 12, 31), target_amount=750000, is_profit_milestone=True),
            RevenueMilestone(id="ms_profit_y4", label="Year 4 Net Profit", target_date=date(2029, 12, 31), target_amount=1200000, is_profit_milestone=True),
            RevenueMilestone(id="ms_profit_y5", label="Year 5 Net Profit", target_date=date(2030, 12, 31), target_amount=1800000, is_profit_milestone=True),
        ],
    )

    project = BusinessPlanProject(
        id=DEMO_PROJECT_ID,
        name="AquaPure Smart Filters FZE",
        setup=setup,
        products=products,
        revenue=revenue,
        direct_costs=direct_costs,
        staffing=staffing,
        operating_expenses=operating_expenses,
        startup_costs=startup_costs,
        fixed_assets=fixed_assets,
        working_capital=working_capital,
        financing=financing,
        tax=tax,
        scenarios=scenarios,
        kpis=kpis,
    )

    # Stable timestamps across the whole document.
    project.created_at = _TS
    project.updated_at = _TS
    for section in [setup, working_capital, financing, tax, kpis, *products, *revenue, *direct_costs,
                    *staffing, *operating_expenses, *startup_costs, *fixed_assets, *scenarios,
                    financing.equity, *financing.loans, *financing.grants, *kpis.milestones]:
        _stamp(section)

    # Seed explicit 60-month projection schedules (the income statement reads
    # these as the source of truth). Revenue quantities and expense amounts are
    # stored; direct-cost projections derive from method + revenue drivers.
    from . import operating_expense_projection_service as oep
    from . import revenue_projection_service as rps
    from .projection_period_service import build_projection_periods

    start, _years, n = build_projection_periods(project)
    rps.ensure_persisted(project, n, start)
    oep.ensure_persisted(project, n, start)

    return project
