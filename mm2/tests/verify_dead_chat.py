from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

root = Path(__file__).resolve().parents[2]
source = (root / "mm2/updYarhm.txt").read_text(encoding="utf-8")
start = source.index("function AineRuntime.attachDeadChat()")
code = source[start:source.index("function AineRuntime.clone", start)]
ast.parse(code)
lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
lua.execute(r'''
services.TextChatService=O('Folder','TextChatService')
services.TextChatService.MessageReceived=sig()
local channels=O('Folder','TextChannels',services.TextChatService)
general=O('TextChannel','RBXGeneral',channels)
local players=services.Players
speaker=O('Player','Other');speaker.UserId=2
function players:GetPlayerByUserId(id) if id==2 then return speaker end end
function players:FindFirstChild(name) if name=='Other' then return speaker end end
local env={YARHM_isDeadInRound=function(who) return who==speaker end}
function getgenv() return env end
local close
AineRuntime={connect=function(signal,fn) return signal:Connect(fn) end,onClose=function(fn) close=fn end}
lines={}
function general:DisplaySystemMessage(text)
 table.insert(lines,text)
 services.TextChatService.MessageReceived:Fire({Text=text,TextChannel=general})
end
legacyFolder=O('Folder','DefaultChatSystemChatEvents',rep)
legacy=O('RemoteEvent','OnMessageDoneFiltering',legacyFolder)
function closeChat() close() end
''')
lua.execute(code)
lua.execute(r'''
local controller=AineRuntime.attachDeadChat()
local dead={Name='Dead'}
services.TextChatService.MessageReceived:Fire({TextSource={UserId=2},Text='hello <b>',TextChannel=dead})
assert(#lines==1 and lines[1]=='[Dead] @Other: hello &lt;b&gt;')
legacy.OnClientEvent:Fire({SpeakerUserId=2,Message='hello <b>',OriginalChannel='Dead',IsFiltered=true})
assert(#lines==1)
legacy.OnClientEvent:Fire({SpeakerUserId=2,Message='not filtered',OriginalChannel='Dead',IsFiltered=false})
assert(#lines==1)
services.TextChatService.MessageReceived:Fire({TextSource={UserId=2},Text='already visible',TextChannel=general})
assert(#lines==1)
controller.enabled=false
legacy.OnClientEvent:Fire({SpeakerUserId=2,Message='disabled',OriginalChannel='Dead'})
assert(#lines==1)
controller.enabled=true
local later=O('RemoteEvent','OnMessageDoneFiltering',legacyFolder)
rep.DescendantAdded:Fire(later)
later.OnClientEvent:Fire({FromSpeaker='Other',Message='new event',OriginalChannel='Dead'})
assert(#lines==2)
closeChat();assert(not controller.enabled and next(controller.seen)==nil)
''')
print("PASS: delivered dead messages mirrored with escaped text; modern/legacy duplicates, unfiltered payloads, system recursion, already visible messages and disabled mode skipped; late legacy event attachment and close cleanup verified.")
