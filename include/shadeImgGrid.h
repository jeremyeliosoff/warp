//#include "include/cCommon.h"
//JINCLUDE include/cCommon.h

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

//void mix3i(int* a, int* b, float m, int* ret) {
//	int i;
//	for (i = 0; i < 3; i++) {
//		ret[i] = mixI(a[i], b[i], m);
//	}
//}

float g_dist(float x0, float y0, float x1, float y1) {
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
		ret[i] = (int) MIN((int)255, (int)(a[i]*k));
	}
}

float jRand(int seed) {
	return ((seed + 11)*(seed + 1321) % 1000)/1000.0;
}


void getImageCell(int x, int y, int xres, int yres,
  int* img,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		//int i = (y * xres + x) * 3;
		int i = (y * xres + x) * 3;
		ret[0] = img[i];
		ret[1] = img[i+1];
		ret[2] = img[i+2];
	}
}



void fToI3(float* vf, int *vi) {
	for (int i=0; i < 3; i ++) {
		vi[i] = (int) vf[i];
	}
}

void iToF3(int* vi, float *vf) {
	for (int i=0; i < 3; i ++) {
		vf[i] = (float) vi[i]/255;
	}
}

void iToF3g(int* vi, float *vf) {
	for (int i=0; i < 3; i ++) {
		vf[i] = (float) vi[i]/255;
	}
}


void setArrayCellShd(int x, int y, int xres, int yres,
  int* val,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[i] = val[0];
		ret[i+1] = val[1];
		ret[i+2] = val[2];
	}
}

void compArrayCellShd(int x, int y, int xres, int yres,
  float alpha,
  int* val,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		ret[i] = mixF(ret[i], val[0], alpha);
		ret[i+1] = mixF(ret[i+1], val[1], alpha);
		ret[i+2] = mixF(ret[i+2], val[2], alpha);
	}
}

int getCellScalar(int x, int y, int yres,
  int* tidPosGridThisLev)
{
	int i = x * yres + y;
	return tidPosGridThisLev[i];
}

int getBorders(int edgeThick, int x, int y, int xres, int yres, int thisTidPos,
  int* tidPosGridThisLev,
  int* bordNxNyPxPy)
{
	int bordTotal = 0;	
	for (int xx=-edgeThick; xx<=edgeThick; xx++) {
		for (int yy=-edgeThick; yy<=edgeThick; yy++) {

			int xxx = x + xx;
			int yyy = y + yy;
			int i = xxx * yres + yyy;

			if (xxx == x && yyy == y) {  // WITHOUT THIS BIG D SEG-FAULTS!!!
				continue;
			} else if (xxx < 0 || yyy < 0 ||
				xxx >= xres-1 || yyy >= yres-1 ||
				thisTidPos != tidPosGridThisLev[i]) {
				bordTotal += 1;
			}
		}
	}
	return bordTotal;
}

