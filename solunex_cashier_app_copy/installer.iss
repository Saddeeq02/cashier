[Setup]
AppName=IE Cashier
AppVersion=1.0
DefaultDirName={pf}\IECashier
DefaultGroupName=IE Cashier
OutputDir=dist_installer
OutputBaseFilename=IECashierSetup
SetupIconFile=C:\Users\RAFAWA ENTERPRISES\Desktop\solunex_cashier_app\iande.ico

Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\IECashier.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\IE Cashier"; Filename: "{app}\IECashier.exe"
Name: "{autodesktop}\IE Cashier"; Filename: "{app}\IECashier.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Additional Icons"

[Run]
Filename: "{app}\IECashier.exe"; Description: "Launch IE Cashier"; Flags: nowait postinstall skipifsilent