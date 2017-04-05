#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

import sys
import os
import os.path
import glob
unicode = type(u"")

top_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(top_dir, "Cheetah", "Version.py")) as f:
    class about: exec(f.read(), None)

try:
    # to avoid those bloody out-of-date manifests!!
    os.remove(os.path.join(top_dir, "MANIFEST"))
except:
    pass

if os.getenv("CHEETAH_INSTALL_WITHOUT_SETUPTOOLS"):
    raise SystemExit("'setuptools' is required to install this package. "
                     "Please see the README for details.")

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    raise SystemExit("'setuptools' is required to install this package. "
                     "Please see the README for details.")

from distutils.command.build_ext import build_ext
from distutils.command.install_data import install_data
from distutils.errors import (CCompilerError,
                              DistutilsExecError,
                              DistutilsPlatformError)

ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)
if sys.platform == "win32":
    # distutils.msvc9compiler can raise an IOError when failing to
    # find the compiler
    ext_errors += (IOError,)


class optional_build_ext(build_ext):
    """\
    A modified version of the distutils build_ext command that allows
    the building of extensions ti fail.
    """

    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError as exc:
            self._unavailable(exc)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except ext_errors as exc:
            self._unavailable(exc)

    def _unavailable(self, exc):
        print("One or more C extensions failed to build.")
        print("Details: %s" % exc)
        if os.environ.get("CHEETAH_C_EXTENSIONS_REQUIRED"):
            raise exc
        print("Performance enhancements will not be available.")


class mod_install_data(install_data):
    """\
    A modified version of the disutils install_data command that allows data
    files to be included directly in the installed Python package tree.
    """

    def finalize_options(self):

        if self.install_dir is None:
            installobj = self.distribution.get_command_obj("install")
            # self.install_dir = installobj.install_platlib
            self.install_dir = installobj.install_lib
        install_data.finalize_options(self)

    def run(self):

        if not self.dry_run:
            self.mkpath(self.install_dir)

        data_files = self.get_inputs()
        for entry in data_files:
            if not isinstance(entry, (str, unicode)):
                raise ValueError('The entries in "data_files" must be strings')

            entry = os.sep.join(entry.split('/'))
            # entry is a filename or glob pattern
            if entry.startswith('recursive:'):
                entry = entry[len('recursive:'):]
                dir = entry.split()[0]
                globPatterns = entry.split()[1:]
                # imports from Cheetah ...
                from Cheetah.FileUtils import findFiles
                filenames = findFiles(dir, globPatterns)
            else:
                filenames = glob.glob(entry)

            for filename in filenames:
                # generate the dstPath from the filename
                # - deal with 'package_dir' translations
                topDir, subPath = (filename.split(os.sep)[0],
                                   os.sep.join(filename.split(os.sep)[1:]))

                package_dirDict = self.distribution.package_dir
                if package_dirDict:
                    packageDir = topDir
                    for key, val in package_dirDict.items():
                        if val == topDir:
                            packageDir = key
                            break
                else:
                    packageDir = topDir
                dstPath = os.path.join(self.install_dir, packageDir, subPath)

                # add the file to the list of outfiles
                dstdir = os.path.split(dstPath)[0]
                if not self.dry_run:
                    self.mkpath(dstdir)
                    outfile = self.copy_file(filename, dstPath)[0]
                else:
                    outfile = dstPath
                self.outfiles.append(outfile)


class SetupConfig(object):

    version = about.Version

    dev_tag = ""
    download_url = "https://pypi.python.org/pypi/%s/%s%s" % ("Cheetah3",
                                                             version, dev_tag)
    del dev_tag

    ext_modules = [
        Extension("Cheetah._namemapper",
                  [os.path.join("Cheetah", "c", "_namemapper.c")]),
    ]

    # Add setup extensions
    cmdclass = {
        "build_ext": optional_build_ext,
        "install_data": mod_install_data,
    }

    # Data Files and Scripts #

    data_files = [
        "recursive: Cheetah *.tmpl *.txt *.rst LICENSE TODO"
    ]

    if sys.platform == "win32":
        # use 'entry_points' instead of 'scripts'
        entry_points = {
            "console_scripts": [
                "cheetah = Cheetah.CheetahWrapper:_cheetah",
                "cheetah-compile = Cheetah.CheetahWrapper:_cheetah_compile",
                "cheetah-analyze = Cheetah.DirectiveAnalyzer:main",
            ]
        }
    else:
        scripts = (
            "bin/cheetah",
            "bin/cheetah-compile",
            "bin/cheetah-analyze",
        )

    python_requires = ">=2.7.0,!=3.0.*,!=3.1.*,!=3.2.*"
    test_suite = "Cheetah.Tests.Test.test_suite"


def run_setup(configurations):
    """\
    Run distutils setup.

    The parameters passed to setup() are extracted from the list of modules,
    classes or instances given in configurations.

    Names with leading underscore are removed from the parameters.
    Parameters which are not strings, lists, tuples, or dicts are removed as
    well.  Configurations which occur later in the configurations list
    override settings of configurations earlier in the list.

    """

    # Build parameter dictionary
    kws = {}
    for configuration in configurations:
        kws.update(vars(configuration))
    for name, value in list(kws.items()):
        if (name[:1] == "_" or
            not isinstance(value, (str, unicode, list, tuple, dict, int))):
            kws.pop(name, None)

    # Invoke distutils setup
    setup(**kws)


configurations = (SetupConfig,)
run_setup(configurations)
