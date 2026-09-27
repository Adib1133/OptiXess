; Optional installer recipe for Inno Setup 6. Compile after building ArcScaler.exe.
[Setup]
AppId=ArcScaler.Desktop
AppName=ArcScaler
AppVersion=1.1.0
DefaultDirName={localappdata}\Programs\ArcScaler
DefaultGroupName=ArcScaler
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=dist
OutputBaseFilename=ArcScaler-Setup
SetupIconFile=assets\arcscaler.ico
UninstallDisplayIcon={app}\ArcScaler.exe
Compression=lzma2
SolidCompression=yes
[Files]
Source: "dist\ArcScaler.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\ArcScaler"; Filename: "{app}\ArcScaler.exe"; IconFilename: "{app}\ArcScaler.exe"
Name: "{autodesktop}\ArcScaler"; Filename: "{app}\ArcScaler.exe"; IconFilename: "{app}\ArcScaler.exe"
[Run]
Filename: "{app}\ArcScaler.exe"; Description: "Launch ArcScaler"; Flags: nowait postinstall skipifsilent
