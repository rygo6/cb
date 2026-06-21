# C♭ (CFlat): Minimal C-Style, Data-Oriented C++ Dialect

*C♭* is written `Cb` or `CFlat` in code and ASCII contexts. It is pronounced "C-flat."

This is not a new compiler. It is a C++ subset and build profile for projects that want C-like compile times, C-like binary size, and a small amount of modern C++ syntax.

It keeps the C++ features that help C-style programming. Templates. Namespaces. Lambdas. Attributes. Header-only metaprogramming helpers.

It also restores the C99 and GNU C conveniences that clang and GCC already accept in C++ mode. Designated initializers. Compound literals. VLAs. Statement expressions.

> **Note:** C♭ targets clang and GCC only. MSVC does not have the same flags, runtime behavior, or GNU extension surface. Use a GCC-family toolchain.
>
> clang supports much of GCC's GNU C/C++ surface. The important `-f*` flags, `__builtin_*`, `__attribute__`, statement expressions, designated initializers, compound literals, and VLAs all exist there. MSVC grew in a different direction, with different intrinsics and `__declspec`, so there is no faithful translation of this profile.
>
> Beyond the technical mismatch: any self-respecting programmer should make an effort to be Microsoft-free in every way possible. Sticking to clang/GCC and an open toolchain is not just what C♭ requires. It is the right default.

## Philosophy

The point of C♭ is to keep writing C in spirit.

That means flat structure. Direct control. Plain data. Explicit data flow. It does not mean pretending C++ is not there. It means only using the parts of C++ that make that style better.

C♭ keeps features when they help C-style architecture. It drops features when they push the program toward object orientation, hidden runtime behavior, or large library machinery.

This is what the name means. C♭ is flat.

No object model. No class hierarchy. No encapsulation-driven design. The normal shape of a program should be plain structs and free functions.

C♭ prefers a **data-oriented approach**. Data layout and transformation come first. Objects that bundle data and behavior do not. Structs describe data. Free functions transform it. The program stays organized around how data moves through memory.

C++ pulls in a lot of runtime surface by default. Exception unwinding. RTTI. libstdc++ symbols. Semantic interposition. Threadsafe-static guards.

Most of that is irrelevant for programs that:

- never throw exceptions
- never use `dynamic_cast` or `typeid`
- run only in-process
- want predictable codegen

C♭ strips that runtime surface while keeping cheap C++ syntax.

