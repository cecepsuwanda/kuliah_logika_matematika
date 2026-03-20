@echo off
setlocal

set "ROOT_DIR=%~dp0..\..\"
set "OUTPUT_DIR=%ROOT_DIR%output"
set "SOURCE_DIR=%~dp0"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%" 2>nul

echo ============================================================
echo Compiling Main Document
echo ============================================================

pushd "%SOURCE_DIR%"

REM Check for latexmk AND perl
where latexmk >nul 2>nul
if errorlevel 1 (
    echo Latexmk not found. Using pdflatex loop...
    goto :pdflatex_loop
) else (
    where perl >nul 2>nul
    if errorlevel 1 (
        echo Latexmk found but Perl is missing. Skipping latexmk.
        goto :pdflatex_loop
    ) else (
        echo Latexmk and Perl found. Using latexmk...
        latexmk -pdf -interaction=nonstopmode -output-directory="%OUTPUT_DIR%" "main.tex"
        if errorlevel 1 (
            echo Latexmk failed. Falling back to pdflatex loop...
            goto :pdflatex_loop
        ) else (
            goto :success
        )
    )
)

:pdflatex_loop
echo Running Stage 1: pdflatex...
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="%OUTPUT_DIR%" "main.tex"
if errorlevel 1 goto :failed

echo Running Stage 2: bibtex...
bibtex "%OUTPUT_DIR%\main"

echo Running Stage 3: pdflatex...
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="%OUTPUT_DIR%" "main.tex"

echo Running Stage 4: pdflatex...
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="%OUTPUT_DIR%" "main.tex"
if errorlevel 1 goto :failed

:success
popd

echo Cleaning up intermediate files...
call :cleanup "%OUTPUT_DIR%"
call :cleanup "%SOURCE_DIR%"

echo.
echo Operation Completed.
echo Final PDF: %OUTPUT_DIR%\main.pdf
goto :end

:failed
popd
echo.
echo ERROR: Compilation failed.
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