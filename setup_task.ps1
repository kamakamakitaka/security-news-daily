$projectPath = "C:\Users\mstk\security-news-analyzer"
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $projectPath "src\main.py"
$taskName = "SecurityNewsAnalyzer"

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Daily -At "21:35"
$settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId (whoami) -LogonType Interactive -RunLevel Highest

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task"
}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily security news analysis" -Force
Write-Host "Task registered successfully!"
Write-Host ""
Write-Host "Settings:"
Write-Host "  - Daily execution at 21:35"
Write-Host "  - StartWhenAvailable: PC OFF時は起動後に実行"
Write-Host "  - AllowStartIfOnBatteries: バッテリー電源でも実行"
