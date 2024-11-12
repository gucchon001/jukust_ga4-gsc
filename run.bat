@echo off
chcp 65001 > nul
:: 仮想環境のディレクトリを設定
set "venv_path=.\myenv"
:: 仮想環境が存在しない場合は作成
if not exist "%venv_path%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv %venv_path%
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created successfully.
)
:: 仮想環境をアクティベート
call %venv_path%\Scripts\activate
:: pipの現在のバージョンを取得して必要に応じてアップデート
for /f "tokens=2 delims= " %%a in ('pip --version') do set "current_pip_version=%%a"
set "latest_pip_version=24.2"
if not "%current_pip_version%"=="%latest_pip_version%" (
    echo Updating pip to version %latest_pip_version%...
    python -m pip install --upgrade pip==%latest_pip_version%
    if errorlevel 1 (
        echo Error: Failed to update pip to version %latest_pip_version%.
        exit /b 1
    )
    echo pip updated to version %latest_pip_version% successfully.
)
:: requirements.txtが存在するか確認
if not exist requirements.txt (
    echo Error: requirements.txt file not found.
    exit /b 1
)
:: requirements.txtのハッシュ値を計算
for /f "skip=1 delims=" %%a in ('certutil -hashfile requirements.txt SHA256') do if not defined current_hash set "current_hash=%%a"
:: 前回のハッシュ値を読み込む
if exist .req_hash (
    set /p stored_hash=<.req_hash
) else (
    set "stored_hash="
)
:: ハッシュ値を比較し、必要に応じてインストールを実行
if not "%current_hash%"=="%stored_hash%" (
    echo Requirements have changed. Installing/updating libraries...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required libraries.
        exit /b 1
    )
    echo %current_hash%>.req_hash
    echo Libraries installed/updated successfully.
) else (
    echo No changes in requirements. Skipping installation.
)
:: 引数で指定されたアプリを実行
if "%1"=="" (
    echo Error: Please specify the app file to run, e.g., main.py
    exit /b 1
)
:: Pythonファイルを実行
python "%1"
if errorlevel 1 (
    echo Error: Failed to run %1
    exit /b 1
)