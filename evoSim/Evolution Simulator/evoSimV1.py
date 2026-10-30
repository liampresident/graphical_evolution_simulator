#Computer Science NEA
#Define all imports and global variables in one organised spot
import random
import tkinter as tk
import tkinter.font as tkFont
import sqlite3
import pygame
import math
import time
import hashlib
import uuid
import matplotlib.pyplot as plt
from   tkinter import END, HORIZONTAL
from   tkinter import *
from   math import atan2, pi
global homeExists
global home
global AccountID
global LoggedIn
global root
global rootexists
global createExists
global MaxCells
global MaxPlants
global biomes_dict
createExists = False
rootexists   = False
LoggedIn     = False
homeExists   = False
MaxCells     = False
MaxPlants    = False
conn         = sqlite3.connect('Simulator.db')
cursor       = conn.cursor()
biomes_dict = {"block1":[], "block2":[], "block3":[], "block4":[], "block5":[],"block6":[],"block7":[], "block8":[],"block9":[], "block10":[], "block11":[], "block12":[], "block13":[], "block14":[],"block15":[],"block16":[]}
colours = [(144, 238, 144), (173, 216, 230), (0, 100, 0), (211, 169, 108)]


def drawGraph(type,Day,simID): # Draw graphs
  listx = []
  listy = []
  query = f'SELECT "{type}" FROM Simulations WHERE SimID = "{simID}";'
  cursor.execute(query) # Get old dataset
  string = str(cursor.fetchone()[0])
  splitstring = string.split('-')#Transform into new array
  for x in splitstring:
    listy.append(eval(x))#Make into integers (y axis)
  for x in range(len(splitstring)):
    listx.append(x)#X axis
  #Set names of axis
  if type == 'CellGraph':
    type = 'Cell Count'
  elif type == 'DietGraph':
    type = 'Diet Average'
  elif type == 'SizeGraph':
    type = 'Size Average'
  else:
    type = 'Speed Average'
  #Ploit graph
  plt.figure(figsize=(4, 4))
  plt.plot(listx, listy)
  plt.xlabel('Day')
  plt.ylabel(type)
  plt.show()


#Function using uuid module to get unique ID's
def FindUniqueID():
    return str(uuid.uuid4())
