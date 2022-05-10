"""Code pour tester le meilleur génome enregistrer sur une run"""


import pygame
import neat
import math
import sys
import pickle

largeur_écran = 1500
hauteur_écran = 800
generation = 0

class Voiture:
    def __init__(self):
        self.surface = pygame.image.load("voiture.png")
        self.surface = pygame.transform.scale(self.surface, (100,56))
        self.surface_tournée = self.surface
        self.position = [300,640]
        self.angle =0
        self.vitesse= 2
        self.centre = [self.position[0]+50,self.position[1]+28]
        self.capteurs = []
        self.en_vie = True
        self.distance = 0
        self.temps = 0
        self.coins=[]

    def dessiner_capteurs(self,écran):
        for r in self.capteurs :
            position,distance = r
            pygame.draw.line(écran,(0,255,0),self.centre,position,1)
            pygame.draw.circle(écran,(0,255,0),position,5)
            pygame.draw.circle(écran,(0,0,0),self.coins[0],5)
            pygame.draw.circle(écran,(0,0,0),self.coins[1],5)
            pygame.draw.circle(écran,(0,0,0),self.coins[2],5)
            pygame.draw.circle(écran,(0,0,0),self.coins[3],5)

    def dessiner(self,écran):
        écran.blit(self.surface_tournée, self.position)
        self.dessiner_capteurs(écran)
        
    def collisions(self,circuit):
        self.en_vie = True
        for p in self.coins :
            if circuit.get_at((math.floor(p[0]),math.floor(p[1]))) == (255,255,255,255):
                self.en_vie = False

    def action_capteurs(self, angle1, circuit):
        longueur = 0 
        x = self.centre[0] 
        y = self.centre[1]
        while (not circuit.get_at((x,y)) == (255,255,255,255)) :
            longueur += 1
            x = math.floor (self.centre[0] + math.cos(math.radians(self.angle + angle1))*longueur)
            y = math.floor (self.centre[1] - math.sin(math.radians(self.angle + angle1))*longueur)
        self.capteurs.append([(x,y),longueur])

    def rotation_voiture(self,surface,angle):
        rot_image = pygame.transform.rotate(surface, angle)
        return rot_image      

    def calcul_centre(self):
        pi = math.pi
        a = math.radians(self.angle)
        if (self.angle) % 360 >= 0 and (self.angle) % 360 <= 90 :
            return [math.floor(self.position[0]+(56*math.sin(a)+100*math.cos(a))//2),math.floor(self.position[1]+(100*math.sin(a)+56*math.cos(a))//2)]
        if (self.angle) % 360 >= 90 and (self.angle) % 360 <= 180 :
            return [math.floor(self.position[0]+(56*math.sin(pi-a)+100*math.cos(pi-a))//2),math.floor(self.position[1]+(100*math.sin(pi-a)+56*math.cos(pi-a))//2)]
        if (self.angle) % 360 >= 180 and (self.angle) % 360 <= 270 :
            return [math.floor(self.position[0]+(56*math.sin(a-pi)+100*math.cos(a-pi))//2),math.floor(self.position[1]+(100*math.sin(a-pi)+56*math.cos(a-pi))//2)]
        if (self.angle) % 360 >= 270 and (self.angle) % 360 <= 360 :
            return [math.floor(self.position[0]+(56*math.sin(-a)+100*math.cos(-a))//2),math.floor(self.position[1]+(100*math.sin(-a)+56*math.cos(-a))//2)]

    def mise_à_jour(self, circuit):
        #self.vitesse =  10

        self.surface_tournée = self.rotation_voiture(self.surface, self.angle)

        self.position[0] += math.floor(math.cos(math.radians(self.angle))*self.vitesse)
        if self.position[0] < 20 :
            self.position[0] = 20
        elif self.position[0] > largeur_écran - 120 :
            self.position[0] = largeur_écran - 120
        self.position[1] -= math.floor(math.sin(math.radians(self.angle))*self.vitesse)
        if self.position[1] < 20 :
            self.position[1] = 20
        elif self.position[1] > hauteur_écran - 120 :
            self.position[1] = hauteur_écran - 120

        self.distance += self.vitesse
        self.temps += 1

        self.centre = self.calcul_centre()
        theta = math.pi - math.radians(26 + self.angle)
        long = 55
        theta1 = theta1 = math.radians(self.angle - 26)
        xg = math.cos(theta)*long
        yg = math.sin(theta)*long
        xd = math.cos(theta1)*long
        yd = math.sin(theta1)*long
        coin_hg = [math.floor(self.centre[0] - xg*0.9), math.floor(self.centre[1]- yg*0.9)]
        coin_hd = [math.floor(self.centre[0] + xd*0.95),math.floor(self.centre[1] - yd*0.95)]
        coin_bg = [math.floor(self.centre[0] - xd*0.98),math.floor(self.centre[1] + yd*0.98)]
        coin_bd = [math.floor(self.centre[0] + xg), math.floor(self.centre[1] + yg)]
        self.coins=[coin_hg,coin_hd,coin_bg,coin_bd]
        self.collisions(circuit)
        self.capteurs = []
        for theta in range (-90,120,45):
            self.action_capteurs(theta,circuit)

    def données(self):
        res=[0,0,0,0,0]
        for i,r in enumerate (self.capteurs) :
            res[i] =(r[1])
        return res

    def récompense(self):
        return self.distance

def simulation(genomes,config):
    nets,voitures = [],[]
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        voitures.append(Voiture())
        
    pygame.init()
    écran = pygame.display.set_mode((largeur_écran,hauteur_écran))
    horloge = pygame.time.Clock()
    circuit = pygame.image.load('circuit_difficile2.png')

    global generation
    generation += 1

    temps = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
                
        for index, voiture in enumerate(voitures):
            output = nets[index].activate(voiture.données())
            if output[0]>0.33:
                voiture.angle += 10
            elif output[0]<-0.33:
                voiture.angle -= 10
            if output[1]>0.33:
                if voiture.vitesse <= 10 :            
                    voiture.vitesse += 2
            elif output[1]<-0.33 :
                if voiture.vitesse >= -10 :
                    voiture.vitesse -=2

        voitures[0].mise_à_jour(circuit)
                
        temps += 1

        if temps == 1250 :
            break

        écran.blit(circuit, (0, 0))
        for voiture in voitures:
                voiture.dessiner(écran)
        pygame.display.flip()
        horloge.tick(60)
        if not (voitures[0].en_vie) :
            break

        
if __name__ == "__main__":
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    with open("meilleur_difficile1.pkl", "rb") as f:
        genome = pickle.load(f)
    genomes= [(1,genome)]
    simulation(genomes, config)
