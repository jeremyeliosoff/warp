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
  int over,
  int* val,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y) * 3;
		if (over == 1) {
			ret[i] = mixF(ret[i], val[0], alpha);
			ret[i+1] = mixF(ret[i+1], val[1], alpha);
			ret[i+2] = mixF(ret[i+2], val[2], alpha);
		} else { // TODO make this work, impliment alpha!!
			ret[i] = mixF(ret[i], val[0], alpha);
			ret[i+1] = mixF(ret[i+1], val[1], alpha);
			ret[i+2] = mixF(ret[i+2], val[2], alpha);
		}
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
			int nTids,
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
			int style0x1y2rad,
			int radiateTime,
			int edgeThick,
			int bgMode,
			int fr,


			int* inhFrames,
			int* exhFrames,
			int* brFrames,
			float* cInOutVals,
			int* srcImg,
			//int* tidImg,
			int* tidPosGridThisLev,
			int* tids,
			int* bbxs,
			float* xfs,
			float* isBulbs,
			int* tidTrips,
			int* aovRipImg,
			int* alphaBoost, // TODO remove this, not used!!
			int* shadedImg,
			int* shadedImgXf)
{


	int tidPos = -1;
	int outClr[3];
	float szRel[2] = {0, 0};
	float xfx = 0;
	float xfy = 0;

	// Darken far from Center
	int cx = centX*xres;	
	int cy = centY*yres;	
	float dNorm;
	//int style0x1y2rad = 1;
	if (style0x1y2rad == 0) {
		dNorm = ((float)abs(x-cx))/xres;
		dNorm /= centX < .5 ? 1 - centX : centX;
	} else if (style0x1y2rad == 1) {
		dNorm = ((float)abs(y-cy))/yres;
		dNorm /= centY < .5 ? 1 - centY : centY;
	} else {
		float farCornerX = centX > .5 ? 0 : 1;
		float farCornerY = centY > .5 ? 0 : 1;
		float cornerToCent = g_dist(farCornerX, farCornerY, cx, cy);
		float dFromCent = g_dist(x, y, cx, cy);
		dNorm = dFromCent/cornerToCent;
	}
	dNorm = (float)jSmoothstep(0.0, 1.0, dNorm); // Needed?

	float isBulb = 0;
	int bordTotalBulb = 0;
	int inBorderBulb = 0;
	int inBorder = 0;

	if (bgMode == 1) {
		assignIS(50, 50, 50, outClr);
	} else {
		tidPos = getCellScalar(x, y, yres+1, tidPosGridThisLev);

		int bordNxNyPxPy[4];
		int bordTotal = 0;
		isBulb = isBulbs[tidPos];
		
		bordTotal = getBorders(1, x, y, xres, yres+1, tidPos, tidPosGridThisLev, bordNxNyPxPy);
		bordTotalBulb = getBorders(2, x, y, xres, yres+1, tidPos, tidPosGridThisLev, bordNxNyPxPy);
		
		//if (isBulb > .5)
			//bordTotal += bordTotalBulb * isBulb;

		int sz[2];
		int sidCent[2];
		getBbxInfo(tidPos, bbxs, sz, sidCent);

		// Get src colour from image.
		int srcClr[3];
		xfx = xfs[tidPos*2];
		xfy = xfs[tidPos*2+1];
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
		float kLevPct = 1;//mixF(1, levPctK, tripGlobF*levKmix); THIS IS NOW DONE WITH ALPHA

		float tripK = 2;
		float tripKmult = mixF(1, tripK, tripGlobF);

		// Darken bigger
		szRel[0] = (float)sz[0]/xres;
		szRel[1] = (float)sz[1]/yres;

		float rels = szRel[0] * szRel[1];
		float relsMod = rels*rels;
		relsMod *= relsMod;
		float bigKmult = mixF(1.0, clrKBig, MIN(1.0, relsMod));

		float vignK = 1-dNorm;
		vignK = 1-(1-vignK)*(1-vignK);
		float vignKmult = mixF(1, vignK, tripGlobF);
		vignKmult = 1;// mixF(vignKmult, 1, levPct); NOW DONE WITH ALPHA



		inBorder = bordTotal > 0;
		inBorderBulb = bordTotalBulb > 0;
		
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
		//mult3sc(tidClr, levPct, tidClr);  // Darken the blended clr by level.
		//if (doPrint == 1) printf("\n srcClr=%i,%i,%i, trippedClr=%i, %i, %i", srcClr[0], srcClr[1], srcClr[2], trippedClr[0], trippedClr[1], trippedClr[2]);
		//if (doPrint == 1) printf("\nlevPct=%f", levPct);
		mix3I(trippedClr, tidClr, solidClr, trippedClr);
		//if (doPrint == 1) printf("\n LATER tid=%i, trippedClr=%i, %i, %i\n", tid, trippedClr[0], trippedClr[1], trippedClr[2]);
	 
		//assignIV(srcClr, trippedClr); // TEMP
		float intensMult = bordTotal > 0 ? 1 : .5;// + isBulb * 2;
		mult3sc(trippedClr, intensMult, trippedClr);

		//mix3I(srcClr, trippedClr, clrProg, outClr);
		assignIV(trippedClr, outClr);


		// Apply darkenings.
		mult3sc(outClr, kLevPct*tripKmult*vignKmult*bigKmult, outClr);
	}

	int nBreaths = 4;
	
	float outClrF[3];
	outClrF[0] = outClr[0];
	outClrF[1] = outClr[1];
	outClrF[2] = outClr[2];




	//float sidFarFromCent = g_dist(sidCent[0], sidCent[1], cx, cy)/cornerToCent;
	int bulbAdd = 0;
	//float hiLevSooner = 2;
	//float outerSooner = 10;
	//float brighterSooner = 0;
	//float edgeSooner = 50;


	float bulbClrIn[] = {255, 0, 0};


	int cShadedI[3];
	int cAovRip[3];


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

	if (bgMode == 0) {
		// BULB
		int cShadedIBulb[3];
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

		mix3I(cShadedI, cShadedIBulb, isBulb, cShadedI);
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

		int withBorderBulb[3]; int withBorderNoBulb[3];
		mix3I(cShadedI, cShadedIEdge, inBorderBulb*tripGlobF, withBorderBulb);
		mix3I(cShadedI, cShadedIEdge, inBorder*tripGlobF, withBorderNoBulb);
		mix3I(withBorderNoBulb, withBorderBulb, isBulb, cShadedI);
	}
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
	int xWxf = x;
	int yWxf = y;
	float alpha = 1;
	if (bgMode == 0) {	
		float sfFdIn = .2;
		float sfFdOut = .3;
		alpha = jSmoothstep(0, sfFdIn, levProg);
		alpha *= 1.0-jSmoothstep(1-sfFdOut, 1, levProg); // TODO should be tidProg?
		alpha *= levPct;
		xWxf += xfx;
		yWxf += xfy;
	}



	/* DEBUG
	int red[3] = {255, 0, 0};
	int green[3] = {0, 255, 0};
	int blue[3] = {0, 0, 255};
	int yellow[3] = {255, 255, 0};
	int cyan[3] = {0, 255, 255};
	int magenta[3] = {255, 0, 255};

	int ind = tid % 7;

	if (ind == 0) assignIV(red, cShadedI);
	else if (ind == 1) assignIV(green, cShadedI); 
	else if (ind == 1) assignIV(blue, cShadedI); 
	else if (ind == 1) assignIV(yellow, cShadedI); 
	else if (ind == 1) assignIV(cyan, cShadedI); 
	else if (ind == 1) assignIV(magenta, cShadedI); 
	else  assignIV(grey, cShadedI); 
	*/


	
	if (bgMode == 1 || tidPos > 0 && xWxf >= 0 && yWxf >= 0 && xWxf < xres && yWxf < yres) {
		//setArrayCellShd(xWxf, yWxf, xres, yres+1, cShadedI, shadedImgXf);
		float underThresh = .2; // Surfs whos len + wid > underThresh are comped under.
		int over =  szRel[0] + szRel[1] < underThresh ? 1 : 0; // TODO make this work, impliment alpha!!
		compArrayCellShd(xWxf, yWxf, xres, yres+1, alpha, over, cShadedI, shadedImgXf);
	}
	setArrayCellShd(x, y, xres, yres+1, cAovRip, aovRipImg);
	/*
	*/
}

