; Vert Desktop File Converter & PDF Suite
; Inno Setup 6 Script
; Generates standalone 'Vert_Setup.exe' with Desktop & Start Menu shortcuts

#define MyAppName "Vert"
#define MyAppVersion "1.1.2"
#define MyAppPublisher "Hadora Works"
#define MyAppURL "https://github.com/RenggoPandora/Vert"
#define MyAppExeName "Vert.exe"
#define MyAppIcoName "Vert.ico"

[Setup]
; App Identity
AppId={{5E4C208B-8835-4D09-B817-A96BC75EE890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Destination Folder (defaults to Program Files / local AppData if standard user)
DefaultDirName={autopf}\Vert
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
UsePreviousAppDir=yes
CloseApplications=yes
RestartApplications=no
LicenseFile=
OutputDir=..\dist
OutputBaseFilename=Vert_Setup
SetupIconFile=..\Vert.ico
SolidCompression=yes
Compression=lzma2/ultra64

; Privileges & Windows Compatibility
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Dist directory produced by PyInstaller
Source: "..\dist\Vert\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\Vert.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcoName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcoName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall
