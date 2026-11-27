from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

root = Path(__file__).resolve().parents[2]
source = (root / "mm2/updYarhm.txt").read_text(encoding="utf-8")

def section(a, b):
    i = source.index(a)
    return source[i:source.index(b, i)]

round_code = section("\tlocal autoGrabBusy = false", "\n\tlocal lastKillAll")
hunt_code = section("\tlocal autoHunt = false", "\tlocal autoGrabElapsed")
for block in (round_code, hunt_code):
    ast.parse(block)

lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
lua.execute(r'''
local players=services.Players
players.children={}
game.Players=players
local target=O('Player','Target');target.UserId=2;target.Parent=players
target.Character=O('Model','TargetChar',workspace)
local targetHum=O('Humanoid','Humanoid',target.Character);targetHum.Health=100
local targetRoot=O('Part','HumanoidRootPart',target.Character);targetRoot.AssemblyLinearVelocity=V()
function players:GetPlayers() return {p,target} end
function players:GetPlayerByUserId(id) if id==2 then return target end end
local startEvent=O('RemoteEvent','RoundStart',rem)
local endEvent=O('RemoteEvent','RoundEndFade',rem)
local gameplay=rem
local rs2={Heartbeat=sig()}
local clock=0
local function tick() return clock end
local env={}
local function getgenv() return env end
env.YARHM_isAliveInRound=function(who) return who==p and hum.Health>0 or who==target and targetHum.Health>0 end
env.YARHM_isDeadInRound=function(who) return who==target and targetHum.Health<=0 end
env.YARHM_miniFling=function() end
AineRuntime={connect=function(signal,fn) return signal:Connect(fn) end,isProtectedPlayer=function() return false end}
local farmCombat={busy=false}
local flingBusy,teleportShotBusy=false,false
local attempts,mode=0,'fail'
local function releaseFarm() end
local function getNotify() return function() end end
local function flingTarget()
 attempts=attempts+1
 if mode=='error' then error('attempt error') end
 if mode=='spike' then
  targetRoot.AssemblyLinearVelocity=V(600,0,0);rs2.Heartbeat:Fire();targetRoot.AssemblyLinearVelocity=V()
 elseif mode=='roundChange' then endEvent.OnClientEvent:Fire();startEvent.OnClientEvent:Fire() end
end
'''+round_code+r'''
roundFling.enabled=true;roundFling.userId=2
startEvent.OnClientEvent:Fire()
clock=40;rs2.Heartbeat:Fire();assert(attempts==1 and roundFling.pending)
clock=40.1;rs2.Heartbeat:Fire();assert(attempts==1)
clock=41;rs2.Heartbeat:Fire();assert(attempts==2 and roundFling.pending)
mode='spike';clock=42;rs2.Heartbeat:Fire();assert(attempts==3 and not roundFling.pending and roundFling.enabled)
startEvent.OnClientEvent:Fire();mode='error';clock=43;rs2.Heartbeat:Fire();assert(roundFling.pending and not flingBusy)
mode='fail';clock=44;rs2.Heartbeat:Fire();assert(attempts==4)
clock=46;rs2.Heartbeat:Fire();assert(attempts==5 and roundFling.pending)
targetHum.Health=0;clock=47;rs2.Heartbeat:Fire();assert(not roundFling.pending)
targetHum.Health=100;startEvent.OnClientEvent:Fire();mode='roundChange';clock=48
local generation=roundFling.generation
rs2.Heartbeat:Fire();assert(roundFling.pending and roundFling.generation>generation and roundFling.character==nil)
endEvent.OnClientEvent:Fire();assert(not roundFling.pending)
''')

lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
lua.execute(r'''
local players=services.Players
players.children={};game.Players=players
local target=O('Player','Hero');target.Parent=players
local stale=O('Player','OldSheriff');stale.Parent=players
local targetChar=O('Model','HeroChar',workspace);target.Character=targetChar
local targetHum=O('Humanoid','Humanoid',targetChar);targetHum.Health=100
local targetRoot=O('Part','HumanoidRootPart',targetChar);targetRoot.Anchored=false;targetRoot.CFrame=C(20,0,0)
local targetBag=O('Backpack','Backpack',target)
local gun=O('Tool','Gun',targetBag)
local backpack=O('Backpack','Backpack',p)
local knife=O('Tool','Knife',backpack)
local stab=O('RemoteEvent','Stab',knife)
function hum:EquipTool(tool) tool.Parent=char;table.insert(char.children,tool) end
function players:GetPlayers() return {p,stale,target} end
local env={YARHM_isAliveInRound=function(who) return who~=stale end}
local function getgenv() return env end
local farmRoundEnded=false
local seconds,shots,fail=0,0,false
local waitHook
local task={wait=function(dt) seconds=seconds+dt;if waitHook then waitHook() end end}
AineRuntime={closed=false,remember=function() end,isProtectedPlayer=function(who) return who.allowed end}
root.CFrame=C();root.CFrame.LookVector=V(0,0,-1)
function stab:FireServer(action)
 assert(action=='Slash' and targetRoot.Anchored and targetRoot.Position.Z==-1)
 if fail then error('remote error') end
 shots=shots+1
end
'''+hunt_code+r'''
assert(huntGunHolder()==target)
killSheriffTarget(target);assert(shots==0)
autoHunt=true
killSheriffTarget(target)
assert(shots==4 and seconds>=1 and not targetRoot.Anchored and targetRoot.Position.X==20)
target.allowed=true;killSheriffTarget(target);assert(shots==4);target.allowed=false
knife.Parent=nil;killSheriffTarget(target);assert(shots==4);knife.Parent=char
fail=true;assert(not pcall(killSheriffTarget,target));assert(not targetRoot.Anchored and targetRoot.Position.X==20);fail=false
local nested=O('Folder','KnifeLocal',knife)
stab.Parent=nested;table.insert(nested.children,stab)
killSheriffTarget(target);assert(shots==8 and not targetRoot.Anchored)
stab.Parent=nil
local activations=0
function knife:Activate() activations=activations+1 end
function knife:Deactivate() end
killSheriffTarget(target);assert(activations==4 and not targetRoot.Anchored and targetRoot.Position.X==20)
-- A tool that takes multiple frames to equip must not fail the attack lookup.
knife.Parent=backpack
function hum:EquipTool() end
local equipWaits=0
waitHook=function() equipWaits=equipWaits+1;if equipWaits==3 then knife.Parent=char end end
killSheriffTarget(target);assert(equipWaits>=3 and activations==8)
waitHook=function() autoHunt=false end
killSheriffTarget(target);assert(activations==9 and not targetRoot.Anchored)
''')
print("PASS: round fling retries beyond 30 seconds, backs off on errors, stops on observed success/death, restarts next round and ignores stale attempts; hunt selects live gun holder over stale sheriff, equips knife, holds contact through attack window, requires enabled mode/knife, excludes protected target and restores state on error/disable.")
