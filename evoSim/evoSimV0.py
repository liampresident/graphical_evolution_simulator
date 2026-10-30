#Computer Science NEA
import random
import tkinter as tk
import tkinter.font as tkFont
import sqlite3
import pygame
import math
import time
import hashlib
from tkinter import END, HORIZONTAL
from tkinter import *

def runSimulation(simID):
  #define all classes
  class apex():
    pass
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

    def newplant(self):
      mutationRate = 0.01
      if self.maturity ==400:
         newX = self.x + random.randint(-50,50)
         newY = self.y + random.randint(-50,50)
         l = plant(newX,newY,1,0)
         plants.append(l)
  class cell():
    def __init__(self, CellID, speed, size, x, y, sight, energy ,diet, metabolism, fertility, angle):
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
          plants.remove(p)
          o.energy += p.size * o.diet
      # eat meat
      for m in meatL:
        c2 = ((o.x-m.x)**2)+((o.y-m.y)**2)
        distance = math.sqrt(c2)
        if distance < o.size and len(meatL) !=0:
          meatL.remove(m)
          o.energy += m.size * o.diet

    def update(self):
      o.energy -= o.metabolism
      if o.energy <=0:
        objects.remove(o)
        FoodID = FindFoodID(0)
        m = meat(FoodID,o.x,o.y,o.size/2)
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
      else:
        pass
  class meat():
    def __init__(self, FoodID, x, y, size):
      self.FoodID = FoodID
      self.x = x
      self.y = y
      self.size = size

  #open connection to database
  conn = sqlite3.connect('Simulator.db')
  cursor = conn.cursor()
  query1 = f'SELECT * FROM Cells WHERE simID = "{simID}";'
  query2 = f'SELECT COUNT(*) FROM Cells WHERE simID = "{simID}";'
  query3 = f'SELECT COUNT(*) FROM Foods WHERE simID = "{simID}" AND MorP = "Plant";'
  query4 = f'SELECT COUNT(*) FROM Foods WHERE simID = "{simID}" AND MorP = "Meat";'
  #display
  screen = pygame.display.set_mode((worldsize,worldsize))
  clock = pygame.time.Clock()
  global objects
  global plants
  global meatL
  #arrays that will hold all information during running
  objects = []
  plants = []
  meatL = []


  count = cursor.execute(query2)
  details = cursor.execute(query1)
  for i in range(count):
    #pull all information from cell database
    CellID     = details[i][0]
    speed      = details[i][2]
    size       = details[i][3]
    metabolism = details[i][4]
    fertility  = details[i][5]
    diet       = details[i][6]
    sight      = details[i][7]
    energy     = details[i][8]
    posx       = details[i][9]
    posy       = details[i][10]
    lifespan   = details[i][11]
    angle      = details[i][12]
    #create cell
    o = cell(speed,size,posx,posy,sight,energy,0,diet,metabolism,fertility)
    objects.append(o)
  count2   = cursor.execute(query3)
  details2 = cursor.execute(query4)

  #plants
  for i in range(count2):
    FoodID = details2[i][0]
    posx   = details2[i][2]
    posy   = details2[i][3]
    size   = details2[i][4]
    #0 is mnaturity
    #recreate plants
    p = plant(posx,posy,size,0)
    plants.append(p)
  count3 = cursor.execute(query4)
  #Meat
  for i in range(count3):
    FoodID = details2[i][0]
    posx   = details2[i][2]
    posy   = details2[i][3]
    size   = details2[i][4]
    #0 is maturity
    #recreate plants
    m = meat(FoodID, posx, posy, size)
    meatL.append(m)

  paused = False
  pygame.init()
  mutationRate = mutationrateScale.get()
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
      #draw pause screen
      pygame.draw.rect(screen,'white',pygame.Rect(80, 80, 220, 220))
      font = pygame.font.SysFont(None, 24)
      img = font.render('PAUSED', False, (0,0,0))
      screen.blit(img, (150, 150))


      #resume
      pygame.draw.rect(screen,'black',pygame.Rect(140, 200, 80, 20),1)
      font = pygame.font.SysFont(None, 24)
      img = font.render('RESUME', False, (0,0,0))
      screen.blit(img, (144, 203))
    pygame.display.flip()
    clock.tick(60)



