!include MUI2.nsh
!include LogicLib.nsh

Unicode true

!ifndef VERSION
    !error "VERSION must be supplied with /DVERSION=x.y.z"
!endif
!ifndef DIST
    !error "DIST must be supplied with /DDIST=path-to-standalone-bundle"
!endif

!define PRODUCT_NAME "RBC Community Map"
!define PRODUCT_VERSION "${VERSION}"
!define PRODUCT_PUBLISHER "RBC Community Map Team"
!define PRODUCT_WEB_SITE "https://github.com/JELollis/RBC-Map"
!define APP_EXE "RBC Community Map.exe"
!define MUI_ICON "${DIST}\images\favicon.ico"
!define MUI_UNICON "${DIST}\images\favicon.ico"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "RBC-Map-Installer-${PRODUCT_VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\RBC-Map"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Main application" SecMain
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "${DIST}\*.*"
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\images\favicon.ico" 0
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\images\favicon.ico" 0
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\RBC-Map"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"
    ; Deliberately preserve %LOCALAPPDATA%\RBC-Map user data.
SectionEnd

VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2026 RBC Community Map Team"
VIAddVersionKey "URLInfoAbout" "${PRODUCT_WEB_SITE}"
