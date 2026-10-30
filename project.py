import soundcard as sc #main recording library
import numpy as np #main grid formulating library
import time #to capture the frames at a certain threshold
import pygame #to create the display and edit it
import random #randomizing selecti  onss of colors
import threading 
import queue

color_palette = [
    (0, 100, 255),    # Electric blue
    (0, 240, 255),    # Cyan
    (140, 0, 255),    # Purple
    (255, 0, 180),    # Magenta
    (255, 50, 120),   # Hot pink
    (90, 50, 255),    # Violet
    (0, 255, 120),    # Neon green
    (120, 255, 0),    # Lime green
    (0, 200, 130),    # Emerald green
    (0, 180, 190),    # Teal
    (80, 255, 200),   # Mint
    (255, 120, 0),    # Bright orange
    (255, 70, 0),     # Red-orange
    (255, 190, 0),    # Amber
    (255, 245, 0),    # Neon yellow
    (255, 30, 60)     # Crimson red
] #all the colors 

class Particle:
    def __init__(self, x, y, vx, vy, size, lifetime, color): #Initializes every single object in the code thats relevant
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.lifetime = lifetime
        self.color = color
        self.glow_surface = pygame.Surface((40,40), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surface, ((self.color[0], self.color[1], self.color[2], 15)), (20,20), 16)
        pygame.draw.circle(self.glow_surface, ((self.color[0], self.color[1], self.color[2], 35)), (20,20), 11)
        pygame.draw.circle(self.glow_surface, ((self.color[0], self.color[1], self.color[2], 180)), (20,20), 3)
    def update(self): #defines each distance object as well as the lifetime object also handles the random segmefnt of each vx and vy (velocity)
        self.vx += random.uniform(-0.04, 0.04)
        self.vy += random.uniform(-0.04, 0.04)
        self.x = self.x + self.vx
        self.y = self.y + self.vy
        self.lifetime = self.lifetime - 1
    
    def draw(self, screen): #draw
        screen.blit(self.glow_surface, ((int(self.x - 20)), (int(self.y - 20)))) #blit means draw




def record_audio(audio_queue, stop_event): #different function/process for recording audio to decrease lag 
    mic = sc.default_microphone()
    while not stop_event.is_set(): #keep repeating the loop while stop signal not set
        data = mic.record(numframes=4800, samplerate=48000)
        rms = np.sqrt(np.mean(data ** 2))
        audio_queue.put(rms)


def main():#The actual loop that the program loops the rms on
    psv = 0.0
    alpha = 0.8
    grid = np.zeros((360, 640))
    centre_row = grid.shape[0] // 2
    centre_column = grid.shape[1] // 2
    grid[centre_row, centre_column] = 10 #initial energy at center
    fade_factor = 0.97
    pygame.init()
    screen = pygame.display.set_mode((640, 360), pygame.SCALED | pygame.FULLSCREEN)
    trail_surface = pygame.Surface((640, 360), pygame.SRCALPHA)
    trail_surface.fill((0, 0, 0, 0))

    clock = pygame.time.Clock()
    running = True
    particles = []
    stop_event = threading.Event() #starts event as unset
    audio_queue = queue.Queue() #Creates the queue (mailbox for sending and receving data)
    audio_thread = threading.Thread(target=record_audio, args=(audio_queue, stop_event)) #target tells which function to execute args tells u which functions to track when executing
    audio_thread.start()    
    while running:
        for event in pygame.event.get():
         if event.type == pygame.QUIT:
            running = False
            stop_event.set() #calls stop event as unset and then exits the loop
        new_audio = False
        try:
            rms = audio_queue.get_nowait() #recieves the recent rms values
            new_audio = True
        except queue.Empty: #even if its empty it runs and draws visuals
            pass
        if new_audio:
            nv = normalize(rms) #calls the normalize function (Normalized value)
            nsv = smoothing(nv, psv, alpha) #takes in all the values in function
            psv = nsv #previous value turns into new value
            if nsv > 0.1:
                loudness_scale = (nsv - 0.1) / 0.9 #how loud it is 
                speed_scale = 0.5 + (loudness_scale / 2) #the speed of the spreading
                particle_count = 1 + int(loudness_scale * 5) #how many particles 
                for i in range(particle_count):
                    new_particle = Particle(320, 180, (random.uniform(-2, 2) * speed_scale), (random.uniform(-2, 2) * speed_scale), 4, 100, (random.choice(color_palette))) #actually adds the values to the 7 parameters of the class
                    particles.append(new_particle) #appends
            em = energy_mapping(nsv) #Maps out the energy and raises it for clear visuals
            energy_transfer(grid, em) #transfers the updated energy to the grid
        grid = diffuse(grid) #diffuses the energy and creates a brand new grid that loops
        grid = fade(grid, fade_factor) #adds a fade value that fades the visual image away slowly 
        maximum = np.max(grid)
        total = np.sum(grid)
        conversion = energy_to_rgb(grid) #calls energy to rgb conversion
        surface = pygame.surfarray.make_surface(conversion) #creates a surface representing the conversion
        screen.blit(surface, (0, 0)) #copies the background image onto main display
        trail_surface.fill((247, 247, 247, 250), special_flags=pygame.BLEND_RGBA_MULT) #multiplies existing particles color and filling them w the values
        for particle in particles:
            if particle.lifetime > 0:
                particle.update() #updates the particles
                particle.draw(trail_surface) #adds the glow 
        particles = [particle for particle in particles if particle.lifetime > 0] #list comprehension removing expired particles

        screen.blit(trail_surface, (0,0)) #overall last blit
        pygame.display.flip()
        clock.tick(60)
        
    
    audio_thread.join() #tells the loop to wait untill recording finishes then stop it
    pygame.quit()
    stop_event


def normalize(rms):#Normalizes the rms into controlled values
    top = 0.09
    bottom = 0.001

    if rms >= top:
        return 1.0
    elif rms <= bottom:
        return 0.0
    else:
        return (rms - bottom) / (top - bottom)


def smoothing(nv, psv, alpha): #New normalized value(nv) previous smoothed value(psv) alpha(responsiveness)
    nsv = psv + (nv - psv) * alpha #nsv means new smoothed value
    return nsv


def energy_mapping(nsv): #New energy that is mapped to make actual relevant values
    result = nsv * 10
    return result

def energy_transfer(grid, energy): #transfers energy throughout the grid
    row, column = grid.shape
    centre_row = row // 2
    centre_column = column // 2
    center_energy = energy + grid[centre_row, centre_column]
    grid[centre_row, centre_column] = center_energy
    return grid

def diffuse(grid): #diffusion of grid
    rows, columns = grid.shape
    new_grid = np.zeros((rows, columns))
    current = grid[1:-1, 1:-1]
    above = grid[:-2, 1:-1]
    below = grid[2:, 1:-1]
    left = grid[1:-1, :-2]
    right = grid[1:-1, 2:]
    avg = (above + below + right + left) / 4
    new_value = current + 0.7 * (avg - current)
    new_grid[1:-1, 1:-1] = new_value
    return new_grid

def fade(grid, fade_factor): #fading throughout grid
     fade_energy = grid * fade_factor
     return fade_energy


def energy_to_rgb(grid): #existing energy into grid
    brightness = grid * 25.5
    brightness = np.clip(brightness, 0, 255)
    new_array = np.zeros((640, 360, 3), dtype=np.uint8)
    result = np.transpose(brightness)
    new_array[:, :, 0] = result
    new_array[:, :, 1] = result
    new_array[:, :, 2] = result
    return new_array





if __name__ == "__main__":
    main()