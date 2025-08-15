; SecRandom 安装脚本
; 使用 Inno Setup 创建安装包

#define MyAppName "SecRandom"
#define MyAppVersion "1.2.0.0"
#define MyAppPublisher "SECTL"
#define MyAppURL "https://github.com/SECTL/SecRandom"
#define MyAppExeName "SecRandom.exe"

[Setup]
; 基础设置
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=release
OutputBaseFilename=SecRandom-Setup-{#MyAppVersion}
SetupIconFile=resources\SecRandom.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; 权限设置
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimp.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标"; Flags: unchecked
Name: "quicklaunchicon"; Description: "创建快速启动栏快捷方式"; GroupDescription: "附加图标"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
; 主程序文件
Source: "dist\SecRandom\SecRandom.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SecRandom\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 安装包标识文件
Source: "app\Settings\installer_marker.json"; DestDir: "{app}\app\Settings"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// 安装完成后更新安装包标识文件
procedure CurStepChanged(CurStep: TSetupStep);
var
  MarkerFile: String;
  JsonContent: AnsiString;
begin
  if CurStep = ssPostInstall then
  begin
    // 更新安装包标识文件
    MarkerFile := ExpandConstant('{app}\app\Settings\installer_marker.json');
    if LoadStringFromFile(MarkerFile, JsonContent) then
    begin
      JsonContent := StringReplace(JsonContent, '"installation_date": ""', 
        '"installation_date": "' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + '"', [rfReplaceAll]);
      JsonContent := StringReplace(JsonContent, '"installation_path": ""', 
        '"installation_path": "' + ExpandConstant('{app}') + '"', [rfReplaceAll]);
      JsonContent := StringReplace(JsonContent, '"version": ""', 
        '"version": "' + '{#MyAppVersion}' + '"', [rfReplaceAll]);
      SaveStringToFile(MarkerFile, JsonContent, False);
    end;
  end;
end;

// 检查是否正在运行
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // 检查是否已有实例在运行
  if CheckForMutexes('SecRandomSingleInstance') then
  begin
    MsgBox('SecRandom 正在运行，请先关闭程序再继续安装。', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Result := True;
end;

// 卸载时删除所有文件
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    // 删除整个应用目录
    DelTree(ExpandConstant('{app}'), True, True, True);
  end;
end;