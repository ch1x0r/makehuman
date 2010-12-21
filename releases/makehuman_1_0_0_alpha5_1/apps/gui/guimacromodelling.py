#!/usr/bin/python
# -*- coding: utf-8 -*-
import gui3d, time
import animation3d
import humanmodifier
import mh

class MacroAction:

    def __init__(self, human, method, value, postAction,update=True):
        self.name = method
        self.human = human
        self.method = method
        self.before = getattr(self.human, 'get' + self.method)()
        self.after = value
        self.postAction = postAction
        self.update = update

    def do(self):
        getattr(self.human, 'set' + self.method)(self.after)
        self.human.applyAllTargets(self.human.app.progress, update=self.update)
        self.postAction()
        return True

    def undo(self):
        getattr(self.human, 'set' + self.method)(self.before)
        self.human.applyAllTargets(self.human.app.progress)
        self.postAction()
        return True


class EthnicAction:

    def __init__(self, human, ethnic, value, postAction):
        self.name = 'Change %s to %d' % (ethnic, value)
        self.human = human
        self.ethnic = ethnic
        self.before = human.getEthnic(ethnic)
        self.after = value
        self.postAction = postAction

    def do(self):
        self.human.setEthnic(self.ethnic, self.after)
        self.human.applyAllTargets(self.human.app.progress)
        self.postAction()
        return True

    def undo(self):
        self.human.setEthnic(self.ethnic, self.before)
        self.human.applyAllTargets(self.human.app.progress)
        self.postAction()
        return True

class EthnicMapButton(gui3d.RadioButton):

    def __init__(self, group, parent, mesh='data/3dobjs/button_standard.obj', texture=None, selectedTexture=None, position=[0, 0, 9], selected=False):
        gui3d.RadioButton.__init__(self, group, parent, mesh, texture, selectedTexture, position, selected)
        self.button.setRotation([180, 0, 0])

    def onSelected(self, selected):
        if selected:
            pos = self.button.getPosition()
            t = animation3d.Timeline(0.250)
            t.append(animation3d.PathAction(self.button.mesh, [pos, [pos[0] - 300, pos[1] + 100, pos[2]]]))
            t.append(animation3d.ScaleAction(self.button.mesh, [1, 1, 1], [5, 5, 5]))
            t.append(animation3d.UpdateAction(self.app.scene3d))
            t.start()
        else:
            pos = self.button.getPosition()
            t = animation3d.Timeline(0.250)
            t.append(animation3d.PathAction(self.button.mesh, [pos, [pos[0] + 300, pos[1] - 100, pos[2]]]))
            t.append(animation3d.ScaleAction(self.button.mesh, [5, 5, 5], [1, 1, 1]))
            t.append(animation3d.UpdateAction(self.app.scene3d))
            t.start()

    def onMouseDown(self, event):
        human = self.app.scene3d.selectedHuman
        if self.selected:
            faceGroupSel = self.app.scene3d.getSelectedFacesGroup()
            faceGroupName = faceGroupSel.name
            print faceGroupName
            if 'dummy' in faceGroupName:
                self.setSelected(False)
            else:
                if self.parent.ethnicIncreaseButton.selected:
                    self.app.do(EthnicAction(human, faceGroupName, human.getEthnic(faceGroupName) + 0.1, self.syncEthnics))
                elif self.parent.ethnicDecreaseButton.selected:
                    self.app.do(EthnicAction(human, faceGroupName, human.getEthnic(faceGroupName) - 0.1, self.syncEthnics))
                else:
                    self.app.do(EthnicAction(human, faceGroupName, 0.0, self.syncEthnics))
        else:
            self.setSelected(True)

    def onBlur(self, event):
        pass

    # self.setSelected(False)

    def onMouseUp(self, event):
        pass

    def syncEthnics(self):
        human = self.app.scene3d.selectedHuman
        ethnics = human.targetsEthnicStack

    # Calculate the ethnic target value, and store it in dictionary

        obj = self.button.mesh

    # We first clear the non applied ethnics

        for g in obj.facesGroups:
            if g.name not in ethnics:
                g.setColor([255, 255, 255, 255])

    # Then we color the applied ethnics, doing it in two steps makes sure we don't erase our coloring

        for g in obj.facesGroups:
            if g.name in ethnics:
                color = [int(255 * ethnics[g.name]), 1 - int(255 * ethnics[g.name]), 255, 255]
                g.setColor(color)


class MacroModelingTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Macro modelling', category.app.getThemeResource('images', 'macro.png'), category.app.getThemeResource('images',
                                'macro_on.png'))

        self.status = gui3d.TextView(self, mesh='data/3dobjs/empty.obj', position=[10, 575, 9.1])

        gui3d.Object(self, 'data/3dobjs/unit_square.obj', self.app.getThemeResource('images', 'group_main.png'), [10, 80, 9.0], 128,256)
        gui3d.Object(category, 'data/3dobjs/unit_square.obj', self.app.getThemeResource('images', 'group_actions.png'), [10, 472, 9.0], 128,64)
        #gui3d.Object(self, 'data/3dobjs/unit_square.obj', self.app.getThemeResource('images', 'group_ethnics.png'), [10, 340, 9.0],128,128)

    # Macro sliders

        self.genderSlider = gui3d.Slider(self, position=[10, 105, 9.3], value=0.5, label = "Gender")
        self.ageSlider = gui3d.Slider(self, position=[10, 145, 9.01], value=0.5, label = "Age")
        self.muscleSlider = gui3d.Slider(self, position=[10, 190, 9.02], value=0.5, label = "Tone")
        self.weightSlider = gui3d.Slider(self, position=[10, 235, 9.03], value=0.5, label = "Weight")
        self.heightSlider = gui3d.Slider(self, position=[10, 280, 9.04], value=0.5, label = "Height")

        #hair update only necessary for : gender, age , height
        
        @self.genderSlider.event
        def onChange(value):
            human = self.app.scene3d.selectedHuman
            self.app.do(MacroAction(human, 'Gender', value, self.syncSliders,False))
            self.syncStatus()
            if human.hairObj:
                fileChooser=self.app.categories["Library"].tasksByName["Hair"].filechooser
                if fileChooser.files:
                    fileChooser.onFileSelected(fileChooser.files[fileChooser.selectedFile],update=1)
            human.meshData.update()
            if human.hairObj: human.hairObj.update()


        @self.ageSlider.event
        def onChange(value):
            human = self.app.scene3d.selectedHuman
            self.app.do(MacroAction(human, 'Age', value, self.syncSliders,False))
            self.syncStatus()
            if human.hairObj:
                fileChooser=self.app.categories["Library"].tasksByName["Hair"].filechooser
                if fileChooser.files:
                    fileChooser.onFileSelected(fileChooser.files[fileChooser.selectedFile],update=1)
            human.meshData.update()
            if human.hairObj: human.hairObj.update()

        @self.muscleSlider.event
        def onChange(value):
            human = self.app.scene3d.selectedHuman
            self.app.do(MacroAction(human, 'Muscle', value, self.syncSliders))
            self.syncStatus()

        @self.weightSlider.event
        def onChange(value):
            human = self.app.scene3d.selectedHuman
            self.app.do(MacroAction(human, 'Weight', value, self.syncSliders))
            self.syncStatus()

        @self.heightSlider.event
        def onChange(value):
            human = self.app.scene3d.selectedHuman
            before = {}
            before['data/targets/macrodetails/universal-stature-dwarf.target'] = human.getDetail('data/targets/macrodetails/universal-stature-dwarf.target')
            before['data/targets/macrodetails/universal-stature-giant.target'] = human.getDetail('data/targets/macrodetails/universal-stature-giant.target')
            modifier = humanmodifier.Modifier(human, 'data/targets/macrodetails/universal-stature-dwarf.target',
                                              'data/targets/macrodetails/universal-stature-giant.target')
            modifier.setValue(value * 2 - 1,update=0)
            after = {}
            after['data/targets/macrodetails/universal-stature-dwarf.target'] = human.getDetail('data/targets/macrodetails/universal-stature-dwarf.target')
            after['data/targets/macrodetails/universal-stature-giant.target'] = human.getDetail('data/targets/macrodetails/universal-stature-giant.target')
            self.app.did(humanmodifier.Action(human, before, after, self.syncSliders,update=False))
            human.applyAllTargets(self.app.progress,update=False)
            #Best method is to reload hair and readjust.. other methods arent very convincing
            #May be expensive? since our changes are not realtime we can live with it for the time being
            if human.hairObj:
                fileChooser=self.app.categories["Library"].tasksByName["Hair"].filechooser
                if fileChooser.files:
                    fileChooser.onFileSelected(fileChooser.files[fileChooser.selectedFile],update=1)
            #self.app.categories["Library"].tasksByName["Hair"].adjustHairObj(human.hairObj, human.meshData)
            human.meshData.update()
            if human.hairObj : human.hairObj.update()
            #self.app.scene3d.redraw(True)


    # Ethnic controls
        '''
        self.ethnicMapButtonGroup = []
        self.asiaButton = EthnicMapButton(self, self.ethnicMapButtonGroup, mesh='data/3dobjs/button_asia.obj', texture=self.app.getThemeResource('images',
                                          'button_asia.png'), position=[630, 150, 9])
        self.europeButton = EthnicMapButton(self, self.ethnicMapButtonGroup, mesh='data/3dobjs/button_europe.obj', texture=self.app.getThemeResource('images',
                                            'button_europe.png'), position=[690, 150, 9])
        self.africaButton = EthnicMapButton(self, self.ethnicMapButtonGroup, mesh='data/3dobjs/button_africa.obj', texture=self.app.getThemeResource('images',
                                            'button_africa.png'), position=[630, 210, 9])
        self.americaButton = EthnicMapButton(self, self.ethnicMapButtonGroup, mesh='data/3dobjs/button_america.obj', texture=self.app.getThemeResource('images',
                                             'button_america.png'), position=[690, 210, 9])
        self.ethnicButtonGroup = []
        self.ethnicIncreaseButton = gui3d.RadioButton(self, self.ethnicButtonGroup, mesh='data/3dobjs/button_standard_little.obj',
                                                      texture=self.app.getThemeResource('images', 'button_ethnincr.png'),
                                                      selectedTexture=self.app.getThemeResource('images', 'button_ethnincr_on.png'), position=[750, 140, 9],
                                                      selected=True)
        self.ethnicDecreaseButton = gui3d.RadioButton(self, self.ethnicButtonGroup, mesh='data/3dobjs/button_standard_little.obj',
                                                      texture=self.app.getThemeResource('images', 'button_ethndecr.png'),
                                                      selectedTexture=self.app.getThemeResource('images', 'button_ethndecr_on.png'), position=[750, 180, 9])
        '''
    # Common controls

        self.background = gui3d.Object(category, 'data/3dobjs/background.obj', position=[400, 300, -89.98])

        self.currentHair = gui3d.Button(category, mesh='data/3dobjs/button_standard_little.obj', texture=self.app.scene3d.selectedHuman.hairFile.replace('.hair', '.png'
                                        ), position=[600, 580, 9.2])

        @self.currentHair.event
        def onClicked(event):
            self.app.switchCategory('Library')
            self.app.scene3d.redraw(1)

        self.backgroundImage = gui3d.Object(category, 'data/3dobjs/background.obj', position=[400, 300, 1], visible=False)
        self.backgroundImageToggle = gui3d.ToggleButton(category, mesh='data/3dobjs/button_standard.obj', position=[33, 522, 9.1],
                                                        texture=self.app.getThemeResource('images', 'button_background_toggle.png'),
                                                        selectedTexture=self.app.getThemeResource('images', 'button_background_toggle_on.png'),
                                                        focusedTexture=self.app.getThemeResource('images', 'button_background_toggle_focused.png'))

        @self.backgroundImageToggle.event
        def onClicked(event):
            if self.backgroundImage.isVisible():
                self.backgroundImage.hide()
                self.backgroundImageToggle.setSelected(False)
            elif self.backgroundImage.hasTexture():
                self.backgroundImage.show()
                self.backgroundImageToggle.setSelected(True)
            else:
                self.app.switchCategory('Library')
                self.app.switchTask('Background')
            self.app.scene3d.redraw(1)
            
        self.anaglyphsButton = gui3d.ToggleButton(category, mesh='data/3dobjs/button_standard.obj', texture=self.app.getThemeResource('images', 'button_3dglasses.png'),
                                       selectedTexture=self.app.getThemeResource('images', 'button_3dglasses_on.png'), position=[68, 522, 9.1])

        @self.anaglyphsButton.event
        def onClicked(event):
            stereoMode = mh.cameras[0].stereoMode
            stereoMode += 1
            if stereoMode > 2:
                stereoMode = 0
            mh.cameras[0].stereoMode = stereoMode
            
            # We need a black background for stereo
            background = self.app.categories["Modelling"].tasksByName["Macro modelling"].background
            if stereoMode:
                color = [  0,   0,   0, 255]
                self.anaglyphsButton.setSelected(True)
            else:
                color = [100, 100, 100, 255]
                self.anaglyphsButton.setSelected(False)
            for g in background.mesh.facesGroups:
                g.setColor(color)

            self.app.scene3d.redraw()
            
    # Ethnics buttons
        '''
        self.ethnicsGroup = []
        self.asianButton = gui3d.RadioButton(self, self.ethnicsGroup, mesh='data/3dobjs/button_standard_big.obj', texture=self.app.getThemeResource('images',
                                             'button_african.png'), selectedTexture=self.app.getThemeResource('images', 'button_african_on.png'), position=[49, 372, 9.1])
        self.africanButton = gui3d.RadioButton(self, self.ethnicsGroup, mesh='data/3dobjs/button_standard_big.obj', texture=self.app.getThemeResource('images',
                                               'button_asian.png'), selectedTexture=self.app.getThemeResource('images', 'button_asian_on.png'), position=[49, 392, 9.1])
        self.caucas1Button = gui3d.RadioButton(self, self.ethnicsGroup, mesh='data/3dobjs/button_standard_big.obj', texture=self.app.getThemeResource('images',
                                               'button_caucas1.png'), selectedTexture=self.app.getThemeResource('images', 'button_caucas1_on.png'), position=[49, 412,
                                               9.1])
        self.caucas2Button = gui3d.RadioButton(self, self.ethnicsGroup, mesh='data/3dobjs/button_standard_big.obj', texture=self.app.getThemeResource('images',
                                               'button_caucas2.png'), selectedTexture=self.app.getThemeResource('images', 'button_caucas2_on.png'), position=[49, 432,
                                               9.1])
        self.pacificButton = gui3d.RadioButton(self, self.ethnicsGroup, mesh='data/3dobjs/button_standard_big.obj', texture=self.app.getThemeResource('images',
                                               'button_pacific.png'), selectedTexture=self.app.getThemeResource('images', 'button_pacific_on.png'), position=[49, 452,
                                               9.1])
        self.ethnicResetButton = gui3d.Button(self, mesh='data/3dobjs/button_standard.obj', texture=self.app.getThemeResource('images', 'button_ethnreset.png'),
                                              selectedTexture=self.app.getThemeResource('images', 'button_ethnreset_on.png'), position=[100, 452, 9.1])
        '''
        self.syncSliders()
        self.syncStatus()

    def syncSliders(self):
        human = self.app.scene3d.selectedHuman
        self.genderSlider.setValue(human.getGender())
        self.ageSlider.setValue(human.getAge())
        self.muscleSlider.setValue(human.getMuscle())
        self.weightSlider.setValue(human.getWeight())
        modifier = humanmodifier.Modifier(human, 'data/targets/macrodetails/universal-stature-dwarf.target', 'data/targets/macrodetails/universal-stature-giant.target')
        self.heightSlider.setValue(0.5 + modifier.getValue() / 2.0)

    def syncEthnics(self):
        #self.asiaButton.syncEthnics()
        #self.europeButton.syncEthnics()
        #self.africaButton.syncEthnics()
        #self.americaButton.syncEthnics()
        pass

    def syncStatus(self):
        human = self.app.scene3d.selectedHuman
        status = ''
        if human.getGender() == 0.5:
            gender = 'Gender: neutral, '
        else:
            gender = 'Gender: %.2f%% female, %.2f%% male, ' % ((1.0 - human.getGender()) * 100, human.getGender() * 100)
        status += gender
        if human.getAge() < 0.5:
            age = 12 + ((25 - 12) * 2) * human.getAge()
        else:
            age = 25 + ((70 - 25) * 2) * (human.getAge() - 0.5)
        status += 'Age: %d, ' % age
        status += 'Muscle: %.2f%%, ' % (human.getMuscle() * 100.0)
        status += 'Weight: %.2f%%' % (50 + (150 - 50) * human.getWeight())
        self.status.setText(status)

    def onShow(self, event):
        self.genderSlider.setFocus()
        gui3d.TaskView.onShow(self, event)

