#!/usr/bin/python -OO
import os
import platform
from subprocess import call

svn_url = 'http://decada.googlecode.com/svn/trunk/PySampo/'
exp_dirs = ['docs', 'ekeys', 'locale', 'pixmaps', 'plugins', 'profiles', 'styles', 'tests']

call(["python", "-OO", "cx_setup.py", "build"])
py_ver = platform.python_version_tuple()
lib_path = 'exe.' + platform.system().lower() + '-' + platform.machine() + '-' + py_ver[0] + '.' + py_ver[1]
print lib_path

for dn in exp_dirs:
	call(["svn", "export", "--force", svn_url + dn, os.path.join('build', lib_path, dn)])
#svn export http://decada.googlecode.com/svn/trunk/PySampo/docs 
call(['cp', 'DefaultShape.py', os.path.join('build', lib_path)])