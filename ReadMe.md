# This is Roast Bot with TTS

This bot roasts you on what ever application you are on so if I am on vscode its gonna roast my ass or any application I use. Currently it works for MacOs, Windows, and Linux. It can also read minecraft logs and roasts you on what ever action u doing.

## Installation

### Windows

* git clone this repo
* Set up a python virutal enviroment in python version 3.11 or 3.10
* pip install -r requirements.txt
* rename keys.example.json to keys.json and add your api keys
* python main.py

### MacOS

* git clone this repo
* Set up a python virutal enviroment in python version 3.11
* pip install -r requirements.txt
* Rename keys.example.json to keys.json and add your api keys.
* python main.py

### Linux

* git clone this repo
* Set up a python virtual environment in python version 3.12+
* Install xdotool for your distro (required for window monitoring):

| Distro | Command |
| --- | --- |
| Arch / Manjaro / EndeavourOS | `sudo pacman -S xdotool` |
| Ubuntu / Debian / Linux Mint / Pop!_OS | `sudo apt install xdotool` |
| Fedora | `sudo dnf install xdotool` |
| openSUSE | `sudo zypper install xdotool` |
| Gentoo | `sudo emerge x11-misc/xdotool` |
| Void Linux | `sudo xbps-install -S xdotool` |
| NixOS | `nix-env -iA nixpkgs.xdotool` |

> **Note:** xdotool requires X11. If you are on Wayland, install `lswt` instead for window detection.

**Wayland users:** Install `lswt`:

| Distro | Command |
| --- | --- |
| Arch / Manjaro / EndeavourOS (AUR) | `yay -S lswt` |
| Ubuntu / Debian / Fedora / others | build from source: `sr.ht/~leon_plickat/lswt` |

> **Note:** Window detection on Wayland requires your compositor to expose the activated window state. This works on sway and Hyprland. COSMIC currently does not expose this, so window detection will not work on COSMIC Wayland.

* pip install -r requirements.txt
* Rename keys.example.json to keys.json and add your api keys.
* python main.py

## Goals

* [ ] Allow custom png images to talk for characters
* [ ] Add more models ( open router, xai, etc)
* [ ] Add more tts options

## Wiki

Work in progresss

## Feature Request

Work in progress

## Inspired

Inspired by [caysdontlikecoffee](https://www.instagram.com/catsdontlikecoffee/) on instagram who also did the same but for Minecraft only.
