
void convertTidToClr(int tid, uchar* ret) {
	if (tid < 0) {
		ret[0] = 0; ret[1] = 0; ret[2] = 0;
	} else {
		if (tid == 0)
			tid = 21111;// Get rid of white, it doesn't tint nicely.

		int octant = tid%8;
		int tDiv = tid/8;
		int ocR = tDiv % 128 + 128*(octant % 2);
		tDiv = tDiv/128;
		int ocG = tDiv % 128 + 128*(octant/2 % 2);
		tDiv = tDiv/128;
		int ocB = tDiv % 128 + 128*(octant/4 % 2); // This should never loop - till we get to tid = 256^3
		ret[0] = 255-ocR; ret[1] = 255-ocG; ret[2] = 255-ocB;
	}
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

//void mix3i(int* a, int* b, float m, uchar* ret) {
//	int i;
//	for (i = 0; i < 3; i++) {
//		ret[i] = mixI(a[i], b[i], m);
//	}
//}

float dist(float x0, float y0, float x1, float y1) {
	float dx = x1-x0;
	float dy = y1-y0;
	return sqrt(dx*dx + dy*dy);
}

void mult3_255(uchar* a, uchar* b, uchar* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (uchar) (a[i]*((float)b[i])/255);
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
  __global uchar* img,
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


void assign(
	uchar* src,
	uchar* dst)
{
	dst[0] = src[0];
	dst[1] = src[1];
	dst[2] = src[2];
}

void setArrayCell(int x, int y, int xres, int yres,
  uchar* val,
  __global uchar* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}

int getCellScalar(int x, int y, int yres,
  __global int* tidPosGridThisLev)
{
	int i = x * yres + y;
	return tidPosGridThisLev[i];
}

void getBbxInfo(int tidPos,
		__global int* bbxs,
		int* sz, int* cent) {
	int ofs = tidPos*4;
	int mn[2];
	int mx[2];
	mn[0] = bbxs[ofs];
	mn[1] = bbxs[ofs+1];
	mx[0] = bbxs[ofs+2];
	mx[1] = bbxs[ofs+3];
	sz[0] = mx[0]-mn[0];
	sz[1] = mx[1]-mn[1];
	cent[0] = (mn[0] + mx[0])/2;
	cent[1] = (mn[1] + mx[1])/2;
}

__kernel void krShadeImg(
			int xres,
			int yres,
			int levPct,
			int tripGlobPct,
			float clrKBig,
			__global int* cIn,
			__global int* cOut,
			__global uchar* srcImg,
			__global uchar* tidImg,
			__global int* tidPosGridThisLev,
			__global int* tids,
			__global int* bbxs,
			__global int* tidTrips,
			//__global int* cents,
			__global uchar* shadedImg)
{
	unsigned int x = get_global_id(0);
	unsigned int y = get_global_id(1);

	int tidPos = getCellScalar(x, y, yres+1, tidPosGridThisLev);

	int sz[2];
	int cent[2];
	getBbxInfo(tidPos, bbxs, sz, cent);


	uchar srcClr[3];
	getImageCell(x, y, xres, yres+1, srcImg, srcClr);

	int tid = tids[tidPos];
	uchar tidClr[] = {0, 0, 0};
	convertTidToClr(tid, tidClr);

	
	float tripGlobF = tripGlobPct*.01;
	float tidTrip = ((float)tidTrips[tidPos])/100;
	float clrProg = tripGlobF;//tidTrip;//smoothstep(0, .3, tidTrip);

	// Vary colour from inner to outer
	int cx = xres/2;	
	int cy = yres/2;	
	float dFromCent = dist(x, y, cx, cy);
	//float dFromCent = dist(cent[0], cent[1], cx, cy);
	float dNorm = dFromCent/cx;
	dNorm = (float)smoothstep(0.0, 1.0, dNorm);
	uchar inOutClr[3];
	// Sad, sad workaround for matching types.
	uchar a[3] = {cIn[0], cIn[1], cIn[2]};
	uchar b[3] = {cOut[0], cOut[1], cOut[2]};
	mix3(a, b, dNorm, inOutClr);
	float mixInOut = 1;
	uchar tripClr[3];

	// Mult inOutClr by tripClr
	mult3_255(inOutClr, tidClr, inOutClr);
	//mult3sc(inOutClr, 2, inOutClr);
	//mix3(tidClr, inOutClr, clrProg*mixInOut, tripClr);
	mix3(tidClr, inOutClr, 1, tripClr);

	uchar trippedClr[3];
	mult3_255(srcClr, tripClr, trippedClr);
 
	mult3sc(trippedClr, 2, trippedClr);


	uchar outClr[3];
	mix3(srcClr, trippedClr, clrProg, outClr);
	//assign(inOutClr, outClr);

	// Darken lower level when tripping.
	float levPctF = levPct*.01;
	float levPctK = 1.0-(1.0-levPctF)*(1.0-levPctF);
	float levKmix = .2;
	float kLevPct = mix(1, levPctK, tripGlobF*levKmix);

	float tripK = 1.2;
	float tripKmult = mix(1, tripK, tripGlobF);

	// Darken bigger
	float rels = ((float)sz[0]/xres) * ((float)sz[1]/yres);
	float relsMod = rels*rels;
	relsMod *= relsMod;
	float bigKmult = mix(1.0, clrKBig, min(1.0, relsMod));

	float vignK = 1-dNorm;
	vignK = 1-(1-vignK)*(1-vignK);
	float vignKmult = mix(1, vignK, tripGlobF);
	vignKmult = mix(vignKmult, 1, levPctF);

	mult3sc(outClr, kLevPct*tripKmult*vignKmult*bigKmult, outClr);
	

	// DEBUG
	// assign(tidClr, outClr);
	// yres+1 from trial+error.
	setArrayCell(x, y, xres, yres+1, outClr, shadedImg);
}
