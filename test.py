xd = list()
xd.append("test")
xd.append("test")
xd.append("test")
xd.append("test")
xd.append("test")


x = 0
listt = "("
while True:
    if x == len(xd):
        break
    if x+1 == len(xd):
        listt+=str(xd[x])
    else:
        listt+=str(xd[x])+", "
    print(xd[x], x)
    x+=1
listt+=")"
print(listt)