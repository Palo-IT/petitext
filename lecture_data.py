# coding: utf-8
import codecs


def lecture_fichier(path = "./définition de famille (simple).txt") :
    data = []
    with codecs.open(path, "r", "utf-8") as f :
        for line in f.readlines():
            if not line.strip().startswith("#") and not "#--" in line.strip() and not line.strip() == "":
                data.append(line.strip("\r\n"))

    f.close()
    return data
    
#print (lecture_fichier())
