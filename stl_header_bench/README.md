# STL header-only benchmark harness

This directory contains a generated benchmark suite for the CFlat C++-specific STL header-only claims. Direct libc headers such as `string.h`, `math.h`, and `stdint.h` are treated as ordinary C/POSIX usage, so C++ wrapper headers such as `<cstring>`, `<cmath>`, and `<cstdint>` are intentionally excluded.

Run:

```sh
./run.py
```

The script generates paired C++ and C facility test cases into `src_gen/`, compiles each at `-O0` and `-O2`, link-checks the C++ cases with `-nostdlib++`, emits assembly, runtime-checks C++/C parity for each pair, and writes labeled outputs such as:

- `src_gen/algorithm.sort.cpp`
- `src_gen/algorithm.sort.c`
- `src_gen/algorithm.sort.driver.cpp`
- `src_gen/algorithm.sort.driver.c`

- `build/results.clang.csv`
- `build/results.clang.md`
- `build/results.gcc.csv`
- `build/results.gcc.md`
- `STL_HEADER_ONLY_RESULTS.md`

`src_gen/` is generated but committed so benchmark inputs are reviewable. `build/` contains compiler outputs and raw result files and is ignored.

The comparison is intentionally mechanical. Assembly verdicts are based on `.text` bytes and counted assembly instructions versus the C baseline for the same facility. That is a heuristic, not proof of runtime performance. The generated report includes header summaries, facility breakdowns, and worse-than-C facility highlights.
