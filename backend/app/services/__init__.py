"""Business-logic services: section registry, completion, review, seed."""
from __future__ import annotations

from .registry import COLLECTION_SECTIONS, SINGLETON_SECTIONS, SectionSpec
from .completion import build_completion_report, build_review_status
from .projects import ProjectService

__all__ = [
    "SectionSpec",
    "COLLECTION_SECTIONS",
    "SINGLETON_SECTIONS",
    "build_completion_report",
    "build_review_status",
    "ProjectService",
]
