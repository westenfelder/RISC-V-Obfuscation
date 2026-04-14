FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    clang \
    xxd \
    nasm \
    vim \
    tmux \
    python3 \
    python3-pip \
    python3-venv \
    gcc-riscv64-linux-gnu \
    g++-riscv64-linux-gnu \
    gcc-riscv64-unknown-elf \
    binutils-riscv64-unknown-elf \
    qemu-user \
    qemu-system-misc \
    gdb-multiarch \
    gdb \
    gdbserver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN echo 'syntax on \n\
inoremap jj <Esc> \n\
set rnu \n\
set nu \n\
set foldmethod=marker \n\
set hlsearch' > /root/.vimrc

WORKDIR /workspace

CMD ["/bin/bash"]
