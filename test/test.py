# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

from random import randint
import cocotb
from nes import NES_Controller

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge
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
    await Timer(randint(200, 400), units="us")

    # The following assertion is just an example of how to check the output values.
    # Map pressed_button to a binary value in descending powers of 2 from 128
    
    # Active high output
    button_map = {
        "A":     0b10000000,
        "B":     0b01000000,
        "Select":0b00100000,
        "Start": 0b00010000,
        "Up":    0b00001000,
        "Down":  0b00000100,
        "Left":  0b00000010,
        "Right": 0b00000001
    }

    while True:
        # Wait for the complete transmission cycle
        await FallingEdge(dut.nes_latch)
        await RisingEdge(dut.nes_latch)
        await RisingEdge(dut.nes_latch)
       
        # If no button was queued, skip this cycle
        if len( expected_buttons_pressed_list) == 0:
            continue

        expected_data_out = 0
       
        for b in expected_buttons_pressed_list:
            expected_data_out |= button_map[b]

        # Small random wait to simulate async timing
        await Timer(randint(10, 10), units="ns")

        val = await tqv.read_reg(1)
        dut._log.info(f"Async check: std_buttons={val:08b}, expected={expected_data_out:08b}")

        assert val == expected_data_out , f"Mismatch for {expected_buttons_pressed_list}"

async def random_reset(dut, tqv, weighting):
    # Wait for a random time before resetting
    while True:
        await Timer(randint(100, 500), units="us")
        if randint(1, weighting) == 1:
            dut._log.info("Applying random reset")
            await tqv.reset()
            assert await tqv.read_reg(1) == 0
            await RisingEdge(dut.nes_latch)
            dut._log.info("Reset released, clearing expected queue")


@cocotb.test()
async def test_nes(dut):
    dut._log.info("Start")
    tqv = TinyQV(dut, PERIPHERAL_NUM)
    nes = NES_Controller(dut)
    # Set the clock period to 16 ns (~64 MHz)
    clock = Clock(dut.clk, 16, units="ns")
    cocotb.start_soon(clock.start())
    cocotb.start_soon(random_reset(dut,tqv, 10))

    dut._log.info("Test project behavior")
    cocotb.start_soon(nes.model_nes())
    await tqv.reset()
    
    cocotb.start_soon(nes_scoreboard(dut,tqv))
    await nes_sequencer(dut, nes, num_presses=10)

    await ClockCycles(dut.clk, 10)

    # The following assertion is just an example of how to check the output values.
    # Map pressed_button to a binary value in descending powers of 2 from 128


    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
