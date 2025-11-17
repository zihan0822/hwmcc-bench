#!/usr/bin/env python3

import subprocess
from pathlib import Path


def experiments_with_default_pattern(names):
    return [(name, f"*{name}*") for name in names]

run = experiments_with_default_pattern(
    [
        "picorv32_mut",
        "marlann",
        "zipcpu_zipcpu_piped",
        "zipcpu_zipcpu_dcache",
        "ridecore_array",
        "arbitrated_fifos",
    ]
)

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)
duration = 10

for name, pattern in run:
    print(f"Running {name} with file search pattern {pattern}")

    # Build the full shell command
    cmd = (
        f'find build -name "{pattern}" -executable | '
        f"xargs python3 spin-util-sig-term.py "
        f"-t {duration} "
        f'-r "simulation cycle:\\s*(-?\\d+)"'
    )

    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)

    (results_dir / f"{name}.out").write_text(result.stdout)
