@echo off
echo ====================================================
echo Menjalankan Aplikasi HR Analytics (Virtual Environment)
echo ====================================================

:: Cek apakah folder env ada
if not exist "env\Scripts\activate.bat" (
    echo Error: Virtual environment tidak ditemukan di folder "env".
    pause
    exit /b
)

:: Mengaktifkan virtual environment
call env\Scripts\activate.bat

:: Memastikan scikit-learn 1.6.1 terinstal di dalam env ini jika belum
python -c "import sklearn; print('Scikit-learn version:', sklearn.__version__)"

echo Memulai Server Flask...
python app.py

pause
