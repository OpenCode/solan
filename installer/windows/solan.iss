; Windows installer for Solan (Inno Setup 6).
; Built by .github/workflows/release.yml:
;   iscc /DAppVersion=1.2.3 /DSourceExe=path\to\solan.exe /DOutputDir=out installer\windows\solan.iss
; Installs for the current user only (no administrator rights), adds solan to the PATH
; and a "Share with Solan" entry to the folders' right-click menu.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef SourceExe
  #define SourceExe "..\..\dist\solan.exe"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\dist"
#endif

[Setup]
AppId={{6F0B8C52-3C7E-4B8E-9C1D-5A3E2F7B9D41}
AppName=Solan
AppVersion={#AppVersion}
AppPublisher=Francesco Apruzzese
AppPublisherURL=https://github.com/OpenCode/solan
DefaultDirName={localappdata}\Programs\Solan
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ChangesEnvironment=yes
OutputDir={#OutputDir}
OutputBaseFilename=solan-{#AppVersion}-windows-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=Solan

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "solan.exe"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

; Right-click menu: "Share with Solan" on a folder and on the empty area inside a folder.
; cmd /k keeps the window open, so the address (or an error) stays visible;
; closing the window stops sharing. %V is the folder's path.
Root: HKCU; Subkey: "Software\Classes\Directory\shell\Solan"; ValueType: string; ValueName: ""; \
  ValueData: "Share with Solan"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\Solan"; ValueType: string; ValueName: "Icon"; \
  ValueData: "{app}\solan.exe"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\Solan\command"; ValueType: string; ValueName: ""; \
  ValueData: "cmd.exe /k """"{app}\solan.exe"" ""%V"""""
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\Solan"; ValueType: string; ValueName: ""; \
  ValueData: "Share with Solan"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\Solan"; ValueType: string; ValueName: "Icon"; \
  ValueData: "{app}\solan.exe"
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\Solan\command"; ValueType: string; ValueName: ""; \
  ValueData: "cmd.exe /k """"{app}\solan.exe"" ""%V"""""

[Messages]
FinishedLabel=Solan is installed.%n%nRight-click a folder and choose "Share with Solan" (on Windows 11 it's under "Show more options"), or open a new terminal and run:%n%n    solan C:\path\to\folder

[Code]
function NeedsAddPath(Dir: string): Boolean;
var
  Path: string;
begin
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Path) then
    Result := True
  else
    Result := Pos(';' + Uppercase(Dir) + ';', ';' + Uppercase(Path) + ';') = 0;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Path, Dir: string;
  P: Integer;
begin
  if CurUninstallStep <> usPostUninstall then
    Exit;
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Path) then
    Exit;
  Dir := ExpandConstant('{app}');
  P := Pos(';' + Uppercase(Dir), Uppercase(Path));
  if P > 0 then
  begin
    Delete(Path, P, Length(Dir) + 1);
    RegWriteExpandStringValue(HKCU, 'Environment', 'Path', Path);
  end;
end;