#This function only has to take the simId as a parameter in order to run a simulation
def runSimulation(simID):
  global AccountID
  global biomes_dict
  global objects
  global plants
  global meatL
  global MaxPlants,MaxCells
  global referencepoints


  #define all classes
  class plant():
    def __init__(self, FoodID, x, y, size, maturity):
      self.FoodID = FoodID
      self.x = x
      self.y = y
      self.size = size
      self.maturity = maturity
    def updateP(self):
      self.maturity += 1
      x = (500,1000)
      for b in x:
        if self.maturity == b and self.size <= 10:
          self.size += 1
      if self.maturity == 1000:
         self.maturity = 0

    def newplant(self,MaxPlants):
      if self.maturity == 400 and MaxPlants == False:
         global FoodId
         FoodID = FindUniqueID()
         newX = self.x + random.randint(-50,50)
         newY = self.y + random.randint(-50,50)
         l = plant(FoodID,newX,newY,1,0)
         plants.append(l)
         query = f'INSERT INTO Foods(FoodID, SimID, Position_x, Position_y, Size, MorP) VALUES("{FoodID}", "{simID}", {newX}, {newY}, 1, "Plant");'
         cursor.execute(query)
         conn.commit()
  class cell():
    def __init__(self, CellID, speed, size, x, y, sight, energy ,diet, metabolism, fertility, angle, lifespan, biome):
      self.CellID = CellID
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
      self.lifespan = lifespan
      self.biome = biome

    def move(self,worldsize):
      global referencepoints
      closestRP = (2000,2000)
      holderRP = 1000
      closestPoint = 'block1'
      for key in referencepoints:# Find closest refernece point
        x = referencepoints[key][0]
        y = referencepoints[key][1]
        dist = math.sqrt(((o.x-x)**2)+(o.y-y)**2) # pythagorean
        if dist<holderRP:
          holderRP = dist
          closestRP = (x,y)
          closestPoint = key
      for key in biomes_dict:
        if closestPoint == key:
          colour = biomes_dict[key]
          if colour == (144, 238, 144):
            o.biome = 'Normal'
          elif colour == (173, 216, 230):
            o.biome = 'Water'
          elif colour == (0, 100, 0):
            o.biome = 'Forest'
          else:
            o.biome = 'Desert'


      closest = (2000,2000)
      shortest = 1001
      #Search every node 
      #Determine closest and select that branch
      for p in plants : # Determine closest plant to cell
          hyp = (((o.x-p.x)**2) + ((o.y-p.y)**2))
          dist = math.sqrt(hyp) # pythagorean
          if dist<=o.sight:#Determine if in sight
            if dist<shortest: # mark as closest 
              shortest = dist
              closest = (p.x,p.y)#store

      for m in meatL : # Determine closest meat to cell
        dist = math.sqrt(((o.x-m.x)**2)+((o.y-m.y)**2))# pythagorean
        if dist<=o.sight:
          if dist<shortest:
            shortest = dist
            closest = (m.x,m.y)
            
      dx = closest[0] - o.x
      dy = o.y - closest[1]
      rads = math.atan2(-dy,dx)
      #Heading direction
      if closest[0] == 2000 and closest[1] == 2000:
        ang = o.angle
      else:
        changex = closest[0] - o.x
        changey = o.y - closest[1]
        ang = math.atan2(-changey,changex)
        

      #move
      if o.biome == 'Water': # Move slower if in water biome
        o.x += (math.cos(ang)* o.speed[0])/2
        o.y += (math.sin(ang)* o.speed[1])/2
      else:
        o.x += math.cos(ang)* o.speed[0]
        o.y += math.sin(ang)* o.speed[1]
      #turn around if at border
      if (o.x-o.size) <= 0 or (o.x + o.size) >= worldsize:
        o.speed[0] = -o.speed[0]
      if (o.y+o.size) >= worldsize or (o.y - o.size) <= 0:
        o.speed[1] = -o.speed[1]
      o.angle = ang

    def eat(self):
      #eat plants
      for p in plants:
        c2 = ((o.x-p.x)**2)+((o.y-p.y)**2)
        distance = math.sqrt(c2)
        if distance < o.size and len(plants) !=0:
          o.energy += p.size * o.diet
          query = f'DELETE FROM Foods WHERE FoodID = "{p.FoodID}";'
          cursor.execute(query)
          conn.commit()
          plants.remove(p)

      # eat meat
      for m in meatL:
        c2 = ((o.x-m.x)**2)+((o.y-m.y)**2)
        distance = math.sqrt(c2)
        if distance < o.size and len(meatL) !=0:
          query = f'DELETE FROM Foods WHERE FoodID = "{m.FoodID}";'
          cursor.execute(query)
          meatL.remove(m)
          conn.commit()
          o.energy += m.size * o.diet

    def update(self):
      if o.biome == 'Desert':#Faster metabolsim rate if in desert
        o.energy -= o.metabolism 
      else:
        o.energy -= o.metabolism * 0.5

      if o.energy <=0:
        global FoodID #make meat
        FoodID = FindUniqueID()
        if (o.size/2)< 1:
          o.size = 1
        m = meat(FoodID,o.x,o.y,o.size/2,0)
        meatL.append(m)
        query = f'INSERT INTO Foods(FoodID,SimID,Position_x,Position_y,Size,MorP) VALUES("{FoodID}","{simID}",{math.trunc(o.x)},{math.trunc(o.y)},{o.size/2},"Meat");'
        #delete cell
        query2 = f'DELETE FROM Cells WHERE CellID = "{o.CellID}";'
        cursor.execute(query)
        conn.commit()
        cursor.execute(query2)
        conn.commit()
        objects.remove(o)
      if SimTime == 1999:
        o.lifespan += 1

    def baby(self,MaxCells):
      ranchance = random.randint(0,4000)
      if o.energy >= 30 and MaxCells == False and ranchance <= o.fertility:
        chance = [1-(0.1*mutationRate),1+(0.1*mutationRate)]# Either mutates bigger or smaller
        o.energy -= 10

        prob = random.choice(chance)
        n = random.uniform(0,2)
        newspeed = [n,n]
        newsize = (o.size/2) + prob
        newX = o.x + 5
        newY = o.y
        newsight = (o.sight +1)* prob
        newenergy = newsize * 9
        newangle = o.angle+180
        newdiet = o.diet * prob
        newMetabolism = (newspeed[0])/(newsize)
        newfertility = (o.fertility+1) * prob
        lifespan = 0
        CellID = FindUniqueID()
        d = cell(CellID,newspeed, newsize, newX, newY, newsight, newenergy, newdiet, newMetabolism, newfertility, newangle, lifespan,'Normal')
        objects.append(d)

        query = f'INSERT INTO Cells(CellID, SimID, Speed, Size, Metabolism, Fertility, Diet,Sight, Energy, Position_x, Position_y, Lifespan, Angle) VALUES ("{CellID}", "{simID}", {n}, {newsize}, {newMetabolism}, {newfertility}, {newdiet}, {newsight}, {newenergy}, {math.trunc(newX)}, {math.trunc(newY)}, {lifespan}, {newangle})'
        cursor.execute(query)
        conn.commit()
  class meat():
    def __init__(self, FoodID, x, y, size, tick):
      self.FoodID = FoodID
      self.x = x
      self.y = y
      self.size = size
      self.tick = tick

    def rot(self):
      m.tick += 1
      if m.tick > 400:
        m.tick = 0
        m.size -= 1
      if m.size <=1:
        meatL.remove(m)
        query = f'DELETE FROM Foods WHERE FoodID = "{m.FoodID}";'
        cursor.execute(query)
        conn.commit()

  #Grab all information from the Simulation with simID and put into classes

  query00 = f'SELECT MutationRate, PopulationControl, WorldSize, Biomes,Day,Time FROM Simulations WHERE SimID = "{simID}";'
  celldetailsquery = f'SELECT * FROM Cells WHERE SimID = "{simID}";'
  cellcount = f'SELECT COUNT(*) FROM Cells WHERE SimID = "{simID}";'
  plantcount = f'SELECT COUNT(*) FROM Foods WHERE SimID = "{simID}" AND MorP = "Plant";'
  meatcount = f'SELECT COUNT(*) FROM Foods WHERE SimID = "{simID}" AND MorP = "Meat";'
  plantdetailsquery = f'SELECT * FROM Foods WHERE SimID = "{simID}" AND MorP = "Plant";'
  meatdetailsquery = f'SELECT * FROM Foods WHERE SimID = "{simID}" AND MorP = "Meat";'
  biomePattern = f'SELECT BiomesPattern FROM Simulations WHERE SimID = "{simID}";'
  cursor.execute(query00)
  execute = cursor.fetchall()
  mutationRate = int(execute[0][0])
  PopulationControl = str(execute[0][1])
  worldsize = int(execute[0][2])
  biomes = execute[0][3]
  Day = execute[0][4]
  hour = execute[0][5]
  cursor.execute(biomePattern)
  string = cursor.fetchone()
  newstring = string[0]
  list = []
  for i in range(len(newstring)):
    if newstring[i] == 'N':
      list.append((144, 238, 144))
    elif newstring[i] == 'W':
      list.append((173, 216, 230))
    elif newstring[i] == 'F':
      list.append((0, 100, 0))
    else:
      list.append((211, 169, 108))

  biomes_dict['block1']  = list[0]
  biomes_dict['block2']  = list[1]
  biomes_dict['block3']  = list[2]
  biomes_dict['block4']  = list[3]
  biomes_dict['block5']  = list[4]
  biomes_dict['block6']  = list[5]
  biomes_dict['block7']  = list[6]
  biomes_dict['block8']  = list[7]
  biomes_dict['block9']  = list[8]
  biomes_dict['block10'] = list[9]
  biomes_dict['block11'] = list[10]
  biomes_dict['block12'] = list[11]
  biomes_dict['block13'] = list[12]
  biomes_dict['block14'] = list[13]
  biomes_dict['block15'] = list[14]
  biomes_dict['block16'] = list[15]
  #Reference points
  global referencepoints
  wz = worldsize
  referencepoints = {"block1":(wz/8,wz/8), "block2":(3*(wz/8),wz/8), "block3":(5*(wz/8),wz/8), "block4":(7*(wz/8),wz/8), "block5":(wz/8,3*(wz/8)),"block6":(3*(wz/8),3*(wz/8)),"block7":(5*(wz/8),3*(wz/8)), "block8":(7*(wz/8),3*(wz/8)),"block9":(wz/8,5*(wz/8)), "block10":(3*(wz/8),5*(wz/8)), "block11":(5*(wz/8),5*(wz/8)), "block12":(7*(wz/8),5*(wz/8)), "block13":(wz/8,7*(wz/8)), "block14":(3*(wz/8),7*(wz/8)),"block15":(5*(wz/8),7*(wz/8)),"block16":(7*(wz/8),7*(wz/8))}
  if PopulationControl == 'Yes':
    PopulationControl = True
  else:
    PopulationControl = False
  if biomes == 'Yes':
    biomes = True
  else:
    biomes = False


  #arrays that will hold all information during running
  objects = []
  plants = []
  meatL = []

  #Cells
  cursor.execute(cellcount)
  count = cursor.fetchone()[0]
  cursor.execute(celldetailsquery)
  CellDetails = cursor.fetchall()
  for i in range(count):
    #pull all information from cell database
    CellID     = CellDetails[i][0]
    n          = CellDetails[i][2]
    speed      = [n,n]
    size       = CellDetails[i][3]
    metabolism = CellDetails[i][4]
    fertility  = CellDetails[i][5]
    diet       = CellDetails[i][6]
    sight      = CellDetails[i][7]
    energy     = CellDetails[i][8]
    posx       = CellDetails[i][9]
    posy       = CellDetails[i][10]
    lifespan   = CellDetails[i][11]
    angle      = CellDetails[i][12]

    #create cell
    o = cell(CellID,speed,size,posx,posy,sight,energy,diet,metabolism,fertility,angle,lifespan,'Normal')
    objects.append(o)

  #plants
  cursor.execute(plantcount)
  count2   = cursor.fetchone()[0]
  cursor.execute(plantdetailsquery)
  PlantDetails = cursor.fetchall()

  for i in range(int(count2)):
    FoodID = PlantDetails[i][0]
    posx   = PlantDetails[i][2]
    posy   = PlantDetails[i][3]
    size   = PlantDetails[i][4]
    #0 is maturity
    #recreate plants
    p = plant(FoodID,posx,posy,size,0)
    plants.append(p)

  #Meat
  cursor.execute(meatcount)
  count3 = cursor.fetchone()[0]
  cursor.execute(meatdetailsquery)
  MeatDetails = cursor.fetchall()
  for i in range(int(count3)):
    FoodID = MeatDetails[i][0]
    posx   = MeatDetails[i][2]
    posy   = MeatDetails[i][3]
    size   = MeatDetails[i][4]
    tick = 0
    #recreate meat
    m = meat(FoodID, posx, posy, size,tick)
    meatL.append(m)


  paused = False
  pygame.init()
  screen = pygame.display.set_mode((worldsize,worldsize))
  clock = pygame.time.Clock()
  running = True
  SimTime = hour * 83
  while running == True:
    if SimTime >= 2000:
      Day +=1
      SimTime   = 0
      print(f'Day: {Day}')
      def makeStringLonger(string,appended):
        if appended == None:
          appeneded = ''
        if string == None:
          string = ''
        appended = str(appended)
        string += f'-{appended}'
        return(string)
      #Get current Sim values
      CellCount = len(objects)
      
      dietTotal = 0
      for d in objects:
        dietTotal += d.diet
      if CellCount != 0:
        DietAvg   = dietTotal/CellCount
      else:
         DietAvg = 0
      
      speedTotal = 0
      for s in objects:
        speed = s.speed[0]
        if speed < 0:
          speed = -1*s.speed[0]
        speedTotal += speed
      if CellCount != 0:
        SpeedAvg   = speedTotal/CellCount
      else:
         SpeedAvg = 0
      
      sizeTotal = 0
      for si in objects:
        sizeTotal += si.size
      if CellCount!= 0:
        SizeAvg  = sizeTotal/CellCount
      else:
         SizeAvg= 0

      
      #get saved graph values
      fetchValues = f'SELECT CellGraph,DietGraph,SizeGraph,SpeedGraph FROM Simulations WHERE SimID = "{simID}";'
     
      #Get all these values
      cursor.execute(fetchValues)
      fetch = cursor.fetchall()
      currentCount = str(fetch[0][0])
      currentDiet  = str(fetch[0][1])
      currentSize  = str(fetch[0][2])
      currentSpeed = str(fetch[0][3])

      #Update history
      counta = makeStringLonger(currentCount,CellCount)
      dieta = makeStringLonger(currentDiet,DietAvg)
      sizea = makeStringLonger(currentSize,SizeAvg)
      speeda = makeStringLonger(currentSpeed,SpeedAvg)
      #Save back to database
      query1 = f'UPDATE Simulations SET CellGraph = "{counta}",DietGraph = "{dieta}",SizeGraph = "{sizea}",SpeedGraph = "{speeda}" WHERE SimID = "{simID}";'

      cursor.execute(query1)
      conn.commit()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        runnning = False
      if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        if pos[0] >10 and pos[0]<40 and pos[1] >10 and pos[1]<40:
          paused = True # pause
        if pos[0] >140 and pos[0]<217 and pos[1] >200 and pos[1]<217 and paused == True:
          paused = False # resume
        if pos[0] > 140 and pos[0] < 217 and pos[1] >220 and pos[1] <240 and paused == True:
          
          running = False
        for o in objects:
          dist = math.sqrt((pos[0]-o.x)**2 + (pos[1] - o.y)**2)
          if dist < 1.5*o.size:
            print(f"Cell Speed: {o.speed[0]}")
            print(f"Cell Size: {o.size}")
            print(f"Cell Energy: {o.energy}")
            print(f"Cell Sight: {o.sight}")
            print(f"Cell Diet: {o.diet}")
            print(f"Cell Lifespan: {o.lifespan}")
            print(f"Cell Biome: {o.biome}")
            print(f"Cell Angle: {o.angle}")
        if paused == True:
          x = pos[0]
          y = pos[1]
          if x > 100 and x < 180 and y > 250 and y < 270:
            drawGraph('CellGraph',Day,simID)
          elif x>190 and x < 270 and y>250 and y<270:
            drawGraph('DietGraph',Day,simID)
          elif x>100 and x < 180 and y>300 and y<320:
            drawGraph('SizeGraph',Day,simID)
          elif x>190 and x < 270 and y>300 and y<320:
            drawGraph('SpeedGraph',Day,simID)
          else:
            pass

    bsize = worldsize / 4 # size of the block
    wz = worldsize

    # Visual aspects of biomes
    pygame.draw.rect(screen,biomes_dict['block1'], pygame.Rect(0, 0, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block2'], pygame.Rect(wz/4, 0, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block3'], pygame.Rect(wz/2, 0, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block4'], pygame.Rect(3*(wz/4), 0, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block5'], pygame.Rect(0, wz/4, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block6'], pygame.Rect(wz/4, wz/4, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block7'], pygame.Rect(wz/2, wz/4, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block8'], pygame.Rect(3*(wz/4), wz/4, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block9'], pygame.Rect(0, wz/2, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block10'], pygame.Rect(wz/4, wz/2, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block11'], pygame.Rect(wz/2, wz/2, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block12'], pygame.Rect(3*(wz/4), wz/2, bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block13'], pygame.Rect(0, 3*(wz/4), bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block14'], pygame.Rect(wz/4, 3*(wz/4), bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block15'], pygame.Rect(wz/2, 3*(wz/4), bsize, bsize))
    pygame.draw.rect(screen,biomes_dict['block16'], pygame.Rect(3*(wz/4), 3*(wz/4), bsize, bsize))

    #Population Control
    if PopulationControl == True:
      if len(objects) <2:
        CellID = FindUniqueID()
        ranx = random.randint(0,worldsize)
        rany = random.randint(0,worldsize)
        angle = random.randint(0,360)
        ransize = random.randint(1,10)
        n = (random.randint(0,100)/50)
        ranspeed = [n,n]
        ransight = random.randint(0,200)
        metabolism = ((ranspeed[0])**2)/(ransize)
        multiplier = 10 ** 2 # truncate at 2 dp
        metabolism = (int(metabolism * multiplier) / multiplier)
        fertility = random.randint(1,100)
        randiet = (random.randint(0,100)/100)
        energy = 5*ransize
        o = cell(CellID, ranspeed, ransize, ranx, rany, ransight, energy, randiet, metabolism, fertility, angle, 0,'Normal')
        objects.append(o)
        query =f'INSERT INTO Cells (CellID,SimID,Speed,Size,Metabolism,Fertility,Diet,Sight,Energy,Position_x,Position_y,Lifespan,Angle) VALUES("{CellID}","{simID}",{n},{ransize},{metabolism},0,{randiet},{ransight},{energy},{ranx},{rany},0,{angle});'
        cursor.execute(query)
        conn.commit() # Spawn new cell if no cells left
      if len(plants) <4:
        FoodID = FindUniqueID()
        ranx = random.randint(0,worldsize)
        rany = random.randint(0,worldsize)
        size = random.randint(1,5)
        p = plant(FoodID, ranx, rany, size,0)
        plants.append(p)
        query = f'INSERT INTO Foods(FoodID, SimID, Position_x, Position_y, Size, MorP) VALUES("{FoodID}", "{simID}", {ranx}, {rany}, {size}, "Plant");'
        cursor.execute(query) # Spawn new plant if no plants left
        conn.commit()
      MaxCells = False
      if len(objects) > 30:#Stop too many cells spawning
        MaxCells = True#Mark variable MaxCells as true
      MaxPlants = False
      if len(plants) > 45:
        MaxPlants = True #Mark variable MaxPlants as true

    #Main code
    if paused != True:
      SimTime += 1
      #Cell functions
      for o in objects:
        if o.size > 14:# control sizes of cells
          o.size = 14
        o.move(worldsize)
        o.eat()
        o.update()
        o.baby(MaxCells)
        #         r    g   b
        colourb = [255,255,255]
        speed = o.speed[0]
        if speed <0:
          speed = -1*speed
        for x in range(o.lifespan):
          new = colourb[0] - 10
          colourb[0] = new
        for x in range(math.trunc(o.diet*100)):
          new2 = colourb[1] - 10
          colourb[1] = new2
        for x in range(math.trunc(speed*100)):
          new3 = colourb[2] - 10
          colourb[2] = new3
        if colourb[0] < 0:
          colourb[0] = 0
        if colourb[1] < 0:
          colourb[1] = 0
        if colourb[2] < 0:
          colourb[2] = 0
        pygame.draw.circle(screen,colourb,(o.x,o.y),o.size)
      #Draw dead cells
      for m in meatL:
        m.rot()
        pygame.draw.circle(screen,'dark red',(m.x,m.y),m.size)
      #Plant functions
      for p in plants:
        p.updateP()
        p.newplant(MaxPlants)
        pygame.draw.circle(screen,'green',(p.x,p.y),p.size)
      #Pause Button
      pygame.draw.rect(screen, (255,255,255), pygame.Rect(10, 10, 40, 40))
      pygame.draw.line(screen, (0, 0, 0), [20, 20], [20, 30], 5)
      pygame.draw.line(screen, (0, 0, 0), [30, 20], [30, 30], 5)
      #Day counter
      pygame.draw.rect(screen,'white',pygame.Rect(60, 10, 60, 20))
      font = pygame.font.SysFont(None, 24)
      img = font.render(f'Day: {Day}', False, (0,0,0))
      screen.blit(img, (61, 11))

      #In game clock
      hour = int(SimTime // 83)
      pygame.draw.rect(screen,'white',pygame.Rect(150, 10, 60, 20))
      font = pygame.font.SysFont(None, 24)
      ampm = 'am'
      if hour >= 12:
        ampm = 'pm'
      img = font.render(f'{hour} : {ampm}', False, (0,0,0))
      screen.blit(img, (151, 11))

    elif paused == True:
      #Keep cells and plants in the background
      for o in objects:
        #         r    g   b
        colourb = [255,255,255]
        speed = o.speed[0]
        if speed <0:
          speed = -1*speed
        for x in range(o.lifespan):
          new = colourb[0] - 10
          colourb[0] = new
        for x in range(math.trunc(o.diet*100)):
          new2 = colourb[1] - 10
          colourb[1] = new2
        for x in range(math.trunc(speed*100)):
          new3 = colourb[2] - 10
          colourb[2] = new3
        if colourb[0] < 0:
          colourb[0] = 0
        if colourb[1] < 0:
          colourb[1] = 0
        if colourb[2] < 0:
          colourb[2] = 0
        pygame.draw.circle(screen,colourb,(o.x,o.y),o.size)
      for p in plants:
        pygame.draw.circle(screen,'green',(p.x,p.y),p.size)
      for m in meatL:
        pygame.draw.circle(screen,'dark red',(m.x,m.y),m.size)
      #Keep day and time in background
      #Day counter
      pygame.draw.rect(screen,'white',pygame.Rect(60, 10, 60, 20))
      font = pygame.font.SysFont(None, 24)
      img = font.render(f'Day: {Day}', False, (0,0,0))
      screen.blit(img, (61, 11))

      #In game clock
      hour = int(SimTime // 83)
      pygame.draw.rect(screen,'white',pygame.Rect(150, 10, 60, 20))
      font = pygame.font.SysFont(None, 24)
      ampm = 'am'
      if hour >= 12:
        ampm = 'pm'
      img = font.render(f'{hour} : {ampm}', False, (0,0,0))
      screen.blit(img, (151, 11))

      #draw pause screen
      pygame.draw.rect(screen,'white',pygame.Rect(80, 80, 220, 280))
      font = pygame.font.SysFont(None, 24)
      img = font.render('PAUSED', False, (0,0,0))
      screen.blit(img, (150, 150))

      #resume
      pygame.draw.rect(screen,'black',pygame.Rect(140, 200, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('RESUME', False, (0,0,0))
      screen.blit(img, (144, 203))
      #Quit
      pygame.draw.rect(screen,'black',pygame.Rect(140, 220, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('Quit', False, (0,0,0))
      screen.blit(img, (144, 223))
      
      #Cell count button
      pygame.draw.rect(screen,'black',pygame.Rect(100, 250, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('Count', False, (0,0,0))
      screen.blit(img, (101, 251))
      #DietAvg button
      pygame.draw.rect(screen,'black',pygame.Rect(190, 250, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('Diet', False, (0,0,0))
      screen.blit(img, (191, 251))
     #SizeAvg button
      pygame.draw.rect(screen,'black',pygame.Rect(100, 300, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('Size', False, (0,0,0))
      screen.blit(img, (101, 301))
     #SpeedAvg button
      pygame.draw.rect(screen,'black',pygame.Rect(190, 300, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('Speed', False, (0,0,0))
      screen.blit(img, (191, 301))
    else:
      paused = False
    pygame.display.flip()
    clock.tick(60)


  #Game loop stopped
  query = f'UPDATE Simulations SET Day = {Day},Time = {hour} WHERE SimID = "{simID}";'
  cursor.execute(query)
  conn.commit()
  if len(objects) >0:
    for o in objects:
      speed1      = o.speed[0]
      size1       = o.size
      x1          = o.x
      y1          = o.y
      sight1      = o.sight
      energy1     = o.energy
      angle1      = o.angle
      metabolism1 = o.metabolism
      fertility1  = o.fertility
      lifespan1   = o.lifespan
      #Repopulate the database
      query1 = f'UPDATE Cells SET Speed = {speed1}, Size = {size1}, Position_x = {x1}, Position_y = {y1}, Energy = {energy1}, Angle = {angle1}, Metabolism = {metabolism1},Fertility = {fertility1}, Lifespan = {lifespan1} WHERE CellID = "{o.CellID}";'
      cursor.execute(query1)
      conn.commit() # Save to database (UPDATE)

  #Repopulate plants
  if len(plants) >0:
    for p in plants:
      FoodID   = p.FoodID
      x        = p.x
      y        = p.y
      size     = p.size
      query = f'UPDATE Foods SET Position_x = {x}, Position_y = {y}, Size = {size} WHERE FoodID = "{FoodID}";'
      cursor.execute(query)
      conn.commit()# Save to database (UPDATE)

  #Repopulate meat
  if len(meatL) >0:
    for m in meatL:
      FoodID   = m.FoodID
      x        = m.x
      y        = m.y
      size     = m.size
      query = f'UPDATE Foods SET Position_x = {x}, Position_y = {y}, Size = {size} WHERE FoodID = "{FoodID}";'
      cursor.execute(query)
      conn.commit()# Save to database (UPDATE)
  pygame.quit()

  query = f'SELECT AccountID FROM Simulations WHERE SimID = "{simID}";'
  cursor.execute(query)
  AccountID = cursor.fetchone()[0]
  homes(AccountID)

def HashPassword(password):
  #Hash method that encrypts the parameter
  password = password.encode('utf-8')  
  hash = hashlib.sha256(password)
  digest = hash.hexdigest()
  return(digest)

def homes(AccountID):#main interface
  global ID
  ID = AccountID
  global rootexists
  if rootexists == True:
    root.destroy()
    rootexists = False


  def NewButton():#new world
      home.destroy()

      def startNew():
        size = s.get()
        if len(simNameEntry.get()) < 1 or size == 0: # Check if sim name is empty and worldsize check
          label = tk.Label(create, text = 'Enter a Name for the World or \n Make Sure world size is selected')
          label.place(x=120,y=350)

        else:
          #Generate a simID for the new world and collect all options from user
          global simID
          simID = FindUniqueID()
          worldsize = 400
          worldsize = s.get()


          PopulationControl = 'No'
          if pop.get() == 1:
            PopulationControl = 'Yes'
          stringg = ''
          Biomes = 'No'
          if bio.get() == 1:
            Biomes = 'Yes'
            randomList = [] #Assign each block a random colour, Light Green - Light Blue - Dark Green - Sandy yellow
            colours = ['N', 'W', 'F', 'D']
            for i in range(16):
              colour = random.choice(colours)
              stringg += colour

          else:
            for d in range(16):
              stringg += 'N'

          name = str(simNameEntry.get())
          day = 0
          status = 'Alive'
          mr = mutationrateScale.get()
          if mr == None:
            mr = 0
          hour = 0
          
          cursor.execute(f'INSERT INTO Simulations(AccountID, SimID, SimName, Day, Status, WorldSize, Biomes, PopulationControl, MutationRate, BiomesPattern,Time,CellGraph,DietGraph,SpeedGraph,SizeGraph) VALUES({AccountID},"{simID}", "{name}" , {day}, "{status}", {worldsize}, "{Biomes}", "{PopulationControl}", {mr}, "{stringg}",{hour},"{cellnumberScale.get()}","0","0","0");')
          conn.commit()

          cellnumber = cellnumberScale.get()

          #Generate Cells and Add them to database Cells
          for x in range (cellnumber):
            global CellID
            CellID = FindUniqueID()
            ranx = random.randint(0,worldsize)
            rany = random.randint(0,worldsize)
            angle = random.randint(0,360)

            #Set everything Uniformly
            ransize = sizeScale.get()
            n = (speedScale.get()/10)
            ranspeed = [n,n]
            ransight = sightScale.get()
            metabolism = ((ranspeed[0])**2)/(ransize)
            multiplier = 10 ** 2
            metabolism = (int(metabolism * multiplier) / multiplier)
            fertility = fertilityScale.get()
            randiet = (dietScale.get())/100
            lifespan = 0
            #If requested to be random, then change everything to random

            if inter.get() == 1:
              ransize = random.randint(1,10)
              n = (random.randint(0,100)/100)
              ranspeed = [n,n]
              ransight = random.randint(0,100)
              metabolism = ((ranspeed[0])**2)/(ransize)
              multiplier = 10 ** 2
              metabolism = (int(metabolism * multiplier) / multiplier)
              fertility = random.randint(1,100)
              randiet = (random.randint(0,100)/100)

            energy = 5*ransize
            #Store to Database
            query =f'INSERT INTO Cells (CellID,SimID,Speed,Size,Metabolism,Fertility,Diet,Sight,Energy,Position_x,Position_y,Lifespan,Angle) VALUES("{CellID}","{simID}",{n},{ransize},{metabolism},0,{randiet},{ransight},{energy},{ranx},{rany},{lifespan},{angle});'
            cursor.execute(query)
            conn.commit()


          #Same for plants
          biomesList = ('N', 'N', 'N', 'N', 'N', 'W', 'W', 'W', 'W', 'W', 'W', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'D', 'D', 'D') # Distribution is repeated so that
          # Normal has 25% chance
          # Water has 25% chance
          #Forest has 35% chance
          #Desert has 15% chance
          wz = worldsize

          for p in range(cellnumber+10):  
            FoodID = FindUniqueID()
            if Biomes == 'No':
              edge = worldsize - 10
              ranx = random.randint(10,edge)
              rany = random.randint(10,edge)
              ransize = random.randint(0,5)
              ranmaturity = random.randint(1,300)
            else:
              biomeSpawn = random.choice(biomesList)# returns biome to spawn in
              ransize = random.randint(0,5)
              ranmaturity = random.randint(1,300)
              avaliableBiomes = []
              #example stringg value: DFFDNNFWFWDDNFFD
              markerList = []
              for f in range(len(stringg)):
                if stringg[f] == biomeSpawn: # Marks the index of the biome matching the randomiser
                  markerList.append(f) # eg 1,4,7,9 which means block1 etc
              randomItem = random.choice(markerList) # eg 1
              block = 'block'
              block += str(randomItem)
              #define variables for grid edge values
              fourth = wz/4
              half = wz/2
              threefourths = 3*(wz/4)
              #define the x and the y values for the plant to spawn in relating to the grid value it is closest to
              if block == 'block1':
                ranx = random.randint(0,fourth)
                rany = random.randint(0,fourth)
              elif block == 'block2':
                ranx = random.randint(fourth,half)
                rany = random.randint(0,fourth)
              elif block == 'block3':
                ranx = random.randint(half,threefourths)
                rany = random.randint(0,fourth)
              elif block == 'block4':
                ranx = random.randint(threefourths,wz)
                rany = random.randint(0,fourth)
              elif block == 'block5':
                ranx = random.randint(0,fourth)
                rany = random.randint(fourth,half)
              elif block == 'block6':
                ranx = random.randint(fourth,half)
                rany = random.randint(fourth,half)
              elif block == 'block7':
                ranx = random.randint(half,threefourths)
                rany = random.randint(fourth,half)
              elif block == 'block8':
                ranx = random.randint(threefourths,wz)
                rany = random.randint(fourth,half)
              elif block == 'block9':
                ranx = random.randint(0,fourth)
                rany = random.randint(half,threefourths)
              elif block == 'block10':
                ranx = random.randint(fourth,half)
                rany = random.randint(half,threefourths)
              elif block == 'block11':
                ranx = random.randint(half,threefourths)
                rany = random.randint(half,threefourths)
              elif block == 'block12':
                ranx = random.randint(threefourths,wz)
                rany = random.randint(half,threefourths)
              elif block == 'block13':
                ranx = random.randint(0,fourth)
                rany = random.randint(threefourths,wz)
              elif block == 'block14':
                ranx = random.randint(fourth,half)
                rany = random.randint(threefourths,wz)
              elif block == 'block15':
                ranx = random.randint(half,threefourths)
                rany = random.randint(threefourths,wz)
              else:
                ranx = random.randint(threefourths,wz)
                rany = random.randint(threefourths,wz)


            query = f'INSERT INTO Foods(FoodID,SimID,Position_x,Position_y,Size,MorP) VALUES("{FoodID}","{simID}",{ranx},{rany},{ransize},"Plant");'
            cursor.execute(query)
            conn.commit()

          create.destroy()
          runSimulation(simID)

      #display info to help clear up misunderstanding about the settings to the user
      def info():
          la1 = Label(create, text = 'Uniform: All cells are created with the same stats\nRandom: Each cell is created with random attributes upon creation')
          la1.place(x=105,y=330)
          la2 = Label(create, text = 'Speed: How fast they move \nSize: How big they are \nSight: how far each cell can detect objects like food or cells \nFertility: how frequent a cell will reproduce')
          la2.place(x=105,y=360)
      def reset():
            speedScale.set(0)
            sizeScale.set(0)
            fertilityScale.set(0)
            sightScale.set(0)
            dietScale.set(0)
      def Back():
        create.destroy()
        homes(ID)

      def disable_scales(): # Stop user using the scales when random genetics is selected
        speedScale.set(0)
        sizeScale.set(0)
        fertilityScale.set(0)
        sightScale.set(0)
        dietScale.set(0)
        if inter.get() == 1:
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


      #Create window for creating a new world
      #must be user friendly and easy to understand
      createExists = True
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

      backToHomeScreen = tk.Button(leftFrame, text = 'Back', command = Back)
      backToHomeScreen.place(x=0,y=10)
      info = tk.Button(leftFrame, text = 'Info', command = info)
      info.place(x=10, y = 150)
      start = tk.Button(leftFrame, text = 'Start', command = startNew)
      start.place(x=10, y = 200)


      cellnumberLabel = tk.Label(create,text = 'Starting number of Cells:')
      cellnumberLabel.place(x=105,y=20)
      cellnumberScale = tk.Scale(create,from_=1,to=20,length = 120, orient = HORIZONTAL)
      cellnumberScale.place(x=260,y=0)

      mutationrateLabel = tk.Label(create,text = 'Mutation percentage:')
      mutationrateLabel.place(x=105,y=60)
      mutationrateScale = tk.Scale(create,from_=0,to=100,length = 120,orient = HORIZONTAL)
      mutationrateScale.place(x=260,y=40)

      inter = tk.IntVar()
      uniformCheckbox = tk.Checkbutton(create, text = 'Uniform Genes', variable = inter,onvalue = 0,command = disable_scales)
      uniformCheckbox.place(x = 105,y=100)
      randomCheckbox = tk.Checkbutton(create, text = 'Random Genes', variable = inter,onvalue = 1, command = disable_scales)
      randomCheckbox.place(x = 380,y=100)

      speedLabel = tk.Label(create,text = 'Speed :')
      speedLabel.place(x=105,y=140)
      speedScale = tk.Scale(create,from_=0,to=10,length = 100,orient = HORIZONTAL)
      speedScale.place(x=160,y=130)

      sizeLabel = tk.Label(create,text = 'Size :')
      sizeLabel.place(x=105,y=180)
      sizeScale = tk.Scale(create,from_=1,to=10,length = 100,orient = HORIZONTAL)
      sizeScale.place(x=160,y=170)

      fertilityLabel = tk.Label(create,text = 'Fertility :')
      fertilityLabel.place(x=105,y=220)
      fertilityScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL)
      fertilityScale.place(x=160,y=210)

      sightLabel = tk.Label(create,text = 'Sight depth :')
      sightLabel.place(x=280,y=140)
      sightScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL)
      sightScale.place(x=380,y=130)

      dietLabel = tk.Label(create,text = 'Diet scale:')
      dietLabel.place(x=280,y=180)
      dietScale = tk.Scale(create,from_=0,to=100,length = 100,orient = HORIZONTAL)
      dietScale.place(x=380,y=170)

      bio = tk.IntVar()
      biomes = tk.Checkbutton(create, text = 'Biomes', variable = bio).place(x = 105,y=260)

      pop = tk.IntVar()
      populationControl = tk.Checkbutton(create, text = 'Population Control', variable = pop).place(x = 280,y=260)

      simulationSize = tk.Label(create, text = 'Simulation Size: ').place(x=105,y=280)
      s = tk.IntVar()
      small = tk.Checkbutton(create, text = 'Small', variable = s,onvalue = 400)
      small.place(x = 105,y=300)
      medium = tk.Checkbutton(create, text = 'Medium', variable = s,onvalue = 600)
      medium.place(x = 200,y=300)
      large = tk.Checkbutton(create, text = 'Large', variable = s,onvalue = 800)
      large.place(x = 280,y=300)


      leftFrame.mainloop()
      create.mainloop()

  def LoadButton():# ability to select and load old worlds
    home.destroy()
    def back():
      load.destroy()
      homes(AccountID)

    def start():#save settings into database then run simulation
      simID = 'null'
      for i in box.curselection():#get selected row
        simName = box.get(i)
      if simName == 'null':#check if row is selected or not
        label = tk.Label(load, text = 'Something went wrong\nPlease select a world and try again').place(x = 100,y = 350)
      else:
        query = f'Select SimID FROM Simulations WHERE SimName = "{simName}";'
        cursor.execute(query)
        simID = cursor.fetchone()[0]
        load.destroy()
        runSimulation(simID)

    def deleteWorld():
      simName = 'null'
      if len(box.curselection())== 0:
        label = tk.Label(load, text = 'Something went wrong\nPlease select a world and try again').place(x = 100,y = 350)
      else:
        for i in box.curselection():#get selected row
          simName = box.get(i)

        query = f'DELETE FROM Simulations WHERE SimName = "{simName}";'
        cursor.execute(query)
        conn.commit()

        selected_index = box.curselection()[0]
        box.delete(selected_index)#delete selected row




    load = tk.Tk()
    load.geometry("600x500")
    load.title('Load World')
    query = f'SELECT COUNT(*) FROM Simulations WHERE AccountID = "{AccountID}";'
    cursor.execute(query)
    count = cursor.fetchone()[0]
    query = f'SELECT SimName FROM Simulations WHERE AccountID = "{AccountID}";'
    cursor.execute(query)

    simname = tk.Label(load, text = 'Sim Name:').place(x = 110,y=80)
    back = tk.Button(load,text = 'Back',command = back).place(x=10,y=10)
    submit = tk.Button(load,text = 'Start',command = start).place(x = 140, y = 300)
    label = tk.Label(load, text = 'Select World:').place(x = 40,y = 50)
    delete = tk.Button(load,text = 'Delete',command = deleteWorld).place(x = 240, y = 300)

    scrollbar = tk.Scrollbar(load)
    scrollbar.place(x = 390, y = 110)
    fetch = cursor.fetchall()
    box = tk.Listbox(load, yscrollcommand = scrollbar.set, selectmode = SINGLE, width = 40)

    for i in range(count):#populate listbox with simulation names
      details = fetch[i]
      box.insert(END, str(details[0]))

    box.place(x = 60,y = 110)
    scrollbar.config(command = box.yview )
    load.mainloop()



  def AccountButton():
        global home
        home.destroy()
        accountwin = tk.Tk()
        accountwin.title("Account Settings")
        accountwin.geometry('600x500')
        accountwin.resizable(width=True, height=True)
        FONT10 = tkFont.Font(family='Times',size=10)
        FONT28 = tkFont.Font(family='Times',size=28)
        FONT7 = tkFont.Font(family='Times',size=7)
        def Update():
          NewUsername = UsernameEntry.get()
          NewPassword = HashPassword(PasswordEntry.get())
          NewRecovery = MemorableWordEntry.get()
          if len(NewUsername) < 1 or len(PasswordEntry.get()) <6 or len(NewRecovery) < 6:
            label = tk.Label(accountwin,text = "Not enough characters")
            label.place(x = 100,y = 230)
          else:
            query = f"UPDATE Users SET Username = '{NewUsername}',Password = '{NewPassword}', RecoveryWord = '{NewRecovery}' WHERE AccountID = '{AccountID}';"
            cursor.execute(query)
            conn.commit()
            la1 = tk.Label(accountwin, text = 'Account Successfully Updated')
            la1.place(x = 100,y = 350)

        def Delete():
          #Delete everything tied to specific ID
          query = f'SELECT SimID FROM Simulations WHERE AccountID = {ID};'
          cursor.execute(query)
          sims = cursor.fetchall()
          for i in sims:
            simss = f'DELETE FROM Simulations WHERE SimID = "{i[0]}";'
            cells = f'DELETE FROM Cells WHERE SimID = "{i[0]}";'
            foods = f'DELETE FROM Foods WHERE SimID = "{i[0]}";'
            cursor.execute(simss)
            conn.commit()
            cursor.execute(cells)
            conn.commit()
            cursor.execute(foods)
            conn.commit()
          

          query = f"DELETE FROM Users WHERE AccountID = {ID}"
          cursor.execute(query)
          conn.commit()
          accountwin.destroy()


          StartingMainMenu()
        def Back():
          accountwin.destroy()
          homes(AccountID)

        accountwinLabel =tk.Label(accountwin, font = FONT28, text ='Account Settings')
        accountwinLabel.place(x=50,y=10,width=494,height=100)

        statement = f"SELECT Username,RecoveryWord FROM Users WHERE AccountID = {AccountID};"
        cursor.execute(statement)
        details = cursor.fetchall()


        Username = Label(accountwin,text = 'Username:', font = FONT10)
        Username.place(x=100,y=150)
        UsernameEntry = Entry(accountwin)
        UsernameEntry.place(x=300,y=150)
        UsernameEntry.insert(0,details[0][0])

        Password = Label(accountwin,text = 'Password:', font = FONT10)
        Password.place(x=100,y=170)
        PasswordEntry = Entry(accountwin)
        PasswordEntry.place(x=300,y=170)

        MemorableWord = Label(accountwin,text = 'Memorable Word:', font = FONT10)
        MemorableWord.place(x=100, y = 190)
        MemorableWordEntry = Entry(accountwin)
        MemorableWordEntry.place(x=300, y = 190)
        MemorableWordEntry.insert(0,details[0][1])

        Update = Button(accountwin,text = 'Update',command = Update)
        Update.place(x=100,y=300)

        delete = Button(accountwin,text = 'Delete Account',command = Delete)
        delete.place(x = 200,y = 300)


        Back = Button(accountwin,text = 'Back', command = Back)
        Back.place(x=10,y=10)
        accountwin.mainloop()


  def LogOffButton():
    home.destroy()
    homeExists = False
    AccountID = ''
    StartingMainMenu()
  #GUI for main menu
  global home
  homeExists = True
  home = tk.Tk()
  home.title("Graphical Evolution Simulator")
  home.geometry('600x500')
  home.resizable(width=True, height=True)
  FONT10 = tkFont.Font(family='Times',size=10)
  FONT28 = tkFont.Font(family='Times',size=28)
  FONT7 = tkFont.Font(family='Times',size=7)

  homeScreenLabel =tk.Label(home, font = FONT28, text ='Graphical Evolution \n Simulator')
  homeScreenLabel.place(x=50,y=50,width=400,height=100)


  NewButton =tk.Button(home, font = FONT10, text ='New', command = NewButton)
  NewButton.place(x=50,y=240)

  if AccountID != 0:
    LoadButton =tk.Button(home, font = FONT10, text ='Load', command = LoadButton)
    LoadButton.place(x=50,y=280)
    AccountButton =tk.Button(home, font = FONT10, text ='Account', command = AccountButton)
    AccountButton.place(x=50,y=320)

  LogOffButton =tk.Button(home, font = FONT10, text ='Log Off', command = LogOffButton)
  LogOffButton.place(x=400,y=20)

  QuitButton =tk.Button(home, font = FONT10, text ='Quit', command = QuitButton_command)
  QuitButton.place(x=500,y=20)

  ID = AccountID
  accountnum = tk.Label(home,font = FONT10, text = 'Account ID : {}'.format(ID))
  accountnum.place(x=10,y=10)
  home.mainloop()

def LogInButton_command():# GUI for log in 
        global rootexists
        if rootexists == True:
                root.destroy()
                rootexists = False

        def BackToMainMenuLogin():
                loginWin.destroy()
                StartingMainMenu()

        def submitLogIn():
          global loginWin#check they match the string requierments
          if len(UsernameEntry.get()) < 2 or len(UserPasswordEntry.get()) < 6:
            Label = tk.Label(loginWin, text = 'Not enough characters')
            Label.place(x = 200,y=350)
          else:
            EnteredUsernameEntry = UsernameEntry.get()
            EnteredUserPasswordEntry = HashPassword(UserPasswordEntry.get())#hash password and see if its the same in the database

            statement = f"SELECT Username FROM Users WHERE Username = '{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
            cursor.execute(statement)
            if not cursor.fetchone():
                label1 = tk.Label(loginWin,text ='Login Failed').place(x=180,y=350)
            else:
                statement = f"SELECT AccountID FROM Users WHERE Username='{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
                cursor.execute(statement)
                AccountID = cursor.fetchone()[0]
                loginWin.destroy()
                homes(AccountID)#return accountID



        def clearLogin():
                UsernameEntry.delete(0, END)
                UserPasswordEntry.delete(0, END)
        def newpassword():
          def submitE():
            e1 = entry1.get()
            e2 = entry2.get()
            if e1 == e2:
              password = HashPassword(e1)
              query1 = f'SELECT AccountID FROM Users WHERE RecoveryWord = "{MemorableWord}";'
              cursor.execute(query1)
              AccountID = cursor.fetchone()[0]
              query2 = f"UPDATE Users SET Password = '{password}' WHERE AccountID = '{AccountID}';"
              cursor.execute(query2)
              conn.commit()
              newPassword.destroy()
              LogInButton_command()
            else:
              label = tk.Label(newPassword,text = 'Details do not match').place(x = 100,y = 350)

          newPassword = tk.Tk()
          newPassword.geometry("600x500")
          recoveryWin.destroy()
          label = tk.Label(newPassword,text = 'Set New Password:').place(x = 100,y=100)
          newPassword.title("Set New Password")
          password = tk.Label(newPassword, text = 'Password: ').place(x = 100,y=180)
          entry1 = tk.Entry(newPassword)
          entry1.place(x = 200,y=180)

          confirmPassword = tk.Label(newPassword, text = 'Re-enter: ').place(x=100,y=200)
          entry2 = tk.Entry(newPassword)
          entry2.place(x = 200, y = 200)

          submit = tk.Button(newPassword,text = 'Submit',command = submitE).place(x=190,y=300)
          newPassword.mainloop()

        def ForgottenPassword():
                loginWin.destroy()
                def submitRecovery():
                  global MemorableWord
                  Username = UsernameEntry.get()
                  MemorableWord = MemorableWordEntry.get()

                  query = f"SELECT AccountID FROM Users WHERE Username = '{Username}'AND RecoveryWord = '{MemorableWord}';"
                  cursor.execute(query)
                  if not cursor.fetchone():
                    label1 = Label(recoveryWin,text = 'No Account Found').place(x=100,y=350)
                  else:
                    #Set New Password
                    global AccountID
                    AccountID = cursor.fetchone()
                    newpassword()

                def clearRecovery():
                        UsernameEntry.delete(0,END)
                        MemorableWordEntry.delete(0,END)

                def BackToLogInRecovery():
                        recoveryWin.destroy()
                        LogInButton_command()

                global recoveryWin
                recoveryWin = tk.Tk()
                recoveryWin.title("Account Recovery")
                recoveryWin.geometry('600x500')
                recoveryWin.resizable(width=False, height=False)
                AccountRecoveryLabel =tk.Label(recoveryWin, font = FONT28, text ='Account Recovery')
                AccountRecoveryLabel.place(x=50,y=70)

                UsernameLabel = tk.Label(recoveryWin, font = FONT10, text ='Username: ')
                UsernameLabel.place(x=50,y=200)
                UsernameEntry = tk.Entry(recoveryWin)
                UsernameEntry.place(x = 200, y = 200)

                MemorableWordLabel =tk.Label(recoveryWin, font = FONT10, text ='Memorable Word:')
                MemorableWordLabel.place(x=50,y=300)
                MemorableWordEntry = tk.Entry(recoveryWin)
                MemorableWordEntry.place(x = 200, y = 300)

                submitRecovery = tk.Button(recoveryWin,text = "Submit", font = FONT10, command = submitRecovery)
                submitRecovery.place(x=150,y=350)

                clearRecovery = tk.Button(recoveryWin,text = "Clear", font = FONT10, command = clearRecovery)
                clearRecovery.place(x=300,y=350,width=100,height=30)

                BackToLogInRecovery = tk.Button(recoveryWin,text = "Back", font = FONT10, command = BackToLogInRecovery)
                BackToLogInRecovery.place(x=10,y=10,width=70,height=30)
                recoveryWin.mainloop()

        global loginWin
        loginWin = tk.Tk()
        loginWin.title("Graphical Evolution Simulator")
        loginWin.geometry('600x500')
        loginWin.resizable(width=True, height=True)
        FONT10 = tkFont.Font(family='Times',size=10)
        FONT28 = tkFont.Font(family='Times',size=28)
        FONT7 = tkFont.Font(family='Times',size=7)

        LoginScreenLabel =tk.Label(loginWin, font = FONT28, text ='Graphical Evolution Simulator\nLog In')
        LoginScreenLabel.place(x=50,y=70,width=494,height=100)

        UsernameLabel =tk.Label(loginWin, font = FONT10, text ='Username')
        UsernameLabel.place(x=50,y=200)
        UsernameEntry = tk.Entry(loginWin)
        UsernameEntry.place(x = 180, y = 200)

        UserPasswordLabel =tk.Label(loginWin, font = FONT10, text ='Password')
        UserPasswordLabel.place(x=50,y=250)
        UserPasswordEntry = tk.Entry(loginWin)
        UserPasswordEntry.place(x = 180, y = 250)

        submitLogIn = tk.Button(loginWin,text = "Log In", font = FONT10, command = submitLogIn)
        submitLogIn.place(x=100,y=300,width=100,height=30)

        clearLogin = tk.Button(loginWin,text = "Clear", font = FONT10, command = clearLogin)
        clearLogin.place(x=250,y=300,width=100,height=30)

        ForgottenPassword = tk.Button(loginWin,text = "Forgotten Password?", font = FONT10, command = ForgottenPassword)
        ForgottenPassword.place(x=400,y=300,width=110,height=30)

        BackToMainMenu = tk.Button(loginWin,text = "Back", font = FONT10, command = BackToMainMenuLogin)
        BackToMainMenu.place(x=10,y=10,width=70,height=30)
        loginWin.mainloop()

def SignUpButton_command():
        global rootexists
        if rootexists == True:
                root.destroy()
                rootexists = False

        def BackToMainMenuSignup():
                signupWin.destroy()
                StartingMainMenu()

        def submitSignup():
              if len(UsernameEntry.get()) < 2 or len(UserPasswordEntry.get()) < 6 or len(MemorableWordEntry.get()) < 6:
                label = tk.Label(signupWin, text = 'Not enough characters')
                label.place(x = 150,y = 380)
              else:
                EnteredUsernameEntry = str(UsernameEntry.get())
                EnteredUserPasswordEntry = HashPassword(str(UserPasswordEntry.get()))
                EnteredMemorableWordEntry = str(MemorableWordEntry.get())
                #Check if this user already exists
                query = f'SELECT AccountID FROM Users Where Username = "{UsernameEntry.get()}";'
                cursor.execute(query)
                if not cursor.fetchone():
  
                    #Recursive function to check if new AccountID is taken or nah
                      def FindAccountID(AccountID):
                        query = f'SELECT Username FROM Users WHERE AccountID = {AccountID}'
                        current = AccountID
                        cursor.execute(query)
                        if not cursor.fetchone():
                          return (current)
                        else:
                          current = AccountID
                          AccountID += 1 
                          FindAccountID(AccountID)
  
                      newID = FindAccountID(1)
  
                      cursor.execute("INSERT INTO Users(AccountID,Username,Password,RecoveryWord) VALUES(?,?,?,?)",(newID,EnteredUsernameEntry,EnteredUserPasswordEntry,EnteredMemorableWordEntry))
                      conn.commit()
                      signupWin.destroy()
                      statement = f"SELECT AccountID from Users WHERE Username='{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
                      cursor.execute(statement)
  
                      newID = cursor.fetchone()[0]
                      homes(newID)

                else:
                    label23 = tk.Label(signupWin, text = 'Account with this username already exists').place(x=100,y=380)


        def clearSignup():
                UsernameEntry.delete(0,END)
                UserPasswordEntry.delete(0,END)
                MemorableWordEntry.delete(0,END)
        global signupWin
        signupWin = tk.Tk()
        signupWin.title("Graphical Evolution Simulator")
        signupWin.geometry('600x500')
        signupWin.resizable(width=True, height=True)
        FONT10 = tkFont.Font(family='Times',size=10)
        FONT28 = tkFont.Font(family='Times',size=28)
        FONT7 = tkFont.Font(family='Times',size=7)

        SignupScreenLabel =tk.Label(signupWin, font = FONT28, text ='Graphical Evolution Simulator\nSign up')
        SignupScreenLabel.place(x=50,y=70,width=494,height=100)

        UsernameLabel =tk.Label(signupWin, font = FONT10, text ='Username')
        UsernameLabel.place(x=50,y=200)
        UsernameEntry = tk.Entry(signupWin)
        UsernameEntry.place(x = 180, y = 200)

        UserPasswordLabel =tk.Label(signupWin, font = FONT10, text ='Password')
        UserPasswordLabel.place(x=50,y=250)
        UserPasswordEntry = tk.Entry(signupWin)
        UserPasswordEntry.place(x = 180, y = 250)

        MemorableWordLabel =tk.Label(signupWin, font = FONT10, text ='Memorable Word')
        MemorableWordLabel.place(x=50,y=300)
        MemorableWordEntry = tk.Entry(signupWin)
        MemorableWordEntry.place(x = 180, y = 300)
        MemorableWordLabelinfo =tk.Label(signupWin, font = FONT10, text ='A word such as a pet name to \nrecover your account in the event you forget\n your password')
        MemorableWordLabelinfo.place(x=350,y=290)

        submitSignup = tk.Button(signupWin,text = "Sign up", font = FONT10, command = submitSignup)
        submitSignup.place(x=100,y=350,width=100,height=30)

        clearSignup = tk.Button(signupWin,text = "Clear", font = FONT10, command = clearSignup)
        clearSignup.place(x=250,y=350,width=100,height=30)

        BackToMainMenu = tk.Button(signupWin,text = "Back", font = FONT10, command = BackToMainMenuSignup)
        BackToMainMenu.place(x=10,y=10,width=70,height=30)
        signupWin.mainloop()

def QuitButton_command():
        exit()

def guestcontinue():
      homes(0)

def StartingMainMenu():
    global root
    global rootexists
    rootexists = True
    root = tk.Tk()
    root.title("Graphical Evolution Simulator")
    root.geometry('600x500')
    root.resizable(width=False, height=False)
    FONT10 = tkFont.Font(family='Times',size=10)
    FONT28 = tkFont.Font(family='Times',size=28)
    FONT7 = tkFont.Font(family='Times',size=7)

    MainMenuLabel =tk.Label(root, font = FONT28, text ='Graphical Evolution \nSimulator')
    MainMenuLabel.place(x=100,y=70)

    LogInButton=tk.Button(root,text = "Log In", font = FONT10, command = LogInButton_command)
    LogInButton.place(x=250,y=180,width=100,height=42)

    SignUpButton=tk.Button(root, font = FONT10, text ="Sign Up",command = SignUpButton_command )
    SignUpButton.place(x=250,y=230,width=100,height=40)

    GuestButton=tk.Button(root, font = FONT7, text =  "Continue as Guest", command = guestcontinue)
    GuestButton.place(x=250,y=280,width=100,height=20)

    QuitButton=tk.Button(root, font = FONT10, text = "Quit", command = QuitButton_command)
    QuitButton.place(x=510,y=10,width=70,height=25)

    root.mainloop()

AccountID = 0
  #Begin Code
StartingMainMenu()