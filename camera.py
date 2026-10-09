from settings import WIDTH, HIGHT, CAMERA_SMOOTH 

class Camera:
    def __init__(self, world_width, world_height):
        # how big is the whole map is in pixels 
        self.world_width = world_width
        self.world_height = world_height 


        # x and y are the top left corner of what the screen is showing
        self.x = 0.0
        self.y = 0.0

        def snap(self, target_x, target_y,):
            # jump straight to the target, used when the game starts 
            self.x = target_x - WIDTH / 2
            self.y = target_y - HEIGHT / 2
            self.clamp()

            def follow(self, target_x, target_y, dt):
                want_x = target_x - WIDTH / 2
                want_y = target_y - HEIGHT / 2

                # move a little bit toword the target every frame instead of jumping 
                # the smaller the number the more floaty the camera feels 
                amount = min(1, CAMERA_SMOOTH * dt)
                self.x += (want_x - self.x) * amount 
                self.y += (want_y - self.y) * amount

                self.clap()

            def clamp(self):
                #dont show anything outside the map
                self.x =max(0, min(self.world_width - WIDTH,self.x))
                self.y =max(0,min(self.world_height - HEIGHT,self.y))

            def apply(self, rect):
                #moving a rect from world space to sscreen space 
                return rect.move(-int(round(self.x)), -int(round(self.y)))
            