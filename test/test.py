# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from nes import NES_Controller

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge
from tqv import TinyQV

# When submitting your design, change this to 16 + the peripheral number
PERIPHERAL_NUM = 16 


@cocotb.test()
async def test_sanity(dut):
    dut._log.info("Start")
    nes = NES_Controller(dut)
    # Set the clock period to 16 ns (~64 MHz)
    clock = Clock(dut.clk, 16, units="ns")
    cocotb.start_soon(clock.start())

    dut._log.info("Test project behavior")
    cocotb.start_soon(nes.model_nes())

    tqv = TinyQV(dut, PERIPHERAL_NUM)
    await tqv.reset()

    pressed_button = nes.press()

    await ClockCycles(dut.clk, 10)

    # wait for a full timer cycle for the input to be registerd
    await Timer(210, units="us")
    
    # The following assertion is just an example of how to check the output values.
    # Map pressed_button to a binary value in descending powers of 2 from 128
    
    # Active low buttons
    button_map = {
        "A":     0b01111111,
        "B":     0b10111111,
        "Select":0b11011111,
        "Start": 0b11101111,
        "Up":    0b11110111,
        "Down":  0b11111011,
        "Left":  0b11111101,
        "Right": 0b11111110
    }

    dut._log.info(f"Read value from std_buttons: {button_map[pressed_button]:08b}")
    assert await tqv.read_reg(1) == button_map[pressed_button]

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
