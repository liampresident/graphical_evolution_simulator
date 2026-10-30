password = 'congratuaationsa '
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
