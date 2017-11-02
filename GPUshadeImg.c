
void convertTidToClr(int tid, int* ret) {
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

float mixI(int a, int b, float m) {
	return m*b + (1.0-m)*a;
}

void mix3(int* a, int* b, float m, int* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixI(a[i], b[i], m);
	}
}

//void mix3i(int* a, int* b, float m, int* ret) {
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

void mult3_255(int* a, int* b, int* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (int) (a[i]*((float)b[i])/255);
	}
}

void mult3sc(int* a, float k, int* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (int) min((int)255, (int)(a[i]*k));
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

void getImageCell(int x, int y, int xres, int yres,
  __global int* img,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		//int i = (y * xres + x) * 3;
		int i = (x * yres + y) * 3;
		ret[0] = img[i];
		ret[1] = img[i+1];
		ret[2] = img[i+2];
	}
}


void assign(
	int* src,
	int* dst)
{
	dst[0] = src[0];
	dst[1] = src[1];
	dst[2] = src[2];
}

void setArrayCell(int x, int y, int xres, int yres,
  int* val,
  __global int* ret)
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

int getBorders(int x, int y, int xres, int yres, int thisTidPos,
  __global int* tidPosGridThisLev,
  int* bordNxNyPxPy)
{

	
	int bordIndex;
	for (bordIndex=0; bordIndex<4; bordIndex++) {
		int xx;
		int yy;
		if (bordIndex < 2) {
			xx = x-1 + 2*bordIndex;
			yy = y;
		} else {
			xx = x;
			yy = y-1 + 2*(bordIndex-2);
		}
		int i = xx * yres + yy;
		if (xx < 0 || yy < 0 ||
			xx > xres-1 || yy > yres-1 ||
			thisTidPos != tidPosGridThisLev[i]) {
			bordNxNyPxPy[bordIndex] = 1;
		} else {
			bordNxNyPxPy[bordIndex] = 0;
		}
		
	}
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

void filterImg  (int x, int y, int xres, int yres,
	float xfx,
	float xfy,
	__global int* img,
	int* bordNxNyPxPy,
	int* ret) {

	int i;
	for (i=0; i<3; i++) {
		ret[i] = 0;
	}	

	float xOfs = xfx - floor(xfx);//fmod(xfx, 1.0);
	float yOfs = xfy - floor(xfy);//fmod(xfy, 1.0);
	//float xOfs = fmod(xfx, 1.0);
	//float yOfs = fmod(xfy, 1.0);

	int xx;
	int yy;

	if (x > xres-1 || y > yres -1) {
			getImageCell(x, y, xres, yres+1, img, ret);
	} else {
		for (xx=0; xx<2; xx++) {
			for (yy=0; yy<2; yy++) {

				int srcClrSamp[3];
				getImageCell(x+xx, y+yy, xres, yres+1, img, srcClrSamp);

				float wx = xx == 0 ? xOfs : 1.0-xOfs;
				float wy = yy == 0 ? yOfs : 1.0-yOfs;

				float alpha = 1;
				if (bordNxNyPxPy[0] == 1) alpha *= 1.0-xOfs;
				if (bordNxNyPxPy[1] == 1) alpha *= 1.0-yOfs;
				if (bordNxNyPxPy[2] == 1) alpha *= xOfs;
				if (bordNxNyPxPy[3] == 1) alpha *= yOfs;

				for (i=0; i<3; i++) {
					ret[i] += srcClrSamp[i]*(wx*wy);// *alpha;  TODO: implement alpha
				}

				//ret[0] = 255*xOfs; ret[1] = 255*yOfs; ret[2] = 50;
				
				//if (wx < 0 || wy < 0) {
				if (0==1 && (bordNxNyPxPy[0] == 1 || 
					bordNxNyPxPy[1] == 1 || 
					bordNxNyPxPy[2] == 1 || 
					bordNxNyPxPy[3] == 1)) {
					ret[0] = 255;
					ret[1] = 0;
					ret[2] = 0;
				}
				if (xOfs < 0) {
					ret[0] = 0;
					ret[1] = 255;
					ret[2] = 0;
				}


			}
		}
	}
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
			__global float* xfs,
			__global int* tidTrips,
			//__global int* cents,
			__global uchar* shadedImg)
{
	unsigned int x = get_global_id(0);
	unsigned int y = get_global_id(1);


	int tidPos = getCellScalar(x, y, yres+1, tidPosGridThisLev);

	int bordNxNyPxPy[4];
	getBorders(x, y, xres, yres+1, tidPos, tidPosGridThisLev, bordNxNyPxPy);

	int sz[2];
	int cent[2];
	getBbxInfo(tidPos, bbxs, sz, cent);


	int srcClr[3];
	//USEFILT float xfx = xfs[tidPos*2]; float xfy = xfs[tidPos*2+1]; filterImg(x, y, xres, yres, xfx, xfy, srcImg, bordNxNyPxPy, srcClr);
	/*NOUSEFILT*/getImageCell(x, y, xres, yres+1, srcImg, srcClr);

	int tid = tids[tidPos];
	int tidClr[] = {0, 0, 0};
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
	int inOutClr[3];
	// Sad, sad workaround for matching types.
	int a[3] = {cIn[0], cIn[1], cIn[2]};
	int b[3] = {cOut[0], cOut[1], cOut[2]};
	mix3(a, b, dNorm, inOutClr);
	float mixInOut = 1;
	int tripClr[3];

	// Mult inOutClr by tripClr
	mult3_255(inOutClr, tidClr, inOutClr);
	//mult3sc(inOutClr, 2, inOutClr);
	//mix3(tidClr, inOutClr, clrProg*mixInOut, tripClr);
	mix3(tidClr, inOutClr, 1, tripClr);

	int trippedClr[3];
	mult3_255(srcClr, tripClr, trippedClr);
 
	mult3sc(trippedClr, 2, trippedClr);


	int outClr[3];
	mix3(srcClr, trippedClr, clrProg, outClr);
	//assign(inOutClr, outClr);

	// Darken lower level when tripping.
	float levPctF = levPct*.01;
	float levPctK = 1.0-(1.0-levPctF)*(1.0-levPctF);
	float levKmix = .2;
	float kLevPct = mix(1, levPctK, tripGlobF*levKmix);

	float tripK = 2;
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
	//setArrayCell(x, y, xres, yres+1, srcClr, shadedImg);
}
