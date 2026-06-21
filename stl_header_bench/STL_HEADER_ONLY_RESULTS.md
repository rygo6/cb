# STL header-only compile and assembly results

This report is generated from `stl_header_bench/run.py`.

Each row compares a C++ STL header facility with a semantically matched C equivalent.

Verdicts use the `-O2` text and instruction ratios:

- `Slightly Better Than C`: both C++ text and instruction ratios are below 0.99x C
- `Precisely C`: within 1 percent of C
- `Approximately C`: within 5 percent of C
- `Near C`: within 25 percent of C
- `Some overhead`: up to 2x C
- `Worse assembly`: more than 2x C
- `Does not link`: fails the CFlat `-nostdlib++` link check

## Run Environment

| Label | C++ compiler | C compiler | OS | CPU |
|-------|--------------|------------|----|-----|
| clang | `Ubuntu clang version 18.1.3 (1ubuntu1)` | `Ubuntu clang version 18.1.3 (1ubuntu1)` | Ubuntu 24.04.4 LTS | AMD Ryzen AI 9 HX 370 w/ Radeon 890M |
| gcc | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | Ubuntu 24.04.4 LTS | AMD Ryzen AI 9 HX 370 w/ Radeon 890M |

## Compiler Flags

| Label | C++ compile flags | C++ link flags | C compile flags |
|-------|-------------------|----------------|-----------------|
| clang | `-std=c++23 -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension -Wno-address-of-temporary -Wno-missing-field-initializers` | `-static-libgcc -nostdlib++` | `-std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables` |
| gcc | `-std=c++23 -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-pedantic -Wno-vla -Wno-missing-field-initializers` | `-static-libgcc -nostdlib++` | `-std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables` |

## Command Templates

Commands are shown with placeholders for the optimization level, generated source, generated driver, and output path.

| Label | Command | Template |
|-------|---------|----------|
| clang | C++ object | `clang++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension -Wno-address-of-temporary -Wno-missing-field-initializers -c {source.cpp} -o {output.o}` |
| clang | C object | `clang -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} -c {source.c} -o {output.o}` |
| clang | C++ assembly | `clang++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension -Wno-address-of-temporary -Wno-missing-field-initializers -S {source.cpp} -o {output.s}` |
| clang | C assembly | `clang -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} -S {source.c} -o {output.s}` |
| clang | C++ nostdlib++ link | `clang++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension -Wno-address-of-temporary -Wno-missing-field-initializers {source.cpp} {driver.cpp} -static-libgcc -nostdlib++ -o {output.exe}` |
| clang | C link | `clang -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} {source.c} {driver.c} -o {output.exe}` |
| gcc | C++ object | `g++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-pedantic -Wno-vla -Wno-missing-field-initializers -c {source.cpp} -o {output.o}` |
| gcc | C object | `gcc -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} -c {source.c} -o {output.o}` |
| gcc | C++ assembly | `g++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-pedantic -Wno-vla -Wno-missing-field-initializers -S {source.cpp} -o {output.s}` |
| gcc | C assembly | `gcc -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} -S {source.c} -o {output.s}` |
| gcc | C++ nostdlib++ link | `g++ -std=c++23 {opt} -fno-exceptions -fno-rtti -fno-unwind-tables -fno-asynchronous-unwind-tables -fvisibility=hidden -fno-semantic-interposition -fno-math-errno -fno-trapping-math -Wno-pedantic -Wno-vla -Wno-missing-field-initializers {source.cpp} {driver.cpp} -static-libgcc -nostdlib++ -o {output.exe}` |
| gcc | C link | `gcc -std=gnu11 -fno-unwind-tables -fno-asynchronous-unwind-tables {opt} {source.c} {driver.c} -o {output.exe}` |

## Facility Overview

Columns:

- `Facility`: the tested STL header facility.
- `nostdlib++`: ok only when both clang and GCC link the C++ case with `-nostdlib++` at `-O2`.
- `C parity`: ok only when both compilers' C++ runtime result matches the C baseline at `n=7`.
- `gcc/clang`: ok only when both previous checks pass on both compilers.

