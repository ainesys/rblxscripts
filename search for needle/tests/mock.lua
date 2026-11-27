
table.clear=function(t) for k in pairs(t) do t[k]=nil end end
math.clamp=function(v,a,b) return math.max(a,math.min(b,v)) end
OverlapParams={new=function() return {} end}
now=0; os.clock=function() return now end
function sig() local s={h={}}; function s:Connect(f) local c={on=true}; function c:Disconnect() self.on=false end; self.h[#self.h+1]={f,c}; return c end; function s:Fire(...) for _,h in ipairs(self.h) do if h[2].on then h[1](...) end end end; return s end
local vm={}; function V(x,y,z) return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},vm) end
vm.__add=function(a,b) return V(a.X+b.X,a.Y+b.Y,a.Z+b.Z) end
vm.__mul=function(a,b) return V(a.X*b,a.Y*b,a.Z*b) end
vm.__sub=function(a,b) return V(a.X-b.X,a.Y-b.Y,a.Z-b.Z) end
vm.__index=function(a,k) if k=='Magnitude' then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z) end; if k=='Unit' then local n=math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z); return V(a.X/n,a.Y/n,a.Z/n) end end
local cm={}; function C(x,y,z) return setmetatable({Position=type(x)=='table' and x or V(x,y,z)},cm) end
cm.__mul=function(a,b) return C(a.Position+b.Position) end; cm.__add=function(a,b) return C(a.Position+b) end; cm.__index=function(a,k) if k=='Rotation' then return C() end; if k=='PointToObjectSpace' then return function(self,v) return v-self.Position end end end
Vector3={new=V,zero=V()}; CFrame={new=C}
Color3={new=function() end,fromRGB=function() end}; UDim={new=function() end}; UDim2={new=function() return {X={Offset=0},Y={Offset=0}} end,fromOffset=function(x,y) return {X={Offset=x},Y={Offset=y}} end,fromScale=function() return {X={Offset=0},Y={Offset=0}} end}
Enum=setmetatable({},{__index=function() return setmetatable({},{__index=function(_,k) return k end}) end})
local m={}
function m:GetPropertyChangedSignal(k) self.signals=self.signals or {}; self.signals[k]=self.signals[k] or sig(); return self.signals[k] end
function m:IsA(c) return self.ClassName==c or c=='BasePart' and self.ClassName=='Part' end
function m:FindFirstChild(n,r) for _,o in ipairs(self.children) do if o.Parent==self and o.Name==n then return o end end; if r then for _,o in ipairs(self:GetChildren()) do local found=o:FindFirstChild(n,true); if found then return found end end end end
m.WaitForChild=m.FindFirstChild
function m:GetChildren() local a={}; for _,o in ipairs(self.children) do if o.Parent==self then a[#a+1]=o end end; return a end
function m:GetDescendants() self.scanCount=(self.scanCount or 0)+1; local a={}; for _,o in ipairs(self:GetChildren()) do a[#a+1]=o; for _,d in ipairs(o:GetDescendants()) do a[#a+1]=d end end; return a end
function m:FindFirstChildOfClass(c) for _,o in ipairs(self.children) do if o:IsA(c) then return o end end end
function m:FindFirstChildWhichIsA(c) for _,o in ipairs(self:GetDescendants()) do if o:IsA(c) then return o end end end
function m:IsDescendantOf(o) local p=self.Parent; while p do if p==o then return true end; p=p.Parent end; return false end
function m:GetAttribute(k) return self.attr[k] end
function m:GetPivot() return self.CFrame or C() end
function m:FireServer(...) self.calls[#self.calls+1]={...} end
function m:Invoke(...) return self.OnInvoke(...) end
function m:Destroy() self.Destroying:Fire(); self.Parent=nil end
local mt={__index=function(o,k) if k=='Position' then return o.CFrame.Position end; if k=='AbsoluteSize' then return o.Name=='SafeArea' and V(2340,1080) or V(280,294) end; if k=='AbsolutePosition' then local p=rawget(o,'Position'); return p and V(p.X.Offset,p.Y.Offset) or V() end; return m[k] end,__newindex=function(o,k,v) rawset(o,k,v); if k=='Parent' and v then v.children[#v.children+1]=o end end}
function O(c,n,p) local o=setmetatable({ClassName=c,Name=n,children={},attr={},calls={},Transparency=0,Size=V(1,1,1),CanCollide=true,InputBegan=sig(),OnClientEvent=sig(),Destroying=sig(),DescendantAdded=sig(),DescendantRemoving=sig(),Activated=sig()},mt); o.Parent=p; return o end
Instance={new=function(c) return O(c,c) end}
workspace=O('Folder','Workspace'); p=O('Player','Player'); pg=O('Folder','PlayerGui',p); p.CharacterRemoving=sig()
char=O('Model','Character',workspace); p.Character=char; root=O('Part','HumanoidRootPart',char); root.CFrame=C(); hum=O('Humanoid','Humanoid',char); hum.Health=100
p.attr={HayHeld=0,HayCapacity=25}
rep=O('Folder','ReplicatedStorage'); rem=O('Folder','NeedleHaystack',rep)
for _,n in ipairs({'PickHay','SellHay','VacuumAction','PitchforkDig','CollectGem','DeployDrone','BuyUpgrade'}) do O('RemoteEvent',n,rem) end
hf=O('Folder','HaystackClient',workspace)
for i=1,10 do local h=O('Part','Hay'..i,hf); h.CFrame=C(i,0,0); h.attr.HayId=i end
sm=O('Model','SellModel',workspace); cow=O('Model','Cow',sm); cow.CFrame=C(100,0,0)
hb=sig(); services={Players={LocalPlayer=p},RunService={Heartbeat=hb},ReplicatedStorage=rep,UserInputService={InputBegan=sig(),InputChanged=sig(),InputEnded=sig()}}
game={IsLoaded=function() return true end,GetService=function(_,n) return services[n] end}
warn=print
function tick(t) now=t; hb:Fire() end
function calls(n) return #rem:FindFirstChild(n).calls end

function m:GetPartBoundsInRadius() return hf:GetChildren() end

function m:GetServerTimeNow() return now end
table.find=function(t,v) for i,x in ipairs(t) do if x==v then return i end end end
