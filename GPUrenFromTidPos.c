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

void renTidPos(
	int xi,
	int yi,
	int tidPos,
	uchar* imgClr,
	uchar* prevVal,
	int xres,
	int yres,
	int nClrs,
	int lev,
	float levThresh,
	__global int* _tidPosGrid,
	__global int* tids,
	__global int* atrBbx,
	__global uchar* clrsInt,
	__global uchar* srcImg,
	__global uchar* sidPostThisAr,
	__global uchar* sidPostALLPrev,
	__global uchar* sidPostALL,
	__global uchar* outsPerLev,
	__global uchar* outsAllPrev,
	__global uchar* outsAll) {

	float prog = levThresh;
	if (tidPos > -1) {
		int tid = tids[tidPos];

		//int mnx, mny, mxx, mxy;
		//getBbx(atrBbx, tid, &mnx, &mny, &mxx, &mxy);
		int cx = xres/2;
		int cy = .35*yres;
		int tcx, tcy, dx, dy, mnx, mny, mxx, mxy;
		getBbxInfo(atrBbx, tidPos, &tcx, &tcy, &dx, &dy, &mnx, &mny, &mxx, &mxy);
		float big = ((float)dx/xres)*((float)dy/yres);
		float bigK = 1-big;
		bigK *= bigK;


		float xfK = 0;
		
		if (cx < mnx || cx > mxx || cy < mny || cy > mxy) {
			float xfKK = 3;
			xfK = smoothLaunch(0.2, 1.0, prog) * bigK * xfKK;
		}

		int xofs = xfK*(tcx-cx);//jRandNP(tid) * 10;
		int yofs = xfK*(tcy-cy);//jRandNP(tid+11) * 10;
		int xo = xi + xofs;
		int yo = yi + yofs;

		float mxr = 4*(1-prog)*prog;
		//imgClr[0] = 200;
		//imgClr[1] = 200;
		//imgClr[2] = 200;

		uchar clrRand[] = {0, 0, 0};
		int clrInd = tid % nClrs;
		clrRand[0] = clrsInt[clrInd * 3];
		clrRand[1] = clrsInt[clrInd * 3+1];
		clrRand[2] = clrsInt[clrInd * 3+2];

		uchar val[] = {0, 0, 0};
		val[0] = imgClr[0];
		val[1] = imgClr[1];
		val[2] = imgClr[2];

		float clrMix = smoothLaunch(0.0, 1.0, prog)*(1-big);
		mix3(imgClr, clrRand, clrMix, val);


		uchar valMixed[] = {0, 0, 0};
		// TODO: This is from xi,yi; should be xo,yo, no?
		mix3(prevVal, val, mxr, valMixed);

		setLevCell(0, xo, yo, xres, yres, valMixed, outsAll);
		setImgLevCell(0, lev, xo, yo, xres, yres, val, outsPerLev);
	}
}


__kernel void renFromTid(
			int xres,
			int yres,
			int nTids,
			int nClrs,
			int lev,
			float levThresh,
			__global int* _tidPosGrid,
			__global int* tids,
			__global int* atrBbx,
			__global uchar* clrsInt,
			__global uchar* srcImg,
			__global uchar* sidPostThisAr,
			__global uchar* sidPostALLPrev,
			__global uchar* sidPostALL,
			__global uchar* outsPerLev,
			__global uchar* outsAllPrev,
			__global uchar* outsAll)
{
	int xi = get_global_id(0);
	int yi = get_global_id(1);

	uchar val[] = {0, 0, 0};


	uchar prevVal[] = {0, 0, 0};
	getArrayCell(xi, yi, xres, yres, outsAllPrev, prevVal);

	setLevCell(0, xi, yi, xres, yres, prevVal, outsAll);
	setImgLevCell(0, lev, xi, yi, xres, yres, val, outsPerLev);

	// Make sure you've coloured the entire background before proceding.
	barrier(CLK_GLOBAL_MEM_FENCE);

	uchar imgClr[3];
	getImageCell(xi, yi, xres, yres, srcImg, imgClr);

	//getImageCell(xi, yi, xres, yres, srcImg, imgClr);
	//setArrayCell(xi, yi, xres, yres, imgClr, sidPostALL);


	int tidPos = getCellScalar(xi, yi, yres, _tidPosGrid);

	bool safeMode = 1;
	
	if (safeMode) {
		//int nTids = 11;
		int tidPosToCheck;
		for (tidPosToCheck = 0; tidPosToCheck < nTids; tidPosToCheck++) {
			if (tidPosToCheck == tidPos) {
				renTidPos(
					xi,
					yi,
					tidPos,
					imgClr,
					prevVal,
					xres,
					yres,
					nClrs,
					lev,
					levThresh,
					_tidPosGrid,
					tids,
					atrBbx,
					clrsInt,
					srcImg,
					sidPostThisAr,
					sidPostALLPrev,
					sidPostALL,
					outsPerLev,
					outsAllPrev,
					outsAll);
				int dud = 0;
			}
			barrier(CLK_LOCAL_MEM_FENCE);
		}
	} else {
		renTidPos(
			xi,
			yi,
			tidPos,
			imgClr,
			prevVal,
			xres,
			yres,
			nClrs,
			lev,
			levThresh,
			_tidPosGrid,
			tids,
			atrBbx,
			clrsInt,
			srcImg,
			sidPostThisAr,
			sidPostALLPrev,
			sidPostALL,
			outsPerLev,
			outsAllPrev,
			outsAll);
	}

	
	/*

	AOV experiments
	float xr = (float)xi/xres;
	float yr = (float)yi/yres;
	
	val[0] = 0;
	val[1] = 255;
	val[2] = xr < levThresh ? 0 : 255;
	setLevCell(1, xi, yi, xres, yres, val, outsPerLev);
	
	val[0] = 199;//yr < .5*levThresh ? 0 : 255;
	val[1] = 199;//0;
	val[2] = 0;//255;
	setLevCell(2, xi, yi, xres, yres, val, outsPerLev);
	
	
	val[0] = 0;
	val[1] = 199;//yr > levThresh ? 0 : 255;
	val[2] = 0;//255;
	setLevCell(1, xi, yi, xres, yres, val, outsAll);
	
	val[0] = 0;
	val[1] = 0;//yr > levThresh ? 0 : 255;
	val[2] = 199;//255;
	setLevCell(2, xi, yi, xres, yres, val, outsAll);
	*/
	
}
