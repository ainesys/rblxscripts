from lupa import LuaRuntime


def runtime():
    lua = LuaRuntime(encoding=None)
    lua.execute(b"""
bit32={}
function bit32.band(a,b,...) local v=(a & b) & 0xffffffff;if select('#',...)>0 then return bit32.band(v,...) end;return v end
function bit32.bxor(a,b,...) local v=(a ~ b) & 0xffffffff;if select('#',...)>0 then return bit32.bxor(v,...) end;return v end
function bit32.bor(a,b) return (a | b) & 0xffffffff end
function bit32.bnot(a) return (~a) & 0xffffffff end
function bit32.rshift(a,n) return (a & 0xffffffff) >> n end
function bit32.rrotate(a,n) return ((a >> n) | (a << (32-n))) & 0xffffffff end
function bit32.lrotate(a,n) return ((a << n) | (a >> (32-n))) & 0xffffffff end
table.clear=function(t) for k in pairs(t) do t[k]=nil end end
buffer={}
function buffer.create(n) return {size=n,words={}} end
function buffer.fromstring(s)
 local b=buffer.create(#s)
 for i=1,#s,4 do b.words[(i-1)//4]=string.unpack('<I4',s,i) end
 return b
end
function buffer.readu32(b,offset) assert(offset>=0 and offset+4<=b.size and offset%4==0);return b.words[offset//4] or 0 end
function buffer.writeu32(b,offset,v) assert(offset>=0 and offset+4<=b.size and offset%4==0);b.words[offset//4]=v end
function buffer.tostring(b)
 local out={}
 for i=0,b.size-1,4 do out[#out+1]=string.pack('<I4',buffer.readu32(b,i)) end
 return table.concat(out)
end
function buffer.fill(b,offset,value) assert(offset==0 and value==0);table.clear(b.words) end
AineRuntime={}
""")
    return lua
