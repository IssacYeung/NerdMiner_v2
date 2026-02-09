# UF2 Firmware Support

## Overview

This repository now supports generating UF2 (USB Flashing Format) firmware files for ESP32-S3 and ESP32-C3 based boards. UF2 is a file format developed by Microsoft for flashing microcontrollers over USB Mass Storage Class (MSC).

## Supported Boards

The following environments automatically generate UF2 files during build:

### ESP32-S3 Boards
- `ESP32-S3-mini-wemos`
- `ESP32-S3-mini-weact`
- `ESP32-S3-devKitv1`
- `NerminerV2` (ESP32-S3 based)
- `Lilygo-T-Embed` (ESP32-S3 based)
- `NerminerV2-S3-AMOLED`
- `NerminerV2-S3-DONGLE`
- `NerminerV2-T-QT` (ESP32-S3 based)
- `M5-StampS3`

### ESP32-C3 Boards
- `ESP32-C3-super-mini`
- `ESP32-C3-devKitmv1`

## How It Works

When you build the firmware using PlatformIO, the build system:

1. Compiles the firmware and generates `.bin` files (standard process)
2. Automatically runs `scripts/generate_uf2.py` as a post-build action
3. Uses `scripts/uf2conv.py` to convert the firmware `.bin` to `.uf2` format
4. Outputs both `.bin` and `.uf2` files in the build directory

## Building Firmware with UF2

### Using PlatformIO CLI

```bash
# Build all environments (generates both .bin and .uf2 for supported boards)
pio run

# Build specific environment
pio run -e M5-StampS3

# Build output location
ls .pio/build/M5-StampS3/firmware.bin
ls .pio/build/M5-StampS3/firmware.uf2
```

### Using PlatformIO IDE

1. Open the project in PlatformIO IDE
2. Select your target environment
3. Click "Build"
4. Both `.bin` and `.uf2` files will be in `.pio/build/<environment>/`

## Flashing with UF2

### Prerequisites

Your board must have a UF2-compatible bootloader (such as TinyUF2) installed. Most modern ESP32-S3 and ESP32-C3 boards with native USB support can use UF2.

### Flashing Process

1. **Enter bootloader mode:**
   - Hold the BOOT button on your board
   - While holding BOOT, press and release the RESET button (or plug in USB)
   - Release the BOOT button
   - The board should appear as a USB drive (e.g., "ESP32S3-UF2" or similar)

2. **Flash the firmware:**
   - Locate the `.uf2` file in `.pio/build/<environment>/firmware.uf2`
   - Drag and drop the `.uf2` file to the USB drive
   - The board will automatically flash and reboot

3. **Verify:**
   - After flashing completes, the board will restart automatically
   - The USB drive will disappear
   - Your NerdMiner should boot with the new firmware

## Manual UF2 Conversion

If you need to manually convert a `.bin` file to `.uf2` format:

```bash
# For ESP32-S3 boards
python3 scripts/uf2conv.py firmware.bin -c -f ESP32S3 -b 0x0000 -o firmware.uf2

# For ESP32-C3 boards
python3 scripts/uf2conv.py firmware.bin -c -f ESP32C3 -b 0x0000 -o firmware.uf2
```

## Troubleshooting

### Board doesn't appear as USB drive

- Make sure your board has TinyUF2 or compatible bootloader installed
- Try a different USB cable (must support data, not just power)
- Try a different USB port
- Some boards require specific button combinations to enter bootloader mode

### UF2 file not generated during build

- Verify you're building an ESP32-S3 or ESP32-C3 environment
- Check that `scripts/generate_uf2.py` and `scripts/uf2conv.py` are present
- Regular ESP32 (non-S3/C3) boards don't support UF2 by default

### Flash fails or board doesn't boot

- Verify you're using the correct `.uf2` file for your board model
- Try flashing using the traditional `.bin` method with esptool
- Check that the base address in the UF2 conversion is correct

## Benefits of UF2

- **No drivers needed:** Works with standard USB Mass Storage drivers
- **Cross-platform:** Works on Windows, macOS, and Linux without special tools
- **Simple process:** Just drag and drop the file
- **Fast:** Quick flashing compared to serial methods
- **Reliable:** Less prone to timing issues than serial flashing

## Additional Resources

- [UF2 File Format Specification](https://github.com/microsoft/uf2)
- [TinyUF2 Bootloader](https://github.com/adafruit/tinyuf2)
- [ESP32-S3 USB Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/usb-otg-console.html)
