import time

class Character:
    def __init__(self, name, hp, damage):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
    
    def attack(self, target):
        print(self.name+" dealt "+str(self.damage)+" damage")
        target.hp = target.hp - self.damage
        if target.hp < 0:
            target.hp = 0
        print(target.name+" HP:",str(target.hp),"/",str(target.max_hp))
        print("---------------------------------------")
        time.sleep(1)

    
joe = Character('Joe',10,2)
bob = Character('Bob',10,3)

while True:
    joe.attack(bob)
    if bob.hp <= 0:
        print("Joe killed Bob!")
        break
    bob.attack(joe)
    if joe.hp <= 0:
        print("Bob killed Joe!")
        break





