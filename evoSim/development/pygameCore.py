import pygame
import random
import math
from pygame.locals import *
import tkinter as tk
from tkinter import  *
worldsize=400
def fritters():
  pass

def start():
  create.destroy()
  if b.get() == 6:
    biomes = True
  class plant():
    def __init__(self,x,y,size,maturity):
      self.x = x
      self.y = y
      self.size = size
      self.maturity = maturity
    def updateP(self):
      self.maturity += 1
      if self.maturity == 300 and self.size <= 10:
        self.size += 1
        self.maturity = 0

    def newplant(self):
      mutationRate = mr.get()
      newX = self.x + random.randint(-70,70)
      newY = self.y + random.randint(-70,70)
      if self.maturity ==200 or self.maturity == 250 and self.size >=5:
         l = plant(newX,newY,1,0)
         plants.append(l)
      if len(plants) <=2:
         l = plant(newX,newY,1,0)
         plants.append(l)
  class cell():

    def __init__(self,speed,size,x,y,sight,energy,angle,diet,metabolism,fertility):
      self.speed = speed
      self.size = size
      self.x = x
      self.y = y
      self.sight = sight
      self.energy = energy
      self.angle = angle
      self.diet = diet
      self.metabolism = metabolism
      self.fertility = fertility

    def move(self,worldsize):
        closest = (2000,2000)
        holder = 1001
        for p in plants : # Determine closest plant to cell
            dist = math.sqrt(((o.x-p.x)**2)+(o.y-p.y)**2) # pythagorean
            if dist<=o.sight:
              if dist<holder:
                holder = dist
                closest = (p.x,p.y)

        for m in meatL : # Determine closest meat to cell
          dist = math.sqrt(((o.x-m.x)**2)+(o.y-m.y)**2) # pythagorean
          if dist<=o.sight:
            if dist<holder:
              holder = dist
              closest = (m.x,m.y)

        #Heading direction
        if closest[0] == 2000 and closest[1] == 2000:
          ang = o.angle
        else:
          ang = math.atan2((closest[1] - o.y),(closest[0] - o.x))
        #move
        o.x += math.cos(ang)* o.speed[0]
        o.y += math.sin(ang)* o.speed[1]



        #turn around if at border
        if (o.x-o.size-1) <= 0 or (o.x + o.size+1) >= worldsize:
          o.speed[0] = -o.speed[0]
        if (o.y+o.size+1) >= worldsize or (o.y - o.size-1) <= 0:
          o.speed[1] = -o.speed[1]
        


    def eat(self):
      #eat plants
      for p in plants:
        c2 = ((o.x-p.x)**2)+((o.y-p.y)**2)
        distance = math.sqrt(c2)
        if distance < o.size and len(plants) !=0:
          plants.remove(p)
          o.energy += (p.size * o.diet *15)
      # eat meat
      for m in meatL:
        c2 = ((o.x-m.x)**2)+((o.y-m.y)**2)
        distance = math.sqrt(c2)
        if distance < o.size and len(meatL) !=0:
          meatL.remove(m)
          o.energy += (m.size * (1-o.diet) *15)

    def update(self):
      o.energy -= o.metabolism
      if o.energy <=0:
        objects.remove(o)
        if o.size == 1:
          size = 1
        else:
          size = o.size
        m = meat(o.x,o.y,size)
        meatL.append(m)
    def baby(self):
      ranchance = random.randint(1,1000)
      if ranchance> 1:
        pass
      elif o.energy >= 30:
        mutationRate = 0.01
        chance = [1-mutationRate,1+mutationRate]
        prob = random.choice(chance)
        n = random.uniform(0,2)
        newspeed = [n,n]
        newsize = o.size * prob
        newX = o.x + 5
        newY = o.y
        newsight = o.sight * prob
        newenergy = o.energy
        newangle = o.angle*2
        newdiet = o.diet *prob
        newMetabolism = (newspeed[0])/(newsize)
        newfertility = o.fertility * prob
        d = cell(newspeed,newsize,newX,newY,newsight,newenergy,newangle,newdiet,newMetabolism,newfertility)
        objects.append(d)  
  class meat():
    def __init__(self,x,y,size):
      self.x = x
      self.y = y
      self.size = size

  if s.get() == 1: 
    worldsize = 400
  elif s.get() == 2: 
    worldsize = 600
  else: 
    worldsize = 800

  cellnumber = cn.get()
  mutationRate = mr.get()/100
  screen = pygame.display.set_mode((worldsize,worldsize))
  clock = pygame.time.Clock()
  global objects
  global plants
  global meatL
  objects = []
  plants = []
  meatL = []
  #To inherit the attribute from world creation scales
  global speed 
  global size
  global fertility
  global sight
  global diet
  #
  if i.get() == 5:
    for x in range (cellnumber):
      ranx = random.randint(0,worldsize)
      rany = random.randint(0,worldsize)
      ransize = random.randint(5,10)
      n = random.uniform(0,0.5)
      ranspeed = [n,n]
      ransight = random.randint(0,200)
      metabolism = (ranspeed[0]/ransize)*0.1
      ranfertility = random.randint(1,100)
      ranangle = random.randint(1,360)
      randiet = (random.randint(-50,50))/100
      energy = size.get()*15
      o = cell(ranspeed, ransize, ranx, rany, ransight, energy, ranangle, randiet, metabolism, ranfertility)
      objects.append(o)

  
  else:
    Cellsize = size.get()
    Cellspeed = speed.get()*0.1
    for x in range (cellnumber):
      ranx = random.randint(0,worldsize)
      rany = random.randint(0,worldsize)
      metabolism = Cellspeed/Cellsize
      ranangle = random.randint(1,360)
      energy = size.get()*15
      speed = [Cellspeed,Cellspeed]
      o = cell(speed,size.get(),ranx,rany,sight.get(),energy ,ranangle,diet.get(),metabolism,fertility.get())
      objects.append(o)
      



  
  for p in range(cellnumber*3):
    ranx = random.randint(10,worldsize - 10)
    rany = random.randint(10,worldsize - 10)
    ransize = random.randint(0,5)
    ranmaturity = random.randint(100,500)
    p = plant(ranx,rany,ransize,ranmaturity)
    plants.append(p)

  paused = False
  pygame.init()

  def menu():
    running = False
    while not running:
      menu = pygame_menu.Menu('Welcome', 400, 300,
      theme=pygame_menu.themes.THEME_BLUE)
      menu.add.button('Resume', running = True)
      menu.add.button('Quit', pygame_menu.events.EXIT)

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        exit()
      if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()

        if pos[0] >10 and pos[0]<40 and pos[1] >10 and pos[1]<40:
          paused = True
        if pos[0] >140 and pos[0]<217 and pos[1] >200 and pos[1]<217:
          paused = False

    screen.fill('black')
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(0, 0, worldsize, worldsize),1)



    if paused == False:
      #Draw dead cells
      for m in meatL:
        pygame.draw.circle(screen,'dark red',(m.x,m.y),m.size)
      #Cell functions
      for o in objects:
        o.move(worldsize)
        o.eat()
        o.update()
        o.baby()
        pygame.draw.circle(screen,'red',(o.x,o.y),o.size)
      #Plant functions
      for p in plants:
        p.updateP()
        p.newplant()
        pygame.draw.circle(screen,'green',(p.x,p.y),p.size)
      #Pause Button
      pygame.draw.rect(screen, (255,255,255), pygame.Rect(10, 10, 40, 40))
      pygame.draw.line(screen, (0, 0, 0), [20, 20], [20, 30], 5)
      pygame.draw.line(screen, (0, 0, 0), [30, 20], [30, 30], 5)
    else:
      #Keep cells and plants in the background
      for o in objects:
        pygame.draw.circle(screen,'red',(o.x,o.y),o.size)
      for p in plants:
        pygame.draw.circle(screen,'green',(p.x,p.y),p.size)

      menu()
      #draw pause screen
      '''
      pygame.draw.rect(screen,'white',pygame.Rect(80, 80, 220, 220))
      font = pygame.font.SysFont(None, 24)
      img = font.render('PAUSED', False, (0,0,0))
      screen.blit(img, (150, 150))
      #resume
      pygame.draw.rect(screen,'black',pygame.Rect(140, 200, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('RESUME', False, (0,0,0))
      screen.blit(img, (144, 203))
      '''
    pygame.display.flip()
    clock.tick(60)

