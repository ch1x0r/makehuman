""" 
**Project Name:**	  MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**	http://code.google.com/p/makehuman/

**Authors:**		   Thomas Larsson

**Copyright(c):**	  MakeHuman Team 2001-2009

**Licensing:**		 GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
Hair importer for Blender.2.5

"""

bl_addon_info = {
	'name': 'Import MakeHuman hair (.obj)',
	'author': 'Thomas Larsson',
	'version': '0.7',
	'blender': (2, 5, 6),
	'api': 33590,
	'location': 'File > Import',
	'description': 'Import MakeHuman hair file (.obj)',
	'url': 'http://www.makehuman.org',
	'category': 'Import/Export'}

"""
Place this file in the .blender/scripts/addons dir
You have to activated the script in the "Add-Ons" tab (user preferences).
Access from the File > Import menu.
"""

import bpy
import mathutils
from mathutils import *
import os

#
#	Structure of obj file
#

"""
v 0.140943 8.017279 0.227470
v 0.136992 8.053163 0.281365
v 0.232386 8.314340 0.444419
v 0.450719 8.241523 0.873019
v 0.415614 7.887863 1.029564
v 0.297117 7.653935 1.108557
v -0.113154 7.533733 1.182444
cstype bspline
deg 3
curv 0.0 1.0 -1 -2 -3 -4 -5 -6 -7
parm u 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
end
"""

#
#	importHair(filename, scale, invert, useCurves):
#

def importHair(filename, scale, invert, useCurves):
	guides = readHairFile(filename, scale)
	if invert:
		for guide in guides:
			guide.reverse()
	(nmax,nguides) = equalizeHairLengths(guides)
	print("%d guides, %d steps" % (len(nguides), nmax))
	if useCurves:
		makeCurves('HairCurves', nguides)
	else:
		makeHair('Hair', nmax-1, nguides)
		bpy.ops.particle.particle_edit_toggle()

	'''
	fp = open("/home/thomas/myblends/hair/test2.txt", "w")
	nmax = len(guides[0])
	for m,guide in enumerate(guides):
		printGuideAndHair(fp, guide, psys.particles[m], psys.settings.hair_step, nmax)
	fp.close()	
	'''
	return

#
#	writeHairFile(fileName, scale):
#	For debugging, export hair as obj
#

def writeHairFile(fileName, scale):
	ob = bpy.context.object
	psys = ob.active_particle_system
	if psys and psys.name == 'Hair':
		pass
	else:
		raise NameError("Active object has no hair")

	path1 = os.path.expanduser(fileName)
	filePath = os.path.realpath(path1)
	print( "Writing hair " + filePath )
	fp = open(filePath, "w")

	for n,par in enumerate(psys.particles):
		v = par.location / scale
		fp.write("v %.3f %.3f %.3f\n" % (v[0], v[1], v[2]))
		for h in par.is_hair:
			v = h.location / scale
			fp.write("v %.3f %.3f %.3f\n" % (v[0], v[1], v[2]))
		fp.write("g Hair.%03d\n" % n)
		fp.write("end\n\n")
	fp.close()
	return

#
#	readHairFile(fileName, scale):
#	Read obj file with hair strands as curves
#

def readHairFile(fileName, scale):
	path1 = os.path.expanduser(fileName)
	filePath = os.path.realpath(path1)
	print( "Reading hair " + filePath )
	fp = open(filePath, "rU")
	guide = []
	guides = []
	lineNo = 0

	for line in fp: 
		words= line.split()
		lineNo += 1
		if len(words) == 0:
			pass
		elif words[0] == 'v':
			(x,y,z) = (float(words[1]), float(words[2]), float(words[3]))
			guide.append(scale*Vector((x,-z,y)))
		elif words[0] == 'end':
			guides.append(guide)
			guide = []
		elif words[0] == 'f':
			raise NameError("Hair file '%s' must only contain curves, not meshes" % filePath)
		else:
			pass
	fp.close()
	print("File %s read" % fileName)
	return guides

