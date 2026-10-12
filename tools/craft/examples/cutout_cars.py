import cv2,numpy as np,json
im=cv2.imread('base.png');Y=1150;H,W=im.shape[:2]
VP=np.array([479.,1180.])
boxes=[(120,92,230,170),(330,93,429,180),(560,90,659,167),(740,86,852,162),(515,62,572,106),(292,56,345,94),(403,52,447,89),(620,58,677,100)]
full=np.zeros((H,W),np.uint8);rect=np.zeros((H,W),np.uint8);cars=[]
for i,(x0,y0,x1,y1) in enumerate(boxes):
    y0+=Y;y1+=Y;p=8
    X0,Y0,X1,Y1=x0-p,y0-p,x1+p,y1+p
    sub=im[Y0:Y1,X0:X1].copy()
    m=np.zeros(sub.shape[:2],np.uint8)
    bg=np.zeros((1,65));fg=np.zeros((1,65))
    cv2.grabCut(sub,m,(p-2,p-2,x1-x0+4,y1-y0+4),bg,fg,6,cv2.GC_INIT_WITH_RECT)
    m=((m==1)|(m==3)).astype(np.uint8)
    n,l,st,_=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]);m=(l==k).astype(np.uint8)
        ff=m.copy();h,w=m.shape;mm=np.zeros((h+2,w+2),np.uint8);cv2.floodFill(ff,mm,(0,0),1);m=m|(1-ff)
    if m.sum()<20:
        m[:]=0;m[p:p+y1-y0,p:p+x1-x0]=1;print('rect fallback',i)
    m=cv2.dilate(m,np.array([[0,1,0],[0,1,0],[0,1,0]],np.uint8),anchor=(1,0),iterations=3)
    full[Y0:Y1,X0:X1]|=m
    rect[y0-3:y1+7,x0-4:x1+4]=1
    a=cv2.GaussianBlur(m.astype(np.float32),(3,3),0)
    cv2.imwrite(f'car{i}.png',np.dstack([sub,(a*255).astype(np.uint8)]))
    ys,xs=np.where(m>0)
    cars.append(dict(i=i,x0=X0,y0=Y0,w=X1-X0,h=Y1-Y0,bx=float(X0+xs.mean()),by=float(Y0+ys.max())))
json.dump(cars,open('cars.json','w'),indent=1)
mask=rect|cv2.dilate(full,np.ones((5,5),np.uint8))
cv2.imwrite('mask.png',mask*255)

lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
roadc=lab[1700,300]
road=np.zeros((H,W),np.uint8)
def ext(p,yb):
    return [int(VP[0]+(p[0]-VP[0])*(yb-VP[1])/(p[1]-VP[1])),yb]
poly=np.array([[454,1187],[503,1187],[680+int((H+400-1240)/0.30),H+400],[int((1320-(H+400))/0.293),H+400]],np.int32)
cv2.fillPoly(road,[poly],1)
cv2.imwrite('road.png',road*255)
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
isyel=lambda c:False
plate=im.copy();base=np.array(im[1700,300],np.uint8)
ys,xs=np.where(mask>0)
for y,x in zip(ys,xs):
    d=np.array([x,y],float)-VP;n=np.linalg.norm(d);u=d/n;t=n;src=None
    while True:
        t+=1;q=VP+u*t;qx,qy=int(round(q[0])),int(round(q[1]))
        if qx<0 or qy<0 or qx>=W or qy>=H: break
        if not mask[qy,qx]: src=im[qy,qx];break
    if road[y,x]:
        val=base
        if src is not None:
            h_,s_,v_=cv2.cvtColor(src.reshape(1,1,3),cv2.COLOR_BGR2HSV)[0,0]
            if 12<h_<40 and s_>100 and v_>90: val=src
        plate[y,x]=val
    elif src is not None and y>=1187: plate[y,x]=src
hole=((mask>0)&(road==0)&(np.arange(H)[:,None]<1187)).astype(np.uint8)*255
plate=cv2.inpaint(plate,hole,5,cv2.INPAINT_TELEA)
cv2.imwrite('plate.png',plate)
cv2.imwrite('vis.png',np.vstack([im[1180:1340],plate[1180:1340],cv2.cvtColor(road*255,cv2.COLOR_GRAY2BGR)[1180:1340]]))