It also restores selected GNU C-style extensions in C++ mode. That rationale lives in [C99 / C-style features](#c99--c-style-features).

The desired result is simple. C-like compile times. C-like binary size. C++ syntax only where it pays for itself.

## Compile-side flags (CFLAT)

These go in `CXXFLAGS`.

| Flag | Effect |
|------|--------|
| `-fno-exceptions` | Disables exception support. Compiler still parses `try` / `catch` but emits no unwinding tables or throw machinery. |
| `-fno-rtti` | Disables runtime type info. No `dynamic_cast`, no `typeid` on polymorphic types. |
| `-fno-unwind-tables` | Drops `.eh_frame` stack-unwinding metadata. Safe with exceptions off, cuts binary size. |
| `-fno-asynchronous-unwind-tables` | Same as above for the async variant used by signal handlers. |
| `-fvisibility=hidden` | All symbols default to hidden. The right choice for an executable that exports nothing. |
| `-fno-semantic-interposition` | Tells the optimizer the binary's own functions cannot be replaced at runtime, enabling more aggressive inlining and devirtualization. |
| `-fno-math-errno` | math.h functions don't set `errno` on overflow. Allows vectorization of `sinf` / `cosf` / `sqrtf` loops. |
| `-fno-trapping-math` | FP ops don't raise traps. Matches typical shader-language semantics. |

## Link-side flags (LDFLAT)

These go in `LDFLAGS`.

| Flag | Effect |
|------|--------|
| `-static-libgcc` | Statically links libgcc helpers. Removes `libgcc_s.so.1` from the runtime dependency list. |
| `-nostdlib++` | Drops libstdc++ from the link line. Turns forbidden runtime use into link failures. |

## Deliberately NOT included

`-fno-threadsafe-statics` is not part of C♭.

This is intentional.

A runtime-initialized function-local static, such as `static auto x = compute()`, emits `__cxa_guard_acquire`, `__cxa_guard_release`, and `__cxa_guard_abort`. Those symbols live in libstdc++.

Since C♭ links with `-nostdlib++`, that pattern fails to link.

This is the point. Hidden lazy initialization becomes a visible build failure. Use `constexpr`, file-scope storage with no runtime init, or an explicit lazy-init mechanism.

## What still works

- Templates and template metaprogramming.
- Namespaces.
- Lambdas, including generic and capturing.
- Range-based `for` loops.
- Default member initializers in structs / classes.
- Member functions, constructors, destructors.
- `auto`, `decltype`, structured bindings.
- `constexpr` evaluation, `constinit`, `consteval`.
- Header-only STL helpers: `std::initializer_list`, `std::type_traits`, `std::numeric_limits`, tuple-style metaprogramming, etc.
- Attributes: `[[nodiscard]]`, `[[likely]]`, `[[unlikely]]`, `[[gnu::format(printf, ...)]]`, `[[gnu::always_inline]]`.

## C99 / C-style features

This is the rationale for the restored C99 and GNU C surface.

clang and GCC already compile these constructs in C++ mode. The warnings are portability diagnostics. They are not codegen switches.

C♭ does not care about ISO portability here. It cares that clang and GCC have stable, documented behavior for these constructs.

The warnings to suppress (clang spellings, with GCC equivalents in [Boilerplate](#boilerplate)):

| Flag | Re-enables |
|------|------------|
| `-Wno-c99-designator` | C99/GNU designated initializers, including forms that ISO C++ does not allow. |
| `-Wno-c23-extensions` | C23-era constructs used from C++ (e.g. `#embed`, newer literal forms). |
| `-Wno-vla-cxx-extension` | C99 variable-length arrays (`T arr[n]` with a runtime `n`). |
| `-Wno-address-of-temporary` | Taking the address of a compound literal / temporary (`&(struct Foo){ ... }`). |
| `-Wno-missing-field-initializers` | Aggregate / designated init that leaves trailing fields to zero-initialize. |

> **This is not undefined behavior.** These are documented GNU/Clang extensions with specified behavior on the supported C++ compilers. The tradeoff is ISO portability and MSVC, not correctness. The real hazards are usage footguns: dangling compound literals and unbounded VLAs.

### Available C / C99 features

With those warnings off, these constructs are available on supported clang/GCC toolchains:

- **Designated initializers** - `Foo f = { .a = 1, .c = 3 }`, including GNU forms beyond ISO C++'s narrower rules.
- **Compound literals** - `&(Foo){ .a = 1 }`, an unnamed object built in place.
- **Variable-length arrays** - `T arr[n]` with a runtime `n`.
- **Statement expressions** - `({ ... result })`, a GNU block expression useful in macros.
- **`__attribute__((...))`** - GNU attributes such as `packed`, `aligned`, `cold`, and `format`.
- **`__builtin_*` intrinsics** - `__builtin_expect`, `__builtin_trap`, `__builtin_unreachable`, `__builtin_memcpy`, etc.
- **Other C idioms** - anonymous structs/unions, `__typeof__`, `__restrict`, and libc.

There are minor version and diagnostic differences at the edges. That is why the build examples pick warning flags per compiler.

> **Warning - compound literal lifetime.** In C++ mode, `(struct Foo){ ... }` is a temporary whose lifetime ends at the full expression, not the enclosing block. Do not store a pointer or reference to it. Use a named local if it must outlive the statement.

> **Warning - VLAs only on cold paths.** VLAs are useful in setup, enumeration, and one-shot code. Keep them out of hot paths. They create runtime-variable stack frames and `alloca`-style bookkeeping. Use fixed-size storage, preallocated buffers, or arenas in per-frame work.

## What breaks

- `std::vector`, `std::string`, `std::map`, `std::unordered_map`, `std::function`, `std::shared_ptr`, anything with runtime allocation backed by libstdc++.
- `std::cout`, `std::cerr`, `std::cin`, iostreams. Use libc I/O directly, such as `stdio.h`, instead.
- `throw`, `try`, `catch`. Will not work as intended.
- `dynamic_cast`, `typeid` on polymorphic types.
- Function-local `static T x = runtime_init()`. Lift to file-scope or `constexpr`.
- Most third-party C++ libraries that assume `-lstdc++` is on the link line.

libc remains fully usable. Prefer the direct libc/POSIX C headers, such as `stdio.h`, `stdlib.h`, `string.h`, `math.h`, and `time.h`, instead of the C++ wrapper headers such as `<cstdio>`, `<cstdlib>`, `<cstring>`, `<cmath>`, and `<ctime>`.

## Compile-time vs link-time

This distinction matters.

STL **headers** still work at compile time. `-nostdlib++` only removes the standard C++ library from the link step.

That means header-only facilities work. Link-time facilities do not unless you provide their missing symbols yourself.

On clang, `-stdlib=libstdc++` selects the standard-library headers. libstdc++ and libc++ both have useful header-only subsets.

## Usable standard headers

This breakdown should be verified by linking representative usage at `-O0` under the C♭ flags.

Do not verify only at `-O2`. The optimizer can delete code before it references missing runtime symbols.

### The trigger that decides it

A header is usable unless the code you instantiate hits one of three missing pieces:

1. **Heap allocation**: `operator new` / `operator new[]` / `operator delete`.
2. **A throw path**: `std::__throw_length_error`, `__throw_bad_alloc`, `__throw_logic_error`, `__throw_bad_function_call`, `__throw_system_error`, `__throw_out_of_range`, etc.
3. **Out-of-line library symbols or static init**: iostreams, locale, `ios_base::Init`.

Pure template, `constexpr`, and `inline` headers with none of those are fully supported.

### Fully supported

```
<type_traits> <utility> <initializer_list> <tuple> <array> <span>
<string_view>* <optional>* <variant>* <bit> <bitset> <limits>
<concepts> <compare> <numbers> <ratio> <algorithm>**
<version> <source_location>
```

C library headers, backed by libc/libm:

```
<stdint.h> <stddef.h> <string.h> <math.h> <stdarg.h> <limits.h> <float.h>
<inttypes.h> <stdlib.h> <stdio.h> <time.h>
```

Prefer these `.h` C headers from libc directly. Do not route ordinary C library usage through the C++ wrapper headers unless a specific C++ interop reason requires it.

`*` Avoid throwing accessors: `optional::value()`, bad `std::get`, `string_view::at()`, and bad `substr()`. Use `*opt`, `std::get_if`, and `operator[]`.

`**` `<algorithm>` is fine for non-allocating use: `min`, `max`, `clamp`, `sort` over your own data. Include it explicitly.

### Conditionally supported

Header is fine. Specific uses fail.

| Header | Supported | Fails to link |
|--------|-------------|---------------|
| `<functional>` | `std::invoke`, `std::ref`, `std::hash`, `std::less` / `plus`, lambdas | `std::function` (`__throw_bad_function_call`) |
| `<new>` | placement `new`, `std::nothrow`, `std::launder` | global `new` / `new[]` / `delete` / `delete[]` unless you provide them |
| `<atomic>` | Lock-free operations on naturally supported scalar atomics | Operations that need out-of-line atomic helpers on the target (`__atomic_*`, sometimes `-latomic`) |
| `<chrono>` | `duration` / `time_point` arithmetic and constants | Clock queries such as `system_clock::now()` / `steady_clock::now()` that require out-of-line library support |
| `<memory>` | `std::addressof`, `std::uninitialized_*` on your buffers, `unique_ptr` over storage you control | `make_unique` / `make_shared` / deleting `unique_ptr<T[]>` without delete support |

### Unsupported

These need libstdc++ for normal use:

`<vector>` `<string>` `<map>` `<unordered_map>` `<set>` `<deque>`, `<iostream>` `<sstream>` `<fstream>`, `<mutex>` `<regex>` `<locale>`.

They hit allocation, throw paths, out-of-line symbols, or static init.

To use them anyway, provide the missing pieces yourself. Allocation functions. `std::__throw_*` traps. Any other symbols the linker reports. That should be an explicit decision, not the default.

## Containers and replacements

When a standard facility breaks the profile, write or generate a small purpose-built replacement.

This is not about purity. It is about avoiding the three link-time failure categories above.

A bespoke `Vector`, string, or helper can be smaller and easier to reason about than pulling in the full standard-library version.

**Avoid `std::string` specifically.** It drags in `char_traits`, allocator machinery, throw paths, and many inline templates. Prefer plain buffers, `std::string_view` over owned storage, or a small custom string type.

**Check with asserts, not branches.** Container operations should assert preconditions in debug, then run straight-line in release. `push()` should `assert(!full())`, not carry an always-on capacity branch.

Expose checks separately as `full()`, `empty()`, `capacity()`, or `remaining()`.

This means hot code does not pay for checks it does not need. Callers ask for checks only where state is genuinely uncertain.

## Avoid heap allocation

This is the memory-policy rationale.

Prefer fixed memory with known lifetime and footprint:

- **A single static "fat struct"** that owns long-lived state by value. One top-level object holds subsystems instead of scattering heap objects.
- **Static / fixed-capacity containers** with inline storage: `Pool`, `Arena`, fixed-capacity `Array`, or `Vector<T, N>`.

Use dynamic allocation only when size is truly unknowable.

When you do use it, route it through one arena or a deliberate `operator new`.

## Free functions over methods

Compose systems out of **structs and free functions**.

The meat of the program should live in namespace or global functions that take data as parameters. `Do(object)`, not `object.Do()`.

C++ cannot add methods outside the original class definition. Once behavior lives in class methods, extension means breaking the pattern or subclassing.

Free functions stay open. Anyone can add another `Do(object)` against the same struct.

Extension-method languages add machinery to recover what C already had: functions beside data. C♭ keeps the simpler form.

Methods on structs are still useful as small POD conveniences. They should not carry the application.

- **Structs only - no encapsulation.** Plain data. Long-lived state lives in the static [fat struct](#avoid-heap-allocation).
- **Free functions for the meat** of everything: `Do(object)`.
- **Member functions only for shorthand POD utilities**: convenience, not substance.

### Namespace whole categories

Use namespaces to group subsystems.

`Render::Submit(frame)` and `Audio::Mix(...)` give scoped call sites without classes, singletons, or lifetime baggage.

The namespace organizes the functions. The data stays in structs passed as parameters.

### Keep a system in one `.hpp` and one `.cpp`

Prefer one translation unit per subsystem: one public `.hpp` and one implementation `.cpp`.

Use a header-only `.hpp` only when the subsystem is genuinely header-only. The normal shape is still a declaration/definition split.

This keeps the single-header spirit at the subsystem level without literally putting the whole system in one file.

The benefits:

- **Compile speed.** One TU parses subsystem headers once and emits one object file. Fewer, larger TUs often reduce total build work and redundant header parsing.
- **Locality.** Structs, public functions, and internal helpers live together. File-local helpers stay out of headers.
- **A clean boundary.** The `.hpp` is the public subsystem surface. The `.cpp` holds everything else.
- **Fewer dependencies.** The graph is subsystem-to-subsystem, not file-per-class sprawl.

The unit of modularity in C♭ is the **subsystem pair**, not the class.

## Boilerplate

Keep the build simple: `Makefile`, `build.sh`, or `build.bat`. C♭ depends on visible compiler and linker flags, so avoid meta build systems unless you have a strong reason.

### Makefile

```make
CXX ?= c++

# The codegen and link flags below are spelled identically on clang and GCC.
CFLAT  := -fno-unwind-tables \
          -fno-asynchronous-unwind-tables \
          -fvisibility=hidden \
          -fno-semantic-interposition \
          -fno-math-errno \
          -fno-trapping-math

LDFLAT := -static-libgcc \
          -nostdlib++

# Re-enable C99 / C-style features (designated initializers, compound literals,
# VLAs) by silencing their "extension" warnings. The flag *names* differ between
# clang and GCC, so pick the right set from the compiler's --version banner.
ifeq ($(shell $(CXX) --version 2>/dev/null | grep -ci clang),0)
  C99 := -Wno-pedantic -Wno-vla -Wno-missing-field-initializers          # GCC
else
  C99 := -Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension \
         -Wno-address-of-temporary -Wno-missing-field-initializers       # clang
endif

CXXFLAGS += -std=c++23 -fno-exceptions -fno-rtti $(CFLAT) $(C99)
LDFLAGS  += $(LDFLAT)
```

(`-fno-exceptions -fno-rtti` are outside `CFLAT` because they are core language toggles. Group them however suits your taste.)

### build.sh

```sh
#!/bin/sh
set -e

CXX="${CXX:-c++}"   # works with clang++ or g++

# Spelled identically on clang and GCC.
CFLAT="-fno-unwind-tables -fno-asynchronous-unwind-tables \
       -fvisibility=hidden -fno-semantic-interposition \
       -fno-math-errno -fno-trapping-math"
LDFLAT="-static-libgcc -nostdlib++"

# Re-enable C99 / C-style features (designated initializers, compound literals,
# VLAs). Flag names differ between clang and GCC, so pick per compiler.
if "$CXX" --version 2>/dev/null | grep -qi clang
then
  C99="-Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension \
       -Wno-address-of-temporary -Wno-missing-field-initializers"
else
  C99="-Wno-pedantic -Wno-vla -Wno-missing-field-initializers"
fi

"$CXX" -std=c++23 -fno-exceptions -fno-rtti $CFLAT $C99 $LDFLAT \
       -o your_target src/*.cpp
```

### build.bat

```bat
@echo off
if not defined CXX set CXX=c++

rem Spelled identically on clang and GCC.
set CFLAT=-fno-unwind-tables -fno-asynchronous-unwind-tables ^
 -fvisibility=hidden -fno-semantic-interposition ^
 -fno-math-errno -fno-trapping-math
set LDFLAT=-static-libgcc -nostdlib++

rem Re-enable C99 / C-style features (designated initializers, compound literals,
rem VLAs). Flag names differ between clang and GCC, so pick per compiler.
%CXX% --version | findstr /i clang >nul
if %errorlevel%==0 (
  set C99=-Wno-c99-designator -Wno-c23-extensions -Wno-vla-cxx-extension ^
   -Wno-address-of-temporary -Wno-missing-field-initializers
) else (
  set C99=-Wno-pedantic -Wno-vla -Wno-missing-field-initializers
)

%CXX% -std=c++23 -fno-exceptions -fno-rtti %CFLAT% %C99% %LDFLAT% ^
        -o your_target.exe src\*.cpp
```

## Prior art

C♭ sits in the "C-like C++" lineage.

This section only maps prior art. The rationale lives above.

- [**Orthodox C++**](https://bkaradzic.github.io/posts/orthodoxc++/) - the direct ancestor. Same ban-list. C♭ adds link-time stripping, threadsafe-static tripwires, and restored C99/GNU extensions. Orthodox C++ tries to stay orthodox. C♭ pragmatically uses newer C or C++ features when they support the C♭ philosophy.
- [**"Keep It C-mple"** (Radchenko talk)](https://www.youtube.com/watch?v=lTXHOOwfTAo) - the Orthodox C++ argument as a talk.
- [**Defold engine style**](https://defold.com/2020/05/31/The-Defold-engine-code-style/) - closest in practice: no exceptions/RTTI, custom containers, raw pointers, clear ownership.
- [**A dialect of C++**](https://satish.com.in/20180302/) - similar flags, but keeps the full STL and heap allocation.
- [**"C++, it's not you. It's me."**](https://c0de517e.blogspot.com/2019/02/c-its-not-you-its-me.html) - same spirit as an essay rather than a spec.
- [**Embedded C++ (EC++)**](https://en.wikipedia.org/wiki/Embedded_C%2B%2B) - the opposite trap: it removes templates and namespaces, exactly what C♭ keeps.
- [**"Why Your C++ Should Be Simple"**](http://hacksoflife.blogspot.com/2017/03/why-your-c-should-be-simple.html) - a readability argument, not a runtime strip-down.
- [**Orthodoxy** (Clang plugin)](https://github.com/d-musique/orthodoxy) - an enforcement tool that could mechanically enforce C♭.

The unusual part is the combination: link-time tripwires plus restored C99/GNU C features.
