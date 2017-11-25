#define MAX( a, b ) ( ( a > b) ? a : b )
#define MIN( a, b ) ( ( a < b) ? a : b )
#define CLAMP( v, mn, mx ) ( MAX ( mn, MIN ( mx, v) ) )


void vSMult(float* a, float b, float* out) {
	for (int i=0; i<3; i++) {
		out[i] = ((float) a[i]) * ((float) b);
	}
}

void vMult(float* a, float* b, float* out) {
	for (int i=0; i<3; i++) {
		out[i] = a[i] * b[i];
	}
}

void vAdd(float* a, float* b, float* out) {
	for (int i=0; i<3; i++) {
		out[i] = a[i] + b[i];
	}
}

float fit(float v, float omn, float omx, float nmn, float nmx) {
	float prog = (v-omn)/(omx-omn);
	return nmn + prog * (nmx-nmn);
}

void csFunc(float* r, float* g, float* b, float* in, float* out) {
	for (int i=0; i<3; i++) {
		out[i] = 0;
	}
	
	float toAdd[3];
	vSMult(r, ((float) in[0])/255.0, toAdd);
	vAdd(out, toAdd, out);

	vSMult(g, ((float) in[1])/255.0, toAdd);
	vAdd(out, toAdd, out);

	vSMult(b, ((float) in[2])/255.0, toAdd);
	vAdd(out, toAdd, out);
}

float jSmoothstep(float edge0, float edge1, float x) {
	// Scale, bias and saturate x to 0..1 range
	float ret = edge1;
	if (edge1 > edge0) {
		ret = CLAMP((x - edge0)/(edge1 - edge0), 0.0, 1.0); 
		//Evaluate polynomial
		ret = ret*ret*(3 - 2*ret);
	}
	return ret;
}

float smoothpulse(float edge0, float edge1, float edge2, float edge3, float x) {
	return jSmoothstep(edge0, edge1, x) - jSmoothstep(edge2, edge3, x);
}

float dist(float x0, float y0, float x1, float y1) {
	float dx = x1-x0;
	float dy = y1-y0;
	return sqrt(dx*dx + dy*dy);
}

float mixF(float a, float b, float m) {
	return m*b + (1.0-m)*a;
}

float mixI(int a, int b, float m) {
	return m*b + (1.0-m)*a;
}


void mix3I(int* a, int* b, float m, int* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixI(a[i], b[i], m);
	}
}

void mix3F(float* a, float* b, float m, float* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixF(a[i], b[i], m);
	}
}

void mix3FItoI(float* a, int* b, float m, int* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = (int) mixF(a[i], (float)((int)b[i]), m);
	}
}


void assignFV(
	float* src,
	float* dst)
{
	dst[0] = src[0];
	dst[1] = src[1];
	dst[2] = src[2];
}

void assignIV(
	int* src,
	int* dst)
{
	dst[0] = src[0];
	dst[1] = src[1];
	dst[2] = src[2];
}

void assignIS(
	int x,
	int y,
	int z,
	int* dst)
{
	dst[0] = x;
	dst[1] = y;
	dst[2] = z;
}

void assignFS(
	float x,
	float y,
	float z,
	float* dst)
{
	dst[0] = x;
	dst[1] = y;
	dst[2] = z;
}
float getBreathFramesAndProg (int fr,
	int* breaths,  // __GLOBAL
	int nBreaths,
		int *nFrPvBreath, int *nFrNxBreath) {
	float brProg = 0;
	*nFrPvBreath = 0;
	*nFrNxBreath = 1;

	for (int i=0; i<nBreaths-1; i++) {
		if (fr >= breaths[i] && fr < breaths[i+1]) {
			*nFrPvBreath = i;
			*nFrNxBreath = i+1;
			brProg = fit(fr,
				breaths[*nFrPvBreath], breaths[*nFrNxBreath], 0, 1);
			//brProg = fit(fr, 2000, 2700, 0, 1);
			break;
		}
	}
	//return CLAMP(brProg, 0, 1);
	return brProg;
}