| Facility | nostdlib++ | C parity | gcc/clang |
|----------|------------|----------|-----------|
| `algorithm.binary_search` | ok | ok | ok |
| `algorithm.clamp` | ok | ok | ok |
| `algorithm.min_max_element` | ok | ok | ok |
| `algorithm.sort` | ok | ok | ok |
| `array.front_back_size_data` | ok | ok | ok |
| `array.index_iteration` | ok | ok | ok |
| `atomic.compare_exchange` | ok | ok | ok |
| `atomic.exchange` | ok | ok | ok |
| `atomic.store_load_fetch_add` | ok | ok | ok |
| `bit.bit_floor` | ok | ok | ok |
| `bit.bit_width` | ok | ok | ok |
| `bit.countr_zero` | ok | ok | ok |
| `bit.has_single_bit` | ok | ok | ok |
| `bit.popcount` | ok | ok | ok |
| `bit.rotl` | ok | ok | ok |
| `bitset.any_none` | ok | ok | ok |
| `bitset.construction_to_ulong` | ok | ok | ok |
| `bitset.count_test` | ok | ok | ok |
| `bitset.set_reset_flip` | ok | ok | ok |
| `chrono.durations_duration_cast` | ok | ok | ok |
| `chrono.time_point_time_since_epoch` | ok | ok | ok |
| `compare.generated_equality` | ok | ok | ok |
| `compare.spaceship_ordering` | ok | ok | ok |
| `concepts.integral` | ok | ok | ok |
| `concepts.same_as_requires` | ok | ok | ok |
| `concepts.totally_ordered` | ok | ok | ok |
| `functional.hash` | ok | ok | ok |
| `functional.invoke` | ok | ok | ok |
| `functional.less_plus` | ok | ok | ok |
| `functional.reference_wrapper_ref` | ok | ok | ok |
| `initializer_list.construction_size_begin_iteration` | ok | ok | ok |
| `limits.is_signed_digits` | ok | ok | ok |
| `limits.min_max` | ok | ok | ok |
| `memory.addressof_to_address` | ok | ok | ok |
| `memory.construct_destroy_at` | ok | ok | ok |
| `new.launder` | ok | ok | ok |
| `new.placement_new` | ok | ok | ok |
| `numbers.e` | ok | ok | ok |
| `numbers.pi` | ok | ok | ok |
| `numbers.sqrt2` | ok | ok | ok |
| `optional.bool_deref` | ok | ok | ok |
| `optional.construction_has_value_emplace` | ok | ok | ok |
| `optional.value_or_reset` | ok | ok | ok |
| `ratio.ratio_add` | ok | ok | ok |
| `ratio.ratio_multiply` | ok | ok | ok |
| `ratio.reduction` | ok | ok | ok |
| `source_location.current_line_column` | ok | ok | ok |
| `source_location.file_function_name` | ok | ok | ok |
| `span.construction_size_data` | ok | ok | ok |
| `span.front_back_index_iteration` | ok | ok | ok |
| `span.subspan` | ok | ok | ok |
| `string_view.construction_size_index` | ok | ok | ok |
| `string_view.find` | ok | ok | ok |
| `string_view.remove_prefix` | ok | ok | ok |
| `string_view.substr` | ok | ok | ok |
| `tuple.apply` | ok | ok | ok |
| `tuple.make_tuple_get_tuple_size` | ok | ok | ok |
| `tuple.structured_binding` | ok | ok | ok |
| `type_traits.add_pointer` | ok | ok | ok |
| `type_traits.remove_cv` | ok | ok | ok |
| `type_traits.type_predicates` | ok | ok | ok |
| `utility.exchange` | ok | ok | ok |
| `utility.pair_make_pair` | ok | ok | ok |
| `utility.swap` | ok | ok | ok |
| `variant.construction_holds_alternative` | ok | ok | ok |
| `variant.emplace` | ok | ok | ok |
| `variant.get_if_index` | ok | ok | ok |
| `version.feature_test_macro` | ok | ok | ok |

All listed facilities have a handwritten C equivalent in this harness. Header-level `.combined` rows are synthesized from these facilities for assembly summaries and are not separate compile-time facility measurements.

## Facility Assembly Generation

Columns:

- `Facility`: either a synthesized header-level `.combined` aggregate or an indented facility row explaining a non-precise result.
- `O2 compile C++ / C`: median C++ compile time, median matched C compile time, and their ratio; `.combined` rows aggregate the included facility compile times.
- `O2 text`: the C++ `.text` byte size divided by the matched C `.text` byte size.
- `O2 instructions`: the counted C++ assembly instruction total divided by the matched C total.
- `Verdict`: classifies the worse of the text and instruction ratios.

