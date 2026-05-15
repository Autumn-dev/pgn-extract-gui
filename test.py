import platform
import subprocess
import os 
import shutil
import tempfile

if platform.system() == "Windows":
    print("Windows detected")
elif platform.system() == "Darwin":
    original_dir = os.path.abspath(".")

    tmp_script = os.path.join(tempfile.gettempdir(), "unix_install.sh")  # Assuming unix_install.sh is in the current directory
    shutil.copy("unix_install.sh", tmp_script)
    os.chmod(tmp_script, 0o755)  # Make the script executable
    print("macOS detected")
    apple_script = f'do shell script "bash \\"{tmp_script}\\" \\"{original_dir}\\"" with administrator privileges'
    shell = subprocess.run(['osascript','-e', apple_script]) # Assuming unix_install.sh is in the current directory

elif platform.system() == "Linux":
    print("Linux detected")