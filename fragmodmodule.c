#include <Python.h>
#include "numpy/arrayobject.h"
#include "cCommon.h"


// Define a new exception object for our module.
static PyObject *fragmodError;


static PyObject* fragmod_cspaceImg(PyObject* self, PyObject* args) {
	PyArrayObject *cInOutValsPtr=NULL;
	PyArrayObject *in=NULL;
	PyArrayObject *out=NULL;
	PyArrayObject *aovRipPtr=NULL;
	int xr;
	int yr;
	int fr;
	int inOutBoth;
	float trip;

    //if (!PyArg_ParseTuple(args, "OOii", &in, &out, &xr, &yr)) return NULL;
    if (!PyArg_ParseTuple(args, "OOOOiiiif",
			&cInOutValsPtr,
			&in, &out,
			&aovRipPtr,
			&xr, &yr, &fr, &inOutBoth, &trip)) return NULL;
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

			// TEMP
			int inhFrames[] = {1840, 2270, 2700, 3080};
			int exhFrames[] = {2090, 2510, 2940, 3350};


			int cShadedI[3];
			int aovRip[3];
			int nBreaths = 4;
			getCspacePvNxInOut (
				fr,
				cAvg, //outClrF, 
				cInOutVals,
				inhFrames,
				exhFrames,
				nBreaths,
				dNorm,
				aovRip,
				cShadedI
				);

			//mix3F(cAvg, cShadedI, 0, cShadedI);
			mix3FItoI(cAvg, cShadedI, trip, cShadedI);
			//cShadedI[0] = 255;//cAvg[0];
			//cShadedI[1] = 0;//cAvg[1];
			//cShadedI[2] = 255;//cAvg[2];
			float kIntens = 1+5*trip;
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
