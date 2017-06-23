import time, codecs
from MonCoreNLP import lecture_fichier
from MonCoreNLP import get_enhancedPlusPlusDependencies
from gestion import Gestionnaire_Relation
from flask import Flask, redirect, url_for, request
from include_html import getHtml


# declaration de l'application
app = Flask(__name__)

# tableau pour stocker les nouvelles conclusions
tmp = []

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name



@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        file_name = request.form['file_name']
        new_line = request.form['new_line']
        return redirect(url_for('generer_tous_arbres',filePath = file_name, newLine=new_line))
    else:
        file_name = request.args.get('file_name')
        new_line = request.args.get('new_line')
        return redirect(url_for('generer_tous_arbres',filePath = file_name, newLine=new_line))



@app.route('/result')
def generer_tous_arbres ():

    path = request.args['filePath']
    data = request.args['newLine']
    entete = {
    u"./definition de famille (simple).txt" : u"la définition simple de la famille",
    u"./univers des objets.txt" : u"l'univers des objets abstraits",
    u"./Connaissance des organismes.txt" : u"l'univers de la connaissance des organismes"
    }
    enhanced = {}
    arbre = {}
    ner = []
    roles = []
    words = []
    datum = ""
    message = ""



    message += getHtml("./until_body.html")
    donnees = lecture_fichier(path)


    if (data == ""):
        del tmp[:]
        message += "<body onload= 'showNextRow(); window.scrollTo(0,document.body.scrollHeight);' >"
    else:
        tmp.append(data)
        donnees.extend(tmp)
        message += "<body onload= 'window.scrollTo(0,document.body.scrollHeight);' >"


    message += getHtml("./head_of_body.html")
    gestion = Gestionnaire_Relation()
    message += "<div style='margin-left: 199px;'><h2>Raisonnement sur "
    message += entete[path]
    message += "</h2>"
    #message += "<div id='myProgress'><div id='myBar'>10%</div></div></td>"
    message += "<br></br><table>"

    for datum in donnees:
        message += "<tr>"
        message +=  u"<td><button class='btn btn-info' > Fait </button>&nbsp;&nbsp;&nbsp;"
        message += datum
        message += "</td>"

        print("# Fait ##############" + datum + "###############")
        enhanced, ner, roles, words = get_enhancedPlusPlusDependencies(datum)

        label = gestion.pre_traitement(datum, words,roles)
        r = gestion.ajouter_relation(label, words, roles, ner)

        messageConcHyp = ""
        conc = []
        hyp = []
        messageConcHyp = getConclusionsHypothese (conc, hyp, gestion, r)

        message += messageConcHyp

        datum = ""


        print("###############################################################")

    message += "</table><br></br>"
    message += "<input type=button class='btn btn-inverse' value='Avancer sur le raisonnement' id='onemore' style='width:260px;height:70px'/>"
    message += "<br></br>"
    message += "<form action = 'http://127.0.0.1:5000/login' method = 'POST'>"
    message += "      <input type='HIDDEN' name = 'file_name' value = '" + path + "' />"
    message += "      <input type='text' name = 'new_line' value='' placeholder='Ajouter ici un nouveau fait' style='width:250px;margin-bottom: 0px;'/>"
    message += "      <input class='btn btn-info' type='submit' value='Ajouter et raisonner' />"
    message += "</form><br></br>"

    message += "</div></body></html>"
    return message



def getConclusionsHypothese (conc, hyp, gestion, r):
    message = ""
    concHtml = getConclusions(conc, gestion, r)
    message = concHtml
    hypHtml = getHypotheses(hyp, gestion, r)
    message += hypHtml

    return message


def getConclusions (conc, gestion, r):

    conc = gestion.getConclusions(r)
    message = "<table>"
    for c in conc:
        message += "<tr>"
        message += "<td>"
        message += u"<button class='btn btn-primary'  >&#x2794;&nbsp;Conclusion(s) générée(s) à ce moment </button>&nbsp;&nbsp;&nbsp;"
        message += c.relationToligne()
        message += "</td>"

    message += "</table>"
    return message


def getHypotheses (hyp, gestion, r):

    hyp = gestion.getHypotheses(r)
    message = "<table>"
    for h in hyp:
        message += "<tr>"
        message += "<td>"
        message += u"<button class='btn btn-warning' >&#x2794;&nbsp;Hypothèse(s) générée(s) à ce moment </button>&nbsp;&nbsp;&nbsp;"
        message += h.relationToligne()
        message += "</td>"

    message += "</table>"
    return message




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
