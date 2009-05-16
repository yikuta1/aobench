#!/usr/bin/env python
# -*-mode: python; cording: utf-8 -*-
# $Id: pt.py,v 1.1 2009/02/24 06:19:33 ikuta Exp $
# Copyright (c) 2009 Yoshihito Ikuta All Rights Reserved.
#
# a porting project "aobench" by syoyo to Python

import math
import random
import time

#PI = 3.14159265358979323846
WIDTH = 256
HEIGHT = 256
NSUBSAMPLES = 2
NAO_SAMPLES = 8
NPATH_SAMPLES   = 4
MAX_TRACE_DEPTH = 8
#NPATH_SAMPLES   = 128
#MAX_TRACE_DEPTH = 16

# render objects
sphere1 = []
sphere2 = []
sphere3 = []
plane = []
rimg = []
#isect = [1.0e+17, [0, 0, 0], [0, 0, 0], [0, 0, 0], [0.0, 0.0, 0.0], 0] # distance, position[], normal[], color[], emissiveCol[], hit

def vdot(v0, v1):
	c = v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]
	return c

def vcross(v0, v1):
	c = [0] * 3
	c[0] = v0[1] * v1[2] - v0[2] * v1[1]
	c[1] = v0[2] * v1[0] - v0[0] * v1[2]
	c[2] = v0[0] * v1[1] - v0[1] * v1[0]
	return c

def vnormalize(c):
	length = math.sqrt(vdot(c, c))

	if math.fabs(length) > 1.0e-17:
		c[0] /= length
		c[1] /= length
		c[2] /= length
	return c


def ray_sphere_intersect(isect, ray, sphere):
	ro = ray[0]
	rd = ray[1]
	rs = [ro[0] - sphere[0][0], ro[1] - sphere[0][1], ro[2] - sphere[0][2]]

	B = vdot(rs, rd)
	C = vdot(rs, rs) - (sphere[1] * sphere[1])
	D = B * B - C

	if D > 0.0:
		t = B * -1 - math.sqrt(D)
		if t > 0.0 and t < isect[0]:
			isect[0] = t
			isect[5] = 1
			isect[1][0] = ro[0] + rd[0] * t
			isect[1][1] = ro[1] + rd[1] * t
			isect[1][2] = ro[2] + rd[2] * t

			n = vnormalize([isect[1][0] - sphere[0][0], isect[1][1] - sphere[0][1], isect[1][2] - sphere[0][2]])
			isect[2][0] = n[0]
			isect[2][1] = n[1]
			isect[2][2] = n[2]
			isect[3][0] = sphere[2][0]
			isect[3][1] = sphere[2][1]
			isect[3][2] = sphere[2][2]
			isect[4][0] = sphere[3][0]
			isect[4][1] = sphere[3][1]
			isect[4][2] = sphere[3][2]
	return isect

def ray_plane_intersect(isect, ray, plane):
	ro = ray[0]
	rd = ray[1]

	plane_p = [plane[0][0], plane[0][1], plane[0][2]]
	plane_n = [plane[1][0], plane[1][1], plane[1][2]]
	d = -1 * vdot(plane_p, plane_n)
	v = vdot(rd, plane_n)

	if abs(v) < 1.0e-17:
		return isect

	t = -1 * (vdot(ro, plane_n) + d) / v

	if t > 0.0 and t < isect[0]:
		isect[0] = t
		isect[5] = 1
		isect[1][0] = ro[0] + rd[0] * t
		isect[1][1] = ro[1] + rd[1] * t
		isect[1][2] = ro[2] + rd[2] * t
		isect[2][0] = plane[1][0]
		isect[2][1] = plane[1][1]
		isect[2][2] = plane[1][2]
		isect[3][0] = plane[2][0]
		isect[3][1] = plane[2][1]
		isect[3][2] = plane[2][2]
		isect[4][0] = plane[3][0]
		isect[4][1] = plane[3][1]
		isect[4][2] = plane[3][2]
	return isect

def orthoBasis(basis, n):
	b2 = n
	b0 = basis[0]

	v = [0.0, 0.0, 0.0]
	if((n[0] < 0.6) and (n[0] > -0.6)):
		v[0] = 1.0
	elif ((n[1] < 0.6) and (n[1] > -0.6)):
		v[1] = 1.0
	elif ((n[2] < 0.6) and (n[2] > -0.6)):
		v[2] = 1.0
	else:
		v[0] = 1.0

	b1 = [v[0], v[1], v[2]]
	b0 = vnormalize(vcross(b1, b2))
	basis[1] = vnormalize(vcross(b2, b0))
	basis[0] = b0
	basis[2] = b2

def clamp(f):
	i = f * 255.5
	if (i < 0):
		i = 0
	if (i > 255):
		i = 255
	return i

