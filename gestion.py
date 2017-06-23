# coding: utf-8
from Mot import Mot
from objets_relation import Relation, Objets, Concepts, isconcept
from parametres import *


class Gestionnaire_Relation:
    
    #constructeur
    def __init__(self, ):
        self.liste_relations = []
        self.liste_objets = []
        self.conclusions = []
        self.hypotheses = []
        self.liste_concepts = []
        self.decomposition = {}
        self.objets_d_relations = {}
        self.objets_g_relations = {}
        
    """ 
    cette fonction permet de mettre toutes les tettres d'une phrase en miniscule sauf si c'est un nom propore
    """
    def pre_traitement(self,label, mots, roles):

        for i in range(len(mots)):
            if roles[i] != "NPP":
                m = mots[i].lower()
                mots[i] = m
        label=""
        for mot in mots:
            label+= mot + " "
        label = label[0: len(label)-1]
        return label
        
    def ajouter_relation(self, label, words, roles, ners) :
        
        relation = self.getRelation_verbe(label, words, roles, ners)
        self.liste_relations.append(relation)
        return relation

    
    def concept_existant(self, conc_lemma):
        for c in self.liste_concepts:
            #print(conc_lemma, "cccccc ", c.lemma)
            if c.lemma == conc_lemma:
                return True, c
        return False, None
    
    def ajout_objet(self, indice_ini, indice_fin, objets):
        new, objet = objets.getObjet(indice_ini, indice_fin, self.liste_objets)
        #print("new ", new)
        exist, conc = self.concept_existant(objet.lemma)
        print("exist", exist, "lemm ", objet.lemma)
        if exist == False:
            #print ("the_coonc", objet.lemma)
            conc = Concepts(objet.mot)
            self.liste_concepts.append(conc)
        else:
            print("ihhhhhhhhhhhhhhhhhhhh", len(conc.relations_g))
            objet.relations_g.extend(conc.relations_g)
            objet.relations_d.extend(conc.relations_d)
        """
        else:
            #self, label, mots , is_conc, conc
            new_obj = Objets(objet.label, objet.mots, objet.is_conc, objet.mot)
            objet = new_obj
        """
        if new:
            self.liste_objets.append(objet)
            
        return objet, conc
        
    def ajout_obj_sousrelation(self, objet, new):
        exist, conc = self.concept_existant(objet.lemma)
        if exist == False:
            conc = Concepts(objet.mot)
            self.liste_concepts.append(conc)
        else:
            print("ihhhhhhhhhhhhhhhhhhhh", len(conc.relations_g))
            objet.relations_g.extend(conc.relations_g)
            objet.relations_d.extend(conc.relations_d)
        """
        else:
            #self, label, mots , is_conc, conc
            new_obj = Objets(objet.label, objet.mots, objet.is_conc, objet.mot)
            objet = new_obj     
        """
        if new:
            self.liste_objets.append(objet)
            
        return objet, conc
        
        
    """
    cette fonction sert à convertir une phrase quelconque en une relation
    """
    def getRelation_verbe(self, label, mots, roles, ners):
        
        #lesmots represente la liste des mots sous format d'objets de la classe Mot
        lesmots = []
        for i in range(len(mots)):
            lesmots.append(Mot(mots[i], roles[i], ners[i]))
        #print("iiiiiiiiiiiiiiii",len(lesmots))
        is_conc, conc = isconcept(lesmots)   
        objet = Objets(label, lesmots, False, conc)
        try:
            indice = roles.index("V")
            #print("indice", indice)
            objet_g, conc_g = self.ajout_objet(0, indice, objet)
            #print("ajout g ok")
            try:
                indice_ponc = roles.index("PUNC")
            except:
                indice_ponc = len(roles)-1
            #print("indice_ponc", indice_ponc)
            objet_d, conc_d = self.ajout_objet(indice+1, indice_ponc, objet)
            
            #print("ajout d ok")
            lien = lesmots[indice]
            ##print("oooooooooooooooooooooooooooo", indice_ponc, "len len", len(lesmots))
            ponctuation = lesmots [indice_ponc]
            ind = objet_d.is_relation()
            if ind != -1 :
                objg, objd, lien1, new1, new2 = objet_d.get_relation(ind, self.liste_objets)
                obj_g, c_g = self.ajout_obj_sousrelation(objg, new1)
                obj_d, c_d = self.ajout_obj_sousrelation(objd, new2)
                sous_relation = Relation(obj_g, obj_d, lien1, None , "conj de coordination", None)
            else:
                sous_relation = None
            r = Relation(objet_g, objet_d, lien, ponctuation, "verbe", sous_relation)
            if ind != -1 :    
                if(lien1.lemma == "ou"):
                    self.decomposition[objet_g] = [sous_relation, r]
            if objet_g.is_conc :
                self.traitement_relation_concept(objet_g, r,"relation_g", conc_g)
            if objet_d.is_conc :
                self.traitement_relation_concept(objet_d, r, "relation_d", conc_d)
            
            return r
        except Exception as e:
            raise ValueError("il n'y a pas de verbe!!! ", str(e))
        return
        
        
    def traitement_relation_concept(self, objet, relation, position, concept):
        if position == "relation_g":
            objet.relations_g.append(relation)
            concept.relations_g.append(relation)
        elif position == "relation_d":
            objet.relations_d.append(relation)
            concept.relations_d.append(relation)
            
    def traitement_avoir(self, relation):
        ##print ("rrrr", relation)
        if(relation == None):
            lien = Mot("est partie de", "V", "O")
            return lien
        elif relation.lien.label == "et":
            lien = Mot("sont partie de", "V", "O")
            return lien
        else:
            return None
    
    def traitement_partie_de(self, relation):
        if  ("est partie d" in relation.relationToligne()):
            lien = Mot("a", "V", "O")
            return lien
        elif ("sont partie d" in relation.relationToligne() ) or ("font partie d" in relation.relationToligne()):
            lien = Mot("a", "V", "O")
            return lien
        else:
            return None
    
    
    def traitement_NPropore(self, relation):
        
        return None
    
        
    def concatene_objets (self, objs):
        newMot = objs[0].mots
        vergule = Mot(",", "PUNC", "O")
        newlabel = objs[0].label
        for i in range(1, len(objs)-1):
            newMot.append(vergule)
            newMot.extend(objs[i].mots)
            newlabel += ", " + objs[i].label
        newMot.append(Mot("ou", "CC", "O"))
        newMot.extend(objs[len(objs)-1].mots)
        newlabel += "ou " + objs[len(objs)-1].label
        is_conc, conc = isconcept(newMot)
        
        return Objets(newlabel, newMot, is_conc, conc)
    
    """
    cette fonction sert à traiter la règle:
    Si obj1 est obj2 ou obj3 ET obj2 est obj21 ou obj22 ET obj3 est obj31 ou obj32 Alors
    obj1 est obj21 , obj22, obj31 ou obj32
    """
    def decomposer(self, new_relation):
        if new_relation.sous_relation != None:
            if(new_relation.objet_g in self.decomposition.keys()):
                #print("il est dans les keys")
                relation_pere, pere, objet_frere = self.pere_de(new_relation.objet_g)
                #print("pere "+str(pere)+"\n"+str(relation_pere))
                #print("frere "+str(objet_frere)+"\n")
                if  pere != None:
                    if(objet_frere in self.decomposition.keys()):
                        sous1 = new_relation.sous_relation
                        sous2, relation_frere = self.decomposition[objet_frere]

                        #print (sous2.lien)
                        #print(sous1.lien)
                        newobjet = self.concatene_objets([sous1.objet_g, sous1.objet_d, sous2.objet_g, sous2.objet_d])
                        self.liste_objets.append(newobjet)
                        ind = newobjet.is_relation()
                        objg, objd, lien1, new1, new2 = newobjet.get_relation(ind, self.liste_objets)
                        if new1:
                            self.liste_objets.append(objg)
                        if new2:
                            self.liste_objets.append(objd)
                        sous_relation = Relation(objg, objd, lien1, None , "conj de coordination", None)
                        r = Relation(pere, newobjet, new_relation.lien, new_relation.ponctuation, "verbe", 
                                    sous_relation)
                        #print("ooooooooooooooooooo "+str(relation_pere)+"\n aaaaaaaaaaaaa "+ str(relation_frere) + 
                        #"\n bbbbbbbbbbbbb "+str(new_relation))
                        r.origine.extend([relation_pere, relation_frere, new_relation])
                        return r 
        return None
    
    
    """
    cette fonction permet de detecter si un objet fait partie de la décomposition d'un autre objet et
    de retourner cet objet père  
    """
    def pere_de(self, objet):
        ##print("dkhal pere_de")
        for key, relation in self.decomposition.items():
            ##print("key "+ str(key) + "relation 0" +str(relation[0]) + "relation 1" +str(relation[1]))
            if(objet == relation[0].objet_g):
                return relation[1], key,  relation[0].objet_d
            if (objet == relation[0].objet_d):
                return relation[1], key,  relation[0].objet_g
        return None, None, None
    
    
    
    """
    cette fonction sert à traiter la règle:
    Si obj1 est obj2 ET obj2 est obj3 Alors
    obj1 est obj3
    """
    def chercher_ascendant(self, new_relation):
        #print("dkhal lahna"+ new_relation.relationToligne())
        for relation in self.liste_relations:
            if relation.lien.label in LISTE_ETRE:
                #print("rd", relation.objet_d, "nrd", new_relation.objet_d, "rg", relation.objet_g,"nrg", new_relation.objet_g)
                if relation.objet_d == new_relation.objet_g:
                    r = Relation(relation.objet_g, new_relation.objet_d, relation.lien, relation.ponctuation, "verbe", 
                                new_relation.sous_relation)
                    r.origine.extend([relation,new_relation])
                    return r
                if relation.objet_g == new_relation.objet_d:
                    #print("dkhal lahna")
                    r = Relation(new_relation.objet_g, relation.objet_d, relation.lien, relation.ponctuation, "verbe", 
                                None)
                    r.origine.extend([relation,new_relation])
                    return r
        return None
    
    """
    cette fonction  sert à traiter la règle:
    Si obj1 est obj2 ou obj3   Et   obj2 est obj4    et  obj3 est obj5 Alors
    
    obj1 est obj4 ou obj5
    """
    def nouvelle_decomposition (self, new_relation):
        relation_pere, pere, objet_frere = self.pere_de(new_relation.objet_g)
        if pere!= None:
            for relation in self.liste_relations:
                if (relation.lien.label in LISTE_ETRE) and (relation.objet_g == objet_frere) and (relation.sous_relation == None):
                    new_obj = self.concatene_objets([relation.objet_d, new_relation.objet_d])
                    self.liste_objets.append(new_obj)
                    lien1 = Mot("ou", "CC", "O")
                    sous_relation = Relation(relation.objet_d, new_relation.objet_d, lien1, None , "conj de coordination", None)
                    r = Relation(pere, new_obj, relation.lien, relation.ponctuation, "verbe", sous_relation)
                    r.origine.extend([relation_pere, relation, new_relation])
                    return r
        return None
                    
            
            
        
        
        
        
        
    """
    cette fonction sert à traiter la règle:
    Si obj1 est obj2 Et obj3 est obj2 Alors
    obj1 et Obj3 sont obj2
    """
    def union(self, new_relation):
        for relation in self.liste_relations:
            if relation.lien.label in ['est']:
                if(relation != new_relation):
                    if relation.objet_d == new_relation.objet_d:
                        newobj = relation.objet_g.union_objets(new_relation.objet_g)
                        newlien = Mot("sont", "V", "O")
                        r = Relation(newobj, new_relation.objet_d, newlien, relation.ponctuation, "verbe", 
                                    new_relation.sous_relation)
                        r.origine.extend([relation,new_relation])
                        return r
                else:
                    return None
        return None
    
    """
    cette fonction sert à traiter la règle:
    Si obj1 est obj2 ou obj3  ET  obj3 est obj2 Alors
    obj3 est probablement Obj1 
    """
    def simple_hypothese(self, relation):
        relation_pere, pere, objet_frere = self.pere_de(relation.objet_d)
        ##print("ooooooooooooooooooooooo",str(pere))
        if pere != None:
            lien = Mot("est probablement", "V", "O")
            r = Relation(relation.objet_g, pere, lien, relation.ponctuation, "verbe", None)
            r.origine.extend([relation_pere, relation])
            return r
        else:
            return None
    
    
    """
    cette fonction sert à traiter la règle:
    Si obj1 est obj2 ou obj3  ET  obj4 est obj5 ou obj2 Alors
    obj4 est probablement Obj1 
    """
    def complex_hypothese(self, relation):
        sous_relation, r = self.decomposition[relation.objet_g]
        relation_pere_d, pere_d, objet_frere_d = self.pere_de(sous_relation.objet_d)
        if (pere_d != None) and not(pere_d == relation.objet_g):
            lien = Mot("est probablement", "V", "O")
            res = Relation(relation.objet_g, pere_d, lien, relation.ponctuation, "verbe", None)
            res.origine.extend([relation_pere_d, relation])
            return res
        relation_pere_g, pere_g, objet_frere_g = self.pere_de(sous_relation.objet_g)
        if (pere_g != None) and not(pere_g == relation.objet_g):
            lien = Mot("est probablement", "V", "O")
            res = Relation(relation.objet_g, pere_g, lien, relation.ponctuation, "verbe", None)
            res.origine.extend([relation_pere_g, relation])
            return res
        return None
        
        
        
    def getHypotheses(self, relation):
        nouvelles_hypotheses = []
        new = False
        if(not relation.objet_d.is_adj()):
            if relation.lien.label in LISTE_ETRE:   #il faut que ça soit la liste du verbe etre
                if(relation.sous_relation == None):
                    r = self.simple_hypothese(relation)
                    ##print(r.relationToligne())
                    if r!=None:
                        self.hypotheses.append(r)
                        nouvelles_hypotheses.append(r)
                        new = True
                else:
                    r = self.complex_hypothese(relation)
                    if r!=None :
                        ##print(str(r.relationToligne()))
                        self.hypotheses.append(r)
                        nouvelles_hypotheses.append(r)
                        new = True
        while new:
            r_new = self.sous_hypotheses(r)
            if r_new == None:
                new = False
            else:
                r = r_new
                self.hypotheses.append(r)
                nouvelles_hypotheses.append(r)   
        return nouvelles_hypotheses
    
    
    
    def contient (self, obj_g, obj_d, lien):
        for relation in self.hypotheses:
            if(relation.objet_g == obj_g) and (relation.objet_d == obj_d) and (relation.lien.label == lien.label):
                return True
        return False
    """
    cette fonction genere les hypotheses respectant la regle
    Si obj1 est obj2 Ou obj3 ET obj2 est problablement obj4 Alors
    obj1 est probablement obj4.
    """
    
    def sous_hypotheses(self, new_relation):
        relation_pere, pere, objet_frere = self.pere_de(new_relation.objet_g)
        if pere != None:
            lien = Mot("est probablement", "V", "O")
            if not self.contient(pere, new_relation.objet_d, lien):
                r = Relation(pere, new_relation.objet_d, lien, new_relation.ponctuation, "verbe", None)
                r.origine.extend([relation_pere, new_relation])
                ##print(str(r.relationToligne()))
                self.hypotheses.append(r)
                return r
            else:
                return None
        else:
            return None
        #return self.hypotheses
                    
    def ajout_relation_concept(self, relation):
        if relation.objet_g.is_conc:
            relation.objet_g.relations_g.append(relation)
        if relation.objet_d.is_conc:
            relation.objet_d.relations_d.append(relation)
    def inverser_objet_relation(self, relation, conclusion):
        ponct = Mot(".", "PUNC", "O")
        origine = relation
        if conclusion.label in ["ont", "a"] :
           
            r = Relation(relation.objet_d.objet_dTo_g1(), relation.objet_g, conclusion, ponct, conclusion.label, None)
        else:
            r = Relation(relation.objet_d, relation.objet_g, conclusion, ponct, conclusion.label, None)
        
        r.origine.append(origine)
        self.ajout_relation_concept(r)
        self.conclusions.append(r)
        self.liste_relations.append(r)
        return r
    
    def transfert_relation_concept_objet(self, objet):
        conclusion_heritage = []
        for relation in objet.relations_g:
            conclusion_heritage.append(Relation(objet, relation.objet_d, relation.lien, relation.ponctuation, relation.label,  
                                                relation.sous_relation))
        return conclusion_heritage
            
    def getConclusions(self, relation):
        nouvelles_conclusion = []
        new = False
        if not(relation.objet_g.is_conc):
            print("cest pas un conc", relation.objet_g.lemma, "aaaaaaaaaaaaa", len(relation.objet_g.relations_g))
            conc_herit = self.transfert_relation_concept_objet(relation.objet_g)
            for conc in conc_herit:
                self.conclusions.append(conc)
                self.liste_relations.append(conc)
                nouvelles_conclusion.append(conc)
                new = True
                
        if(not relation.objet_d.is_adj()):
            if relation.lien.label in LISTE_AVOIR:   
                ##print ("traitement avoir")
                conclusion = self.traitement_avoir(relation.sous_relation)
                if conclusion != None:
                    ##print("coooooooonnnnnnn", str(conc))
                    ##print(str(relation.objet_d.objet_dTo_g()))
                    r = self.inverser_objet_relation(relation, conclusion)
                    nouvelles_conclusion.append(r)
                    new = True

            elif relation.lien.label in LISTE_ETRE:
                #traitement partie de
                conclusion = self.traitement_partie_de(relation)
                if conclusion!=None:
                    r = self.inverser_objet_relation(relation, conclusion)
                    nouvelles_conclusion.append(r)
                    new = True
                    
                # recherche ascendants
                r = self.chercher_ascendant (relation)
                if r != None:
                    ##print (r.relationToligne())
                    self.conclusions.append(r)
                    self.liste_relations.append(r)
                    nouvelles_conclusion.append(r)
                    new = True
                    #else:
                    ##print ("pas d'ascendants")
                r = self.union(relation)
                if r!=None:
                    ##print (r.relationToligne())
                    ##print (str(r))
                    self.conclusions.append(r)
                    self.liste_relations.append(r)
                    nouvelles_conclusion.append(r)
                    new = True
                #else:
                    ##print ("pas d'unions")
                r = self.nouvelle_decomposition(relation)
                if r!=None:
                    ##print (r.relationToligne())
                    ##print (str(r))
                    self.conclusions.append(r)
                    self.liste_relations.append(r)
                    nouvelles_conclusion.append(r)
                    new = True
                #else:
                    ##print ("pas de nouvelle decomposition")
                r = self.decomposer(relation)
                if r!=None:
                    ##print (r.relationToligne())
                    ##print (str(r))
                    self.conclusions.append(r)
                    self.liste_relations.append(r)
                    nouvelles_conclusion.append(r)
                    new = True
                #else:
                    ##print ("pas de doomposition multiple")
            else:
                print ("je ne connais pas ce verbe !!!")
        else:
            print("contient un adjectif")
        return nouvelles_conclusion
                    
             
