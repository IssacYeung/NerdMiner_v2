#!/usr/bin/env python3
"""
UF2 Conversion Script
Converts binary files to UF2 format for USB bootloader flashing
Based on Microsoft's UF2 specification
"""
import sys
import struct
import subprocess
import re
import os
import os.path
import argparse

UF2_MAGIC_START0 = 0x0A324655  # "UF2\n"
UF2_MAGIC_START1 = 0x9E5D5157  # Randomly selected
UF2_MAGIC_END = 0x0AB16F30     # Ditto

INFO_FILE = "/INFO_UF2.TXT"

appstartaddr = 0x2000
familyid = 0x0


def is_uf2(buf):
    w = struct.unpack("<II", buf[0:8])
    return w[0] == UF2_MAGIC_START0 and w[1] == UF2_MAGIC_START1


def convert_from_uf2(buf):
    global appstartaddr
    numblocks = len(buf) // 512
    curraddr = None
    outp = b""
    for blockno in range(numblocks):
        ptr = blockno * 512
        block = buf[ptr:ptr + 512]
        hd = struct.unpack(b"<IIIIIIII", block[0:32])
        if hd[0] != UF2_MAGIC_START0 or hd[1] != UF2_MAGIC_START1:
            print("Skipping block at " + str(ptr) + "; bad magic")
            continue
        if hd[2] & 1:
            # NO-flash flag set; skip block
            continue
        datalen = hd[4]
        if datalen > 476:
            assert False, "Invalid UF2 data size at " + str(ptr)
        newaddr = hd[3]
        if curraddr == None:
            appstartaddr = newaddr
            curraddr = newaddr
        padding = newaddr - curraddr
        if padding < 0:
            assert False, "Block out of order at " + str(ptr)
        if padding > 10 * 1024 * 1024:
            assert False, "More than 10M of padding needed at " + str(ptr)
        if padding % 4 != 0:
            assert False, "Non-word padding size at " + str(ptr)
        while padding > 0:
            padding -= 4
            outp += b"\x00\x00\x00\x00"
        outp += block[32:32 + datalen]
        curraddr = newaddr + datalen
    return outp


def convert_to_carray(file_content):
    outp = "const unsigned long bindata_len = %d;\n" % len(file_content)
    outp += "const unsigned char bindata[] __attribute__((aligned(16))) = {"
    for i in range(len(file_content)):
        if i % 16 == 0:
            outp += "\n"
        outp += "0x%02x, " % file_content[i]
    outp += "\n};\n"
    return bytes(outp, "utf-8")


def convert_to_uf2(file_content):
    global familyid
    datapadding = b""
    while len(datapadding) < 512 - 256 - 32 - 4:
        datapadding += b"\x00\x00\x00\x00"
    numblocks = (len(file_content) + 255) // 256
    outp = b""
    for blockno in range(numblocks):
        ptr = 256 * blockno
        chunk = file_content[ptr:ptr + 256]
        flags = 0x0
        if familyid:
            flags |= 0x2000
        hd = struct.pack(b"<IIIIIIII",
                         UF2_MAGIC_START0, UF2_MAGIC_START1,
                         flags, ptr + appstartaddr, 256, blockno, numblocks, familyid)
        while len(chunk) < 256:
            chunk += b"\x00"
        block = hd + chunk + datapadding + struct.pack(b"<I", UF2_MAGIC_END)
        assert len(block) == 512
        outp += block
    return outp


def main():
    global appstartaddr, familyid
    parser = argparse.ArgumentParser(description='Convert to UF2 or flash directly.')
    parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                        help='input file (BIN)')
    parser.add_argument('-b', '--base', dest='base', type=str,
                        default="0x2000",
                        help='set base address of application for BIN format (default: 0x2000)')
    parser.add_argument('-f', '--family', dest='family', type=str,
                        default="0x0",
                        help='specify familyID - number or name')
    parser.add_argument('-o', '--output', metavar="FILE", dest='output', type=str,
                        help='write output to named file; defaults to "flash.uf2" or "flash.bin" where sensible')
    parser.add_argument('-c', '--convert', dest='convert', action='store_true',
                        help='do not flash, just convert')
    parser.add_argument('-C', '--carray', dest='carray', action='store_true',
                        help='convert binary file to a C array, not UF2')
    args = parser.parse_args()

    appstartaddr = int(args.base, 0)

    families = {
        'SAMD21': 0x68ed2b88,
        'SAML21': 0x1851780a,
        'SAMD51': 0x55114460,
        'NRF52': 0x1b57745f,
        'STM32F1': 0x5ee21072,
        'STM32F4': 0x57755a57,
        'ATMEGA32': 0x16573617,
        'MIMXRT10XX': 0x4fb2d5bd,
        'STM32F2': 0x5d1a0a2e,
        'STM32F407': 0x6db66082,
        'STM32G0': 0x300f5633,
        'STM32L4': 0x00ff6919,
        'ESP32S2': 0xbfdd4eee,
        'ESP32S3': 0xc47e5767,
        'ESP32C3': 0x1c3f10ab,
        'RP2040': 0xe48bff56,
    }

    if args.family.upper() in families:
        familyid = families[args.family.upper()]
    else:
        try:
            familyid = int(args.family, 0)
        except ValueError:
            print("Family ID needs to be a number or one of:", families.keys())
            sys.exit(1)

    if not args.input:
        print("No input file specified")
        sys.exit(1)

    with open(args.input, mode='rb') as f:
        inpbuf = f.read()

    if is_uf2(inpbuf):
        outbuf = convert_from_uf2(inpbuf)
        extension = ".bin"
    elif args.carray:
        outbuf = convert_to_carray(inpbuf)
        extension = ".h"
    else:
        outbuf = convert_to_uf2(inpbuf)
        extension = ".uf2"

    if args.output == None:
        args.output = os.path.splitext(args.input)[0] + extension
    
    with open(args.output, "wb") as f:
        f.write(outbuf)
    
    print("Wrote %d bytes to %s" % (len(outbuf), args.output))


if __name__ == "__main__":
    main()
