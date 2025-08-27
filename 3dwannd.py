import bpy
import json
import os
import sys
import time
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add




sys.path.append( '/home/yoyo/Apps/blender3dWannd' )

pSrc = ['/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/home/yoyo/.local/lib/python3.8/site-packages', '/usr/local/lib/python3.8/dist-packages', '/usr/local/lib/python3.8/dist-packages/youtube_dl-2021.12.17-py3.8.egg', '/usr/local/lib/python3.8/dist-packages/qtile-0.22.2.dev202+g0dc89418-py3.8-linux-x86_64.egg', '/usr/local/lib/python3.8/dist-packages/Box2D-2.3.10-py3.8-linux-x86_64.egg', '/usr/local/lib/python3.8/dist-packages/python_for_android-2024.1.21-py3.8.egg', '/usr/local/lib/python3.8/dist-packages/build-1.2.2.post1-py3.8.egg', '/usr/local/lib/python3.8/dist-packages/pyproject_hooks-1.2.0-py3.8.egg', '/usr/lib/python3/dist-packages']
for p in pSrc:
    sys.path.append( p )
sys.path.append( '/home/yoyo/Apps/viteyss-site-3dWannd/bin/' )

import base64
import wsHelper
from threading import Thread
import mainb
import cv2


aaContext = -1
def add_object(context, mname, vecP = 1):
    global aaContext
    if context != -1:
        aaContext = context
    else:
        context = aaContext
        
    scale_x = 1
    scale_y = 1

    verts = [
        Vector((-vecP * scale_x, vecP * scale_y, 0)),
        Vector((vecP * scale_x, vecP * scale_y, 0)),
        Vector((vecP * scale_x, -vecP * scale_y, 0)),
        Vector((-vecP * scale_x, -vecP * scale_y, 0)),
    ]

    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name=mname)
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh)
    
    

fpsRunnerRun = False
circleObj = -1
def fpsRunner( dwannd ):
    global fpsRunnerRun
    
    if fpsRunnerRun:
        print("fpsRunnerRunning ...")
        return 1
    
    fpsRunnerRun = True
    
    def run(*args):
        global fpsRunnerRun
        global circleObj
        
        currF = 0
        cap = -1
        while fpsRunnerRun:
            
            #print(['runner', 'currF', currF, '/', dwannd.streamCurrentFrame ])
            time.sleep(.1)
            
            gotF = dwannd.streamCurrentFrame
            
            if (gotF - currF) > 40 and cap == -1:
                print('load file ....')
                cap = cv2.VideoCapture( dwannd.tmpFile )
                
            if (gotF - currF) > 50:
                over = (gotF - currF)
                print(['process... over',over])

                for f in range( 0, over-50):
                    #print(['process... currF',currF])
                    ret, frame = cap.read()
                    if (f%3) == 0:
                        mainb.DoProcess( frame )
                        dwannd.avgP = mainb.avgP                
                        dwannd.accu = mainb.acuLevel
                        
                        if circleObj != -1 and len( dwannd.avgP ) == 3:
                            circleObj.location = dwannd.avgP
                            if dwannd.accu > 0.001:
                                circleObj.scale = [ dwannd.accu,dwannd.accu,1.0]
                        time.sleep(0.02)
                
                    if gotF != -1:
                        currF+=1
                
                
        print(f"fpsRunner DONE...f{dwannd.streamCurrentFrame}")
            
        fpsRunnerRun = False
        
        if cap != -1:
            cap.release()
            cap = -1
    
    Thread( target=run ).start()
    
    