### clang

| Facility | O2 compile C++ / C | O2 text | O2 instructions | Verdict |
|----------|--------------------|---------|-----------------|---------|
| `algorithm.combined` | 0.4366s / 0.0880s (4.96x) | 1.17x | 1.08x | Near C |
| &nbsp;&nbsp;`algorithm.sort` | 0.1231s / 0.0232s (5.31x) | 1.17x | 1.12x | Near C |
| &nbsp;&nbsp;`algorithm.min_max_element` | 0.1048s / 0.0202s (5.18x) | 1.46x | 1.33x | Some overhead |
| &nbsp;&nbsp;`algorithm.binary_search` | 0.1047s / 0.0233s (4.50x) | 1.13x | 0.94x | Near C |
| &nbsp;&nbsp;`algorithm.clamp` | 0.1039s / 0.0213s (4.87x) | 1.13x | 1.07x | Near C |
| `array.combined` | 0.1305s / 0.0401s (3.26x) | 1.00x | 1.00x | Precisely C |
| `atomic.combined` | 0.1636s / 0.0609s (2.68x) | 1.00x | 1.00x | Precisely C |
| `bit.combined` | 0.2040s / 0.1226s (1.66x) | 1.11x | 1.12x | Near C |
| &nbsp;&nbsp;`bit.bit_floor` | 0.0389s / 0.0209s (1.86x) | 1.81x | 1.83x | Some overhead |
| `bitset.combined` | 0.6149s / 0.0779s (7.89x) | 1.00x | 1.00x | Precisely C |
| `chrono.combined` | 1.1258s / 0.0385s (29.24x) | 1.00x | 1.00x | Precisely C |
| `compare.combined` | 0.0649s / 0.0421s (1.54x) | 1.00x | 1.00x | Precisely C |
| `concepts.combined` | 0.0831s / 0.0608s (1.37x) | 1.00x | 1.00x | Precisely C |
| `functional.combined` | 0.5827s / 0.0759s (7.68x) | 1.00x | 1.00x | Precisely C |
| `initializer_list.combined` | 0.0243s / 0.0170s (1.43x) | 1.00x | 1.00x | Precisely C |
| `limits.combined` | 0.0539s / 0.0413s (1.30x) | 1.00x | 1.00x | Precisely C |
| `memory.combined` | 0.9031s / 0.0380s (23.77x) | 1.00x | 1.00x | Precisely C |
| `new.combined` | 0.0463s / 0.0382s (1.21x) | 1.00x | 1.00x | Precisely C |
| `numbers.combined` | 0.0895s / 0.0633s (1.41x) | 1.00x | 1.00x | Precisely C |
| `optional.combined` | 0.1721s / 0.0566s (3.04x) | 1.00x | 1.00x | Precisely C |
| `ratio.combined` | 0.0977s / 0.0552s (1.77x) | 1.00x | 1.00x | Precisely C |
| `source_location.combined` | 0.0473s / 0.0424s (1.12x) | 1.00x | 1.00x | Precisely C |
| `span.combined` | 0.2406s / 0.0588s (4.09x) | 1.00x | 1.00x | Precisely C |
| `string_view.combined` | 0.3595s / 0.0819s (4.39x) | 1.00x | 1.00x | Precisely C |
| `tuple.combined` | 0.2230s / 0.0617s (3.61x) | 1.00x | 1.00x | Precisely C |
| `type_traits.combined` | 0.0855s / 0.0593s (1.44x) | 1.00x | 1.00x | Precisely C |
| `utility.combined` | 0.1369s / 0.0541s (2.53x) | 1.00x | 1.00x | Precisely C |
| `variant.combined` | 0.1695s / 0.0580s (2.92x) | 1.00x | 1.00x | Precisely C |
| `version.combined` | 0.0239s / 0.0201s (1.19x) | 1.00x | 1.00x | Precisely C |

### gcc