#
#	equalizeHairLengths(guides):
#	All hairs in Blender must have the same length. Interpolate the guide curves ensure this.
#
	
def equalizeHairLengths(guides):
	nmax = 0
	nguides = []
	for guide in guides:
		n = len(guide)
		if n > nmax:
			nmax = n
		#for k in range(1,n):
		#	guide[k] -= guide[0]
	
	for guide in guides:
		if len(guide) < nmax:
			nguide = recalcHair(guide, nmax)
		else:
			nguide = guide
		nguides.append(nguide)
	return (nmax, nguides)

#
#	recalcHair(guide, nmax):
#	Recalculates a single hair curve
#
	
def recalcHair(guide, nmax):
	n = len(guide)
	if n == nmax:
		return guide
	dx = float(nmax)/n
	x = 0.0
	y0 = Vector([0.0, 0.0, 0.0])
	y0 = guide[0]
	nguide = [guide[0].copy()]
	for k in range(1,n):
		y = guide[k]
		f = (y-y0)/dx
		x += dx
		while x > 0.9999:
			y0 += f
			nguide.append(y0.copy())
			k += 1
			x -= 1
	y0 = guide[n-1]
	nguide.append(y0.copy())
	return nguide
			
#
#	printGuides(fp, guide, nguide, nmax):
#	printGuideAndHair(fp, guide, par, hs, nmax):
#	For debugging
#

def printGuides(fp, guide, nguide, nmax):
	if len(nguide) != nmax:
		fp.write("wrong size %d != %d\n" % (len(nguide), nmax))
		return
	fp.write("\n\n")
	for n,v in enumerate(guide):
		nv = nguide[n]
		fp.write("(%.3f %.3f %.3f)\t=> (%.3f %.3f %.3f)\n" % (v[0], v[1], v[2], nv[0], nv[1], nv[2]))
	for n in range(len(guide), nmax):
		nv = nguide[n]
		fp.write("\t\t\t\t=> (%.3f %.3f %.3f)\n" % (nv[0], nv[1], nv[2]))
	return
	
def printGuideAndHair(fp, guide, par, hs, nmax):
	fp.write("\n\n")
	for n,v in enumerate(guide):
		if n == 0:
			nv = par.location
		else:
			nv = par.is_hair[n-1].co
		fp.write("%2d %2d  (%.3f %.3f %.3f)\t=> (%.3f %.3f %.3f)" % (n-1, hs, v[0], v[1], v[2], nv[0], nv[1], nv[2]))
		if n > 0:
			h = par.is_hair[n-1]
			lv = h.co_hair_space
			fp.write(" (%.3f %.3f %.3f) %.3f %.3f\n" % (lv[0], lv[1], lv[2], h.time, h.weight))
		else:
			fp.write("\n")
	return
	
#	
#	makeHair(name, hstep, guides):
#	Create particle hair from guide curves. 
#	hstep = hair_step setting
#

def makeHair(name, hstep, guides):
	ob = bpy.context.object
	bpy.ops.object.particle_system_add()
	psys = ob.particle_systems.active
	psys.name = name

	settings = psys.settings
	settings.type = 'HAIR'
	settings.name = 'HairSettings'
	settings.count = len(guides)
	settings.hair_step = hstep
	# [‘VERT’, ‘FACE’, ‘VOLUME’, ‘PARTICLE’]
	settings.emit_from = 'FACE'
	settings.use_render_emitter = True

	settings.use_hair_bspline = True
	#settings.hair_geometry = True
	#settings.grid_resolution = 
	#settings.draw_step = 1

	settings.material = 3
	#settings.use_render_adaptive = True
	settings.use_strand_primitive = True

	settings.child_type = 'PARTICLES'
	settings.child_nbr = int(1000/settings.count)+1
	settings.rendered_child_count = 10*settings.child_nbr
	settings.child_length = 1.0
	settings.child_radius = 0.2

	'''
	settings.clump_factor = 0.0
	settings.clumppow = 0.0

	settings.rough_endpoint = 0.0
	settings.rough_end_shape = 1.0
	settings.rough1 = 0.0
	settings.rough1_size = 1.0
	settings.rough2 = 0.0
	settings.rough2_size = 1.0
	settings.rough2_thres = 0.0

	settings.kink = 'CURL'
	settings.kink_amplitude = 0.2
	settings.kink_shape = 0.0
	settings.kink_frequency = 2.0
	'''
	bpy.ops.particle.disconnect_hair(all=True)
	bpy.ops.particle.particle_edit_toggle()

	for m,guide in enumerate(guides):
		par = psys.particles[m]
		setStrand(guide, par, hstep)

	bpy.ops.particle.select_all(action='SELECT')
	bpy.ops.particle.connect_hair(all=True)
	return

