from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    VIP = "vip"
    STANDARD = "standard"
