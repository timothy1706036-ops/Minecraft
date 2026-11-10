from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.load_models()
        self.make_world()
        self.crosshair()

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


game = Game()
game.run()