#
#	setStrand(guide, par, hstep):
#

def setStrand(guide, par, hstep):
	nmax = hstep
	dt = 100.0/(hstep)
	dw = 1.0/(hstep-1)
	if len(guide) < nmax+1:
		nmax = len(guide)-1
		#raise NameError("Wrong length %d != %d" % (len(guide), hstep))
	par.location = guide[0]
	for n in range(0, nmax):
		point = guide[n+1]
		h = par.is_hair[n]
		#h.co = point
		h.co_hair_space = point
		h.time = (n+1)*dt
		w = 1.0 - (n+1)*dw
		h.weight = max(w, 0.0)
	for n in range(nmax, hstep):
		point = guide[nmax]
		h = par.is_hair[n]
		#h.co = point
		h.co_hair_space = point
		h.time = (n+1)*dt
		w = 1.0 - (n+1)*dw
		h.weight = max(w, 0.0)

	#print(par.location)
	#for n in range(0, hstep):
	#	print("  ", par.is_hair[n].co)
	return

#
#	reverseStrands(ob):
#	getGuideFromHair(par):
#

def reverseStrands(ob):
	psys = ob.particle_systems.active
	if (not psys) or psys.settings.type != 'HAIR':
		print("Cannot reverse strands. No active hair.")
		return
	for par in psys.particles:
		if par.select:
			guide = getGuideFromHair(par)
			hstep = len(guide)
			setStrand(guide, par, psys.hair_step)
	return

def getGuideFromHair(par):
	guide = [par.location]
	for h in par.is_hair:
		guide.append( h.co_hair_space.copy() )
	guide.reverse()
	return guide

#
#	makeCurves(name, guides):
#	setSplinePoint(pt, x):
#

def makeCurves(name, guides):
	cu = bpy.data.curves.new('HairCurve', 'CURVE')
	ob = bpy.data.objects.new('HairCurve', cu)
	bpy.context.scene.objects.link(ob)
	cu.dimensions = '3D'

	for guide in guides:
		npoints = len(guide)
		spline = cu.splines.new('NURBS')
		spline.points.add(npoints-1)
		for n in range(npoints):
			setSplinePoint(spline.points[n].co, guide[n])
	return ob

def setSplinePoint(pt, x):
	pt[0] = x[0]
	pt[1] = x[1]
	pt[2] = x[2]
	return

#
#	reverseCurves(ob):
#

def reverseCurves(ob):
	for spline in ob.data.splines:
		selected = False
		for pt in spline.points:
			if pt.select:
				selected = True
				break
		if selected:
			guide = []
			for pt in spline.points:
				guide.append(pt.co.copy())
			guide.reverse()
			npoints = len(guide)
			for n in range(npoints):
				setSplinePoint(spline.points[n].co, guide[n])
	return

#
#	makeHairFromCurve(ob, cuOb):
#

def makeHairFromCurve(ob, cuOb):
	guides = []
	for spline in cuOb.data.splines:
		guide = []
		for pt in spline.points:
			x = pt.co
			guide.append( Vector((x[0], x[1], x[2])) )
		guides.append(guide)
	makeHair('Hair', len(guides[0])-1, guides)
	return

#
#	User interface
#

DEBUG= False
from bpy.props import *

#
#	class IMPORT_OT_makehuman_hair_obj(bpy.types.Operator):
#

