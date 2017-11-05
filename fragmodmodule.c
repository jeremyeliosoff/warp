#include <Python.h>
#include "numpy/arrayobject.h"
#include "cCommon.h"


// Define a new exception object for our module.
static PyObject *fragmodError;


static PyObject* fragmod_cspaceImg(PyObject* self, PyObject* args) {
	PyArrayObject *in=NULL;
	PyArrayObject *out=NULL;
	PyArrayObject *cInRPtr=NULL;
	PyArrayObject *cInGPtr=NULL;
	PyArrayObject *cInBPtr=NULL;
	PyArrayObject *cOutRPtr=NULL;
	PyArrayObject *cOutGPtr=NULL;
	PyArrayObject *cOutBPtr=NULL;
	int xr;
	int yr;

    //if (!PyArg_ParseTuple(args, "OOii", &in, &out, &xr, &yr)) return NULL;
    if (!PyArg_ParseTuple(args, "OOOOOOOOii",
			&in, &out,
			&cInRPtr, &cInGPtr, &cInBPtr,
			&cOutRPtr, &cOutGPtr, &cOutBPtr,
			&xr, &yr)) return NULL;
	float cInR[3] = {0, 0, 0};
	float cInG[3] = {0, 0, 0};
	float cInB[3] = {0, 0, 0};
	float cOutR[3] = {0, 0, 0};
	float cOutG[3] = {0, 0, 0};
	float cOutB[3] = {0, 0, 0};

	for (int i=0; i < 3; i++) {
		cInR[i] = *((float *)PyArray_GETPTR1(cInRPtr, i));
		cInG[i] = *((float *)PyArray_GETPTR1(cInGPtr, i));
		cInB[i] = *((float *)PyArray_GETPTR1(cInBPtr, i));
		cOutR[i] = *((float *)PyArray_GETPTR1(cOutRPtr, i));
		cOutG[i] = *((float *)PyArray_GETPTR1(cOutGPtr, i));
		cOutB[i] = *((float *)PyArray_GETPTR1(cOutBPtr, i));
	}
	
	for (int x=0; x < xr; x ++) {
		for (int y=0; y < yr; y ++) {
			int tot[3] = {0, 0, 0};
			int count = 0;
			for (int xx=x; xx < MIN(x+2, xr); xx ++) {
				for (int yy=y; yy < MIN(y+2, yr); yy ++) {
					count += 1;
					//unsigned char a=*((unsigned char *)PyArray_GETPTR3(in,xx,yy,0));
					//tot += a;
					for (int i=0; i<3; i++) {
						tot[i] += *((unsigned char *)PyArray_GETPTR3(in,xx,yy,i));
					}
				}
			}

			//float mxInOut = 1.0-(float)y/yr;
			float r[3] = {1, 0, 0};
			float g[3] = {0, 1, 0};
			float b[3] = {0, 0, 1};

			float cAvg[3] = {0, 0, 0};
			for (int j=0; j<3; j++) {
				cAvg[j] = tot[j]/count;
			}

			float cCspaceIn[3] = {0, 0, 0};
			float cCspaceOut[3] = {0, 0, 0};
			csFunc(cInR, cInG, cInB, cAvg, cCspaceIn);
			csFunc(cOutR, cOutG, cOutB, cAvg, cCspaceOut);
			float cTint[3];
			float mxInOut = CLAMP(dist(x, y, xr/2, yr/2)/(xr/2), 0, 1);
			mixF3(cCspaceIn, cCspaceOut, mxInOut, cTint);
			for (int j=0; j<3; j++) {
				int *b=((int *)PyArray_GETPTR3(out,x,y,j));
				//*b = MIN(255, (int) (cTint[j]*tot[j]/count));
				//*b = MIN(255, (int) (cCspaceIn[j]*tot[j]/count));
				*b = MIN(255, (int) (cTint[j]*255));
				//*b = MIN(255, (int) (cCspaceIn[j]*255));
				//*b = MIN(255, (int) cAvg[j]);
				//*b = MIN(255, (int) cCspace[j]);
				//if (j == 0) *b *= mxInOut;

			}
		}
	}
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
