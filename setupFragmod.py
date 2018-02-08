from distutils.core import setup, Extension

module1 = Extension('fragmod',
	include_dirs = ['/usr/local/include', '/home/jeremy/dev/warp/include'],
	depends = ['/home/jeremy/dev/warp/include/cCommon.h',
		'/home/jeremy/dev/warp/include/initJtGrid.h'
		'/home/jeremy/dev/warp/include/shadeImgGrid.h'
		],
	libraries = ['pthread'],
	sources = ['fragmodmodule.c'])


setup (name = 'fragmod',
	version = '1.0',
	description = 'This is an example package.',
	author = 'gOd',
	url = 'some.site',
	ext_modules=[module1])


