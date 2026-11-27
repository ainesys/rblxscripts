from pathlib import Path
from crypto_runtime import runtime
from luaparser import ast

source = (Path(__file__).resolve().parents[1] / "updYarhm.txt").read_text(encoding="utf-8")
start = source.index("do\n\tlocal salt =")
end = source.index("do\n\tlocal sessionWhitelist", start)
code = source[start:end]
ast.parse(code)
# Only in this test: substitute a public test record and fake the costly primitive.
code = code.replace(source[source.index("local verifier =", start):source.index("\n", source.index("local verifier =", start))], 'local verifier = string.rep("V",32)')
lua = runtime()
lua.execute(b"""
local players={}
game={GetService=function() return players end}
local now=0
local calls=0
local jobs={}
local fail=false
local unavailable=false
NativeTask={wait=function() coroutine.yield('frame') end}
local nativeClock=os.clock
os.clock=function() now=now+0.01;return now end
local function candidate(name,id) return {Name=name,UserId=id,Parent=players} end
local other=candidate('Other',11)
local owner=candidate('Owner',20)
AineRuntime.scrypt=function(key,salt,n,r,p,length,checkpoint)
 calls=calls+1
 assert(n==16384 and r==8 and p==1 and length==32 and #salt==16)
 checkpoint()
 if fail then error('allocation error') end
 if unavailable then error('missing buffer') end
 return key=='owner:20' and string.rep('V',32) or string.rep('N',32)
end
warn=function() end
"""+code.encode()+b"""
assert(AineRuntime.isProtectedPlayer(other))
assert(AineRuntime.isProtectedPlayer(owner))
assert(AineRuntime.protectedPlayer()==nil and calls==0)
AineRuntime.spawn=function(fn) jobs[#jobs+1]=coroutine.create(fn) end
AineRuntime.startIdentityChecks()
assert(#jobs==1)
assert(AineRuntime.isProtectedPlayer(owner) and #jobs==1)
while coroutine.status(jobs[1])~='dead' do assert(coroutine.resume(jobs[1])) end
assert(calls==2 and AineRuntime.identityStatus.state=='ready')
assert(not AineRuntime.isProtectedPlayer(other))
assert(AineRuntime.isProtectedPlayer(owner) and AineRuntime.protectedPlayer()==owner)
assert(AineRuntime.identityStatus.checked==2)
AineRuntime.clearProtectedPlayer(owner);owner.Parent=nil
assert(AineRuntime.protectedPlayer()==nil)
local rejoined=candidate('OWNER',20)
assert(AineRuntime.isProtectedPlayer(rejoined) and calls==2 and AineRuntime.protectedPlayer()==rejoined)
local pending=candidate('Pending',30)
fail=true;assert(AineRuntime.isProtectedPlayer(pending))
local job=jobs[#jobs]
while coroutine.status(job)~='dead' do assert(coroutine.resume(job)) end
assert(AineRuntime.identityStatus.state=='error')
assert(AineRuntime.protectedPlayer()==rejoined)
AineRuntime.closed=true
assert(AineRuntime.isProtectedPlayer(pending))
assert(AineRuntime.protectedPlayer()==rejoined)
os.clock=nativeClock
""")
assert "local sealed" not in source and "local marker" not in source
assert source.count("AineRuntime.scrypt,key,salt,16384,8,1,32,checkpoint") == 1
print("PASS: serial async queue, frame yielding, no authority while pending, fail-safe errors, one derivation per identity, cached rejoin, owner clearing, and removal of fast record.")
