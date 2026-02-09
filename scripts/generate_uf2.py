#!/usr/bin/env python3
"""
Extra script for PlatformIO to generate UF2 files after build
"""
import os
import sys
from os.path import join

Import("env")

def generate_uf2(source, target, env):
    """Generate UF2 file from firmware binary"""
    firmware_bin = str(target[0])
    firmware_uf2 = firmware_bin.replace(".bin", ".uf2")
    
    # Get the board type to determine the correct family ID
    board = env.get("BOARD", "")
    
    # Determine family ID based on board
    family_id = "0x0"
    base_addr = "0x0000"  # Default base address for ESP32
    
    if "esp32-s2" in board or "ESP32-S2" in str(env.get("BUILD_FLAGS", [])):
        family_id = "ESP32S2"
        base_addr = "0x1000"
    elif "esp32-s3" in board or "ESP32-S3" in str(env.get("BUILD_FLAGS", [])):
        family_id = "ESP32S3"
        base_addr = "0x0000"
    elif "esp32-c3" in board or "ESP32-C3" in str(env.get("BUILD_FLAGS", [])):
        family_id = "ESP32C3"
        base_addr = "0x0000"
    elif "esp32" in board:
        # Regular ESP32 doesn't support UF2 by default, skip
        print("Skipping UF2 generation for regular ESP32 (not supported)")
        return
    
    # Path to uf2conv.py script
    uf2conv_path = join(env.get("PROJECT_DIR"), "scripts", "uf2conv.py")
    
    if not os.path.exists(uf2conv_path):
        print("Warning: uf2conv.py not found at", uf2conv_path)
        return
    
    # Generate UF2 file
    print("Generating UF2 file...")
    print(f"  Input: {firmware_bin}")
    print(f"  Output: {firmware_uf2}")
    print(f"  Family: {family_id}")
    print(f"  Base address: {base_addr}")
    
    cmd = [
        sys.executable,
        uf2conv_path,
        firmware_bin,
        "-c",
        "-f", family_id,
        "-b", base_addr,
        "-o", firmware_uf2
    ]
    
    env.Execute(" ".join(cmd))
    print(f"UF2 file generated: {firmware_uf2}")

# Add post action to generate UF2 after building the firmware
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", generate_uf2)
