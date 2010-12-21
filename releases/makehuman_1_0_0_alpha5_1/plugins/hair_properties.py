#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d, hair, font3d
from aljabr import vdist,vsub,vmul,vadd, vnorm

print 'hair properties imported'


class Action:

    def __init__(self, human, before, after, postAction=None):
        self.name = 'Change hair color'
        self.human = human
        self.before = before
        self.after = after
        self.postAction = postAction

    def do(self):
        self.human.hairColor = self.after
        if self.postAction:
            self.postAction()
        return True

    def undo(self):
        self.human.hairColor = self.before
        if self.postAction:
            self.postAction()
        return True


class HairPropertiesTaskView(gui3d.TaskView):

    def __init__(self, category):        
        
        gui3d.TaskView.__init__(self, category, 'Hair', category.app.getThemeResource('images', 'button_hair_det.png'), category.app.getThemeResource('images',
                                'button_hair_det_on.png'))
                                
        gui3d.Object(self, 'data/3dobjs/unit_square.obj', self.app.getThemeResource('images', 'group_hair_tool.png'), [10, 211, 9.0], 128,256)

        #############
        #SLIDERS
        #############
        self.redSlider = gui3d.Slider(self, self.app.getThemeResource('images', 'slider_red.png'), self.app.getThemeResource('images', 'slider.png'),
                                      self.app.getThemeResource('images', 'slider_focused.png'), position=[10, 235, 9.2])

        self.redSliderLabel = gui3d.TextView(self, mesh='data/3dobjs/empty.obj', position=[60, 350, 9.4])
        self.redSliderLabel.setText('Red: 0')

        self.greenSlider = gui3d.Slider(self, self.app.getThemeResource('images', 'slider_green.png'), self.app.getThemeResource('images', 'slider.png'),
                                        self.app.getThemeResource('images', 'slider_focused.png'), position=[10, 265, 9.2])

        self.greenSliderLabel = gui3d.TextView(self, mesh='data/3dobjs/empty.obj', position=[60, 370, 9.4])
        self.greenSliderLabel.setText('Green: 0')

        self.blueSlider = gui3d.Slider(self, self.app.getThemeResource('images', 'slider_blue.png'), self.app.getThemeResource('images', 'slider.png'),
                                       self.app.getThemeResource('images', 'slider_focused.png'), position=[10, 295, 9.2])

        self.blueSliderLabel = gui3d.TextView(self, mesh='data/3dobjs/empty.obj', position=[60, 390, 9.4])
        self.blueSliderLabel.setText('Blue: 0')
    
        self.widthSlider = gui3d.Slider(self, position=[10, 150, 9], value=1.0, min=0.3,max=30.0, label = "Hair width") 

        self.colorPreview = gui3d.Object(self, 'data/3dobjs/colorpreview.obj', position=[20, 340, 9.4])
                    
        @self.redSlider.event
        def onChanging(value):
            self.setColor([value, self.greenSlider.getValue(), self.blueSlider.getValue()])
            
        @self.redSlider.event
        def onChange(value):
            self.changeColor([value, self.greenSlider.getValue(), self.blueSlider.getValue()])

        @self.greenSlider.event
        def onChanging(value):
            self.setColor([self.redSlider.getValue(), value, self.blueSlider.getValue()])
            
        @self.greenSlider.event
        def onChange(value):
            self.changeColor([self.redSlider.getValue(), value, self.blueSlider.getValue()])
            
        @self.blueSlider.event
        def onChanging(value):
            self.setColor([self.redSlider.getValue(), self.greenSlider.getValue(), value])

        @self.blueSlider.event
        def onChange(value):
            self.changeColor([self.redSlider.getValue(), self.greenSlider.getValue(), value])
            
        @self.widthSlider.event
        def onChanging(value):
            human = self.app.scene3d.selectedHuman
            if len(human.hairObj.verts)>0 : 
               hairWidthUpdate(human.scene, human.hairObj, widthFactor=self.widthSlider.getValue())
            #pass #Do something!

    def changeColor(self, color):
        action = Action(self.app.scene3d.selectedHuman, self.app.scene3d.selectedHuman.hairColor, color, self.syncSliders)
        self.app.do(action)
        human = self.app.scene3d.selectedHuman
        c = [int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), 255]
        human.hairObj.facesGroups[0].setColor(c)

    def setColor(self, color):
        c = [int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), 255]
        for g in self.colorPreview.mesh.facesGroups:
            g.setColor(c)
        self.redSliderLabel.setText('Red:%i' % c[0])
        self.greenSliderLabel.setText('Green:%i' % c[1])
        self.blueSliderLabel.setText('Blue:%i' % c[2])

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        hairColor = self.app.scene3d.selectedHuman.hairColor
        self.syncSliders()

    def syncSliders(self):
        hairColor = self.app.scene3d.selectedHuman.hairColor
        self.redSlider.setValue(hairColor[0])
        self.greenSlider.setValue(hairColor[1])
        self.blueSlider.setValue(hairColor[2])
        self.setColor(hairColor)


category = None
taskview = None

def load(app):
    taskview = HairPropertiesTaskView(app.categories['Modelling'])
    print 'hair properties loaded'

def unload(app):
    print 'hair properties unloaded'


#obj = hair object
def hairWidthUpdate(scn, obj,res=0.04, widthFactor=1.0): #luckily both normal and vertex index of object remains the same!
  N=len(obj.verts)
  origWidth = vdist(obj.verts[1].co,obj.verts[0].co)/res
  diff= (widthFactor-origWidth)*res/2
  for i in xrange(0,N/2):
      vec=vmul(vnorm(vsub(obj.verts[i*2+1].co,obj.verts[i*2].co)), diff) 
      obj.verts[i*2].co=vsub(obj.verts[i*2].co,vec)
      obj.verts[i*2+1].co=vadd(obj.verts[i*2+1].co,vec)
      obj.verts[i*2].update(updateNor=0)
      obj.verts[i*2+1].update(updateNor=0)