set PYTHON="c:\Python27\python.exe"
set SVN="c:\Program Files\TortoiseSVN\bin\TortoiseProc.exe"
set SVN_MODE="Tortoise"

%PYTHON% win_setup.py py2exe
copy DefaultShape.py dist\DefaultShape.py
if %SVN_MODE% == "Tortoise" (
  mkdir dist\docs
  xcopy docs dist\docs /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\ekeys
  xcopy ekeys dist\ekeys /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\locale
  xcopy locale dist\locale /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\pixmaps
  xcopy pixmaps dist\pixmaps /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\plugins
  xcopy plugins dist\plugins /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\profiles
  xcopy profiles dist\profiles /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\styles
  xcopy styles dist\styles /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
  mkdir dist\tests
  xcopy tests dist\tests /EXCLUDE:win_no_svn.txt /E /C /I /F /R /Y
)

del /Q build
