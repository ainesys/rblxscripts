from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

root = Path(__file__).resolve().parents[2]
source = (root / "99nightshollow/AineHollow.txt").read_text(encoding="utf-8")
ast.parse(source)
lua = LuaRuntime()
lua.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))


def section(start, end):
    return source[source.index(start):source.index(end, source.index(start))]


setup = r'''
local Settings = {HoverHeight=28, MobDistance=38, AutoFuel=false, AutoEnterVoid=false}
local state = {closed=false, enabled=true, generation=0}
local guard = {untilTime=0, mobs={}, nextScan=0}
local player, ReplicatedStorage = p, rep
local tagged = {}
local Players = {GetPlayerFromCharacter=function() return nil end}
local CollectionService = {GetTagged=function(_, tag) return tagged[tag] or {} end}
local RunService = {Heartbeat=hb}
local dragged
local function make(class, props, parent)
 local obj=O(class,class,parent)
 for k,v in pairs(props) do obj[k]=v end
 return obj
end
local connections={}
local function connect(signal, callback)
 local c=signal:Connect(callback);connections[#connections+1]=c;return c
end
local m=getmetatable(root).__index(root,'IsA')
local objectMethods=getmetatable(root).__index
function root:GetAttributes() return self.attr end
root.AssemblyMass=1
workspace.Gravity=196.2
local function stopDragging() dragged=nil end
local function eatFood() return false end
local function heal() return false end
local function chooseUpgrade() return false end
local function defend() return false end
local function prepareSupplies() return false end
local function getClient() return nil end
local vm=getmetatable(V())
vm.__mul=function(a,b)
 if type(b)=='number' then return V(a.X*b,a.Y*b,a.Z*b) end
 return V(a.X*b.X,a.Y*b.Y,a.Z*b.Z)
end
local function safeLantern() state.safe=true end
local function collectFlower() state.collected=true end
local function enterVoid() state.entered=true end
local function fuelFire() state.fueled=true end
local function chopTree() state.chopped=true end
'''

helpers = section("local function character()", "local function stopDragging()")
progress = section("local function flowerProgress()", "local function nearestTagged(")
heartbeat = section("connect(RunService.Heartbeat, function()", "connect(UserInputService.InputBegan,")
step = section("local function step()", "connect(autoButton.Activated,")

checks = r'''
tick(1)
assert(root.Position.Y==28 and root:FindFirstChild('HollowSafetyHover'), 'initial hover')
assert(guard.force.Position.Y==28, 'hover target holds altitude')
state.enabled=false
local y=root.Position.Y
tick(2)
assert(root.Position.Y==y, 'pause retains protection')
local wolf=O('Model','Wolf',workspace)
local wr=O('Part','HumanoidRootPart',wolf);wr.CFrame=C(4,28,0)
wolf.PrimaryPart=wr;tagged.NPC={wolf}
tick(3)
assert(root.Position.Y==56 and state.generation==1, 'mob triggers retreat and cancellation')
tagged.NPC={}
hum.Health=90
tick(4)
assert(root.Position.Y==84 and state.generation==2, 'damage triggers retreat')
hum.Health=0;y=root.Position.Y
tick(5)
assert(root.Position.Y==y, 'dead character is not moved')
hum.Health=100;guard.lastHealth=100;guard.untilTime=0
local hollow=O('Folder','HollowMap',workspace)
function hollow:GetAttributes() return self.attr end
hollow.attr={PlantCount=20,HollowPlant0=V(),HollowPlant19=V(),HollowLantern0=V()}
local picked,total=flowerProgress()
assert(picked==18 and total==20, 'progress counts only remaining plants')
hollow.attr={PlantCount=20,HollowLantern0=V()}
picked,total=flowerProgress()
assert(picked==20 and total==20, 'map progress can be full without a win')
state.enabled=true
workspace.attr.Progress=3
step()
assert(state.enabled and not state.status:find('complete'), 'inactive cleared map is not completion')
p.attr.HollowBeaten=true
step()
assert(not state.enabled and state.status:find('server confirmed'), 'only server completion stops the quest')
tick(20)
assert(root:FindFirstChild('HollowSafetyHover'), 'completion retains protection')
root.CFrame=C(0,-300,8000)
tick(21)
assert(guard.force.Position.Z==8000 and guard.force.Position.Y==-285, 'hover follows server zone transitions')
releaseHover()
assert(not root:FindFirstChild('HollowSafetyHover'), 'hover cleanup')
for _,c in ipairs(connections) do c:Disconnect() end
print('PASS: hover, pause protection, mob/damage retreat, cancellation, death, map progress, completion, cleanup')
'''
lua.execute(setup + helpers + progress + heartbeat + step + checks)

