from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast
root=Path(__file__).resolve().parents[2]
s=(root/'mm2/updYarhm.txt').read_text(encoding='utf-8')
a=s.index('function AineRuntime.attachPrivateCommands');b=s.index('function AineRuntime.clone',a);code=s[a:b];ast.parse(code)
r=LuaRuntime();r.execute('''
local handlers={}
local lp={UserId=10};local owner={UserId=20}
local players={LocalPlayer=lp};owner.Parent=players
local signal={Connect=function(self,fn) self.fn=fn end}
game={GetService=function(_,name) if name=='Players' then return players else return {MessageReceived=signal} end end}
AineRuntime={protectedPlayer=function() return owner end,connect=function(signal,fn) signal:Connect(fn) end,onClose=function() end}
AineRuntime.spawn=function(fn) fn() end
'''+code+'''
local calls={}
for _,key in ipairs({'ka','gun','fling','tp','wl','f','farm','lobby','hide'}) do handlers[key]=function(arg) calls[#calls+1]={key,arg} end end
local c=AineRuntime.attachPrivateCommands(handlers)
assert(not c.receive(99,'ka','RBXWhisper:10_20'))
assert(not c.receive(20,'ka','RBXGeneral'))
assert(not c.receive(20,'ka','RBXWhisper:20_30'))
assert(c.receive(20,' KA ','RBXWhisper:20_10','1'))
assert(not c.receive(20,'ka','RBXWhisper:20_10','1'))
assert(c.receive(20,'gun -k','RBXWhisper:10_20','2'))
assert(c.receive(20,'fling abc','RBXWhisper:10_20','3'))
assert(c.receive(20,'fling -m','RBXWhisper:10_20','4'))
assert(c.receive(20,'fling -s','RBXWhisper:10_20','5'))
assert(c.receive(20,'tp lobby','RBXWhisper:10_20','6'))
assert(c.receive(20,'gun','RBXWhisper:10_20','7'))
assert(#calls==7 and calls[2][1]=='gun' and calls[2][2]=='-k')
assert(c.receive(20,'gun -','RBXWhisper:10_20','alias-gun'))
assert(calls[8][1]=='gun' and calls[8][2]=='-k')
assert(c.receive(20,'..','RBXWhisper:10_20','alias-repeat'))
assert(calls[9][1]=='gun' and calls[9][2]=='-k')
assert(c.receive(20,'tp anywhere','RBXWhisper:10_20','8'))
assert(not c.receive(20,'ka extra','RBXWhisper:10_20','9'))
owner.Parent=nil;assert(not c.receive(20,'ka','RBXWhisper:10_20','10'))
''')
print('PASS: only cached owner whispering to local account can issue commands; all requested forms dispatch, public/third-party/duplicate/malformed messages rejected.')

a=s.index("\t\tlocal function resolveCommandTarget")
b=s.index("\t\tlocal function commandFling",a)
resolver=s[a:b]
ast.parse(resolver)
r=LuaRuntime()
r.execute("""
local lp={Name='Alt'}
local alpha={Name='AlphaUser',DisplayName='Alpha'}
local beta={Name='BetaUser',DisplayName='Beta'}
local owner={Name='Owner',DisplayName='Owner'}
game={Players={LocalPlayer=lp,GetPlayers=function() return {lp,alpha,beta,owner} end}}
AineRuntime={isProtectedPlayer=function(p) return p==owner end}
local function findRole(tool) return tool=='Knife' and alpha or beta end
"""+resolver+"""
assert(resolveCommandTarget('alph')==alpha)
assert(resolveCommandTarget('@betauser')==beta)
assert(resolveCommandTarget('-m')==alpha and resolveCommandTarget('-s')==beta)
assert(not pcall(resolveCommandTarget,'owner'))
beta.DisplayName='Alpha Two'
assert(not pcall(resolveCommandTarget,'alph'))
""")
a=s.index("getgenv().YARHM_passRecipientStatus = function")
b=s.index("getgenv().YARHM_isAliveInRound",a)
status=s[a:b]
ast.parse(status)
r=LuaRuntime()
r.execute("""
local env={};function getgenv() return env end
local old,new={},{}
local player={Name='Recipient',Character=new}
local playerData={Recipient={Dead=true,Role='Innocent'}}
local playerDataCharacters={Recipient=old}
local inactiveRoles={lobby=true}
"""+status+"""
assert(env.YARHM_passRecipientStatus(player)==nil)
player.Character=old;assert(env.YARHM_passRecipientStatus(player)=='dead')
playerData.Recipient={Role='Murderer'};assert(env.YARHM_passRecipientStatus(player)=='murderer')
""")
print('PASS: unique partial usernames and role flags resolve, ambiguity and protected targets reject; role data from previous characters ignored while current death/murderer data retained.')

