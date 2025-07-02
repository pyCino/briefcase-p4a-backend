from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import will_build
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    version = 'master'
    # Use the zip archive of the master branch to get the latest code
    url = 'https://github.com/kivy/pyjnius/archive/refs/heads/master.zip'
    name = 'pyjnius'
    depends = [('genericndkbuild', 'sdl2'), 'six']
    site_packages_name = 'jnius'

    patches = [('genericndkbuild_jnienv_getter.patch', will_build('genericndkbuild'))]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        return env

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)
        info('pyjnius postbuild_arch completed for arch {}'.format(arch.arch))


recipe = PyjniusRecipe() 