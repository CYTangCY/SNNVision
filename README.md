# SNNVision

related work from gogolexy and twetto

System:rasberrypi OS

![image](https://github.com/CYTangCY/SNNVision/blob/RasberryPi_Version/report_image.png)

## first

sudo apt update

sudo pip3 install --upgrade pip

## system package requirements:

sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev  libqtgui4  libqt4-test cmake llvm gcc g++ qt5-default

## python requirements

(python3.7 ~ 3.8.6) 

numpy

matplotlib

opencv 4.2.0 or higher

pyqtgraph

llvmlite 0.32.0 or higher

numba 0.49.0 - 0.52.0

scipy

### pyqt5 (need compile 1~2 hour with RasberryPi 4)

## Usage

python3 main.py 

"-t" "--num-threads" (type=int, default=1, help="# of threads to accelerate")

"-dp" "--display-potential" (help="Whether or not neural potentials should be displayed")(for computer)

"-do" "--display-obstacle" (help="Whether or not obstacles should be displayed")

"-da" "--display-activity" (help="Whether or not activity should be displayed")(for computer)

"-i" "--input", type=str (help="Input video file instead of live stream.")

"-p" "--pose", type=str (help="Input IMU data.")

"-o" "--output", type=str (help="Output processed video file for obstacle detection.")

"-m" "--models", type=str (help="Use Izhikevich = iz, Use Lif=lif")




