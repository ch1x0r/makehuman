import os.path
#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d
import os
import random
import algos3d
import mh
import humanmodifier
import events3d

class AsymmTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Asymm', category.app.getThemeResource('images', 'button_asymm.png'), category.app.getThemeResource('images', 'button_asymm_on.png'))

        #Sliders       
        self.asymmBrowSlider = gui3d.Slider(self,  position=[20, 80, 9.3], value=0.0, min=-1.0, max=1.0, label="Brow asymmetry")
        self.asymmCheekSlider = gui3d.Slider(self,  position=[20, 120, 9.3], value=0.0, min=-1.0, max=1.0, label="Cheek asymmetry")
        self.asymmEarsSlider = gui3d.Slider(self,  position=[20, 160, 9.3], value=0.0, min=-1.0, max=1.0, label="Ears asymmetry")
        self.asymmEyeSlider = gui3d.Slider(self,  position=[20, 200, 9.3], value=0.0, min=-1.0, max=1.0, label="Eye asymmetry")
        self.asymmJawSlider = gui3d.Slider(self,  position=[20, 240, 9.3], value=0.0, min=-1.0, max=1.0, label="Jaw asymmetry")
        self.asymmMouthSlider = gui3d.Slider(self,  position=[20, 280, 9.3], value=0.0, min=-1.0, max=1.0, label="Mouth asymmetry")
        self.asymmNoseSlider = gui3d.Slider(self,  position=[20, 320, 9.3], value=0.0, min=-1.0, max=1.0, label="Nose asymmetry")
        self.asymmTempleSlider = gui3d.Slider(self,  position=[20, 360, 9.3], value=0.0, min=-1.0, max=1.0, label="Temple asymmetry")
        self.asymmTopSlider = gui3d.Slider(self,  position=[20, 400, 9.3], value=0.0, min=-1.0, max=1.0, label="Top asymmetry")
        self.asymmTrunkSlider = gui3d.Slider(self,  position=[20, 440, 9.3], value=0.0, min=-1.0, max=1.0, label="Trunk asymmetry")
        self.asymmBreastSlider = gui3d.Slider(self,  position=[20, 480, 9.3], value=0.0, min=-1.0, max=1.0, label="Breast asymmetry")

        #Get a list with all targes (complete with path) used in asymm library
        self.asymmDataPath = "data/targets/asym/"
        self.asymmTargets = []
        for f in os.listdir(self.asymmDataPath):
            if os.path.isfile(os.path.join(self.asymmDataPath, f)):
                self.asymmTargets.append(os.path.join(self.asymmDataPath, f))

        #The human mesh
        self.human = self.app.scene3d.selectedHuman

        #Random factor from Slider
        self.randomVal = 0.5
        
        # Modifiers
        self.modifiers = {}
        for bodypart in ["brown", "cheek","ear","eye", "jaw", "mouth","nose","temple","top","trunk","breast"]:
            self.getModifiers(bodypart)
        
        # Undo memory
        self.before = None

        #Sliders events

        @self.asymmBrowSlider.event
        def onChange(value):
            self.changeValue("brown",value)
            
        @self.asymmBrowSlider.event
        def onChanging(value):
            self.changeValue("brown",value,True)

        @self.asymmCheekSlider.event
        def onChange(value):
            self.changeValue("cheek",value)
            
        @self.asymmCheekSlider.event
        def onChanging(value):
            self.changeValue("cheek",value,True)

        @self.asymmEarsSlider.event
        def onChange(value):
            self.changeValue("ear",value)
            
        @self.asymmEarsSlider.event
        def onChanging(value):
            self.changeValue("ear",value,True)

        @self.asymmEyeSlider.event
        def onChange(value):
            self.changeValue("eye",value)
            
        @self.asymmEyeSlider.event
        def onChanging(value):
            self.changeValue("eye",value,True)

        @self.asymmJawSlider.event
        def onChange(value):
            self.changeValue("jaw",value)
            
        @self.asymmJawSlider.event
        def onChanging(value):
            self.changeValue("jaw",value,True)

        @self.asymmMouthSlider.event
        def onChange(value):
            self.changeValue("mouth",value)
            
        @self.asymmMouthSlider.event
        def onChanging(value):
            self.changeValue("mouth",value,True)

        @self.asymmNoseSlider.event
        def onChange(value):
            self.changeValue("nose",value)
            
        @self.asymmNoseSlider.event
        def onChanging(value):
            self.changeValue("nose",value,True)

        @self.asymmTempleSlider.event
        def onChange(value):
            self.changeValue("temple",value)
            
        @self.asymmTempleSlider.event
        def onChanging(value):
            self.changeValue("temple",value,True)

        @self.asymmTopSlider.event
        def onChange(value):
            self.changeValue("top",value)
            
        @self.asymmTopSlider.event
        def onChanging(value):
            self.changeValue("top",value,True)

        @self.asymmTrunkSlider.event
        def onChange(value):
            self.changeValue("trunk",value)
            
        @self.asymmTrunkSlider.event
        def onChanging(value):
            self.changeValue("trunk",value,True)

        @self.asymmBreastSlider.event
        def onChange(value):
            self.changeValue("breast",value)

        @self.asymmBreastSlider.event
        def onChanging(value):
            self.changeValue("breast",value,True)

    def changeValue(self, bodyPartName, value, realtime=False):
        """
        This function apply the targets, and inform the undo system about the changes.
        @return: None
        @type  bodyPartName: String
        @param bodyPartName: Name of the body part to asymmetrise
        @type  value: Float
        @param value: The amount of asymmetry
        """
        if realtime:
            if not self.before:
                self.before = self.getTargetsAndValues(bodyPartName)
                
            self.calcAsymm(value,bodyPartName)
        else:
            self.calcAsymm(value,bodyPartName)
            self.human.applyAllTargets(self.human.app.progress)
            
            after = self.getTargetsAndValues(bodyPartName)
            
            self.app.did(humanmodifier.Action(self.human, self.before, after, self.syncSliders))
            
            self.before = None

    def buildListOfTargetPairs(self, name):
        """
        This function scan all targets and build a list of list:
        [[target1-left,target1-right],...,[targetN-left,targetN-right]]
        @return: List of lists
        @type  name: String
        @param targets: Name of the body part to asymmetrise
        """
        pairs = []
        for f in self.asymmTargets:
            if name in f:
                dirPath = os.path.dirname(f)
                targetName = os.path.splitext(os.path.basename(f))[0]
                prefix = targetName[:-2]
                suffix = targetName[-2:]
                if suffix == "-r":
                    f2 = dirPath + "/" + prefix + "-l.target"
                    pair = [f,f2]
                    pairs.append(pair)
        return pairs


    def getTargetsAndValues(self, bodypart):
        """
        This function return a dictionary with "targetPath:val" items, getting them
        from the human details stack.
        It's used to get both "before" and "after" dictionaries.
        @return: Dictionary
        @type  targets: List
        @param targets: List of targets to get
        """
        modifiers = self.getModifiers(bodypart)
           
        targetsAndValues = {}
        for modifier in modifiers:                
            targetsAndValues[modifier.left] = self.human.getDetail(modifier.left)
            targetsAndValues[modifier.right] = self.human.getDetail(modifier.right)
        return targetsAndValues

    def calcAsymm(self, value, bodypart):
            """
            This function load all asymmetry targets for the specified part of body
            (for example brown, eyes, etc..) and return a dictionary with
            the applied targets, used as "after" parameter in undo system
            @return: Dictionary
            @type  value: Float
            @param value: The amount of asymmetry
            @type  bodypart: String
            @param bodypart: The name of part to asymmetrize.
            """
            modifiers = self.getModifiers(bodypart)
           
            for modifier in modifiers:                
                modifier.setValue(value)
                
    def getModifiers(self, bodypart):
        modifiers = self.modifiers.get(bodypart, None)
        if not modifiers:
            modifiers = []
            targets = self.buildListOfTargetPairs(bodypart)
            for pair in targets:
                modifier = humanmodifier.Modifier(self.human, pair[0], pair[1])
                modifiers.append(modifier)
            self.modifiers[bodypart] = modifiers
        return modifiers
        
    def getSliderValue(self, bodypart):
        modifiers = self.modifiers[bodypart]
        if modifiers:
            return modifiers[0].getValue()
        else:
            return 0.0
            
    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        self.asymmBrowSlider.setFocus()
        self.syncSliders()
            
    def syncSliders(self):
        self.asymmBrowSlider.setValue(self.getSliderValue('brown'))
        self.asymmCheekSlider.setValue(self.getSliderValue('cheek'))
        self.asymmEarsSlider.setValue(self.getSliderValue('ear'))
        self.asymmEyeSlider.setValue(self.getSliderValue('eye'))
        self.asymmJawSlider.setValue(self.getSliderValue('jaw'))
        self.asymmMouthSlider.setValue(self.getSliderValue('mouth'))
        self.asymmNoseSlider.setValue(self.getSliderValue('nose'))
        self.asymmTempleSlider.setValue(self.getSliderValue('temple'))
        self.asymmTopSlider.setValue(self.getSliderValue('top'))
        self.asymmTrunkSlider.setValue(self.getSliderValue('trunk'))
        self.asymmBreastSlider.setValue(self.getSliderValue('breast'))
        
    def onKeyDown(self, event):

        # Undo redo
        if event.key == events3d.SDLK_y:
            self.app.redo()
        elif event.key == events3d.SDLK_z:
            self.app.undo()
            
        gui3d.TaskView.onKeyDown(self, event)

