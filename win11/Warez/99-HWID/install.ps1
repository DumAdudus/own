# For LTSC edition only
if (!(Get-ComputerInfo -Property WindowsProductName).WindowsProductName.Contains('LTSC')) {
    return
}

$logFile = "C:\Windows\Setup\Scripts\HWID.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

.\MAS_AIO-CRC32_31F7FD1E.cmd /HWID

Stop-Transcript