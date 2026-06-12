"""Pages 9-10 — Working Capital and Financing models."""
from __future__ import annotations

from datetime import date

from pydantic import Field

from .base import EntityBase
from .enums import FinancingSource, RepaymentType, StockPurchaseCycle


# --------------------------------------------------------------------------
# Page 9 — Working Capital
# --------------------------------------------------------------------------
class WorkingCapitalAssumption(EntityBase):
    accounts_receivable_days: float = Field(default=30, ge=0)
    percent_sales_on_credit: float = Field(default=0, ge=0, le=100)
    accounts_payable_days: float = Field(default=30, ge=0)
    inventory_days: float = Field(default=0, ge=0)
    minimum_cash_balance: float = Field(default=0, ge=0)
    safety_stock_percent: float = Field(default=0, ge=0, le=100)
    bad_debt_percent: float = Field(default=0, ge=0, le=100)
    customer_deposit_percent: float = Field(default=0, ge=0, le=100)
    supplier_advance_percent: float = Field(default=0, ge=0, le=100)
    stock_purchase_cycle: StockPurchaseCycle = StockPurchaseCycle.MONTHLY
    collection_warning_threshold_days: float = Field(default=90, ge=0)

    @property
    def cash_conversion_cycle(self) -> float:
        """CCC = DIO + DSO - DPO."""
        return (
            self.inventory_days
            + self.accounts_receivable_days
            - self.accounts_payable_days
        )


# --------------------------------------------------------------------------
# Page 10 — Financing (Equity + Loans + Grants)
# --------------------------------------------------------------------------
class EquityFunding(EntityBase):
    founder_capital: float = Field(default=0, ge=0)
    investor_equity: float = Field(default=0, ge=0)
    investment_date: date | None = None
    shareholding_percent: float = Field(default=0, ge=0, le=100)
    investor_name: str | None = Field(default=None, max_length=160)
    use_of_funds: str | None = Field(default=None, max_length=2000)
    dividend_policy_percent: float = Field(default=0, ge=0, le=100)


class LoanFunding(EntityBase):
    name: str = Field(..., min_length=1, max_length=160)
    lender: str | None = Field(default=None, max_length=160)
    amount: float = Field(default=0, ge=0)
    drawdown_date: date | None = None
    interest_rate: float = Field(default=0, ge=0, description="annual %")
    repayment_period_months: int = Field(default=12, ge=1)
    grace_period_months: int = Field(default=0, ge=0)
    repayment_type: RepaymentType = RepaymentType.EQUAL_INSTALLMENTS
    collateral: str | None = Field(default=None, max_length=400)
    arrangement_fee: float = Field(default=0, ge=0)


class GrantFunding(EntityBase):
    name: str = Field(..., min_length=1, max_length=160)
    amount: float = Field(default=0, ge=0)
    expected_date: date | None = None
    restrictions: str | None = Field(default=None, max_length=2000)
    # When True, the grant is only recognised as other income in the optimistic
    # scenario (P&L). When False, it is recognised in every scenario.
    scenario_dependent: bool = False


class Financing(EntityBase):
    """Aggregate financing container persisted as a singleton per project."""

    equity: EquityFunding = Field(default_factory=EquityFunding)
    loans: list[LoanFunding] = Field(default_factory=list)
    grants: list[GrantFunding] = Field(default_factory=list)

    @property
    def total_funding(self) -> float:
        equity = self.equity.founder_capital + self.equity.investor_equity
        loans = sum(loan.amount for loan in self.loans)
        grants = sum(grant.amount for grant in self.grants)
        return equity + loans + grants
