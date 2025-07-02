"""
Android P4A Platform for Briefcase.

This module provides the AndroidP4APlatform class that registers all P4A commands
for the Briefcase backend system.
"""

from briefcase.platforms.android import AndroidPlatform

from .p4a import (
    P4ACreateCommand,
    P4AUpdateCommand,
    P4AOpenCommand,
    P4ABuildCommand,
    P4ARunCommand,
    P4APackageCommand,
    P4APublishCommand,
)


class AndroidP4APlatform(AndroidPlatform):
    """Android platform using Python-for-Android (P4A)."""

    # Register all P4A commands
    create_command = P4ACreateCommand
    update_command = P4AUpdateCommand
    open_command = P4AOpenCommand
    build_command = P4ABuildCommand
    run_command = P4ARunCommand
    package_command = P4APackageCommand
    publish_command = P4APublishCommand 