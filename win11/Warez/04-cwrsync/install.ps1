$logFile = "C:\Windows\Setup\Scripts\openssh.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

app_ver = "6.3.1"
Copy-Item -Path "cwrsync_$app_ver" -Destination "$Env:Programfiles" -Recurse
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$Env:Programfiles\cwrsync_$app_ver\bin", "Machine")

Stop-Transcript