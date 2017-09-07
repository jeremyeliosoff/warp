
int clrAvg(uchar* clr)
{
	return (clr[0] + clr[1] + clr[2])/3;
}


void getClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar* ret)
{
	int i = y * xres * npix + x * npix;
	ret[0] = imgArray[i];
	ret[1] = imgArray[i+1];
	ret[2] = imgArray[i+2];
}

void setClr(int x, int y, int xres, int npix,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	ret[i] = val[0];
	ret[i+1] = val[1];
	ret[i+2] = val[2];
}


int getClrAvg(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray)
{
	uchar clr[3];
	getClr(x, y, xres, npix,imgArray, clr);
	return clrAvg(clr);
}

void cpClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	uchar clr[3];
	uchar avg = getClrAvg(x, y, xres, npix, imgArray);
	uchar retClr[] = {avg, avg, avg};

	setClr(x, y, xres, npix, retClr, ret);
	//uchar avg = clrAvg(clr);
	//ret[i] = avg;
	//ret[i+1] = avg;
	//ret[i+2] = avg;
}

__kernel void initJtC(
			__global uchar* imgArray,
			__global uchar* jtLevels) 
{
	int x = get_global_id(1);
	int y = get_global_id(0);

	int xres = %d;
	int yres = %d;
	int npix = 3;
	//cpClr(x, y, xres, npix, imgArray, jtLevels);
	uchar nbrs[4];

	if (x < xres-1 && y < yres-1) {
		int i;
		int tot = 0;

		for (i = 0; i < 4; i++) {
			int xx = x + i/2;
			int yy = y + i%%2;
			uchar avg = getClrAvg(xx, yy, xres, npix, imgArray);
			int levThreshInt = 100; // Adapt from py.
			uchar val = avg > levThreshInt ? 1 : 0;
			nbrs[i] = val;
			tot += val;
		}
		uchar retClr[3] = {tot, tot, tot};
		setClr(x, y, xres, npix, retClr, jtLevels);
	}
}
