from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

root = Path(__file__).resolve().parents[2]
source = (root / "mm2/updYarhm.txt").read_text(encoding="utf-8")
start = source.index("function AineRuntime.retirePreviousUI")
end = source.index("\n-- scrypt (RFC 7914)", start)
bootstrap = source[start:end]
ast.parse(bootstrap)
assert "forsaken" not in source.lower()
assert "ISODJDY_routine" not in source
assert 'makeQuickButton("JoinUserQuickBtn"' not in source
start = source.index("local function AIIGMH_routine()")
ast.parse(source[start:source.index("local function HVVD_routine()", start)])

lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
lua.execute(r'''
AineRuntime={}
pg.ClassName="PlayerGui"
local env={}
oldClosed=0;shutdownCalled=0
function getgenv() return env end
env.YARHM_runtime={close=function() oldClosed=oldClosed+1 end}
services.CoreGui=O('Folder','CoreGui')
hidden=O('Folder','HiddenGui')
function gethui() return hidden end
legacy=O('ScreenGui','YARHM',services.CoreGui)
O('TextButton','JoinUserQuickBtn',legacy)
playerLegacy=O('ScreenGui','YARHM',pg)
hiddenLegacy=O('ScreenGui','YARHM',hidden)
local shutdown=O('BindableFunction','Shutdown',hiddenLegacy)
shutdown.OnInvoke=function() shutdownCalled=shutdownCalled+1 end
unrelated=O('ScreenGui','OtherUI',services.CoreGui)
renamed=O('ScreenGui','RenamedLegacy',hidden)
env.YARHM=renamed
local robloxGui=O('Folder','RobloxGui',services.CoreGui)
nested=O('ScreenGui','RandomName',robloxGui)
O('ModuleScript','FUNCTIONS',nested);O('Frame','Menu',nested);O('LocalScript','Universal',nested)
''')
lua.execute(bootstrap)
lua.execute(r'''
assert(oldClosed==1 and shutdownCalled==1)
assert(legacy.Parent==nil and playerLegacy.Parent==nil and hiddenLegacy.Parent==nil)
assert(unrelated.Parent==services.CoreGui)
assert(renamed.Parent==nil and nested.Parent==nil)
''')
print("PASS: rerun closes previous runtime and removes old screen UI from CoreGui, hidden GUI, and PlayerGui; unrelated UI survives; Forsaken module/tab removed; menu controller syntax passes.")
