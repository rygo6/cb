#!/usr/bin/env python3
import argparse
import csv
import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
SRC_GEN = ROOT / "src_gen"

CFLAT_COMMON = [
    "-fno-exceptions",
    "-fno-rtti",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fvisibility=hidden",
    "-fno-semantic-interposition",
    "-fno-math-errno",
    "-fno-trapping-math",
]

CLANG_C99 = [
    "-Wno-c99-designator",
    "-Wno-c23-extensions",
    "-Wno-vla-cxx-extension",
    "-Wno-address-of-temporary",
    "-Wno-missing-field-initializers",
]

GCC_C99 = [
    "-Wno-pedantic",
    "-Wno-vla",
    "-Wno-missing-field-initializers",
]

LINK_FLAGS = ["-static-libgcc", "-nostdlib++"]
C_COMMON = [
    "-std=gnu11",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
]


CASES = [
    {
        "name": "type_traits",
        "header": "<type_traits>",
        "cpp_includes": "#include <type_traits>\n",
        "cpp_body": """
            using Raw = std::remove_cv_t<const int>;
            using Ptr = std::add_pointer_t<Raw>;
            int value = n;
            if constexpr (std::is_integral_v<Raw>) value += 3;
            if constexpr (std::is_same_v<Ptr, int *>) value += 5;
            if constexpr (std::is_trivially_copyable_v<Raw>) value += 7;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + 3 + 5 + 7;
            *out = value;
            return value;
        """,
    },
    {
        "name": "utility",
        "header": "<utility>",
        "cpp_includes": "#include <utility>\n",
        "cpp_body": """
            std::pair<int, int> p{n, n + 1};
            std::pair<int, int> q = std::make_pair(n + 2, n + 3);
            std::swap(p.second, q.first);
            int old = std::exchange(p.first, q.second);
            int value = old + p.first + p.second + q.first;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            struct Pair { int first; int second; } p = { n, n + 1 }, q = { n + 2, n + 3 };
            int tmp = p.second;
            p.second = q.first;
            q.first = tmp;
            int old = p.first;
            p.first = q.second;
            int value = old + p.first + p.second + q.first;
            *out = value;
            return value;
        """,
    },
    {
        "name": "initializer_list",
        "header": "<initializer_list>",
        "cpp_includes": "#include <initializer_list>\n\nstatic int sum_initializer_list(std::initializer_list<int> values)\n{\n    int sum = 0;\n    for (int v : values) sum += v;\n    return sum;\n}\n",
        "cpp_body": """
            std::initializer_list<int> values = {1, 2, n, 4};
            int sum = int(values.size()) + *values.begin() + sum_initializer_list(values);
            *out = sum;
            return sum;
        """,
        "c_includes": "",
        "c_body": """
            int values[4] = {1, 2, n, 4};
            int sum = 4 + values[0];
            for (int i = 0; i < 4; ++i) sum += values[i];
            *out = sum;
            return sum;
        """,
    },
    {
        "name": "tuple",
        "header": "<tuple>",
        "cpp_includes": "#include <tuple>\n",
        "cpp_body": """
            auto t = std::make_tuple(n, n + 1, n + 2);
            auto [a, b, c] = t;
            int value = std::get<0>(t) + b + c + int(std::tuple_size_v<decltype(t)>);
            value += std::apply([](int x, int y, int z) { return x + y + z; }, t);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            struct T { int a; int b; int c; } t = { n, n + 1, n + 2 };
            int b = t.b;
            int c = t.c;
            int value = t.a + b + c + 3;
            value += t.a + t.b + t.c;
            *out = value;
            return value;
        """,
    },
    {
        "name": "array",
        "header": "<array>",
        "cpp_includes": "#include <array>\n",
        "cpp_body": """
            std::array<int, 4> a = {1, 2, n, 4};
            a.front() += 1;
            a.back() += int(a.size());
            int sum = a[0] + *a.data();
            for (int v : a) sum += v;
            *out = sum;
            return sum;
        """,
        "c_includes": "",
        "c_body": """
            int a[4] = {1, 2, n, 4};
            a[0] += 1;
            a[3] += 4;
            int sum = a[0] + *a;
            for (int i = 0; i < 4; ++i) sum += a[i];
            *out = sum;
            return sum;
        """,
    },
    {
        "name": "span",
        "header": "<span>",
        "cpp_includes": "#include <span>\n",
        "cpp_body": """
            int a[4] = {1, 2, n, 4};
            std::span<int> s(a);
            std::span<int> tail = s.subspan(1, 2);
            int sum = int(s.size()) + s.front() + s.back() + tail[0] + *s.data();
            for (int v : s) sum += v;
            *out = sum;
            return sum;
        """,
        "c_includes": "",
        "c_body": """
            int a[4] = {1, 2, n, 4};
            int sum = 4 + a[0] + a[3] + a[1] + *a;
            for (int i = 0; i < 4; ++i) sum += a[i];
            *out = sum;
            return sum;
        """,
    },
    {
        "name": "string_view",
        "header": "<string_view>",
        "cpp_includes": "#include <string_view>\n",
        "cpp_body": """
            std::string_view s = "cflat";
            s.remove_prefix(1);
            int value = int(s.size()) + s[0] + int(s.find('a')) + int(s.substr(1, 2).size()) + n;
            *out = value;
            return value;
        """,
        "c_includes": "#include <string.h>\n",
        "c_body": """
            const char *base = "cflat";
            size_t len = strlen(base);
            const char *s = base + 1;
            len -= 1;
            const char *found = memchr(s, 'a', len);
            int pos = found ? (int)(found - s) : (int)len;
            size_t sub_len = 2u < len - 1u ? 2u : len - 1u;
            int value = (int)len + s[0] + pos + (int)sub_len + n;
            *out = value;
            return value;
        """,
    },
    {
        "name": "optional",
        "header": "<optional>",
        "cpp_includes": "#include <optional>\n",
        "cpp_body": """
            std::optional<int> v;
            if (!v.has_value()) v.emplace(n);
            int value = v ? *v + v.value_or(2) : 1;
            v.reset();
            value += v.value_or(3);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            struct Optional { int has; int value; } v = {0, 0};
            if (!v.has) { v.has = 1; v.value = n; }
            int value = v.has ? v.value + v.value : 1;
            v.has = 0;
            value += v.has ? v.value : 3;
            *out = value;
            return value;
        """,
    },
    {
        "name": "variant",
        "header": "<variant>",
        "cpp_includes": "#include <variant>\n",
        "cpp_body": """
            std::variant<int, float> v = n;
            int value = std::holds_alternative<int>(v) ? 1 : 0;
            if (int *p = std::get_if<int>(&v)) value += *p + int(v.index());
            v.emplace<float>(float(value));
            value += std::holds_alternative<float>(v) ? 2 : 0;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            struct Variant { int tag; union { int i; float f; } data; } v;
            v.tag = 0;
            v.data.i = n;
            int value = v.tag == 0 ? 1 : 0;
            value += v.tag == 0 ? v.data.i + v.tag : 0;
            v.tag = 1;
            v.data.f = (float)value;
            value += v.tag == 1 ? 2 : 0;
            *out = value;
            return value;
        """,
    },
    {
        "name": "bit",
        "header": "<bit>",
        "cpp_includes": "#include <bit>\n",
        "cpp_body": """
            unsigned x = (unsigned)n | 1u;
            unsigned y = std::rotl(x, 3);
            int value = std::popcount(x) + std::countr_zero(x) + int(std::bit_width(x));
            value += std::has_single_bit(8u) ? 1 : 0;
            value += int(std::bit_floor(y | 1u) != 0);
            *out = value;
            return value;
        """,
        "c_includes": "#include <stdint.h>\n",
        "c_body": """
            unsigned x = (unsigned)n | 1u;
            unsigned y = (x << 3) | (x >> (sizeof(unsigned) * 8 - 3));
            int value = __builtin_popcount(x) + __builtin_ctz(x) + (int)(sizeof(unsigned) * 8 - __builtin_clz(x));
            value += ((8u & (8u - 1u)) == 0u) ? 1 : 0;
            value += ((y | 1u) != 0u) ? 1 : 0;
            *out = value;
            return value;
        """,
    },
    {
        "name": "bitset",
        "header": "<bitset>",
        "cpp_includes": "#include <bitset>\n",
        "cpp_body": """
            std::bitset<32> b((unsigned)n);
            b.set(3);
            b.reset(0);
            b.flip(1);
            int value = int(b.count()) + int(b.test(1));
            value += b.any() ? 1 : 0;
            value += b.none() ? 1 : 0;
            value += int(b.to_ulong() & 15ul);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            unsigned b = (unsigned)n;
            b |= 8u;
            b &= ~1u;
            b ^= 2u;
            int value = __builtin_popcount(b) + ((b >> 1) & 1u);
            value += b != 0u ? 1 : 0;
            value += b == 0u ? 1 : 0;
            value += (int)(b & 15u);
            *out = value;
            return value;
        """,
    },
    {
        "name": "limits",
        "header": "<limits>",
        "cpp_includes": "#include <limits>\n",
        "cpp_body": """
            int value = n;
            value += std::numeric_limits<unsigned char>::min();
            value += std::numeric_limits<unsigned char>::max();
            value += std::numeric_limits<int>::is_signed ? 1 : 0;
            value += std::numeric_limits<int>::digits > 0 ? 1 : 0;
            *out = value;
            return value;
        """,
        "c_includes": "#include <limits.h>\n",
        "c_body": """
            int value = n;
            value += 0;
            value += UCHAR_MAX;
            value += ((int)-1 < 0) ? 1 : 0;
            value += (sizeof(int) * 8 - 1) > 0 ? 1 : 0;
            *out = value;
            return value;
        """,
    },
    {
        "name": "concepts",
        "header": "<concepts>",
        "cpp_includes": "#include <concepts>\n\ntemplate <std::integral T>\nstatic T add_one(T v) { return v + 1; }\n\ntemplate <typename T> requires std::same_as<T, int>\nstatic T add_same(T v) { return v + 2; }\n",
        "cpp_body": """
            int value = add_one(n);
            value = add_same(value);
            if constexpr (std::totally_ordered<int>) value += n < value ? 1 : 0;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + 1;
            value = value + 2;
            value += n < value ? 1 : 0;
            *out = value;
            return value;
        """,
    },
    {
        "name": "compare",
        "header": "<compare>",
        "cpp_includes": "#include <compare>\n\nstruct CmpBox { int v; auto operator<=>(const CmpBox&) const = default; };\n",
        "cpp_body": """
            CmpBox a{n};
            CmpBox b{n + 1};
            auto order = a <=> b;
            int value = (order < 0) ? 1 : 0;
            value += std::is_lt(order) ? 2 : 0;
            value += (a == a) ? 3 : 0;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            struct CmpBox { int v; } a = { n }, b = { n + 1 };
            int cmp = (a.v > b.v) - (a.v < b.v);
            int value = cmp < 0 ? 1 : 0;
            value += cmp < 0 ? 2 : 0;
            value += a.v == a.v ? 3 : 0;
            *out = value;
            return value;
        """,
    },
    {
        "name": "numbers",
        "header": "<numbers>",
        "cpp_includes": "#include <numbers>\n",
        "cpp_body": """
            int value = n;
            value += int(std::numbers::pi * 1000.0);
            value += int(std::numbers::e * 1000.0);
            value += int(std::numbers::sqrt2 * 1000.0);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n;
            value += 3141;
            value += 2718;
            value += 1414;
            *out = value;
            return value;
        """,
    },
    {
        "name": "ratio",
        "header": "<ratio>",
        "cpp_includes": "#include <ratio>\n",
        "cpp_body": """
            using A = std::ratio<1, 3>;
            using B = std::ratio<1, 6>;
            using Sum = std::ratio_add<A, B>;
            using Product = std::ratio_multiply<A, B>;
            using Reduced = std::ratio<2, 4>;
            int value = n + int(Sum::num) + int(Sum::den);
            value += int(Product::num) + int(Product::den);
            value += int(Reduced::num) + int(Reduced::den);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + 1 + 2;
            value += 1 + 18;
            value += 1 + 2;
            *out = value;
            return value;
        """,
    },
    {
        "name": "algorithm",
        "header": "<algorithm>",
        "cpp_includes": "#include <algorithm>\n",
        "cpp_body": """
            int a[4] = {n, 4, 1, 2};
            std::sort(a, a + 4);
            int value = a[0] + a[3];
            value += a[0];
            value += a[3];
            int found = 0;
            for (int i = 0; i < 4; ++i) if (a[i] == 4) found = 1;
            value += found;
            value += n < 1 ? 1 : (n > 4 ? 4 : n);
            value += *std::min_element(a, a + 4);
            value += *std::max_element(a, a + 4);
            value += std::binary_search(a, a + 4, 4) ? 1 : 0;
            value += std::clamp(n, 1, 4);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int a[4] = {n, 4, 1, 2};
            for (int i = 1; i < 4; ++i) {
                int key = a[i];
                int j = i - 1;
                while (j >= 0 && a[j] > key) {
                    a[j + 1] = a[j];
                    --j;
                }
                a[j + 1] = key;
            }
            int value = a[0] + a[3];
            value += a[0];
            value += a[3];
            int found = 0;
            for (int i = 0; i < 4; ++i) if (a[i] == 4) found = 1;
            value += found;
            value += n < 1 ? 1 : (n > 4 ? 4 : n);
            int min_v = a[0];
            int max_v = a[0];
            for (int i = 1; i < 4; ++i) {
                if (a[i] < min_v) min_v = a[i];
                if (a[i] > max_v) max_v = a[i];
            }
            value += min_v;
            value += max_v;
            int lo = 0, hi = 4;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (a[mid] < 4) lo = mid + 1;
                else hi = mid;
            }
            value += (lo < 4 && a[lo] == 4) ? 1 : 0;
            value += n < 1 ? 1 : (n > 4 ? 4 : n);
            *out = value;
            return value;
        """,
    },
    {
        "name": "version",
        "header": "<version>",
        "cpp_includes": "#include <version>\n",
        "cpp_body": """
            int value = n;
            #ifdef __cpp_lib_span
            value += 1;
            #endif
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + 1;
            *out = value;
            return value;
        """,
    },
    {
        "name": "source_location",
        "header": "<source_location>",
        "cpp_includes": "#include <source_location>\n",
        "cpp_body": """
            auto loc = std::source_location::current();
            int value = n + int(loc.line() != 0);
            value += int(loc.column() != 0);
            value += int(loc.file_name()[0] != 0);
            value += int(loc.function_name()[0] != 0);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + (__LINE__ != 0);
            value += 1;
            value += (__FILE__[0] != 0);
            value += 1;
            *out = value;
            return value;
        """,
    },
    {
        "name": "functional",
        "header": "<functional>",
        "cpp_includes": "#include <functional>\n\nstatic int add_functional(int a, int b) { return a + b; }\n",
        "cpp_body": """
            int value = std::invoke(add_functional, n, 3);
            int alias = 4;
            std::reference_wrapper<int> ref = std::ref(alias);
            value += ref.get();
            value += std::less<int>{}(n, value) ? 1 : 0;
            value = std::plus<int>{}(value, int(std::hash<int>{}(3)));
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = n + 3;
            int alias = 4;
            int *ref = &alias;
            value += *ref;
            value += n < value ? 1 : 0;
            value = value + 3;
            *out = value;
            return value;
        """,
    },
    {
        "name": "new",
        "header": "<new>",
        "cpp_includes": "#include <new>\n",
        "cpp_body": """
            alignas(int) unsigned char storage[sizeof(int)];
            int *p = new (storage) int(n + 5);
            int *q = std::launder(reinterpret_cast<int *>(storage));
            int value = *p + *q;
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int storage = n + 5;
            int *p = &storage;
            int *q = &storage;
            int value = *p + *q;
            *out = value;
            return value;
        """,
    },
    {
        "name": "memory",
        "header": "<memory>",
        "cpp_includes": "#include <memory>\n",
        "cpp_body": """
            alignas(int) unsigned char storage[sizeof(int)];
            int source = n + 7;
            int *p = std::construct_at(reinterpret_cast<int *>(storage), source);
            int *addr = std::addressof(*p);
            int *raw = std::to_address(addr);
            int value = *raw;
            std::destroy_at(p);
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int storage = n + 7;
            int *addr = &storage;
            int *raw = addr;
            int value = *raw;
            *out = value;
            return value;
        """,
    },
    {
        "name": "atomic",
        "header": "<atomic>",
        "cpp_includes": "#include <atomic>\n",
        "cpp_body": """
            std::atomic<int> value{n};
            value.store(n + 1, std::memory_order_relaxed);
            value.fetch_add(3, std::memory_order_relaxed);
            int expected = n + 4;
            value.compare_exchange_strong(expected, n + 5, std::memory_order_relaxed);
            int result = value.exchange(value.load(std::memory_order_relaxed) + 1, std::memory_order_relaxed);
            *out = result;
            return result;
        """,
        "c_includes": "#include <stdatomic.h>\n",
        "c_body": """
            atomic_int value;
            atomic_init(&value, n);
            atomic_store_explicit(&value, n + 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&value, 3, memory_order_relaxed);
            int expected = n + 4;
            atomic_compare_exchange_strong_explicit(&value, &expected, n + 5, memory_order_relaxed, memory_order_relaxed);
            int loaded = atomic_load_explicit(&value, memory_order_relaxed);
            int result = atomic_exchange_explicit(&value, loaded + 1, memory_order_relaxed);
            *out = result;
            return result;
        """,
    },
    {
        "name": "chrono",
        "header": "<chrono>",
        "cpp_includes": "#include <chrono>\n",
        "cpp_body": """
            using namespace std::chrono;
            milliseconds a{n};
            microseconds b = duration_cast<microseconds>(a + milliseconds{2});
            time_point<steady_clock, microseconds> t{b};
            t += microseconds{3};
            int value = int(t.time_since_epoch().count());
            *out = value;
            return value;
        """,
        "c_includes": "",
        "c_body": """
            int value = (n + 2) * 1000;
            value += 3;
            *out = value;
            return value;
        """,
    },

]


