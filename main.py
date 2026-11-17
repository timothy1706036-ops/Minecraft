from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import DirectionalLight
from panda3d.core import AmbientLight
from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionNode, CollisionRay, CollisionBox

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.mouse_locked = False
        self.load_models()
        self.Lighting()
        self.make_world()
        self.crosshair()
        self.Camera()
        self.setup_raycast()
        self.button = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.control()
        self.lock_mouse()
        self.taskMgr.add(self.update, "update")

    def load_models(self):
        self.grass = self.loader.loadModel("grass-block.glb")
        self.grass.setHpr(0, 90, 0)
        self.dirt = self.loader.loadModel("dirt-block.glb")
        self.sand = self.loader.loadModel("sand-block.glb")
        self.stone = self.loader.loadModel("stone-block.glb")

    def make_block(self, block_type, position):
        if block_type == "grass":
            block = self.grass.copyTo(self.render)
        elif block_type == "dirt":
            block = self.dirt.copyTo(self.render)
        elif block_type == "sand":
            block = self.sand.copyTo(self.render)
        elif block_type == "stone":
            block = self.stone.copyTo(self.render)
        else:
            raise ValueError(f"Unknown block type: {block_type}")

        solid = block.attachNewNode(CollisionNode("block"))
        solid.node().addSolid(CollisionBox((0, 0, 0), 0.5, 0.5, 0.5))
        solid.setPythonTag("owner", block)
        block.setPos(position)
        return block

    def make_world(self):
        for x in range(-5, 6):
            for y in range(-5, 6):
                if (x + y) % 2 == 0:
                    self.make_block("grass", (x, y, 0))

    def crosshair(self):
        c = OnscreenImage(image="Crosshair.png", pos=(0, 0, 0), scale=0.05)
        c.setTransparency(TransparencyAttrib.MAlpha)

    def Lighting(self):
        sun = DirectionalLight("sun")
        sun.setColor((0.8, 0.8, 0.8, 1))
        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-45, -45, 0)
        self.render.setLight(sun_node)
        
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
        ambient_node = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_node)

    def Camera(self):
        self.camLens.setFov(75)

    def update(self, task):
        dt = globalClock.getDt()
        speed = 14.0

        if self.button["forward"]:
            self.camera.setY(self.camera, speed * dt)
        if self.button["backward"]:
            self.camera.setY(self.camera, -speed * dt)
        if self.button["left"]:
            self.camera.setX(self.camera, -speed * dt)
        if self.button["right"]:
            self.camera.setX(self.camera, speed * dt)
        if self.button["up"]:
            self.camera.setZ(self.camera, speed * dt)
        if self.button["down"]:
            self.camera.setZ(self.camera, -speed * dt)
        if self.mouse_locked and self.mouseWatcherNode and self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            cx = self.win.getXSize() // 2
            cy = self.win.getYSize() // 2
            dx = md.getX() - cx
            dy = md.getY() - cy

            sensitivity = 0.15
            self.camera.setH(self.camera.getH() - dx * sensitivity)
            self.camera.setP(self.camera.getP() - dy * sensitivity)
            self.camera.setP(max(85, max(-85, self.camera.getP())))
            self.win.movePointer(0, cx, cy)
            self.ctrav.traverse(self.render)
        return task.cont if task else None


    def set_button(self, action, value):
        self.button[action] = value

    def control(self):
        mapping = {
            "w": "forward",
            "s": "backward",
            "a": "left",
            "d": "right",
            "space": "up",
            "shift": "down"
        }
        for key, action in mapping.items():
            self.accept(key, self.set_button, [action, True])
            self.accept(f"{key}-up", self.set_button, [action, False])
            self.accept("escape", self.toggle_mouse)

        self.accept('mouse1', self.break_block)
    def lock_mouse(self):
        if hasattr(self.win, "requestProperties"):
            props = WindowProperties()
            props.setCursorHidden(True)
            self.win.requestProperties(props)
        self.mouse_locked = True

    def unlock_mouse(self):
        if hasattr(self.win, "requestProperties"):
            props = WindowProperties()
            props.setCursorHidden(False)
            self.win.requestProperties(props)
        self.mouse_locked = False

    def toggle_mouse(self):
        if self.mouse_locked:
            self.unlock_mouse()
        else:
            self.lock_mouse()

    def change_mouse_status(self, action, active):
        self.press[action] = active

    def setup_raycast(self):
        self.ctrav = CollisionTraverser()
        self.rayQueue = CollisionHandlerQueue()

        light = CollisionRay(0, 0, 0, 0, 1, 0)
        light_node = CollisionNode("lightRay")
        light_node.addSolid(light)
        light_path = self.camera.attachNewNode(light_node)
        self.ctrav.addCollider(light_path, self.rayQueue)

    def break_block(self):
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            entry = self.rayQueue.getEntry(0)
            block = entry.getIntoNodePath().getPythonTag("owner")

            if block and self.camera.getDistance(block) < 14:
                block.removeNode()
                print("Block broken!")
        


    

    
game = Game()
game.run()