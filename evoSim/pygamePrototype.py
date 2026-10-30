import pygame
import random
worldsize = 200
biomes = True
pygame.init()
screen = pygame.display.set_mode((worldsize, worldsize))
running = True

biomes_dict = {"block1":[], "block2":[], "block3":[], "block4":[], "block5":[],"block6":[],"block7":[], "block8":[],"block9":[], "block10":[], "block11":[], "block12":[], "block13":[], "block14":[],"block15":[],"block16":[]}
if biomes == True:
  randomList = [] #Assign each block a random colour, Light Green - Light Blue - Dark Green - Sandy yellow
  colours = [(144, 238, 144), (173, 216, 230), (0, 100, 0), (211, 169, 108)]
for i in range(16):
    colour = random.choice(colours)
    if colour == (144, 238, 144):
        biome_type = 'Normal'
    elif colour == (173, 216, 230):
        biome_type = 'Water'
    elif colour == (0, 100, 0):
        biome_type = 'Forest'
    else:
        biome_type = 'Desert'
    randomList.append([colour, biome_type])
list = []
for i in range(len(randomList)):
  list.append(randomList[i][0])
query = f'UPDATE Simulations SET BiomePattern = {list} WHERE SimID = {simID};'
biomes_dict['block1']  = randomList[0]
biomes_dict['block2']  = randomList[1]
biomes_dict['block3']  = randomList[2]
biomes_dict['block4']  = randomList[3]
biomes_dict['block5']  = randomList[4]
biomes_dict['block6']  = randomList[5]
biomes_dict['block7']  = randomList[6]
biomes_dict['block8']  = randomList[7]
biomes_dict['block9']  = randomList[8]
biomes_dict['block10'] = randomList[9]
biomes_dict['block11'] = randomList[10]
biomes_dict['block12'] = randomList[11]
biomes_dict['block13'] = randomList[12]
biomes_dict['block14'] = randomList[13]
biomes_dict['block15'] = randomList[14]
biomes_dict['block16'] = randomList[15]
while running == True:
  bsize = worldsize / 4 # size of the block
  wz = worldsize # Visual aspects of biomes
  pygame.draw.rect(screen,biomes_dict['block1'][0], pygame.Rect(0, 0, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block2'][0], pygame.Rect(wz/4, 0, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block3'][0], pygame.Rect(wz/2, 0, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block4'][0], pygame.Rect(3*(wz/4), 0, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block5'][0], pygame.Rect(0, wz/4, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block6'][0], pygame.Rect(wz/4, wz/4, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block7'][0], pygame.Rect(wz/2, wz/4, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block8'][0], pygame.Rect(3*(wz/4), wz/4, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block9'][0], pygame.Rect(0, wz/2, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block10'][0], pygame.Rect(wz/4, wz/2, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block11'][0], pygame.Rect(wz/2, wz/2, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block12'][0], pygame.Rect(3*(wz/4), wz/2, bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block13'][0], pygame.Rect(0, 3*(wz/4), bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block14'][0], pygame.Rect(wz/4, 3*(wz/4), bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block15'][0], pygame.Rect(wz/2, 3*(wz/4), bsize, bsize))
  pygame.draw.rect(screen,biomes_dict['block16'][0], pygame.Rect(3*(wz/4), 3*(wz/4), bsize, bsize))



  
  pygame.display.update()