combat = LuaRuntime()
combat.execute((root / "search for needle/tests/mock.lua").read_text(encoding="utf-8"))
combat_setup = r'''
local player=p
local state={closed=false,enabled=true}
local Settings={AutoHeal=true,HealBelow=85,AutoDefend=true}
local nextHeal,nextShot=0,0
local function update() end
local inv=O('Folder','Inventory',p)
hum.MaxHealth=100
root.AssemblyMass=1
local selected,shots,reloads=0,0,0
local tool, equipped
local client={InventoryHandler={},CollisionUtility={}}
function client.InventoryHandler.GetCurrentlyEquippedClass() return equipped end
function client.InventoryHandler.RequestEquipItem(item)
 selected=item.Name
 tool={Ammo=item:GetAttribute('Ammo') or 1,FireRate=1,ProjectileSpeed=350}
 function tool:Activate()
  hum.Health=math.min(hum.MaxHealth,hum.Health+(item:GetAttribute('RestoreHealth') or 0))
  item:Destroy()
 end
 function tool:Reload() reloads=reloads+1 end
 function tool:Fire(ray) assert(ray.Origin and ray.Direction,'aim ray');shots=shots+1 end
 equipped={Model=item,Tool=tool}
end
local function getClient() return client end
task={wait=function(dt) now=now+(dt or .1) end}
Ray={new=function(origin,direction) return {Origin=origin,Direction=direction} end}
local enemies={}
local CollectionService={GetTagged=function() return enemies end}
local isPlayer=false
local Players={GetPlayerFromCharacter=function() return isPlayer and {} or nil end}
local blocked=false
local wall=O('Part','Wall',workspace)
function workspace:Raycast() return blocked and {Instance=wall} or nil end
local function medicine(name,amount)
 local item=O('Model',name,inv);item.attr.RestoreHealth=amount;return item
end
'''
combat_functions = section("local function equipItem(", "local function step()")
combat_checks = r'''
local bandage=medicine('Bandage',50)
local medkit=medicine('MedKit',100)
hum.Health=20
assert(heal(char,root,hum) and selected=='MedKit' and hum.Health==100, 'critical health prioritizes medkit')
hum.Health=100;now=10
assert(not heal(char,root,hum), 'healthy character preserves medicine')
hum.MaxHealth=200;hum.Health=150;now=20
assert(heal(char,root,hum) and selected=='Bandage' and hum.Health==200, 'healing threshold scales with max health')
local rifle=O('Model','Rifle',inv);rifle.attr={ToolName='Firearm',Ammo=1}
local wolf=O('Model','Wolf',workspace);wolf.attr.Health=100
local head=O('Part','Head',wolf);head.CFrame=C(20,5,0);head.AssemblyLinearVelocity=V()
enemies={wolf};now=30
assert(defend(char,root) and shots==1 and selected=='Rifle', 'owned gun aims at mob')
now=40;isPlayer=true
assert(not defend(char,root) and shots==1, 'never target a player')
isPlayer=false;blocked=true;now=50
assert(not defend(char,root) and shots==1, 'do not shoot through obstructing geometry')
blocked=false;rifle.attr.Ammo=0;p.attr.RifleAmmo=5;tool.Ammo=0;now=60
assert(defend(char,root) and reloads==1, 'empty gun uses native reload')
rifle:Destroy();now=70
assert(not defend(char,root) and shots==1, 'no weapon means no fabricated shots')
print('PASS: medicine selection, full-health preservation, max-health scaling, aimed fire, player exclusion, line of sight, reload, missing weapon')
'''
combat.execute(combat_setup + combat_functions + combat_checks)
