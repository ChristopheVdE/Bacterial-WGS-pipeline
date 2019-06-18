@echo off
REM INFO -----------------------------------------------------------
echo ANALYSIS TYPE
echo  - For short read assembly, input: '1' or 'short'
echo  - For long read assembly, input: '2' or 'long'
echo  - For hybrid assembly, input: '3' or 'hybrid'

REM ASK ANALYSIS TYPE-----------------------------------------------
set /p analysis="Please provide Analysis type here: " && echo.
REM ----------------------------------------------------------------

REM START CORRECT ASSEMBLY WRAPPER----------------------------------
python.exe run_assembly.py %analysis%
REM ----------------------------------------------------------------

PAUSE