def load(app):
    """
    Plugin load function, needed by design.
    """
    category = app.getCategory('Advanced','button_advance.png','button_advance_on.png')
    taskview = AsymmTaskView(category)
    print 'Asymm loaded'

    #Zoom and pan the camera
    @taskview.event
    def onMouseWheel(event):
        if event.wheelDelta > 0:
            mh.cameras[0].eyeZ -= 0.65
            app.scene3d.redraw()
        else:
            mh.cameras[0].eyeZ += 0.65
            app.scene3d.redraw()

    @taskview.event
    def onMouseDragged(event):
        diff = app.scene3d.getMouseDiff()
        leftButtonDown = event.button & 1
        middleButtonDown = event.button & 2
        rightButtonDown = event.button & 4

        if leftButtonDown and rightButtonDown or middleButtonDown:
            mh.cameras[0].eyeZ += 0.05 * diff[1]
        elif leftButtonDown:
            human = app.scene3d.selectedHuman
            rot = human.getRotation()
            rot[0] += 0.5 * diff[1]
            rot[1] += 0.5 * diff[0]
            human.setRotation(rot)
        elif rightButtonDown:
            human = app.scene3d.selectedHuman
            trans = human.getPosition()
            trans[0] += 0.1 * diff[0]
            trans[1] -= 0.1 * diff[1]
            human.setPosition(trans)



