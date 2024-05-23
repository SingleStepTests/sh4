# sh4 JSON tests
If you've used TomHarte-style JSON tests before, this may be familiar to you.

This repository hosts a bunch of tests for an SH4 CPU emulator. It was generated using Reicast's CPU interpreter, using the branch raddad_testgen on https://github.com/ncarrillo/reicast .

This only tests the basic functionality of all the valid SH4 encodings, minus PREF, MACL, and MACH, since the test format only supports one read or write per instruction (aside from instruction fetches). Enough to get you through the BIOS and into some games, at least.

You must run transcode_json.py after pulling the tests. This will translate the .json.bin format into .json format to easily work with. If you wish to use the binary representation, the .py file should document it fairly clearly.

Each .JSON file represents a valid encoding for an instruction, plus the PR and SZ bits for this.

Each tests has a list with 500 entries that look like this (this is from 0110nnnnmmmm0000_sz0_pr0.json):

```json
  {
    "initial": {
      "R": [
        0,
        607951292,
        339404701,
        2903317062,
        3603374455,
        2439438834,
        656238375,
        2611285952,
        3165037489,
        3242538682,
        4159368018,
        2019566466,
        3718168823,
        2904868278,
        4280931894,
        2562944062
      ],
      "R_": [
        4,
        1565497588,
        2722264310,
        4278977379,
        3459672999,
        2851628040,
        395136730,
        3792091456
      ],
      "FP0": [
        8699888,
        2903412715,
        703702668,
        3201454075,
        3781873168,
        3626478839,
        1399497680,
        869405182,
        1414502100,
        313840832,
        3927151297,
        332055238,
        1445018913,
        3328684589,
        2937712015,
        1318836025
      ],
      "FP1": [
        4262583999,
        1881134429,
        1476219139,
        441998510,
        1817142444,
        62002743,
        429963413,
        1927115332,
        3320426796,
        97644723,
        3526939960,
        2886081679,
        4178119026,
        3354311430,
        305185032,
        3127902481
      ],
      "PC": 212597368,
      "GBR": 1993771878,
      "SR": 1610613682,
      "SSR": 2244073807,
      "SPC": 17043104,
      "VBR": 3216387433,
      "SGR": 2389929555,
      "DBR": 1338537593,
      "MACL": 1988875386,
      "MACH": 1752903741,
      "PR": 3933907350,
      "FPSCR": 2359298
    },
    "final": {
      "R": [
        0,
        1215902584,
        339404701,
        2903317062,
        3603374455,
        2439438834,
        656238375,
        2611285952,
        3165037489,
        3242538682,
        4294967283,
        2019566466,
        3718168823,
        2904868278,
        4280931894,
        2562944062
      ],
      "R_": [
        4,
        1565497588,
        2722264310,
        4278977379,
        3459672999,
        2851628040,
        395136730,
        3792091456
      ],
      "FP0": [
        8699888,
        2903412715,
        703702668,
        3201454075,
        3781873168,
        3626478839,
        1399497680,
        869405182,
        1414502100,
        313840832,
        3927151297,
        332055238,
        1445018913,
        3328684589,
        2937712015,
        1318836025
      ],
      "FP1": [
        4262583999,
        1881134429,
        1476219139,
        441998510,
        1817142444,
        62002743,
        429963413,
        1927115332,
        3320426796,
        97644723,
        3526939960,
        2886081679,
        4178119026,
        3354311430,
        305185032,
        3127902481
      ],
      "PC": 212597376,
      "GBR": 1993771878,
      "SR": 1610613682,
      "SSR": 2244073807,
      "SPC": 17043104,
      "VBR": 3216387433,
      "SGR": 2389929555,
      "DBR": 1338537593,
      "MACL": 1988875386,
      "MACH": 1752903741,
      "PR": 3933907350,
      "FPSCR": 2359298
    },
    "cycles": [
      {
        "actions": 4,
        "fetch_addr": 38654705664,
        "fetch_val": 18446744069414584320
      },
      {
        "actions": 4,
        "fetch_addr": 117166707834880,
        "fetch_val": 18446744069414584320
      },
      {
        "actions": 5,
        "fetch_addr": 53996328845312,
        "fetch_val": 18446744069414584320,
        "read_addr": 1043677052928,
        "read_val": 17179869184
      },
      {
        "actions": 4,
        "fetch_addr": 38654705664,
        "fetch_val": 18446744069414584320
      }
    ],
    "opcodes": [
      9,
      27280,
      12572,
      9,
      12844
    ]
  }
```

At the high level, there are the following entries:

'initial' and 'final', which represent processor state before and after the tests, and include many of the registers.

'opcodes', which lists the opcodes as they are fetched from memory (more on this lower, it works a little differently than you'd expect.)

And finally, 'cycles', which lists what happened on each cycle. Except fetch_val appears bugged right now. The 'actions' in each cycle is a bitmask, where bit 1 is read, 2 is write, and 4 is instruction fetch.

Note that this assumes no real pipeline, though delay slots are tested for and supported.

The opcodes in any give test go like this:

NOP          <-- start off with a NOP
opcode       <-- run our opcode
ADD R1, R1   <-- this will be in a delay slot, thus allowing detection of whether or not a delay slot is executed after an instruction
NOP          <-- this allows the last instruction to not be a delay-slot
ADD R2, R2   <-- if a branch is taken or PC goes haywire, this should also give us a difference, since it is always provided to anything not in the normal instruction flow

The first 4 are provided for the first 4 instruction fetches, starting at PC; the last one is provided for any instruction fetch anywhere else in memory.

To run the test, set your CPU up by the initial state, run 4 cycles, and compare to the end state. Also compare what happens each instruction/cycle, to what your emulator does.

Pseudocode for making use of these:

```
read_instruction(test, addr) {
    if addr != test.cycles[test.cpu.cycle_number].fetch_addr]): alert issue
    num = (addr - test.base_addr) / 2;
    if ((num >= 0) && (num <= 3)): return test.opcodes[num];
    return test.opcodes[4];
}

read_ram(test, addr) {
    if test.read_addr != addr: alert issue
    test.did_read = true;
    return test.read_val
}

write_ram(test, addr, val) {
    if test.write_addr != addr: alert issue
    if test.write_val != val: alert issue
    test.did_write = true
}

do_test(test, cpu) {
    copy test initial state to CPU;
    cpu.ins_fetch = &read_instruction;
    cpu.read_mem = &read_ram;
    cpu.write_mem = &write_ram;
    
    test.base_addr = test.initial.PC;
    test.did_write = test.did_read = false;
    
    cpu.run_cycles(4);
    
    if (!compare_cpu_state_to_final(cpu, test.final)): raise alert;
    if (!check_reads_and_writes(test, test.cycles)): raise alert;
}

// Test that any reads or writes that were supposed to happen, did happen
check_reads_and_writes(test, cycles) {
    if (test.did_write != cycles_have_a_write(cycles)): raise alert;
    if (test.did_read != cycles_have_a_read(cycles)): raise alert;
}

```

Disclaimers:

* The tests do not properly restrict reads and writes to byte-alignment, other than instructions.
* The tests treat RAM as a 32-bit flat space with no memory-mapped registers.
* The tests may have bugs, this is an in-development release v0.1
* This was developed by hacking parts of my emulator (jsmooch-emus) into Reicast. There may be issues with the tests we don't know yet.
* Toggling RB causes the first 8 registers in R and R_ to actually swap, instead of updating some internal reference to them. That's how the 4 emulators I know of do it, so the test does too.

I hope you find it useful!
