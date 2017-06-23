# coding: utf-8
from Mot import Mot

class Concepts:
    
    def __init__(self, mot):
            ##print("mot not null")
            self.clabel = mot.label
            self.lemma = mot.lemma
            ##print("lemme ", self.lemma)
            self.mot = mot
            self.relations_g = [] #liste des relations dans lesquelles nous avons le concept en objet_g
            self.relations_d = [] #liste des relations dans lesquelles nous avons le concept en objet_d
            self.decompositions = []
    
    
    
        
class Objets(Concepts) :
    
    def __init__(self, label, mots , is_conc, conc):
        Concepts.__init__(self, conc)
        ##print("ahhhhhhhhhhhhhhh", self.clabel)
        self.is_conc = is_conc
        self.label = label
        self.mots = mots
        return
        
    
    """
    methode qui retourne l'indice du 'cc' lorsqu'il existe
    """    
    def is_relation(self):
        indice = -1
        i = 0
        for mot in self.mots:
            if "cc" in mot.role:
                indice = i
                break;
            elif "CC" in mot.role:
                indice = i
                break;
            i += 1
        return indice
                
    """
    methode qui convertie un objet compose en Relation
    """    
        
    def get_relation(self, indice, les_objets):
        
        new1, obj1 = self.getObjet (0, indice, les_objets)
        new2, obj2 = self.getObjet (indice + 1, len (self.mots), les_objets)
        lien = self.mots[indice]
        return obj1, obj2, lien, new1, new2  
    
    def contains_adj(self,):
        for mot in self.mots:
            if(mot.role == "ADJ"):
                return True
        return False
    
    def is_adj(self,):
        if len(self.mots) == 1:
            return self.mots[0].role == "ADJ"
        return False
    def appartient(self, o_label, les_objets):
        for obj in les_objets:
            label = obj.label
            #print("oooolabel", o_label.replace(" ", ""), "label", label.replace(" ",""))
            if o_label.replace(" ", "") == label.replace(" ",""):
                
                return True, obj
        return False, None
            
    def union_objets(self, objet2):
        newlabel= self.label + " et " + objet2.label
        newMot = self.mots
        newMot.append(Mot("et", "DET", "O"))
        newMot.extend(objet2.mots)
        is_conc,conc = isconcept(newMot)
        return Objets(newlabel, newMot, is_conc, conc)
    
    #les_objets represente la liste des objets deja traités
    def getObjet(self, indice_ini, indice_fin, les_objets): 
        #print("dkhal get objet")
        o_mot = self.mots[indice_ini : indice_fin]
        o_label = ""
        for mot in o_mot:
            if mot.label != ".":
                o_label += mot.label + " "
            else:
                o_label += mot.label
        #print("olabel", o_label)
        app, obj = self.appartient(o_label, les_objets)
        #print("aaaaaaaaaaaa",app, "obj ", str(obj))
        if app :  
            return not app, obj
        else:
            #print("getobjettttttttttttttttt ", o_mot[0])
            is_conc, conc = isconcept(o_mot)
            #print ("is_conc", conc)
             
            ##print("getobjettttttttttttttttt ",is_conc)
            return not app, Objets(o_label, o_mot, is_conc, conc)
    
    """
    cette methode permet de mettre un objet qui était à droite de la relation en objet gauche
    en mettant la première lettre en majuscule.
    """
    """
    def objet_dTo_g(self):
        premier_mot = self.mots[0].label
        premier_mot = premier_mot[0].upper() + premier_mot[1:]
        self.mots[0].label = premier_mot
        self.label = self.label[0].upper() + self.label[1:]
        return self
    
    
    def objet_gTo_d(self):
        premier_mot = self.mots[0].label
        premier_mot = premier_mot[0].lower() + premier_mot[1:]
        self.mots[0].label = premier_mot
        self.label = self.label[0].lower() + self.label[1:]
        return self
    """

    
    def objet_dTo_g1(self):
        new_mots = self.mots[2:]
        is_conc, conc = isconcept(new_mots)
        label = ""
        for mot in new_mots:
            label += mot.label +" "
        return Objets(label, new_mots, is_conc, conc )
        
    
    def __str__(self):
        
        res = "label " + self.label +" \nmots["
        for mot in self.mots:
            res += str(mot) + " , "
        res += "]"
        return res;
    
    def affichage(self): 
        
        self.show_label()
        self.show_mots()

        
    def show_label(self):
        print(self.label)
        
    def show_mots(self):
        for mot in self.mots:
            print(str(mot)) 
   

