cd### Running from terminal ###
These instructions assume you have installed conda and docker installed before you proceed.
Instructions for installing conda: https://conda.io/projects/conda/en/latest/user-guide/install/index.html
Instructions for installing docker: https://docs.docker.com/engine/install/

Navigate to the artifice directory within your terminal and execute the following command:

$ conda env create -f environment.yml

This will create a conda environment with the required dependencies. Activate it with:

$ conda activate artifice

To run artifice from the terminal:

$ python artifice.pyw

### Creating executable (windows) ###

To create an executable on windows first follow the steps above to create the conda environment, then create executable using pyinstaller and the provided spec file:

$ pyinstaller windows_build\artifice.spec

You can find the executable at ./windows_build/dist/artifice.exe. In this folder you can also find an InnoSetup install script (ARTIFICE_installer.iss), with which an installer for windows can be created.

### Creating executable (mac) ###

To create an executable for macOS follow the instructions above to create the conda environment, then run the following script:

$ source mac_build/build_artifice

### Creating Debian/Ubuntu ###

Compilation of .deb package is done using a docker image, to create it run:

$ docker build --no-cache -t artifice_linux_compiler /linux_build/compiler_docker

This will pull from the main branch of the github repo, edit the dockerfile to build from another branch. Then edit the following script to point to whatever directory you want your package and run it:

$ source /linux_build/create_application

