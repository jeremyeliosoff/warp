
int getClrAvg(uchar* clr)
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


void cpClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	uchar clr[3];
	getClr(x, y, xres, npix, imgArray, clr);
	uchar avg = getClrAvg(clr);
	ret[i] = avg;
	ret[i+1] = avg;
	ret[i+2] = avg;
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
	cpClr(x, y, xres, npix, imgArray, jtLevels);

}
