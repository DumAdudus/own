$logFile = "C:\Windows\Setup\Scripts\qemu-ga.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

$exe = "qemu-ga-x86_64.msi"
Start-Process msiexec -ArgumentList '/i',$exe,'/passive','/norestart','/log C:\Windows\Setup\Scripts\ga.log' -Wait

Stop-Transcript