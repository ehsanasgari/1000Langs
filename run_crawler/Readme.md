# Installation instruction using miniconda on Linux and MacOSx

We recommend to use a conda virtual environment for installation of 1000Langs.


## (1) Miniconda installation

The first step is to install the latest version of conda on your system.

### Linux
```
cd ~
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ./Miniconda3-latest-Linux-x86_64.sh
```

### MacOS
```
cd ~
curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash ./Miniconda3-latest-MacOSX-x86_64.sh
```


## (2) General configurations of conda envinronment

Then you need to add the conda to your path. Please modify the following path if you changed in the installation

```
export PATH="~/miniconda3/bin:$PATH"
```

Then you need to add conda channels:

```
conda config --add channels conda-forge
```



## (3) Installation of dependencies in the virtual environment

The next step would be installation of the dependencies:

```
conda create --name lang1000 --file env_linux.txt
```

Then you need to activate the DiTaxa virtual environment:

```
source activate lang1000
```

Install other requirements using pip:

```
pip install -r requirement.txt
```



## Running the 1000Langs

You need to obtain an API code from bible digital platform. You may obtain this from the following link:
https://www.digitalbibleplatform.com/signup/

Example running of 1000Langs (replace 'YOURAPICODE' with your API code)
```
python3 lang1000.py --outdir /mounts/data/proj/asgari/superparallelproj/new_bpc/ --apikey YOURAPICODE --override 1 --repeat 3 --updatemeta 1 --cores 20
```

To see the details of the parameters you can use help  '-h'
```
python3 lang1000.py -h

```
