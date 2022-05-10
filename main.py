from __future__ import print_function
import pygame
import neat
import math
import sys
import pickle
import visualize
#import graphviz


largeur_écran = 1500
hauteur_écran = 800
generation = 0

"""Création de la classe voiture avec les paramètres utiles ainsi que l'aspect visuel
"""

class Voiture:
    def __init__(self):
        self.surface = pygame.image.load("voiture.png")
        self.surface = pygame.transform.scale(self.surface, (100,56))
        self.surface_tournée = self.surface #création de la "surface" de la voiture 
        #et de celle servant pour la rotation
        self.position = [300,640] #position initiale de la voiture
        self.angle =0#par rapport à l'axe horizontal de la voiture
        self.vitesse= 10 #vitesse initiale de la voiture
        self.centre = [self.position[0]+50,self.position[1]+28] #Centre de la voiture
        self.capteurs = [] #Liste contenant la position finale et la distace parcourue par les lasers
        self.sur_la_route = True
        self.distance = 0 #Distance parcourue depuis le début
        self.temps = 0 
        self.coins=[] #Liste contenant la position des 4 coins de la voiture



    def dessiner_capteurs(self,écran):
        for r in self.capteurs :
            position,distance = r
            pygame.draw.line(écran,(0,255,0),self.centre,position,1)
            pygame.draw.circle(écran,(0,255,0),position,5)
        pygame.draw.circle(écran,(0,0,0),self.coins[0],5)
        pygame.draw.circle(écran,(0,0,0),self.coins[1],5)
        pygame.draw.circle(écran,(0,0,0),self.coins[2],5)
        pygame.draw.circle(écran,(0,0,0),self.coins[3],5)


    def dessiner(self,écran):#Mise à jour de l'affichage d'une voiture
        écran.blit(self.surface_tournée, self.position)
        self.dessiner_capteurs(écran)
        
    def hors_piste(self,circuit):#détection de hors-piste grâce à la couleur du fond à la positionn des coins
        self.sur_la_route = True
        for p in self.coins :
            if circuit.get_at((math.floor(p[0]),math.floor(p[1]))) == (255,255,255,255):
                self.sur_la_route = False

    def action_capteurs(self, angle1, circuit):
        longueur = 0 
        x = self.centre[0] 
        y = self.centre[1]
        while (not circuit.get_at((x,y)) == (255,255,255,255)) :
            longueur += 1
            x = math.floor (self.centre[0] + math.cos(math.radians(self.angle + angle1))*longueur)
            y = math.floor (self.centre[1] - math.sin(math.radians(self.angle + angle1))*longueur)
        self.capteurs.append([(x,y),longueur])#Laser de longueur infinie qui s'arrête lorsqu'il atteint le bord

    def rotation_voiture(self,surface,angle):
        rot_image = pygame.transform.rotate(surface, angle)
        return rot_image      

    def calcul_centre(self):#Nouveau centre après la mise à jour
        pi = math.pi
        a = math.radians(self.angle)
        if (self.angle) % 360 >= 0 and (self.angle) % 360 <= 90 :
            return [math.floor(self.position[0]+(56*math.sin(a)+100*math.cos(a))//2),math.floor(self.position[1]+(100*math.sin(a)+56*math.cos(a))//2)]
        elif (self.angle) % 360 >= 90 and (self.angle) % 360 <= 180 :
            return [math.floor(self.position[0]+(56*math.sin(pi-a)+100*math.cos(pi-a))//2),math.floor(self.position[1]+(100*math.sin(pi-a)+56*math.cos(pi-a))//2)]
        elif (self.angle) % 360 >= 180 and (self.angle) % 360 <= 270 :
            return [math.floor(self.position[0]+(56*math.sin(a-pi)+100*math.cos(a-pi))//2),math.floor(self.position[1]+(100*math.sin(a-pi)+56*math.cos(a-pi))//2)]
        elif (self.angle) % 360 >= 270 and (self.angle) % 360 <= 360 :
            return [math.floor(self.position[0]+(56*math.sin(-a)+100*math.cos(-a))//2),math.floor(self.position[1]+(100*math.sin(-a)+56*math.cos(-a))//2)]

    def mise_à_jour(self, circuit):#Fonction appelée à chaque changement de "frame"
        #self.vitesse =  10

        self.surface_tournée = self.rotation_voiture(self.surface, self.angle)

        self.position[0] += math.floor(math.cos(math.radians(self.angle))*self.vitesse) 
        #Calcul de la nouvelle position, de sorte qu'elle ne sorte pas de l'écran
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
        self.hors_piste(circuit)
        self.capteurs = []
        for theta in range (-90,135,45):
            self.action_capteurs(theta,circuit)

    def données(self):#On récupère la distance parcourue par chaque laser, c'est la couche d'entrée du réseau
        res=[0,0,0,0,0]
        for i,r in enumerate (self.capteurs) :
            res[i] =(r[1])
        return res

    def récompense(self):
        return self.distance

"""Utilisation du module Neat"""

def simulation(genomes,config):
    nets,voitures = [],[]
    for genome_id, genome in genomes: #Création des voitures et de leur réseau de neurones associé
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        voitures.append(Voiture())
        
    pygame.init()
    écran = pygame.display.set_mode((largeur_écran,hauteur_écran))
    horloge = pygame.time.Clock()
    circuit = pygame.image.load('circuit_facile.png')#Choix du circuit

    global generation
    generation += 1

    temps = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
                
        for index, voiture in enumerate(voitures):
            output = nets[index].activate(voiture.données())
            #Neurone de sortie pour la rotation
            if output[0]>0.33:  #On sépare l'intervalle [-1,1] en trois pour prendre la décision
                voiture.angle += 10
            elif output[0]<-0.33:
                voiture.angle -= 10
            #Neurone de sortie pour la vitesse
            if output[1]>0.33: #On sépare l'intervalle [-1,1] en trois pour prendre la décision
                if voiture.vitesse <= 10 : #Vitesse max           
                    voiture.vitesse += 2
            elif output[1]<-0.33 :
                if voiture.vitesse >= -10 : # Vitesse Min
                    voiture.vitesse -=2

        voitures_restantes = 0
        for i, voiture in enumerate(voitures):
            if voiture.sur_la_route:
                voitures_restantes += 1
                voiture.mise_à_jour(circuit)
                genomes[i][1].fitness = voiture.récompense() #Fonction de fitness de l'algorithme génétique
                
        if voitures_restantes == 0:
            break

        temps += 1

        if temps == 1250 : 
            assert voitures_restantes > 0 # Test unitaire pour vérifier qu'il reste au moins une voiture
            break

        écran.blit(circuit, (0, 0))
        for voiture in voitures:
            if voiture.sur_la_route:
                voiture.dessiner(écran)
        pygame.display.flip()
        horloge.tick(60)

        
if __name__ == "__main__":
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    meilleur=p.run(simulation, 1000)
    
    print('\nBest genome:\n{!s}'.format(meilleur))
    node_names = {-1:'-90', -2: '-45',-3: '0',-4:'45', -5:'90', 0:'angle',1:'vitesse'}
    #visualize.draw_net(config, meilleur, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    #visualize.plot_species(stats, view=True)
    with open("meilleur.pkl", "wb") as f: #enregistrement du meilleur génome pour le tester sur d'autres circuits
        pickle.dump(meilleur, f)
        f.close()