def info():
  la1 = Label(create, text = 'Uniform: All cells are created with the same stats\nRandom: Each cell is created with random attributes upon creation')
  la1.place(x=105,y=330)
  la2 = Label(create, text = 'Speed: How fast they move \nSize: How big they are \nSight: how far each cell can detect objects like food or cells \nFertility: how frequent a cell will reproduce')
  la2.place(x=105,y=370)

def disable_scales():
  if i.get() == 5:
    speedScale.config(state='disabled',bg = 'grey')
    sizeScale.config(state='disabled',bg = 'grey')
    fertilityScale.config(state='disabled',bg = 'grey')
    sightScale.config(state='disabled',bg = 'grey')
    dietScale.config(state='disabled',bg = 'grey')
  else:
    speedScale.config(state='normal',bg = 'light grey')
    sizeScale.config(state='normal',bg = 'light grey')
    fertilityScale.config(state='normal',bg = 'light grey')
    sightScale.config(state='normal',bg = 'light grey')
    dietScale.config(state='normal',bg = 'light grey')
global create
create = tk.Tk()
create.title("Create New World")
create.geometry("600x500")      
leftFrame = tk.Frame(create,width = 100, height = 400, highlightthickness = 2, highlightbackground = 'black')
leftFrame.place(x=0,y=0)
newworldlabel = tk.Label(leftFrame, text = "Create New \nWorld")
newworldlabel.place(x=10,y=50)
simNameLabel = tk.Label(leftFrame, text = "World Name:")
simNameLabel.place(x=10,y=70)
simNameEntry = tk.Entry(leftFrame, width = 10)
simNameEntry.place(x=10,y=100)

