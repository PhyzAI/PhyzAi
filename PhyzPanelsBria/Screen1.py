'''
Created on Jul 17, 2023

@author: briac
'''
import pygame as pg
from pygame.locals import *
from random import randint
import math 

# init
pg.init()
flags = pg.FULLSCREEN
screen = pg.display.set_mode((800, 400), flags, vsync=1)
#screen = pg.display.set_mode((800, 400))

BLUE  = (48, 255, 194)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (249, 0, 0)
GREEN = (0, 239, 0)
YELLOW = (255, 255, 0)

FONT      = pg.font.SysFont("Roboto", 50) # large font
FONTsmall = pg.font.SysFont("Roboto", 22) # small font

background = pg.image.load("PhyzAi Background.png")
backgroundRect = background.get_rect(center=(400, 200))

class Bar():
    def __init__(self, rect, bar = BLUE, outline = WHITE):
        self.rect = pg.Rect(rect)
        self.bar = bar
        self.outline = outline
        self.value = 0
    def draw(self, surf):
        length = round(self.value * self.rect.height / 100)
        top = self.rect.height - length
        pg.draw.rect(surf, self.bar, (self.rect.x, self.rect.y + top, self.rect.width, length))
        pg.draw.rect(surf, self.outline, self.rect, 2)    
   
#create 3 progress bar
bar1 = Bar((200, 80, 50, 300))
bar2 = Bar((350, 80, 50, 300))
bar3 = Bar((500, 80, 50, 300))


done = False

finished = FONT.render("Success!", True, "white")
finished_rect = finished.get_rect(center = (650, 200))

tempText = FONT.render("This is a test", True, "BLUE")
tempTextRect = tempText.get_rect(center = (400, 200))

randtime = randint(2, 10)

radar_sweep_angle = 0
radar_sweep_length = 170

map = pg.image.load("map.png")
mapRect = map.get_rect(center = (405, 225))

engine = FONT.render("ENGINES:", True, "WHITE")
engineRect = tempText.get_rect(center = (200, 75))
shields = FONT.render("SHIELDS:", True, "WHITE")
shieldsRect = tempText.get_rect(center = (200, 150))
toilets = FONT.render("TOILETS:", True, "WHITE")
toiletsRect = tempText.get_rect(center = (200, 225))
cantina = FONT.render("CANTINA:", True, "WHITE")
cantinaRect = tempText.get_rect(center = (200, 300))
sickbay = FONT.render("SICK BAY:", True, "WHITE")
sickbayRect = tempText.get_rect(center = (200, 375))

gauge = pg.image.load("gauges.png")
gaugeRect = gauge.get_rect(center = (405, 215))

