"""
Briefcase P4A Backend - Python-for-Android Commands

This module provides Briefcase commands for building Android APKs using python-for-android
directly within Briefcase's build pipeline.

Features:
- Direct P4A integration with Briefcase's build pipeline
- Automatic Android SDK/NDK management
- Support for debug and release APK builds
- Python 3.13 compatibility with automatic version detection and conditional pyjnius handling
- UI framework agnostic Android APK generation
- Intelligent pyjnius conflict detection and warnings

Author: Al pyCino <thealpycino@gmail.com>
License: MIT
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from briefcase.commands import (
    BuildCommand,
    CreateCommand,
    OpenCommand,
    PackageCommand,
    PublishCommand,
    RunCommand,
    UpdateCommand,
)
from briefcase.config import AppConfig, parsed_version
from briefcase.exceptions import BriefcaseCommandError
from briefcase.integrations.android_sdk import AndroidSDK
from briefcase.integrations.subprocess import SubprocessArgT


# Default NDK version compatible with P4A
DEFAULT_NDK_VERSION = "25.2.9519653"


class P4AMixin:
    output_format = "p4a"
    platform = "android"
    platform_target_version = "0.3.23"

    @property
    def packaging_formats(self):
        return ["apk", "debug-apk"]

    @property
    def default_packaging_format(self):
        return "apk"

    def bundle_path(self, app):
        """The path to the bundle for the app in the P4A format.
        
        P4A templates use app_name instead of output_format for the directory structure.
        """
        return self.build_path(app) / app.app_name

    def project_path(self, app):
        return self.bundle_path(app)

    def binary_path(self, app):
        return self.bundle_path(app) / f"{app.formal_name}-debug.apk"

    def distribution_path(self, app):
        extension = {
            "apk": "apk",
            "debug-apk": "debug.apk",
        }[app.packaging_format]
        return self.dist_path / f"{app.formal_name}-{app.version}.{extension}"

    def run_p4a(self, app, args: list[SubprocessArgT]):
        """Run python-for-android commands.
        
        :param app: The application to build
        :param args: The p4a command arguments
        """
        env = os.environ.copy()
        env.update(self.tools.android_sdk.env)
        
        self.tools.subprocess.run(
            ["p4a"] + args,
            env=env,
            cwd=self.bundle_path(app),
            check=True,
            encoding=self.tools.system_encoding,
        )

    def verify_tools(self):
        """Verify that all required external tools are available."""
        super().verify_tools()
        AndroidSDK.verify(tools=self.tools)
        self._check_pyjnius_compatibility()
        
    def _check_pyjnius_compatibility(self):
        """Check for potential pyjnius compatibility issues and warn the user."""
        python_version = sys.version_info
        is_python_313_plus = python_version >= (3, 13)
        
        if not is_python_313_plus:
            return
            
        try:
            import pyjnius
            installed_version = getattr(pyjnius, '__version__', 'unknown')
            
            if not installed_version.startswith('1.') and 'dev' not in installed_version:
                self.tools.console.info(
                    f"Found pyjnius {installed_version} - compatible with Python {python_version.major}.{python_version.minor}",
                    prefix="Python 3.13"
                )
            else:
                self.tools.console.warning(
                    f"""
Potential pyjnius compatibility issue detected:
- Python version: {python_version.major}.{python_version.minor}.{python_version.micro}
- Installed pyjnius: {installed_version}

For Python 3.13+, you may need the latest pyjnius from master branch.
The backend will automatically use the correct version for APK builds,
but your development environment might need:

    pip install git+https://github.com/kivy/pyjnius.git

