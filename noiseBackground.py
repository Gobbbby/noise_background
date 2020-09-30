
import numpy as np
import noise
from sys import stdout
from subprocess import check_output



class noiseBackground:
    def __init__(self, rows, cols):
        self.size = (rows, cols//2)             # dividing by 2 because each pixel takes up 2 characters
        self.scale = 0.5
        self.coordGrids = np.meshgrid(np.linspace(0, 1, self.size[1]), np.linspace(0, 1, self.size[0]))
        self.transitionLoops = 100

        self.noise = np.zeros(self.size)
        self.prevNoise = np.zeros(self.size)
        self.difference = np.zeros(self.size)

        for _ in range(2): self.setNoise()

        self.increments = [
            '  ',
            '\u001b[33m' '..' '\033[0;0m',
            '\u001b[32m' '::' '\033[0;0m',
            '\u001b[34m' 'xx' '\033[0;0m',
            '\u001b[35m' 'XX' '\033[0;0m',
            '\033[1;31m' '@@' '\033[0;0m',
        ]

        self.inRange = lambda n, l, h: l if n < l else n if n < h else h
        self.incrNum = lambda x: self.inRange(int((x*10+6)/2), 0, 5)


    def setNoise(self):
        self.prevNoise = self.noise

        self.noise = np.vectorize(noise.pnoise2)(                               # applying perlin noise
                                                 self.coordGrids[1]/self.scale,
                                                 self.coordGrids[0]/self.scale,
                                                 octaves=1,
                                                 persistence=0.5,
                                                 lacunarity=2.0,
                                                 repeatx=self.size[1],
                                                 repeaty=self.size[0],
                                                 base=np.random.randint(0,100)
                                                 )

        self.difference = self.noise - self.prevNoise
        self.difference /= self.transitionLoops


    def __str__(self):
        string = '\n'
        for row in self.prevNoise:
            for cell in row:
                try:
                    string += self.increments[self.incrNum(cell)]
                except:
                    print(self.incrNum(cell))
            string += '\n'
        return string



rows, cols = map(int, check_output(['stty', 'size']).split())       # getting the rows and columns of the terminal window, and converting them to integer

noiseB = noiseBackground(rows-2, cols)                      # subtracting 2 because it "overshoots" by 2, in the case of this program (it starts scrolling)

stdout.write(f'\u001b[1J')                                  # clearing the screen
stdout.write(f'\u001b[999A')                                # going to the top of the screen
stdout.write('\u001b[s')                                    # saving the position



while True:
    for _ in range(noiseB.transitionLoops):
        stdout.write(str(noiseB))
        stdout.write('\u001b[u')                            # going back to the saved position
        noiseB.prevNoise += noiseB.difference
    noiseB.setNoise()