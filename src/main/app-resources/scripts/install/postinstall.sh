cd /tmp
mkdir matlab_runtime_90
cd matlab_runtime_90
wget http://ssd.mathworks.com/supportfiles/downloads/R2015a/deployment_files/R2015a/installers/glnxa64/MCR_R2015a_glnxa64_installer.zip
unzip MCR_R2015a_glnxa64_installer.zip
./install -console -mode silent -agreeToLicense yes -destinationFolder /opt/
