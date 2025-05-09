import sys
from pathlib import Path

env_path = Path(sys.argv[1])
yaml_path = Path(sys.argv[2])

with env_path.open() as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with yaml_path.open("w") as f:
    for line in lines:
        key, value = line.split("=", 1)
        f.write(f'{key}: "{value}"\n')