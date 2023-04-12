import re

def split_pol(txt):
  sfind = '([+-]?) *([\d]*)([a-zA-Z]?)(?:\^(\d+))?'
  temp = []
  for k in re.findall(sfind, txt):
    c, var, exp = None, None, None
    if k!=('', '', '', ''):
      if k[1] == '':
        c = 1
      else:
        c = int(k[1])
        if k[0] == '-': c =-c
        if k[3] == '':
          if k[2]=='':
            e=0
          else:
            e=1
        else:
          e = int(k[3])
        temp.append((c, e))
  return temp

def add(pol1, pol2):
  for i in range(len(pol1)):
    for j in pol2:
      if pol1[i][1] == j[1]:
        pol1[i] = ((pol1[i][0] + j[0]), pol1[i],[1])
        pol2.remove(j)
  pol3 = pol1 + pol2
  for j in pol3:
    if j[0]==0:
      pol3.remove(j)
  return sorted(pol3)

def final_poly(poly):
  s = ''
  for ele in poly:
    if ele[0] == 1 and ele[1]:
      s = s + ' + ' + ' x**' + str(ele[1])
    elif ele[0]>0 and ele[1] == 1:
      s=s + ' + '+str(ele[0])+ ' x '
    elif ele[0]<0 and ele[1]==1:
      s=s+str(ele[0])+ ' x '
    elif ele[0]>0 and ele[1]:
      s=s + ' + ' +str(ele[0])+ ' x**'+str(ele[1])
    elif ele[0] < 1 and ele[1]:
      s=s +str(ele[0]) + ' x**'+str(ele[1])
    elif ele[0]>0 and ele[1]==0:
      s=s+' + ' + str(ele[0])
    elif ele[0]>0 and ele[1]==1:
      s=s+'-'+str(ele[0])
  return s


def add_polynomials(polynomial_str):
  l1 = re.findall(r'\(.*?\)', polynomial_str)
  s1 = l1[0]
  s2 = l1[1]

  s1 = s1.replace("(","")
  s1 = s1.replace(")","")
  s2 = s2.replace("(","")
  s2 = s2.replace(")","")
  s1 = s1.replace("**","^")
  s2 = s2.replace("**","^")

  pol1 = split_pol(s1)
  pol2 = split_pol(s2)
  total = add(pol1, pol2)
  eq = final_poly(total)
  print(str(polynomial_str)+ ' = '+ eq)

add_polynomials('(4x**5 + 3x**3 + 3) + (6x**6 + 7x**3 + 4)')