"""
Cette classe represente une relation est sous la forme objet_g ----> lien -----> objet_d
elle est definie par deux objets de la classe Objets objet_g et objet_d
et d'un lien qui est un Mot
"""
class Relation:
    
    #constructeur
    def __init__(self, objet_g, objet_d, lien, ponctuation, label, sous_relation):
        self.objet_g = objet_g
        self.objet_d = objet_d
        self.lien = lien
        self.label = label
        self.sous_relation = sous_relation
        self.ponctuation = ponctuation
        #self.les_objets = []
        self.origine = []
        
    def __str__(self):
        res = self.label + "\n" + str(self.objet_g) + "\n--->\n" + str(self.lien) + "\n--->\n" + str(self.objet_d)
        res += "\nsous-relation\n\t" + str(self.sous_relation) + "\norigine\n\t"
        for o in self.origine:
            res += str(o.relationToligne()) + "\t"
        return res
    
    
    
    
    """
    
    methode qui retourne True si la relation est simple c-a-d contient un seul un mot verbe un mot 
    sinon elle retourne False
    
    """
    def relationToligne(self):
        return self.objet_g.label + self.lien.label +" "+ self.objet_d.label + self.ponctuation.label
    
    def isSimple(self):
        #print("hhhhhhh")
        return (self.objet_g.is_relation() == -1) and (self.objet_d.is_relation() == -1)
            
    """
    cette fonction sert à convertir une phrase quelconque en une relation
    """
def getRelation_verbe(label, mots, roles, ners, les_objets):
    #lesmots represente la liste des mots sous format d'objets de la classe Mot
    lesmots = []
    for i in range(len(mots)):
        lesmots.append(Mot(mots[i], roles[i], ners[i]))
    is_conc, conc = isconcept(lesmots)
    #print("premier isconcept")
    objet = Objets(label, lesmots, is_conc, conc)
    try:
        indice = roles.index("V")
        new, objet_g = objet.getObjet(0, indice, les_objets)
        #print("OBJET G")
        try:
            indice_ponc = roles.index("PUNC")
        except:
            indice_ponc = len(roles)-1
        if new:
            les_objets.append(objet_g)
        new, objet_d = objet.getObjet(indice+1, indice_ponc,  les_objets)
        if new:
            les_objets.append(objet_g)
        lien = lesmots[indice]
        ponctuation = lesmots [indice_ponc]
        ind = objet_d.is_relation()
        if ind != -1 :
            objg, objd, lien1, new1, new2 = objet_d.get_relation(ind, les_objets)
            if new1:
                les_objets.append(objg)
            if new2:
                les_objets.append(objd)
            sous_relation = Relation(objg, objd, lien1, None , "conj de coordination", None)
        else:
            sous_relation = None
        return les_objets, Relation(objet_g, objet_d, lien, ponctuation, "verbe", sous_relation)
    except Exception as e:
        message = str(e)
        ##print(message)
        raise ValueError("il n'y a pas de verbe!!! " + message) 
def isconcept(mots):
    i = 0
    le_conc = None
    if len(mots) == 1:
        #print("len 1")
        if mots[0].role == "NPP":
            if mots[0].ner == "PERSON":
                #print("dans person")
                le_conc = Mot("personne", "NC", "O")
                #print ("leconc ", le_conc.clabel)
            elif mots[0].ner == "LOCATION":
                le_conc = Mot("lieu", "NC", "O")
            else:
                le_conc = Mot("inconnu", "null", "O")
            return False, le_conc
        elif mots[0].role == "DET":
            return False, None
        else:
            return True, mots[0]
    else:
        for mot in mots: # traitement du cas où nous avons un  nom commun dans la liste des mots
            if mot.role == "NC" or mot.role == "N":
                le_conc = mot
                label = ""
                for lab in range(0, i):
                    label += mots[lab].label + " "
                if label in ['tout ', 'chaque ', 'toute ', 'tous les ', "toutes les ", "tous ", "toutes "]:
                    return True, le_conc
                return False, le_conc
            i +=1
        for mot in mots: #traitement du cas où nous n'avons pas de nom commun mais un adjectif
            if mot.role == "ADJ":
                le_conc = mot
                return False , le_conc  
    return False, le_conc

if __name__ == "__main__" :
        #chaque personne est un homme ou une femme

    ners = ['PERSON', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['NPP', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Patrick', 'est', 'un', 'homme', 'ou', 'une', 'femme', '.']
    label = "Patrick est un homme ou une femme."
    les_objets = []
    liste_objet, r = getRelation_verbe(label, words, roles, ners, les_objets)
    print(str(r.objet_g.is_conc), "son concept", r.objet_g.clabel)
    ners = ['PERSON', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['NPP', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Patrick', 'est', 'un', 'homme', 'ou', 'une', 'femme', '.']
    label = "Patrick est un homme ou une femme."
    liste_objet, r = getRelation_verbe(label, words, roles, ners, les_objets)
    print(str(r.objet_g.is_conc), "son concept", r.objet_g.clabel)
    #print(str(r.relationToligne()))
    

    """
    
    cette classe 
    
    """
