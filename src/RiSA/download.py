"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

from .libraries import *
sys.path.insert(0, os.getcwd())

# Functions

def download_credentials(urs, username, password):
    """
    Credentials for downloading from IMERG
    """
    homeDir = os.path.expanduser("~") + os.sep
    with open(homeDir + '.netrc', 'w') as file:
        file.write(f'machine {urs} login {username} password {password}')
        file.close()
    with open(homeDir + '.urs_cookies', 'w') as file:
        file.write('')
        file.close()
    with open(homeDir + '.dodsrc', 'w') as file:
        file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
        file.write('HTTP.NETRC={}.netrc'.format(homeDir))
        file.close()
    print('Saved .netrc, .urs_cookies, and .dodsrc to:', homeDir)
    # Set appropriate permissions for Linux/macOS
    if platform.system() != "Windows":
        Popen('chmod og-rw ~/.netrc', shell=True)
    else:
        # Copy dodsrc to working directory in Windows  
        shutil.copy2(homeDir + '.dodsrc', os.getcwd())
        print('Copied .dodsrc to:', os.getcwd())