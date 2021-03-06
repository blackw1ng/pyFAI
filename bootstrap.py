#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Bootstrap helps you to test pyFAI scipts without installing them 
by patching your PYTONPATH on the fly

example: ./bootstrap.py pyFAI-integrate test/testimages/Pilatus1M.edf

"""

__authors__ = ["Frédéric-Emmanuel Picca", "Jérôme Kieffer"]
__contact__ = "jerome.kieffer@esrf.eu"
__license__ = "GPLv3+"
__date__ = "2013-07-15"

import sys
import os
import shutil
import distutils.util
import subprocess

def _copy(infile, outfile):
    "link or copy file according to the OS. Nota those are HARD_LINKS"
    if "link" in dir(os):
        os.link(infile, outfile)
    else:
        shutil.copy(infile, outfile)

def _distutils_dir_name(dname="lib"):
    """
    Returns the name of a distutils build directory
    """
    platform = distutils.util.get_platform()
    architecture = "%s.%s-%i.%i" % (dname, platform,
                                    sys.version_info[0], sys.version_info[1])
    return architecture


def _distutils_scripts_name():
    """Return the name of the distrutils scripts sirectory"""
    f = "scripts-{version[0]}.{version[1]}"
    return f.format(version=sys.version_info)


def _get_available_scripts(path):
    res = []
    try:
        res = " ".join([s.rstrip('.py') for s in os.listdir(path)])
    except OSError:
        res = ["no script available, did you ran "
               "'python setup.py build' before bootstrapping ?"]
    return res

def _copy_files(source, dest, extn):
    """
    copy all files with a given extension from source to destination 
    """
    full_src = os.path.join(os.path.dirname(__file__), source)
    for clf in os.listdir(full_src):
        if clf.endswith(extn) and clf not in os.listdir(dest):
            _copy(os.path.join(full_src, clf), os.path.join(dest, clf))


SCRIPTSPATH = os.path.join(os.path.dirname(__file__),
                           'build', _distutils_scripts_name())
LIBPATH = os.path.join(os.path.dirname(__file__),
                       'build', _distutils_dir_name('lib'))

if (not os.path.isdir(SCRIPTSPATH)) or (not os.path.isdir(LIBPATH)):
    build = subprocess.Popen([sys.executable, "setup.py", "build"],
                     shell=False, cwd=os.path.dirname(__file__))
    print("Build process ended with rc= %s" % build.wait())
_copy_files("openCL", os.path.join(LIBPATH, "pyFAI"), ".cl")
_copy_files("gui", os.path.join(LIBPATH, "pyFAI"), ".ui")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ./bootstrap.py <script>\n")
        print("Available scripts : %s\n" %
              _get_available_scripts(SCRIPTSPATH))
        sys.exit(1)

    print("Executing %s from source checkout" % (sys.argv[1]))

    sys.path.insert(0, LIBPATH)
    print("01. Patched sys.path with %s" % LIBPATH)

    sys.path.insert(0, SCRIPTSPATH)
    print("02. Patched sys.path with %s" % SCRIPTSPATH)

    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    print("03. patch the sys.argv : ", sys.argv)

    print("04. Executing %s.main()" % (script,))
    execfile(os.path.join(SCRIPTSPATH, script))
