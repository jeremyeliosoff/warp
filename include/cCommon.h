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

float dist(float x0, float y0, float x1, float y1) {
	float dx = x1-x0;
	float dy = y1-y0;
	return sqrt(dx*dx + dy*dy);
}

float mixF(float a, float b, float m) {
	return m*b + (1.0-m)*a;
}

void mixF3(float* a, float* b, float m, float* ret) {
	int i;
	for (i = 0; i < 3; i++) {
		ret[i] = mixF(a[i], b[i], m);
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