from bs4 import BeautifulSoup


class PresentationConfig:
    slideShows = {}
    def __init__(self, configPath):
        with open(configPath, 'r') as f:
            data = f.read()
        
        # Passing the stored data inside
        # the beautifulsoup parser, storing
        # the returned object 
        Bs_data = BeautifulSoup(data, "xml")
        
        # Finding all instances of slideshow
        slideshows = Bs_data.find_all('slideshow')

        for slideshow in slideshows:
            self.slideShows[slideshow["name"].lower()] = slideshow["folderpath"]

        # print(self.slideShows)
    
    def getFolderPathOfShow(self, showName):
        showName = showName.lower()
        try:
            return self.slideShows[showName]
        except:
            print("Slideshow with name %s does not exist" % showName)
            return None


