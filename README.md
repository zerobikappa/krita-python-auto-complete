# Fake Krita PYI generator

This project aims to provide intellisense and code completion in your code editor to simplify the development process when making krita extensions.

Traditionally, language servers & code editors like VS Code, PyCharm & Vim (etc) wont be able to recognize the krita module and hence throw warnings and errors at you everywhere as it simply do not know of this “krita” module, which is what this project is meant to solve.

A quick demo video:

https://user-images.githubusercontent.com/20190653/163692838-c6f9d7a2-2b3d-4649-a077-32df41c57842.mp4

This project was:
Originally created by @scottpetrovic ([krita-python-auto-complete](https://github.com/scottpetrovic/krita-python-auto-complete))
&darr;
Enhanced by @ItsCubeTime ([fake-pykrita](https://github.com/ItsCubeTime/fake-pykrita))
&darr;
I shrinked a part of their codes and added some new features, to make it more easy to use. ([now you are here](https://github.com/zerobikappa/krita-python-auto-complete))

(I removed some directories and files, including the `pykrita` directory, therefore I changed the repo name back to the initial one)

## 1.How to use

All you need to obtain from this project is only one file: `krita.pyi`. A `.pyi` file is a **Python Interface Definition file** that contains code stub reference for implementation of the interface. Just put the file to the same path of you python script, or place it to the directory, which was contained in `$PYTHONPATH`, then your IDE or LSP will be able to grab suggestions from this file.

### 1.1.Get a pre-built krita.pyi file in Github Release

(1) Download the `krita.pyi` file from [github release](https://github.com/zerobikappa/krita-python-auto-complete/releases). It is recommended to choose the version which is the same as your Krita version.

(2) Move the `krita.pyi` file into your project directory(where the `__init__.py` file was contained).

(3) Add this line in your python script:

```python
from krita import *
```

(4) optionally, if there are other module directories in your project folder, you may need to add your project directory in `$PYTHONPATH`, so that the language server can find your `krita.pyi` file.

In step(2) you can place the `krita.pyi` file in any other directory instead of your project folder, as long as that folder is in your `$PYTHONPATH`. However, in order to keep your system clean, maybe it is not recommended to install it in your system path or user path. I think it is better to place it in your project folder, then you can restrict the changes only in your project folder -- you can also change `$PYTHONPATH` in your project setting, or add `krita.pyi` in your `.gitignore` file, or do whatever you want.

## 2.How to build

If you cannot find a proper `krita.pyi` file in [github release](https://github.com/zerobikappa/krita-python-auto-complete/releases), you can generate it by yourself.

### 2.1 Use generator script to build `krita.pyi`

(1) Obtain Krita source code
Download Krita source code from [Krita project page](https://github.com/KDE/krita/tags)

(2) Download generator script from this repository

```bash
wget -c https://raw.githubusercontent.com/zerobikappa/krita-python-auto-complete/master/generate-python-autocomplete-file.py
```

(3) Run script

```bash
python generate-python-autocomplete-file.py
```

(4) You may see a file dialog popup, which ask you choose Krita source code directory. **Please select the path where contains Krita Project's main `CMakeLists.txt` file.** Then click "OK" to run script.

(5) After complete without error, you can found an `output` directory was created in your current location, and the `krita.pyi` is in it.

```bash
.
├── generate-python-autocomplete-file.py
└── output
    └── krita.pyi

2 directories, 2 files
```

(6) (Optional) After first run the script, the setting of Krita source code path will be saved in `/tmp/kritaHomeDirSave.py`(for Linux) or `C:\Users\AppData\Local\Temp\kritaHomeDirSave.py`(for Windows). When you run the script again, it will not ask you again for the source code path, unless you remove the `kritaHomeDirSave.py` or reboot your computer.

If you want to build the `krita.pyi` in non-interactive session (such as `CI` or `github action`), you can prepare the `kritaHomeDirSave.py` file in advance. For example:

```bash
echo "kritaHomeDir = \"/home/username/Downloads/krita-5.1.0\"" > /tmp/kritaHomDirSave.py
```

For more details, please refer [my github action workflow file](https://github.com/zerobikappa/krita-python-auto-complete/blob/master/.github/workflows/generate-fake-module-file.yml).
You can fork this repository as well and run the action by yourself. Do whatever you want.



