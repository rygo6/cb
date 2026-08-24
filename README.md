> This document is currently under heavy revision and editing.

# Flat C++ Dialect - C♭ Cb CFlat 

C++ is a pioneering language which has proven out some incredibly usefull tools for programming. However at the same time, many of it's explorations have simoualaneously proven to be not be useful, to even detrimental. Over the years C++ has accumulated considerable cruft and functionality which in retrospect we can see as being bad, or short-sighted, or made moot by other advents.

In response to this there have been numerous new languages attemptng restart from first principles. Building something compeletely fresh from the ground up.

CFlat takes a different approach. What if instead of starting over you instead forked C++ and deleted the bad parts? This seems like the simpler and more pragmatic approach compared to starting over. 

_C++ would be a great language if you deleted most of it._

## What is wrong with C++?

> "Everything after C was a mistake." _-some open-source programer_

The above statement is more true than not true, but is not entirely true.

The more specific truth is that everything after C increasingly became polluted by incentives other than simply being a productive programmer creating value for end-users by writing the best applications possible.

- The industry went through a phase where programmer productivity was measured by lines of code, or lines changed, or 'artifacts' (i.e. files, abstraction, etc.) generated. This created an incentive in organizations to adopt programming languages and styles of prgramming which produced more lines of code and more files for the same resultant functionality. The push for C++ and Java largely came from the Corporate Enterprise side of the industry. While open-source kernels, drivers, servers and databases which were never subjected to such incentives remained on C. Once upon a time if you did not follow the crowd into one of these languages or styles of programming which let you add considerable 'fluff' to your code to pad you corporate metrics your pay could suffer and you probably owuld have been laid off.

- The rapid growth of Big Tech created environemnts where there was incentive to build internal moats for your codebase. To add as many layers of complex invention and abstraction as possible so the overhead for ever removing the creator from the codebase would be too great.

- It became the mark of a highly qualified proffeisonal to have authored some portion of a common language or common library. Creating incentive for people to try and invent anything they can possibly get away with inventing to have another line item on their resume. Leading to an endless churn of new language features, new languages, new frameworks and new libraries. Which were not done becuase we truly needed such things, but because their became icnentive to do so simply for the sake of doing so.

- The huge influx of demand for software in every industry created an environemnt where non-technical businessmen with large quanties of cash to spend on development were now forking out millions for applicatons or websites to be developed. This created incentive to get as many line items as possible on your invoice and building the software in such a way where adding an additional month, or 6 months, or year, could always be justified.

- The rise of software companies which also sold cloud compute, or new consumer hardware, incentivized the writing of software in such a way where having to purchase additional cloud compute, or new hardware, fed back into the companies bottomline. Creating the incentive to have little concern with doing things as performantly and minimally as possible. Instead allowing overhead and resource consumption to go up little-by-little just enough to justify always needing to purchase new hardware or spend more on compute at a regular interval.

It's not that someone is smarter than another.

It is that certain languages, approaches and mentalities to programming evolved out of environemnts which had incentivies other than enabling a programmer creat evaluable software to solve real problems.

Or worse, they evolved from enviornments which incentivized downright charlatanry.

The resultant language or approach to programming is more so shaped by the enviornment of incentives from which it came. Not how smart any particular individual was.

The purpose of CFlat is to go back to C before all these polluted incentives came into play. Then sort through the large canon of features and approaches asking the question of:
> "As a programmer wanting to write a piece of software to the highest quality possible, as quickly as possible, does this help me do that?"

## CFlat

*CFlat* is written `Cb` or `CFlat` in code and ASCII contexts. It is pronounced "C-flat."

This is not a new compiler. It is a C++ subset and build profile for projects that want C-like compile times, C-like binary size, and a small amount of C++ syntax for ease of development.

CFlat is in a similiar vein to 'Embedded C++' or 'Orthodox C++' or other efforts to define constrained subsets of C++. Except CFlat is more explicitly focused on retaining a C-Style Data-Oriented stlye of programming. While being more pragmatic in pulling in new C23 and C++ features that aid that style of programming.

