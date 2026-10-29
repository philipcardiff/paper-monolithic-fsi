import sys, runpy, math, collections
sys.argv=['x',sys.argv[1]]
src=open('audit_ratio.py').read().split('out = []')[0]
exec(src)
g=collections.defaultdict(list)
for o,n in zip(own,nei):
    r=max(V[o],V[n])/min(V[o],V[n])
    if r>1.5: g[round(0.5*(C[o][1]+C[n][1]),3) if abs(C[o][1]-C[n][1])>abs(C[o][0]-C[n][0]) else ('x',round(0.5*(C[o][0]+C[n][0]),3))].append((r,0.5*(C[o][0]+C[n][0]),0.5*(C[o][1]+C[n][1])))
for k,v in sorted(g.items(),key=str):
    xs=[t[1] for t in v]; ys=[t[2] for t in v]
    print(k,len(v),'Vratio max %.2f'%max(t[0] for t in v),'x %.3f-%.3f'%(min(xs),max(xs)),'y %.3f-%.3f'%(min(ys),max(ys)))
