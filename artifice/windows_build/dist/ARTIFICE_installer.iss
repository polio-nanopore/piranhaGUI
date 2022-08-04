; -- ARTIFICE_installer.iss --
; script for installing artifice


[Setup]
AppName=ARTIFICE
AppVersion=1.3.2
WizardStyle=modern
DefaultDirName={autopf}\ARTIFICE
DefaultGroupName=ARTIFICE
UninstallDisplayIcon={app}\.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.\installer
OutputBaseFilename=ARTIFICEv1.3.2_installer_windows

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon";

[Files]
Source: "ARTIFICE.exe"; DestDir: "{app}"
;Source: "runs\archived_runs.json"; DestDir: "{app}\runs"
Source: "resources\poseqco_logo_cropped.png"; DestDir: "{app}\resources"
Source: "resources\LiberationSans-Regular.ttf"; DestDir: "{app}\resources"
Source: "resources\translation_scheme.csv"; DestDir: "{app}\resources"
Source: "resources\piranha.png"; DestDir: "{app}\resources"
Source: "resources\a_logo.png"; DestDir: "{app}\resources"
Source: "resources\placeholder_artifice2.ico"; DestDir: "{app}\resources"
Source: "builtin_protocols\*"; DestDir: "{app}\builtin_protocols"; Flags: ignoreversion recursesubdirs
Source: "config.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\ARTIFICE"; Filename: "{app}\ARTIFICE.exe"
Name: "{commondesktop}\ARTIFICE"; Filename: "{app}\ARTIFICE.exe"; Tasks: desktopicon
