from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

root = Path(__file__).resolve().parents[2]
source = (root / "mm2/updYarhm.txt").read_text(encoding="utf-8")

def section(start, end):
    offset = source.index(start)
    return source[offset:source.index(end, offset)]

landing = section("function AineRuntime.passGunLanding", "function AineRuntime.clone")
control = section("\tlocal passGun =", '\n\tdo\n\t\tlocal function resolveCommandTarget')
join = section("\tdo\n\t\tlocal busy, teleportPending", "\n\tlocal passGun =")
for block in (landing, control, join):
    ast.parse(block)
assert "JoinUserQuickBtn" not in source and "JoinUserPanel" not in source
assert 'Args = {"Join someone by Roblox username", "Join server"' in source

lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
lua.execute(r'''
local cm=getmetatable(C())
cm.__index=function(a,k)
 if k=='LookVector' then return rawget(a,'facing') or V(0,0,-1) end
 if k=='ToObjectSpace' then return function(self,other) return C(other.Position-self.Position) end end
end
CFrame.lookAt=function(position,look) local frame=C(position);frame.facing=(look-position).Unit;return frame end
RaycastParams={new=function() return {} end}
AineRuntime={closed=false}
Vector2={zero=V()}
local contacts, rays={},0
floorMissing, wallBlocked, boxBlocked, firstBlocked=false,false,false,false
function workspace:Raycast(origin,direction,params)
 assert(params.RespectCanCollide and #params.FilterDescendantsInstances==2)
 if direction.Y==-12 then
  if floorMissing then return nil end
  return {Position=V(origin.X,0,origin.Z),Normal=V(0,1,0)}
 end
 rays=rays+1
 if wallBlocked or (frontBlocked and math.abs(direction.Y)<1) or (firstBlocked and rays==1) then return {Instance={}} end
end
function workspace:GetPartBoundsInBox(frame,size,params)
 assert(params.RespectCanCollide and size.X>0 and size.Y>0 and size.Z>0)
 return boxBlocked and {{}} or {}
end
function char:GetBoundingBox() return root.CFrame,V(2,6,2) end
function char:GetPivot() return root.CFrame end
local pivotCount=0
function char:PivotTo(frame) pivotCount=pivotCount+1;root.CFrame=frame end
function countPivots() return pivotCount end
root.Size=V(2,2,2);root.CFrame=C(100,3.2,100);hum.HipHeight=2
recipient=O('Player','Recipient');recipient.allowed=true
recipient.Character=O('Model','RecipientChar',workspace)
targetRoot=O('Part','HumanoidRootPart',recipient.Character);targetRoot.Size=V(2,2,2);targetRoot.CFrame=C(0,3.2,0)
targetHum=O('Humanoid','Humanoid',recipient.Character);targetHum.Health=100
''')
lua.execute(landing)
lua.execute(r'''
local frame=AineRuntime.passGunLanding(char,targetRoot)
assert(frame and frame.Position.Z<0 and frame.Position.Y>=3)
targetRoot.CFrame.facing=V(1,0,0)
frame=AineRuntime.passGunLanding(char,targetRoot);assert(frame.Position.X>0 and frame.Position.Z==0)
frontBlocked=true
frame=AineRuntime.passGunLanding(char,targetRoot);assert(frame and frame.Position.Y>targetRoot.Position.Y and frame.Position.X==targetRoot.Position.X)
frontBlocked=false
wallBlocked=true;assert(not AineRuntime.passGunLanding(char,targetRoot));wallBlocked=false
boxBlocked=true;assert(not AineRuntime.passGunLanding(char,targetRoot));boxBlocked=false
floorMissing=true;assert(not AineRuntime.passGunLanding(char,targetRoot));floorMissing=false
''')
lua.execute(r'''
local players=services.Players
players.children={}
game.Players=players
function players:GetPlayers() return {p,recipient} end
recipient.Parent=players
local backpack=O('Backpack','Backpack',p)
local gun=O('Tool','Gun',char)
function hum:EquipTool(tool) tool.Parent=char end
function AineRuntime.protectedPlayer() if recipient.allowed then return recipient end end
local hooks={}
function AineRuntime.connect(signal,fn) hooks[signal]=fn end
local rs2={Heartbeat={}}
local autoGrabBusy,flingBusy,teleportShotBusy,farmEnabled=false,false,false,false
local farmCombat={busy=false}
local farmRoundEnded=false
local recipientAlive,murderer=true,nil
local env={YARHM_passRecipientStatus=function(player) if player==recipient and not recipientAlive then return "dead" end end}
local function getgenv() return env end
local function findRole() return murderer end
local farmPauseUntil=0
local flyUtility={IsFlying=function() return false end}
local function updateFlySwitch() end
local function releaseFarm() end
local function setFarmEnabled() end
local function getNotify() return function() end end
local function makeQuickButton() return {Destroying={},Visible=false},{Scale=0} end
local function bindSwipe(button,tap,up) button.tap=tap;button.up=up end
local function tick() return 10 end
local afterWait
local lastWait
local task={wait=function(seconds) lastWait=seconds;if afterWait then afterWait() end end}
'''+control+r'''
assert(passGun.target()==recipient)
recipient.allowed=false;passGun.updateVisibility(true);assert(not passGun.button.Visible and passGun.scale.Scale==0)
recipient.allowed=true;passGun.updateVisibility(false);assert(not passGun.button.Visible)
passGun.updateVisibility(true);assert(passGun.button.Visible and passGun.scale.Scale==1)
recipient.Parent=nil;passGun.updateVisibility(true);assert(not passGun.button.Visible)
recipient.Parent=players
local origin=root.CFrame
recipient.allowed=false;passGun.run(false);assert(hum.Health==100 and root.CFrame==origin)
recipient.allowed=true;gun.Parent=backpack;table.insert(backpack.children,gun)
recipientAlive=false;passGun.run(false);assert(hum.Health==100 and root.CFrame==origin)
recipientAlive=true;murderer=recipient;passGun.run(false);assert(hum.Health==100 and root.CFrame==origin)
murderer=nil;local knife=O('Tool','Knife',recipient.Character)
passGun.run(false);assert(hum.Health==100 and root.CFrame==origin);knife.Parent=nil
local targetBag=O('Backpack','Backpack',recipient);knife.Parent=targetBag;table.insert(targetBag.children,knife)
passGun.run(false);assert(hum.Health==100 and root.CFrame==origin);knife.Parent=nil
targetHum.Health=0;passGun.run(false);assert(hum.Health==100 and root.CFrame==origin);targetHum.Health=100

local ready, reason=passGun.recipientReady(recipient);assert(ready and reason==nil)
local status=env.YARHM_passRecipientStatus
env.YARHM_passRecipientStatus=function() return "inactive" end
assert(passGun.recipientReady(recipient))
env.YARHM_passRecipientStatus=nil
assert(passGun.recipientReady(recipient))
env.YARHM_passRecipientStatus=status
boxBlocked=true;passGun.run(false);assert(hum.Health==100 and root.CFrame==origin);boxBlocked=false
local beforePivots=countPivots()
passGun.run(false);assert(countPivots()==beforePivots+5)
assert(hum.Health==0 and root.Position.X>0 and not passGun.busy and not autoGrabBusy and lastWait==0.5)
hum.Health=100;root.CFrame=origin;gun.Parent=nil
passGun.run(false);assert(hum.Health==100 and root.CFrame==origin)
gun.Parent=char;flingBusy=true;passGun.run(false);assert(hum.Health==100);flingBusy=false
afterWait=function() recipient.Parent=nil end
passGun.run(false);assert(hum.Health==100 and root.Position.X==origin.Position.X and not passGun.busy)
recipient.Parent=players
afterWait=function() murderer=recipient end
passGun.run(false);assert(hum.Health==100 and root.Position.X==origin.Position.X and not passGun.busy)
murderer=nil;afterWait=function() recipientAlive=false end
passGun.run(false);assert(hum.Health==100 and root.Position.X==origin.Position.X and not passGun.busy)
recipientAlive=true;afterWait=nil
passGun.button.up();assert(passGun.auto and passGun.button.Text=='Auto Pass\nGun ON')
passGun.retryAt=0;murderer=recipient;hooks[rs2.Heartbeat](0.25);assert(hum.Health==100)
murderer=nil;recipientAlive=false;hooks[rs2.Heartbeat](0.25);assert(hum.Health==100)
recipientAlive=true;hooks[rs2.Heartbeat](0.25);assert(hum.Health==0)
passGun.button.up();assert(not passGun.auto)
''')
print("PASS: manual and automatic passing reject dead and murderer recipients before moving and before resetting; landing follows recipient facing, blocks walls/occupied space/missing floor; pass requires unlocked recipient and owned gun; equips backpack gun, resets after teleport, respects busy state, restores position on recipient departure, and supports auto toggle; menu-only Join User and changed Lua syntax verified.")
