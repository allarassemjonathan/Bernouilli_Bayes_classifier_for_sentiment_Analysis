import math

STOP_WORDS = set(
    """
    a about above across after afterwards again against all almost alone along
    already also although always am amazon among amongst amount an and another any anyhow
    anyone anything anyway anywhere author are around as at b c d e f g h i j k l m n o p q r s t u v w x y z
    back be became because become becomes becoming been before beforehand behind
    being below beside besides between beyond both bottom book books book. but by
    call can cannot ca could cd
    did do does doing done down due during
    each edition eight either eleven else elsewhere empty enough even ever every
    everyone everything everywhere except
    few fifteen fifty film first five find for former formerly forty four from front full
    further
    get give go -
    had has have he hence her here hereafter hereby herein hereupon hers herself
    him himself his how however hundred
    i i'm i've if in indeed into is it its it's itself
    keep
    last latter latterly least less little lot
    just
    made make many may me meanwhile might mine more moreover most mostly move movie movies much
    must my myself money
    name namely neither never nevertheless next new nine no nobody none noone nor 
    nothing now nowhere
    of off often on once one only onto or other others otherwise our ours ourselves
    out over own
    part pages page per perhaps product please put point
    quite
    rather re really regarding read
    same say says said see seem seemed seeming seems serious several she should show side
    since six sixty so some somehow someone something sometime sometimes somewhere
    still story such
    take ten than that the their them themselves then thence there thereafter
    thereby therefore therein thereupon these they third this those though thought three
    through throughout thru thus to the time together too top toward towards twelve twenty
    two
    under until up unless upon us use used using
    various very very version via was way we well were what whatever when whence whenever where
    whereafter whereas whereby wherein whereupon wherever whether which while
    whither who whoever whole whom whose why will with within without would
    yet you your yours yourself yourselves music album life old new christmas world 
    """.split()
)


def update_distribution(filename):
    dicoGood = load_distribution("Bad")
    dicoBad = load_distribution("Good")
    if dicoBad==None:
        dicoBad = {}
        dicoGood = {}
    file1 = open(filename, 'r', encoding = "ISO-8859-1")
    punc = '''±¬¤¸£×¥¿*¶¼¦¹¯§¾´ª½¢¡®…³=²º­¨0123456789!→°()-[]{};:'"«»\,+<>./?@#$%^&*~©'''
    for line in file1.readlines():
        line = line.lower()
        line = line.replace('didn\'t', 'didnt')
        line = line.replace('isn\'t','isnt')
        line = line.replace('don\'t', 'dont')
        line = line.replace('did not', 'didnt')
        line = line.replace('do not', 'dont')
        ar = line.split(' ')
        for i in range(len(ar)):
            if i+1 < len(ar)and (ar[i]=='isnt' or ar[i]=='not'):
                ar[i]=ar[i] + '_' + ar[i+1]
                ar.pop(i+1)
        line = ''
        for word in ar:
            for e in word:
                if e in'.!?:,':
                    word = word.replace(e, '')
            line = line + ' ' + word
        if line.split()[0] == '__label__1':
            for key in line.split():
                if key not in STOP_WORDS:
                    if key in dicoBad.keys():
                        dicoBad[key] = dicoBad[key] + 1
                    else:
                        dicoBad[key] = 1
                
        else:
            for key in line.split():
                if key not in STOP_WORDS:
                    if key in dicoGood.keys():
                        dicoGood[key] = dicoGood[key] + 1
                    else:
                        dicoGood[key] = 1
                

    file2 = open("model_Good.txt", 'w', encoding = "ISO-8859-1")
    dicoGood = {k:v for k,v in sorted(dicoGood.items(), key = lambda item: item[1])}
    for i in dicoGood.keys():
        file2.write(i + ' ' + str(dicoGood[i]) + '\n')
    file2.close()

    file2 = open("model_Bad.txt", 'w', encoding = "ISO-8859-1")
    dicoBad = {k:v for k,v in sorted(dicoBad.items(), key = lambda item: item[1])}
    for i in dicoBad.keys():
        file2.write(i + ' ' + str(dicoBad[i]) + '\n')
    file2.close()
    return dicoBad, dicoGood

def Bernouilli_model(dic, sentence):
    dic = dict(sorted(dic.items(), key=lambda x: x[0].lower()))
    #print(dic)
    ar = sentence.split(' ')
    ar.sort()
    #print(ar)
    presence = []
    for el in dic.keys():
        if el in ar:
            presence.append(1)
        else:
            presence.append(0)
            
    product = 0
    keys = sorted(dic.keys(), key=lambda x:x.lower())
    #print(keys)
    total = 0
    for el in dic.keys():
        total = total + dic[el]
        
    for i in range(len(dic.keys())):
        prob = dic[keys[i]]/total
        xi = presence[i]
        product = product + math.log(pow(prob, xi)*pow(1-prob, 1-xi))
        
    #print(product)
    return product

def assess(filename):
    d1, d2 = load_distribution()
    lines = open("test.ft.txt", 'r', encoding = "ISO-8859-1").readlines()
    newlines =""
    for line in lines:
        line = line.lower()
        newlines = newlines + '\i' + line
    test = newlines.split('\i')
    c = 0
    for s in test:
        sol = ['__label__1', '__label__2']
        if Bernouilli_model(d1, s)> Bernouilli_model(d2, s):
            if sol[0]==s[0:10]:
                c= c + 1
        else:
            if sol[1]==s[0:10]:
                c= c + 1        
    print('Acuracy ' + str(c/len(test)))


def load_distribution():
    dicoGood = {}
    dicoBad = {}
    f = open("model_Good.txt", 'r', encoding= "ISO-8859-1")
    for line in f.readlines():
        temp = line.split(" ")
        if len(temp)>1:
            dicoGood[temp[0]] = int(temp[1])
    f = open("model_Bad.txt", 'r', encoding= "ISO-8859-1")
    for line in f.readlines():
        temp = line.split(" ")
        if len(temp)>1:
            dicoBad[temp[0]] = int(temp[1])
    return dicoGood,dicoBad

    
def expressivity(comment):
    d1, d2 = load_distribution()
    ar = comment.split(' ')
    for i in range(len(ar)):
        if ar[i] in STOP_WORDS:
            ar[i] = ''
    ar.remove('')
    line = ''
    for word in ar:
        for e in word:
            if e in'.!?:,':
                word = word.replace(e, '')
        line = line + ' ' + word
            
    pGood = Bernouilli_model(d1, comment)
    print(pGood)
    pBad = Bernouilli_model(d2, comment)
    print(pBad)
    return pGood/pBad
    
        
j
s = ['I loved that tool so much','I hated that package sfsz afasf afasfas afasfasfas', 'useful When least you think so.']

for el in s:
    print(expressivity(el))