""",
                    prefix="Python 3.13"
                )
        except ImportError:
            self.tools.console.info(
                "No pyjnius found in environment - will be installed automatically during build",
                prefix="Python 3.13"
            )
    
    def _x_permissions(self, app: AppConfig):
        """Extract the known cross-platform permission definitions from the app's
        permissions definitions.

        After calling this method, the ``permissions`` declaration for the app will
        only contain keys that are *not* cross-platform keys.

        :param app: The config object for the app
        :returns: A dictionary of known cross-platform permission definitions.
        """
        return {
            key: app.permission.pop(key, None)
            for key in [
                "camera",
                "microphone",
                "coarse_location",
                "fine_location",
                "background_location",
                "photo_library",
            ]
        }

    def permissions_context(self, app: AppConfig, x_permissions: dict[str, str]):
        """Additional template context for permissions.

        :param app: The config object for the app
        :param x_permissions: The dictionary of known cross-platform permission
            definitions.
        :returns: The template context describing permissions for the app.
        """
        # Default Android permissions
        permissions = {
            "android.permission.INTERNET": True,
            "android.permission.ACCESS_NETWORK_STATE": True,
        }

        # Default Android features
        features = {}

        if x_permissions["camera"]:
            permissions["android.permission.CAMERA"] = True
            features["android.hardware.camera"] = False

        if x_permissions["microphone"]:
            permissions["android.permission.RECORD_AUDIO"] = True

        if x_permissions["fine_location"]:
            permissions["android.permission.ACCESS_FINE_LOCATION"] = True
            features["android.hardware.location.gps"] = False

        if x_permissions["coarse_location"]:
            permissions["android.permission.ACCESS_COARSE_LOCATION"] = True
            features["android.hardware.location.network"] = False

        if x_permissions["background_location"]:
            permissions["android.permission.ACCESS_BACKGROUND_LOCATION"] = True

        if x_permissions["photo_library"]:
            permissions["android.permission.READ_MEDIA_VISUAL_USER_SELECTED"] = True

        permissions.update(app.permission)
        features.update(getattr(app, "feature", {}))

        return {
            "permissions": permissions,
            "features": features,
        }

    def get_installed_ndk_version(self):
        """Get the installed NDK version from Briefcase's AndroidSDK.
        
        Returns the first available NDK version found in the SDK.
        Raises BriefcaseCommandError if no NDK is found.
        """
        ndk_path = self.tools.android_sdk.root_path / "ndk"
        
        if not ndk_path.exists():
            raise BriefcaseCommandError(
                f"""
No Android NDK found in {ndk_path}.

The Python-for-Android backend requires the Android NDK to be installed.
You can install it using:

1. Android Studio SDK Manager:
   - Open Android Studio
   - Go to Tools > SDK Manager > SDK Tools
   - Check "NDK (Side by side)" and install

2. Command line:
   - {self.tools.android_sdk.sdkmanager_path} "ndk;{DEFAULT_NDK_VERSION}"

3. Let Briefcase install it:
   - Run 'briefcase android create' which will prompt for NDK installation

After installation, the NDK should be available at:
{ndk_path}/{{version}}/
"""
            )
        
        versions = []
        for ndk_dir in ndk_path.iterdir():
            if ndk_dir.is_dir() and ndk_dir.name[0].isdigit():
                versions.append(ndk_dir.name)
        
        if not versions:
            raise BriefcaseCommandError(
                f"""
No NDK versions found in {ndk_path}.

The directory exists but contains no NDK installations.
Install an NDK version using:

1. Android Studio SDK Manager (recommended)
2. Command line: {self.tools.android_sdk.sdkmanager_path} "ndk;{DEFAULT_NDK_VERSION}"

