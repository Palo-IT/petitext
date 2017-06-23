import codecs

def getHtml(path = "./before_body.html") :
    html= ""
    with codecs.open(path, "r", "utf-8") as f :
        for line in f.readlines():
            html += "\n" + line

    f.close()
    return html
