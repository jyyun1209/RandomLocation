# ================================
# Embeddable Python + pip + packages Auto Install
# ================================

$pythonVersion = "3.9.13"
$arch = "amd64"
$zipName = "python-$pythonVersion-embed-$arch.zip"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/$zipName"
$pythonDir = Join-Path $PSScriptRoot "..\python-3.9"
$reqFile = Join-Path $PSScriptRoot "requirements.txt"

# -----------------------------------------------------
Write-Host "===> Python $pythonVersion 환경 준비 중..." -ForegroundColor Cyan

if (!(Test-Path $pythonDir)) {
    Write-Host "Downloading Embeddable Python from $pythonUrl"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $zipName
    Expand-Archive -Path $zipName -DestinationPath $pythonDir -Force
    Remove-Item $zipName

    $pthFile = Get-ChildItem "$pythonDir\python*._pth" | Select-Object -First 1
    if ($pthFile) {
        $content = Get-Content $pthFile
        if ($content -match '#\s*import site') {
            (Get-Content $pthFile) -replace '#\s*import site','import site' | Set-Content $pthFile
            Write-Host "Patched $($pthFile.Name) (import site 활성화)"
        } else {
            Write-Host "$($pthFile.Name)에 이미 import site가 활성화되어 있습니다."
    }
}

    Write-Host "✅ Embeddable Python 설치 완료: $pythonDir"
} else {
    Write-Host "Python 폴더가 이미 존재함. 건너뜁니다."
}

# -----------------------------------------------------
# pip 설치
Write-Host "`n===> pip 설치 중..." -ForegroundColor Cyan

$pythonExe = Join-Path $pythonDir "python.exe"
$pythonDll = Join-Path $pythonDir "python39.dll"

if (!(Test-Path $pythonExe)) {
    Write-Host "❌ python.exe를 찾을 수 없습니다. 설치 경로 확인 필요." -ForegroundColor Red
    exit 1
}

# get-pip.py 다운로드 및 실행
$pipUrl = "https://bootstrap.pypa.io/get-pip.py"
$pipScript = Join-Path $env:TEMP "get-pip.py"

Invoke-WebRequest $pipUrl -OutFile $pipScript
& $pythonExe $pipScript --no-warn-script-location
Remove-Item $pipScript

Write-Host "✅ pip 설치 완료"

# -----------------------------------------------------
# 필수 패키지 설치
Write-Host "`n===> 필수 패키지 설치 중..." -ForegroundColor Cyan

if (!(Test-Path $reqFile)) {
    Write-Host "requirements.txt 파일이 없습니다. 패키지 설치를 건너뜁니다."
} else {
    & $pythonExe -m pip install --upgrade pip --no-warn-script-location
    & $pythonExe -m pip install -r $reqFile --no-warn-script-location
    Write-Host "✅ requirements.txt 기반 패키지 설치 완료"
}

Write-Host "`n🎉 Python 환경 준비 완료!"
