from pathlib import Path
from lupa import LuaRuntime
from luaparser import ast
import sys
source_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "AineNeedle.txt"
source=source_path.read_text(encoding="utf-8")
ast.parse(source)
l=LuaRuntime()
l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(source)
l.execute(r"""
tick(.1); assert(calls('PickHay')==1,'bounded collection')
local scans=char.scanCount
for i=1,20 do tick(.1+i*.001) end
assert(char.scanCount==scans,'do not rescan character every frame')
local accessory=O('Part','Accessory',char); accessory.CFrame=C(); char.DescendantAdded:Fire(accessory); assert(not accessory.CanCollide,'new parts tracked')
p.attr.HayHeld=25; tick(.2); assert(root.Position.X==100,'cow travel'); assert(calls('SellHay')==0,'replication wait')
tick(.4); assert(calls('SellHay')==1,'sale call'); tick(.6); assert(calls('SellHay')==1,'retry interval'); assert(root.Position.X==100,'await confirmation')
p.attr.HayHeld=0; tick(.8); assert(root.Position.X==0,'sale return')
p.attr.VacuumOwned=true; tick(1); assert(calls('VacuumAction')>=2,'vacuum start and tick')
pg:FindFirstChild('AineNeedle'):FindFirstChild('Shutdown'):Invoke(); assert(root.CanCollide and accessory.CanCollide,'restore collision'); assert(not root:FindFirstChild('NeedleFarmHover'),'remove hover')
local added=O('Part','AfterClose',char); added.CFrame=C(); char.DescendantAdded:Fire(added); assert(added.CanCollide,'disconnect collision watcher')
local n=calls('PickHay'); tick(2); assert(calls('PickHay')==n,'disconnect heartbeat')
print('PASS: collection, event-based collisions, sale confirmation/retries, vacuum, cleanup')
""")
l.execute(source)
l.execute(source)
l.execute(r"""
local count=0; for _,o in ipairs(pg:GetChildren()) do if o.Name=='AineNeedle' then count=count+1 end end; assert(count==1,'one panel on rerun')
p.attr.VacuumOwned=false
tick(3); p.CharacterRemoving:Fire(); assert(root.CanCollide,'respawn restoration'); assert(not root:FindFirstChild('NeedleFarmHover'),'respawn hover cleanup')
print('PASS: rerun and character removal')
""")
# Empty eligible slice while hay is cooling down must not trigger premature selling.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text()); l.execute(source)
l.execute(r"""
for i=10,3,-1 do local part=hf.children[i]; hf.DescendantRemoving:Fire(part); part.Parent=nil end
p.attr.HayHeld=1
tick(.1); tick(.15); tick(.2)
assert(calls('SellHay')==0 and root.Position.X~=100,'cooldown is not an empty stack')
print('PASS: cooldown does not cause premature sell')
""")

