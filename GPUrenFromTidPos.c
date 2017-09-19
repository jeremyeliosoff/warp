/*float smoothstep(float edge0, float edge1, float x) {
	// Scale, bias and saturate x to 0..1 range
	float ret = edge1;
	if (edge1 > edge0) {
		ret = clamp((x - edge0)/(edge1 - edge0), 0.0, 1.0); 
		//Evaluate polynomial
		ret = ret*ret*(3 - 2*ret);
	}
	return ret;
}
*/


float smoothLaunch(float edge0, float edge1, float x) {
	return min(1.0,2.0*smoothstep(edge0, edge0+(edge1-edge0)*2, x));
}

float mixI(uchar a, uchar b, float m) {
	return m*b + (1.0-m)*a;
}

void mix3(uchar* a, uchar* b, float m, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixI(a[i], b[i], m);
	}
}

void set3uchar(uchar x, uchar y, uchar z, uchar* ret) {
	ret[0] = x;
	ret[1] = y;
	ret[2] = z;
}

void getArrayCell(int x, int y, int xres, int yres,
  uchar __attribute__((address_space(1)))* img,
  uchar* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[0] = img[i];
		ret[1] = img[i+1];
		ret[2] = img[i+2];
	}
}

void setLevCell(int n, int x, int y, int xres, int yres,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (n*xres*yres + x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];//i < 15 ? 255 : i % 255;
	}
}

void setLevCell0(int n, int x, int y, int xres, int yres,
  uchar __attribute__((address_space(1)))* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (n*xres*yres + x * yres + y) * 3;
		ret[i] = 0;
		ret[i+1] = 0;
		ret[i+2] = 0;
	}
}

void setImgLevCell(int imgn, int n, int x, int y, int xres, int yres,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (imgn*n*xres*yres + x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}


void setArrayCell(int x, int y, int xres, int yres,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		//int i = (y * xres + x) * 3;
		int i = (x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}

void getImageCell(int x, int y, int xresIn, int yresIn,
  uchar __attribute__((address_space(1)))* img,
  uchar* ret)
{
	int xres = xresIn + 1;
	int yres = yresIn + 1;
	if (x >= 0 && x < yres && y >= 0 && y < xres) {
		int i = (y * yres + x) * 3;
		//int i = (x * yres + y) * 3;
		ret[0] = img[i];
		ret[1] = img[i+1];
		ret[2] = img[i+2];
	}
}

float jRand(int seed) {
	return ((seed + 11)*(seed + 1321) % 1000)/1000.0;
}

float jRandNP(int seed) {
	return 2.0*jRand(seed) - 1.0;
}

int getCellScalar(int x, int y, int xres, int yres,
  int __attribute__((address_space(1)))* _inSurfGrid)
{
	if (x < 0 || x > yres || y < 0 || y > xres) {
		return -1;
	} else {
		//int i = y * xres + x;
		int i = x * xres + y;
		return _inSurfGrid[i];
	}
}

void getBbx(int __attribute__((address_space(1)))* atrBbx, int i, int* mnx, int* mny, int* mxx, int* mxy) {
	int ix4 = i*4;

	*mnx = atrBbx[ix4];
	*mny = atrBbx[ix4+1];
	*mxx = atrBbx[ix4+2];
	*mxy = atrBbx[ix4+3];
}


void getBbxInfo(int __attribute__((address_space(1)))* atrBbx,
		int i, int* cx, int* cy, int *dx, int *dy,
		int* mnx, int* mny, int* mxx, int* mxy) {
	int ix4 = i*4;

	getBbx(atrBbx, i, mnx, mny, mxx, mxy);

	*cx = (*mnx + *mxx)/2;
	*cy = (*mny + *mxy)/2;
	*dx = *mxx - *mnx;
	*dy = *mxy - *mny;

}

__kernel void renFromTid(
			int xres,
			int yres,
			int tidPosToRen,
			int xofs,
			__global int* _tidPosGrid,
			__global uchar* srcImg,
			__global uchar* outsAllPrev,
			__global uchar* outsAll)
{
	int yo = get_global_id(0);
	int xo = get_global_id(1);

	uchar red[] = {255, 0, 0};
	uchar green[] = {0, 255, 0};

	__local int xxof;
	xxof = 30;
	//__private int yi;
	__local int xofss;
	xofss = 2;
	int yi = yo;//tidPosToRen % 2;
	int xi = xo + 1;// + xofs;//1*(((tidPosToRen/30) % 2)-1);

	//int xii = xi-1;

	int tidPos = -1;
	//if (yi < xres-1 && xi < yres-1) 
		tidPos = getCellScalar(xi-1, yi, xres-1, yres-1, _tidPosGrid); // Why xi-1?

	uchar outsAllPrevClr[] = {0, 0, 0};
	getImageCell(xi, yi, xres-1, yres-1, outsAllPrev, outsAllPrevClr);

	uchar imgClr[] = {0, 0, 0};
	getImageCell(xi, yi, xres-1, yres-1, srcImg, imgClr); // Why -1?

	uchar outClr[] = {0, 0, 0};
	if (tidPos == tidPosToRen) 
	//if (1)
	{
		set3uchar(255, 0, 100, outClr);
		//setLevCell(0, yo, xo, xres, yres, outClr, outsAll);
		imgClr[tidPosToRen % 3] = 200;
		if (tidPosToRen == 3 || tidPosToRen == 10) {
			set3uchar(200, 0, 0, imgClr);

		}
		setLevCell(0, yo, xo, xres, yres, imgClr, outsAll);
	} else {
		set3uchar(0, 200, 0, outClr);
		setLevCell(0, yo, xo, xres, yres, outsAllPrevClr, outsAll);
		//setLevCell(0, yo, xo, xres, yres, imgClr, outsAll);
		//setLevCell(0, yo, xo, xres, yres, outClr, outsAll);
	}

	//xi += 1;
	//setLevCell(0, yo, xo, xres, yres, red, outsAll);
	//uchar db[] = {(10*yi)%255, (10*xi)%255, 0};
	//setLevCell(0, yo, xo, xres, yres, imgClr, outsAll);
	//setLevCell(0, yi, xi, xres, yres, db, outsAll);
	//setLevCell(0, yi, xi+3, xres, yres, red, outsAll);

	
}
