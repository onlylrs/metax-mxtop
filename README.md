<h1 align="center">mxtop</h1>

<p align="center">
  <a href="https://github.com/onlylrs/metax-mxtop"><img src="https://img.shields.io/github/stars/onlylrs/metax-mxtop?style=flat-square&logo=github&color=181717" alt="GitHub stars"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="MIT License"/></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/Platform-Linux-FCC624?style=flat-square&logo=linux&logoColor=black" alt="Linux"/>
  <img src="https://img.shields.io/badge/GPU-MetaX-6366f1?style=flat-square" alt="MetaX GPU"/>
</p>

<p align="center">
  <code>mxtop</code> is an nvitop-like terminal monitor for MetaX GPUs. It shows live GPU
  temperature, power, utilization, memory use, and GPU processes from MetaX
  management tooling.
</p>

<p align="center">
  <img src="assets/mxtop-light.png" alt="mxtop light ui" width="45%" style="display:inline-block; margin-right:2%;" />
  <img src="assets/mxtop-dark.png" alt="mxtop dark ui" width="45%" style="display:inline-block;" />
</p>


## Install

Install directly from GitHub:

```bash
pip install -U "git+https://github.com/onlylrs/metax-mxtop.git"
```

Or

```bash
git clone https://github.com/onlylrs/metax-mxtop.git
cd metax-mxtop
pip install -e .
```

## Usage

Open the interactive terminal dashboard:

```bash
mxtop
```

More usage and introduction, see [intro.md](INTRO.md)

### 🔥News
Thanks for great extended work [metax-mxtop](https://github.com/linkedlist771/metax-mxtop) with more features!