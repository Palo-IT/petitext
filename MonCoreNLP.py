# coding: utf-8
"""

serveur dans (home simph)  ./nltk-data/stanford-corenlp-full-2016-10-31/

lancement

java -mx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9009 -timeout  15000

warning :

il a besoin de 6G 5g de  ram pour traiter 2 langues comme en et fr
- mettre dans la directory les models java pour chaque langue....voir le site stanford 
coreNLP server.


"""



import time
import requests, logging, sys
import pprint, json, time
import codecs

root = logging.getLogger('Root')
root.setLevel(logging.WARNING)

lhandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] : %(message)s',
                '%Y-%m-%d %H:%M:%S')
lhandler.setFormatter(formatter)
root.addHandler(lhandler)

class CoreNLP:
    root.debug('Object instantiating..')
    annotator_full_list = ["tokenize", "cleanxml", "ssplit", "pos", 
    "lemma", "ner", "regexner", "truecase", "parse", "depparse", "dcoref", 
    "relation", "natlog", "quote", "sentiment"]
    language_full_list = ['en', 'fr', 'ar', 'zh', 'de', 'es']
    url = 'http://127.0.0.1:9009'
    out_format = 'json'

    def __init__(self, url=url,
                 language = "en",
                 annotator_list=annotator_full_list,
                isPrint = False,
                ):
        
        if isPrint :
            root.setLevel(logging.DEBUG)
            
        
        assert url.upper().startswith('HTTP'),             'url string should be prefixed with http'
        
        if 'SENTIMENT' in map(str.upper, annotator_list):
            root.warning('You are using "Sentiment" annotator which is'                'not supported by Old version of CoreNLP')
        
        
        if url.endswith('/'):
            self.url = url[:-1]
        else:
            self.url = url

        assert isinstance(annotator_list, list),             'annotators can be passed only as a python list'
        if len(annotator_list) == 14:
            root.info('Using all the annotators, It might take a while')
        
        self.annotator_list = annotator_list
        self.language = language
        self.isPrint = isPrint
        common=set(self.annotator_list).intersection(self.annotator_full_list)
        not_suprtd_elem = set(self.annotator_list) - common
        assertion_error = 'annotator not supported: ' + str(not_suprtd_elem)
        assert not not_suprtd_elem, assertion_error
        
        common = set([self.language]).intersection(self.language_full_list)
        not_existing_language = set ( [self.language ]) - common
        assertion_error = 'language not supported: ' + str(not_existing_language)
        assert not not_existing_language, assertion_error
        
        


    @staticmethod
    def server_connection(current_url, data,):
        root.debug('server connection: ' + current_url)
        # modif PL
        root.debug ("data :"+ data )
        #print (type(data))
        assert isinstance(data, unicode) and data, 'Enter valid string input'
        try:
            data_utf = data.encode('utf-8')
        except:
            print (repr(data))
            raise
        try:
            server_out = requests.post(current_url, 
                                        data_utf, 
                                        headers={'Connection': 'close'})
        except requests.exceptions.ConnectionError:
            root.error('Connection Error, check you have server running')
            raise Exception('Check your CoreNLP Server status \n'
                'if not sure, Check the pywrap doc for Server instantiation')
        return server_out
    
   
    def url_calc(self, serializer=''):
        s_string = '/?properties={"annotators": "'
        anot_string = ','.join(self.annotator_list)
        m_string = '", "outputFormat": "' + self.out_format
        f_string = '", "serializer": "' + serializer + '"}&pipelineLanguage='+self.language
        return self.url + s_string + anot_string + m_string + f_string


    def basic(self, data, out_format='json', serializer=''):
        self.out_format = out_format
        format_list = ['JSON', 'XML', 'TEXT', 'SERIALIZED']
        assert out_format.upper() in format_list,             'output format not supported, check stanford doc'
        
        if out_format.upper() == 'SERIALIZED' and not serializer:
            root.info(
                'Default Serializer is using - ' + 
                'edu.stanford.nlp.pipeline.ProtobufAnnotationSerializer')
            serializer = ('edu.stanford.nlp.pipeline.'
                'ProtobufAnnotationSerializer')
                
        current_url = self.url_calc(serializer)
        
        
        return self.server_connection(current_url, data,)

    @staticmethod
    def tokensregex(data, pattern='', custom_filter=''):
        root.info('TokenRegex started')
        return CoreNLP.regex('/tokensregex', data, pattern, custom_filter)

    @staticmethod
    def semgrex(data, pattern='', custom_filter=''):
        root.info('SemRegex started')
        return CoreNLP.regex('/semgrex', data, pattern, custom_filter)

    @staticmethod
    def tregex(data, pattern='', custom_filter=''):
        root.info('Tregex started')
        return CoreNLP.regex('/tregex', data, pattern, custom_filter)

    @classmethod
    def regex(cls, endpoint, data, pattern, custom_filter):
        url_string = '/?pattern=' + str(pattern) +'&filter=' + custom_filter 
        current_url = cls.url + endpoint + url_string
        root.info('Returning the data requested')
        return cls.server_connection(current_url, data)

    @staticmethod
    def process_sentences(sentences):
        assert isinstance(sentences, list), 'it should be a list'
        index = 0
        new_index = 0
        token_dict = {
        'index':[],
        'truecaseText':[],
        'ner':[],
        'before':[],
        'originalText':[],
        'characterOffsetBegin':[],
        'lemma':[],
        'truecase':[],
        'pos':[],
        'characterOffsetEnd':[],
        'speaker':[],
        'word':[],
        'after':[],
        'normalizedNER':[]
        }
        for sentence in sentences:
            index = new_index
            tokens = sentence['tokens']
            for val in tokens:

                #workaround to handle length inconsistancie with normalizedNER, rethink the logic
                if 'ner' in val.keys() and 'normalizedNER' not in val.keys():
                    token_dict['normalizedNER'].append(0)
                    
                for key, val in val.items():
                    if key == 'index':
                        new_index = index + int(val)
                        token_dict[key].append(str(new_index))
                    else:
                        try:
                            token_dict[key].append(val)
                        except KeyError:
                            token_dict[key] = [val]
                            root.info('New key added: ' + key)
        
                         
        return [token_dict, sentences]


    def arrange(self, data):
        root.info('Executing custom function')
        assert isinstance(data, unicode) and data, 'Enter valid string input'
        if 'lemma' not in self.annotator_list:
            self.annotator_list.append('lemma')
        
        current_url = self.url_calc()
        r = self.server_connection(current_url, data)
        try:
            r = r.json()
            rs = r['sentences']
        except ValueError:
            root.error('Value Error: '+r.text+', Check special chars in input')
            rs = []
        return self.process_sentences(rs)
    