| Facility | O2 compile C++ / C | O2 text | O2 instructions | Verdict |
|----------|--------------------|---------|-----------------|---------|
| `algorithm.combined` | 0.3591s / 0.0579s (6.20x) | 3.16x | 3.99x | Worse assembly |
| &nbsp;&nbsp;`algorithm.sort` | 0.1078s / 0.0168s (6.40x) | 6.25x | 8.37x | Worse assembly |
| &nbsp;&nbsp;`algorithm.min_max_element` | 0.0819s / 0.0129s (6.33x) | 2.74x | 3.30x | Worse assembly |
| &nbsp;&nbsp;`algorithm.binary_search` | 0.0881s / 0.0157s (5.61x) | 1.04x | 1.02x | Approximately C |
| `array.combined` | 0.0876s / 0.0234s (3.75x) | 2.25x | 3.75x | Worse assembly |
| &nbsp;&nbsp;`array.index_iteration` | 0.0466s / 0.0117s (3.99x) | 3.65x | 6.50x | Worse assembly |
| `atomic.combined` | 0.1673s / 0.0388s (4.31x) | 0.98x | 0.96x | Slightly Better Than C |
| &nbsp;&nbsp;`atomic.store_load_fetch_add` | 0.0583s / 0.0127s (4.58x) | 0.96x | 0.94x | Slightly Better Than C |
| &nbsp;&nbsp;`atomic.exchange` | 0.0604s / 0.0126s (4.81x) | 0.98x | 0.94x | Slightly Better Than C |
| `bit.combined` | 0.1579s / 0.0765s (2.06x) | 1.00x | 1.03x | Approximately C |
| &nbsp;&nbsp;`bit.bit_floor` | 0.0312s / 0.0141s (2.21x) | 1.02x | 1.12x | Near C |
| `bitset.combined` | 0.7106s / 0.0487s (14.60x) | 0.96x | 0.84x | Slightly Better Than C |
| &nbsp;&nbsp;`bitset.set_reset_flip` | 0.2329s / 0.0126s (18.55x) | 0.94x | 0.88x | Slightly Better Than C |
| &nbsp;&nbsp;`bitset.any_none` | 0.1280s / 0.0118s (10.83x) | 0.89x | 0.44x | Slightly Better Than C |
| `chrono.combined` | 0.8190s / 0.0213s (38.52x) | 1.08x | 1.22x | Near C |
| &nbsp;&nbsp;`chrono.durations_duration_cast` | 0.4091s / 0.0102s (40.14x) | 1.15x | 1.40x | Some overhead |
| `compare.combined` | 0.0530s / 0.0215s (2.46x) | 1.00x | 1.00x | Precisely C |
| `concepts.combined` | 0.0649s / 0.0319s (2.03x) | 1.00x | 1.00x | Precisely C |
| `functional.combined` | 0.5025s / 0.0468s (10.73x) | 1.00x | 1.00x | Precisely C |
| `initializer_list.combined` | 0.0166s / 0.0122s (1.36x) | 3.76x | 6.50x | Worse assembly |
| &nbsp;&nbsp;`initializer_list.construction_size_begin_iteration` | 0.0166s / 0.0122s (1.36x) | 3.76x | 6.50x | Worse assembly |
| `limits.combined` | 0.0392s / 0.0234s (1.68x) | 1.00x | 1.00x | Precisely C |
| `memory.combined` | 0.3658s / 0.0223s (16.37x) | 1.00x | 1.00x | Precisely C |
| `new.combined` | 0.0298s / 0.0243s (1.23x) | 1.59x | 2.38x | Worse assembly |
| &nbsp;&nbsp;`new.launder` | 0.0154s / 0.0126s (1.22x) | 2.16x | 3.75x | Worse assembly |
| `numbers.combined` | 0.0665s / 0.0328s (2.03x) | 1.00x | 1.00x | Precisely C |
| `optional.combined` | 0.1268s / 0.0335s (3.78x) | 1.00x | 1.00x | Precisely C |
| `ratio.combined` | 0.0741s / 0.0342s (2.17x) | 1.00x | 1.00x | Precisely C |
| `source_location.combined` | 0.0264s / 0.0230s (1.15x) | 1.00x | 1.00x | Precisely C |
| `span.combined` | 0.1962s / 0.0351s (5.58x) | 1.87x | 2.83x | Worse assembly |
| &nbsp;&nbsp;`span.front_back_index_iteration` | 0.0666s / 0.0120s (5.55x) | 3.70x | 6.50x | Worse assembly |
| `string_view.combined` | 0.2606s / 0.0528s (4.94x) | 1.00x | 1.00x | Precisely C |
| `tuple.combined` | 0.1675s / 0.0343s (4.88x) | 1.00x | 1.00x | Precisely C |
| `type_traits.combined` | 0.0618s / 0.0338s (1.83x) | 1.00x | 1.00x | Precisely C |
| `utility.combined` | 0.0957s / 0.0327s (2.92x) | 1.00x | 1.00x | Precisely C |
| `variant.combined` | 0.1448s / 0.0344s (4.21x) | 1.00x | 1.00x | Precisely C |
| `version.combined` | 0.0131s / 0.0109s (1.20x) | 1.00x | 1.00x | Precisely C |