void getBbxInfo(int tidPos,
		int* bbxs,
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
	int* img,
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
					ret[i] += srcClrSamp[i]*(wx*wy)*1.2;// *alpha;  TODO: implement alpha
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



void krShadeImg(
			// Const
			int x,
			int y,
			int xres,
			int yres,

			// Per-obj varying attrs
			int lev,
			float levProg,
			float levPct,
			float tripGlobF,

			// Parms
			float clrKBig,
			float kRip,
			float centX,
			float centY,
			float satClr,
			float multClr,
			float solidClr,
			int radiateTime,
			int edgeThick,
			int fr,


			int* inhFrames,
			int* exhFrames,
			int* brFrames,
			float* cInOutVals,
			int* srcImg,
			int* tidImg,
			int* tidPosGridThisLev,
			int* tids,
			int* bbxs,
			float* xfs,
			float* isBulbs,
			int* tidTrips,
			int* aovRipImg,
			int* alphaBoost,
			int* shadedImg,
			int* shadedImgXf)
{

	int tidPos = getCellScalar(x, y, yres+1, tidPosGridThisLev);

	int bordNxNyPxPy[4];
	int bordTotal = 0;
	int bordTotalBulb = 0;
	float isBulb = isBulbs[tidPos];
	
	bordTotal = getBorders(1, x, y, xres, yres+1, tidPos, tidPosGridThisLev, bordNxNyPxPy);
	bordTotalBulb = getBorders(2, x, y, xres, yres+1, tidPos, tidPosGridThisLev, bordNxNyPxPy);
	
	//if (isBulb > .5)
		//bordTotal += bordTotalBulb * isBulb;

	int sz[2];
	int sidCent[2];
	getBbxInfo(tidPos, bbxs, sz, sidCent);

	// Get src colour from image.
	int srcClr[3];
	float xfx = xfs[tidPos*2];
	float xfy = xfs[tidPos*2+1];
	//filterImg(x, y, xres, yres, xfx, xfy, srcImg, bordNxNyPxPy, srcClr);
	getImageCell(x, y, xres+1, yres+1, srcImg, srcClr);

	// Get tid.
	int tid = tids[tidPos];
	int tidClr[] = {0, 0, 0};
	convertTidToClr(tid, tidClr);
	int doPrint = tidPos > -1 ? 1 : 0;
	doPrint =0;
	if (doPrint == 1) {
		printf("\n cInOutVals");
		for (int i = 0; i<(4*3*3); i ++) {
			printf("\n\t%f", cInOutVals[i]);
		}
	}
	if (doPrint == 1) printf("\n tid=%i, srcClr=%i, %i, %i, tidClr=%i, %i, %i", tid, srcClr[0], srcClr[1], srcClr[2], tidClr[0], tidClr[1], tidClr[2]);
	//if (x % 100 == 0 && y % 50 == 0) printf("\n tidPos=%i, tid=%i, tidClr=%i, %i, %i", tidPos, tid, tidClr[0], tidClr[1], tidClr[2]);
	//if (tidPos > -1) printf("\n tidPos=%i, tid=%i, tidClr=%i, %i, %i", tidPos, tid, tidClr[0], tidClr[1], tidClr[2]);

	
	// Get clrProg.
	//float tripGlobF = tripGlobPct*.01;
	float tidTrip = ((float)tidTrips[tidPos])/100;
	float clrProg = tripGlobF;//tidTrip;//smoothstep(0, .3, tidTrip);




	// Darken lower level when tripping.
	//float levPctF = levPct*.01;
	float levPctK = 1.0-(1.0-levPct)*(1.0-levPct);
	float levKmix = .2;
	float kLevPct = mixF(1, levPctK, tripGlobF*levKmix);

	float tripK = 2;
	float tripKmult = mixF(1, tripK, tripGlobF);

	// Darken bigger
	float szRel[2] = {(float)sz[0]/xres, (float)sz[1]/yres};
	float rels = szRel[0] * szRel[1];
	float relsMod = rels*rels;
	relsMod *= relsMod;
	float bigKmult = mixF(1.0, clrKBig, MIN(1.0, relsMod));

	// Darken far from Center
	int cx = centX*xres;	
	int cy = centY*yres;	
	float dFromCent = g_dist(x, y, cx, cy);
	//float dNorm = dFromCent/cx;
	float farCornerX = centX > .5 ? 0 : 1;
	float farCornerY = centY > .5 ? 0 : 1;
	float cornerToCent = g_dist(farCornerX, farCornerY, cx, cy);
	float dNorm = dFromCent/cornerToCent;
	dNorm = (float)jSmoothstep(0.0, 1.0, dNorm);
	float vignK = 1-dNorm;
	vignK = 1-(1-vignK)*(1-vignK);
	float vignKmult = mixF(1, vignK, tripGlobF);
	vignKmult = mixF(vignKmult, 1, levPct);



	int inBorder = bordTotal > 0;
	int inBorderBulb = bordTotalBulb > 0;
	
	// If this is a bulb, but your in the bulb border, turn off
	// bulb here, and use bordTotalBulb as bordTotal.
	if (inBorderBulb && isBulb > 0) {
		isBulb = 0;
		bordTotal = bordTotalBulb;
	}


	// Get trippedClr = srcClr * tidClr * brightening
	int multedClr[3], trippedClr[3];
	int grey[] = {200, 200, 200};
	//if (doPrint == 1) printf("\nPREtid=%i, tidClr=%i, %i, %i", tid, tidClr[0], tidClr[1], tidClr[2]);
	mix3I(grey, tidClr, satClr, tidClr);
	//if (doPrint == 1) printf("\nPOStid=%i, tidClr=%i, %i, %i", tid, tidClr[0], tidClr[1], tidClr[2]);
	mult3_255(srcClr, tidClr, multedClr);

	mix3I(srcClr, multedClr, multClr, trippedClr);
	mult3sc(tidClr, levPct, tidClr);  // Darken the blended clr by level.
	//if (doPrint == 1) printf("\n srcClr=%i,%i,%i, trippedClr=%i, %i, %i", srcClr[0], srcClr[1], srcClr[2], trippedClr[0], trippedClr[1], trippedClr[2]);
	//if (doPrint == 1) printf("\nlevPct=%f", levPct);
	mix3I(trippedClr, tidClr, solidClr, trippedClr);
	//if (doPrint == 1) printf("\n LATER tid=%i, trippedClr=%i, %i, %i\n", tid, trippedClr[0], trippedClr[1], trippedClr[2]);
 
	//assignIV(srcClr, trippedClr); // TEMP
	float intensMult = bordTotal > 0 ? 1 : .5;// + isBulb * 2;
	mult3sc(trippedClr, intensMult, trippedClr);

	int outClr[3];
	//mix3I(srcClr, trippedClr, clrProg, outClr);
	assignIV(trippedClr, outClr);


	// Apply darkenings.
	mult3sc(outClr, kLevPct*tripKmult*vignKmult*bigKmult, outClr);


	int nBreaths = 4;
	
	float outClrF[3];
	outClrF[0] = outClr[0];
	outClrF[1] = outClr[1];
	outClrF[2] = outClr[2];


	float lum = ((float)(srcClr[0] + srcClr[1] + srcClr[2]))/(255*3);
	float lumFromLevPct = MAX(0, lum - levPct);


	//float sidFarFromCent = g_dist(sidCent[0], sidCent[1], cx, cy)/cornerToCent;
	int bulbAdd = 0;
	//float hiLevSooner = 2;
	//float outerSooner = 10;
	//float brighterSooner = 0;
	//float edgeSooner = 50;

	//fr += isBulb * bulbAdd + hiLevSooner * lev + (1-sidFarFromCent) *
	//	outerSooner + brighterSooner*lumFromLevPct + edgeSooner * bordTotal * tripGlobF;

	float bulbClrIn[] = {255, 0, 0};


	int cShadedI[3];
	int cShadedIBulb[3];
	int cAovRip[3];
	getCspacePvNxInOut (
		fr+bulbAdd,
		x,
		radiateTime,
		//outClrF, 
		bulbClrIn, 
		cInOutVals,
		inhFrames,
		exhFrames,
		brFrames,
		nBreaths,
		dNorm,
		kRip,
		cAovRip,
		cShadedIBulb
		);


	float maxComp = 0;
	float cShadedIBulbF[3];

	for (int i = 0; i < 3; i++) {
		cShadedIBulbF[i] = MAX(0, 1.0-((float)cShadedIBulb[i])/255.0);
		maxComp = MAX(maxComp, cShadedIBulbF[i]);
	}
	for (int i = 0; i < 3; i++) {
		cShadedIBulbF[i] = cShadedIBulbF[i]/maxComp;
	}

	for (int i = 0; i < 3; i++) {
		cShadedIBulb[i] = (int)(cShadedIBulbF[i]*255.0f);
	}


	int borderAdd = 500;
	int cShadedIEdge[3];
	getCspacePvNxInOut (
		fr + borderAdd,
		x,
		radiateTime,
		outClrF, 
		cInOutVals,
		inhFrames,
		exhFrames,
		brFrames,
		nBreaths,
		dNorm,
		kRip,
		cAovRip,
		cShadedIEdge
		);


	getCspacePvNxInOut (
		fr,
		x,
		radiateTime,
		outClrF, 
		cInOutVals,
		inhFrames,
		exhFrames,
		brFrames,
		nBreaths,
		dNorm,
		kRip,
		cAovRip,
		cShadedI
		);


	//float segClr[3] = {1, .95, .8};
	//float segClr[3] = {255, 225, 155};
	//int bulbClr[3] = {0, 255, 0};
	//int notBulbClr[3] = {255, 0, 0};
	mix3I(cShadedI, cShadedIBulb, isBulb, cShadedI);
	int withBorderBulb[3]; int withBorderNoBulb[3];
	mix3I(cShadedI, cShadedIEdge, inBorderBulb*tripGlobF, withBorderBulb);
	mix3I(cShadedI, cShadedIEdge, inBorder*tripGlobF, withBorderNoBulb);
	mix3I(withBorderNoBulb, withBorderBulb, isBulb, cShadedI);
	//assignIV(srcClr, cShadedI);
	//mix3I(notBulbClr, bulbClr, isBulb, cShadedI);
		//mix3I(notBulbClr, bulbClr, isBulb, cShadedI);
		//float toAdd[3];
		//vSMult(outClrF, isBulb*10, toAdd);
		//vSMult(outClrF, isBulb*10, toAdd);
		//vISMult(cShadedI, 1 + 3*isBulb, cShadedI);

		//vAdd(outClrF, toAdd, outClrF);

	//cShadedI[0] = CLAMP((int) outClrF[0], 0, 255);
	//cShadedI[1] = CLAMP((int) outClrF[1], 0, 255);
	//cShadedI[2] = CLAMP((int) outClrF[2], 0, 255);

	cShadedI[0] = CLAMP(cShadedI[0], 0, 255);
	cShadedI[1] = CLAMP(cShadedI[1], 0, 255);
	cShadedI[2] = CLAMP(cShadedI[2], 0, 255);

	//ALWAYS FULLY MIX cSpace dIlr, don't -> mix3I(srcClr, cShadedI, clrProg, cShadedI);

	//int green[3] = {0, 255, 0};
	//assignIV(green, cShadedI);
	//if (bordTotal == 0) { // TEMP!

	//}
	//if (isBulb) {
		//assignIS (255*(1-isBulb), isBulb*255, 0, cShadedI);
	//} else {
		//assignIS (255, 0, 0, cShadedI);
	//}

	//assignIV(tidClr, cShadedI);
	//assignIV(green, cShadedI);

	//int xc = ((float)x/xres) * 255;
	//int yc = ((float)y/yres) * 255;
	//assignIS(xc, yc, 200, cShadedI);

	setArrayCellShd(x, y, xres, yres+1, cShadedI, shadedImg);
	int xWxf = x + xfx;
	int yWxf = y + xfy;
	float sfFdIn = .2;
	float sfFdOut = .3;
	float alpha = jSmoothstep(0, sfFdIn, levProg);
	alpha *= 1.0-jSmoothstep(1-sfFdOut, 1, levProg); // TODO should be tidProg

	if (tidPos > 0 && xWxf >= 0 && yWxf >= 0 && xWxf < xres && yWxf < yres)
		//setArrayCellShd(xWxf, yWxf, xres, yres+1, cShadedI, shadedImgXf);
		compArrayCellShd(xWxf, yWxf, xres, yres+1, alpha, cShadedI, shadedImgXf);
	setArrayCellShd(x, y, xres, yres+1, cAovRip, aovRipImg);
	/*
	*/
}

void shadeImgGrid(
			int xres,
			int yres,
			int lev,
			float levProg,
			float levPct,
			float tripGlobF,
			float clrKBig,
			float kRip,
			float centX,
			float centY,
			float satClr,
			float multClr,
			float solidClr,
			int radiateTime,
			int edgeThick,
			int fr,
			int* inhFrames,
			int* exhFrames,
			int* brFrames,
			float* cInOutVals,
			int* srcImg,
			int* tidImg,
			int* tidPosGridThisLev,
			int* tids,
			int* bbxs,
			float* xfs,
			float* isBulbs,
			int* tidTrips,
			int* aovRipImg,
			int* alphaBoost,
			int* shadedImg,
			int* shadedImgXf)
{
	int x, y;

	for (x = 0; x < xres; x++ ) {
		//if (x % 100 == 0) printf("\n satClr=%f, multClr=%f, solidClr=%f", satClr, multClr, solidClr);
		for (y = 0; y < yres; y++ ) {
			krShadeImg(
				// Const
				x,
				y,
				xres,
				yres,

				// attrs
				lev,
				levProg,
				levPct,
				tripGlobF,

				// Parms
				clrKBig,
				kRip,
				centX,
				centY,
				satClr,
				multClr,
				solidClr,
				radiateTime,
				edgeThick,
				fr,


				inhFrames,
				exhFrames,
				brFrames,
				cInOutVals,
				srcImg,
				tidImg,
				tidPosGridThisLev,
				tids,
				bbxs,
				xfs,
				isBulbs,
				tidTrips,
				aovRipImg,
				alphaBoost,
				shadedImg,
				shadedImgXf);
		}
	}
}
