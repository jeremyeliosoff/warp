float mixI(uchar a, uchar b, float m) {
	return m*b + (1.0-m)*a;
}

void mix3(uchar* a, uchar* b, float m, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixI(a[i], b[i], m);
	}
}

void mult3_255(uchar* a, uchar* b, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (uchar) (a[i]*(float)(b[i]/255));
	}
}

void mult3sc(uchar* a, float k, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (uchar) min((int)255, (int)(a[i]*k));
	}
}

float jRand(int seed) {
	return ((seed + 11)*(seed + 1321) % 1000)/1000.0;
}

float ssmoothstep(float edge0, float edge1, float x) {
	// Scale, bias and saturate x to 0..1 range
	float ret = edge1;
	if (edge1 > edge0) {
		ret = clamp((x - edge0)/(edge1 - edge0), 0.0, 1.0); 
		//Evaluate polynomial
		ret = ret*ret*(3 - 2*ret);
	}
	return ret;
}

void getImageCell(int x, int y, int xresIn, int yresIn,
  uchar __attribute__((address_space(1)))* img,
  uchar* ret)
{
	int xres = xresIn + 0;
	int yres = yresIn + 0;
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		//int i = (y * xres + x) * 3;
		int i = (x * yres + y) * 3;
		ret[0] = img[i];
		ret[1] = img[i+1];
		ret[2] = img[i+2];
	}
}


void setArrayCell(int x, int y, int xres, int yres,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}

int getCellScalar(int x, int y, int xres, int yres,
  __global int* tidPosGridThisLev)
{
	//int i = y * xres + x;
	int i = x * yres + y;
	return tidPosGridThisLev[i];
}

void getBbxInfo(int tidPos,
		__global int* bbxs,
		int* mn, int* mx, int* cent) {
	int ofs = tidPos*4;
	mn[0] = bbxs[ofs];
	mn[1] = bbxs[ofs+1];
	mx[0] = bbxs[ofs+2];
	mx[1] = bbxs[ofs+3];
	cent[0] = (mn[0] + mx[0])/2;
	cent[1] = (mn[1] + mx[1])/2;
}

__kernel void krShadeImg(
			int xres,
			int yres,
			__global uchar* srcImg,
			__global uchar* tidImg,
			__global int* tidPosGridThisLev,
			//__global int* tids,
			__global int* bbxs,
			__global int* tidProgs,
			//__global int* cents,
			__global uchar* shadedImg)
{
	unsigned int x = get_global_id(0);
	unsigned int y = get_global_id(1);

	int xx = x;//max(0, x+2);
	int yy = y;//max(0, y+2);
	int tidPos = getCellScalar(xx, yy, xres, yres+1, tidPosGridThisLev);

	int mn[2];
	int mx[2];
	int cent[2];
	getBbxInfo(tidPos, bbxs, mn, mx, cent);


	uchar outClr[3];
	uchar srcClr[3];
	getImageCell(x, y, xres, yres+1, srcImg, srcClr);

	uchar tidClr[3];
	getImageCell(x, y, xres, yres+1, tidImg, tidClr);
	////imgClr[0] = (50*tidPos)%255;//255*((float)mx[0])/xres;
	//imgClr[2] = 0;
	////if (mn[0] == 77) 
	////if (mn[0] == 77 && tidPos == 0) // && mn[1] == 6) //&& mx[0] == 87 && mx[1] == 17)
	////if (0 && x > mn[0]) // && mn[1] == 6) //&& mx[0] == 87 && mx[1] == 17)

	outClr[0] = 100;
	outClr[1] = 100;
	outClr[2] = 100;

	if (x > mn[0]+3)
		outClr[0] = 255;
	if (y > mn[1]+3) // && mn[1] == 6) //&& mx[0] == 87 && mx[1] == 17)
		outClr[1] = 255;
	if (x > mx[0]-5)
		outClr[2] = 255;

	//if (x % 5 == 0)
	//	outClr[0] = 250;

	//if (y % 5 == 0)
	//	outClr[1] = 250;
	

	//if (tidPos == -1) {
	//	outClr[0] = 200;
	//	outClr[1] = 200;
	//	outClr[2] = 200;
	//} else {
	//	outClr[0] = 255*(tidPos%2);
	//	outClr[1] = 255*((tidPos/2)%2);
	//	outClr[2] = 255*((tidPos/4)%2);
	//}

	// yres+1 from trial + error.
	
	outClr[0] = 255*((float)cent[1])/xres;
	outClr[1] = 255-outClr[0];//y % 255;
	outClr[2] = 0;

	float tidProg = ((float)tidProgs[tidPos])/100;
	float clrProg = tidProg;//smoothstep(0, .3, tidProg);

	uchar tripClr[3];
	mult3_255(srcClr, tidClr, tripClr);
	mult3sc(tripClr, 2, tripClr);

	mix3(srcClr, tripClr, clrProg, outClr);
	


	setArrayCell(x, y, xres, yres+1, outClr, shadedImg);
}
