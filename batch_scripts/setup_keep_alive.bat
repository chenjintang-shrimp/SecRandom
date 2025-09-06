@echo off
:: SecRandom 保活守护批处理脚本
:: 此脚本用于设置Windows任务计划程序，实现无需Python环境的保活功能

echo 正在配置SecRandom保活守护...

:: 检查是否有管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已获取管理员权限，继续配置...
) else (
    echo 需要管理员权限来设置任务计划程序。
    echo 请右键点击此脚本，选择"以管理员身份运行"。
    pause
    exit /b 1
)

:: 获取当前脚本所在目录
set SCRIPT_DIR=%~dp0
set APP_EXE=%SCRIPT_DIR%SecRandom.exe

:: 检查应用程序是否存在
if not exist "%APP_EXE%" (
    echo 错误: 未找到SecRandom.exe文件。
    echo 请确保此脚本与SecRandom.exe在同一目录下。
    pause
    exit /b 1
)

:: 创建PowerShell脚本
echo Set-ExecutionPolicy RemoteSigned -Scope Process -Force > "%TEMP%\setup_keep_alive.ps1"
echo $taskName = "SecRandomKeepAlive" >> "%TEMP%\setup_keep_alive.ps1"
echo $appPath = "%APP_EXE%" >> "%TEMP%\setup_keep_alive.ps1"
echo $scriptDir = "%SCRIPT_DIR%" >> "%TEMP%\setup_keep_alive.ps1"
echo. >> "%TEMP%\setup_keep_alive.ps1"
echo # 检查任务是否已存在 >> "%TEMP%\setup_keep_alive.ps1"
echo $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue >> "%TEMP%\setup_keep_alive.ps1"
echo. >> "%TEMP%\setup_keep_alive.ps1"
echo if ($taskExists) { >> "%TEMP%\setup_keep_alive.ps1"
echo     Write-Host "任务已存在，正在删除旧任务..." >> "%TEMP%\setup_keep_alive.ps1"
echo     Unregister-ScheduledTask -TaskName $taskName -Confirm:$false >> "%TEMP%\setup_keep_alive.ps1"
echo } >> "%TEMP%\setup_keep_alive.ps1"
echo. >> "%TEMP%\setup_keep_alive.ps1"
echo # 创建新的任务 >> "%TEMP%\setup_keep_alive.ps1"
echo Write-Host "正在创建保活任务..." >> "%TEMP%\setup_keep_alive.ps1"
echo $action = New-ScheduledTaskAction -Execute "$appPath" >> "%TEMP%\setup_keep_alive.ps1"
echo $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650) >> "%TEMP%\setup_keep_alive.ps1"
echo $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -DontStopOnIdleEnd >> "%TEMP%\setup_keep_alive.ps1"
echo $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount >> "%TEMP%\setup_keep_alive.ps1"
echo. >> "%TEMP%\setup_keep_alive.ps1"
echo Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "SecRandom保活守护任务" >> "%TEMP%\setup_keep_alive.ps1"
echo. >> "%TEMP%\setup_keep_alive.ps1"
echo Write-Host "保活任务创建成功！" >> "%TEMP%\setup_keep_alive.ps1"
echo Write-Host "任务名称: $taskName" >> "%TEMP%\setup_keep_alive.ps1"
echo Write-Host "执行间隔: 每5分钟" >> "%TEMP%\setup_keep_alive.ps1"
echo Write-Host "应用程序路径: $appPath" >> "%TEMP%\setup_keep_alive.ps1"

:: 执行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "%TEMP%\setup_keep_alive.ps1"

:: 清理临时文件
del "%TEMP%\setup_keep_alive.ps1"

echo.
echo SecRandom保活守护配置完成！
echo 系统将每5分钟检查一次SecRandom是否在运行，如果未运行则自动启动。
echo.
pause