big_gauge_sweep_angle = 270
medium_gauge_sweep_angle = 200
little_gauge_sweep_angle = 130

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
            
    #draw background       
    screen.blit(background, backgroundRect)
        
    num = randint(1, 6)
    #num = 6 # for debug
    
    # BE debug:
    randtime = randint(10, 12)
    #randtime = randint(40, 80)

    counter = 1
    
    #min values used in random int statement
    value1 = 1
    value2 = 1
    value3 = 1
    max = 5
       
    if num == 2: 
        randtime = 2* randtime * randtime 
        
    while counter < randtime:  

        if num == 1:
            time = randint(1, 6)
            
            #BE adding titles
            sIntLevels = FONT.render("Intelligence Density Tensor", True, "WHITE")
            sIntLevelsRect = sIntLevels.get_rect(topleft = (80, 30))
            screen.blit(sIntLevels, sIntLevelsRect)

            #draw all the rectangles
            pg.draw.circle(screen, (51, 51, 51), (150, 100), 15, 0)  
            pg.draw.circle(screen, (51, 51, 51), (150, 200), 15, 0)
            pg.draw.circle(screen, (51, 51, 51), (150, 300), 15, 0)
            
            #BE adding labels
            sIntLabel1 = FONT.render("Math", True, "GREEN")
            sIntLabel1Rect = tempText.get_rect(topleft = (250, 350))
            screen.blit(sIntLabel1, sIntLabel1Rect)
            sIntLabel2 = FONT.render("Art", True, "GREEN")
            sIntLabel2Rect = tempText.get_rect(topleft = (400, 350))
            screen.blit(sIntLabel2, sIntLabel2Rect)
            sIntLabel3 = FONT.render("Humor", True, "GREEN")
            sIntLabel3Rect = tempText.get_rect(topleft = (550, 350))
            screen.blit(sIntLabel3, sIntLabel3Rect)


            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("ACCEPT", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("ABORT", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("HONK", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("WEIRD", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("RINSE", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("PANIC", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  

            #random number generator to pick progress bar value
            bar1.value = randint(value1, max)
            bar2.value = randint(value2, max)
            bar3.value = randint(value3, max)
        
            #set min for random int generator to current value
            value1 = bar1.value
            value2 = bar2.value
            value3 = bar3.value + 5
        
            #increment max value but never let it get above 100
            max = max + 5
            if max > 100: 
                max = 100
            
            pg.time.wait(1000)
            
            #randomly light up little circles    
            if time == 1:
                pg.draw.circle(screen, (0, 0, 255), (150, 100), 15, 0)
            elif time == 2:
                pg.draw.circle(screen, (0, 255, 0), (150, 200), 15, 0)
            elif time == 3:
                pg.draw.circle(screen, (255, 255, 255), (150, 300), 15, 0)
                    
            #draw text and screens
            if value1 == 100 and value2 == 100 and value3 == 100:
                screen.blit(finished, finished_rect)
                
            bar1.draw(screen)
            bar2.draw(screen)
            bar3.draw(screen)
            
        elif num == 2:
            #random color
            colorr = randint(10, 255)
            colorb = randint(10, 255)
            colorg = randint(10, 255)
            
            #BE adding titles
            sLifeSigns = FONT.render("Life Signs Analysis", True, "WHITE")
            sLifeSignsRect = sLifeSigns.get_rect(topleft = (80, 30))
            screen.blit(sLifeSigns, sLifeSignsRect)


            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("BUG", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("DUCK", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("CAT", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("DOG", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("HUMAN", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("OTHER", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  


            #math
            rawtime = pg.time.get_ticks()
            t = rawtime %600
            
            x = t + 100
            
            y1 = math.sin(t/130) *(-80) +250
            y2 = math.sin(t/37)  *50 +120
            y3 = math.sin(t/22)  *30 +350
            
            #create circles
            pg.draw.circle(screen, (colorr, colorb, colorg), (x, y1), 10)
            pg.draw.circle(screen, (colorg, colorb, colorr), (x, y2), 10)
            pg.draw.circle(screen, (colorb, colorr, colorg), (x, y3), 10)
            
            pg.time.wait(10)
             
            pg.display.update()
            
        elif num == 3:
            # radar view
            
            #BE adding titles
            sMedFood = FONT.render("Closest Mediterrenean Food Loci", True, "WHITE")
            sMedFoodRect = sMedFood.get_rect(topleft = (80, 30))
            screen.blit(sMedFood, sMedFoodRect)

            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("TUR", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("GRK", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("PER", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("CAL", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("LEB", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("KEBOB", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  

            #make it so the screen resets every so often
            reset = randint(0, 7)    
            if reset == 0:
                pg.draw.rect(screen, (0, 0, 0), pg.Rect(80, 30, 600, 360))
            
            #draw the green circles
            pg.draw.circle(screen, (0, 255, 0), (410, 235), 170, 3)
            pg.draw.circle(screen, (0, 255, 0), (410, 235), 130, 2)
            pg.draw.circle(screen, (0, 255, 0), (410, 235), 90, 2)
            pg.draw.circle(screen, (0, 255, 0), (410, 235), 50, 2)
            
            #random locations for the things being detected
            xpos = randint(250, 590)
            ypos = randint(45, 385)
            
            #make the bar rotate
            x = 420 + radar_sweep_length * math.sin(math.radians(radar_sweep_angle))
            y = 215 + radar_sweep_length * math.cos(math.radians(radar_sweep_angle))
            pg.draw.line(screen, (0, 255, 0), (420, 215), (x, y), 3)
            
            radar_sweep_angle += 5
            
            #draw little targets
            pg.draw.circle(screen, (255, 255, 255), (xpos, ypos), 5, 0)
            pg.time.wait(350)
            
            xpos = randint(250, 590)
            ypos = randint(45, 385)
            
            pg.draw.circle(screen, (255, 255, 255), (xpos, ypos), 5, 0)
            pg.time.wait(650)
            
            pg.display.update()
                        
        elif num == 4:
            # map screen

            screen.blit(map, mapRect)
            #BE adding titles
            sBigfootMap = FONT.render("Realtime Global Cryptid Sightings", True, "WHITE")
            sBigfootMapRect = sBigfootMap.get_rect(topleft = (80, 30))
            screen.blit(sBigfootMap, sBigfootMapRect)

            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("Yeti", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("Bigfoot", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("Nessie", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("Chupa", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("Jersey", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("Yowie", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  

            #draw 10 colored dots randomly on map
            count = 0
            while count < 10:
                pg.time.wait(100)
                
                colorr = randint(0, 255)
                colorg = randint(0, 255)
                colorb = randint(0, 255)
                
                xpos = randint(200, 600)
                ypos = randint(100, 350)
                
                pg.draw.circle(screen, (colorr, colorg, colorb), (xpos, ypos), 5, 0)
                
                count += 1
                
            pg.time.wait(100)
            
        elif num == 5:
            # four lines of random stuff status

            pg.draw.rect(screen, (0, 0, 0), pg.Rect(200, 30, 530, 360))
            
            screen.blit(engine, engineRect)
            screen.blit(shields, shieldsRect)
            screen.blit(toilets, toiletsRect)
            screen.blit(cantina, cantinaRect)
            screen.blit(sickbay, sickbayRect)
            
            eWorks = randint(1, 4)
            sWorks = randint(1, 3)
            aWorks = randint(1, 3)
            tWorks = randint(1, 3)
            sbWorks = randint(1, 5)
            
            if eWorks == 1:
                eOnline = FONT.render("ONLINE", True, "WHITE")
                eOnlineRect = tempText.get_rect(center = (400, 75))
                screen.blit(eOnline, eOnlineRect)
            elif eWorks == 2:
                eOnline = FONT.render("MISSING!", True, "RED")
                eOnlineRect = tempText.get_rect(center = (400, 75))
                screen.blit(eOnline, eOnlineRect)
            elif eWorks == 3:
                eOnline = FONT.render("She can't take any more!", True, "YELLOW")
                eOnlineRect = tempText.get_rect(center = (400, 75))
                screen.blit(eOnline, eOnlineRect)
            else:
                eOffline = FONT.render("OFFLINE", True, "RED")
                eOfflineRect = tempText.get_rect(center = (400, 75))
                screen.blit(eOffline, eOfflineRect)
                pg.draw.circle(screen, (255, 0, 0), (630, 75), 10, 0)
            
            if sWorks == 1:
                sOnline = FONT.render("100%", True, "GREEN")
                sOnlineRect = tempText.get_rect(center = (400, 150))
                screen.blit(sOnline, sOnlineRect)
            elif sWorks == 2:
                sOnline = FONT.render("73.147236%", True, "GREEN")
                sOnlineRect = tempText.get_rect(center = (400, 150))
                screen.blit(sOnline, sOnlineRect)  
            else:
                sOffline = FONT.render("0% RUN!", True, "RED")
                sOfflineRect = tempText.get_rect(center = (400, 150))
                screen.blit(sOffline, sOfflineRect)
                pg.draw.circle(screen, (255, 0, 0), (630, 150), 10, 0)
            
            if aWorks == 1:
                aOnline = FONT.render("FLUSHABLE", True, "WHITE")
                aOnlineRect = tempText.get_rect(center = (400, 225))
                screen.blit(aOnline, aOnlineRect)
            elif aWorks == 2:
                aOnline = FONT.render("YELLO? LET IT MELLO", True, "YELLOW")
                aOnlineRect = tempText.get_rect(center = (400, 225))
                screen.blit(aOnline, aOnlineRect)
            else:
                aOffline = FONT.render("BETTER HOLD IT!", True, "RED")
                aOfflineRect = tempText.get_rect(center = (400, 225))
                screen.blit(aOffline, aOfflineRect)
                
            if tWorks == 1:
                tOnline = FONT.render("SERVING", True, "GREEN")
                tOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(tOnline, tOnlineRect)
            elif tWorks == 2:
                tOnline = FONT.render("TAKE A TRAY", True, "BLUE")
                tOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(tOnline, tOnlineRect)
            else:
                tOffline = FONT.render("OUT OF COFFEE!", True, "RED")
                tOfflineRect = tempText.get_rect(center = (400, 300))
                screen.blit(tOffline, tOfflineRect)
                pg.draw.circle(screen, (255, 0, 0), (700, 300), 10, 0)

            if sbWorks == 1:
                sbOnline = FONT.render("SERVING #87", True, "GREEN")
                sbOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(tOnline, tOnlineRect)
            elif sbWorks == 2:
                sbOnline = FONT.render("PAGING DR KIM", True, "BLUE")
                sbOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(sbOnline, sbOnlineRect)
            elif sbWorks == 3:
                sbOnline = FONT.render("STERILIZING", True, "BLUE")
                sbOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(sbOnline, sbOnlineRect)
            elif sbWorks == 4:
                sbOnline = FONT.render("Colonoscopy in progress", True, "YELLOW")
                sbOnlineRect = tempText.get_rect(center = (400, 300))
                screen.blit(sbOnline, sbOnlineRect)  
            else:
                sbOffline = FONT.render("FULL!", True, "RED")
                sbOfflineRect = tempText.get_rect(center = (400, 300))
                screen.blit(sbOffline, sbOfflineRect)
                pg.draw.circle(screen, (255, 0, 0), (700, 300), 10, 0)



                        
            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("Diags", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("Verify", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("Status", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("Details", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("Strange", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("Who?", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  

            pg.time.wait(3000)
            
        else:
            #three pie chart circles
            screen.blit(gauge, gaugeRect) 

            #BE adding titles
            sCivLevels = FONT.render("Civilization Detector", True, "WHITE")
            sCivLevelsRect = sCivLevels.get_rect(topleft = (80, 30))
            screen.blit(sCivLevels, sCivLevelsRect)

            #BE adding labels
            sCivLabel1 = FONT.render("Education", True, "GREEN")
            sCivLabel1Rect = tempText.get_rect(topleft = (134, 197))
            screen.blit(sCivLabel1, sCivLabel1Rect)
            sCivLabel2 = FONT.render("Philosophy", True, "GREEN")
            sCivLabel2Rect = tempText.get_rect(topleft = (134, 365))
            screen.blit(sCivLabel2, sCivLabel2Rect)
            sCivLabel3 = FONT.render("Technology", True, "GREEN")
            sCivLabel3Rect = tempText.get_rect(topleft = (405, 350))
            screen.blit(sCivLabel3, sCivLabel3Rect)

            #BE adding buttonlabels
            sIntButton1 = FONTsmall.render("Stone", True, "BLACK")
            sIntButton1Rect = sIntButton1.get_rect(center = (763, 61))
            screen.blit(sIntButton1, sIntButton1Rect)
            sIntButton2 = FONTsmall.render("Metal", True, "BLACK")
            sIntButton2Rect = sIntButton2.get_rect(center = (763, 121))
            screen.blit(sIntButton2, sIntButton2Rect)
            sIntButton3 = FONTsmall.render("Farming", True, "BLACK")
            sIntButton3Rect = sIntButton3.get_rect(center = (763, 182))
            screen.blit(sIntButton3, sIntButton3Rect)         
            sIntButton4 = FONTsmall.render("Writing", True, "BLACK")
            sIntButton4Rect = sIntButton4.get_rect(center = (763, 242))
            screen.blit(sIntButton4, sIntButton4Rect)  
            sIntButton5 = FONTsmall.render("Steam", True, "BLACK")
            sIntButton5Rect = sIntButton5.get_rect(center = (763, 303))
            screen.blit(sIntButton5, sIntButton5Rect)  
            sIntButton6 = FONTsmall.render("Electricity", True, "BLACK")
            sIntButton6Rect = sIntButton6.get_rect(center = (763, 363))
            screen.blit(sIntButton6, sIntButton6Rect)  

            #make the big bar rotate
            bigX = 500 + 131 * math.sin(math.radians(big_gauge_sweep_angle))
            bigY = 215 + 131 * math.cos(math.radians(big_gauge_sweep_angle))
            pg.draw.line(screen, (255, 255, 255), (500, 215), (bigX, bigY), 3)
            
            #make the medium bar rotate
            mediumX = 215 + 70 * math.sin(math.radians(medium_gauge_sweep_angle))
            mediumY = 145 + 70 * math.cos(math.radians(medium_gauge_sweep_angle))
            pg.draw.line(screen, (255, 255, 255), (220, 135), (mediumX, mediumY), 3)
            
            #make the little bar rotate
            littleX = 215 + 65 * math.sin(math.radians(little_gauge_sweep_angle))
            littleY = 300 + 65 * math.cos(math.radians(little_gauge_sweep_angle))
            pg.draw.line(screen, (255, 255, 255), (220, 300), (littleX, littleY), 3)
            
            big_gauge_sweep_angle -= 2 
            if big_gauge_sweep_angle < 90:
                big_gauge_sweep_angle = 270
            
            medium_gauge_sweep_angle -= 5 
            if medium_gauge_sweep_angle < 90:
                medium_gauge_sweep_angle = 270
                
            little_gauge_sweep_angle -= 4     
            if little_gauge_sweep_angle < 90:
                little_gauge_sweep_angle = 270

            
                
            pg.time.wait(650)
        
        counter += 1              
        pg.display.flip()
        


#pg.quit()