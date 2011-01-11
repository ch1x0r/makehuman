# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
	"name": "MHX Fourier",
	"author": "Thomas Larsson",
	"version": "0.1",
	"blender": (2, 5, 5),
	"api": 33590,
	"location": "View3D > Properties > MHX Fourier",
	"description": "Fourier tool",
	"warning": "",
	"category": "3D View"}

"""
Run from text window. 
Access from UI panel (N-key) when rig is active.

"""

MAJOR_VERSION = 0
MINOR_VERSION = 2
BLENDER_VERSION = (2, 55, 5)

import bpy, cmath, math
from bpy.props import *

#
#	ditfft2(f, N, z):
#
#	Y_0,...,N−1 ← ditfft2(X, N, s):             DFT of (X0, Xs, X2s, ..., X(N-1)s):
#    if N = 1 then
#        Y_0 ← X_0                                      trivial size-1 DFT base case
#    else
#        Y_0,...,N/2−1 ← ditfft2(X, N/2, 2s)             DFT of (X_0, X_2s, X_4s, ...)
#        Y_N/2,...,N−1 ← ditfft2(X+s, N/2, 2s)           DFT of (X_s, X_s+2s, X_s+4s, ...)
#        for k = 0 to N/2−1                           combine DFTs of two halves into full DFT:
#            t ← Y_k
#            Y_k ← t + exp(−2πi k/N) * Y_k+N/2
#            Y_k+N/2 ← t − exp(−2πi k/N) * Y_k+N/2
#        endfor
#    endif
	
def ditfft2(f, N, z):
	if N == 1:
		return f
	else:
		N2 = int(N/2)
		f_even = ditfft2(f[::2], N2, z*z)
		f_odd = ditfft2(f[1::2], N2, z*z)
		e = 1
		y_even = []
		y_odd = []
		for k in range(N2):
			t0 = f_even[k]
			t1 = f_odd[k]
			y_even.append( t0 + e*t1 )
			y_odd.append( t0 - e*t1 )
			e *= z
		return y_even + y_odd

#
#	fourierFCurves(context):
#

def fourierFCurves(context):
	rig = context.object
	try:
		act = rig.animation_data.action
	except:
		act = None
	if not act:
		print("No FCurves to Fourier")
		return

	for fcu in act.fcurves:
		fourierFCurve(fcu, act, context.scene)
	setInterpolation(rig)
	return

#
#	fourierFCurve(fcu, act, scn):
#

def fourierFCurve(fcu, act, scn):
	words = fcu.data_path.split('.')
	if words[-1] == 'location':
		isLoc = True
		doFourier = scn.MhxFourierLoc
	elif words[-1] == 'rotation_quaternion':
		isLoc = False
		doFourier = scn.MhxFourierRot
	else:
		doFourier = False
	if not doFourier:
		return

	N = int(2**scn.MhxFourierLevels)
	points = fcu.keyframe_points
	if len(points) <= 2:
		return
	t0 = scn.frame_start
	tn = scn.frame_end
	T = (tn-t0+1)
	dt = T/N
	f0 = fcu.evaluate(t0)
	if isLoc:
		fn = fcu.evaluate(tn)
		df = (fn-f0)/N*(T+1)/T
		# print(f0, fn, N, T)
	else:
		df = 0
	fcu.keyframe_points.add(frame=tn+1, value=f0)

	f = []
	for i in range(N):
		ti = t0 + i*dt
		fi = fcu.evaluate(ti)
		f.append( fi-i*df )
	#if isLoc:
	#	print(fcu.data_path, fcu.array_index, df)
	#	printList(f)
	w = complex( 0, -2*cmath.pi/N )
	z = cmath.exp(w)
	fhat = ditfft2(f, N, z)
	#if isLoc:
	#	print("   ***")
	#	printList(fhat)

	path = fcu.data_path
	index = fcu.array_index
	grp = fcu.group.name
	act.fcurves.remove(fcu)
	nfcu = act.fcurves.new(path, index, grp)
	w = complex( 0, 2*cmath.pi/T )
	z = cmath.exp(w)
	e = 1
	kmax = int(2**scn.MhxFourierTerms)
	if kmax > N/2:
		kmax = N/2
	for ti in range(t0, tn+2):
		yi = evalFourier(fhat, kmax, e)/N
		e *= z
		nfcu.keyframe_points.add(frame=ti, value=yi)
	return