## Facility Compile Time

Columns:

- `Facility`: the tested facility row.
- `O2 compile C++ / C`: the median C++ compile time, median matched C compile time, and their ratio for that compiler.

### clang

Summary for `clang` O2 facility rows:

| Metric | Median | Min | Max | Average |
|--------|--------|-----|-----|---------|
| C++ compile time | 0.0550s | 0.0211s | 0.5651s | 0.0894s |
| C compile time | 0.0201s | 0.0167s | 0.0246s | 0.0199s |
| C++ / C ratio | 2.88x | 1.03x | 30.37x | 4.57x |

| Facility | O2 compile C++ / C |
|----------|--------------------|
| `chrono.durations_duration_cast` | 0.5651s / 0.0200s (28.20x) |
| `chrono.time_point_time_since_epoch` | 0.5607s / 0.0185s (30.37x) |
| `memory.addressof_to_address` | 0.4534s / 0.0201s (22.60x) |
| `memory.construct_destroy_at` | 0.4497s / 0.0179s (25.08x) |
| `bitset.count_test` | 0.1603s / 0.0190s (8.42x) |
| `bitset.construction_to_ulong` | 0.1539s / 0.0210s (7.31x) |
| `functional.less_plus` | 0.1518s / 0.0205s (7.41x) |
| `bitset.any_none` | 0.1517s / 0.0211s (7.19x) |
| `bitset.set_reset_flip` | 0.1491s / 0.0167s (8.92x) |
| `functional.reference_wrapper_ref` | 0.1483s / 0.0170s (8.73x) |
| `functional.invoke` | 0.1420s / 0.0204s (6.96x) |
| `functional.hash` | 0.1407s / 0.0181s (7.79x) |
| `algorithm.sort` | 0.1231s / 0.0232s (5.31x) |
| `algorithm.min_max_element` | 0.1048s / 0.0202s (5.18x) |
| `algorithm.binary_search` | 0.1047s / 0.0233s (4.50x) |
| `algorithm.clamp` | 0.1039s / 0.0213s (4.87x) |
| `string_view.construction_size_index` | 0.0922s / 0.0189s (4.88x) |
| `string_view.find` | 0.0896s / 0.0224s (3.99x) |
| `string_view.remove_prefix` | 0.0895s / 0.0206s (4.34x) |
| `string_view.substr` | 0.0883s / 0.0200s (4.42x) |
| `span.construction_size_data` | 0.0855s / 0.0206s (4.14x) |
| `span.subspan` | 0.0792s / 0.0196s (4.05x) |
| `tuple.apply` | 0.0760s / 0.0199s (3.83x) |
| `span.front_back_index_iteration` | 0.0759s / 0.0186s (4.07x) |
| `tuple.structured_binding` | 0.0740s / 0.0214s (3.46x) |
| `tuple.make_tuple_get_tuple_size` | 0.0729s / 0.0205s (3.55x) |
| `array.index_iteration` | 0.0670s / 0.0227s (2.96x) |
| `array.front_back_size_data` | 0.0635s / 0.0174s (3.65x) |
| `optional.value_or_reset` | 0.0634s / 0.0208s (3.06x) |
| `utility.pair_make_pair` | 0.0610s / 0.0178s (3.43x) |
| `variant.construction_holds_alternative` | 0.0604s / 0.0201s (3.00x) |
| `variant.emplace` | 0.0601s / 0.0171s (3.51x) |
| `optional.construction_has_value_emplace` | 0.0584s / 0.0173s (3.37x) |
| `atomic.compare_exchange` | 0.0550s / 0.0199s (2.77x) |
| `atomic.store_load_fetch_add` | 0.0549s / 0.0191s (2.88x) |
| `atomic.exchange` | 0.0537s / 0.0220s (2.44x) |
| `optional.bool_deref` | 0.0503s / 0.0185s (2.72x) |
| `variant.get_if_index` | 0.0490s / 0.0208s (2.35x) |
| `utility.exchange` | 0.0392s / 0.0194s (2.02x) |
| `bit.bit_floor` | 0.0389s / 0.0209s (1.86x) |
| `bit.bit_width` | 0.0380s / 0.0221s (1.72x) |
| `utility.swap` | 0.0367s / 0.0170s (2.16x) |
| `ratio.ratio_multiply` | 0.0363s / 0.0179s (2.02x) |
| `numbers.e` | 0.0348s / 0.0246s (1.41x) |
| `bit.popcount` | 0.0336s / 0.0195s (1.72x) |
| `compare.spaceship_ordering` | 0.0330s / 0.0198s (1.67x) |
| `bit.rotl` | 0.0325s / 0.0186s (1.75x) |
| `compare.generated_equality` | 0.0319s / 0.0223s (1.43x) |
| `type_traits.add_pointer` | 0.0314s / 0.0173s (1.82x) |
| `ratio.ratio_add` | 0.0313s / 0.0186s (1.68x) |
| `bit.has_single_bit` | 0.0307s / 0.0195s (1.58x) |
| `bit.countr_zero` | 0.0303s / 0.0219s (1.38x) |
| `ratio.reduction` | 0.0301s / 0.0186s (1.62x) |
| `concepts.totally_ordered` | 0.0289s / 0.0199s (1.45x) |
| `type_traits.type_predicates` | 0.0283s / 0.0204s (1.39x) |
| `concepts.same_as_requires` | 0.0283s / 0.0202s (1.40x) |
| `numbers.sqrt2` | 0.0282s / 0.0182s (1.55x) |
| `limits.min_max` | 0.0271s / 0.0211s (1.28x) |
| `limits.is_signed_digits` | 0.0268s / 0.0202s (1.33x) |
| `numbers.pi` | 0.0265s / 0.0204s (1.29x) |
| `concepts.integral` | 0.0260s / 0.0208s (1.25x) |
| `type_traits.remove_cv` | 0.0257s / 0.0216s (1.19x) |
| `new.placement_new` | 0.0252s / 0.0178s (1.42x) |
| `source_location.file_function_name` | 0.0246s / 0.0218s (1.12x) |
| `initializer_list.construction_size_begin_iteration` | 0.0243s / 0.0170s (1.43x) |
| `version.feature_test_macro` | 0.0239s / 0.0201s (1.19x) |
| `source_location.current_line_column` | 0.0228s / 0.0205s (1.11x) |
| `new.launder` | 0.0211s / 0.0205s (1.03x) |