class dwannd:
    
    def __init__(self):
        
        self.connected = False
        self.avgP = [0,0,0]
        self.accu = 1.0
        
        self.tmpFile = '/tmp/bpyOcv.tmp'
        
        self.wsHostUrl = "wss://192.168.43.220:8080/fooWSS"
        self.wsClientID = 'b3d'
        self.wsH = -1
        self.ws = -1
        self.wsHStatus = 'not use'
        
        self.mediaChunks = []
        self.streamCurrentFrame = -1
        self.POIC = 1
        
        self.frameProcess = 0
        
        global fpsRunnerRun
        self.fpsR = fpsRunnerRun
        
        
        self.cl('init...')
        self.cl(["os current directory",os.getcwd()])

        
        
    def cl(self, str):
        print(['bpy 3dwannd', str])
        
    def getStatus(self):
        self.cl(['getStatus',self.wsH])
        if self.wsH != -1:
            return f"ws"
        else:
            return "--"
        
    def start(self):
        self.cl('got START')
        
        
        self.cl(f"clean tmp file: {self.tmpFile}")
        try:
            os.remove( self.tmpFile )
        except:
            self.cl("  no tmp file. First run ?")
        
        self.wsH = wsHelper.wsStart(
            self.on_message,
            self.wsClientID,
            host=self.wsHostUrl
        )
        self.wsHStatus ='connecting...'
        fpsRunner(self)
        
    
        
    def stop(self):
        
        self.cl('got STOP')
        self.cl(['wsH is',self.wsH])
        self.wsH.close()
        self.wsHStatus = 'down...'
        self.wsH = -1
        self.streamCurrentFrame = -1
        global fpsRunnerRun
        fpsRunnerRun = False

    def on_message( self, ws, msg ):
        #self.cl(['on_message',msg])
        self.ws = ws
        self.wsHStatus = 'ok'        
        
        j = json.loads( msg )
        if j['topic'] == 'dziHarv/mediaStream':
            self.mediaChunks.append( j['totalFrames'] )
            self.streamCurrentFrame = j['totalFrames']
            #print(['totalFrames',j['totalFrames']])

            with open(self.tmpFile, 'ab') as f:
                f.write( base64.b64decode( j['chunk'] ) )
            
        elif j['topic'] == 'bt/SetPOI':
            nTemp = f"POI_{self.POIC}"
            self.POIC+= 1
            add_object(-1, nTemp, 0.01)
            global aaContext
            tmpObj = aaContext.scene.objects.get(nTemp,-1)
            if tmpObj != -1:
                tmpObj.location = self.avgP
            
        
        

wan = -1


class dwanndStartOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "dwannd.start" # <- put this string in layout.operator()
    bl_label = "Start it" # <- button name

    @classmethod
    def poll(cls, context):
        global wan
        if wan.wsH == -1:
            return 'ok'
        else:
            return ''

    def execute(self, context):
        
        global circleObj
        if circleObj == -1:
        
            circleObj = context.scene.objects.get('3dWannd',-1)
            if circleObj == -1:
                add_object( context, '3dWannd')
                circleObj = context.scene.objects['3dWannd']
        
        global wan
        wan.start()
        return {'FINISHED'}
    

class dwanndStopOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "dwannd.stop" # <- put this string in layout.operator()
    bl_label = "Stop it" # <- button name

    @classmethod
    def poll(cls, context):
        global wan
        if wan.wsH == -1:
            return ''
        else:
            return 'ok'

    def execute(self, context):
        global wan
        wan.stop()
        return {'FINISHED'}
    

    




class Layout3dWanndPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "3d Wannd"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #layout.label(text="3D Wannd:")

        row = self.layout.row()
        row.label(text = f"As ({context.scene.wan.wsClientID}):")
        row.label( text=f"ws: {context.scene.wan.wsHStatus}" )
        
        row = self.layout.row()        
        row.operator( 'dwannd.start', text='Start' )
        row.operator( 'dwannd.stop', text='Stop' )
        
        layout.label( text=f"accu: {context.scene.wan.accu}" )
        layout.label( text=f"avgP: {context.scene.wan.avgP}" )
        layout.label( text=f"stream frame: {context.scene.wan.streamCurrentFrame} R:{context.scene.fpsRunnerRun}" )
        
        
        #row = self.layout.row()
        
        #row.label( text=f"wsH: {context.scene.wan.wsHStatus}" )
        
        

def register():
    bpy.utils.register_class(Layout3dWanndPanel)
    bpy.utils.register_class(dwanndStartOperator)
    bpy.utils.register_class(dwanndStopOperator)
    #bpy.utils.register_class(dwanndWsStatusOperator)
    global wan
    global fpsRunnerRun
    wan = dwannd()
    
    bpy.types.Scene.wan = wan
    bpy.types.Scene.fpsRunnerRun = fpsRunnerRun
    print("register")


def unregister():
    bpy.utils.unregister_class(Layout3dWanndPanel)
    bpy.utils.unregister_class(dwanndStartOperator)
    bpy.utils.register_class(dwanndStopOperator)
    #bpy.utils.unregister_class(dwanndWsStatusOperator)
    
    del bpy.types.Scene.wan
    del bpy.types.Scene.fpsRunnerRun
    global wan
    wan.stop()
    wan = -1
        
    print("unregister")


if __name__ == "__main__":
    register()
