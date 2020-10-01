# MiniNDN examples

## Repository

This repository contains a list of examples for [MiniNDN](https://github.com/named-data/mini-ndn), a [Mininet](https://github.com/mininet/mininet) extension that enables support for [Named Data Networking](https://named-data.net/) nodes.

The domain in `domains/` is derived by the [NASA access log dataset](https://www.kaggle.com/souhagaa/nasa-access-log-dataset), converting HTTP URLs to NDN content names.

At the moment of writing, MiniNDN only supports Python2. To simplify deployment, the two executables in `executables/` are written with Python2 in mind. For better Python3 implementations look into [PyNDN examples](https://github.com/named-data/PyNDN2).

## Setup

### Named Data Networking

MiniNDN uses the local installed binaries of NDN, a complete installation of `ndn-cxx` and `NFD` is necessary. For simpler and faster topology setup install `NLSR`, a service discovery service.

#### Debian based (Ubuntu, ecc...) and Fedora

Follow the installation instructions on the [mini-ndn project page](https://github.com/named-data/mini-ndn).

#### Arch Linux based

Install the packet [`mini-ndn-git`](https://aur.archlinux.org/packages/mini-ndn-git/) from the AUR. All the necessary dependent packets should be present.

### Python2

Install the required packages using `pip2 install -r requirements.txt`.

To keep your setup clean use virtualenv `virtualenv2 --system-site-packages venv` and activate the environment with `source venv/bin/activate`.
Then run the command `pip2 install -r requirements.txt` as above.