#
#	evalFourier(fhat, kmax, z):
#

def evalFourier(fhat, kmax, z):
	e = 1
	f = 0
	k = 0
	for fn in fhat:
		f += fn*e
		e *= z
		k += 1
		if k >= kmax:
			break
	y = f + f.conjugate()
	if abs(y.imag) > 1e-3:
		raise NameError("Not real", f)
	return y.real

#
#	Testing
#	printList(arr):
#	makeTestCurve(context)
#	class OBJECT_OT_MakeTestCurve(bpy.types.Operator):
#

def printList(arr):
	for elt in arr:
		if type(elt) == float:
			print("%.3f" % elt)
		elif type(elt) == complex:
			if abs(elt.imag) < 1e-4:
				print("%.3f" % elt.real)
			elif abs(elt.real) < 1e-4:
				print("%.3fj" % elt.imag)
			else:
				print("%.3f+%.3fj" % (elt.real, elt.imag))


def makeTestCurve(context):
	scn = context.scene
	t0 = scn.frame_start
	tn = scn.frame_end
	N = tn-t0+1
	rig = context.object
	act = rig.animation_data.action
	fcu = act.fcurves[0]
	path = fcu.data_path
	index = fcu.array_index
	grp = fcu.group.name
	act.fcurves.remove(fcu)
	nfcu = act.fcurves.new(path, index, grp)
	w = 2*cmath.pi/N
	for k in range(N+1):
		t = k+t0
		y = 2*math.sin(w*k) + math.sin(2*w*k)
		nfcu.keyframe_points.add(frame=t, value=y)
	setInterpolation(rig)
	return

class OBJECT_OT_MakeTestCurveButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_MakeTestCurveButton"
	bl_label = "Make test curve"

	def execute(self, context):
		makeTestCurve(context)
		print("Made curve")
		return{'FINISHED'}	

#
#	setInterpolation(rig):
#

def setInterpolation(rig):
	if not rig.animation_data:
		return
	act = rig.animation_data.action
	if not act:
		return
	for fcu in act.fcurves:
		for pt in fcu.keyframe_points:
			pt.interpolation = 'LINEAR'
		fcu.extrapolation = 'CONSTANT'
	return

#
#	class OBJECT_OT_FourierButton(bpy.types.Operator):
#

class OBJECT_OT_FourierButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_FourierButton"
	bl_label = "Fourier"

	def execute(self, context):
		import bpy
		fourierFCurves(context)
		print("Curves Fouriered")
		return{'FINISHED'}	


#
#	class MhxFourierPanel(bpy.types.Panel):
#

class Bvh2MhxFourierPanel(bpy.types.Panel):
	bl_label = "Mhx Fourier"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(cls, context):
		if context.object and context.object.type == 'ARMATURE':
			return True

	def draw(self, context):
		layout = self.layout
		scn = context.scene
		layout.operator("object.InitInterfaceButton")
		#layout.operator("object.MakeTestCurveButton")

		layout.label('Fourier')
		row = layout.row()
		row.prop(scn, "MhxFourierLoc")
		row.prop(scn, "MhxFourierRot")
		layout.prop(scn, "MhxFourierLevels")
		layout.prop(scn, "MhxFourierTerms")
		layout.operator("object.FourierButton")

		return

#
#	class OBJECT_OT_InitInterfaceButton(bpy.types.Operator):
#

def initInterface(context):
	bpy.types.Scene.MhxFourierLoc = BoolProperty(
		name="Location",
		description="Fourier transform location F-curves",
		default=True)

	bpy.types.Scene.MhxFourierRot = BoolProperty(
		name="Rotation",
		description="Fourier transform rotation F-curves",
		default=True)

	bpy.types.Scene.MhxFourierLevels = IntProperty(
		name="Fourier levels", 
		description="Fourier levels",
		min = 1, max = 6,
		default=3)

	bpy.types.Scene.MhxFourierTerms = IntProperty(
		name="Fourier terms", 
		description="Fourier terms",
		min = 1, max = 12,
		default=4)

class OBJECT_OT_InitInterfaceButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_InitInterfaceButton"
	bl_label = "Initialize"

	def execute(self, context):
		import bpy
		initInterface(context)
		print("Interface initialized")
		return{'FINISHED'}	

initInterface(bpy.context)

#
#	register
#

def register():
	pass

def unregister():
	pass

if __name__ == "__main__":
	register()
