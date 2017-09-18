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
		ret[i+2] = val[2];
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
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		//int i = (y * xres + x) * 3;
		int i = (y * xres + x) * 3;
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

int getCellScalar(int x, int y, int yres,
  int __attribute__((address_space(1)))* _inSurfGrid)
{
	//int i = y * xres + x;
	int i = x * yres + y;
	return _inSurfGrid[i];
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
			int nClrs,
			int lev,
			float levThresh,
			__global int* _tidPosGrid,
			__global int* tids,
			__global int* atrBbx,
			__global uchar* clrsInt,
			__global uchar* outsAllPrev,
			__global uchar* outsAll)
{
	int xi = get_global_id(0);
	int yi = get_global_id(1);

	float prog = levThresh;


	uchar val[] = {0, 0, 0};
	uchar prevVal[] = {0, 0, 0};
	uchar red = {255, 0, 0};
	uchar green = {0, 255, 0};

	getArrayCell(xi, yi, xres, yres, outsAllPrev, prevVal);

	setLevCell0(0, xi, yi, xres, yres, outsAll);

	int tidPos = getCellScalar(xi, yi, yres, _tidPosGrid);
	if (tidPos > -10) {
		int tid = tids[tidPos];

		int xofs = 0;//xfK*(tcx-cx);//jRandNP(tid) * 10;
		int yofs = 3;//fK*(tcy-cy);//jRandNP(tid+11) * 10;
		int xo = xi + xofs;
		int yo = yi + yofs;

		float mxr = 4*(1-prog)*prog;
		uchar val[] = {0, 0, 0};
		int clrInd = tid % nClrs;
		val[0] = clrsInt[clrInd * 3];
		val[1] = clrsInt[clrInd * 3+1];
		val[2] = clrsInt[clrInd * 3+2];


		setLevCell(0, xo, yo, xres, yres, red, outsAll);
	} else {
		// Strange: if you don't do this, it accumulates levs.
		//setLevCell(0, xi, yi, xres, yres, prevVal, outsAll);
	}

	
}
