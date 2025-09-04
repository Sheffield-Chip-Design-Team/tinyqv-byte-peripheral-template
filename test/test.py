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

    nes.press('A')

    await ClockCycles(dut.clk, 10)

    # wait for a full timer cycle for the input to be registerd
    await Timer(300, units="us")
    
    # The following assertion is just an example of how to check the output values.

    assert await tqv.read_reg(1) == 0b10000000
    

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
