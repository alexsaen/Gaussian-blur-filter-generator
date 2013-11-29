#
# script to generate vertex and fragment shaders for Gaussian blur with given kernel size
#

import sys, math, string

						# 1d Gaussian distribution, s is standard deviation
def gaussian ( x, s ):
	return math.exp ( -x*x/(2*s*s) )

						# return array normalized of coefficients for kernal size k
def buildCoeffs ( k, s ):
	coeffs = []	
	sum    = -1.0
	for x in range ( k + 1 ):
		c    = gaussian ( float ( x ), s )
		sum += 2*c
		coeffs.append ( c )
	
						# renormalize coeffs
	for x in range ( k + 1 ):
		coeffs [x] = coeffs [x] / sum
	
	return coeffs

def genVertexShader ( k, s ):
	return "void gause(float2 duv)\n{\n\tgl_Position     = gl_ModelViewProjectionMatrix * gl_Vertex;\n\tgl_TexCoord [0] = gl_MultiTexCoord0;\n}\n"

def genFragmentShader ( k, s, d1, d2 ):
	coeffs = buildCoeffs ( k, s )
	shd1   = "#ifndef GAUSS_FXH\n#define GAUSS_FXH\n\nfloat4 gauss( sampler TextureSampler, float2 tx, float2 dx)\n{\n"
	shd2   = "\tfloat2 sdx = float2(0, 0);\n"
	shd4   = "\tfloat4 sum = tex2D(TextureSampler, tx ) * %f;\n\n" % coeffs [0]
	shd    = shd1 + shd2 + shd4
	
	for x in range ( 1, k + 1 ):
		shd = shd + ( "\tsum += (tex2D( TextureSampler, tx + sdx ) + tex2D( TextureSampler, tx - sdx ) )* %f; \n" % coeffs [x] )
		shd = shd + "\tsdx += dx;\n"
		
	return shd + "\n\treturn sum;\n}\n\n#endif\n"


def getOpts ():
	opt  = ""
	opts = {}
	for s in sys.argv[1:]:
		if s [0] == '-':
			opt = s[1:]
		else:
			opts [opt] = s
			opt        = ""
	
	return opts

			
if __name__ == "__main__":
	s    = 3.0
	k    = 7
	name = "b-y"
	
	if len ( sys.argv ) > 1:					# there're some arguments
		if sys.argv [1] == '-h' or sys.argv [1] == '-?':
			print "Gaussian blure shader generator"
			print "Options:"
			print "     -s n        - set the S constant"
			print "     -k n        - set the kernel radius"
			print "     -f filename - set the output filename"
			sys.exit ( 0 )
			
		opts = getOpts ()
		
		if opts.has_key ( "s" ):
			s = string.atof ( opts ["s"] )
			
		if opts.has_key ( "k" ):
			k = string.atoi ( opts ["k"] )
		
		if opts.has_key ( "f" ):
			name = opts ["f"]
		
	frag = genFragmentShader ( k, s, 0.0, 1.0 / 512.0 )
	f2   = open ( name + ".fxh", "w" )
	f2.write ( frag )
	f2.close ()
	print "Shaders %s and %s have been successfully generated" % ( name + ".vsh", name + ".fsh" )