def HashPassword(password):
  ascii = ''.join(str(ord(a)) for a in password)#Convert string into ascii
  mod = str(int(ascii) // 11)
  #Hash method
  import hashlib
  hashed = hashlib.md5(mod.encode())
  p = hashed.hexdigest()
  asciiHash = ''.join(str(ord(b)) for b in p) #Convert digest back into ascii
  newList =[]
  broken = asciiHash.split('5') # Split the acsii digest anywhere the number 5 appears
  broken = [x for x in broken if x != ''] # Remove null values
  for x in range(len(broken)): # Mod all integers in list by 23
    newList.append(int(broken[x])//23)
  def makeString(list):#Recursive function to convert a list to string
    if len(list) == 0:
      return ''
    else:
      return str(list[0]) +  makeString(list[1:])
  final = []
  convertedList =[]
  finalHash = makeString(newList)
  return(finalHash)
def FindFoodID(ID):
  global FoodID
  conn = sqlite3.connect('Simulator.db')
  cursor = conn.cursor()
  query = f'SELECT Size FROM Foods WHERE FoodID = "{ID}";'
  cursor.execute(query)
  if not cursor.fetchone():
    FoodID = ID
  else:
    ID += 1 
    cursor.close()
    FindFoodID(ID)
def FindCellID(ID):
  global CellID
  conn = sqlite3.connect('Simulator.db')
  cursor = conn.cursor()
  query = f'SELECT Size FROM Cells WHERE CellID = "{ID}";'
  cursor.execute(query)
  if not cursor.fetchone():
    CellID = ID
  else:
    ID += 1 
    cursor.close()
    FindCellID(ID)
def FindSimID(ID):
  global simID

  conn = sqlite3.connect('Simulator.db')
  cursor = conn.cursor()
  query = f'SELECT SimName FROM Simulations WHERE SimID = "{ID}";'
  cursor.execute(query)
  if not cursor.fetchone():
    simID = ID
  else:
    ID += 1 
    cursor.close()
    FindSimID(ID)

global homeExists
global home
homeExists = False
global AccountID
global LoggedIn
LoggedIn = False
global root
global rootexists
rootexists = False

def homes(AccountID):
  global ID
  ID = AccountID
  global rootexists
  if rootexists == True:
    root.destroy()
    rootexists = False
  def ContinueButton():
      home.destroy()

  def NewButton():
      home.destroy()

      def startNew():
        #Open connection to database
        conn = sqlite3.connect('Simulator.db')
        cursor = conn.cursor()

        #Generate a simID for the new world and collect all options from user
        global simID
        FindSimID(1)
        print(simID)

        worldsize = s.get()

        PopulationControl = 'No'
        if pop.get() == 1:
          PopulationControl = 'Yes'
        Biomes = 'No'
        if bio.get() == 1:
          Biomes = 'Yes'

        name = str(simNameEntry.get())
        day = 0
        status = 'Alive'
        mr = mutationrateScale.get()

        cursor.execute(f'INSERT INTO Simulations(AccountID, SimID, SimName, Day, Status, WorldSize, Biomes, PopulationControl, MutationRate) VALUES({AccountID},{simID}, "{name}" , {day}, "{status}", {worldsize}, "{Biomes}", "{PopulationControl}", {mr});')
        conn.commit()
        cursor.close()
        cellnumber = cellnumberScale.get()

        #Generate Cells and Add them to database Cells
        for x in range (cellnumber):
          conn = sqlite3.connect("Simulator.db")
          cursor = conn.cursor()
          global CellID
          FindCellID(0)
          ranx = random.randint(0,worldsize)
          rany = random.randint(0,worldsize)
          angle = random.randint(0,360)

          #Set everything Uniformly
          ransize = sizeScale.get()
          n = speedScale.get()
          ranspeed = [n,n]
          ransight = sightScale.get()
          metabolism = ((ranspeed[0])**2)/(ransize)
          fertility = fertilityScale.get()
          randiet = (dietScale.get())/100
          energy = 5*ransize
          #If requested to be random, then change everything to random

          if i.get() == 1:
            ransize = random.randint(5,10)
            n = random.uniform(0,1)
            ranspeed = [n,n]
            ransight = random.randint(0,200)
            metabolism = ((ranspeed[0])**2)/(ransize)
            fertility = random.randint(1,100)
            randiet = random.uniform(0,1)


          #Store to Database
          query =f'INSERT INTO Cells (CellID,SimID,Speed,Size,Metabolism,Fertility,Diet,Sight,Energy,Position_x,Position_y,Lifespan,Angle) VALUES({CellID},{simID},{n},{ransize},{metabolism},0,{randiet},{ransight},{energy},{ranx},{rany},0,{angle});'
          cursor.execute(query)
          conn.commit()
          cursor.close()




        #Same for plants
        for p in range(cellnumber+20):
          conn = sqlite3.connect("Simulator.db")
          cursor = conn.cursor()
          global FoodID
          FindFoodID(0)
          ranx = random.randint(10,worldsize - 10)
          rany = random.randint(10,worldsize - 10)
          ransize = random.randint(0,5)
          ranmaturity = random.randint(1,300)

          query = f'INSERT INTO Foods(FoodID,SimID,Position_x,Position_y,Size,MorP) VALUES({FoodID},{simID},{ranx},{rany},{ransize},"Plant");'
          cursor.execute(query)
          conn.commit()
          cursor.close()

        #Terminate connection and call sub routine to get world up and running

        runSimulation(simID)
        create.destroy()

#####################################
      def info():
          la1 = Label(create, text = 'Uniform: All cells are created with the same stats\nRandom: Each cell is created with random attributes upon creation')
          la1.place(x=105,y=300)
          la2 = Label(create, text = 'Speed: How fast they move \nSize: How big they are \nSight: how far each cell can detect objects like food or cells \nFertility: how frequent a cell will reproduce')
          la2.place(x=105,y=330)
      def reset():
            speedScale.set(0)
            sizeScale.set(0)
            fertilityScale.set(0)
            sightScale.set(0)
            dietScale.set(0)
      def Back():
        create.destroy()
        homes(ID)

      def disable_scales():
        speedScale.set(0)
        sizeScale.set(0)
        fertilityScale.set(0)
        sightScale.set(0)
        dietScale.set(0)
        if i.get() == 1:
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

      i = tk.IntVar()
      uniformCheckbox = tk.Checkbutton(create, text = 'Uniform Genes', variable = i,onvalue = 0,command = disable_scales)
      uniformCheckbox.place(x = 105,y=100)
      randomCheckbox = tk.Checkbutton(create, text = 'Random Genes', variable = i,onvalue = 1, command = disable_scales)
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

  def LoadButton():
    print('I do nothing yet')



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
          NewPassword = HashPassword(PasswordEntry.get)
          NewRecovery = MemorableWordEntry.get()
          conn = sqlite3.connect('Simulator.db')
          cursor = conn.cursor()
          query = f"UPDATE Users SET Username = '{NewUsername}',Password = '{NewPassword}', Recovery_Word = '{NewRecovery}' WHERE AccountID = {AccountID};"
          cursor.execute(query)
          conn.commit()
          la1 = Label(accountwin, text = 'Account Successfully Updated')
          la1.place(x = 100,y = 350)
          cursor.close()
        def Delete():
          conn = sqlite3.connect('Simulator.db')
          cursor = conn.cursor()
          query = f"DELETE FROM Users WHERE AccountID = {ID}"
          cursor.execute(query)
          conn.commit()
          accountwin.destroy()
          cursor.close()
          StartingMainMenu()
        def Back():
            homes(AccountID)
            accountwin.destroy()

        accountwinLabel =tk.Label(accountwin, font = FONT28, text ='Account Settings')
        accountwinLabel.place(x=50,y=10,width=494,height=100)

        conn = sqlite3.connect('Simulator.db')
        cursor = conn.cursor()
        statement = f"SELECT Username,Password,RecoveryWord FROM Users WHERE AccountID = {AccountID};"
        cursor.execute(statement)
        details = cursor.fetchone()


        Username = Label(accountwin,text = 'Username:', font = FONT10)
        Username.place(x=100,y=150)
        UsernameEntry = Entry(accountwin)
        UsernameEntry.place(x=300,y=150)
        UsernameEntry.insert(0,details[0])

        Password = Label(accountwin,text = 'Password:', font = FONT10)
        Password.place(x=100,y=170)
        PasswordEntry = Entry(accountwin)
        PasswordEntry.place(x=300,y=170)

        MemorableWord = Label(accountwin,text = 'Memorable Word:', font = FONT10)
        MemorableWord.place(x=100, y = 190)
        MemorableWordEntry = Entry(accountwin)
        MemorableWordEntry.place(x=300, y = 190)
        MemorableWordEntry.insert(0,details[2])

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

  global home
  homeExists = True
  home = tk.Tk()
  home.title("Graphical Evolution Simulator")
  home.geometry('600x500')
  home.resizable(width=True, height=True)
  FONT10 = tkFont.Font(family='Times',size=10)
  FONT28 = tkFont.Font(family='Times',size=28)
  FONT7 = tkFont.Font(family='Times',size=7)

  homeScreenLabel =tk.Label(home, font = FONT28, text ='Graphical Evolution Simulator')
  homeScreenLabel.place(x=50,y=70,width=494,height=100)


  NewButton =tk.Button(home, font = FONT10, text ='New', command = NewButton)
  NewButton.place(x=50,y=240)

  if AccountID != 0:
    ContinueButton =tk.Button(home, font = FONT10, text ='Continue', command = ContinueButton)
    ContinueButton.place(x=50,y=200)
    LoadButton =tk.Button(home, font = FONT10, text ='Load', command = LoadButton)
    LoadButton.place(x=50,y=280)
    AccountButton =tk.Button(home, font = FONT10, text ='Account', command = AccountButton)
    AccountButton.place(x=50,y=320)

  LogOffButton =tk.Button(home, font = FONT10, text ='Log Off', command = LogOffButton)
  LogOffButton.place(x=400,y=20)

  QuitButton =tk.Button(home, font = FONT10, text ='Quit', command = QuitButton_command)
  QuitButton.place(x=500,y=20)

  ID = AccountID
  accountnum = tk.Label(home,font = FONT10, text = '{}'.format(ID))
  accountnum.place(x=10,y=10)
  home.mainloop()

def LogInButton_command():
        global rootexists
        if rootexists == True:
                root.destroy()
                rootexists = False

        def BackToMainMenuLogin():
                loginWin.destroy()
                StartingMainMenu()

        def submitLogIn():
            global loginWin
            EnteredUsernameEntry = UsernameEntry.get()
            EnteredUserPasswordEntry = HashPassword(UserPasswordEntry.get())
            con = sqlite3.connect("Simulator.db")
            cur = con.cursor()
            statement = f"SELECT Username FROM Users WHERE Username = '{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
            cur.execute(statement)
            if not cur.fetchone():
                label = Label(loginWin,text ='Login Failed').place(x=100,y=300)
            else:
                con = sqlite3.connect("Simulator.db")
                cur = con.cursor()
                statement = f"SELECT AccountID FROM Users WHERE Username='{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
                cur.execute(statement)
                AccountID = cur.fetchone()[0]
                loginWin.destroy()
                cur.close()
                homes(AccountID)



        def clearLogin():
                UsernameEntry.delete(0, END)
                UserPasswordEntry.delete(0, END)
        def ForgottenPassword():
                loginWin.destroy()
                def submitRecovery():

                  Username = UsernameEntry.get()
                  MemorableWord = HashPassword(MemorableWordEntry.get())
                  con = sqlite3.connect('Simulator.db')
                  cursor = con.cursor()
                  query = f"SELECT AccountID FROM Users WHERE Username = '{Username}'AND RecoveryWord = '{MemorableWord}';"
                  cursor.execute(query)
                  if not cursor.fetchone():
                    label1 = Label(recoveryWin,text = 'No Account Found').place(x=100,y=350)
                  else:
                    #Set New Password
                    newPassword = tk.Tk()
                    recoveryWin.destroy()
                    def submit():
                      if entry.get() == confirmEntry.get():
                        password = HashPassword(entry.get())
                        label = Label(newPassword,text = 'Changed successfully').place(x = 100,y = 350)
                        query2 = f"UPDATE Users SET Password = {password} WHERE AccountID = {AccountID};"
                        cursor.execute(query2)
                        con.commit()
                        cursor.close()
                      else:
                        label = Label(newPassword,text = 'Details incorrect').place(x = 100,y = 350)
                    newPassword.geometry('400x400')
                    newPassword.title("Set New Password")
                    password = Label(newPassword, text = 'Password: ').place(x = 100,y=180)
                    entry = Entry(newPassword).place(x = 200,y=180)
                    confirmPassword = Label(newPassword, text = 'Re-enter: ').place(x=100,y=200)
                    confirmEntry = Entry(newPassword).place(x = 200, y = 200)

                    submit = Button(newPassword,text = 'Submit',command = submit).place(x=190,y=300)


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
                AccountRecoveryLabel.place(x=50,y=70,width=494,height=100)

                UsernameLabel =tk.Label(recoveryWin, font = FONT10, text ='Username: ')
                UsernameLabel.place(x=50,y=200)
                UsernameEntry = tk.Entry(recoveryWin)
                UsernameEntry.place(x = 200, y = 200)

                MemorableWordLabel =tk.Label(recoveryWin, font = FONT10, text ='Memorable Word:')
                MemorableWordLabel.place(x=50,y=300)
                MemorableWordEntry = tk.Entry(recoveryWin)
                MemorableWordEntry.place(x = 200, y = 300)

                submitRecovery = tk.Button(recoveryWin,text = "Submit", font = FONT10, command = submitRecovery)
                submitRecovery.place(x=150,y=400,width=100,height=30)

                clearRecovery = tk.Button(recoveryWin,text = "Clear", font = FONT10, command = clearRecovery)
                clearRecovery.place(x=300,y=400,width=100,height=30)

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
                EnteredUsernameEntry = str(UsernameEntry.get())
                EnteredUserPasswordEntry = HashPassword(str(UserPasswordEntry.get()))
                EnteredMemorableWordEntry = HashPassword(str(MemorableWordEntry.get()))

                connect = sqlite3.connect("Simulator.db")
                cursor = connect.cursor()
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

                cursor.execute("INSERT INTO Users (AccountID,Username,Password,RecoveryWord) VALUES(?,?,?,?)",(newID,EnteredUsernameEntry,EnteredUserPasswordEntry,EnteredMemorableWordEntry))
                connect.commit()
                signupWin.destroy()
                statement = f"SELECT AccountID from Users WHERE Username='{EnteredUsernameEntry}' AND Password = '{EnteredUserPasswordEntry}';"
                cursor.execute(statement)

                newID = cursor.fetchone()[0]
                cursor.close()
                homes(newID)



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

    MainMenuLabel =tk.Label(root, font = FONT28, text ='Graphical Evolution Simulator')
    MainMenuLabel.place(x=50,y=90,width=494,height=30)

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

StartingMainMenu()