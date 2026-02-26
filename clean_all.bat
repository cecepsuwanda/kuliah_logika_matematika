@echo off
echo ============================================================
echo Menghapus file hasil kompilasi LaTeX di seluruh codebase...
echo ============================================================

pushd "%~dp0"

echo Memproses folder dan subfolder...
del /s /q *.aux 2>nul
del /s /q *.bbl 2>nul
del /s /q *.blg 2>nul
del /s /q *.bcf 2>nul
del /s /q *.out 2>nul
del /s /q *.toc 2>nul
del /s /q *.lof 2>nul
del /s /q *.lot 2>nul
del /s /q *.fls 2>nul
del /s /q *.fdb_latexmk 2>nul
del /s /q *.nav 2>nul
del /s /q *.snm 2>nul
del /s /q *.vrb 2>nul
del /s /q *.idx 2>nul
del /s /q *.ilg 2>nul
del /s /q *.ind 2>nul
del /s /q *.acn 2>nul
del /s /q *.acr 2>nul
del /s /q *.alg 2>nul
del /s /q *.glg 2>nul
del /s /q *.glo 2>nul
del /s /q *.gls 2>nul
del /s /q *.ist 2>nul
del /s /q *.xdy 2>nul
del /s /q *.run.xml 2>nul
del /s /q *.synctex 2>nul
del /s /q *.synctex.gz 2>nul
del /s /q *.pdfsync 2>nul
del /s /q *.log 2>nul
del /s /q *.lol 2>nul
del /s /q *.pdf 2>nul

popd

echo.
echo Pembersihan selesai!
pause
