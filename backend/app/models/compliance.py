"""Page 11 — Tax, VAT & Regulatory model."""
from __future__ import annotations

from pydantic import Field

from .base import EntityBase
from .enums import TaxFrequency


class TaxAssumption(EntityBase):
    corporate_tax_rate: float = Field(default=0, ge=0, le=100)
    vat_rate: float = Field(default=0, ge=0, le=100)
    vat_registration_threshold: float = Field(default=0, ge=0)
    customs_duty_rate: float = Field(default=0, ge=0, le=100)
    municipality_fees: float = Field(default=0, ge=0)
    license_renewal_fees: float = Field(default=0, ge=0)
    withholding_tax_rate: float = Field(default=0, ge=0, le=100)
    zakat_rate: float | None = Field(default=None, ge=0, le=100)
    employer_social_security_rate: float = Field(default=0, ge=0, le=100)
    employee_social_security_rate: float = Field(default=0, ge=0, le=100)

    tax_payment_frequency: TaxFrequency = TaxFrequency.YEARLY
    vat_payment_frequency: TaxFrequency = TaxFrequency.QUARTERLY
    tax_loss_carryforward_enabled: bool = True

    corporate_tax_enabled: bool = True
    vat_enabled: bool = True