After installation, the NDK should be available at:
{ndk_path}/{{version}}/
"""
            )
        
        versions.sort(key=lambda v: tuple(map(int, v.split('.'))))
        selected_version = versions[-1]
        
        self.tools.console.info(
            f"Using NDK version {selected_version} from {ndk_path / selected_version}"
        )
        
        return selected_version

    def _build_apk(self, app: AppConfig, release_mode: bool = False):
        """Build the APK for the given app."""
        
        args = ["--private", self.bundle_path(app) / "src"]
        
        # Use standard app configuration
        args.extend(["--package", app.bundle])
        args.extend(["--name", app.formal_name])
        args.extend(["--version", app.version])
        
        # TODO: Add requirements handling - for now let P4A use defaults
            
        if release_mode:
            args.append("--release")
        else:
            args.append("--debug")
        
        permissions = self._x_permissions(app)
        
        if permissions:
            for permission, enabled in permissions.items():
                if enabled:
                    args.extend(["--permission", permission])
        
        self.run_p4a(app, ["apk"] + args)
        
        built_apk = self.bundle_path(app) / f"{app.formal_name}-debug.apk"
        expected_apk = self.binary_path(app)
        
        if built_apk.exists():
            built_apk.rename(expected_apk)
        else:
            alternative_paths = [
                self.bundle_path(app) / f"{app.app_name}-debug.apk",
                self.bundle_path(app) / f"{app.module_name}-debug.apk",
                self.bundle_path(app) / "dist" / f"{app.formal_name}-debug.apk",
            ]
            
            for alt_path in alternative_paths:
                if alt_path.exists():
                    alt_path.rename(expected_apk)
                    break
            else:
                raise BriefcaseCommandError(
                    f"Unable to find the APK generated by P4A at {built_apk}"
                )


class P4ACreateCommand(P4AMixin, CreateCommand):
    """A command to create a new Python-for-Android project."""

    description = "Create and populate a new Android project using python-for-android."
    hidden_app_properties = {"permission", "feature"}

    @property
    def app_template_url(self) -> str:
        return "https://github.com/pyCino/briefcase-p4a-template.git"

    def output_format_template_context(self, app: AppConfig):
        """Additional template context for the P4A output format."""
        x_permissions = self._x_permissions(app)
        
        python_version = sys.version_info
        is_python_313_plus = python_version >= (3, 13)
        
        return {
            **super().output_format_template_context(app),
            **self.permissions_context(app, x_permissions),
            "pyjnius_requirement": (
                "git+https://github.com/kivy/pyjnius.git" 
                if is_python_313_plus 
                else "pyjnius>=1.4.1"
            )
        }

    def generate_app_template(self, app: AppConfig):
        """Generate the application template."""
        super().generate_app_template(app)


class P4ABuildCommand(P4AMixin, BuildCommand):
    """Build an Android APK using Python-for-Android."""
    
    description = "Build an Android APK using Python-for-Android."

    def build_app(self, app: AppConfig, test_mode: bool, **kwargs):
        """Build an application.

        :param app: The application to build
        :param test_mode: Should the app be updated in test mode? (default: False)
        """
        self._build_apk(app, release_mode=False)


class P4ARunCommand(P4AMixin, RunCommand):
    description = "Run an Android APK built with Python-for-Android on a device."

    def verify_tools(self):
        """Verify that the Android APK tools in `briefcase` will operate on this system,
        downloading tools as needed."""
        super().verify_tools()
        self.tools.android_sdk.verify_adb()

    def add_options(self, parser):
        """Add command-line options for the run command."""
        parser.add_argument(
            "--device",
            dest="device_or_avd",
            help="The device or AVD to run the app on",
        )
        parser.add_argument(
            "--emulator-args",
            dest="extra_emulator_args",
            help="Additional arguments to pass to the emulator",
        )
        parser.add_argument(
            "--shutdown-on-exit",
            dest="shutdown_on_exit",
            action="store_true",
            help="Shutdown the emulator when the app exits",
        )

    def run_app(
        self,
        app: AppConfig,
        test_mode: bool,
        passthrough: list[str],
        device_or_avd=None,
        extra_emulator_args=None,
        shutdown_on_exit=False,
        **kwargs,
    ):
        """Run the app on device or emulator."""
        
        if not self.binary_path(app).exists():
            raise BriefcaseCommandError(
                f"Application {app.app_name!r} has not been built. "
                f"Run `briefcase build` first."
            )
        
        self.tools.subprocess.run(
            [
                self.tools.android_sdk.adb_path,
                "install",
                "-r",
                self.binary_path(app),
            ],
            check=True,
        )
        
        activity = app.android_activity or "org.kivy.android.PythonActivity"
        
        self.tools.subprocess.run(
            [
                self.tools.android_sdk.adb_path,
                "shell",
                "am",
                "start",
                "-n",
                f"{app.bundle}/{activity}",
            ],
            check=True,
        )


class P4APackageCommand(P4AMixin, PackageCommand):
    """Create an Android APK in release mode using Python-for-Android."""
    
    description = "Create an Android APK in release mode using Python-for-Android."

    def package_app(self, app: AppConfig, **kwargs):
        """Package the application.

        :param app: The application to package
        """
        self._build_apk(app, release_mode=True)


class P4APublishCommand(P4AMixin, PublishCommand):
    description = "Publish an Android APK built with Python-for-Android."

    def publish_app(self, app: AppConfig, **kwargs):
        """Publish the app to the distribution directory."""
        distribution_file = self.distribution_path(app)
        
        os.makedirs(distribution_file.parent, exist_ok=True)
        
        with open(self.binary_path(app), "rb") as source:
            with open(distribution_file, "wb") as target:
                target.write(source.read())


class P4AUpdateCommand(P4ACreateCommand, UpdateCommand):
    """Update an existing Android P4A project."""
    
    description = "Update an existing Android P4A project."

    def update_app(self, app: AppConfig, test_mode: bool, **kwargs):
        """Update an existing Android P4A project."""
        self.generate_app_template(app)


class P4AOpenCommand(P4AMixin, OpenCommand):
    """Open the folder for an existing Android P4A project."""
    
    description = "Open the folder for an existing Android P4A project."

    def open_app(self, app: AppConfig, **kwargs):
        """Open the project folder for the application.

        :param app: The application to open
        """
        project_path = self.bundle_path(app)
        
        if not project_path.exists():
            raise BriefcaseCommandError(
                f"Project for {app.app_name} does not exist. "
                "Run 'briefcase create' first to create the project."
            )
        
        self.console.info(f"Opening project folder: {project_path}", prefix=app.app_name)
        
        self.tools.subprocess.run(
            self.tools.file_manager_open_command + [str(project_path)],
            check=True,
        )


# Export the command classes
create = P4ACreateCommand
update = P4AUpdateCommand
open = P4AOpenCommand
build = P4ABuildCommand
run = P4ARunCommand
package = P4APackageCommand
publish = P4APublishCommand