r=LuaRuntime()
r.execute("AineRuntime={connect=function(signal,fn) signal:Connect(fn) end,onClose=function() end,spawn=function(fn) fn() end}")
r.execute(code)
r.execute("""
-- Reuse the authenticated parser with the additional command forms.
local lp={UserId=10};local owner={UserId=20};local players={LocalPlayer=lp};owner.Parent=players
local signal={Connect=function() end}
game={GetService=function(_,n) return n=='Players' and players or {MessageReceived=signal} end}
AineRuntime.protectedPlayer=function() return owner end
local seen={}
local handlers={}
for _,key in ipairs({'wl','f','farm','lobby','hide'}) do handlers[key]=function(arg) seen[#seen+1]={key,arg} end end
local c=AineRuntime.attachPrivateCommands(handlers)
for i,text in ipairs({'wl abc','f -inno','farm','farm -k','lobby','hide','hide gun'}) do
 assert(c.receive(20,text,'RBXWhisper:10_20',tostring(i)))
end
assert(#seen==7 and seen[1][1]=='wl' and seen[7][2]=='gun')
""")
a=s.index('do\n\tlocal sessionWhitelist');b=s.index('function AineRuntime.remember',a)
whitelist=s[a:b];ast.parse(whitelist)
r=LuaRuntime();r.execute("AineRuntime={isProtectedPlayer=function(p) return p.owner==true end}")
r.execute(whitelist)
r.execute("extra={UserId=44};AineRuntime.whitelistPlayer(extra);assert(AineRuntime.isProtectedPlayer(extra));assert(AineRuntime.isProtectedPlayer({UserId=99,owner=true}))")
r.execute("AineRuntime={isProtectedPlayer=function(p) return p.owner==true end}")
r.execute(whitelist);r.execute("assert(not AineRuntime.isProtectedPlayer(extra))")
a=s.index('\t\tlocal function hideWithGun()');b=s.index('\t\tAineRuntime.attachPrivateCommands({',a)
hide=s[a:b];ast.parse(hide)
r=LuaRuntime();r.execute("""
local clock=0
local hum={Health=100}
local hasGun=false
local character={FindFirstChildOfClass=function() return hum end,FindFirstChild=function() return hasGun end}
local lp={Character=character,FindFirstChildOfClass=function() end}
game={Players={LocalPlayer=lp}}
local autoGrab,autoGrabBusy,flingBusy,teleportShotBusy=false,false,false,false
local farmCombat={busy=false}
local farmEnabled=false
local function tick() return clock end
local function updateAutoGunButton() end
local order={}
local function onGrabGunClick() order[#order+1]='pickup';hasGun=true end
local function teleportToSpawns() order[#order+1]='lobby';return true end
local drops=true
workspace={FindFirstChild=function() return drops end}
AineRuntime={closed=false}
local task={wait=function(dt) clock=clock+dt;if dt==1 then assert(hum.Health==100);order[#order+1]='wait1' end end}
"""+hide+"""
hideWithGun();assert(hum.Health==0 and not autoGrab and order[1]=='pickup' and order[2]=='lobby' and order[3]=='wait1')
hum.Health=100;hasGun=false;drops=false;order={}
hideWithGun();assert(hum.Health==100 and #order==0 and not autoGrab)
""")
print('PASS: extra commands authenticated; whitelist resets with new runtime; hide gun picks up before lobby, waits one second alive then resets, and never resets without a gun.')

