/*
 * Copyright (c) 2025 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Change the name of this module to something that reflects its functionality and includes your name for uniqueness
// For example tqvp_yourname_spi for an SPI peripheral.
// Then edit tt_wrapper.v line 38 and change tqvp_example to your chosen module name.
module tqvp_nes_snes_controller (
    input         clk,          // Clock - the TinyQV project clock is normally set to 64MHz.
    input         rst_n,        // Reset_n - low to reset.

    input  [7:0]  ui_in,        // The input PMOD, always available.  Note that ui_in[7] is normally used for UART RX.
                                // The inputs are synchronized to the clock, note this will introduce 2 cycles of delay on the inputs.

    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected.
                                // Note that uo_out[0] is normally used for UART TX.

    input [3:0]   address,      // Address within this peripheral's address space

    input         data_write,   // Data write request from the TinyQV core.
    input [7:0]   data_in,      // Data in to the peripheral, valid when data_write is high.
    
    output [7:0]  data_out      // Data out from the peripheral, set this in accordance with the supplied address
);

    wire [7:0] standard_buttons;
    wire [3:0] extra_snes_buttons;
    wire is_snes;

    NESTest_Top nes_snes_module (

        // system
        .system_clk_64MHz(clk), // System clock from TinyQV (64MHz)
        .rst_n(rst_n),         // active low reset

        // NES controller interface [GPIO]. We generate latch and clock internally and send to controller. Data returns.
        .NES_Data(ui_in[1]), // NES controller data -> ui_in[1]
        .NES_Latch(uo_out[6]), // uo_out[6] -> NES controller latch
        .NES_Clk(uo_out[7]), // uo_out[7] -> NES controller clk

        // SNES PMOD interface [3 pins]
        .SNES_PMOD_Data(ui_in[2]),    // PMOD IO7 ->  ui_in[2] 
        .SNES_PMOD_Clk(ui_in[3]),     // PMOD IO6 ->  ui_in[3]
        .SNES_PMOD_Latch(ui_in[4]),   // PMOD IO5 ->  ui_in[4]

        // button states: to data_out[7:0] on address 0x1
        .A_out(standard_buttons[7]),
        .B_out(standard_buttons[6]),
        .select_out(standard_buttons[5]),
        .start_out(standard_buttons[4]),
        .up_out(standard_buttons[3]),
        .down_out(standard_buttons[2]),
        .left_out(standard_buttons[1]),
        .right_out(standard_buttons[0]),
        
        // Additional SNES buttons: to data_out[3:0] on address 0x2
        .X_out(extra_snes_buttons[3]),
        .Y_out(extra_snes_buttons[2]),
        .L_out(extra_snes_buttons[1]),
        .R_out(extra_snes_buttons[0]),
        
        // Status indicator: to data_out[0] on address 0x0
        .controller_status(is_snes)  // 1 = SNES active, 0 = NES active

    );

    // IO connections so far:

    // ui_in
    // NES controller data -> ui_in[1]
    // SNES_PMOD_Data ->  ui_in[2] 
    // SNES_PMOD_Clk ->  ui_in[3]
    // SNES_PMOD_Latch ->  ui_in[4]

    // uo_out
    // uo_out[6] -> NES controller latch
    // uo_out[7] -> NES controller clk

    // All output pins must be assigned. If not used, assign to 0.
    assign uo_out[5:0] = 6'b000000;
    //  BUG: TT-RV-0001 - NO_INVERT
    assign data_out = (address == 4'h0) ? {7'b0000, is_snes} :
                      (address == 4'h1) ? standard_buttons :
                      (address == 4'h2) ? {4'b0000, extra_snes_buttons} :
                      8'h0;

endmodule
