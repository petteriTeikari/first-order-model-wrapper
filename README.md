# First Order Motion Model for Image Animation

This repository contains the source code for the paper [First Order Motion Model for Image Animation](https://papers.nips.cc/paper/8935-first-order-motion-model-for-image-animation) by Aliaksandr Siarohin, [Stéphane Lathuilière](http://stelat.eu), [Sergey Tulyakov](http://stulyakov.com), [Elisa Ricci](http://elisaricci.eu/) and [Nicu Sebe](http://disi.unitn.it/~sebe/).

See original repo notes in https://github.com/AliaksandrSiarohin/first-order-model

## Petteri's notes for getting the repo to work 

The original repo was quite easy to get it running and nicely documented, this just added the audio to the output. TODO! put everything behiund a single Python call on command window so there are no separate steps. If you are new to using code/AI for creative purposes, you might want to look at the [instructions for getting video style transfer to work](https://github.com/petteriTeikari/ReReVST-UX-Wrapper) to get maybe a bit better understand what all these components are that you need to install.

### Pre-prerequisites

* Install [Anaconda3](https://www.anaconda.com/products/individual#windows) (if you have other Python 3.8 already, that is fine) ([installation instructions](https://docs.anaconda.com/anaconda/install/windows/))
* Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git), if you are `pull`ing this repo (you could just download the zip as well if you really do not know what this is)
* Install [`ffmpeg`](https://ffmpeg.org/download.html) 
* GO to terminal / command window here and execute the commands from there (**NOTE!** all the path separators are in Linux/Mac syntax `/` instead of Windows' \\)

### Clone this repository

```bash
git clone https://github.com/petteriTeikari/first-order-model-wrapper
cd first-order-model-wrapper
```

### Virtual environment setup

Create virtual environment

```bash
python3.8 -m venv venv-1stOrderModelMotion
```

Activate this created virtual environment, and start installing libraries to it:

in Ubuntu:
```
source venv-1stOrderModelMotion/bin/activate
```

command in **Windows** [Pip and virtualenv on Windows](https://programwithus.com/learn/python/pip-virtualenv-windows) (`cd Scripts` - `activate` - `cd..`):

```
Scripts/activate
```

Upgrade the `pip` (automatic installer for all the libraries)

```
python3.8 -m pip install --upgrade pip
```

`requirements.txt` contains all the library version that were used to get this code working, if you go and improvise and install the latest libraries, this repository might not work, so use **exactly** the same versions to get started (you can upgrade libraries later if you feel like there is need for it)

```
pip install -r requirements.txt
```

### PyTorch install

Check the one matching your OS and GPU situation

Ubuntu 18.04 with a NVIDIA GPU

```
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
```

Ubuntu 18.04 if you do not have NVIDIA GPU

```
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
```

Windows with NVIDIA GPU

```
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio===0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
```

Windows without GPU

```
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio===0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
```

Mac, I guess you need to [install from PyTorch sources](https://github.com/pytorch/pytorch#from-source), if you want to run this on GPU.

Mac with CPU:

```
pip install torch torchvision torchaudio
```


### Other tasks to do 

* Download [`vox-cpk.pth.tar`](https://drive.google.com/file/d/1_v_xW1V52gZCZnXgh1Ap_gwA9YVIzUnS/view?usp=sharing) for face animation (provided by the original authors), and place the file to the subfolder `checkpoints`

* For cropping and preprocessing a youtube video (to get the face from it), you need to install [`face-alignment`](https://github.com/1adrianb/face-alignment) library (comes as preloaded with [an issue fixed for you]()):

```bash
cd face-alignment
pip install -r requirements.txt
python setup.py install
cd ..
```

### How to animate a static face from an image

TODO! Maybe make a nicer wrapper and do all on one-go

![](doc/workflow.png)

The prerequisites 1) and 2) need to be done only once per image, and once per video. Like with the "actually animating" you just use pre-cropped images and videos.

#### Prerequisite 1) Crop your static image 

E.g. portrait of yourself or some celebrity, "celebrity portrait" Google search gave young Stalin so it is our demo photo now

```
python crop-face-img.py --inp ./DATA_inputs/images/stalin.jpg
```

Takes around ~3 sec and adds the `_crop` suffix to your filename

```
Image cropped in 0:00:03.406049, and saved to ./DATA_inputs/images/stalin_crop.jpg
```

#### Prerequisite 2) Crop your driving video

E.g. you have downloaded some .mp4 file from youtube

```
python crop-video.py --inp ./DATA_inputs/driving_videos/scatman.mp4
```

That script actually does not do any cropping _per se_ but give you the command that you need to run on command line (and you need [`ffmpeg`](https://ffmpeg.org/download.html) installed for this), the command is displayed on the command window after the script execution, and with the `scatman.mp4`, it is the following (with the `crop.mp4` replaced with your actual output filename:

```
ffmpeg -i ./DATA_inputs/driving_videos/scatman.mp4 -ss 0.0 -t 8.8 -filter:v "crop=236:243:0:4, scale=256:256" ./DATA_inputs/driving_videos/scatman_crop.mp4
```

##### If you get multiple crop commands

You need to manually rename the parts, e.g.

```
ffmpeg -i ./DATA_inputs/driving_videos/spit.mp4 -ss 0.0 -t 12.966666666666667 -filter:v "crop=1135:930:604:0, scale=256:256" crop1.mp4
ffmpeg -i ./DATA_inputs/driving_videos/spit.mp4 -ss 13.1 -t 7.799999999999999 -filter:v "crop=1106:881:501:0, scale=256:256" crop2.mp4
```

and then combine back to a single mp4 file:

```
ffmpeg -i concat:"crop1.mp4|crop2.mp4" spit_crop.mp4
```

#### Actually animate

The `vox-256.yaml` is the configuration file used by the original author for the face animation, and the `.pth` is the pretrained model provided by the original authors

```
python demo.py  --config config/vox-256.yaml --driving_video ./DATA_inputs/driving_videos/scatman_crop.mp4 --source_image ./DATA_inputs/images/stalin_crop.jpg --checkpoint checkpoints/vox-cpk.pth.tar --relative --adapt_scale
```

Around real-time processing with `NVIDIA RTX 2070 Super`, i.e. 33.34 fps, `100%|█████████████| 264/264 [00:07<00:00, 33.34it/s]`

#### TODO! 

You could probably want just one call for all these steps, i.e. you are annoyed by all the cropping calls :P

![learn to code](doc/learn_to_code.png)

From ["How to learn programming | George Hotz and Lex Fridman"](https://youtu.be/NjYICpXJ03M)