def trace(ray, depth):
	global NAO_SAMPLES
	global sphere1
	global sphere2
	global sphere3
	global plane
	#global isect

	#print MAX_TRACE_DEPTH
	#print depth
	if depth >= MAX_TRACE_DEPTH:
		return [0.0, 0.0, 0.0]

	#
	# 1. find nearest intersection.
	#
	isect = [1.0e+17, [0, 0, 0], [0, 0, 0], [0, 0, 0], [0.0, 0.0, 0.0], 0]
	#isect = [1.0e+17, 0, 0, 0, 0, 0, 0, 0]
	isect = ray_sphere_intersect(isect, ray, sphere1)
	isect = ray_sphere_intersect(isect, ray, sphere2)
	isect = ray_sphere_intersect(isect, ray, sphere3)
	isect = ray_plane_intersect(isect, ray, plane)

	if isect[5] == 0:
		return [0.75, 0.75, 0.75]

	#
	# 2. Pick a random ray direction with importance sampling.
	#    p = cos(theta) / PI
	#
	#PI = 3.14159265358979323846
	theta = random.random()
	phi = 2.0 * math.pi * random.random()

	x = math.cos(phi) * math.sqrt(1.0 - theta)
	y = math.sin(phi) * math.sqrt(1.0 - theta)
	z = math.sqrt(theta)

	basis = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
	orthoBasis(basis, [isect[2][0], isect[2][1], isect[2][2]])

	b0 = basis[0]
	b1 = basis[1]
	b2 = basis[2]

	# local -> global
	rx = x * (b0[0]) + y * (b1[0]) + z * (b2[0])
	ry = x * (b0[1]) + y * (b1[1]) + z * (b2[1])
	rz = x * (b0[2]) + y * (b1[2]) + z * (b2[2])

	# Slightly move ray org towards ray dir to avoid numerical probrem.
	eps = 0.0001

	p = [isect[1][0] + eps * rx, isect[1][1] + eps * ry, isect[1][2] + eps * rz]
	newRay = [p, [rx, ry, rz]]

	fscale = 1.0 / math.pi # diffuse. BRDF / PI
	fr = [isect[3][0] * fscale, isect[3][1] * fscale, isect[3][2] * fscale]
	cosTheta = vdot([rx, ry, rz], [isect[2][0], isect[2][1], isect[2][2]]) # Ray.dir . N
	Li = trace(newRay, depth + 1)
	Le = [isect[4][0], isect[4][1], isect[4][2]]

	#
	# 3. Calculate contribution.
	#
	# Lo = Le + PI * fr * cosTheta * Li 
	# But we do not need cosThata attenuation since its weight is already
	# included in importance sampling of ray direction.4
	Lo = [Le[0] + math.pi * fr[0] * Li[0], Le[1] + math.pi * fr[1] * Li[1], Le[2] + math.pi * fr[2] * Li[2]]

	return Lo;

def pathTrace(ray):
	i = 0

	col = [0.0, 0.0, 0.0]
	for i in range(NPATH_SAMPLES):
		tcol = trace(ray, 0)
		col[0] += tcol[0]
		col[1] += tcol[1]
		col[2] += tcol[2]

	scale = 1.0 / (float)(NPATH_SAMPLES)
	#print col
	#print scale
	col[0] *= scale
	col[1] *= scale
	col[2] *= scale
	#print('%f %f %f\n'%(col[0], col[1], col[2]))
	return col

def render(w, h, nsubsamples):
	global sphere1
	global sphere2
	global sphere3
	global plane
	global rimg
	x = y = 0
	u = v = 0
	fimg = [0] * (w * h * 3)

	for y in range(h):
		for x in range(w):
			for v in range(nsubsamples):
				for u in range(nsubsamples):
					px = (x + (u / (float)(nsubsamples)) - (w / 2.0)) / (w / 2.0)
					py = -1 * (y + (v / (float)(nsubsamples)) - (h / 2.0)) / (h / 2.0)
					ray0 = [0.0, 0.0, 0.0]
					ray1 = vnormalize([px, py, -1.0])
					ray = [ray0, ray1]

					col = [0, 0, 0]
					col = pathTrace(ray)

					fimg[3 * (y * w + x) + 0] += col[0]
					fimg[3 * (y * w + x) + 1] += col[1]
					fimg[3 * (y * w + x) + 2] += col[2]
			fimg[3 * (y * w + x) + 0] /= (float)(nsubsamples * nsubsamples)
			fimg[3 * (y * w + x) + 1] /= (float)(nsubsamples * nsubsamples)
			fimg[3 * (y * w + x) + 2] /= (float)(nsubsamples * nsubsamples)

			rimg[3 * (y * w + x) + 0] = clamp(fimg[3 * (y * w + x) + 0])
			rimg[3 * (y * w + x) + 1] = clamp(fimg[3 * (y * w + x) + 1])
			rimg[3 * (y * w + x) + 2] = clamp(fimg[3 * (y * w + x) + 2])
	return rimg


def init_scene():
	global sphere1
	global sphere2
	global sphere3
	global plane

	sphere1 = [[-1.05, 0.0, -2.0], 0.5, [0.75, 0.0, 0.0], [0.0, 0.0, 0.0]]
	sphere2 = [[0.0, 0.0, -2.0], 0.5, [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
	sphere3 = [[1.05, 0.0, -2.0], 0.5, [0.0, 0.0, 0.75], [0.0, 0.0, 0.0]]
	plane = [[0.0, -0.5, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5, 0.5], [0.0, 0.0, 0.0]]

def saveppm(fname, w, h, rimg):
	fp = open(fname, 'w')

	fp.write('P3\n')
	fp.write('%i %i\n'%(w, h))
	fp.write('255\n')
	for i in range(w * h * 3):
		fp.write('%i '%rimg[i])
		if(0 == (i + 1) % 3):
			fp.write('\n')
	fp.close()


def pt(path):
	global rimg

	t = time.clock()
	final_time = 0

	rimg = [0] * (WIDTH * HEIGHT * 3)
	init_scene()
	rimg = render(WIDTH, HEIGHT, NSUBSAMPLES)

	saveppm(path, WIDTH, HEIGHT, rimg)

	final_time = time.clock() - t
	print "final time: " + str(final_time) + " seconds"

if __name__ == '__main__':
	print "test\n"
	pt('pt.ppm')
