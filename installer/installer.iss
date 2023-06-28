; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "DVTFront"
#define MyAppVersion "1.0"
#define MyAppPublisher "Boston Scientifc"
#define MyAppURL "http://www.bostonscientific.com/"
#define MyAppExeName "start_gx1_simulator.bat"
#define python3_dir="D:\Workspace\GX1\Python38"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{C0637995-8CA5-4463-BE6F-AD117E9614B2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=DVTFront
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Icons]
Name: "{commondesktop}\DVTFront"; Filename: "{app}\GX1Automation\start_gx1_simulator.bat"; WorkingDir: "{app}\GX1Automation"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\*"; DestDir: "{app}\GX1Automation"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "venv\*,TestReports\*,TestProtocols\*,logs\*,installer\*,.git\*,.idea\*,__pycache__\*"
Source: "{#python3_dir}\*"; DestDir: "{app}\python3"; Flags: ignoreversion recursesubdirs createallsubdirs;
Source: "..\venv\Lib\site-packages\*";DestDir:"{app}\python3\Lib\site-packages";Flags: ignoreversion recursesubdirs createallsubdirs;
Source: "..\venv\Scripts\*";DestDir:"{app}\python3\Scripts";Flags: ignoreversion recursesubdirs createallsubdirs;
Source: "Redist\VC_redist_2017.x64.exe"; DestDir: {tmp}; Flags: dontcopy
Source: "post_install_process.py"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "pip-21.3.1\*"; DestDir: "{app}\pip-21.3.1"; Flags: ignoreversion recursesubdirs
Source: "setting.py"; DestDir: "{app}\GX1Automation"; Flags: ignoreversion recursesubdirs


[Run]
Filename: "{tmp}\VC_redist_2017.x64.exe"; StatusMsg: "InstallingVC2017redist"; Parameters: "/quiet"; Check: VC2017RedistNeedsInstall ; Flags: waituntilterminated
Filename: "{app}\Python3\python.exe"; Parameters:"post_install_process.py"; StatusMsg: "Updating Python37 for Local Enviornment"; Flags: waituntilterminated;WorkingDir:"{app}"
Filename: "{app}\Python3\python.exe"; Parameters:"setup.py install"; StatusMsg: "Install pip"; Flags: waituntilterminated;WorkingDir:"{app}\pip-21.3.1"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\python3\Scripts"; \
    Check: NeedsAddPath('{app}\python3\Scripts')
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Code]
function VC2017RedistNeedsInstall: Boolean;
var 
  Version: String;
begin
  if (RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version)) then
  begin
    // Is the installed version at least 14.14 ? 
    Log('VC Redist Version check : found ' + Version);
    Result := (CompareStr(Version, 'v14.14.26429.03')<0);
  end
  else 
  begin
    // Not even an old version installed
    Result := True;
  end;
  if (Result) then
  begin
    ExtractTemporaryFile('VC_redist_2017.x64.exe');
  end;
end;
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    DeleteFile(ExpandConstant('{app}\post_install_process.py'));
  end;
end;

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  { look for the path with leading and trailing semicolon }
  { Pos() returns 0 if not found }
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\GX1Automation\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\GX1Automation\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\GX1Automation\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent



