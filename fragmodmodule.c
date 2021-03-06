#include <Python.h>
#include "numpy/arrayobject.h"
#include "cCommon.h"
#include "initJtGrid.h"
#include "shadeImgGrid.h"
#include "setTidPosGrid.h"
#include "arrayIntToClr.h"


// Define a new exception object for our module.
static PyObject *fragmodError;


static PyObject* fragmod_shadeImgGrid(PyObject* self, PyObject* args) {
	// Const
	int xres;
	int yres;

	// Per-obj varying attrs
	int lev;
	int nTids;
	float levProg;
	float levPct;
	float tripGlobF;

	// Parms
	float clrKBig;
	float kRip;
	float moveK;
	float moveUseAsBiggest;
	float moveBiggestPow;
	float moveKForBiggest;
	float moveRippleSpeed;
	float moveKofs;
	float centX;
	float centY;
	float satClr;
	float multClr;
	float solidClr;
	int style0x1y2rad;
	int leftToRight;
	int topToBottom;
	int radiateTime;
	int edgeThick;
	int bgMode;
	int fr;


	PyArrayObject *inhFrames=NULL;
	PyArrayObject *exhFrames=NULL;
	PyArrayObject *brFrames=NULL;
	PyArrayObject *cInOutVals=NULL;
	PyArrayObject *srcImg=NULL;
	//PyArrayObject *tidImg=NULL;
	PyArrayObject *tidPosGridThisLev=NULL;
	PyArrayObject *tids=NULL;
	PyArrayObject *bbxs=NULL;
	PyArrayObject *xfs=NULL;
	PyArrayObject *isBulbs=NULL;
	PyArrayObject *tidTrips=NULL;
	PyArrayObject *aovRipImg=NULL;
	PyArrayObject *alphaBoost=NULL;
	PyArrayObject *shadedImg=NULL;
	PyArrayObject *shadedImgXf=NULL;

	// TODO: Many i's should be f's!
    if (!PyArg_ParseTuple(args, "iiiiffffffffffffffffiiiiiiiOOOOOOOOOOOOOOO",
		&xres,
		&yres,
		&lev,
		&nTids,
		&levProg,
		&levPct,
		&tripGlobF,
		&clrKBig,
		&kRip,
		&moveK,
		&moveUseAsBiggest,
		&moveBiggestPow,
		&moveKForBiggest,
		&moveRippleSpeed,
		&moveKofs,
		&centX,
		&centY,
		&satClr,
		&multClr,
		&solidClr,
		&style0x1y2rad,
		&leftToRight,
		&topToBottom,
		&radiateTime,
		&edgeThick,
		&bgMode,
		&fr,
		&inhFrames,
		&exhFrames,
		&brFrames,
		&cInOutVals,
		&srcImg,
		//&tidImg,
		&tidPosGridThisLev,
		&tids,
		&bbxs,
		&xfs,
		&isBulbs,
		&tidTrips,
		&aovRipImg,
		&alphaBoost,
		&shadedImg,
		&shadedImgXf)) return NULL;



		int *inhFramesPtr = ((int *)PyArray_GETPTR1(inhFrames,0));
		int *exhFramesPtr = ((int *)PyArray_GETPTR1(exhFrames,0));
		int *brFramesPtr = ((int *)PyArray_GETPTR1(brFrames,0));
		float *cInOutValsPtr = ((float *)PyArray_GETPTR1(cInOutVals,0));
		int *srcImgPtr = ((int *)PyArray_GETPTR1(srcImg,0));
		//int *tidImgPtr = ((int *)PyArray_GETPTR1(tidImg,0));
		int *tidPosGridThisLevPtr = ((int *)PyArray_GETPTR1(tidPosGridThisLev,0));
		int *tidsPtr = ((int *)PyArray_GETPTR1(tids,0));
		int *bbxsPtr = ((int *)PyArray_GETPTR1(bbxs,0));
		float *xfsPtr = ((float *)PyArray_GETPTR1(xfs,0));
		float *isBulbsPtr = ((float *)PyArray_GETPTR1(isBulbs,0));
		int *tidTripsPtr = ((int *)PyArray_GETPTR1(tidTrips,0));
		int *aovRipImgPtr = ((int *)PyArray_GETPTR1(aovRipImg,0));
		int *alphaBoostPtr = ((int *)PyArray_GETPTR1(alphaBoost,0));
		int *shadedImgPtr = ((int *)PyArray_GETPTR1(shadedImg,0));
		int *shadedImgXfPtr = ((int *)PyArray_GETPTR1(shadedImgXf,0));
	
	printf("\nfragmod_shadeImgGrid(): PRE shadeImgGrid");

	shadeImgGrid(
		// Const
		xres,
		yres,
		lev,
		nTids,
		levProg,
		levPct,
		tripGlobF,
		clrKBig,
		kRip,
		moveK,
		moveUseAsBiggest,
		moveBiggestPow,
		moveKForBiggest,
		moveRippleSpeed,
		moveKofs,
		centX,
		centY,
		satClr,
		multClr,
		solidClr,
		style0x1y2rad,
		leftToRight,
		topToBottom,
		radiateTime,
		edgeThick,
		bgMode,
		fr,
		inhFramesPtr,
		exhFramesPtr,
		brFramesPtr,
		cInOutValsPtr,
		srcImgPtr,
		//tidImgPtr,
		tidPosGridThisLevPtr,
		tidsPtr,
		bbxsPtr,
		xfsPtr,
		isBulbsPtr,
		tidTripsPtr,
		aovRipImgPtr,
		alphaBoostPtr,
		shadedImgPtr,
		shadedImgXfPtr);
	printf("\nfragmod_shadeImgGrid(): POST shadeImgGrid\n\n");

	double foo = 8;
	return Py_BuildValue("f", foo);

}

static PyObject* fragmod_arrayIntToClr(PyObject* self, PyObject* args) {
	int xres;
	int yres;
	PyArrayObject *ints=NULL;
	PyArrayObject *clrs=NULL;

    if (!PyArg_ParseTuple(args, "iiOO",
		&xres, &yres, &ints, &clrs)) return NULL;

	int *intsPtr = ((int *)PyArray_GETPTR1(ints,0));
	int *clrsPtr = ((int *)PyArray_GETPTR1(clrs,0));
	
	printf("\n fragmod PRE arrayIntToClr");
	arrayIntToClr(
		xres,
		yres,
		intsPtr,
		clrsPtr
		);
	printf("\n fragmod POST arrayIntToClr");

	double foo = 8;
	return Py_BuildValue("f", foo);
}

static PyObject* fragmod_arrayClrToInt(PyObject* self, PyObject* args) {
	int xres;
	int yres;
	PyArrayObject *clrs=NULL;
	PyArrayObject *ints=NULL;

    if (!PyArg_ParseTuple(args, "iiOO",
		&xres, &yres, &clrs, &ints)) return NULL;

	int *clrsPtr = ((int *)PyArray_GETPTR1(clrs,0));
	int *intsPtr = ((int *)PyArray_GETPTR1(ints,0));
	
	printf("\n fragmod PRE arrayClrToInt");
	arrayClrToInt(
		xres,
		yres,
		clrsPtr,
		intsPtr
		);
	printf("\n fragmod POST arrayClrToInt");

	double foo = 8;
	return Py_BuildValue("f", foo);
}


static PyObject* fragmod_setTidPosGrid(PyObject* self, PyObject* args) {
	int xres;
	int yres;
	int nSids;
	PyArrayObject *sidsSortedPtr=NULL;
	PyArrayObject *posSortedPtr=NULL;
	PyArrayObject *inSurfGridPtr=NULL;
	PyArrayObject *tidPosGridPtr=NULL;

    if (!PyArg_ParseTuple(args, "iiiOOOO",
		&xres, &yres, &nSids,
		&sidsSortedPtr, &posSortedPtr, &inSurfGridPtr, &tidPosGridPtr)) return NULL;

	int *sidsSortedPtrI = ((int *)PyArray_GETPTR1(sidsSortedPtr,0));
	int *posSortedPtrI = ((int *)PyArray_GETPTR1(posSortedPtr,0));
	int *inSurfGridPtrI = ((int *)PyArray_GETPTR1(inSurfGridPtr,0));
	int *tidPosGridPtrI = ((int *)PyArray_GETPTR1(tidPosGridPtr,0));
	
	printf("\nPRE setTidPosGrid");
	setTidPosGrid(
		xres,
		yres,
		nSids,
		sidsSortedPtrI,
		posSortedPtrI,
		inSurfGridPtrI,
		tidPosGridPtrI
		);
	printf("\nPOST setTidPosGrid");

	double foo = 8;
	return Py_BuildValue("f", foo);
}

static PyObject* fragmod_initJtGrid(PyObject* self, PyObject* args) {
	int xres;
	int yres;
	int lev;
	PyArrayObject *imgArrayPtr=NULL;
	PyArrayObject *levThreshArrayPtr=NULL;
	PyArrayObject *nconsOutPtr=NULL;
	int nBreaths;
	float dNorm;
    if (!PyArg_ParseTuple(args, "iiiOOO",
		&xres, &yres, &lev,
		&imgArrayPtr, &levThreshArrayPtr, &nconsOutPtr)) return NULL;

	int *imgArrayPtrI = ((int *)PyArray_GETPTR1(imgArrayPtr,0));
	int *levThreshArrayPtrI = ((int *)PyArray_GETPTR1(levThreshArrayPtr,0));
	int *nconsOutPtrI = ((int *)PyArray_GETPTR1(nconsOutPtr,0));
	
	printf("\nPRE initJtCgrid");
	initJtCgrid(
		xres,
		yres,
		lev,
		imgArrayPtrI,
		levThreshArrayPtrI,
		nconsOutPtrI);
	printf("\nPOST initJtCgrid");

	double foo = 8;
	return Py_BuildValue("f", foo);

}

static PyObject* fragmod_calcInRip(PyObject* self, PyObject* args) {
	int fr;
	PyArrayObject *brFramesPtr=NULL;
	int nBreaths;
	float dNorm;
	float kRip;
    if (!PyArg_ParseTuple(args, "iOiff",
		&fr, &brFramesPtr, &nBreaths,
		&dNorm, &kRip)) return NULL;
	
	int brFrames[nBreaths];
	
	for (int i=0; i < nBreaths; i ++) {
		brFrames[i] = *((int *)PyArray_GETPTR1(brFramesPtr, i));
	}

	float inRip = calcInRip(fr, brFrames, nBreaths, dNorm, kRip);
	return Py_BuildValue("f", inRip);
	//return Py_BuildValue("f", inRip);

}

static PyObject* fragmod_cspace(PyObject* self, PyObject* args) {
	PyArrayObject *rPtr=NULL;
	PyArrayObject *gPtr=NULL;
	PyArrayObject *bPtr=NULL;
	PyArrayObject *outPtr=NULL;
    if (!PyArg_ParseTuple(args, "OOOO",
			&rPtr, &gPtr, &bPtr, &outPtr)) return NULL;

	float r[3];
	float g[3];
	float b[3];
	float out[3];

	for (int i=0; i < 3; i++) {
		r[i] = *((float *)PyArray_GETPTR1(rPtr, i));
		g[i] = *((float *)PyArray_GETPTR1(gPtr, i));
		b[i] = *((float *)PyArray_GETPTR1(bPtr, i));
		//out[i] = *((float *)PyArray_GETPTR1(outPtr, i));
	}

	float white[3] = {255, 255, 255};
	csFunc(r, g, b, white, out);

	float mx = MAX(out[0], out[1]);
	mx = MAX(mx, out[2]);

	for (int i=0; i < 3; i++) {
		float *a = ((float *)PyArray_GETPTR1(outPtr,i));
		//*a = CLAMP((float) out[i]/mx, 0, 1);
		*a = (float) out[i]/mx;
	}

	// No idea what this stuff is for.
	double foo = 8;
	return Py_BuildValue("d", foo);
}

static PyObject* fragmod_cspaceImg(PyObject* self, PyObject* args) {
	PyArrayObject *cInOutValsPtr=NULL;
	PyArrayObject *in=NULL;
	PyArrayObject *out=NULL;
	PyArrayObject *aovRipPtr=NULL;
	PyArrayObject *brFramesPtr=NULL;
	int xr;
	int yr;
	int fr;
	int radiateTime;
	int inOutBoth;
	float trip;

    //if (!PyArg_ParseTuple(args, "OOii", &in, &out, &xr, &yr)) return NULL;
    if (!PyArg_ParseTuple(args, "OOOOOiiiiif",
			&cInOutValsPtr,
			&in, &out,
			&aovRipPtr,
			&brFramesPtr,
			&xr, &yr, &fr, &radiateTime, &inOutBoth, &trip)) return NULL;

	printf ("\n\n BBBBBBBBBBBBBefore");
	int nBreaths = 4;
	int brFrames[nBreaths*2];
	for (int i=0; i < nBreaths*2; i++) {
		brFrames[i] = *((int *)PyArray_GETPTR1(brFramesPtr, i));
	}
	// 4 breaths * 2 inOuts * 3 rgbs * 3 comps per rgb
	float cInOutVals[24*3];
	for (int i=0; i < 24*3; i++) {
		cInOutVals[i] = *((float *)PyArray_GETPTR1(cInOutValsPtr, i));
		int inOut = (i/36) % 2; // 0 : inClr, 1 : outClr
		if ((inOut == 0 && inOutBoth == 1) || (inOut == 1 && inOutBoth == 0)) {
			cInOutVals[i] = 0;
		}
	}


	for (int x=0; x < xr; x ++) {
		for (int y=0; y < yr; y ++) {
			int tot[3] = {0, 0, 0};
			int count = 0;
			for (int xx=x; xx < MIN(x+1, xr); xx ++) {
				for (int yy=y; yy < MIN(y+1, yr); yy ++) {
					count += 1;
					//unsigned char a=*((unsigned char *)PyArray_GETPTR3(in,xx,yy,0));
					//tot += a;
					for (int i=0; i<3; i++) {
						tot[i] += *((unsigned char *)PyArray_GETPTR3(in,xx,yy,i));
					}
				}
			}

			float cAvg[3] = {0, 0, 0};
			//float dNorm = CLAMP(dist(x, y, xr/2, yr/2)/(xr/2), 0, 1);
			float dNorm = CLAMP(dist(x, y, xr/2, yr/2)/dist(0, 0, xr/2, yr/2), 0, 1);
			// TODO: Make sure you keep track of lumLift, kIntens, kVign -
			// maybe add a fade to grey?
			float lumLift = mixF(10, 2, pow(dNorm, .5))*trip;
			for (int j=0; j<3; j++) {
				cAvg[j] = (lumLift + tot[j])/count;
			}

			int inhFrames[nBreaths];
			int exhFrames[nBreaths];

			for (int i=0; i<nBreaths; i++) {
				inhFrames[i] = brFrames[i*2];
				exhFrames[i] = brFrames[i*2+1];
			}



			float kRip = mixF(.1, 1, trip);

			int cShadedI[3];
			int aovRip[3];
			getCspacePvNxInOut (
				fr,
				x, // For debug.
				radiateTime,
				cAvg, //outClrF, 
				cInOutVals,
				inhFrames,
				exhFrames,
				brFrames,
				nBreaths,
				dNorm,
				kRip,
				aovRip,
				cShadedI
				);

			//mix3F(cAvg, cShadedI, 0, cShadedI);
			mix3FItoI(cAvg, cShadedI, trip, cShadedI);
			//cShadedI[0] = 255;//cAvg[0];
			//cShadedI[1] = 0;//cAvg[1];
			//cShadedI[2] = 255;//cAvg[2];
			float kIntens = 1.2+4.8*trip;
			//float kIntens = 1;//-.8*trip;
			float kVign = MAX(0, 1-dNorm*trip);
			for (int j=0; j<3; j++) {
				int *a = ((int *)PyArray_GETPTR3(out,x,y,j));
				//*a = MIN(255, kVign*kIntens*(int) (cShadedI[j]));
				*a = MIN(255, kVign*kIntens*(int) (cShadedI[j]));

				int *b = ((int *)PyArray_GETPTR3(aovRipPtr,x,y,j));
				*b = MIN(255, (int) aovRip[j]);
				//if (j == 0) *a = 255;
			}
		}
	}
	// No idea what this stuff is for.
	double foo = 8;
	return Py_BuildValue("d", foo);
}

static PyMethodDef fragmod_methods[] = {
	// PythonName,	 C-function name,	argument presentation,	description
	{"cspaceImg",	fragmod_cspaceImg,	METH_VARARGS,	"Test ls 3d"},
	{"cspace",	fragmod_cspace,	METH_VARARGS,	"Test ls 3d"},
	{"calcInRip",	fragmod_calcInRip,	METH_VARARGS,	"Test ls 3d"},
	{"initJtGrid",	fragmod_initJtGrid,	METH_VARARGS,	"Init Jt Grid"},
	{"shadeImgGrid",	fragmod_shadeImgGrid,	METH_VARARGS,	"Shade Img Grid"},
	{"setTidPosGrid",	fragmod_setTidPosGrid,	METH_VARARGS,	"Set tid pos grid"},
	{"arrayIntToClr",	fragmod_arrayIntToClr,	METH_VARARGS,	"Int array to clr array"},
	{"arrayClrToInt",	fragmod_arrayClrToInt,	METH_VARARGS,	"Clr array to int array"},
	{NULL, NULL, 0, NULL} /* Sentinel */
};


PyMODINIT_FUNC initfragmod(void) {
	PyObject *m;
	m = Py_InitModule("fragmod", fragmod_methods);
	if (m == NULL) return;

	fragmodError = PyErr_NewException("fragmod.error", NULL, NULL); // "fragmod.error" python error object.
	Py_INCREF(fragmodError);

	//PyModule_AddObject(m, "error", "ExModError");
	PyModule_AddObject(m, "error", fragmodError);
}
