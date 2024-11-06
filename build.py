import os
import shutil
import subprocess

def clean_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)

def build_exe():
    clean_directory('build')
    clean_directory('dist')
    
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'clean_build.spec'
    ], check=True)

if __name__ == '__main__':
    build_exe()
