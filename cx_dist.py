#!/usr/bin/python -OO
import os
import platform
from subprocess import call
import shutil

svn_url = 'http://decada.googlecode.com/svn/trunk/PySampo/'
exp_dirs = ['docs', 'ekeys', 'locale', 'pixmaps', 'plugins', 'profiles', 'styles', 'tests']

py_ver = platform.python_version_tuple()
lib_path = 'exe.' + platform.system().lower() + '-' + platform.machine() + '-' + py_ver[0] + '.' + py_ver[1]
print lib_path
if os.path.exists(os.path.join('build', lib_path)):
	shutil.rmtree(os.path.join('build', lib_path), True)

call(["python", "-OO", "cx_setup.py", "build"])

for dn in exp_dirs:
	shutil.copytree(dn, os.path.join('build', lib_path, dn))
call(['cp', 'DefaultShape.py', os.path.join('build', lib_path)])