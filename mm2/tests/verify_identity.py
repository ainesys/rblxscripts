from pathlib import Path
import hashlib
import time
from luaparser import ast
from crypto_runtime import runtime

source = (Path(__file__).resolve().parents[1] / "updYarhm.txt").read_text(encoding="utf-8")
start = source.index("-- scrypt (RFC 7914)")
end = source.index("do\n\tlocal salt =", start)
code = source[start:end]
ast.parse(code)
lua = runtime()
lua.execute(code.encode())
scrypt = lua.globals().AineRuntime.scrypt
vectors = [
    (b"", b"", 16, 1, 1, 64),
    (b"candidate:test", bytes(range(16)), 32, 2, 2, 32),
    (b"pleaseletmein", b"SodiumChloride", 16384, 8, 1, 32),
]
for password, salt, n, r, p, length in vectors:
    expected = hashlib.scrypt(password, salt=salt, n=n, r=r, p=p, dklen=length, maxmem=128*1024*1024)
    started = time.perf_counter()
    result = scrypt(password, salt, n, r, p, length)
    assert result == expected, (n, r, p)
    if n == 16:
        assert result.hex() == (
            "77d6576238657b203b19ca42c18a0497"
            "f16b4844e3074ae8dfdffa3fede21442"
            "fcd0069ded0948f8326a753a0fc81f17"
            "e8d3e0fb2e0d3628cf35e20c38d18906"
        )

    print(f"PASS: scrypt N={n}, r={r}, p={p}, length={length} matches OpenSSL ({time.perf_counter()-started:.3f}s on host Lua; not an Android benchmark).", flush=True)
print("PASS: RFC empty-password vector and independent multi-lane/full-cost vectors.", flush=True)
