# RISC-V-Obfuscation
- Created by Quinn, Taylor, Finn and Josiah
- Inspired by the [RISC-Y Business](https://secret.club/2023/12/24/riscy-business.html) project

## Quick Start
```bash
PASSWORD=RISCVCRACK make
./crack_x86 # crack me!
```

## Pipeline
1. `create.py`
    - Calculates six checksums (linear constraints) that accept the password
    - Trains a small neural network to accept the password
    - Writes the checksums and neural network to `main.c`
2. `main.c` is compiled to `crack_riscv`
3. `obfuscate.py`
    - Randomly shuffles the opcodes in `crack_riscv` and saves the result to `crack_riscv_patch`
    - Uses a hardcoded AES key to encrypt `crack_riscv_patch` to the binary blob `crack_riscv_enc`
    - Writes the shuffled opcode map to `shuffle.h` for use in the emulator
4. `crack_riscv_enc` and `shuffle.h` are embedded in a [RISC-V emulator](https://github.com/ksco/rvemu) and compiled to `crack_x86`
    - When run, the emulator decrypts the blob and un-shuffles the opcodes with JIT translation
5. `solve.py` verifies that the challenge is solvable
    - Solves the six checksums, reducing the search space from 30^10 to ~100 passwords
    - Checks each password against `crack_x86` ensuring the neural net only accepts the correct password
6. `crack_x86` is the final obfuscated binary for distribution

## Setup
```bash
# Build
docker build -t riscv-image .
docker compose up -d
docker exec -it riscv-container /bin/bash
PASSWORD=RISCVCRACK make

# Crack Me!
./crack_x86

# Testing
chmod 777 crack_riscv*
qemu-riscv64 ./crack_riscv
qemu-riscv64 ./crack_riscv_patch # should fail with illegal instruction
qemu-riscv64 ./crack_riscv_enc # should fail with exec format error

# Disassemble
riscv64-linux-gnu-objdump -D ./crack_riscv > crack_riscv.dis
ndisasm -b 64 ./crack_x86 > crack_x86.dis

# Cleanup
make clean
docker compose down
```