def add_facility_subcases():
    def clone(base_name, facility, operations, cpp_body, c_body, cpp_includes=None, c_includes=None):
        base = next(c for c in CASES if c.get("header_name", c["name"]) == base_name and c.get("facility", "combined") == "combined")
        CASES.append({
            "name": f"{base_name}.{facility}",
            "header_name": base_name,
            "facility": facility,
            "header": base["header"],
            "operations": operations,
            "cpp_includes": cpp_includes if cpp_includes is not None else base["cpp_includes"],
            "cpp_body": cpp_body,
            "c_includes": c_includes if c_includes is not None else base["c_includes"],
            "c_body": c_body,
        })

    operation_map = {
        "type_traits": "remove_cv_t, add_pointer_t, is_integral_v, is_same_v, is_trivially_copyable_v",
        "utility": "pair, make_pair, swap, exchange",
        "initializer_list": "initializer_list construction, size, begin, range iteration",
        "tuple": "make_tuple, structured binding, get, tuple_size_v, apply",
        "array": "array construction, front, back, size, data, operator[], range iteration",
        "span": "span construction, subspan, size, front, back, data, operator[], range iteration",
        "string_view": "construction, remove_prefix, size, operator[], find, substr",
        "optional": "construction, has_value, emplace, operator bool, operator*, value_or, reset",
        "variant": "construction, holds_alternative, get_if, index, emplace",
        "bit": "rotl, popcount, countr_zero, bit_width, has_single_bit, bit_floor",
        "bitset": "construction, set, reset, flip, count, test, any, none, to_ulong",
        "limits": "numeric_limits min, max, is_signed, digits",
        "concepts": "integral, same_as, requires clause, totally_ordered",
        "compare": "default spaceship, operator<=>, ordering comparison, is_lt, generated equality",
        "numbers": "pi, e, sqrt2",
        "ratio": "ratio, ratio_add, ratio_multiply, compile-time reduction via num/den",
        "algorithm": "sort, min_element, max_element, binary_search, clamp",
        "version": "feature-test macro from <version>",
        "source_location": "current, line, column, file_name, function_name",
        "functional": "invoke, reference_wrapper, ref, less, plus, hash",
        "new": "placement new, launder",
        "memory": "construct_at, addressof, to_address, destroy_at",
        "atomic": "atomic construction, store, fetch_add, compare_exchange_strong, load, exchange",
        "chrono": "milliseconds, microseconds, duration_cast, time_point, time_since_epoch",
    }
    for c in CASES:
        c.setdefault("header_name", c["name"])
        c.setdefault("facility", "combined")
        c.setdefault("operations", operation_map.get(c["header_name"], "combined representative operations"))
        c["name"] = f"{c['header_name']}.combined"

    clone("type_traits", "remove_cv", "remove_cv_t",
        """
            using Raw = std::remove_cv_t<const int>;
            int value = n + int(sizeof(Raw));
            *out = value;
            return value;
        """,
        """
            int value = n + (int)sizeof(int);
            *out = value;
            return value;
        """)
    clone("type_traits", "add_pointer", "add_pointer_t",
        """
            using Ptr = std::add_pointer_t<int>;
            int value = n + int(std::is_same_v<Ptr, int *>);
            *out = value;
            return value;
        """,
        """
            int value = n + 1;
            *out = value;
            return value;
        """)
    clone("type_traits", "type_predicates", "is_integral_v, is_same_v, is_trivially_copyable_v",
        """
            int value = n;
            if constexpr (std::is_integral_v<int>) value += 3;
            if constexpr (std::is_same_v<int, int>) value += 5;
            if constexpr (std::is_trivially_copyable_v<int>) value += 7;
            *out = value;
            return value;
        """,
        """
            int value = n + 3 + 5 + 7;
            *out = value;
            return value;
        """)
    clone("utility", "pair_make_pair", "pair, make_pair",
        """
            std::pair<int, int> p{n, n + 1};
            auto q = std::make_pair(n + 2, n + 3);
            int value = p.first + p.second + q.first + q.second;
            *out = value;
            return value;
        """,
        """
            struct Pair { int first; int second; } p = { n, n + 1 }, q = { n + 2, n + 3 };
            int value = p.first + p.second + q.first + q.second;
            *out = value;
            return value;
        """)
    clone("utility", "swap", "swap",
        """
            int a = n, b = n + 1;
            std::swap(a, b);
            int value = a + b;
            *out = value;
            return value;
        """,
        """
            int a = n, b = n + 1;
            int tmp = a; a = b; b = tmp;
            int value = a + b;
            *out = value;
            return value;
        """)
    clone("utility", "exchange", "exchange",
        """
            int a = n;
            int old = std::exchange(a, n + 3);
            int value = old + a;
            *out = value;
            return value;
        """,
        """
            int a = n;
            int old = a; a = n + 3;
            int value = old + a;
            *out = value;
            return value;
        """)
    clone("initializer_list", "construction_size_begin_iteration", "initializer_list construction, size, begin, range iteration",
        """
            std::initializer_list<int> values = {1, 2, n, 4};
            int sum = int(values.size()) + *values.begin();
            for (int v : values) sum += v;
            *out = sum;
            return sum;
        """,
        """
            int values[4] = {1, 2, n, 4};
            int sum = 4 + values[0];
            for (int i = 0; i < 4; ++i) sum += values[i];
            *out = sum;
            return sum;
        """)
    clone("tuple", "make_tuple_get_tuple_size", "make_tuple, get, tuple_size_v",
        """
            auto t = std::make_tuple(n, n + 1, n + 2);
            int value = std::get<0>(t) + std::get<1>(t) + int(std::tuple_size_v<decltype(t)>);
            *out = value;
            return value;
        """,
        """
            struct T { int a; int b; int c; } t = { n, n + 1, n + 2 };
            int value = t.a + t.b + 3;
            *out = value;
            return value;
        """)
    clone("tuple", "structured_binding", "structured binding",
        """
            auto t = std::make_tuple(n, n + 1, n + 2);
            auto [a, b, c] = t;
            int value = a + b + c;
            *out = value;
            return value;
        """,
        """
            struct T { int a; int b; int c; } t = { n, n + 1, n + 2 };
            int value = t.a + t.b + t.c;
            *out = value;
            return value;
        """)
    clone("tuple", "apply", "apply",
        """
            auto t = std::make_tuple(n, n + 1, n + 2);
            int value = std::apply([](int x, int y, int z) { return x + y + z; }, t);
            *out = value;
            return value;
        """,
        """
            struct T { int a; int b; int c; } t = { n, n + 1, n + 2 };
            int value = t.a + t.b + t.c;
            *out = value;
            return value;
        """)
    clone("span", "construction_size_data", "span construction, size, data",
        """
            int a[4] = {1, 2, n, 4};
            std::span<int> s(a);
            int value = int(s.size()) + *s.data();
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, n, 4};
            int value = 4 + *a;
            *out = value;
            return value;
        """)
    clone("span", "front_back_index_iteration", "front, back, operator[], range iteration",
        """
            int a[4] = {1, 2, n, 4};
            std::span<int> s(a);
            int value = s.front() + s.back() + s[2];
            for (int v : s) value += v;
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, n, 4};
            int value = a[0] + a[3] + a[2];
            for (int i = 0; i < 4; ++i) value += a[i];
            *out = value;
            return value;
        """)
    clone("span", "subspan", "subspan",
        """
            int a[4] = {1, 2, n, 4};
            std::span<int> s(a);
            std::span<int> tail = s.subspan(1, 2);
            int value = int(tail.size()) + tail[0] + tail[1];
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, n, 4};
            int value = 2 + a[1] + a[2];
            *out = value;
            return value;
        """)
    clone("string_view", "construction_size_index", "construction, size, operator[]",
        """
            std::string_view s = "cflat";
            int value = int(s.size()) + s[0] + n;
            *out = value;
            return value;
        """,
        """
            const char *s = "cflat";
            int value = (int)strlen(s) + s[0] + n;
            *out = value;
            return value;
        """,
        c_includes="#include <string.h>\n")
    clone("string_view", "remove_prefix", "remove_prefix",
        """
            std::string_view s = "cflat";
            s.remove_prefix(1);
            int value = int(s.size()) + s[0] + n;
            *out = value;
            return value;
        """,
        """
            const char *s = "cflat";
            size_t len = strlen(s);
            s += 1;
            len -= 1;
            int value = (int)len + s[0] + n;
            *out = value;
            return value;
        """,
        c_includes="#include <string.h>\n")
    clone("string_view", "find", "find",
        """
            std::string_view s = "cflat";
            int value = int(s.find('a')) + n;
            *out = value;
            return value;
        """,
        """
            const char *s = "cflat";
            const char *found = memchr(s, 'a', strlen(s));
            int value = (found ? (int)(found - s) : (int)strlen(s)) + n;
            *out = value;
            return value;
        """,
        c_includes="#include <string.h>\n")
    clone("string_view", "substr", "substr",
        """
            std::string_view s = "cflat";
            auto sub = s.substr(1, 2);
            int value = int(sub.size()) + sub[0] + n;
            *out = value;
            return value;
        """,
        """
            const char *s = "cflat";
            size_t len = strlen(s);
            const char *sub = s + 1;
            size_t sub_len = 2u < len - 1u ? 2u : len - 1u;
            int value = (int)sub_len + sub[0] + n;
            *out = value;
            return value;
        """,
        c_includes="#include <string.h>\n")
    clone("optional", "construction_has_value_emplace", "construction, has_value, emplace",
        """
            std::optional<int> v;
            if (!v.has_value()) v.emplace(n);
            int value = v.has_value() ? *v : 0;
            *out = value;
            return value;
        """,
        """
            struct Optional { int has; int value; } v = {0, 0};
            if (!v.has) { v.has = 1; v.value = n; }
            int value = v.has ? v.value : 0;
            *out = value;
            return value;
        """)
    clone("optional", "bool_deref", "operator bool, operator*",
        """
            std::optional<int> v{n};
            int value = v ? *v : 0;
            *out = value;
            return value;
        """,
        """
            struct Optional { int has; int value; } v = {1, n};
            int value = v.has ? v.value : 0;
            *out = value;
            return value;
        """)
    clone("optional", "value_or_reset", "value_or, reset",
        """
            std::optional<int> v{n};
            int value = v.value_or(2);
            v.reset();
            value += v.value_or(3);
            *out = value;
            return value;
        """,
        """
            struct Optional { int has; int value; } v = {1, n};
            int value = v.has ? v.value : 2;
            v.has = 0;
            value += v.has ? v.value : 3;
            *out = value;
            return value;
        """)
    clone("variant", "construction_holds_alternative", "construction, holds_alternative",
        """
            std::variant<int, float> v = n;
            int value = std::holds_alternative<int>(v) ? n : 0;
            *out = value;
            return value;
        """,
        """
            struct Variant { int tag; union { int i; float f; } data; } v;
            v.tag = 0; v.data.i = n;
            int value = v.tag == 0 ? v.data.i : 0;
            *out = value;
            return value;
        """)
    clone("variant", "get_if_index", "get_if, index",
        """
            std::variant<int, float> v = n;
            int value = int(v.index());
            if (int *p = std::get_if<int>(&v)) value += *p;
            *out = value;
            return value;
        """,
        """
            struct Variant { int tag; union { int i; float f; } data; } v;
            v.tag = 0; v.data.i = n;
            int value = v.tag;
            if (v.tag == 0) value += v.data.i;
            *out = value;
            return value;
        """)
    clone("variant", "emplace", "emplace",
        """
            std::variant<int, float> v = n;
            v.emplace<float>(float(n + 1));
            int value = std::holds_alternative<float>(v) ? n + 1 : 0;
            *out = value;
            return value;
        """,
        """
            struct Variant { int tag; union { int i; float f; } data; } v;
            v.tag = 1; v.data.f = (float)(n + 1);
            int value = v.tag == 1 ? n + 1 : 0;
            *out = value;
            return value;
        """)
    clone("bit", "rotl", "rotl",
        """
            unsigned x = (unsigned)n | 1u;
            int value = int(std::rotl(x, 3));
            *out = value;
            return value;
        """,
        """
            unsigned x = (unsigned)n | 1u;
            int value = (int)((x << 3) | (x >> (sizeof(unsigned) * 8 - 3)));
            *out = value;
            return value;
        """)
    clone("bit", "popcount", "popcount",
        """
            unsigned x = (unsigned)n | 1u;
            int value = std::popcount(x);
            *out = value;
            return value;
        """,
        """
            unsigned x = (unsigned)n | 1u;
            int value = __builtin_popcount(x);
            *out = value;
            return value;
        """)
    clone("bit", "countr_zero", "countr_zero",
        """
            unsigned x = (unsigned)n | 1u;
            int value = std::countr_zero(x);
            *out = value;
            return value;
        """,
        """
            unsigned x = (unsigned)n | 1u;
            int value = __builtin_ctz(x);
            *out = value;
            return value;
        """)
    clone("bit", "bit_width", "bit_width",
        """
            unsigned x = (unsigned)n | 1u;
            int value = int(std::bit_width(x));
            *out = value;
            return value;
        """,
        """
            unsigned x = (unsigned)n | 1u;
            int value = (int)(sizeof(unsigned) * 8 - __builtin_clz(x));
            *out = value;
            return value;
        """)
    clone("bit", "has_single_bit", "has_single_bit",
        """
            int value = std::has_single_bit(8u) ? n : 0;
            *out = value;
            return value;
        """,
        """
            int value = ((8u & (8u - 1u)) == 0u) ? n : 0;
            *out = value;
            return value;
        """)
    clone("bit", "bit_floor", "bit_floor",
        """
            unsigned x = (unsigned)n | 1u;
            int value = int(std::bit_floor(x));
            *out = value;
            return value;
        """,
        """
            unsigned x = (unsigned)n | 1u;
            int value = (int)(1u << (sizeof(unsigned) * 8 - 1 - __builtin_clz(x)));
            *out = value;
            return value;
        """)
    clone("bitset", "construction_to_ulong", "construction, to_ulong",
        """
            std::bitset<32> b((unsigned)n);
            int value = int(b.to_ulong() & 15ul);
            *out = value;
            return value;
        """,
        """
            unsigned b = (unsigned)n;
            int value = (int)(b & 15u);
            *out = value;
            return value;
        """)
    clone("bitset", "set_reset_flip", "set, reset, flip",
        """
            std::bitset<32> b((unsigned)n);
            b.set(3);
            b.reset(0);
            b.flip(1);
            int value = int(b.to_ulong() & 15ul);
            *out = value;
            return value;
        """,
        """
            unsigned b = (unsigned)n;
            b |= 8u;
            b &= ~1u;
            b ^= 2u;
            int value = (int)(b & 15u);
            *out = value;
            return value;
        """)
    clone("bitset", "count_test", "count, test",
        """
            std::bitset<32> b((unsigned)n);
            int value = int(b.count()) + int(b.test(1));
            *out = value;
            return value;
        """,
        """
            unsigned b = (unsigned)n;
            int value = __builtin_popcount(b) + (int)((b >> 1) & 1u);
            *out = value;
            return value;
        """)
    clone("bitset", "any_none", "any, none",
        """
            std::bitset<32> b((unsigned)n);
            int value = (b.any() ? 1 : 0) + (b.none() ? 1 : 0);
            *out = value;
            return value;
        """,
        """
            unsigned b = (unsigned)n;
            int value = (b != 0u ? 1 : 0) + (b == 0u ? 1 : 0);
            *out = value;
            return value;
        """)
    clone("limits", "min_max", "numeric_limits min, max",
        """
            int value = n;
            value += std::numeric_limits<unsigned char>::min();
            value += std::numeric_limits<unsigned char>::max();
            *out = value;
            return value;
        """,
        """
            int value = n + 0 + UCHAR_MAX;
            *out = value;
            return value;
        """)
    clone("limits", "is_signed_digits", "numeric_limits is_signed, digits",
        """
            int value = n;
            value += std::numeric_limits<int>::is_signed ? 1 : 0;
            value += std::numeric_limits<int>::digits > 0 ? 1 : 0;
            *out = value;
            return value;
        """,
        """
            int value = n;
            value += ((int)-1 < 0) ? 1 : 0;
            value += (sizeof(int) * 8 - 1) > 0 ? 1 : 0;
            *out = value;
            return value;
        """)
    clone("concepts", "integral", "integral",
        """
            auto add_one = []<std::integral T>(T v) { return v + 1; };
            int value = add_one(n);
            *out = value;
            return value;
        """,
        """
            int value = n + 1;
            *out = value;
            return value;
        """)
    clone("concepts", "same_as_requires", "same_as, requires clause",
        """
            auto add_same = []<typename T>(T v) requires std::same_as<T, int> { return v + 2; };
            int value = add_same(n);
            *out = value;
            return value;
        """,
        """
            int value = n + 2;
            *out = value;
            return value;
        """)
    clone("concepts", "totally_ordered", "totally_ordered",
        """
            int value = n;
            if constexpr (std::totally_ordered<int>) value += 1;
            *out = value;
            return value;
        """,
        """
            int value = n + 1;
            *out = value;
            return value;
        """)
    clone("compare", "spaceship_ordering", "operator<=>, ordering comparison, is_lt",
        """
            CmpBox a{n};
            CmpBox b{n + 1};
            auto order = a <=> b;
            int value = (order < 0) ? 1 : 0;
            value += std::is_lt(order) ? 2 : 0;
            *out = value;
            return value;
        """,
        """
            struct CmpBox { int v; } a = { n }, b = { n + 1 };
            int cmp = (a.v > b.v) - (a.v < b.v);
            int value = cmp < 0 ? 1 : 0;
            value += cmp < 0 ? 2 : 0;
            *out = value;
            return value;
        """)
    clone("compare", "generated_equality", "default spaceship, generated equality",
        """
            CmpBox a{n};
            int value = (a == a) ? n : 0;
            *out = value;
            return value;
        """,
        """
            struct CmpBox { int v; } a = { n };
            int value = a.v == a.v ? n : 0;
            *out = value;
            return value;
        """)
    clone("numbers", "pi", "pi",
        """
            int value = n + int(std::numbers::pi * 1000.0);
            *out = value;
            return value;
        """,
        """
            int value = n + 3141;
            *out = value;
            return value;
        """)
    clone("numbers", "e", "e",
        """
            int value = n + int(std::numbers::e * 1000.0);
            *out = value;
            return value;
        """,
        """
            int value = n + 2718;
            *out = value;
            return value;
        """)
    clone("numbers", "sqrt2", "sqrt2",
        """
            int value = n + int(std::numbers::sqrt2 * 1000.0);
            *out = value;
            return value;
        """,
        """
            int value = n + 1414;
            *out = value;
            return value;
        """)
    clone("ratio", "ratio_add", "ratio, ratio_add",
        """
            using A = std::ratio<1, 3>;
            using B = std::ratio<1, 6>;
            using Sum = std::ratio_add<A, B>;
            int value = n + int(Sum::num) + int(Sum::den);
            *out = value;
            return value;
        """,
        """
            int value = n + 1 + 2;
            *out = value;
            return value;
        """)
    clone("ratio", "ratio_multiply", "ratio_multiply",
        """
            using A = std::ratio<1, 3>;
            using B = std::ratio<1, 6>;
            using Product = std::ratio_multiply<A, B>;
            int value = n + int(Product::num) + int(Product::den);
            *out = value;
            return value;
        """,
        """
            int value = n + 1 + 18;
            *out = value;
            return value;
        """)
    clone("ratio", "reduction", "compile-time reduction via num/den",
        """
            using Reduced = std::ratio<2, 4>;
            int value = n + int(Reduced::num) + int(Reduced::den);
            *out = value;
            return value;
        """,
        """
            int value = n + 1 + 2;
            *out = value;
            return value;
        """)
    clone("version", "feature_test_macro", "feature-test macro from <version>",
        """
            int value = n;
            #ifdef __cpp_lib_span
            value += 1;
            #endif
            *out = value;
            return value;
        """,
        """
            int value = n + 1;
            *out = value;
            return value;
        """)
    clone("source_location", "current_line_column", "current, line, column",
        """
            auto loc = std::source_location::current();
            int value = n + int(loc.line() != 0);
            value += int(loc.column() != 0);
            *out = value;
            return value;
        """,
        """
            int value = n + (__LINE__ != 0);
            value += 1;
            *out = value;
            return value;
        """)
    clone("source_location", "file_function_name", "file_name, function_name",
        """
            auto loc = std::source_location::current();
            int value = n + int(loc.file_name()[0] != 0);
            value += int(loc.function_name()[0] != 0);
            *out = value;
            return value;
        """,
        """
            int value = n + (__FILE__[0] != 0);
            value += 1;
            *out = value;
            return value;
        """)
    clone("functional", "invoke", "invoke",
        """
            int value = std::invoke(add_functional, n, 3);
            *out = value;
            return value;
        """,
        """
            int value = n + 3;
            *out = value;
            return value;
        """)
    clone("functional", "reference_wrapper_ref", "reference_wrapper, ref",
        """
            int alias = n;
            std::reference_wrapper<int> ref = std::ref(alias);
            int value = ref.get();
            *out = value;
            return value;
        """,
        """
            int alias = n;
            int *ref = &alias;
            int value = *ref;
            *out = value;
            return value;
        """)
    clone("functional", "less_plus", "less, plus",
        """
            int value = std::less<int>{}(n, n + 1) ? 1 : 0;
            value = std::plus<int>{}(value, n);
            *out = value;
            return value;
        """,
        """
            int value = n < n + 1 ? 1 : 0;
            value = value + n;
            *out = value;
            return value;
        """)
    clone("functional", "hash", "hash",
        """
            int value = n + int(std::hash<int>{}(3));
            *out = value;
            return value;
        """,
        """
            int value = n + 3;
            *out = value;
            return value;
        """)
    clone("new", "placement_new", "placement new",
        """
            alignas(int) unsigned char storage[sizeof(int)];
            int *p = new (storage) int(n + 5);
            int value = *p;
            *out = value;
            return value;
        """,
        """
            int storage = n + 5;
            int *p = &storage;
            int value = *p;
            *out = value;
            return value;
        """)
    clone("new", "launder", "launder",
        """
            alignas(int) unsigned char storage[sizeof(int)];
            int *p = new (storage) int(n + 5);
            int *q = std::launder(reinterpret_cast<int *>(storage));
            int value = *p + *q;
            *out = value;
            return value;
        """,
        """
            int storage = n + 5;
            int *p = &storage;
            int *q = &storage;
            int value = *p + *q;
            *out = value;
            return value;
        """)
    clone("memory", "construct_destroy_at", "construct_at, destroy_at",
        """
            alignas(int) unsigned char storage[sizeof(int)];
            int *p = std::construct_at(reinterpret_cast<int *>(storage), n + 7);
            int value = *p;
            std::destroy_at(p);
            *out = value;
            return value;
        """,
        """
            int storage = n + 7;
            int value = storage;
            *out = value;
            return value;
        """)
    clone("memory", "addressof_to_address", "addressof, to_address",
        """
            int source = n + 7;
            int *addr = std::addressof(source);
            int *raw = std::to_address(addr);
            int value = *raw;
            *out = value;
            return value;
        """,
        """
            int source = n + 7;
            int *addr = &source;
            int *raw = addr;
            int value = *raw;
            *out = value;
            return value;
        """)
    clone("chrono", "durations_duration_cast", "milliseconds, microseconds, duration_cast",
        """
            using namespace std::chrono;
            milliseconds a{n};
            microseconds b = duration_cast<microseconds>(a + milliseconds{2});
            int value = int(b.count());
            *out = value;
            return value;
        """,
        """
            int value = (n + 2) * 1000;
            *out = value;
            return value;
        """)
    clone("chrono", "time_point_time_since_epoch", "time_point, time_since_epoch",
        """
            using namespace std::chrono;
            time_point<steady_clock, microseconds> t{microseconds{n}};
            t += microseconds{3};
            int value = int(t.time_since_epoch().count());
            *out = value;
            return value;
        """,
        """
            int value = n + 3;
            *out = value;
            return value;
        """)
    clone("array", "front_back_size_data", "front, back, size, data",
        """
            std::array<int, 4> a = {1, 2, n, 4};
            a.front() += 1;
            a.back() += int(a.size());
            int value = a.front() + a.back() + *a.data();
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, n, 4};
            a[0] += 1;
            a[3] += 4;
            int value = a[0] + a[3] + *a;
            *out = value;
            return value;
        """)
    clone("array", "index_iteration", "operator[], range iteration",
        """
            std::array<int, 4> a = {1, 2, n, 4};
            int value = a[2];
            for (int v : a) value += v;
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, n, 4};
            int value = a[2];
            for (int i = 0; i < 4; ++i) value += a[i];
            *out = value;
            return value;
        """)
    clone("algorithm", "sort", "sort",
        """
            int a[4] = {n, 4, 1, 2};
            std::sort(a, a + 4);
            int value = a[0] + a[1] + a[2] + a[3];
            *out = value;
            return value;
        """,
        """
            int a[4] = {n, 4, 1, 2};
            for (int i = 1; i < 4; ++i) {
                int key = a[i];
                int j = i - 1;
                while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; --j; }
                a[j + 1] = key;
            }
            int value = a[0] + a[1] + a[2] + a[3];
            *out = value;
            return value;
        """)
    clone("algorithm", "min_max_element", "min_element, max_element",
        """
            int a[4] = {n, 4, 1, 2};
            int value = *std::min_element(a, a + 4) + *std::max_element(a, a + 4);
            *out = value;
            return value;
        """,
        """
            int a[4] = {n, 4, 1, 2};
            int min_v = a[0], max_v = a[0];
            for (int i = 1; i < 4; ++i) { if (a[i] < min_v) min_v = a[i]; if (a[i] > max_v) max_v = a[i]; }
            int value = min_v + max_v;
            *out = value;
            return value;
        """)
    clone("algorithm", "binary_search", "binary_search",
        """
            int a[4] = {1, 2, 4, 8};
            int needle = (n & 1) ? 4 : 8;
            int value = std::binary_search(a, a + 4, needle) ? 1 : 0;
            *out = value;
            return value;
        """,
        """
            int a[4] = {1, 2, 4, 8};
            int needle = (n & 1) ? 4 : 8;
            int lo = 0, hi = 4;
            while (lo < hi) { int mid = lo + (hi - lo) / 2; if (a[mid] < needle) lo = mid + 1; else hi = mid; }
            int value = (lo < 4 && a[lo] == needle) ? 1 : 0;
            *out = value;
            return value;
        """)
    clone("algorithm", "clamp", "clamp",
        """
            int value = std::clamp(n, 1, 4);
            value += std::clamp(n + 3, 1, 8);
            *out = value;
            return value;
        """,
        """
            int value = n < 1 ? 1 : (n > 4 ? 4 : n);
            value += (n + 3) < 1 ? 1 : ((n + 3) > 8 ? 8 : (n + 3));
            *out = value;
            return value;
        """)
    clone("atomic", "store_load_fetch_add", "store, load, fetch_add",
        """
            std::atomic<int> value{n};
            value.store(n + 1, std::memory_order_relaxed);
            value.fetch_add(3, std::memory_order_relaxed);
            int result = value.load(std::memory_order_relaxed);
            *out = result;
            return result;
        """,
        """
            atomic_int value;
            atomic_init(&value, n);
            atomic_store_explicit(&value, n + 1, memory_order_relaxed);
            atomic_fetch_add_explicit(&value, 3, memory_order_relaxed);
            int result = atomic_load_explicit(&value, memory_order_relaxed);
            *out = result;
            return result;
        """,
        c_includes="#include <stdatomic.h>\n")
    clone("atomic", "compare_exchange", "compare_exchange_strong",
        """
            std::atomic<int> value{n + 4};
            int expected = n + 4;
            value.compare_exchange_strong(expected, n + 5, std::memory_order_relaxed);
            int result = value.load(std::memory_order_relaxed) + expected;
            *out = result;
            return result;
        """,
        """
            atomic_int value;
            atomic_init(&value, n + 4);
            int expected = n + 4;
            atomic_compare_exchange_strong_explicit(&value, &expected, n + 5, memory_order_relaxed, memory_order_relaxed);
            int result = atomic_load_explicit(&value, memory_order_relaxed) + expected;
            *out = result;
            return result;
        """,
        c_includes="#include <stdatomic.h>\n")
    clone("atomic", "exchange", "exchange",
        """
            std::atomic<int> value{n};
            int result = value.exchange(n + 1, std::memory_order_relaxed);
            result += value.load(std::memory_order_relaxed);
            *out = result;
            return result;
        """,
        """
            atomic_int value;
            atomic_init(&value, n);
            int result = atomic_exchange_explicit(&value, n + 1, memory_order_relaxed);
            result += atomic_load_explicit(&value, memory_order_relaxed);
            *out = result;
            return result;
        """,
        c_includes="#include <stdatomic.h>\n")

    CASES[:] = [
        c for c in CASES
        if c["facility"] != "combined"
    ]


