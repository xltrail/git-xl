#define MyAppName "Git xltrail"

#define PathToX86Binary "..\..\git-xltrail-x86.exe"
#ifnexist PathToX86Binary
  #pragma error PathToX86Binary + " does not exist, please build it first."
#endif

#define PathToX64Binary "..\..\git-xltrail-x64.exe"
#ifnexist PathToX64Binary
  #pragma error PathToX64Binary + " does not exist, please build it first."
#endif

#define PathToDiffX86Binary "..\..\git-xltrail-diff-x86.exe"
#ifnexist PathToDiffX86Binary
  #pragma error PathToDiffX86Binary + " does not exist, please build it first."
#endif

#define PathToDiffX64Binary "..\..\git-xltrail-diff-x64.exe"
#ifnexist PathToDiffX64Binary
  #pragma error PathToDiffX64Binary + " does not exist, please build it first."
#endif

#define PathToMergeX86Binary "..\..\git-xltrail-merge-x86.exe"
#ifnexist PathToMergeX86Binary
  #pragma error PathToMergeX86Binary + " does not exist, please build it first."
#endif

#define PathToMergeX64Binary "..\..\git-xltrail-merge-x64.exe"
#ifnexist PathToMergeX64Binary
  #pragma error PathToMergeX64Binary + " does not exist, please build it first."
#endif

; Arbitrarily choose the x86 executable here as both have the version embedded.
#define MyVersionInfoVersion GetFileVersion(PathToX86Binary)

; Misuse RemoveFileExt to strip the 4th patch-level version number.
#define MyAppVersion RemoveFileExt(MyVersionInfoVersion)

#define MyAppPublisher "Zoomer Analytics LLC"
#define MyAppURL "https://www.xltrail.com/git-xltrail"
#define MyAppFilePrefix "git-xltrail-windows"

[Setup]
AppCopyright=Zoomer Analytics LLC
AppId={{9ACD2AD0-AC00-4B48-8D91-1456F97DBEDD}
AppName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppVersion={#MyAppVersion}
ArchitecturesInstallIn64BitMode=x64
ChangesEnvironment=yes
Compression=lzma
DefaultDirName={code:GetDefaultDirName}
DirExistsWarning=no
DisableReadyPage=True
LicenseFile=..\..\LICENSE.md
OutputBaseFilename={#MyAppFilePrefix}-{#MyAppVersion}
OutputDir=..\..\
PrivilegesRequired=none
SetupIconFile=git-xltrail-logo.ico
SolidCompression=yes
;UninstallDisplayIcon={app}\git-xltrail.exe
UsePreviousAppDir=no
VersionInfoVersion={#MyVersionInfoVersion}
;WizardImageFile=git-xltrail-wizard-image.bmp
;WizardSmallImageFile=git-xltrail-logo.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Run]
; Uninstalls the old Git xltrail version that used a different installer in a different location:
;  If we don't do this, Git will prefer the old version as it is in the same directory as it.
Filename: "{code:GetExistingGitInstallation}\git-xltrail-uninstaller.exe"; Parameters: "/S"; Flags: skipifdoesntexist

[Files]
Source: {#PathToDiffX86Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail-diff.exe"; Check: not Is64BitInstallMode
Source: {#PathToDiffX64Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail-diff.exe"; Check: Is64BitInstallMode
Source: {#PathToMergeX86Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail-merge.exe"; Check: not Is64BitInstallMode
Source: {#PathToMergeX64Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail-merge.exe"; Check: Is64BitInstallMode
Source: {#PathToX86Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail.exe"; Check: not Is64BitInstallMode
Source: {#PathToX64Binary}; DestDir: "{app}"; Flags: ignoreversion; DestName: "git-xltrail.exe"; Check: Is64BitInstallMode

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: IsAdminLoggedOn and NeedsAddPath('{app}')
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "GIT_XLTRAIL_PATH"; ValueData: "{app}"; Check: IsAdminLoggedOn
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: (not IsAdminLoggedOn) and NeedsAddPath('{app}')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "GIT_XLTRAIL_PATH"; ValueData: "{app}"; Check: not IsAdminLoggedOn

[Code]
function GetDefaultDirName(Dummy: string): string;
begin
  if IsAdminLoggedOn then begin
    Result:=ExpandConstant('{pf}\{#MyAppName}');
  end else begin
    Result:=ExpandConstant('{userpf}\{#MyAppName}');
  end;
end;

// Uses cmd to parse and find the location of Git through the env vars.
// Currently only used to support running the uninstaller for the old Git xltrail version.
function GetExistingGitInstallation(Value: string): string;
var
  TmpFileName: String;
  ExecStdOut: AnsiString;
  ResultCode: integer;

begin
  TmpFileName := ExpandConstant('{tmp}') + '\git_location.txt';

  Exec(
    ExpandConstant('{cmd}'),
    '/C "for %i in (git.exe) do @echo. %~$PATH:i > "' + TmpFileName + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode
  );

  if LoadStringFromFile(TmpFileName, ExecStdOut) then begin
      if not (Pos('Git\cmd', ExtractFilePath(ExecStdOut)) = 0) then begin
        // Proxy Git path detected
        Result := ExpandConstant('{pf}');
      if Is64BitInstallMode then
        Result := Result + '\Git\mingw64\bin'
      else
        Result := Result + '\Git\mingw32\bin';
      end else begin
        Result := ExtractFilePath(ExecStdOut);
      end;

      DeleteFile(TmpFileName);
  end;
end;

// Checks to see if we need to add the dir to the env PATH variable.
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
  ParamExpanded: string;
begin
  //expand the setup constants like {app} from Param
  ParamExpanded := ExpandConstant(Param);
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon and with or without \ ending
  // Pos() returns 0 if not found
  Result := Pos(';' + UpperCase(ParamExpanded) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
  if Result = True then
    Result := Pos(';' + UpperCase(ParamExpanded) + '\;', ';' + UpperCase(OrigPath) + ';') = 0;
end;

// Runs the xltrail initialization.
procedure InstallGitxltrail();
var
  ResultCode: integer;
begin
  Exec(
    ExpandConstant('{cmd}'),
    ExpandConstant('/C ""{app}\git-xltrail.exe" install"'),
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode
  );
  if not ResultCode = 1 then
    MsgBox(
    'Git xltrail was not able to automatically initialize itself. ' +
    'Please run "git xltrail install" from the commandline.', mbInformation, MB_OK);
end;

// Event function automatically called when uninstalling:
function InitializeUninstall(): Boolean;
var
  ResultCode: integer;
begin
  Exec(
    ExpandConstant('{cmd}'),
    ExpandConstant('/C ""{app}\git-xltrail.exe" uninstall"'),
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode
  );
  Result := True;
end;