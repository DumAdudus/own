$logFile = "C:\Windows\Setup\Scripts\openssh.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service -Name sshd -StartupType 'Automatic'

# Set PowerShell as OpenSSH default shell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" `
                 -Name DefaultShell `
                 -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
                 -PropertyType String `
                 -Force

Stop-Transcript