add_facility_subcases()


def compiler_kind(cxx):
    try:
        out = subprocess.check_output([cxx, "--version"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return "unknown"
    return "clang" if "clang" in out.lower() else "gcc"


def write_case_sources(case):
    cpp = SRC_GEN / f"{case['name']}.cpp"
    c = SRC_GEN / f"{case['name']}.c"
    cpp_driver = SRC_GEN / f"{case['name']}.driver.cpp"
    c_driver = SRC_GEN / f"{case['name']}.driver.c"
    symbol = case['name'].replace('.', '_')
    cpp.write_text(f"""// Generated by stl_header_bench/run.py
{case['cpp_includes']}
extern "C" __attribute__((noinline)) int cpp_case_{symbol}(int n, int *out)
{{
{case['cpp_body']}
}}
""")
    c.write_text(f"""/* Generated by stl_header_bench/run.py */
{case['c_includes']}
__attribute__((noinline)) int c_case_{symbol}(int n, int *out)
{{
{case['c_body']}
}}
""")
    cpp_driver.write_text(f"""// Generated by stl_header_bench/run.py
extern "C" int cpp_case_{symbol}(int n, int *out);
int main()
{{
    int out = 0;
    int result = cpp_case_{symbol}(7, &out);
    if (result != out) return 255;
    return result & 255;
}}
""")
    c_driver.write_text(f"""/* Generated by stl_header_bench/run.py */
int c_case_{symbol}(int n, int *out);
int main(void)
{{
    int out = 0;
    int result = c_case_{symbol}(7, &out);
    if (result != out) return 255;
    return result & 255;
}}
""")
    return cpp, c, cpp_driver, c_driver


def run_cmd(cmd):
    start = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, time.perf_counter() - start, proc.stdout, proc.stderr


def command_version(cmd):
    proc = subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return "unknown"
    lines = proc.stdout.strip().splitlines()
    return lines[0] if lines else "unknown"


def os_version():
    os_release = Path("/etc/os-release")
    if os_release.exists():
        for line in os_release.read_text(errors="ignore").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    return platform.platform()


def cpu_model():
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(errors="ignore").splitlines():
            if line.startswith("model name") or line.startswith("Hardware") or line.startswith("Processor"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def shell_join(cmd):
    return subprocess.list2cmdline([str(x) for x in cmd])


def median_time(cmd, repeats):
    times = []
    last = None
    for _ in range(repeats):
        last = run_cmd(cmd)
        if last[0] != 0:
            return last[0], None, last[2], last[3]
        times.append(last[1])
    times.sort()
    return 0, times[len(times) // 2], last[2], last[3]


def text_size(path):
    proc = subprocess.run(["size", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return None
    lines = proc.stdout.strip().splitlines()
    if len(lines) < 2:
        return None
    return int(lines[1].split()[0])


def instruction_count(path):
    count = 0
    insn = re.compile(r"^\s+[a-zA-Z][a-zA-Z0-9_.]*\b")
    with open(path, "r", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.endswith(":") or stripped.startswith(".") or stripped.startswith("#"):
                continue
            if insn.match(line):
                count += 1
    return count


def ratio(cpp, c):
    if c in (None, 0) or cpp is None:
        return None
    return cpp / c


def fmt_ratio(value):
    if value is None:
        return "n/a"
    return f"{value:.2f}x"


def fmt_seconds(value):
    if value is None:
        return "fail"
    return f"{value:.4f}s"


def fmt_value(value):
    if value is None:
        return "fail"
    return str(value)


def as_float(value):
    if value in (None, "", "None"):
        return None
    return float(value)


def ok_bool(value):
    return value is True or value == "True"


def report_row(f, name, row, *, indent=False):
    display_name = f"&nbsp;&nbsp;`{name}`" if indent else f"`{name}`"
    f.write(
        f"| {display_name} | {fmt_seconds(as_float(row['cpp_compile_s']))} / {fmt_seconds(as_float(row['c_compile_s']))} "
        f"({fmt_ratio(as_float(row['compile_ratio']))}) | "
        f"{fmt_ratio(as_float(row['text_ratio']))} | "
        f"{fmt_ratio(as_float(row['insn_ratio']))} | {row['verdict']} |\n"
    )


def summary_report_row(f, row):
    f.write(
        f"| `{row['header_name']}.combined` | {fmt_ratio(row['text_ratio'])} | "
        f"{fmt_ratio(row['insn_ratio'])} | {row['verdict']} |\n"
    )


def overview_report_row(f, row):
    link = "ok" if ok_bool(row.get("link_ok")) else "fail"
    runtime = "ok" if ok_bool(row.get("runtime_match")) else "fail"
    f.write(
        f"| `{row['case']}` | {link} | {runtime} |\n"
    )


def combined_overview_report_row(f, facility, by_label, labels):
    link_ok_all = True
    runtime_ok_all = True
    compiler_ok_all = True
    for label in labels:
        row = by_label.get(label)
        link_ok = row is not None and ok_bool(row.get("link_ok"))
        runtime_ok = row is not None and ok_bool(row.get("runtime_match"))
        link_ok_all = link_ok_all and link_ok
        runtime_ok_all = runtime_ok_all and runtime_ok
        compiler_ok_all = compiler_ok_all and link_ok and runtime_ok
    f.write(
        f"| `{facility}` | {'ok' if link_ok_all else 'fail'} | "
        f"{'ok' if runtime_ok_all else 'fail'} | {'ok' if compiler_ok_all else 'fail'} |\n"
    )


def compile_time_report_row(f, row):
    f.write(
        f"| `{row['case']}` | {fmt_seconds(as_float(row['cpp_compile_s']))} / {fmt_seconds(as_float(row['c_compile_s']))} "
        f"({fmt_ratio(as_float(row['compile_ratio']))}) |\n"
    )


def median(values):
    if not values:
        return None
    vals = sorted(values)
    return vals[len(vals) // 2]


def average(values):
    if not values:
        return None
    return sum(values) / len(values)


def compile_time_stats_row(f, label, rows):
    cpp_times = [as_float(r["cpp_compile_s"]) for r in rows if as_float(r["cpp_compile_s"]) is not None]
    c_times = [as_float(r["c_compile_s"]) for r in rows if as_float(r["c_compile_s"]) is not None]
    ratios = [as_float(r["compile_ratio"]) for r in rows if as_float(r["compile_ratio"]) is not None]
    f.write(f"Summary for `{label}` O2 facility rows:\n\n")
    f.write("| Metric | Median | Min | Max | Average |\n")
    f.write("|--------|--------|-----|-----|---------|\n")
    f.write(
        f"| C++ compile time | {fmt_seconds(median(cpp_times))} | {fmt_seconds(min(cpp_times) if cpp_times else None)} | "
        f"{fmt_seconds(max(cpp_times) if cpp_times else None)} | {fmt_seconds(average(cpp_times))} |\n"
    )
    f.write(
        f"| C compile time | {fmt_seconds(median(c_times))} | {fmt_seconds(min(c_times) if c_times else None)} | "
        f"{fmt_seconds(max(c_times) if c_times else None)} | {fmt_seconds(average(c_times))} |\n"
    )
    f.write(
        f"| C++ / C ratio | {fmt_ratio(median(ratios))} | {fmt_ratio(min(ratios) if ratios else None)} | "
        f"{fmt_ratio(max(ratios) if ratios else None)} | {fmt_ratio(average(ratios))} |\n\n"
    )


def report_entries(label, rows, summaries):
    label_rows = [x for x in rows if x["label"] == label and x["opt"] == "O2"]
    combined_rows = {r["header_name"]: r for r in label_rows if r["facility"] == "combined"}
    summary_rows = {r["header_name"]: r for r in summaries if r["label"] == label and r["opt"] == "O2"}
    entries = []
    for header_name in sorted(summary_rows):
        combined = combined_rows.get(header_name)
        if combined is not None:
            entries.append((combined["case"], combined, False))
            combined_verdict = combined["verdict"]
        else:
            combined = summary_rows[header_name]
            entries.append((f"{header_name}.combined", combined, False))
            combined_verdict = combined["verdict"]
        if combined_verdict == "Precisely C":
            continue
        subrows = [
            r for r in label_rows
            if r["header_name"] == header_name
            and r["facility"] != "combined"
            and r["verdict"] != "Precisely C"
        ]
        for r in subrows:
            entries.append((r["case"], r, True))
    return entries



def verdict(row):
    if row["status"] != "ok":
        return "Does not link" if row.get("link_ok") in (False, "False") else "Fail"
    tr = row["text_ratio"] if isinstance(row["text_ratio"], float) else float(row["text_ratio"] or 0)
    ir = row["insn_ratio"] if isinstance(row["insn_ratio"], float) else float(row["insn_ratio"] or 0)
    worst = max(tr, ir)
    if tr < 0.99 and ir < 0.99:
        return "Slightly Better Than C"
    if worst <= 1.01:
        return "Precisely C"
    if worst <= 1.05:
        return "Approximately C"
    if worst <= 1.25:
        return "Near C"
    if worst <= 2.0:
        return "Some overhead"
    return "Worse assembly"


def verdict_rank(v):
    return {"Slightly Better Than C": 0, "Precisely C": 1, "Approximately C": 2, "Near C": 3, "Some overhead": 4, "Worse assembly": 5, "Does not link": 6, "Fail": 7}.get(v, 6)


def read_result_rows():
    rows = []
    for path in sorted(BUILD.glob("results.*.csv")):
        with path.open(newline="") as f:
            rows.extend(csv.DictReader(f))
    return rows


def aggregate(rows):
    groups = {}
    for row in rows:
        groups.setdefault((row.get("label", "unknown"), row["header_name"], row["header"], row["opt"]), []).append(row)
    out = []
    for (label, header_name, header, opt), items in sorted(groups.items()):
        def sf(k):
            vals = [float(i[k]) for i in items if i[k] not in ("", "None")]
            return sum(vals) if len(vals) == len(items) else None
        cpp_text, c_text = sf("cpp_text"), sf("c_text")
        cpp_insn, c_insn = sf("cpp_insn"), sf("c_insn")
        cpp_compile, c_compile = sf("cpp_compile_s"), sf("c_compile_s")
        status = "ok" if all(i["status"] == "ok" for i in items) else "fail"
        row = {"label": label, "header_name": header_name, "header": header, "opt": opt, "facility_count": len(items),
               "cpp_compile_s": cpp_compile, "c_compile_s": c_compile, "compile_ratio": ratio(cpp_compile, c_compile),
               "cpp_text": cpp_text, "c_text": c_text, "text_ratio": ratio(cpp_text, c_text),
               "cpp_insn": cpp_insn, "c_insn": c_insn, "insn_ratio": ratio(cpp_insn, c_insn), "status": status}
        row["verdict"] = verdict(row)
        out.append(row)
    return out


def write_final_report():
    rows = read_result_rows()
    if not rows:
        return
    for row in rows:
        row.setdefault("label", "unknown")
        row.setdefault("header_name", row["case"].split(".")[0])
        row.setdefault("facility", ".".join(row["case"].split(".")[1:]) or "combined")
        row["verdict"] = verdict(row)
    summaries = aggregate(rows)
    labels = sorted(set(r["label"] for r in rows))
    with (ROOT / "STL_HEADER_ONLY_RESULTS.md").open("w") as f:
        f.write("# STL header-only compile and assembly results\n\n")
        f.write("This report is generated from `stl_header_bench/run.py`.\n\n")
        f.write("Each row compares a C++ STL header facility with a semantically matched C equivalent.\n\n")
        f.write("Verdicts use the `-O2` text and instruction ratios:\n\n")
        f.write("- `Slightly Better Than C`: both C++ text and instruction ratios are below 0.99x C\n")
        f.write("- `Precisely C`: within 1 percent of C\n")
        f.write("- `Approximately C`: within 5 percent of C\n")
        f.write("- `Near C`: within 25 percent of C\n")
        f.write("- `Some overhead`: up to 2x C\n")
        f.write("- `Worse assembly`: more than 2x C\n")
        f.write("- `Does not link`: fails the CFlat `-nostdlib++` link check\n\n")
        f.write("## Run Environment\n\n")
        f.write("| Label | C++ compiler | C compiler | OS | CPU |\n")
        f.write("|-------|--------------|------------|----|-----|\n")
        for label in labels:
            row = next(r for r in rows if r["label"] == label)
            f.write(
                f"| {label} | `{row.get('cxx_version', 'unknown')}` | "
                f"`{row.get('cc_version', 'unknown')}` | {row.get('os_version', 'unknown')} | "
                f"{row.get('cpu_model', 'unknown')} |\n"
            )
        f.write("\n")
        f.write("## Compiler Flags\n\n")
        f.write("| Label | C++ compile flags | C++ link flags | C compile flags |\n")
        f.write("|-------|-------------------|----------------|-----------------|\n")
        for label in labels:
            row = next(r for r in rows if r["label"] == label)
            f.write(
                f"| {label} | `{row.get('cxx_flags', 'unknown')}` | "
                f"`{row.get('cxx_link_flags', 'unknown')}` | "
                f"`{row.get('c_flags', 'unknown')}` |\n"
            )
        f.write("\n")
        f.write("## Command Templates\n\n")
        f.write("Commands are shown with placeholders for the optimization level, generated source, generated driver, and output path.\n\n")
        f.write("| Label | Command | Template |\n")
        f.write("|-------|---------|----------|\n")
        for label in labels:
            row = next(r for r in rows if r["label"] == label)
            f.write(f"| {label} | C++ object | `{row.get('cpp_compile_template', 'unknown')}` |\n")
            f.write(f"| {label} | C object | `{row.get('c_compile_template', 'unknown')}` |\n")
            f.write(f"| {label} | C++ assembly | `{row.get('cpp_asm_template', 'unknown')}` |\n")
            f.write(f"| {label} | C assembly | `{row.get('c_asm_template', 'unknown')}` |\n")
            f.write(f"| {label} | C++ nostdlib++ link | `{row.get('cpp_link_template', 'unknown')}` |\n")
            f.write(f"| {label} | C link | `{row.get('c_link_template', 'unknown')}` |\n")
        f.write("\n")
        f.write("## Facility Overview\n\n")
        f.write("Columns:\n\n")
        f.write("- `Facility`: the tested STL header facility.\n")
        f.write("- `nostdlib++`: ok only when both clang and GCC link the C++ case with `-nostdlib++` at `-O2`.\n")
        f.write("- `C parity`: ok only when both compilers' C++ runtime result matches the C baseline at `n=7`.\n")
        f.write("- `gcc/clang`: ok only when both previous checks pass on both compilers.\n\n")
        o2_rows = [r for r in rows if r["opt"] == "O2" and r["facility"] != "combined"]
        facilities = sorted(set(r["case"] for r in o2_rows))
        overview_by_facility = {
            facility: {
                r["label"]: r
                for r in o2_rows
                if r["case"] == facility
            }
            for facility in facilities
        }
        f.write("| Facility | nostdlib++ | C parity | gcc/clang |\n")
        f.write("|----------|------------|----------|-----------|\n")
        for facility in facilities:
            combined_overview_report_row(f, facility, overview_by_facility[facility], labels)
        f.write("\n")
        f.write("All listed facilities have a handwritten C equivalent in this harness. Header-level `.combined` rows are synthesized from these facilities for assembly summaries and are not separate compile-time facility measurements.\n\n")
        f.write("## Facility Assembly Generation\n\n")
        f.write("Columns:\n\n")
        f.write("- `Facility`: either a synthesized header-level `.combined` aggregate or an indented facility row explaining a non-precise result.\n")
        f.write("- `O2 compile C++ / C`: median C++ compile time, median matched C compile time, and their ratio; `.combined` rows aggregate the included facility compile times.\n")
        f.write("- `O2 text`: the C++ `.text` byte size divided by the matched C `.text` byte size.\n")
        f.write("- `O2 instructions`: the counted C++ assembly instruction total divided by the matched C total.\n")
        f.write("- `Verdict`: classifies the worse of the text and instruction ratios.\n\n")
        for label in labels:
            f.write(f"### {label}\n\n| Facility | O2 compile C++ / C | O2 text | O2 instructions | Verdict |\n|----------|--------------------|---------|-----------------|---------|\n")
            for name, r, indent in report_entries(label, rows, summaries):
                report_row(f, name, r, indent=indent)
            f.write("\n")
        f.write("## Facility Compile Time\n\n")
        f.write("Columns:\n\n")
        f.write("- `Facility`: the tested facility row.\n")
        f.write("- `O2 compile C++ / C`: the median C++ compile time, median matched C compile time, and their ratio for that compiler.\n\n")
        for label in labels:
            entries = sorted(
                [
                    r for r in rows
                    if r["label"] == label
                    and r["opt"] == "O2"
                    and r["facility"] != "combined"
                ],
                key=lambda row: as_float(row["cpp_compile_s"]) or -1.0,
                reverse=True,
            )
            f.write(f"### {label}\n\n")
            compile_time_stats_row(f, label, entries)
            f.write("| Facility | O2 compile C++ / C |\n|----------|--------------------|\n")
            for r in entries:
                compile_time_report_row(f, r)
            f.write("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cxx", default=os.environ.get("CXX", "clang++"))
    parser.add_argument("--cc", default=os.environ.get("CC", "clang"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--keep-build", action="store_true")
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    if not shutil.which(args.cxx):
        raise SystemExit(f"missing C++ compiler: {args.cxx}")
    if not shutil.which(args.cc):
        raise SystemExit(f"missing C compiler: {args.cc}")

    if BUILD.exists() and not args.keep_build:
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True, exist_ok=True)
    if SRC_GEN.exists():
        shutil.rmtree(SRC_GEN)
    SRC_GEN.mkdir(parents=True, exist_ok=True)

    kind = compiler_kind(args.cxx)
    label = args.label or kind
    c99_flags = CLANG_C99 if kind == "clang" else GCC_C99
    opt_levels = ["O0", "O2"]
    cxx_version = command_version(args.cxx)
    cc_version = command_version(args.cc)
    run_os_version = os_version()
    run_cpu_model = cpu_model()
    cxx_flags = " ".join(["-std=c++23", *CFLAT_COMMON, *c99_flags])
    cxx_link_flags = " ".join(LINK_FLAGS)
    c_flags = " ".join(C_COMMON)
    cpp_compile_template = shell_join([args.cxx, "-std=c++23", "{opt}", *CFLAT_COMMON, *c99_flags, "-c", "{source.cpp}", "-o", "{output.o}"])
    c_compile_template = shell_join([args.cc, *C_COMMON, "{opt}", "-c", "{source.c}", "-o", "{output.o}"])
    cpp_asm_template = shell_join([args.cxx, "-std=c++23", "{opt}", *CFLAT_COMMON, *c99_flags, "-S", "{source.cpp}", "-o", "{output.s}"])
    c_asm_template = shell_join([args.cc, *C_COMMON, "{opt}", "-S", "{source.c}", "-o", "{output.s}"])
    cpp_link_template = shell_join([args.cxx, "-std=c++23", "{opt}", *CFLAT_COMMON, *c99_flags, "{source.cpp}", "{driver.cpp}", *LINK_FLAGS, "-o", "{output.exe}"])
    c_link_template = shell_join([args.cc, *C_COMMON, "{opt}", "{source.c}", "{driver.c}", "-o", "{output.exe}"])
    rows = []

    for case in CASES:
        cpp, c, cpp_driver, c_driver = write_case_sources(case)
        for opt in opt_levels:
            common_cpp = [args.cxx, "-std=c++23", f"-{opt}", *CFLAT_COMMON, *c99_flags]
            common_c = [args.cc, *C_COMMON, f"-{opt}"]

            cpp_o = BUILD / f"{case['name']}.{opt}.cpp.o"
            c_o = BUILD / f"{case['name']}.{opt}.c.o"
            cpp_s = BUILD / f"{case['name']}.{opt}.cpp.s"
            c_s = BUILD / f"{case['name']}.{opt}.c.s"
            cpp_exe = BUILD / f"{case['name']}.{opt}.cpp.exe"
            c_exe = BUILD / f"{case['name']}.{opt}.c.exe"

            cpp_compile = [*common_cpp, "-c", str(cpp), "-o", str(cpp_o)]
            c_compile = [*common_c, "-c", str(c), "-o", str(c_o)]
            cpp_asm = [*common_cpp, "-S", str(cpp), "-o", str(cpp_s)]
            c_asm = [*common_c, "-S", str(c), "-o", str(c_s)]
            cpp_link = [*common_cpp, str(cpp), str(cpp_driver), *LINK_FLAGS, "-o", str(cpp_exe)]
            c_link = [*common_c, str(c), str(c_driver), "-o", str(c_exe)]

            c_rc, c_time, _, c_err = median_time(c_compile, args.repeats)
            cpp_rc, cpp_time, _, cpp_err = median_time(cpp_compile, args.repeats)
            asm_cpp_rc, _, _, asm_cpp_err = run_cmd(cpp_asm)
            asm_c_rc, _, _, asm_c_err = run_cmd(c_asm)
            link_rc, _, _, link_err = run_cmd(cpp_link)
            c_link_rc, _, _, c_link_err = run_cmd(c_link)
            cpp_run_rc = c_run_rc = None
            if link_rc == 0:
                cpp_run_rc, _, _, _ = run_cmd([str(cpp_exe)])
            if c_link_rc == 0:
                c_run_rc, _, _, _ = run_cmd([str(c_exe)])
            runtime_match = cpp_run_rc is not None and c_run_rc is not None and cpp_run_rc == c_run_rc

            cpp_text = text_size(cpp_o) if cpp_rc == 0 else None
            c_text = text_size(c_o) if c_rc == 0 else None
            cpp_insn = instruction_count(cpp_s) if asm_cpp_rc == 0 else None
            c_insn = instruction_count(c_s) if asm_c_rc == 0 else None

            rows.append({
                "label": label,
                "cxx_version": cxx_version,
                "cc_version": cc_version,
                "os_version": run_os_version,
                "cpu_model": run_cpu_model,
                "cxx_flags": cxx_flags,
                "cxx_link_flags": cxx_link_flags,
                "c_flags": c_flags,
                "cpp_compile_template": cpp_compile_template,
                "c_compile_template": c_compile_template,
                "cpp_asm_template": cpp_asm_template,
                "c_asm_template": c_asm_template,
                "cpp_link_template": cpp_link_template,
                "c_link_template": c_link_template,
                "case": case["name"],
                "header_name": case.get("header_name", case["name"].split(".")[0]),
                "facility": case.get("facility", "combined"),
                "operations": case.get("operations", "combined representative operations"),
                "header": case["header"],
                "opt": opt,
                "cpp_compile_s": cpp_time,
                "c_compile_s": c_time,
                "compile_ratio": ratio(cpp_time, c_time),
                "cpp_text": cpp_text,
                "c_text": c_text,
                "text_ratio": ratio(cpp_text, c_text),
                "cpp_insn": cpp_insn,
                "c_insn": c_insn,
                "insn_ratio": ratio(cpp_insn, c_insn),
                "link_ok": link_rc == 0,
                "runtime_match": runtime_match,
                "status": "ok" if all(rc == 0 for rc in [c_rc, cpp_rc, asm_cpp_rc, asm_c_rc, link_rc, c_link_rc]) and runtime_match else ("link-fail" if link_rc != 0 else "fail"),
                "error": (" ".join(x.strip().splitlines()[-1] for x in [c_err, cpp_err, asm_cpp_err, asm_c_err, link_err, c_link_err] if x.strip()) or (f"runtime C++ exit {cpp_run_rc}, C exit {c_run_rc}" if not runtime_match else ""))[:500],
            })
            rows[-1]["verdict"] = verdict(rows[-1])

    csv_path = BUILD / f"results.{label}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = BUILD / f"results.{label}.md"
    with md_path.open("w") as f:
        f.write("# STL header-only benchmark results\n\n")
        f.write(f"CXX: `{args.cxx}`  \n")
        f.write(f"CXX version: `{cxx_version}`  \n")
        f.write(f"CC: `{args.cc}`  \n")
        f.write(f"CC version: `{cc_version}`  \n")
        f.write(f"OS: `{run_os_version}`  \n")
        f.write(f"CPU: `{run_cpu_model}`  \n")
        f.write(f"CXXFLAGS: `{cxx_flags}`  \n")
        f.write(f"CXX link flags: `{cxx_link_flags}`  \n")
        f.write(f"CFLAGS: `{c_flags}`  \n")
        f.write(f"Repeats: `{args.repeats}` median compile time  \n\n")
        f.write("## Command Templates\n\n")
        f.write("Commands are shown with placeholders for the optimization level, generated source, generated driver, and output path.\n\n")
        f.write(f"- C++ object: `{cpp_compile_template}`\n")
        f.write(f"- C object: `{c_compile_template}`\n")
        f.write(f"- C++ assembly: `{cpp_asm_template}`\n")
        f.write(f"- C assembly: `{c_asm_template}`\n")
        f.write(f"- C++ nostdlib++ link: `{cpp_link_template}`\n")
        f.write(f"- C link: `{c_link_template}`\n\n")
        f.write("| Case | Header | Facility | Opt | Link | Runtime | C++ compile | C compile | Compile | C++ text | C text | Text | C++ insn | C insn | Insn | Verdict |\n")
        f.write("|------|--------|----------|-----|------|---------|-------------|-----------|---------|----------|--------|------|----------|--------|------|---------|\n")
        for row in rows:
            f.write(
                f"| {row['case']} | `{row['header']}` | {row.get('facility', '')} | {row['opt']} | "
                f"{'ok' if row['link_ok'] else 'fail'} | {'ok' if row.get('runtime_match') else 'fail'} | "
                f"{fmt_seconds(row['cpp_compile_s'])} | {fmt_seconds(row['c_compile_s'])} | {fmt_ratio(row['compile_ratio'])} | "
                f"{fmt_value(row['cpp_text'])} | {fmt_value(row['c_text'])} | {fmt_ratio(row['text_ratio'])} | "
                f"{fmt_value(row['cpp_insn'])} | {fmt_value(row['c_insn'])} | {fmt_ratio(row['insn_ratio'])} | {row.get('verdict', '')} |\n"
            )
        failures = [row for row in rows if row["status"] != "ok"]
        if failures:
            f.write("\n## Failures\n\n")
            for row in failures:
                f.write(f"- `{row['case']}` `{row['opt']}`: {row['error']}\n")

    print(f"Wrote {csv_path}")
    write_final_report()
    print(f"Wrote {md_path}")
    print(f"Wrote {ROOT / 'STL_HEADER_ONLY_RESULTS.md'}")


if __name__ == "__main__":
    main()