r=LuaRuntime()
r.execute("""
local lp={UserId=10};local owner={UserId=20};local players={LocalPlayer=lp};owner.Parent=players
local signal={Connect=function() end}
game={GetService=function(_,n) return n=='Players' and players or {MessageReceived=signal} end}
AineRuntime={connect=function(signal,fn) signal:Connect(fn) end,onClose=function() end,spawn=function(fn) fn() end,protectedPlayer=function() return owner end}
"""+code+"""
local calls={}
local handlers={}
for _,key in ipairs({'tp','fling','pass','f'}) do handlers[key]=function(arg,channel) calls[#calls+1]={key,arg,channel} end end
local c=AineRuntime.attachPrivateCommands(handlers)
assert(not c.receive(20,'..','RBXWhisper:10_20','zero'))
for i,text in ipairs({'tp set','tp','tp someone','tp -s','tp -m','tp -d','f bob','pass alice','p alice','..','f -inno'}) do
 assert(c.receive(20,text,'RBXWhisper:10_20',tostring(i)))
end
assert(calls[1][1]=='tp' and calls[1][2]=='set')
assert(calls[2][2]=='' and calls[6][2]=='-d')
assert(calls[7][1]=='fling' and calls[7][2]=='bob')
assert(calls[8][1]=='pass' and calls[9][1]=='pass' and calls[10][1]=='pass')
assert(calls[10][2]=='alice' and calls[10][3]=='RBXWhisper:10_20' and calls[11][1]=='f')
assert(c.receive(20,'fl bob','RBXWhisper:10_20','fl-name'))
assert(calls[12][1]=='fling' and calls[12][2]=='bob')
assert(c.receive(20,'fl -m','RBXWhisper:10_20','fl-murd'))
assert(calls[13][1]=='fling' and calls[13][2]=='-m')
assert(c.receive(20,'fl -s','RBXWhisper:10_20','fl-sheriff'))
assert(calls[14][1]=='fling' and calls[14][2]=='-s')
assert(c.receive(20,'fl -inno','RBXWhisper:10_20','fl-inno'))
assert(calls[15][1]=='f' and calls[15][2]=='-inno')
assert(c.receive(20,'..','RBXWhisper:10_20','fl-repeat'))
assert(calls[16][1]=='f' and calls[16][2]=='-inno')

assert(not c.receive(99,'..','RBXWhisper:10_20','bad'))
""")
print('PASS: repeat requires prior authorized command; saved/player/role/reply teleport forms dispatch; f and p aliases preserve arguments and whisper channel; f -inno retained.')

a=s.index('\t\tlocal savedTeleport');b=s.index('\t\tAineRuntime.attachPrivateCommands({',a)
teleport=s[a:b];ast.parse(teleport)
r=LuaRuntime()
r.execute((root/'search for needle/tests/mock.lua').read_text(encoding='utf-8'))
r.execute("""
local players=services.Players;game.Players=players
p.UserId=10
AineRuntime={protectedPlayer=function() return {UserId=20} end}
local moves=0
function char:GetPivot() return root.CFrame end
function char:PivotTo(frame) moves=moves+1;root.CFrame=frame end
local cm=getmetatable(C())
cm.__index=function(a,k) if k=='ToObjectSpace' then return function(self,other) return C(other.Position-self.Position) end end end
root.CFrame=C(11,22,33)
local targetRoot={CFrame=C(40,50,60)}
local target={Character={FindFirstChild=function() return targetRoot end}}
local function resolveCommandTarget(arg,allow) assert(allow);return target end
local lastReply
local channel={SendAsync=function(_,text) lastReply=text end}
services.TextChatService={FindFirstChild=function() return {FindFirstChild=function(_,name) assert(name=='RBXWhisper:10_20');return channel end} end}
local function teleportToSpawns() moves=moves+1 end
local function getNotify() return function() end end
local flingBusy,autoGrabBusy,teleportShotBusy,farmEnabled=false,false,false,false
local farmCombat={busy=false}
local function setFarmEnabled() end
local function releaseFarm() end
local flyUtility={IsFlying=function() return false end}
local function updateFlySwitch() end
local function tick() return 0 end
local farmPauseUntil=0
"""+teleport+"""
assert(not pcall(teleportCommand,'','Private'))
teleportCommand('set','Private')
root.CFrame=C(0,0,0);teleportCommand('','Private');assert(root.Position.X==11 and root.Position.Y==22)
teleportCommand('-d','Private');assert(lastReply=='Saved coordinates: 11.000, 22.000, 33.000')
teleportCommand('someone','Private');assert(root.Position.X==40 and root.Position.Z==63)
assert(moves==2)
local protectedRoot={CFrame=C(70,80,90)}
local owner={UserId=20,Parent=players,Character={FindFirstChild=function() return protectedRoot end}}
AineRuntime.protectedPlayer=function() return owner end
teleportCommand('@s','Private');assert(root.Position.X==70 and root.Position.Z==93 and moves==3)
owner.Parent=nil;assert(not pcall(teleportCommand,'@s','Private'));assert(moves==3)
AineRuntime.protectedPlayer=function() return nil end
assert(not pcall(teleportCommand,'@s','Private'));assert(moves==3)

""")
print('PASS: tp set saves position, bare tp restores it, tp -d sends coordinates only to the supplied private channel, and player teleport moves beside target.')

