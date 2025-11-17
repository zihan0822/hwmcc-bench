#### BTOR2 HWMCC Benchmark
This repository contains BTOR2 files from past HWMCC competitions and is used to benchmark different BTOR2 simulators.

#### Repo Layout
* `btor2mlir-compile.sh`: Used to compile BTOR2 file into simulation executable with Btor2Mlir
* `spin-util-sig-term.py`: A simple python script that runs a simulation command for a specified duration then terminates it
by sending a SIGTERM signal. A regex string can be specified to extract the simulation cycle from stdout.
```bash
$ python3 spin-util-sig-term.py \
  -t 10 \ # run for 10s before stopping
  -r "simulation cycle:\s*(-?\d+)" \ # regex for output parsing
  <executable>
```

#### How to run
```bash
$ git submodule update --init
$ export LLVM=<path to LLVM toolchain>
$ make all # builds btor2mlir tools and produces executable for each BTOR2 file
$ ./run.py # runs selected categories and emits simulation summary in results/
```