if __name__ == "__main__" :
    
    #chaque personne est un homme ou une femme
    
    """
    ners = ['O', 'O', 'O', 'O', 'O', 'O','O', 'O', 'O', 'O', 'O']
    roles = ['DET','NC', 'CC', 'DET','NC','V','N','P','DET', 'NC',  'PUNC']
    words = ['Des', 'hommes', 'et', 'des','femmes','sont', 'partie', 'de', 'chaque', 'societe', '.']
    label = "Des hommes et des femmes sont partie de chaque société."
    gestion = Gestionnaire_Relation()
    label = gestion.pre_traitement(label, words, roles)
    #print("ph1")
    r1 = gestion.ajouter_relation(label, words, roles, ners)   
    print(r1.relationToligne())
    r3 = gestion.getConclusions(r1)
    print(r3[0].relationToligne())
    print(len(r3[0].objet_d.relations_d))
    """
    
    
    
    
    
    
    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Chaque', 'personne', 'est', 'un', 'homme', 'ou', 'une', 'femme', '.']
    label = "Chaque personne est un homme ou une femme."
    gestion = Gestionnaire_Relation()
    label = gestion.pre_traitement(label, words, roles)
    r1 = gestion.ajouter_relation(label, words, roles, ners)  
    print(r1.objet_g.is_conc, "conc ", r1.objet_g.clabel, len(r1.objet_g.relations_g))
    print(r1.relationToligne())
    r3 = gestion.getConclusions(r1)
    
    ners = ['PERSON', 'O', 'O', 'O']
    roles = ['NPP', 'V', 'ADJ', 'PUNC']
    words = ['Patrick', 'est', 'intelligent', '.']
    label = "Patrick est intelligent."
    label = gestion.pre_traitement(label, words, roles)
    r1 = gestion.ajouter_relation(label, words, roles, ners)   
    print(r1.relationToligne())
    print(r1.objet_g.is_conc, "conc ", r1.objet_g.clabel, len(r1.objet_g.relations_g))
    r3 = gestion.getConclusions(r1)
    for r in r3:
        print(r.relationToligne())
    
    """
    ners = ['O', 'O', 'O', 'O', 'O', 'O','O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'NC', 'DET','CC', 'DET','NC', 'PUNC']
    words = ['Chaque', 'societe', 'a', 'des', 'enfants', 'et', 'des','parents', '.']
    label = "Chaque societe a des enfants et des parents."
    label = gestion.pre_traitement(label, words, roles)
    #print("ph1")
    r2 = gestion.ajouter_relation(label, words, roles, ners)   
    print(r1.objet_g == r2.objet_g)
    print(len(r2.objet_g.relations_g), "\n elem 0",r2.objet_g.relations_g[0].relationToligne())
    #print(len(gestion.decomposition))
    #print("conc1")
   
    gestion.getConclusions(r)


    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Chaque', 'personne', 'est', 'un', 'homme', 'ou', 'une', 'femme', '.']
    label = "Chaque personne est un homme ou une femme."
    gestion = Gestionnaire_Relation()
    label = gestion.pre_traitement(label, words)
    r = gestion.ajouter_relation(label, words, roles, ners)   
    #print("okokokokokokok", len(gestion.decomposition))
   
    #gestion.getConclusions()
    #print("hyp1")
    gestion.getHypotheses(r)
    
    ners = ['O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'PUNC']
    words = [u'Chaque', u'père', u'est', u'un', u'homme', '.']
    label = u"Chaque père est un homme."
    label = gestion.pre_traitement(label, words)
    r = gestion.ajouter_relation(label, words, roles, ners)   
    #print(len(gestion.decomposition))
    ##print("conc1")
    #gestion.getConclusions()
    #print("hyp2")
    #print("okokokokokokok", len(gestion.decomposition))
    gestion.getHypotheses(r)
    
 
    ners = ['O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'PUNC']
    words = ['Un', 'homme', 'est', 'une', 'personne', '.']
    label = "Un homme est une personne."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc3")
    gestion.getConclusions()
    ners = ['O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'PUNC']
    words = ['Chaque', 'frère', 'est', 'un', 'homme', '.']
    label = "Chaque père est un homme."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc4")
    gestion.getConclusions()
    ners = ['O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'ADJ', 'PUNC']
    words = ['Chaque', 'femme', 'est', 'féminine', '.']
    label = "Chaque femme est féminine."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc5")
    gestion.getConclusions()
    #print(len(gestion.decomposition))
    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Chaque', 'personne', 'est', 'un', 'homme', 'ou', 'une', 'femme', '.']
    label = "Chaque personne est un homme ou une femme."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc6")
    gestion.getConclusions()
    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Chaque', 'enfant', 'est', 'un', 'fils', 'ou', 'une', 'fille', '.']
    label = "Chaque enfant est un fils ou une fille."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc7")
    gestion.getConclusions()
    #print(len(gestion.decomposition))
    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'N', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Un', 'fils', 'est', 'un', 'garçon', 'ou', 'un', 'homme', '.']
    label = "Un fils est un garçon ou un homme."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc8")
    gestion.getConclusions()
    #print(len(gestion.decomposition))
    ners = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    roles = ['DET', 'NC', 'V', 'DET', 'NC', 'CC', 'DET', 'NC', 'PUNC']
    words = ['Une', 'fille', 'est', 'une', 'jeune-fille', 'ou', 'une', 'femme', '.']
    label = "Une fille est une jeune-fille ou une femme."
    label = gestion.pre_traitement(label, words)
    gestion.ajouter_relation(label, words, roles, ners)
    #print("conc8")
    gestion.getConclusions()
    #print(len(gestion.decomposition))
 
    """
                    
                    
                
                
    
    
    
