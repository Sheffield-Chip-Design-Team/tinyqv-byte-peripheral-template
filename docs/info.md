<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

The peripheral index is the number TinyQV will use to select your peripheral.  You will pick a free
slot when raising the pull request against the main TinyQV repository, and can fill this in then.  You
also need to set this value as the PERIPHERAL_NUM in your test script.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

# NES/SNES Receiver

Author: Kwashie Andoh, James Ashie Kotey

Peripheral index: 15

## What it does

This peripheral provides a memory-mapped interface for reading NES and SNES gamepad controller states on the TinyQV RISC-V microcontroller. The design automatically detects which controller type is connected and exposes debounced button states through memory-mapped registers.

For complete technical specification, see the [full documentation](https://docs.google.com/document/d/1l_B4vgzqy5NGJJAfXMa3Ju-xB-0VwFmkBfVjibhVOlY/edit?usp=sharing).

**Key Features**
- Supports both NES (8 buttons) and SNES (12 buttons) controllers
- Auto-detection between controller types (falls back to NES if SNES not present)
- Single controller support (either 1 NES or 1 SNES at a time)
- The SNES interface uses [CH32V003-based SNES-compatible controller interface PMOD](https://store.tinytapeout.com/products/Gamepad-Pmod-board-p741891425)
- Clean memory-mapped interface with status and button registers
- Compatible with TinyQV demoboard I/O constraints (3.3V, inputs not 5V tolerant)

## Register map

| Address | Name        | Access | Description                                                         |
|---------|-------------|--------|---------------------------------------------------------------------|
| 0x00    | STD_BTNS    | R      | NES buttons (UP,DOWN,LEFT,RIGHT,B,A, START,SELECT)                  |
| 0x01    | EXT_BTNS    | R      | Additional SNES buttons (X,Y,L,R)                                   |
| 0x02    | STATUS      | R      | A single bit showing whether a snes controller has been connected   |

### Standard Buttons Register (0x01)
| Bit | Button | Description        |
|-----|--------|--------------------|
| 7   | A      | A button (1=pressed) |
| 6   | B      | B button (1=pressed) |
| 5   | Select | Select button (1=pressed) |
| 4   | Start  | Start button (1=pressed) |
| 3   | Up     | Up button (1=pressed) |
| 2   | Down   | Down button (1=pressed) |
| 1   | Left   | Left button (1=pressed) |
| 0   | Right  | Right button (1=pressed) |

### SNES Extended Buttons Register (0x02)
| Bit | Button | Description        |
|-----|--------|--------------------|
| 7-4 | Reserved | Always 0        |
| 3   | X      | X button (1=pressed) |
| 2   | Y      | Y button (1=pressed) |
| 1   | L      | L button (1=pressed) |
| 0   | R      | R button (1=pressed) |

*Note: SNES extended buttons read as 0 when NES controller is active*

## How to test

Plug in the SNES PMOD + Controller or NES controller + adapter and read the associated data address:

1. **Basic Controller Detection:**
   - Read address 0x00 to check controller status
   - Bit 0: 1 = SNES detected, 0 = NES mode

2. **Button Reading:**
   - Read address 0x01 for standard 8-button state
   - Read address 0x02 for SNES extended buttons (if SNES active)
   - Button state: 1 = pressed, 0 = released

- **Example Code:**
   ```c
   // Check controller type
   uint8_t status = read_peripheral(0x00);
   bool is_snes = (status & 0x01);
   
   // Read standard buttons
   uint8_t buttons = read_peripheral(0x01);
   bool a_pressed = (buttons & 0x80);
   bool start_pressed = (buttons & 0x10);
   
   // Read SNES extended buttons (if applicable)
   if (is_snes) {
       uint8_t ext_buttons = read_peripheral(0x02);
       bool x_pressed = (ext_buttons & 0x08);
   }
   ```

## External hardware

**For NES Controller:**
- Standard NES gamepad + Adapter
- 3 wire connection: Data (ui_in[1]), Latch (uo_out[6]), Clock (uo_out[7])

**For SNES Controller:**  
- SNES gamepad
- CH32V003-based SNES-compatible controller interface PMOD  
  (Available at: https://github.com/psychogenic/gamepad-pmod)
- 3 wire PMOD connection: Data (ui_in[2]), Clock (ui_in[3]), Latch (ui_in[4])

## Verification Plan

The peripheral verification included multiple stages to ensure robust operation:

**FPGA Prototyping:**
- Real hardware validation on both NES and SNES controllers
- Recorded demonstration videos available: [NES FPGA Test](https://drive.google.com/file/d/1BqGLOE_gKf2GouaVBYqFd00kkwdsnnQ2/view?usp=sharing)
[SNES FPGA Test](https://drive.google.com/file/d/1PY9-svxJRjp5iImp9vOvUZB5ECgRoXVd/view?usp=sharing)


**Constrained Random Testing:**
- 100-test regression using custom cocotb framework
- Random button press/release sequences at random timing
- Achieved 100% line coverage, 31% toggle coverage, 72% combinational logic coverage