### gcc

Summary for `gcc` O2 facility rows:

| Metric | Median | Min | Max | Average |
|--------|--------|-----|-----|---------|
| C++ compile time | 0.0459s | 0.0121s | 0.4099s | 0.0677s |
| C compile time | 0.0117s | 0.0101s | 0.0168s | 0.0119s |
| C++ / C ratio | 3.70x | 1.06x | 40.14x | 5.77x |

| Facility | O2 compile C++ / C |
|----------|--------------------|
| `chrono.time_point_time_since_epoch` | 0.4099s / 0.0111s (37.03x) |
| `chrono.durations_duration_cast` | 0.4091s / 0.0102s (40.14x) |
| `bitset.set_reset_flip` | 0.2329s / 0.0126s (18.55x) |
| `bitset.construction_to_ulong` | 0.2277s / 0.0120s (18.95x) |
| `memory.addressof_to_address` | 0.1896s / 0.0116s (16.41x) |
| `memory.construct_destroy_at` | 0.1762s / 0.0108s (16.33x) |
| `functional.less_plus` | 0.1354s / 0.0123s (11.00x) |
| `bitset.any_none` | 0.1280s / 0.0118s (10.83x) |
| `functional.invoke` | 0.1246s / 0.0119s (10.45x) |
| `bitset.count_test` | 0.1219s / 0.0123s (9.94x) |
| `functional.reference_wrapper_ref` | 0.1218s / 0.0113s (10.74x) |
| `functional.hash` | 0.1206s / 0.0112s (10.73x) |
| `algorithm.sort` | 0.1078s / 0.0168s (6.40x) |
| `algorithm.binary_search` | 0.0881s / 0.0157s (5.61x) |
| `algorithm.min_max_element` | 0.0819s / 0.0129s (6.33x) |
| `algorithm.clamp` | 0.0813s / 0.0124s (6.54x) |
| `string_view.substr` | 0.0676s / 0.0135s (5.00x) |
| `string_view.find` | 0.0668s / 0.0116s (5.78x) |
| `span.front_back_index_iteration` | 0.0666s / 0.0120s (5.55x) |
| `span.subspan` | 0.0661s / 0.0114s (5.80x) |
| `span.construction_size_data` | 0.0635s / 0.0117s (5.41x) |
| `string_view.remove_prefix` | 0.0635s / 0.0138s (4.62x) |
| `string_view.construction_size_index` | 0.0627s / 0.0140s (4.49x) |
| `atomic.exchange` | 0.0604s / 0.0126s (4.81x) |
| `tuple.make_tuple_get_tuple_size` | 0.0595s / 0.0114s (5.20x) |
| `atomic.store_load_fetch_add` | 0.0583s / 0.0127s (4.58x) |
| `tuple.apply` | 0.0544s / 0.0114s (4.75x) |
| `tuple.structured_binding` | 0.0536s / 0.0114s (4.69x) |
| `variant.emplace` | 0.0521s / 0.0122s (4.29x) |
| `atomic.compare_exchange` | 0.0487s / 0.0135s (3.59x) |
| `variant.get_if_index` | 0.0467s / 0.0112s (4.18x) |
| `array.index_iteration` | 0.0466s / 0.0117s (3.99x) |
| `optional.value_or_reset` | 0.0462s / 0.0116s (3.98x) |
| `variant.construction_holds_alternative` | 0.0459s / 0.0111s (4.15x) |
| `optional.construction_has_value_emplace` | 0.0412s / 0.0113s (3.65x) |
| `array.front_back_size_data` | 0.0410s / 0.0117s (3.51x) |
| `optional.bool_deref` | 0.0394s / 0.0106s (3.70x) |
| `utility.exchange` | 0.0340s / 0.0108s (3.15x) |
| `utility.pair_make_pair` | 0.0324s / 0.0117s (2.78x) |
| `bit.bit_floor` | 0.0312s / 0.0141s (2.21x) |
| `utility.swap` | 0.0292s / 0.0103s (2.85x) |
| `bit.bit_width` | 0.0280s / 0.0125s (2.24x) |
| `compare.generated_equality` | 0.0268s / 0.0102s (2.62x) |
| `compare.spaceship_ordering` | 0.0262s / 0.0113s (2.32x) |
| `bit.countr_zero` | 0.0262s / 0.0122s (2.15x) |
| `bit.has_single_bit` | 0.0262s / 0.0122s (2.15x) |
| `ratio.ratio_add` | 0.0257s / 0.0109s (2.36x) |
| `bit.popcount` | 0.0254s / 0.0125s (2.03x) |
| `ratio.ratio_multiply` | 0.0243s / 0.0121s (2.01x) |
| `ratio.reduction` | 0.0241s / 0.0112s (2.15x) |
| `concepts.integral` | 0.0231s / 0.0101s (2.28x) |
| `numbers.sqrt2` | 0.0229s / 0.0103s (2.22x) |
| `numbers.pi` | 0.0226s / 0.0113s (2.00x) |
| `concepts.same_as_requires` | 0.0222s / 0.0111s (1.99x) |
| `type_traits.type_predicates` | 0.0212s / 0.0111s (1.92x) |
| `type_traits.add_pointer` | 0.0212s / 0.0117s (1.82x) |
| `numbers.e` | 0.0210s / 0.0112s (1.87x) |
| `bit.rotl` | 0.0209s / 0.0129s (1.61x) |
| `limits.min_max` | 0.0201s / 0.0119s (1.70x) |
| `concepts.totally_ordered` | 0.0197s / 0.0107s (1.84x) |
| `type_traits.remove_cv` | 0.0194s / 0.0111s (1.75x) |
| `limits.is_signed_digits` | 0.0190s / 0.0115s (1.65x) |
| `initializer_list.construction_size_begin_iteration` | 0.0166s / 0.0122s (1.36x) |
| `new.launder` | 0.0154s / 0.0126s (1.22x) |
| `new.placement_new` | 0.0144s / 0.0117s (1.23x) |
| `source_location.file_function_name` | 0.0143s / 0.0115s (1.24x) |
| `version.feature_test_macro` | 0.0131s / 0.0109s (1.20x) |
| `source_location.current_line_column` | 0.0121s / 0.0115s (1.06x) |

