@echo off
:: SecRandom 移除保活守护批处理脚本
:: 此脚本用于移除Windows任务计划程序中的保活任务

echo 正在移除SecRandom保活守护...

:: 检查是否有管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已获取管理员权限，继续操作...
) else (
    echo 需要管理员权限来移除任务计划程序。
    echo 请右键点击此脚本，选择"以管理员身份运行"。
    pause
    exit /b 1
)

:: 创建PowerShell脚本
echo Set-ExecutionPolicy RemoteSigned -Scope Process -Force > "%TEMP%\remove_keep_alive.ps1"
echo $taskName = "SecRandomKeepAlive" >> "%TEMP%\remove_keep_alive.ps1"
echo. >> "%TEMP%\remove_keep_alive.ps1"
echo # 检查任务是否存在 >> "%TEMP%\remove_keep_alive.ps1"
echo $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue >> "%TEMP%\remove_keep_alive.ps1"
echo. >> "%TEMP%\remove_keep_alive.ps1"
echo if ($taskExists) { >> "%TEMP%\remove_keep_alive.ps1"
echo     Write-Host "找到保活任务，正在移除..." >> "%TEMP%\remove_keep_alive.ps1"
echo     Unregister-ScheduledTask -TaskName $taskName -Confirm:$false >> "%TEMP%\remove_keep_alive.ps1"
echo     Write-Host "保活任务已成功移除！" >> "%TEMP%\remove_keep_alive.ps1"
echo } else { >> "%TEMP%\remove_keep_alive.ps1"
echo     Write-Host "未找到保活任务，可能已经被移除或从未设置。" >> "%TEMP%\remove_keep_alive.ps1"
echo } >> "%TEMP%\remove_keep_alive.ps1"

:: 执行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "%TEMP%\remove_keep_alive.ps1"

:: 清理临时文件
del "%TEMP%\remove_keep_alive.ps1"

echo.
echo SecRandom保活守护移除操作完成！
echo.
pause