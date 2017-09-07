
void getClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	ret[i] = imgArray[i];
	ret[i+1] = imgArray[i+1];
	ret[i+2] = imgArray[i+2];
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
	getClr(x, y, xres, npix, imgArray, jtLevels);

}
