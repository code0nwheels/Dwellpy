; NSIS Installer Script for Dwellpy
; Creates a professional Windows installer with shortcuts and uninstaller

!include "MUI2.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"

; Installer configuration
!define PRODUCT_NAME "Dwellpy"
!define PRODUCT_VERSION "1.0.0"  ; Will be replaced by build script
!define PRODUCT_PUBLISHER "Dwellpy Team"
!define PRODUCT_WEB_SITE "https://github.com/code0nwheels/dwellpy"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Dwellpy.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; Output file name (will be set by build script)
OutFile "dwellpy-installer.exe"

; Installation directory
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""

; Request administrator privileges
RequestExecutionLevel admin

; Show installer details
ShowInstDetails show
ShowUnInstDetails show

; Modern UI configuration
!define MUI_ABORTWARNING
!define MUI_ICON "dwellpy\assets\icons\Dwellpy.ico"
!define MUI_UNICON "dwellpy\assets\icons\Dwellpy.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page (optional)
;!insertmacro MUI_PAGE_LICENSE "LICENSE"

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Start Menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${PRODUCT_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "NSIS:StartMenuDir"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Dwellpy.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Set installer name
Name "${PRODUCT_NAME}"

; Version information
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "Comments" "Accessibility tool for dwell clicking"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalTrademarks" ""
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© ${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}"

; Installer sections
Section "!Dwellpy Application" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Copy main executable
  File "dist\Dwellpy.exe"
  
  ; Copy documentation
  File /nonfatal "README.md"
  File /nonfatal "LICENSE"
  File /nonfatal "CHANGELOG.md"
  
  ; Copy any additional files if they exist
  File /nonfatal /r "docs"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"
    ; Registry entries
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Dwellpy.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Dwellpy.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Get file size for Add/Remove Programs
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

Section "Desktop Shortcut" SEC02
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Dwellpy.exe" "" "$INSTDIR\Dwellpy.exe" 0
SectionEnd

Section "Quick Launch Shortcut" SEC03
  CreateShortCut "$QUICKLAUNCH\${PRODUCT_NAME}.lnk" "$INSTDIR\Dwellpy.exe" "" "$INSTDIR\Dwellpy.exe" 0
SectionEnd

; Start Menu shortcuts
Section -AdditionalIcons
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_NAME}.lnk" "$INSTDIR\Dwellpy.exe"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Uninstall ${PRODUCT_NAME}.lnk" "$INSTDIR\uninst.exe"
  
  ; Add documentation shortcuts if files exist
  IfFileExists "$INSTDIR\README.md" 0 +2
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Read Me.lnk" "$INSTDIR\README.md"
  
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

; Post-installation
Section -Post
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "InstallDate" ""
SectionEnd

; Component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "The main Dwellpy application executable. This is required."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Creates a shortcut on your desktop for easy access."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Creates a shortcut in the Quick Launch toolbar."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section Uninstall
  ; Remove registry keys
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  ; Remove shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP
  Delete "$SMPROGRAMS\$ICONS_GROUP\Uninstall ${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Read Me.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$QUICKLAUNCH\${PRODUCT_NAME}.lnk"
  
  ; Remove directories
  RMDir "$SMPROGRAMS\$ICONS_GROUP"
  
  ; Remove files
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\Dwellpy.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\CHANGELOG.md"
  
  ; Remove documentation folder
  RMDir /r "$INSTDIR\docs"
  
  ; Remove installation directory (only if empty)
  RMDir "$INSTDIR"
  
  SetAutoClose true
SectionEnd

; Functions
Function .onInit
  ; Check if already installed
  ReadRegStr $R0 HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${PRODUCT_NAME} is already installed. $\n$\nClick 'OK' to remove the \
    previous version or 'Cancel' to cancel this upgrade." \
    IDOK uninst
  Abort
  
  uninst:
    ClearErrors
    Exec $R0
    IfErrors no_remove_uninstaller done
    
  no_remove_uninstaller:
  
  done:
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 \
    "Are you sure you want to completely remove ${PRODUCT_NAME}?" \
    IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK \
    "${PRODUCT_NAME} was successfully removed from your computer."
FunctionEnd
