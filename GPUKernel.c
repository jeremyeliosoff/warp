
bool compare4(int v0, v1, v2, v3, int *b) {
	bool ret = 0;
	if ( v0 == b[0] && v1 == b[1] && v2 == b[2] && v3 == b[3])
		ret = 1;
	return ret;
}

void assign4(int v0, int v1, int v2, int v3, int *ret) {
	ret[0] = v0;
	ret[1] = v1;
	ret[2] = v2;
	ret[3] = v3;
}

int neighboursToConns (int* nbrs, int* cons) {
	int arg[4];
	assign4(0, 1, 1, 1, arg);
	int ret = 0;

	// For some F'ED UP reason, removing all elseifs
	// makes this satisfied if any nbrs == 1.
	if		  (compare4(0, 0,
						0, 0, nbrs)) {
		ret = 'a';
	} else if (compare4(0, 0,
						0, 1, nbrs)) {
		ret = 'b';
	} else if (compare4(0, 0,
						1, 0, nbrs)) {
		ret = 'c';
	} else if (compare4(0, 0,
						1, 1, nbrs)) {
		ret = 'd';
	} else if (compare4(0, 1,
						0, 0, nbrs)) {
		ret = 'e';
	} else if (compare4(0, 1,
						0, 1, nbrs)) {
		ret = 'f';
	} else if (compare4(0, 1,
						1, 0, nbrs)) {
		ret = 'g';
	} else if (compare4(0, 1,
						1, 1, nbrs)) {
		ret = 'h';
	} else if (compare4(1, 0,
						0, 0, nbrs)) {
		ret = 'i';
	} else if (compare4(1, 0,
						0, 1, nbrs)) {
		ret = 'j';
	} else if (compare4(1, 0,
						1, 0, nbrs)) {
		ret = 'k';
	} else if (compare4(1, 0,
						1, 1, nbrs)) {
		ret = 'l';
	} else if (compare4(1, 1,
						0, 0, nbrs)) {
		ret = 'm';
	} else if (compare4(1, 1,
						0, 1, nbrs)) {
		ret = 'n';
	} else if (compare4(1, 1,
						1, 0, nbrs)) {
		ret = 'o';
	} else if (compare4(1, 1,
						1, 1, nbrs)) {
		ret = 'p';
	}

	return ret;
	//(0, 0,\
	// 0, 0):[],

	//(0, 0,\
	// 0, 1):[((0, 1), (1, 0))],

	//(0, 0,\
	// 1, 0):[((-1, 0), (0, 1))],

	//(0, 0,\
	// 1, 1):[((-1, 0), (1, 0))],

	//(0, 1,\
	// 0, 0):[((1, 0), (0, -1))],

	//(0, 1,\
	// 0, 1):[((0, 1), (0, -1))],

	//(0, 1,\
	// 1, 0):[((-1, 0), (0, 1)), ((1, 0), (0, -1))],

	//(0, 1,\
	// 1, 1):[((-1, 0), (0, -1))],

	//(1, 0,\
	// 0, 0):[((0, -1), (-1, 0))],

	//(1, 0,\
	// 0, 1):[((0, 1), (1, 0)), ((0, -1), (-1, 0))],

	//(1, 0,\
	// 1, 0):[((0, -1), (0, 1))],

	//(1, 0,\
	// 1, 1):[((0, -1), (1, 0))],

	//(1, 1,\
	// 0, 0):[((1, 0), (-1, 0))],

	//(1, 1,\
	// 0, 1):[((0, 1), (-1, 0))],

	//(1, 1,\
	// 1, 0):[((1, 0), (0, 1))],

	//(1, 1,\
	// 1, 1):[]
	 }
int clrAvg(uchar* clr)
{
	return (clr[0] + clr[1] + clr[2])/3;
}


void getClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar* ret)
{
	int i = y * xres * npix + x * npix;
	ret[0] = imgArray[i];
	ret[1] = imgArray[i+1];
	ret[2] = imgArray[i+2];
}

void setArrayCell(int x, int y, int xres, int npix,
  uchar* val,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	ret[i] = val[0];
	ret[i+1] = val[1];
	ret[i+2] = val[2];
}

void setArrayCellInt(int x, int y, int levOfs, int xres, int npix,
  int val,
  int __attribute__((address_space(1)))* ret)
{
	int i = y * xres + x;
	ret[i+levOfs] = val;
}


int getClrAvg(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray)
{
	uchar clr[3];
	getClr(x, y, xres, npix,imgArray, clr);
	return clrAvg(clr);
}

void cpClr(int x, int y, int xres, int npix,
  uchar __attribute__((address_space(1)))* imgArray,
  uchar __attribute__((address_space(1)))* ret)
{
	int i = y * xres * npix + x * npix;
	uchar clr[3];
	uchar avg = getClrAvg(x, y, xres, npix, imgArray);
	uchar retClr[] = {avg, avg, avg};

	setArrayCell(x, y, xres, npix, retClr, ret);
	//uchar avg = clrAvg(clr);
	//ret[i] = avg;
	//ret[i+1] = avg;
	//ret[i+2] = avg;
}

__kernel void initJtC(
			int testNLevs,
			__global uchar* imgArray,
			__global uchar* levThreshArray,
			__global int* nconsOut)
{
	int x = get_global_id(1);
	int y = get_global_id(0);

	int xres = %d;
	int yres = %d;
	int npix = 3;

	int lev;
	uchar levThreshInt;

	for (lev = 0; lev < testNLevs; lev ++) {
		levThreshInt = levThreshArray[lev];	

		int levOfs = lev*xres*yres;
		if (x < xres-1 && y < yres-1) {
			int i;
			int tot = 0;
			int nbrs[4];

			for (i = 0; i < 4; i++) {
				int xx = x + i/2;
				int yy = y + i%%2;
				uchar avg = getClrAvg(xx, yy, xres, npix, imgArray);
				int val = avg > levThreshInt ? 1 : 0;
				nbrs[i] = val;
				tot += val;
			}
			//printf("\nnbrs: %%d, %%d, %%d, %%d", nbrs[0], nbrs[1], nbrs[2], nbrs[3]);
			int cons[] = {0, 0, 0, 0};
			int ncons = 0;
			if (tot > 0 and tot < 4) {
				ncons = neighboursToConns (nbrs, cons) - 97;
			}
			//setArrayCell(x, y, xres, 1, tot, nconsOut);
			setArrayCellInt(x, y, levOfs, xres, 1, ncons, nconsOut);
		} else { // We should just make nconsOut res smaller, but doesn't work.
			setArrayCellInt(x, y, levOfs, xres, 1, 0, nconsOut);
		}
	}
}
