"""
    Purpose:
        This project was built to comply with the new project guidance (PEP 
        517) while still allowing for one to easily install the required 
        dependencies within a virtual environment for local development 
        without requiring one to actually install the project as a package via 
        pip.

        Therefore, required packages are defined within the setup.cfg file. 
        They are not listed within a requirements.txt file.

        To easily install the required dependencies for building from source, 
        use this script which replaces "pip install requirements.txt" as it 
        installs each package defined within the "install_requires" section of
        the project's setup.cfg file.   
    Context:
        https://stackoverflow.com/questions/46205648/can-pip-install-from-setup-cfg-as-if-installing-from-a-requirements-file
"""

import configparser
import subprocess


c = configparser.ConfigParser()
c.read('setup.cfg')
requirements = (c['options']['install_requires'].splitlines())
requirements.pop(0)


for requirement in requirements:
    subprocess.call(['pip', 'install', requirement])
