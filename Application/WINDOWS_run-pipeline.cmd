@echo off
REM INFO -----------------------------------------------------------
echo ANALYSIS TYPE
echo  - For short read assembly, input: '1' or 'short'
echo  - For long read assembly, input: '2' or 'long'
echo  - For hybrid assembly, input: '3' or 'hybrid'

REM ASK ANALYSIS TYPE-----------------------------------------------
set /p analysis="Please provide Analysis type here: " && echo.
echo %analysis%
REM ----------------------------------------------------------------

REM SHORT READ WRAPPER----------------------------------------------
IF  %analysis%==1 (
    echo [SHORT] Starting Short reads assembly
    echo.
    python.exe ./Scripts/Short_read/short_read_assembly.py
)
IF %analysis%==short (
    echo [SHORT] Starting Short reads assembly
    echo.
    python.exe ./Scripts/Short_read/short_read_assembly.py
)
REM LONG READ ASSEMBLY-----------------------------------------------
IF  %analysis%==2 (
    echo [LONG] Starting Long reads assembly
    echo.
    python.exe ./Scripts/Long_read/long_read_assembly.py
)
IF %analysis%==long (
    echo [LONG] Starting Long reads assembly
    echo.
    python.exe ./Scripts/Long_read/long_read_assembly.py
)
REM HYBRID ASSEMBLY---------------------------------------------------
IF  %analysis%==3 (
    echo [HYBRID] Starting Hybrid assembly
    echo.
    python.exe ./Scripts/Hybrid/hybrid_assembly.py
)
IF %analysis%==hybrid (
    echo [HYBRID] Starting Hybrid assembly
    echo.
    python.exe ./Scripts/Hybrid/hybrid_assembly.py
)
REM ------------------------------------------------------------------

PAUSE