# Graveyard selling must use the sell part when there is no cow.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute("cow:Destroy(); local s=O('Part','SellPart',sm); s.CFrame=C(100,0,0); p.attr.HayHeld=25")
l.execute(source)
l.execute("tick(.1); assert(root.Position.X==100,'scarecrow sell point'); tick(.4); assert(calls('SellHay')==1,'sell without cow'); print('PASS: graveyard sell point')")
# Multi-grab sends extra ids in one server request and respects the hand cooldown.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute("p.attr.HayGrabCount=3; p.attr.HayGrabRadius=3; p.attr.HayPickCooldown=.55")
l.execute(source)
l.execute("tick(.1); local c=rem:FindFirstChild('PickHay').calls; assert(#c==1 and #c[1][2]==2,'multi-grab ids'); tick(.2); assert(#c==1,'hand cadence'); print('PASS: upgraded multi-grab and cadence')")
# Upgrade purchases use cash, choose eligible tracks, and wait for replication.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(r"""
local config=O('ModuleScript','Config',rem)
require=function() return {UPGRADE_TRACKS={Grab={Levels={{Cost=0},{Cost=.25}}},Speed={Levels={{Cost=0},{Cost=.25}}},Capacity={Levels={{Cost=0},{Cost=1}}}}} end
local stats=O('Folder','leaderstats',p); cash=O('NumberValue','Cash',stats); cash.Value=1
""")
l.execute(source)
l.execute(r"""
tick(.1); local c=rem:FindFirstChild('BuyUpgrade').calls; assert(#c==1 and c[1][1]=='Grab','first upgrade')
tick(.6); assert(#c==1,'wait for upgrade confirmation')
p.attr.HayUpgradeGrab=2; cash.Value=.75; tick(.7); assert(#c==2 and c[2][1]=='Speed','next affordable upgrade')
p.attr.HayUpgradeSpeed=2; cash.Value=.5; tick(1.1); assert(#c==2,'do not overspend')
print('PASS: cash upgrade selection, confirmation, affordability')
""")
# Hidden candles are ignored; revealed candles are collected and placed before lighting.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(r"""
ritual=O('Folder','CandleRitual',rep); cr=O('Folder','Remotes',ritual)
for _,n in ipairs({'PickUpCandle','PlaceCandle','MatchDone','MatchPuzzle'}) do O('RemoteEvent',n,cr) end
candles=O('Folder','HayCandles',workspace); candle=O('Model','Candle1',candles); candle.CFrame=C(30,0,0); candle.attr={HayCandle=true,Revealed=false}
holders=O('Model','WhereToPlaceCandles',workspace); holder=O('Model','1',holders); holder.CFrame=C(100,0,0)
""")
l.execute(source)
l.execute(r"""
tick(.1); assert(#cr:FindFirstChild('PickUpCandle').calls==0,'ignore hidden candles')
candle.attr.Revealed=true; tick(1); assert(root.Position.X==30,'move to revealed candle')
tick(1.3); assert(#cr:FindFirstChild('PickUpCandle').calls==1,'pickup candle')
p.attr.CarryingCandle='Candle1'; tick(1.4); assert(root.Position.X==100,'move to holder')
tick(1.7); assert(#cr:FindFirstChild('PlaceCandle').calls==1,'place candle')
p.attr.CarryingCandle=nil; p.attr.NeedleInputLocked=true; cr:FindFirstChild('MatchPuzzle').OnClientEvent:Fire(holder,0)
tick(2); assert(#cr:FindFirstChild('MatchDone').calls==0,'wait for puzzle')
tick(5); assert(#cr:FindFirstChild('MatchDone').calls==1,'finish granted puzzle once')
tick(5.1); assert(#cr:FindFirstChild('MatchDone').calls==1,'no repeated completion')
holder.attr.Lit=true; p.attr.NeedleInputLocked=false; tick(5.2); assert(root.Position.X==0,'return after confirmed lit')
holders.attr.AllLit=true; tick(5.3); local n=calls('PickHay'); tick(6); assert(calls('PickHay')==n,'wait for boss')
p.attr.NeedleRoundComplete=true; tick(7); assert(root.CanCollide,'release on objective completion')
print('PASS: candle reveal gating, pickup, place, lighting delay, confirmation, boss transition')
""")

# Cash tool buying saves for the displayed coin option and confirms ownership.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(r"""
O('ModuleScript','Config',rem); require=function() return {UPGRADE_TRACKS={}} end
O('RemoteEvent','BuyShopItem',rem)
local stats=O('Folder','leaderstats',p); cash=O('NumberValue','Cash',stats); cash.Value=7.99
p.attr.HayUpgradeGrab=3; p.attr.HayUpgradeSpeed=3; p.attr.HayUpgradeCapacity=2
local shop=O('Folder','BarnShop',workspace); template=O('Model','PitchforkTemplate',shop)
template.attr={ShopBalanceCurrency='Cash',ShopCurrencyB='Coins',ShopPriceB='$8.00'}
""")
l.execute(source)
l.execute(r"""
tick(.1); assert(calls('BuyShopItem')==0,'save until affordable')
cash.Value=8; tick(.5); assert(calls('BuyShopItem')==1,'buy cash pitchfork')
tick(1); assert(calls('BuyShopItem')==1,'wait for ownership confirmation')
p.attr.PitchforkOwned=true; tick(1.1); assert(calls('BuyShopItem')==1,'do not buy owned tool')
print('PASS: cash pitchfork affordability and ownership confirmation')
""")

# Touch dragging changes panel position and clamps it inside the screen.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text()); l.execute(source)
l.execute(r"""
local gui=pg:FindFirstChild('AineNeedle'); local panel=gui:FindFirstChild('Controls',true); local handle=panel:FindFirstChild('DragHandle')
local touch={UserInputType=Enum.UserInputType.Touch,Position=V(20,20,0)}
handle.InputBegan:Fire(touch); touch.Position=V(400,200,0); services.UserInputService.InputChanged:Fire(touch)
assert(panel.Position.X.Offset==388 and panel.Position.Y.Offset==188,'touch drag position')
touch.Position=V(9999,9999,0); services.UserInputService.InputChanged:Fire(touch)
assert(panel.Position.X.Offset==2052 and panel.Position.Y.Offset==778,'screen clamp')
services.UserInputService.InputEnded:Fire(touch); touch.Position=V(0,0,0); services.UserInputService.InputChanged:Fire(touch)
assert(panel.Position.X.Offset==2052,'stop dragging on release')
print('PASS: mobile dragging, screen bounds, touch release')
""")

# Threats interrupt harvesting, use the combat ray call, and then release the farm.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(r"""
local bf=O('Folder','BossFight',rep); O('ModuleScript','BossAim',bf)
local head=O('Part','Head',char); head.CFrame=C(0,1.5,0)
enemy=O('Model','GraveSkeleton',workspace); er=O('Part','RootPart',enemy); er.CFrame=C(6,0,0); enemy.attr.BossState='Chasing'
p.attr.PitchforkOwned=true
require=function() return {rigs=function() if enemy.attr.BossState=='Defeated' then return {} end; return {{rig=enemy,root=er,minion=true}} end,assist=function() return er.Position+V(0,3,0) end} end
""")
l.execute(source)
l.execute(r"""
tick(.1); local c=rem:FindFirstChild('PitchforkDig').calls
assert(#c==1 and c[1][1]=='Boss','defense combat call'); assert(math.abs(c[1][3].Magnitude-1)<.0001,'normalized aim')
assert(calls('PickHay')==0,'defense takes priority')
enemy.attr.BossState='Defeated'; tick(1); assert(c[#c][1]~='Boss','resume farming after threat')
print('PASS: skeleton defense priority, combat arguments, farm resumption')
""")
# Objective completion needs the actual round-complete state, beyond all candles.
l=LuaRuntime(); l.execute(Path(__file__).with_name("mock.lua").read_text())
l.execute(r"""
local bf=O('Folder','BossFight',rep); O('ModuleScript','BossAim',bf)
local head=O('Part','Head',char); head.CFrame=C(0,1.5,0)
boss=O('Model','PumpkinGolem_Rig',workspace); br=O('Part','RootPart',boss); br.CFrame=C(6,0,0); boss.attr.BossState='Sleeping'
local holders=O('Model','WhereToPlaceCandles',workspace); holders.attr.AllLit=true
p.attr.PitchforkOwned=true
require=function() return {rigs=function() if boss.attr.BossState=='Sleeping' then return {} end; return {{rig=boss,root=br,minion=false}} end,assist=function() return br.Position+V(0,3,0) end} end
""")
l.execute(source)
l.execute(r"""
tick(.1); assert(calls('PitchforkDig')==0,'wait for boss wake')
boss.attr.BossState='Stalking'; tick(1); assert(calls('PitchforkDig')==1,'fight awake boss')
boss.attr.BossState='Falling'; tick(2); assert(calls('PitchforkDig')==1 and root.CanCollide,'release for ending')
p.attr.NeedleRoundComplete=true; tick(3); assert(calls('PitchforkDig')==1,'stop on confirmed round complete')
print('PASS: candle-to-boss transition, ending release, confirmed completion')
""")
