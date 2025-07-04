"""
Custom pyjnius recipe for Python 3.13+ compatibility.

This recipe uses the stable pyjnius 1.6.1 release with official patches 
applied to fix Python 3.13 compatibility issues (specifically the 'long' 
type removal). This approach ensures stability while maintaining compatibility.

The patches are based on the official pyjnius GitHub commit:
https://github.com/kivy/pyjnius/commit/c7ae8b85cc315d5283f77e930fa989b72b59c902
"""

import sys
from pythonforandroid.recipe import PythonRecipe


class PyjniusRecipe(PythonRecipe):
    """Pyjnius recipe with Python 3.13 compatibility patches."""
    
    version = '1.6.1'  # Latest stable release
    url = 'https://pypi.python.org/packages/source/p/pyjnius/pyjnius-{version}.tar.gz'
    
    depends = ['python3', 'genericndkbuild']
    site_packages_name = 'pyjnius'
    
    def __init__(self):
        super().__init__()
        # Only apply Python 3.13 compatibility patches when needed
        if sys.version_info >= (3, 13):
            self.patches = ['python313_long_fix.patch']
        else:
            self.patches = []
    
    def should_build(self, arch):
        """Always build to ensure consistent patched version."""
        return super().should_build(arch)


recipe = PyjniusRecipe() 