void getCInOut(
	float* cInOutVals,  // __GLOBAL
	int inOut,
	int cNum,
	int rgb,
	float* out) {
	int nBreaths = 4;
	int i = 9*(inOut * nBreaths + cNum) + 3*rgb;
	for (int j=0; j<3; j++) {
		out[j] = cInOutVals[i + j];
	}
}


void getCspacePvNxInOut (
	int fr,
	float* outClrF, 
	float* cInOutVals,  // __GLOBAL
	int* inhFrames,  // __GLOBAL
	int* exhFrames,  // __GLOBAL
	int nBreaths,
	float dNorm,
	int* aovRip,
	int* cShadedI

) {
	int pvInhFr, nxInhFr, pvExhFr, nxExhFr;
	float inhProgForRipple = getBreathFramesAndProg (fr, inhFrames, nBreaths, &pvInhFr, &nxInhFr);
	int ripFfw = 200;
	float ripSpeed = 15;
	float ripTime = 1.0/ripSpeed;
	float ripEdge = .003;
	float ofs = ripTime*dNorm;
	float edge = ofs + ripEdge * (1-ripTime);
	float inRip = smoothpulse(ofs, edge, edge, 1-ripTime, inhProgForRipple);

	int inFfw = 600;
	int frWOfs = fr + ripFfw * inRip - ((float)inFfw) * -dNorm;

	float inhProg = getBreathFramesAndProg (frWOfs, inhFrames, nBreaths, &pvInhFr, &nxInhFr);
	float exhProg = getBreathFramesAndProg (frWOfs, exhFrames, nBreaths, &pvExhFr, &nxExhFr);

	// Load all the cInOut parm colours 4 uber-arrays for: inPv, inNx, exPv, exNx
	float pvCInRGB[9];
	float nxCInRGB[9];
	float pvCOutRGB[9];
	float nxCOutRGB[9];

	for (int rgb=0; rgb<3; rgb++) {
		int index = rgb * 3;
		getCInOut(cInOutVals, 0, pvInhFr, rgb, &pvCInRGB[index]);
		getCInOut(cInOutVals, 0, nxInhFr, rgb, &nxCInRGB[index]);
		getCInOut(cInOutVals, 1, pvExhFr, rgb, &pvCOutRGB[index]);
		getCInOut(cInOutVals, 1, nxExhFr, rgb, &nxCOutRGB[index]);
	}

	float pvCIn[3];
	float pvCOut[3];
	float nxCIn[3];
	float nxCOut[3];

	csFunc(&pvCInRGB[0], &pvCInRGB[3], &pvCInRGB[6], outClrF, pvCIn);
	csFunc(&pvCOutRGB[0], &pvCOutRGB[3], &pvCOutRGB[6], outClrF, pvCOut);

	csFunc(&nxCInRGB[0], &nxCInRGB[3], &nxCInRGB[6], outClrF, nxCIn);
	csFunc(&nxCOutRGB[0], &nxCOutRGB[3], &nxCOutRGB[6], outClrF, nxCOut);


	float mixedIn[3];
	float mixedOut[3];
	mix3F(pvCIn, nxCIn, inhProg, mixedIn);
	mix3F(pvCOut, nxCOut, exhProg, mixedOut);

	float cShadedF[3];	
	mix3F(mixedIn, mixedOut, dNorm, cShadedF);
	//mix3F(mixedIn, mixedOut, 0, cShadedF); // TEMP

	cShadedI[0] = (int) MIN(255.0f, cShadedF[0]*255.0);
	cShadedI[1] = (int) MIN(255.0f, cShadedF[1]*255.0);
	cShadedI[2] = (int) MIN(255.0f, cShadedF[2]*255.0);
	
	if (aovRip != 0) {
		aovRip[0] = 255 * inRip;
		aovRip[1] = 255 * (1-inRip);
		aovRip[2] = 0;
	}
}