class IMPORT_OT_makehuman_hair_obj(bpy.types.Operator):
	"""Import MakeHuman hair from OBJ curves file (.obj)"""
	bl_idname = "import_hair.makehuman_obj"
	bl_description = 'Import MakeHuman hair from OBJ curves file (.obj)'
	bl_label = "Import MakeHuman hair"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"

	filepath = StringProperty(name="File Path", description="File path used for importing the .obj file", maxlen= 1024, default= "")

	scale = FloatProperty(name="Scale", description="Default meter, decimeter = 1.0", default=1.0)
	invert = BoolProperty(name="Invert", description="Invert hair direction", default=False)
	useCurves = BoolProperty(name="Curves", description="Import curves as curves", default=False)
	
	def execute(self, context):
		p = self.properties
		importHair(p.filepath, p.scale, p.invert, p.useCurves)
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

#
#	class MhxHairPanel(bpy.types.Panel):
#

class MhxHairPanel(bpy.types.Panel):
	bl_label = "MakeHuman Hair"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	def draw(self, context):
		layout = self.layout
		scn = context.scene
		#layout.operator("object.ReverseStrandsButton")
		layout.operator("object.ReverseCurveButton")
		layout.operator("object.MakeHairFromCurvesButton")

#
#	class OBJECT_OT_ReverseStrandsButton(bpy.types.Operator):
#

class OBJECT_OT_ReverseStrandsButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_ReverseStrandsButton"
	bl_label = "Reverse strands"

	@classmethod
	def poll(cls, context):
		return (context.object and context.object.particle_systems.active)	

	def execute(self, context):
		reverseStrands(context.object)
		print("Strands reversed")
		return{'FINISHED'}	

#
#	class OBJECT_OT_ReverseCurveButton(bpy.types.Operator):
#

class OBJECT_OT_ReverseCurveButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_ReverseCurveButton"
	bl_label = "Reverse curve"

	@classmethod
	def poll(cls, context):
		return (context.object and context.object.type == 'CURVE')

	def execute(self, context):
		reverseCurves(context.object)
		print("Curve reversed")
		return{'FINISHED'}	

#
#	class OBJECT_OT_MakeHairFromCurvesButton(bpy.types.Operator):
#

class OBJECT_OT_MakeHairFromCurvesButton(bpy.types.Operator):
	bl_idname = "OBJECT_OT_MakeHairFromCurvesButton"
	bl_label = "Make hair from curves"

	@classmethod
	def poll(cls, context):
		return (context.object and context.object.type == 'MESH')	

	def execute(self, context):
		ob = context.object
		for cuOb in context.scene.objects:
			if cuOb.select and cuOb.type == 'CURVE':
				makeHairFromCurve(ob, cuOb)
		print("Made hair from curves")
		return{'FINISHED'}	

#
#	Register
#

def register():
	bpy.types.register(IMPORT_OT_makehuman_hair_obj)
	menu_func = lambda self, context: self.layout.operator(IMPORT_OT_makehuman_hair_obj.bl_idname, text="MakeHuman hair (.obj)...")
	bpy.types.INFO_MT_file_import.append(menu_func)
 
def unregister():
	bpy.types.unregister(IMPORT_OT_makehuman_hair_obj)
	menu_func = lambda self, context: self.layout.operator(IMPORT_OT_makehuman_hair_obj.bl_idname, text="MakeHuman hair (.obj)...")
	bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	try:
		unregister()
	except:
		pass
	register()

#
#	Testing
#

'''
guide1 = [ [0, 1, 0], [0, 2, 0], [0, 2, 1] ]
guide2 = [ [1, 0, 0], [1, 1, 0], [1, 1, 1] ]
guide3 = [ [2, 0, 0], [2, 1, 0], [2, 1, 1] ]
makeHair('H1', 3, [guide1, guide2, guide3])
makeHair('H2', 3, [guide2])
makeHair('H3', 3, [guide3])


readHairFile('/home/thomas/myblends/hair/hair_hairy.obj', 1.0, False)
writeHairFile('/home/thomas/myblends/hair/haired.obj', 1.0)
'''

