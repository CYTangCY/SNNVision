import numpy as np

with open('boxes.txt','w') as pp:
    i = 1
    for y in range(0, 8, 1):
        for x in range(0, 8, 1):
            xo = 80*x
            yo = 60*y
            xp = 80*(x+1)
            yp = 60*(y+1)
            pp.write('        box%d = np.array([[%d,%d],[%d,%d],[%d,%d],[%d,%d]], np.int)\n'%(i,xo,yo,xp,yo,xp,yp,xo,yp))
            pp.write('        box%d = box%d.reshape((-1, 1, 2))\n'%(i,i))
            pp.write('        self.boxes.append(box%d)\n'%(i))
            i += 1