backToHomeScreen = tk.Button(leftFrame, text = 'Back', command = fritters)
backToHomeScreen.place(x=0,y=10)
info = tk.Button(leftFrame, text = 'Info', command = info)
info.place(x=10, y = 150)
start = tk.Button(leftFrame, text = 'Start', command = start)
start.place(x=10, y = 200)

cn = IntVar()
cellnumberLabel = tk.Label(create,text = 'Starting number of Cells:')
cellnumberLabel.place(x=105,y=20)
cellnumberScale = tk.Scale(create,from_=1,to=20,length = 120, orient = HORIZONTAL, variable = cn)
cellnumberScale.place(x=260,y=0)

mr = IntVar()
mutationrateLabel = tk.Label(create,text = 'Mutation percentage:')
mutationrateLabel.place(x=105,y=60)
mutationrateScale = tk.Scale(create,from_=0,to=100,length = 120,orient = HORIZONTAL, variable = mr)
mutationrateScale.place(x=260,y=40)

i = IntVar()
uniformCheckbox = tk.Checkbutton(create, text = 'Uniform Genes', variable = i,onvalue = 2,command = disable_scales)
uniformCheckbox.place(x = 105,y=100)
randomCheckbox = tk.Checkbutton(create, text = 'Random Genes', variable = i,onvalue = 5, command = disable_scales)
randomCheckbox.place(x = 380,y=100)

speed = IntVar()
speedLabel = tk.Label(create,text = 'Speed :')
speedLabel.place(x=105,y=140)
speedScale = tk.Scale(create,from_=0,to=10,length = 100,orient = HORIZONTAL,variable = speed)
speedScale.place(x=160,y=130)

size = IntVar()
sizeLabel = tk.Label(create,text = 'Size :')
sizeLabel.place(x=105,y=180)
sizeScale = tk.Scale(create,from_=1,to=10,length = 100,orient = HORIZONTAL,variable = size)
sizeScale.place(x=160,y=170)

fertility = IntVar()
fertilityLabel = tk.Label(create,text = 'Fertility :')
fertilityLabel.place(x=105,y=220)
fertilityScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL,variable = fertility)
fertilityScale.place(x=160,y=210)

sight = IntVar()
sightLabel = tk.Label(create,text = 'Sight depth :')
sightLabel.place(x=280,y=140)
sightScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL,variable = sight)
sightScale.place(x=380,y=130)

diet = IntVar()
dietLabel = tk.Label(create,text = 'Diet scale:')
dietLabel.place(x=280,y=180)
dietScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL,variable = diet)
dietScale.place(x=380,y=170)

b = IntVar()
biomes = tk.Checkbutton(create, text = 'Biomes', variable = b,onvalue = 6)
biomes.place(x = 105,y=260)

p = IntVar()
populationControl = tk.Checkbutton(create, text = 'Population Control', variable = p,onvalue = 7)
populationControl.place(x = 280,y=260)

simulationSize = tk.Label(create, text = 'Simulation Size: ').place(x=105,y=280)
s = IntVar()
small = tk.Checkbutton(create, text = 'Small', variable = s,onvalue = 1)
small.place(x = 105,y=300)
medium = tk.Checkbutton(create, text = 'Medium', variable = s,onvalue = 2)
medium.place(x = 200,y=300)
large = tk.Checkbutton(create, text = 'Large', variable = s,onvalue = 3)
large.place(x = 280,y=300)

populationControl.invoke()
uniformCheckbox.invoke()
small.invoke()


leftFrame.mainloop()
create.mainloop()