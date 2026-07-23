; -- ARTIFICE_installer.iss --
; script for installing artifice


[Setup]
AppName=piranhaGUI
AppVersion=1.6.13
WizardStyle=modern
DefaultDirName={autopf}\piranhaGUI
DefaultGroupName=piranhaGUI
UninstallDisplayIcon={app}\.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.\installer
OutputBaseFilename=piranhaGUIv1.6.13_installer_windows

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon";

[Files]
Source: "piranhaGUI.exe"; DestDir: "{app}"
;Source: "runs\archived_runs.json"; DestDir: "{app}\runs"
Source: "resources\*"; DestDir: "{app}\resources"
Source: "piranha_image_file\piranha.tar"; DestDir: "{localappdata}\piranhaGUI"
Source: "builtin_protocols\*"; DestDir: "{app}\builtin_protocols"; Flags: ignoreversion recursesubdirs
Source: "config.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\piranhaGUI"; Filename: "{app}\piranhaGUI.exe"
Name: "{commondesktop}\piranhaGUI"; Filename: "{app}\piranhaGUI.exe"; Tasks: desktopicon
