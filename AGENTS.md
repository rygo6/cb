# Repository Notes

This repository currently contains the CFlat notes in `CFLAT.md` and an untracked benchmark workspace in `stl_header_bench/`.

## STL Header Benchmark

The active work is in `stl_header_bench/`. Its purpose is to compare C++ STL header-only facilities against semantically matched C equivalents for the CFlat header-only claim.

Important files:

- `stl_header_bench/run.py`: benchmark generator, compiler runner, CSV/Markdown reporter.
- `stl_header_bench/STL_HEADER_ONLY_RESULTS.md`: generated combined report from the latest clang and GCC runs.
- `stl_header_bench/README.md`: short usage notes.
- `stl_header_bench/build/results.clang.csv`: latest clang raw results.
- `stl_header_bench/build/results.clang.md`: latest clang Markdown table.
- `stl_header_bench/build/results.gcc.csv`: latest GCC raw results.
- `stl_header_bench/build/results.gcc.md`: latest GCC Markdown table.

The whole `stl_header_bench/` directory is currently untracked.

## How To Run

From repo root:

```sh
./stl_header_bench/run.py --cxx clang++ --cc clang --label clang
./stl_header_bench/run.py --cxx g++ --cc gcc --label gcc --keep-build
```

The first command normally removes `stl_header_bench/build/`. The second uses `--keep-build` so clang artifacts remain and the final combined report includes both compilers.

`run.py` also accepts:

- `--repeats N`: median compile time over N runs, default `3`.
- `--keep-build`: do not remove the build directory before running.
- `--label LABEL`: controls output names `results.LABEL.csv` and `results.LABEL.md`.

## Harness Design

Each benchmark case has:

- a C++ source using a specific STL header or facility
- a C source intended to be a semantically matched equivalent
- an `O0` and `O2` compile
- generated assembly for instruction counting
- object `.text` size measurement using `size`
- a C++ `-nostdlib++` link check
- a runtime parity check at `n=7`, comparing the C++ return value against the C return value

Measured object files contain only the benchmark function. Tiny generated drivers are used only for runtime parity and link checks.

The final report includes:

- facility coverage
- per-header summaries
- per-facility breakdowns
- worse-than-C facility highlights

## Verdicts

Verdicts are based on `O2` `.text` and counted instruction ratios:

- `Precisely C`: within 1 percent of C
- `Approximately C`: within 5 percent of C
- `Near C`: within 25 percent of C
- `Some overhead`: up to 2x C
- `Worse assembly`: more than 2x C
- `Does not link`: fails the CFlat `-nostdlib++` link check

Do not reintroduce the old `C-equivalent` label. It was renamed to `Approximately C`, with the stricter `Precisely C` category added.

## Current Coverage Shape

Most headers still have one broad `*.combined` case with explicit operation metadata. The headers below were refactored into facility-level subcases because the previous one-case-per-header design could not identify the specific worse API:

- `<array>`: `array.front_back_size_data`, `array.index_iteration`
- `<algorithm>`: `algorithm.sort`, `algorithm.min_max_element`, `algorithm.binary_search`, `algorithm.clamp`
- `<atomic>`: `atomic.store_load_fetch_add`, `atomic.compare_exchange`, `atomic.exchange`

If more headers are investigated, prefer adding subcases named `header.facility` rather than expanding a combined case.

## Known Baseline Fixes Already Applied

These old mismatches were fixed in `run.py` and should not be regressed:

- `<array>` C baseline now mutates front/back before summing, matching C++.
- `<concepts>` C baseline no longer has the extra `+3`.
- `<functional>` C baseline includes the `std::hash<int>{}(3)` contribution, represented as `+3`.
- `<algorithm>` C baseline includes equivalents for `min_element`, `max_element`, `binary_search`, and the second `clamp`.

## Latest Audit Results

After the latest clang and GCC runs:

- Each compiler produced 60 rows: 30 `O0`, 30 `O2`.
- All `O2` rows compile, link, and runtime-match the C baseline.
- The only failures are expected `O0` `-nostdlib++` link failures for:
  - `string_view.combined`
  - `bitset.combined`

Latest worse-than-C `O2` facility rows:

- clang:
  - `algorithm.min_max_element`: `Some overhead`
  - `atomic.store_load_fetch_add`: `Worse assembly`
  - `atomic.compare_exchange`: `Worse assembly`
  - `atomic.exchange`: `Worse assembly`
- GCC:
  - `initializer_list.combined`: `Worse assembly`
  - `span.combined`: `Worse assembly`
  - `new.combined`: `Worse assembly`
  - `array.index_iteration`: `Worse assembly`
  - `algorithm.sort`: `Worse assembly`
  - `algorithm.min_max_element`: `Worse assembly`
  - `atomic.store_load_fetch_add`: `Worse assembly`
  - `atomic.compare_exchange`: `Worse assembly`
  - `atomic.exchange`: `Worse assembly`

The generated report has exact ratios and compile times.

## Caveats

- The C equivalents are handwritten baselines, not universal lower bounds.
- Instruction counts are counted from generated assembly and are heuristic.
- Compile-time ratios are often much worse for C++ even when final assembly is `Precisely C`.
- Be careful with generated report data after a failed run; rerun both compilers before trusting `STL_HEADER_ONLY_RESULTS.md`.
- Keep generated benchmark source and object artifacts under `stl_header_bench/build/`.
