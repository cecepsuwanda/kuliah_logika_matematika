@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
set "OUTPUT_DIR=%ROOT_DIR%\output"
set "SUCCESS_COUNT=0"
set "FAIL_COUNT=0"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ============================================================
echo Compiling PPT Chapter Files
echo ============================================================

pushd "%SCRIPT_DIR%"

for %%F in (ppt_bab_*.tex) do (
    set "FILE_NAME=%%~nF"

    echo.
    echo ------------------------------------------------------------
    echo Compiling !FILE_NAME!...
    echo ------------------------------------------------------------

    pdflatex -interaction=nonstopmode -halt-on-error "%%F"
    if !errorlevel! equ 0 (
        pdflatex -interaction=nonstopmode -halt-on-error "%%F"
        if !errorlevel! equ 0 (
            if exist "!FILE_NAME!.pdf" (
                move /y "!FILE_NAME!.pdf" "%OUTPUT_DIR%\!FILE_NAME!.pdf" >nul
                set /a SUCCESS_COUNT+=1
                echo SUCCESS: !FILE_NAME!.pdf moved to output.
            ) else (
                set /a FAIL_COUNT+=1
                echo ERROR: !FILE_NAME!.pdf not found after compile.
            )
        ) else (
            set /a FAIL_COUNT+=1
            echo ERROR: second pdflatex pass failed for !FILE_NAME!.
        )
    ) else (
        set /a FAIL_COUNT+=1
        echo ERROR: first pdflatex pass failed for !FILE_NAME!.
    )

    if exist "!FILE_NAME!.log" (
        move /y "!FILE_NAME!.log" "%OUTPUT_DIR%\!FILE_NAME!.log" >nul
        echo Log: !FILE_NAME!.log moved to output.
    )
)

popd

echo.
echo Cleaning up intermediate files...
call :cleanup "%SCRIPT_DIR%"

echo.
echo ============================================================
echo Compilation Summary
echo ============================================================
echo Output Folder: %OUTPUT_DIR%
echo Success: %SUCCESS_COUNT%
echo Failed : %FAIL_COUNT%

goto :end

:cleanup
set "TARGET_FOLDER=%~1"
pushd "%TARGET_FOLDER%"
for %%E in (aux out toc nav snm vrb fls fdb_latexmk synctex.gz) do (
    del /s /q "*.%%E" 2>nul
)
popd
exit /b 0

:end
echo.
pause
exit /b 0
