import names, time

def randomName():
    return names.get_full_name()


for x in range(10):
    name = randomName()
    print(name)
    time.sleep(1)