The term `Flat` comes from the tendency of C-Style Data-Oriented programming to flatten programs. Flatten inheritence hiearcies. Flatten data structures into single contiguous allocations with minimal heap allocaiton and pointer indirection. Flatten systems fragmented across many files into fewer files. 

This approach to programming is preferable when high-performance, predictable execution time and running on resource constrained hardware is a primary concern. 

## Recognition of Domain Specific Languages

C, C++ and consequently CFlat are systems programming languages. For problem domains in which performance matters. In which using the hardware as optimally as possible is a necessary component of producing the highest quality software possible.

It should be reocgnized that not all problem domains need to have such concern with optimally using the hardware. Shell scripts, Makefiles, Lua, awk and many other domain specific languages are often the more intelligent choice for a given problem domain. The work being executed does not need to use the absolute bare minumum resource, and execute as fast as possible. Utilizing something which enables shorthand syntax and off-the-shelf primitives can be the route to the highest quality necessary, as quickly as possible.

## Performance Matters

Despite poor-performaing domain specific languages having great utility, performance does still matter for many problems domains. And there has been a gradual degradation in the recognition that performance matters due to the incentives of industry. Particulrly in the realm of consumer software. 

A text editor which consumes 5% of the system resource is definitely more valuable, and of higher quality, to the end user than a text editor which consumes 50% of the system resources. Despite the fact that in optimal conditions the user would not notice the difference between 5% and 50% resource consumption. The software which uses less is still more valuable. Because if everyone assumes they get 50% of the system resources then the user can only have two of those applications running. Whereas most users would prefer to do more with their computer.

This issue has compounded in the realm of mobile battery powered devices. Because resource consumption is not simply your software running slower, or being able to run fewer instances of it. Resource consumption is also battery consumption and the user simply not being able to run your software for as long. A piece of software someone can use for 8 hours straight is more valuable than a piece of software they could only use for 6 hours.

So in the ream of software intended for consumers, particularly on mobile battery powered devices. The difference between 50% nad 5% resource consumption matters. The difference 5% and 0.5% resource consumption also matters.

## C-Style Data-Oriented Programming

A C-Style Data-Oriented approch to programming is the ideal mentality to take in a problem domain in which performance matters. This approch to programming can be done in many langugages. It is an approach primarly concerned with answering two questions:

1. What is my data? 
2. What transformations do I need to do on that data?

This is in essence what a program literally is in the machine. Data going through transformations. The furher you get from it being data going through trnasformtions the more you have invented 'Stuff' which conceals what you are actually doing with the machine. Or as the indsutry would call it 'Abstraction'.

Of course it is impossible to program without abstraction. Assembly is an abstraction. C itself is an abstraction. That does not justify complete disregard for how much you have abstracted. For an analogy, the fact that Astronomy uses the abstractions of math and physics to model the cosmos does not mean that _Astrology_ is also correct.

A struct, although an abstraction, does represent the layout of data in physical memory.

A method, although an abstraction, does represent a series of instructions to be executed contiguously in physical memory.

If you are in a problem domain where performance matters then having awarness of what you are doing with the machine also matters. Because that is how you make the machine do things which work with the machine rather than against the machine.

Given this, you should be aware of what your data is and how it is laid out in memory. You should be aware of the procedural sets of instructions that are being executed to transform your data. This does not mean you need to know where every bit is exactly in memory. Nor that you need to be aware of each line of assembly.

However, if you write a program in which everything is fragmented across the heap and you have zero clue as to where any piece of data is in memory in relation to any other piece of data. Because every single 'class' is a smart pointer or other heap allocation. Then you don't know what you are doing with the machine.

If you write a program where a single call of a constructor, which looks as innoculus as any other constructor, can fire off a chain of a dozen methods through hidden internal vtable machinery. And you don't have a clear mental catalog of the general route that call will go, and wehther it will fire off 50 instructions, or 5,000 instructions. Then you don't know what you are doing with the machine.

