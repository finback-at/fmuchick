@echo off 
rem ------------------------------------------------------------
rem This batch builds an FMU of the FMU SDK
rem Usage: build_fmu (me|cs) <fmu_dir_name> 
rem Copyright QTronic GmbH. All rights reserved
rem ------------------------------------------------------------
rem clean up
if exist *.fmu del /Q *.fmu
if exist fmu\source\* del /Q fmu\sources\*
if exist fmu\binaries\win32\* del /Q fmu\binaries\win32\*
if exist fmu\binaries\win64\* del /Q fmu\binaries\win64\*
if exist fmu\resources\* del /Q fmu\resources\*

rem build dll for win32
if defined VS110COMNTOOLS (call "%VS110COMNTOOLS%\vsvars32.bat") else ^
if defined VS100COMNTOOLS (call "%VS100COMNTOOLS%\vsvars32.bat") else ^
if defined VS90COMNTOOLS (call "%VS90COMNTOOLS%\vsvars32.bat") else ^
if defined VS80COMNTOOLS (call "%VS80COMNTOOLS%\vsvars32.bat") else ^
goto noCompiler

if exist *.dll del /Q *.dll
if exist fmu\sources\* del /Q fmu\sources\*
copy src\fmuchick.c fmu\sources\%1.c
copy src\fmuTemplate_.c fmu\sources\
copy src\fmuTemplate.h fmu\sources\
copy model.h fmu\sources\
copy variables.c fmu\sources\
copy fmuchick.cfg fmu\resources\

cl /LD /nologo /DFMI_COSIMULATION fmu\sources\%1.c ws2_32.lib /I.\include
if not exist %1.dll goto compileError
echo "32 bit DLL is generated successfully!"

set BIN_DIR=fmu\binaries\win32
move /Y %1.dll %BIN_DIR%
del %1.exp %1.lib %1.obj

rem build dll for win64
if defined VS110COMNTOOLS (call "%VS110COMNTOOLS%\..\..\VC\vcvarsall.bat" x86_amd64) else ^
if defined VS100COMNTOOLS (call "%VS100COMNTOOLS%\..\..\VC\vcvarsall.bat" x86_amd64) else ^
if defined VS90COMNTOOLS (call "%VS90COMNTOOLS%\..\..\VC\vcvarsall.bat" x86_amd64) else ^
if defined VS80COMNTOOLS (call "%VS80COMNTOOLS%\..\..\VC\vcvarsall.bat" x86_amd64) else ^
goto noCompiler

cl /LD /nologo /DFMI_COSIMULATION fmu\sources\%1.c ws2_32.lib /I.\include
if not exist %1.dll goto compileError
echo "64 bit DLL is generated successfully!"

set BIN_DIR=fmu\binaries\win64
move /Y %1.dll %BIN_DIR%
del %1.exp %1.lib %1.obj
goto cleanup

:noCompiler
echo No Microsoft Visual C compiler found
got cleanup

:compileError
echo build of %1 failed

:cleanup
del variables.c
del model.h
