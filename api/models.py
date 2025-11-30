"""
Pydantic models for API request/response validation.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ===== Request Models =====


class PersonInput(BaseModel):
    name: str = Field(..., min_length=1, description="Person's name")
    work_share: float = Field(..., ge=0, le=1, description="Work share (0.0 to 1.0)")


class ProjectCreate(BaseModel):
    num_people: int = Field(..., gt=0, description="Number of people")
    revenue: float = Field(..., ge=0, description="Total revenue")
    costs: List[float] = Field(..., description="List of costs")
    country: str = Field(
        ..., min_length=1, description="Country (e.g., US, Spain, UK, etc.)"
    )
    tax_type: str = Field(
        ...,
        pattern="^(Individual|Business)$",
        description="Tax type: Individual or Business",
    )
    distribution_method: str = Field(
        default="N/A",
        pattern="^(N/A|Salary|Dividend|Mixed|Reinvest)$",
        description="Distribution method for Business tax",
    )
    salary_amount: Optional[float] = Field(
        default=0, ge=0, description="Salary amount for Mixed distribution method"
    )
    people: List[PersonInput] = Field(
        ..., description="List of people with work shares"
    )

    @field_validator("people")
    @classmethod
    def validate_people_count(cls, v, info):
        if "num_people" in info.data and len(v) != info.data["num_people"]:
            raise ValueError(f"Expected {info.data['num_people']} people, got {len(v)}")
        return v

    @field_validator("people")
    @classmethod
    def validate_work_shares(cls, v):
        total_share = sum(person.work_share for person in v)
        if abs(total_share - 1.0) > 0.01:
            raise ValueError(f"Work shares must sum to 1.0, got {total_share:.2f}")
        return v


class TaxBracketCreate(BaseModel):
    country: str = Field(..., min_length=1, description="Country name")
    tax_type: str = Field(..., pattern="^(Individual|Business)$")
    income_limit: float = Field(..., ge=0)
    rate: float = Field(..., ge=0, le=1)


class RecordUpdate(BaseModel):
    field: str = Field(
        ...,
        pattern="^(num_people|revenue|total_costs|tax_origin|tax_option|distribution_method|salary_amount)$",
    )
    value: str | int | float


# ===== Response Models =====


class PersonResponse(BaseModel):
    id: int
    name: str
    work_share: float
    gross_income: float
    tax_paid: float
    net_income: float

    class Config:
        from_attributes = True


class RecordResponse(BaseModel):
    id: int
    num_people: int
    revenue: float
    total_costs: float
    group_income: float
    individual_income: float
    tax_origin: str
    tax_option: str
    tax_amount: float
    net_income_per_person: float
    net_income_group: float
    distribution_method: str = "N/A"
    salary_amount: float = 0
    created_at: str

    class Config:
        from_attributes = True


class RecordWithPeople(RecordResponse):
    people: List[PersonResponse] = []


class TaxBracketResponse(BaseModel):
    id: int
    country: str
    tax_type: str
    income_limit: float
    rate: float

    class Config:
        from_attributes = True


class ProjectCreateResponse(BaseModel):
    record_id: int
    message: str
    summary: dict


class MessageResponse(BaseModel):
    message: str
    details: Optional[dict] = None