void calcXfC(
	int fr,
	int xres,
	int yres,
	float moveUseAsBiggest,
	float moveBiggestPow,
	float moveKForBiggest,
	float centX,
	float centY,
	float moveRippleSpeed,
	float moveK,
	float moveKofs,
	int style0x1y2rad,
	int* bbx,
	float tidProg,
	float* xfx,
	float* xfy
) {
	int szx = bbx[2] - bbx[0];
	int szy = bbx[3] - bbx[1];
	float szRel = ((float)szx)/((float)xres) * ((float)szy)/((float)yres);

	float relsPostSmooth = jSmoothstep(0, moveUseAsBiggest, szRel);
	relsPostSmooth = pow(relsPostSmooth, moveBiggestPow);// Is pow ok in C?
	float moveKBig = mixF(1.0, moveKForBiggest, relsPostSmooth);

	int tCentx = (bbx[0] + bbx[2])/2;
	int tCenty = (bbx[1] + bbx[3])/2;

	int dFromCentX = tCentx - centX*xres;
	int dFromCentY = tCenty - centY*yres;

	float k = tidProg*moveKBig*moveK*moveKofs; //moveKProg not needed post-cig

	*xfx = dFromCentX*k;
	*xfy = dFromCentY*k;
	
	if (style0x1y2rad == 0) {
		*xfy = 0;
	} else if (style0x1y2rad == 1) {
		*xfx = 0;
	}
}

