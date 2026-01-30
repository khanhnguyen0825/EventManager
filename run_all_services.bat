@echo off
title SOA Multi-Service Runner

:: Vào thư mục gốc chứa tất cả service
cd /d "%~dp0"

:: Chạy auth_service (nếu có)
start cmd /k "cd auth_service && python run.py"

:: Chạy customer_service
start cmd /k "cd customer_service && python run.py"

:: Chạy event_service
start cmd /k "cd event_service && python run.py"

:: Chạy report_service
start cmd /k "cd report_service && python run.py"

:: Chạy public_service
start cmd /k "cd public_service && python run.py"

:: Chạy place_service
start cmd /k "cd place_service && python run.py"

:: Tất cả service đã được bật
echo All services started.
pause
