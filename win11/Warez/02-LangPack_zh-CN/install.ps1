# For LTSC edition only
if (!(Get-ComputerInfo).WindowsProductName.Contains('LTSC')) {
    return
}

$logFile = "C:\Windows\Setup\Scripts\LP-zh-CN.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

$LP = 'zh-CN'

# Add-WindowsPackage -Online -PackagePath .\Microsoft-Windows-Client-LanguagePack-Package-amd64-$LP.cab

Install-Language $LP
# Start-Sleep 10

Set-WinSystemLocale $LP
Set-WinUILanguageOverride $LP
Set-WinUserLanguageList $LP,en-US -Force


Stop-Transcript