void shadeImgGrid(
			int xres,
			int yres,
			int lev,
			int nTids,
			float levProg,
			float levPct,
			float tripGlobF,
			float clrKBig,
			float kRip,
			float moveK,
			float moveUseAsBiggest,
			float moveBiggestPow,
			float moveKForBiggest,
			float moveRippleSpeed,
			float moveKofs,
			float centX,
			float centY,
			float satClr,
			float multClr,
			float solidClr,
			int style0x1y2rad,
			int leftToRight,
			int topToBottom,
			int radiateTime,
			int edgeThick,
			int bgMode,
			int fr,
			int* inhFrames,
			int* exhFrames,
			int* brFrames,
			float* cInOutVals,
			int* srcImg,
			//int* tidImg,
			int* tidPosGridThisLev,
			int* tids,
			int* bbxs,
			float* xfs,
			float* isBulbs,
			int* tidTrips,
			int* aovRipImg,
			int* alphaBoost,
			int* shadedImg, // TODO remove this
			int* shadedImgXf)
{
	int x, y;

	int fromTop = 0;
	int fromLeft = 0;

	//int lenTest = 10;
	float xfsCalc[nTids*2];

	for (int tidPos = 0; tidPos < nTids; tidPos++ ) {
		float xfx = 0;
		float xfy = 0;
		int bbx[4];
		for (int bbxInd = 0; bbxInd < 4; bbxInd++) {
			bbx[bbxInd] = bbxs[tidPos*4 + bbxInd];
		}

		//float tidProg = .5; // FIX
		float tidProg = tidTrips[tidPos]/100.0;

		calcXfC(
			fr,
			xres,
			yres,
			moveUseAsBiggest,
			moveBiggestPow,
			moveKForBiggest,
			centX,
			centY,
			moveRippleSpeed,
			moveK,
			moveKofs,
			style0x1y2rad,
			bbx,
			tidProg,
			&xfx,
			&xfy);
		xfsCalc[tidPos*2] = xfx;
		xfsCalc[tidPos*2+1] = xfy;
	}


	for (x = 0; x < xres; x++ ) {
		//if (x % 100 == 0) printf("\n satClr=%f, multClr=%f, solidClr=%f", satClr, multClr, solidClr);
		for (y = 0; y < yres; y++ ) {
			int yToUse = topToBottom == 1 ? y : yres - y -1;
			int xToUse = leftToRight == 1 ? x : xres - x -1;
			krShadeImg(
				// Const
				xToUse,
				yToUse,
				xres,
				yres,

				// attrs
				lev,
				nTids,
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
				style0x1y2rad,
				radiateTime,
				edgeThick,

				bgMode,
				fr,


				inhFrames,
				exhFrames,
				brFrames,
				cInOutVals,
				srcImg,
				//tidImg,
				tidPosGridThisLev,
				tids,
				bbxs,
				//xfs,
				xfsCalc,
				isBulbs,
				tidTrips,
				aovRipImg,
				alphaBoost,
				shadedImg,
				shadedImgXf);
		}
	}
}
