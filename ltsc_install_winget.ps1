# Install VCLibs
Add-AppxPackage 'https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx'

# Install Microsoft.UI.Xaml from NuGet
$ui_ver_miner = 8
$ui_ver_rev = 6
Invoke-WebRequest -Uri https://www.nuget.org/api/v2/package/Microsoft.UI.Xaml/2.$ui_ver_miner.$ui_ver_rev -OutFile .\microsoft.ui.xaml.2.zip
Expand-Archive .\microsoft.ui.xaml.2.zip
Add-AppxPackage .\microsoft.ui.xaml.2\tools\AppX\x64\Release\Microsoft.UI.Xaml.2.$ui_ver_miner.appx

# Install the latest release of Microsoft.DesktopInstaller from GitHub
$winget_id = "8wekyb3d8bbwe"
Invoke-WebRequest -Uri https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_$winget_id.msixbundle -OutFile .\Microsoft.DesktopAppInstaller_$winget_id.msixbundle
Add-AppxPackage .\Microsoft.DesktopAppInstaller_$winget_id.msixbundle

$ResolveWingetPath = Resolve-Path "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_1.*.0_x64__$winget_id"
if ($ResolveWingetPath){
    $WingetPath = $ResolveWingetPath[-1].Path
}

#Fixing Permissions
TAKEOWN /F "$WingetPath" /R /A /D Y
ICACLS "$WingetPath" /grant Administrators:F /T

#Adding winget dir to path
$ENV:PATH += ";$WingetPath"