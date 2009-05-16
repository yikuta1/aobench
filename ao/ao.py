#!/usr/bin/env python
# -*-mode: python; cording: utf-8 -*-
# $Id: ao.py,v 1.1 2009/02/24 06:19:33 ikuta Exp $
# Copyright (c) 2009 Yoshihito Ikuta. All Rights Reserved.
#
# a porting project "aobench" by syoyo to Python

import math
import random
import time

WIDTH = 256
HEIGHT = 256
NSUBSAMPLES = 2
NAO_SAMPLES = 8

# render objects
sphere1 = []
sphere2 = []
sphere3 = []
plane = []
rimg = []

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
	rs = [ro[0] - sphere[0], ro[1] - sphere[1], ro[2] - sphere[2]]

	B = vdot(rs, rd)
	C = vdot(rs, rs) - (sphere[3] * sphere[3])
	D = B * B - C

	if D > 0.0:
		t = B * -1 - math.sqrt(D)
		if t > 0.0 and t < isect[0]:
			isect[0] = t
			isect[7] = 1
			isect[1] = ro[0] + rd[0] * t
			isect[2] = ro[1] + rd[1] * t
			isect[3] = ro[2] + rd[2] * t

			n = vnormalize([isect[1] - sphere[0], isect[2] - sphere[1], isect[3] - sphere[2]])
			isect[4] = n[0]
			isect[5] = n[1]
			isect[6] = n[2]
	return isect

def ray_plane_intersect(isect, ray, plane):
	ro = ray[0]
	rd = ray[1]

	plane_p = [plane[0], plane[1], plane[2]]
	plane_n = [plane[3], plane[4], plane[5]]
	d = -1 * vdot(plane_p, plane_n)
	v = vdot(rd, plane_n)

	if abs(v) < 1.0e-17:
		return isect

	t = -1 * (vdot(ro, plane_n) + d) / v

	if t > 0.0 and t < isect[0]:
		isect[0] = t
		isect[7] = 1
		isect[1] = ro[0] + rd[0] * t
		isect[2] = ro[1] + rd[1] * t
		isect[3] = ro[2] + rd[2] * t
		isect[4] = plane[3]
		isect[5] = plane[4]
		isect[6] = plane[5]
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


def ambient_occlusion(col, isect):
	global NAO_SAMPLES
	global sphere1
	global sphere2
	global sphere3
	global plane

	i = j = 0
	ntheta = NAO_SAMPLES
	nphi = NAO_SAMPLES
	eps = 0.0001

	p = [isect[1] + eps * isect[4], isect[2] + eps * isect[5], isect[3] + eps * isect[6]]

	basis = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
	orthoBasis(basis, [isect[4], isect[5], isect[6]])

	occlusion = 0.0

	b0 = basis[0]
	b1 = basis[1]
	b2 = basis[2]

	for j in range(ntheta):
		for i in range(nphi):
			theta = math.sqrt(random.random())
			phi = 2.0 * math.pi * random.random()
			#phi = 2.0 * 3.14159265358979323846 * random.random()

			x = math.cos(phi) * theta
			y = math.sin(phi) * theta
			z = math.sqrt(1.0 - theta * theta)

			# local -> global
			rx = x * (b0[0]) + y * (b1[0]) + z * (b2[0])
			ry = x * (b0[1]) + y * (b1[1]) + z * (b2[1])
			rz = x * (b0[2]) + y * (b1[2]) + z * (b2[2])

			ray = [p, [rx, ry, rz]]
			occIsect = [1.0e+17, 0, 0, 0, 0, 0, 0, 0]

			occIsect = ray_sphere_intersect(occIsect, ray, sphere1)
			occIsect = ray_sphere_intersect(occIsect, ray, sphere2)
			occIsect = ray_sphere_intersect(occIsect, ray, sphere3)
			occIsect = ray_plane_intersect(occIsect, ray, plane)

			if occIsect[7] == 1:
				occlusion += 1.0
	occlusion = (ntheta * nphi - occlusion) / (float)(ntheta * nphi)
	col[0] = occlusion
	col[1] = occlusion
	col[2] = occlusion
	return col

def clamp(f):
	i = f * 255.5
	if (i < 0):
		i = 0
	if (i > 255):
		i = 255
	return i

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

					isect = [1.0e+17, 0, 0, 0, 0, 0, 0, 0]

					isect = ray_sphere_intersect(isect, ray, sphere1)
					isect = ray_sphere_intersect(isect, ray, sphere2)
					isect = ray_sphere_intersect(isect, ray, sphere3)
					isect = ray_plane_intersect(isect, ray, plane)

					if isect[7] == 1:
						col = [0, 0, 0]
						col = ambient_occlusion(col, isect)
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

	sphere1 = [-2.0, 0.0, -3.5, 0.5]
	sphere2 = [-0.5, 0.0, -3.0, 0.5]
	sphere3 = [1.0, 0.0, -2.2, 0.5]
	plane = [0.0, -0.5, 0.0, 0.0, 1.0, 0.0]


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


def ao(path):
	global rimg

	t = time.clock()
	final_time = 0

	rimg = [0] * (WIDTH * HEIGHT * 3)
	init_scene()
	rimg = render(WIDTH, HEIGHT, NSUBSAMPLES)

	saveppm(path, WIDTH, HEIGHT, rimg)

	final_time = time.clock() - t
	print "final time: " + str(final_time) + " seconds"
