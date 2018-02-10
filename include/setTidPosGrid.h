 
void setArrayCellShd2(int x, int y, int xres, int yres,
  int val,
  int* ret)
{
	if (x >= 0 && x < xres && y >= 0 && y < yres) {
		int i = (x * yres + y);
		//printf("\nx=%d, y=%d")
		ret[i] = val;
	}
}
// A iterative binary search function. It returns
// location of x in given array arr[l..r] if present,
// otherwise -1
int binarySearch(int arr[], int len, int x)
{
	int l = 0;
	int r = len;
    while (l <= r)
    {
        int m = l + (r-l)/2;
 
        // Check if x is present at mid
        if (arr[m] == x)
            return m;
 
        // If x greater, ignore left half
        if (arr[m] < x)
            l = m + 1;
 
        // If x is smaller, ignore right half
        else
            r = m - 1;
    }
 
    // if we reach here, then element was
    // not present
    return -1;
}

int bruteForceSearch(int arr[], int len, int x)
{
	for (int i = 0; i < len; i++) {
		if (x == arr[i])
			return i;
	}
    // if we reach here, then element was
    // not present
    return -1;
}



void setTidPosGrid(
	int xres,
	int yres,
	int nSids,
	int* sidsSorted,
	int* posSorted,
	int* inSurfGrid,
	int* tidPosGrid
	)
{

	//printf("\n xres=%d, yres=%d", xres, yres);
	for (int x = 0; x < xres; x++ ) {
		//if (x % 100 == 0) printf("\n satClr=%f, multClr=%f, solidClr=%f", satClr, multClr, solidClr);
		for (int y = 0; y < yres; y++ ) {
			int sid = getCellScalar(x, y, yres, inSurfGrid);
			//printf("\n sid=%d", sid);
			int sidPos = bruteForceSearch(sidsSorted, nSids, sid);
			//printf("\n posSorted[0]=%d", posSorted[0]);
			if (sidPos == 0 || posSorted[sidPos] == 0)
				setArrayCellShd2(x, y, xres, yres, -1, tidPosGrid);
			else
				setArrayCellShd2(x, y, xres, yres, posSorted[sidPos], tidPosGrid);
				//setArrayCellShd2(10, 10, xres, yres, 5, tidPosGrid);

		}
	}

}
