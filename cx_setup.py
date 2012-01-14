# A setup script showing advanced features.
#
# Note that for the NT service to build correctly, you need at least
# win32all build 161, for the COM samples, you need build 163.
# Requires wxPython, and Tim Golden's WMI module.
from cx_Freeze import setup, Executable
import sys
import os

desc_txt = "Sampo - the Data Manipulation Framework"
vars_txt = "0.8.0"

buildOptions = dict(
        namespace_packages = ['zope', "zc.lockfile", "BTrees.fsBTree", 'pkg_resources'],
        optimize = 2,
        compressed = 1,
        includes = ["Editra.src.generator",
                     "Editra.src.ed_log",
                     "Editra.src.ed_bookmark",
                     "Editra.src.syntax._python",
                     "Editra.src.syntax._xml",
                     "Editra.src.gentag.parselib",
                     "Editra.src.gentag.pytags",
                     "Editra.src.gentag.xmltags"],
        packages = ["wx.wizard",
                    "Editra.src.extern.pygments",
                    "socket",
                    "htmllib",
                    "htmlentitydefs",
                    "cgi",
                    "urllib",
                    "urllib2",
                    "hashlib",
                    "hmac",
                    "md5",
                    "sha",
                    "json",
                    "base64",
                    "Editra.src.extern.pygments"]
        )

print os.path.dirname(__file__)
sys.path.append(os.path.join(os.path.dirname(__file__), "Editra", "src"))
setup(
    version = vars_txt,
    description = desc_txt,
    name = "Decada",

    # targets to build
    options = dict(build_exe = buildOptions),
    executables = [Executable("Decada.py", targetName="Decada", shortcutName="decada", compress=1)]
    )
