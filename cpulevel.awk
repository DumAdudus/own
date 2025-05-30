#!/usr/bin/awk -f

BEGIN {
    # Collect CPU features from lscpu
    cmd = "lscpu | grep 'Flags:' | awk '{for (i=2; i<=NF; i++) print $i}'"
    while (cmd | getline) {
        features = features " " $0
    }
    close(cmd)

    # Define required features for each x86-64-v level
    levels[1] = "lm cmov cx8 fpu fxsr mmx syscall sse2"
    levels[2] = "cx16 lahf_lm popcnt sse4_1 sse4_2 ssse3"
    levels[3] = "avx avx2 bmi1 bmi2 f16c fma abm movbe xsave"
    levels[4] = "avx512f avx512bw avx512cd avx512dq avx512vl"

    level = 0
    missing = ""

    # Check features for each level
    for (i = 1; i <= 4; i++) {
        level_met = 1
        split(levels[i], flags, " ")
        missing = ""
        for (j in flags) {
            if (features !~ flags[j]) {
                missing = missing flags[j] " "
                level_met = 0
            }
        }
        if (level_met == 1) {
            level = i
        } else {
            print "Current level: x86-64-v" level
            print "Missing for x86-64-v" i ": " missing
            exit i
        }
    }

    # Report the highest supported level
    print "Current level: x86-64-v" level
    exit level + 1
}