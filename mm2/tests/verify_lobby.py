from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast

source = (Path(__file__).resolve().parents[1] / "updYarhm.txt").read_text(encoding="utf-8")
start = source.index("function AineRuntime.lobbyTeleportTarget")
resolver = source[start:source.index("function AineRuntime.clone", start)]
ast.parse(resolver)
start = source.index("\tlocal function teleportToSpawns")
ast.parse(source[start:source.index("\tAineRuntime.connect(mapTeleportBtn.Activated", start)])

lua = LuaRuntime()
lua.execute(r'''
AineRuntime = {}
local methods = {}
function node(name, class, parent)
 local n = setmetatable({Name=name, ClassName=class, children={}, Size={Y=2}}, {__index=methods})
 n.CFrame = setmetatable({name=name}, {__add=function(frame, offset) return {name=frame.name, height=offset.Y} end})
 if parent then n.Parent=parent;table.insert(parent.children,n) end
 return n
end
function methods:IsA(class) return self.ClassName==class or (class=='BasePart' and (self.ClassName=='Part' or self.ClassName=='SpawnLocation')) end
function methods:GetDescendants()
 local all={}
 for _,child in ipairs(self.children) do
  all[#all+1]=child
  for _,nested in ipairs(child:GetDescendants()) do all[#all+1]=nested end
 end
 return all
end
function methods:FindFirstChild(name, recursive)
 for _,child in ipairs(recursive and self:GetDescendants() or self.children) do if child.Name==name then return child end end
end
function methods:FindFirstChildWhichIsA(class, recursive)
 for _,child in ipairs(recursive and self:GetDescendants() or self.children) do if child:IsA(class) then return child end end
end
function methods:IsDescendantOf(ancestor)
 local current=self.Parent
 while current do if current==ancestor then return true end;current=current.Parent end
 return false
end
Vector3={new=function(x,y,z) return {X=x,Y=y,Z=z} end}
CFrame={new=function(x,y,z) return {X=x,Y=y,Z=z} end}
local player={}
game={GetService=function() return {LocalPlayer=player} end}
local map
function getgenv() return {YARHM_getMap=function() return map end} end
function reset()
 workspace=node('Workspace','Workspace');player.RespawnLocation=nil;map=nil
end
function setRespawn(part) player.RespawnLocation=part end
function setMap(part) map=part end
function target() return AineRuntime.lobbyTeleportTarget({HipHeight=2},{Size={Y=2}}) end
''')
lua.execute(resolver)
lua.execute(r'''
reset()
local lobby=node('Lobby','Model',workspace)
local spawns=node('Spawns','Folder',lobby)
node('Spawn','SpawnLocation',spawns)
assert(target().name=='Spawn' and target().height==4.5)
reset()
local normal=node('Normal','Folder',workspace)
local lobby=node('Lobby','Model',normal)
local nested=node('Geometry','Folder',lobby)
node('NestedSpawn','SpawnLocation',nested)
assert(target().name=='NestedSpawn')
reset()
local lobby=node('lobby','Folder',workspace)
node('SpawnPoint','Part',lobby)
assert(target().name=='SpawnPoint')
reset()
local lobby=node('Lobby','Folder',workspace)
local spawns=node('Spawns','Folder',lobby)
node('Pad','Part',spawns)
assert(target().name=='Pad')
reset()
local lobby=node('Lobby','Model',workspace)
node('Decoration','Part',lobby)
local map=node('ActiveMap','Model',workspace)
local spawn=node('RoundSpawn','SpawnLocation',map)
setMap(map);setRespawn(spawn)
assert(target().X==26.851 and target().Y==505.244 and target().Z==-25.753)
reset()
local spawn=node('Respawn','SpawnLocation',workspace)
setRespawn(spawn)
assert(target().name=='Respawn')
reset()
assert(target().X==26.851 and target().Y==505.244 and target().Z==-25.753)
''')
print("PASS: lobby resolver supports standard/nested spawns, nested and lowercase lobbies, named pads, respawn fallback, excludes map respawns and decoration, and uses recorded coordinates when absent; teleport function syntax passes.")
