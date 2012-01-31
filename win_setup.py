# A setup script showing advanced features.
#
# Note that for the NT service to build correctly, you need at least
# win32all build 161, for the COM samples, you need build 163.
# Requires wxPython, and Tim Golden's WMI module.
from distutils.core import setup
import py2exe
import sys
import os
import zipextimporter
zipextimporter.install()

desc_txt = "Sampo - the Data Manipulation Framework"
vars_txt = "0.8.0"

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = vars_txt
        self.company_name = "Lab18.net"
        self.copyright = "(c) 2011 by Lab18.net"
        self.name = desc_txt

sampo = Target(
    # used for the versioninfo resource
    description = desc_txt,
    # what to build
    script = "SamPy.py",
    icon_resources = [(1, "pixmaps\\sampo.ico")],
    dest_base = "Sampo"
    )

print os.path.dirname(__file__)
sys.path.append(os.path.join(os.path.dirname(__file__), "Editra", "src"))
setup(
    options = {"py2exe": {
                    "compressed": 1,
                    "optimize": 2,
                    "includes": ["Editra.src.generator",
                                 "Editra.src.ed_log",
                                 "Editra.src.ed_bookmark",
                                 "Editra.src.syntax._python",
                                 "Editra.src.syntax._xml",
                                 "Editra.src.gentag.parselib",
                                 "Editra.src.gentag.pytags",
                                 "Editra.src.gentag.xmltags"],
                    "packages": ["wx.wizard",
                                 "Editra.src.extern.pygments",
                                 "socket",
                                 "htmllib",
                                 "htmlentitydefs",
                                 "cgi",
                                 "mercurial",
                                 "hglib",
                                 "urllib",
                                 "urllib2",
                                 "hashlib",
                                 "hmac",
                                 "md5",
                                 "sha",
                                 "json",
                                 "base64"]
                    }
              },
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = vars_txt,
    description = vars_txt,
    name = "Sampo",

    # targets to build
    zipfile = "libs\\package",
    windows = [sampo],
    )
