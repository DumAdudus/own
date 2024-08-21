# For LTSC edition only
if (!(Get-ComputerInfo).WindowsProductName.Contains('LTSC')) {
    return
}

$logFile = "C:\Windows\Setup\Scripts\Winget.log"
Start-Transcript -Path $logFile -IncludeInvocationHeader

Set-Location -ErrorAction Stop -LiteralPath $PSScriptRoot

# Install VCLibs
Add-AppxPackage Microsoft.VCLibs.x64.14.00.Desktop.appx

# Install Microsoft.UI.Xaml
$ui_ver_miner = 8
$ui_ver_rev = 6
Add-AppxPackage Microsoft.UI.Xaml.2.$ui_ver_miner.appx

# Install the latest release of Microsoft.DesktopInstaller from GitHub
$winget_id = "8wekyb3d8bbwe"
Add-AppxPackage Microsoft.DesktopAppInstaller_$winget_id.msixbundle

$ResolveWingetPath = Resolve-Path "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_1.*.0_x64__$winget_id"
if ($ResolveWingetPath) {
    $WingetPath = $ResolveWingetPath[-1].Path
}

# $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
# $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

#Fixing Permissions
TAKEOWN /F "$WingetPath" /R /A /D Y
Start-Sleep -Seconds 2
ICACLS "$WingetPath" /grant Administrators:F /T

#Adding winget dir to path
$ENV:PATH += ";$WingetPath"

Stop-Transcript