If your in a problem domain where performance matter, and you don't what you are doing with the machine. Then this means you don't know what you are doing.

This means that to know what you are doing then you need to prefer:

- Abstractions which approximate real qualities of hardware. So you think in terms of hardware and design in congruence with it.
- Flat structure. A wider surface area of visible internals laid out with a bias towards exposing more of what is occuring so you can keep a better overview of what is happening.
- No hidden control flow. No mechanism enabling execution to jump distances which cannot be reasoned about locally. So you can be aware of the execution paths of your program.
- No hidden internal heavy machinery. If two methods have 100 lines of operations their resultant assembly should end up comparable in length.
- Plain data visible in structs biased towards pre-determined allocation and layout as much as possible.

## Is this Premature Optimization?

When Donald Kuth orignally said premature opimization is the root of all evil. That was during a time when the dichotomy was between FORTRAN or machine specific assembly. He notes the big negative of premature optimization is that it makes code less adaptable. That it's primarily an argument to delay any approach to code which would tend towards making it more difficult to refactor. That you should 'Lazily Evaluate' as much as possible. Keep things as open to change as possible. Avoid as much upfront decision making as possible until more is specifically understood through proving out the actual implementation and you are confident subsequent changes won't be necessary. [Premature optimization is the root of all evil | Donald Knuth and Lex Fridman](https://www.youtube.com/watch?v=74RdET79q40)

Reading The Art of Unix Programming, from a different author, conveys a similar framing by adding the subtext "Prototype before polishing" to the "Rule of Optimization". Specifically stating, "A prematurely optimized portion of a design frequently interferes with changes that would have much higher payoffs across the whole design."
[Rule of Optimization: Prototype before polishing. Get it working before you optimize it.](http://www.catb.org/esr/writings/taoup/html/ch01s06.html#rule_of_optimization)

The point wasn't to avoid thinking about performance. It was to avoid anything which prematurely locked in assumptions about how the program worked before more was proven out in the implementation and you could be certain more refactors won't be necessary. It's just that at the time machine specific assembly is what tended to make subsequent refactors difficult.

In that context, abstracting and encapsulating tends to attach more assumptions to logic and data. Making things more difficult to refactor. Requiring more layers, more boundaries and more steps you'd have to deal with if you want to make a pervasive refactor. You could just as easily argue that premature abstraction is the root of all evil by the same reasoning.

A C-style of programming with flattened structs and free floating methods in fewer files keeps everything easier to change. It just so happens that this style of programming also tends to be more performant on average.

It's important to have discretion on when a Domain Specific Language would make sense to use. However programming in a less abstracted way which keeps you more aware of what you are doing with machine is not inherently violating the wisdom to avoid premature optimziation. You do want to avoid any premature rabbit-holing on specific problems until you are certain it needs to be done, preferring the simplest pragmatic approach to prove things out. However not having any performance sense in the inittial structuring of your systems and data can often lead you into a corner which you may only be able to get out of by a complete system rewrite. This is why it is important to have some awarneness of how you are setting things up to work in congruence with the machine. Even if you do not intially rabbit-hole on every direction. The initial scaffolding of the codebase should ensure it is open to it in the future.

## Date-Oriented 101: The RAM was a lie.

Chip architecture itself evolved in a direction over the past few decades which is antithetical to the kind of code which Object Orient Programming language features incentivize.

It is similiar to how, over the past few decades, every chip got multiple cores and threads. To utilize the power of a chip effectively you had to adapt strategies for multi-threading. A change in the physical architecture necessitated this. It wasn't someones opinion, nor some philosophical argument, nor a different taste in how you write software. The push to have multi-threading features in programming languages were a response to a physical change in the chips and how to properly utilize them.

Another quality of chips, just as significant, also changed over the past few decades. It is how the cache works. 

Software has had this term 'Random Access Memory' RAM floating around for decades. Something like Object Oriented Programming presumed you could allocate an object in memory then randomly access all of it's data. This is premise behind class and objects in C++, the new and delete keywords. That you define your objects, then later the system allocate them anywhere on the heap, then it would 'Ranomly Access' them and it didn't matter where they were on the heap. People were sold the mental model of objects being organisms floating around as free agents in space sending messages to one another.

But the truth is 'Random Access Memory' (RAM) has become a misnomer in terms of how any modern chip utilizes memory. The more appropriate term is 'Tiered Cache Access Memory' (TCAM).

Along with more cores and raw Hz. Chips also added more cache. Faster cache. More layers of Cache. It changed the performance profile of the chips.

The short of it is, you must co-locate and pack data based on access pattern. All data which is used for a specific operation you want to pack as tightly as possible with nothing extra. Then whatever data is used for the next operation occupies the next contiguous segment of memory. Also packed as tightly as possible. The intent is to increase likelihood that a cache line is fully utilized and can stay in a faster level of cache longer.

Which is antithetical to spreading data across objects allocated on the heap. Even if you made a custom allocator it is still antithetical to put all data, even cold infrequently accessed data, in the same object next to hot data.

This is the real problem with Object Oriented Programming. It incentivizes an approach to data layout which is contradictory to how chips now function. The loss of performance can be severe. Proper data design can 10x performance depending. It is comparable to not knowing how to use multiple threads.

This is one area where C++ went the wrong direction and what CFlat is a response to. A physical change in the chips themselves made assumptions baked into C++ and the entire mental model of Object Orientation incorrect.

Unlike other arguments of programming which are theoretical or stylistic based. Data Oriented Programming is not. It is a response to physical changes in the chips. Due to this Data-Oriented Programming should be seen as in a category of signifiance comparabel to Multi-Threaded Programming. They are response on how to propery use physical qualities of the chips. In the same way you must have some pre-emptive awareness of what you are doing. Multi-threading a program after it had intiially been built with zero awareness of multi-threading can often mean you must rewrite the program. The same is true for Data-Oriented Programming. Although you don't implenent every detail to it's most optimal condition intially. You do need to be aware of how you set things up in the intiaily design to keep open to that further down the line. 

## C++ Features for C-Style Data-Oriented Programming

The exact things to delete in C++ fall into a few categories.

1. Was a terrilble idea to begn with.
2. Was an idea worth exploring intiially but the past 20 years have shown that it is not useful to potentially detrimental.
3. Was actually good 20 to 30 years ago but the changing nature of hardware has now made it a terrible default.
4. Can be useful in certain scenarios but is a terrible default and should be for scenarios so niche that it should not be in a standardized language.
5. Things which C++ invented to solve problems solely created by prior inventions in C++ to which you should remove the original root cause of the problem and everyhting which came after it.
6. Things which are primarily terrible in some way, but they have a few usages that are actually truly valuable.
7. Things which can be terrible but easily can be helpful.
8. Things which are mostly syntatical sugar.
9. Things which can truly make life easier.

But first lets start with whats good.

### The Good

- Destructors
  - Not necessarily Constructors.
- Default Struct Values
  - Simply makes life easier.
- Namespaces
  - Simply makes life easier.
- std::initializer_list
  - Simply makes life easier.
- Attributes you'd typically make a cumbersome macro for.
  - `[[likely]] [[unlikeliky]] [[gnu::inline]]` makes life easier.
- Struct methods for shorthand to simple operation POD structs.
  - `item.IsConnected` rather than `item.status == Status::Connected` is syntactical sugar but can make life easier.
- Templates
  - Used instead of macros for stamping type-specific code makes life easier.
  - Hiearchal template metapgroggraming can still be bad.
- Method overloads.
  - Can be terrible but easily helpful.
- Default method parameters.
  - Can be terrible but easily helpful.
- General synactical sugar.
  - Tuple. Iterators.
- Consteval
  - Generate hashes at compile time if needed.

### Debatable but good in some way.

- Operator overloads for matrix multiplication.
  - Being able to implement `matrixA * matrixB` to do real matrix multiplication makes life easier for math.
  - However this is detrimental in every other scenario.
- Constructors.
  - `auto state = State(value)` is nicer than having to always make a static method `State::Create(value)`. However constructors doing intricate logic can be an issue as they can't return an error and static Create methods are preferrable for this. 
- refs
  - const ref method parameters can provide nice syntactical sugar and some additional guarantees on something passed in with no negatives.
  - refs for mutable parameters forego one of the critical syntax distinctions of C. The -> pointer syntax is meant to clearly signify distant access while . dot syntax signifies local access. All distant access is made more clear with -> syntax and should be done that way.
  - Mutables refs enable operator overloads and matrix multiplication overloads which are highly useful, but unfortunately can only be implement in this manner.

### The Bad

- STL
  - There are useful things in STL. Overall it is a landmine of performance footguns and compile time footguns. Often providing funcitonality far more complex than you'd ever need.
- Encapsulaiton, access modifiers, classes, friend classes.
  - Aruably worth exploring 30 years ago but now pointless to detrimental. Also partially redundant in a C-Style of programming.
  - "internal" or "private" methods can effectively be accomplished in an implementation of free-floating methods by making them static in the implementation file.
  - Fields on a struct that'd you'd want to signify as internal can have an _ prefix. Or you could rely on a PIMPL like pattern. Or a blob of generic bytes at the bottom of the struct to be fcast.
- Virtual Methods and VTables
  - Useful in some scenarios but should be so rarely used that it shouldn't be in the language. Unnecessary hidden internal machinery and enables hidden control flow. Also incentvizes a style of program where variation of behaviour on a single type cannot be reasoned about locally. Often it's spread across many files.
- New/Delete. Smart Pointers.
  - Terrible to begin with. Misunderstood the important of data design from C instead making it the default the throw any and everything on the heap.
  - Unnecessary complicaton for RAII. 
- Exceptions.
  - Terrible to begin with. Hidden control flow that can jump backwards from any level of nested methods making it diffucult to reason about locally. Hidden heavy machinery can easily bloat assembly without any signal it is doing so.
  - Made irrelevant if you don't do complex logic in a constructor that could fail and needs to be caught.
- RTTI 
  - Useful. But heavy hidden internal machinery. Any type information you need is better handled yourself.
- Move semantics.
  - && is useful in methods and constructors to enforce the need for the parameter being a temporary.
  - Other than that move semantics are a work around for C++ having developed modality of using mutable refs for everythng when it should have been pointers. If you need to change an lvalue to point at the contents of another lvalue that is simply setting a pointer equal to another pointer.

## C++ Compiler Setup

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

These go in `LDFLAGS`.

| Flag | Effect |
|------|--------|
| `-static-libgcc` | Statically links libgcc helpers. Removes `libgcc_s.so.1` from the runtime dependency list. |
| `-nostdlib++` | Drops libstdc++ from the link line. Turns forbidden runtime use into link failures. |

Deliberately NOT included.

`-fno-threadsafe-statics` is not part of CFlat. This is intentional.

A runtime-initialized function-local static, such as `static auto x = compute()`, emits `__cxa_guard_acquire`, `__cxa_guard_release`, and `__cxa_guard_abort`. Those symbols live in libstdc++. Since CFlat links with `-nostdlib++`, that pattern fails to link. Hidden lazy initialization becomes a visible build failure. 

### What still works

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

### What doesn't

- `std::vector`, `std::string`, `std::map`, `std::unordered_map`, `std::function`, `std::shared_ptr`, anything with runtime allocation backed by libstdc++.
- `std::cout`, `std::cerr`, `std::cin`, iostreams. Use libc I/O directly, such as `stdio.h`, instead.
- `throw`, `try`, `catch`. Will not work as intended.
- `dynamic_cast`, `typeid` on polymorphic types.
- Function-local `static T x = runtime_init()`. Lift to file-scope or `constexpr`.
- Most third-party C++ libraries that assume `-lstdc++` is on the link line.

libc remains fully usable. Prefer the direct libc/POSIX C headers, such as `stdio.h`, `stdlib.h`, `string.h`, `math.h`, and `time.h`, instead of the C++ wrapper headers such as `<cstdio>`, `<cstdlib>`, `<cstring>`, `<cmath>`, and `<ctime>`.

## C99 / C-style features

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

## Containers

When a standard facility breaks the profile, write or generate a small purpose-built replacement.

A bespoke `Vector`, string, or helper can be smaller and easier to reason about than pulling in the full standard-library version.

Claude is particularly capable of generating any basic container you need for your exact purpose.

Prefer fixed or statically allocated containers. See [Avoid heap allocation](#Avoid-heap-allocation).

**Avoid `std::string` specifically.** It drags in `char_traits`, allocator machinery, throw paths, and many inline templates. Prefer plain buffers, `std::string_view` over owned storage, or a small custom string type. This easily becomes to slowest compiling source of templates in C++.

## All Checks Compile Out In Release Builds

**Check with asserts, not branches.** Container operations should assert preconditions in debug, then run straight-line in release. `push()` should `assert(!full())`, not carry an always-on capacity branch.

Expose checks separately as `full()`, `empty()`, `capacity()`, or `remaining()`.

This means hot code does not pay for checks it does not need. Callers ask for checks only where state is genuinely uncertain.

## Prefer hot data packing in fat structs with anonymous structs.

A fat struct holds the full program state by value as a single static or stack object. Within it, group fields by access frequency using anonymous structs so hot fields land on the same cache lines.

```cpp
// inline struct App { ] app;
// Where you specify inline, the struct name and the instance name at the end
// will statically allocate a single instance of the struct in a header for all implementations to share.

inline struct App {
    // Hot: touched every frame. Fields read together, packed together.
    struct {
        float4x4 view;
        float4x4 proj;
        float3   eyePos;
        float    time;
        uint32_t frameIndex;
    };

    // Hot: input state read every frame alongside the above but written
    // by a separate event path, so kept in its own anonymous grouping.
    struct {
        float2 mouseDelta;
        float2 mousePos;
        bool   keys[KEY_COUNT];
    };

    // Warm: updated on resize or input events.
    struct {
        uint32_t width;
        uint32_t height;
        float    aspect;
        bool     resizePending;
    } screen;

    // Cold: set once at startup, never touched in the frame loop.
    struct {
        VkDevice         device;
        VkQueue          queue;
        VkCommandPool    cmdPool;
        VkDescriptorPool descPool;
    } vk;
} app;
```

The anonymous `struct { ... };` at the top of `App` promotes its fields directly into `App`'s scope with no member-access prefix. That keeps the hot fields as readable as bare globals while still being a single allocation. The named inner structs (`screen`, `vk`) namespace their fields explicitly because callsites that touch them are already in a setup or event path where the extra token costs nothing.

You can have multiple anonymous struct groupings within the same fat struct. Each one is a logical cluster of fields that are accessed together. Fields that are always read or written at the same time belong in the same anonymous struct so they pack onto the same cache lines. Fields from different access patterns belong in separate groupings, named or anonymous, so they do not pollute each other's lines.

Pack hot fields first. The linker and allocator give you no cache-line guarantees across struct boundaries, but within a struct fields are laid out in declaration order. Putting the frame loop's data at the top of the fat struct maximizes the chance those fields share lines with each other rather than with cold init data.

To ensure a struct literally starts on a cache line you must use the attribute `__attribute__((aligned(64)))`. This may or more not be preferable depending. I would default to **not** using this on everything unless you have a specific reason to. Tightly packing data by access pattern in a fat struct is typically sufficient even if each struct does not literally start on a cacheline, as generally multiple parts of the fat struct will keep getting accessed to keep the whole fat struct in some level of cache. Explicit cache line alignment should only be used when testing proves it useful in situations of multi-threaded cache contention or sequentially operating on continguous equally-spaced elements in a array.

## Avoid heap allocation

Prefer fixed memory with known lifetime and footprint:

- **A single static "fat struct"** that owns long-lived state by value. One top-level object holds subsystems instead of scattering heap objects.
- **Static / fixed-capacity containers** with inline storage: `StaticPool`, `StaticArena`, fixed-capacity `StaticArray`, or `StaticVector<T, N>`.

Use dynamic allocation only when size is truly unknowable.

Use libc directly: `malloc`/`free`, `mmap`/`munmap`, `posix_memalign`.

However, if you need to use `malloc`/`free` so frequently that you find it hard to keep track of where to put a `free` this means your are doing something wrong. Generally `malloc`/`free` usage should be about as common and accessing a file via `mmap`/`munmap`.

`malloc`/`free` are generally unnecessary for the simple file IO. Always prefer to `mmap`/`munmap` when reading files. Prefer to store data to disk in a format which can simply be memcpy'd directly from the mmap'd region.

Most general memory needs can be dealt with via static pools, static arenas and static vectors. Heap allocation is for the rare occurrence when you have no idea about the prospective lifetime, or prospective size, of a given memory need. In most scenarios you know more about your expected memory needs to use something more efficient. To be using heap allocation as a default for all memory needs means there is something wrong your design. Reference this article if you'd like to read more into this: [**Memory Allocation Strategies***](https://www.gingerbill.org/article/2019/02/01/memory-allocation-strategies-001/) 

For the scenario where you truly need something expandable you can `malloc` in the constructor and `free` in the destructor to still have RAII. Claude or Codex can one-shot the creation of any general purpose container using this markdown as direction. In all tests so far it has always produced something leaner, and still perfectly suitable, compared to what is in STL.

## Free functions over methods

Compose systems out of **structs and free functions**.

The meat of the program should live in namespace or global functions that take data as parameters. `Do(object)`, not `object.Do()`.

C++ cannot add methods outside the original class definition. Once behavior lives in class methods, extension means breaking the pattern or subclassing.

Free functions stay open. Anyone can add another `Do(object)` against the same struct.

Extension-method languages add machinery to recover what C already had: functions beside data. CFlat keeps the simpler form.

Methods on structs are still useful as shorthand for simple operaiton on Plain-Old-Data. They should not carry the application.

- **Structs only - no encapsulation.** Plain data. Long-lived state lives in static struct allocaton..
- **Free functions for the meat** of everything: `Do(object)`.
- **Member functions only for shorthand POD utilities**: convenience, not substance.

### Namespace whole categories

Use namespaces to group subsystems.

`Render::Submit(frame)` and `Audio::Mix(...)` give scoped call sites without classes, singletons, or lifetime baggage.

The namespace organizes the functions. The data stays in structs passed as parameters.

### Keep a system in one `.hpp` and one `.cpp`

Prefer one translation unit per subsystem. One public `.hpp` and one implementation `.cpp`.

Use a header-only `.hpp` only when the subsystem is genuinely header-only.

- **Compile speed.** One TU parses subsystem headers once and emits one object file. Fewer, larger TUs often reduce total build work and redundant header parsing.
- **Locality.** Structs, public functions, and internal helpers live together. File-local helpers stay out of headers.
- **A clean boundary.** The `.hpp` is the public subsystem surface. The `.cpp` holds everything else.
- **Fewer dependencies.** The graph is subsystem-to-subsystem, not file-per-class sprawl..

## Usable standard headers

STL **headers** still work at compile time. `-nostdlib++` only removes the standard C++ library from the link step. That means header-only facilities work. Link-time facilities do not unless you provide their missing symbols yourself.

### Fully supported

C++ headers supported.

```
<type_traits> <utility> <initializer_list> <tuple> <array> <span>
<string_view>* <optional>* <variant>* <bit> <bitset> <limits>
<concepts> <compare> <numbers> <ratio> <algorithm>**
<version> <source_location>
```

Prefer these `.h` C headers from libc directly. Do not route ordinary C library usage through the C++ wrapper headers unless a specific C++ interop reason requires it.

```
<stdint.h> <stddef.h> <string.h> <math.h> <stdarg.h> <limits.h> <float.h>
<inttypes.h> <stdlib.h> <stdio.h> <time.h>
```

### Conditionally supported

| Header | Supported | Fails to link |
|--------|-------------|---------------|
| `<functional>` | `std::invoke`, `std::ref`, `std::hash`, `std::less` / `plus`, lambdas | `std::function` (`__throw_bad_function_call`) |
| `<new>` | placement `new`, `std::nothrow`, `std::launder` | global `new` / `new[]` / `delete` / `delete[]` unless you provide them |
| `<atomic>` | Lock-free operations on naturally supported scalar atomics | Operations that need out-of-line atomic helpers on the target (`__atomic_*`, sometimes `-latomic`) |
| `<chrono>` | `duration` / `time_point` arithmetic and constants | Clock queries such as `system_clock::now()` / `steady_clock::now()` that require out-of-line library support |
| `<memory>` | `std::addressof`, `std::uninitialized_*` on your buffers, `unique_ptr` over storage you control | `make_unique` / `make_shared` / deleting `unique_ptr<T[]>` without delete support |

### Unsupported

These need libstdc++ for normal use. They hit allocation, throw paths, out-of-line symbols, or static init.

`<vector>` `<string>` `<map>` `<unordered_map>` `<set>` `<deque>`, `<iostream>` `<sstream>` `<fstream>`, `<mutex>` `<regex>` `<locale>`.

A header is usable unless the code you instantiate hits one of three missing pieces:

1. **Heap allocation**: `operator new` / `operator new[]` / `operator delete`.
2. **A throw path**: `std::__throw_length_error`, `__throw_bad_alloc`, `__throw_logic_error`, `__throw_bad_function_call`, `__throw_system_error`, `__throw_out_of_range`, etc.
3. **Out-of-line library symbols or static init**: iostreams, locale, `ios_base::Init`.

Pure template, `constexpr`, and `inline` headers with none of those are fully supported.

## Boilerplate

Keep the build simple: `Makefile`, `build.sh`, or `build.bat`. CFlat depends on visible compiler and linker flags, so avoid meta build systems unless you have a strong reason.

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

CFlat sits in the "C-like C++" lineage.

This section only maps prior art. The rationale lives above.

- [**Orthodox C++**](https://bkaradzic.github.io/posts/orthodoxc++/) - the direct ancestor. Same ban-list. CFlat adds link-time stripping, threadsafe-static tripwires, and restored C99/GNU extensions. Orthodox C++ tries to stay orthodox. CFlat pragmatically uses newer C or C++ features when they support the CFlat philosophy.
- [**"Keep It C-mple"** (Radchenko talk)](https://www.youtube.com/watch?v=lTXHOOwfTAo) - the Orthodox C++ argument as a talk.
- [**Defold engine style**](https://defold.com/2020/05/31/The-Defold-engine-code-style/) - closest in practice: no exceptions/RTTI, custom containers, raw pointers, clear ownership.
- [**A dialect of C++**](https://satish.com.in/20180302/) - similar flags, but keeps the full STL and heap allocation.
- [**"C++, it's not you. It's me."**](https://c0de517e.blogspot.com/2019/02/c-its-not-you-its-me.html) - same spirit as an essay rather than a spec.
- [**Embedded C++ (EC++)**](https://en.wikipedia.org/wiki/Embedded_C%2B%2B) - the opposite trap: it removes templates and namespaces, exactly what CFlat keeps.
- [**"Why Your C++ Should Be Simple"**](http://hacksoflife.blogspot.com/2017/03/why-your-c-should-be-simple.html) - a readability argument, not a runtime strip-down.
- [**Orthodoxy** (Clang plugin)](https://github.com/d-musique/orthodoxy) - an enforcement tool that could mechanically enforce CFlat.

The unusual part is the combination: link-time tripwires plus restored C99/GNU C features.
