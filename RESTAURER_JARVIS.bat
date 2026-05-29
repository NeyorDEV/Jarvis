@echo off
color 0C
echo ===================================================
echo        J.A.R.V.I.S - PROTOCOLE DE RESTAURATION
echo ===================================================
echo.
echo Restauration de la codebase a son dernier etat stable...
echo.
git reset --hard HEAD
git clean -fd
echo.
echo ===================================================
echo Systeme restaure avec succes.
echo ===================================================
echo.
pause