r=LuaRuntime()
r.execute("""
table.clear=function(t) for k in pairs(t) do t[k]=nil end end
local lp={UserId=10};local owner={UserId=20};local admin={UserId=30,Name='Admin'}
local players={LocalPlayer=lp};owner.Parent=players
local signal={Connect=function() end}
game={GetService=function(_,n) return n=='Players' and players or {MessageReceived=signal} end}
local cleanup
AineRuntime={connect=function(signal,fn) signal:Connect(fn) end,onClose=function(fn) cleanup=fn end,spawn=function(fn) fn() end,protectedPlayer=function() return owner end}
"""+code+"""
local calls={}
local c=AineRuntime.attachPrivateCommands({
 ka=function() calls[#calls+1]='ka' end,
 gun=function() calls[#calls+1]='gun' end,
 resolveAdmin=function(arg) assert(arg=='adm');return admin end,
})
assert(not c.receive(20,'ka','RBXGeneral','pub0'))
assert(not c.receive(99,'pub','RBXGeneral','pub1'))
assert(c.receive(20,'pub','RBXGeneral','pub2') and c.public)
assert(c.receive(20,'pub','RBXWhisper:10_20','pub3') and not c.public)
assert(not c.receive(20,'pub extra','RBXGeneral','pub4'))
assert(not c.receive(20,'admin -a','RBXGeneral','pub5'))
assert(not c.receive(30,'ka','RBXWhisper:10_30','1'))
assert(c.receive(20,'admin adm','RBXWhisper:10_20','2'))
assert(c.receive(30,'ka','RBXWhisper:10_30','3'))
assert(not c.receive(30,'pub','RBXGeneral','pub6'))
assert(not c.receive(30,'pub','RBXWhisper:10_30','4'))
assert(not c.receive(30,'admin -a','RBXWhisper:10_30','5'))
assert(not c.receive(30,'unadmin adm','RBXWhisper:10_30','6'))
assert(not c.receive(30,'ka','RBXGeneral','7'))
assert(c.receive(20,'pub','RBXWhisper:10_20','8'))
assert(c.receive(30,'ka','RBXGeneral','9'))
assert(not c.receive(99,'ka','RBXGeneral','10'))
assert(c.receive(20,'admin -all','RBXGeneral','11'))
assert(c.receive(99,'gun','RBXGeneral','12'))
assert(c.receive(99,'..','RBXGeneral','13'))
assert(calls[#calls]=='gun')
assert(not c.receive(98,'..','RBXGeneral','14'))
assert(not c.receive(99,'unadmin -a','RBXGeneral','15'))
assert(c.receive(20,'unadmin adm','RBXGeneral','16'))
assert(not c.receive(30,'ka','RBXGeneral','17'))
assert(c.receive(20,'admin adm','RBXGeneral','18'))
assert(c.receive(30,'ka','RBXGeneral','19'))
assert(c.receive(20,'unadmin -a','RBXGeneral','20'))
assert(not c.receive(99,'ka','RBXGeneral','21'))
assert(not c.receive(30,'ka','RBXWhisper:10_30','22'))
assert(c.receive(20,'pub','RBXGeneral','23'))
assert(not c.receive(20,'ka','RBXGeneral','24'))
assert(c.receive(20,'ka','RBXWhisper:10_20','25'))
c.busy=true
assert(c.receive(20,'admin -a','RBXWhisper:10_20','26'))
assert(c.receive(20,'unadmin -all','RBXWhisper:10_20','27'))
c.busy=false
cleanup();assert(not c.public and not c.all and next(c.admins)==nil and next(c.history)==nil)
local fresh=AineRuntime.attachPrivateCommands({})
assert(not fresh.public and not fresh.all and next(fresh.admins)==nil)
""")
print('PASS: owner-only pub/admin/unadmin; public transport still requires permission; all-admin and individual denial/regrant; revocation during busy action; per-sender repeat isolation; defaults and cleanup reset.')
