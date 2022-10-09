def add(x,y):
  print(x+y)

def subtract(x,y):
  print(x-y)

function_list = {'add', 'subtract'}

def caller(func, x, y):
  
  eval(func)(x,y) # more security exploits
  
  if func in function_list:
    eval(func)(x,y) # less security exploits

caller("add", 1, 2)
var = input("Enter a string: ") 

if "\"" in var:
    print([var]) 
else: 
    pass