listePOS = """

        CC Coordinating conjunction
        CD Cardinal number
        DT Determiner
        EX Existential there
        FW Foreign word
        IN Preposition or subordinating conjunction
        JJ Adjective
        JJR Adjective, comparative
        JJS Adjective, superlative
        LS List item marker
        MD Modal
        NN Noun, singular or mass
        NNS Noun, plural
        NNP Proper noun, singular
        NNPS Proper noun, plural
        PDT Predeterminer
        POS Possessive ending
        PRP Personal pronoun
        PRP$ Possessive pronoun
        RB Adverb
        RBR Adverb, comparative
        RBS Adverb, superlative
        RP Particle
        SYM Symbol
        TO to
        UH Interjection
        VB Verb, base form
        VBD Verb, past tense
        VBG Verb, gerund or present participle
        VBN Verb, past participle
        VBP Verb, non­3rd person singular present
        VBZ Verb, 3rd person singular present
        WDT Wh­determiner
        WP Wh­pronoun
        WP$ Possessive wh­pronoun
        WRB Wh­adverb
        """


full_annotator_list = ["ner", "pos", "lemma",  "depparse",  "relation"]

language ="fr"

cf = CoreNLP(url='http://localhost:9009',
             language = language,
             annotator_list=full_annotator_list,
             isPrint = False )

"""
#Calling basic function which would return a 'requests' object
out = cf.basic(data, out_format='json'  )
print ('Basic')haque 
pp.pprint(out.json())
"""




pp = pprint.PrettyPrinter(indent=4) 

full_annotator_list = ["tokenize", "cleanxml", "ssplit", "pos", "lemma", "ner", "regexner", "truecase", "parse",
                       "depparse", "dcoref", "relation", "natlog", "quote"]

full_annotator_list = ["ner", "pos", "lemma",  "depparse",  "relation"]

language ="fr"

cf = CoreNLP(url='http://localhost:9009',
             language = language,
             annotator_list=full_annotator_list,
             isPrint = False )

def get_enhancedPlusPlusDependencies (data) :
    t0 = time.time()
    Arrange, sentences = cf.arrange(data,)
    #print ("temps de calcul = %1.2f secondes" %(time.time() - t0))
    #print ("\n ###################### ==== Affichage du dictionnaire Arrange ===== ###################### \n")
    #pp.pprint (Arrange)
    ner = Arrange ['ner']
    roles = Arrange ['pos']
    words = Arrange ['word']
    #print ("ner" + str(ner))
    
    #print ("\n ###################### ==== Affichage du dictionnaire sentences ===== ###################### \n")
    #pp.pprint (sentences)
    enhancedPlusPlusDependencies = sentences[0] ['enhancedPlusPlusDependencies']
    #print ("\n ## == Affichage de la valeur associée à la clé enhancedPlusPlusDependencies dans le dictionnaire sentences == ## \n")
    #pp.pprint(enhancedPlusPlusDependencies)
    
    return enhancedPlusPlusDependencies, ner , roles, words
    



def lecture_fichier(path = "./definition de famille (simple).txt") :
    data = []
    with codecs.open(path, "r", "utf-8") as f :
        for line in f.readlines():
            if not line.strip().startswith("#") and not "#--" in line.strip() and not line.strip() == "":
                data.append(line.strip("\r\n"))

    f.close()
    return data
