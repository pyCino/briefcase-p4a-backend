"""
Briefcase P4A Backend - Python-for-Android backend for Briefcase

Build Android APKs using python-for-android directly within Briefcase.

Author: Al pyCino <thealpycino@gmail.com>
License: MIT
"""

from __future__ import annotations

# Export all P4A commands from p4a.py
from .p4a import (
    P4ACreateCommand,
    P4AUpdateCommand,
    P4AOpenCommand,
    P4ABuildCommand,
    P4ARunCommand,
    P4APackageCommand,
    P4APublishCommand,
)

__version__ = "1.0.0"
__author__ = "Al pyCino"
__email__ = "thealpycino@gmail.com"

__all__ = [
    "P4ACreateCommand",
    "P4AUpdateCommand", 
    "P4AOpenCommand",
    "P4ABuildCommand",
    "P4ARunCommand",
    "P4APackageCommand",
    "P4APublishCommand",
]

# Export commands at module level like gradle format does
create = P4ACreateCommand
update = P4AUpdateCommand
open = P4AOpenCommand
build = P4ABuildCommand
run = P4ARunCommand
package = P4APackageCommand
publish = P4APublishCommand 