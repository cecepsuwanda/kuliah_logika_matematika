@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0..\..\"
set "OUTPUT_DIR=%ROOT_DIR%output"
set "SOURCE_DIR=%~dp0"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ============================================================
echo Compiling Individual Chapters
echo ============================================================

pushd "%SOURCE_DIR%\bab"

for %%F in (bab-*.tex) do (
    set "FILE_NAME=%%~nF"
    echo.
    echo ------------------------------------------------------------
    echo Compiling !FILE_NAME!...
    echo ------------------------------------------------------------
    
    pdflatex -interaction=nonstopmode -halt-on-error "%%F"
    if !errorlevel! equ 0 (
        bibtex "!FILE_NAME!"
        pdflatex -interaction=nonstopmode -halt-on-error "%%F"
        pdflatex -interaction=nonstopmode -halt-on-error "%%F"
        
        if exist "!FILE_NAME!.pdf" (
            echo Moving !FILE_NAME!.pdf to output...
            move /y "!FILE_NAME!.pdf" "%OUTPUT_DIR%\!FILE_NAME!.pdf"
        )
    ) else (
        echo ERROR compiling !FILE_NAME!.
    )
)

popd

echo Cleaning up intermediate files...
call :cleanup "%SOURCE_DIR%"

echo.
echo Operation Completed. Check the output folder for PDFs.
goto :end

:cleanup
set "TARGET_FOLDER=%~1"
pushd "%TARGET_FOLDER%"
for %%E in (aux bbl blg bcf out toc lof lot fls fdb_latexmk nav snm vrb idx ilg ind acn acr alg glg glo gls ist xdy run.xml synctex pdfsync synctex.gz) do (
    del /s /q "*.%%E" 2>nul
)
popd
exit /b 0

:end
echo.
pause
exit /b 0
