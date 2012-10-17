#!/usr/bin/python
# -*- coding: utf-8 -*-
# We need this for gui controls

import gui3d
import humanmodifier

print 'Arms and leg imported'

class GroupBoxRadioButton(gui3d.RadioButton):
    def __init__(self, group, label, groupBox, selected=False):
        gui3d.RadioButton.__init__(self, group, label, selected, style=gui3d.ButtonStyle)
        self.groupBox = groupBox
        
    def onClicked(self, event):
        gui3d.RadioButton.onClicked(self, event)
        self.parent.parent.hideAllBoxes()
        self.groupBox.show()
        
class TorsoSlider(humanmodifier.ModifierSlider):
    def __init__(self,modifier, image, view):
        
        humanmodifier.ModifierSlider.__init__(self, min=-1.0, max=1.0, modifier=modifier, style=gui3d.SliderStyle._replace(height=56, normal=image), thumbStyle=gui3d.SliderThumbStyle._replace(height = 32, width = 32, normal="slider2.png", focused="slider2_focused.png"))
        
        self.view = getattr(gui3d.app, view)
        
    def onFocus(self, event):
        
        humanmodifier.ModifierSlider.onFocus(self, event)
        self.view()
        
    def setPosition(self, position):
        
        humanmodifier.ModifierSlider.setPosition(self, position)
        self.thumb.setPosition([position[0], position[1] + self.style.height / 2 - self.thumbStyle.height / 2, position[2] + 0.01])
        self.setValue(self.getValue())

class TorsoTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Torso')
        
        features = [
            ('Torso', [('data/targets/torso/${ethnic}/${gender}_${age}/%s-${value}.target' % (i[0]), i[0], i[1], i[2], 'data/targets/torso/images/', i[3]) for i in
                [                     
                    ('torso-scale-depth', 'decr', 'incr', 'setGlobalCamera'),
                    ('torso-scale-horiz', 'decr', 'incr', 'setGlobalCamera'),
                    ('torso-scale-vert', 'decr', 'incr', 'setGlobalCamera'),
                    ('torso-trans', 'in', 'out', 'setGlobalCamera'),
                    ('torso-trans', 'down', 'up', 'setGlobalCamera'),
                    ('torso-trans', 'forward', 'backward', 'setGlobalCamera'),                          
                                                      
                ]]),   
            ('Hip', [('data/targets/hip/${ethnic}/${gender}_${age}/%s-${value}.target' % (i[0]), i[0], i[1], i[2], 'data/targets/hip/images/', i[3]) for i in
                [                     
                    ('hip-scale-depth', 'decr', 'incr', 'setGlobalCamera'),
                    ('hip-scale-horiz', 'decr', 'incr', 'setGlobalCamera'),
                    ('hip-scale-vert', 'decr', 'incr', 'setGlobalCamera'),
                    ('hip-trans', 'in', 'out', 'setGlobalCamera'),
                    ('hip-trans', 'down', 'up', 'setGlobalCamera'),
                    ('hip-trans', 'forward', 'backward', 'setGlobalCamera'),                          
                                                      
                ]]), 
            ]

        y = 80
        
        self.groupBoxes = []
        self.radioButtons = []
        self.sliders = []
        
        self.modifiers = {}
        
        self.categoryBox = self.addView(gui3d.GroupBox([650, y, 9.0], 'Category'))
        y += 25
        
        for name, templates in features:
            
            for index, template in enumerate(templates):
                
                if index % 12 == 0:
                    
                    if len(templates) <= 12:
                        title = name.capitalize()
                    else:
                        title = '%s %d' % (name.capitalize(), index / 12 + 1)
                        
                    # Create box
                    box = self.addView(gui3d.GroupBox([10, 80, 9.0], title, gui3d.GroupBoxStyle._replace(width=128+112+4)))
                    self.groupBoxes.append(box)
                    
                    # Create radiobutton
                    radio = self.categoryBox.addView(GroupBoxRadioButton(self.radioButtons, title, box, selected=len(self.radioButtons) == 0))
                    y += 24
            
                # Create sliders
                modifier = humanmodifier.GenderAgeEthnicAsymmetricModifier(template[0], 'value', template[2], template[3], False)
                self.modifiers['%s%d' % (name, index + 1)] = modifier

                slider = box.addView(TorsoSlider(modifier, '%s%s-%s-%s.png' % (template[4], template[1], template[2], template[3]), template[5]))
                self.sliders.append(slider)
                
        y += 16

        self.hideAllBoxes()
        self.groupBoxes[0].show()
        
    def hideAllBoxes(self):
        
        for box in self.groupBoxes:
            
            box.hide()
    
    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        
        gui3d.app.setFaceCamera()
        
        for slider in self.sliders:
            slider.update()
            
    def onResized(self, event):
        
        self.categoryBox.setPosition([event.width - 150, self.categoryBox.getPosition()[1], 9.0])
        
    def onHumanChanged(self, event):

        human = event.human

        for slider in self.sliders:
            slider.update()

    def loadHandler(self, human, values):
        
        if values[0] == 'armslegs':
            modifier = self.modifiers.get(values[1].replace("-", " "), None)
            if modifier:
                modifier.setValue(human, float(values[2]))
       
    def saveHandler(self, human, file):
        
        for name, modifier in self.modifiers.iteritems():
            value = modifier.getValue(human)
            if value:
                file.write('armslegs %s %f\n' % (name.replace(" ", "-"), value))
    
def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addView(TorsoTaskView(category))
    
    app.addLoadHandler('armslegs', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

    print 'Armslegs loaded'

def unload(app):
    pass

