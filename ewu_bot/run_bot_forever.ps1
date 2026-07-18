$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logs = Join-Path $root "EWU_Data\Logs"
$stdout = Join-Path $logs "bot_stdout_current.log"
$stderr = Join-Path $logs "bot_stderr_current.log"
$watchdog = Join-Path $logs "bot_watchdog.log"

New-Item -ItemType Directory -Force -Path $logs | Out-Null
Set-Location $root

while ($true) {
    $started = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $watchdog -Encoding UTF8 -Value "$started starting bot.py"

    $process = Start-Process `
        -FilePath "py.exe" `
        -ArgumentList @("-3.12", "bot.py") `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru `
        -Wait
    $exitCode = $process.ExitCode

    $stopped = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -LiteralPath $watchdog -Encoding UTF8 -Value "$stopped bot.py stopped with exit code $exitCode; restarting in 10s"
    Start-Sleep -Seconds 10
}
