# =============================================================================
# Scraping des maires des grandes villes francaises sur wikipédia
# Création d'une petite base sous forme d'un array sur laquelle faire tourner l'algo de prédiction

# =============================================================================
import re
import requests
from bs4 import BeautifulSoup
 
url='https://fr.wikipedia.org/wiki/Liste_des_maires_des_grandes_villes_fran%C3%A7aises'
content=requests.get(url).content
soup=BeautifulSoup(content, 'lxml')

# data est un tableau de 98 lignes avec  pour colonnes: Commune, Non et Prénom du maire, Parti politique et lien vers la page wikipedia du maire
data=[]
table = soup.find("table", { "class" : "wikitable sortable jquery-tablesorter" })
for row in soup.table.findAll("tr"):
    data.append([])
    cells = row.findAll("td")
    if len(cells)!=0:
        data[-1].append(cells[0].text)
        data[-1].append(cells[1].text)
        data[-1].append(cells[-1].text)
        link=row.findAll("a", {"title" : cells[1].text})
        if len(link)!=0: #ne prend pas en compte les maires qui n'ont pas de page wikipedia
            data[-1].append(link[0].get('href'))
            
    
def occurence(liste, lien): #calcule l'occurence des mots se trouvant sur "liste" dans la page "lien"
    content=requests.get(lien).content
    soup=BeautifulSoup(content, 'lxml')
    S=0
    for i in range(len(liste)):
        S=S+len(soup.body.find_all(string=re.compile('.*{0}.*'.format(liste[i])), recursive=True))
    return S

# =============================================================================
# Creation du training set à partir de "data"
# Xtrain possède 98 lignes (98 maires) et 19 colonnes (19 inputs qui correspondent aux occurences de mots particuliers)
# =============================================================================

Xtrain=[]

for i in range(len(data)):
    if len(data[i])==4:
        x1=occurence(["gauche","Gauche", "gauches"], "https://fr.wikipedia.org"+data[i][3] )
        x2=occurence(["droite","Droite", "droites"], "https://fr.wikipedia.org"+data[i][3] )
        x3=occurence(["Républicain","républicain", "Républicains","républicains"], "https://fr.wikipedia.org"+data[i][3] )
        x4=occurence(["centre","Centre", "centres", "centriste", "centristes"], "https://fr.wikipedia.org"+data[i][3] )
        x5=occurence(["social","socials", "socialiste", "socialistes"], "https://fr.wikipedia.org"+data[i][3] )
        x6=occurence(["démocrate","démocrates"], "https://fr.wikipedia.org"+data[i][3] )
        x7=occurence(["Corse","corse"], "https://fr.wikipedia.org"+data[i][3] )
        x8=occurence(["indépendant", "indépendants"], "https://fr.wikipedia.org"+data[i][3] )
        x9=occurence(["Calédonie","calédonien","calédonienne"], "https://fr.wikipedia.org"+data[i][3] )
        x10=occurence(["communiste","communistes"], "https://fr.wikipedia.org"+data[i][3] )
        x11=occurence(["radical","radicale","radicales"], "https://fr.wikipedia.org"+data[i][3] )
        x12=occurence(["communiste","communistes"], "https://fr.wikipedia.org"+data[i][3] )
        x13=occurence(["guyane","guyanais","Guyane"], "https://fr.wikipedia.org"+data[i][3] )
        x14=occurence(["divers","Divers"], "https://fr.wikipedia.org"+data[i][3] )
        x15=occurence(["Martinique","martiniquais"], "https://fr.wikipedia.org"+data[i][3] )
        x16=occurence(["SE","sans étiquette"], "https://fr.wikipedia.org"+data[i][3] )
        x17=occurence(["écologie","écologique","Europe", "Ecologique"], "https://fr.wikipedia.org"+data[i][3] )
        x18=occurence(["mahorais","Mayotte"], "https://fr.wikipedia.org"+data[i][3] )
        x19=occurence(["Guadeloupe", "guadeloupéen"], "https://fr.wikipedia.org"+data[i][3] )
        Xtrain.append([x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17,x18,x19])
       
# =============================================================================
# Ytrain est la liste des partis correspondants à chaque maire
#Attribution d'un nombre pour chaque étiquette
# =============================================================================
        
Ytrain=[]

for i in range(len(data)):
    if len(data[i])==4:
        if data[i][-2]=="SE":
            Ytrain.append(0)
        if data[i][-2]=="UDI":
            Ytrain.append(1)
        if data[i][-2]=="LR":
            Ytrain.append(2)
        if data[i][-2]=="PS":
            Ytrain.append(3)
        if data[i][-2]=="PCF":
            Ytrain.append(4)
        if data[i][-2]=="Femu a Corsica":
            Ytrain.append(5)
        if data[i][-2]=="MoDem":
            Ytrain.append(6)
        if data[i][-2]=="PRG":
            Ytrain.append(7)
        if data[i][-2]=="DVD":
            Ytrain.append(8)
        if data[i][-2]=="DVG":
            Ytrain.append(9)
        if data[i][-2]=="PSG":
            Ytrain.append(10)
        if data[i][-2]=="EELV":
            Ytrain.append(11)
        if data[i][-2]=="MDM":
            Ytrain.append(12)
        if data[i][-2]=="Calédonie ensemble":
            Ytrain.append(13)
        if data[i][-2]=="PR":
            Ytrain.append(14)
        if data[i][-2]=="PPDG":
            Ytrain.append(15)
        if data[i][-2]=="FASE":
            Ytrain.append(16)
        if data[i][-2]=="UDI/MoDem":
            Ytrain.append(17)
        if data[i][-2]=="FN (app.)":
            Ytrain.append(17)
            
# =============================================================================
# Division au hasard du set de données en un train subset d'environ 80 maires et un test subset de 20 maires
# Pour chaque exécution les subsets sont différents
# Pour obtenir les mêmes subsets à chaque execution il suffit de donner une valeur à l'argument 'random_state'
# =============================================================================
from sklearn.model_selection import train_test_split
from sklearn import cross_validation
from sklearn import metrics
import numpy as np

X = np.array(Xtrain)
t= np.array(Ytrain)
X_train, X_test, t_train, t_test = train_test_split(X, t, test_size=0.2)

# =============================================================================
# Logistic Regression
# =============================================================================

from sklearn.linear_model import LogisticRegression 
predicted = cross_validation.cross_val_predict(LogisticRegression(), X_train, t_train, cv=5)
acc_validation_lr=metrics.accuracy_score(t_train, predicted) #l'accurance de LR calculée sur un validation set

lr=LogisticRegression().fit(X_train, t_train)
t_pred = lr.predict(X_test)
acc_test_lr=metrics.accuracy_score(t_test, t_pred) #l'accurance de LR calculée sur un test set

print(acc_validation_lr,acc_test_lr) 

#ex1 0.78  0.85
#ex2 0.79  0.8
#ex3 0.77  0.9
#ex4 0.83  0.65

# =============================================================================
# MLP Classifier 
# =============================================================================

from sklearn.neural_network import MLPClassifier


# Le réseau de neurones se compose d'un input, d'un output et d'un hidden layer 
# Il n'existe pas de règles générales pour fixer la taille du hidden layer
# neuro(n) prend en entrée n le nombre de colonnes du hidden layer et donne le nombre de lignes du hidden layer qui renvoie la meilleur accuracy
def neuro(n):
    l=[]
    for i in range(19,98): #il est recommendé que le nombre de lignes du hidden layer soit compris entre le nombre d'inputs de notre modèle et le nombre de samples ici le nombre de maires
        mlp=MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(i,n), random_state=1)
        mlp.fit(X_train, t_train)
        l.append(mlp.score(X_test,t_test))
    return l.index(max(l))+19

predicted = cross_validation.cross_val_predict(MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(neuro(5),5), random_state=1), X_train, t_train, cv=5)
acc_validation_mlp=metrics.accuracy_score(t_train, predicted) #l'accurance de MLP calculée sur un validation set

mlp=MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(neuro(5),5))
mlp.fit(X_train, t_train)
t_pred = mlp.predict(X_test)
acc_test_mlp=metrics.accuracy_score(t_test, t_pred) #l'accurance de MLP calculée sur un test set

print(acc_validation_mlp,acc_test_mlp) 

#ex1 0.74 0.8
#ex2 0.73 0.7
#ex3 0.7  0.85
#ex4 0.72 0.85

# =============================================================================
# Decision Tree Classifier
# =============================================================================

from sklearn import tree


tr = tree.DecisionTreeClassifier()
tr.fit(X_train, t_train)

predicted = cross_validation.cross_val_predict(tr, X_train, t_train, cv=5)
acc_validation_tr=metrics.accuracy_score(t_train, predicted) #l'accurance de Tree calculée sur un validation set

t_pred = tr.predict(X_test)
acc_test_tr=metrics.accuracy_score(t_test, t_pred) #l'accurance de Tree calculée sur un test set

print(acc_validation_tr,acc_test_tr)

 

# =============================================================================
# Random Forest Classifier
# =============================================================================

from sklearn.ensemble import RandomForestClassifier

rd = tree.DecisionTreeClassifier()
rd.fit(X_train, t_train)

predicted = cross_validation.cross_val_predict(rd, X_train, t_train, cv=5)
acc_validation_rd=metrics.accuracy_score(t_train, predicted) 

t_pred = rd.predict(X_test)
acc_test_rd=metrics.accuracy_score(t_test, t_pred)

print(acc_validation_rd,acc_test_rd)


# =============================================================================
# Methode ensembliste VOTING CLASSIFIER qui s'appuie sur les méthodes précédentes pour améliorer la prédiction. 
# Chaque maire se voit attribuer un coefficient pour chaque méthode: ce coefficient étant plus grand pour la méthode qui renvoit la bonne prédiction.
# =============================================================================

from sklearn.ensemble import VotingClassifier

clf1=MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(21,5), random_state=1)
clf2 = LogisticRegression(random_state=1)
clf3 = RandomForestClassifier(random_state=1)
clf4 = tree.DecisionTreeClassifier()
eclf = VotingClassifier(estimators=[('nn', clf1),('lr', clf2), ('rf', clf3), ('tr', clf4)], voting='soft')

eclf.fit(X_train,t_train)
t_predicted=eclf.predict(X_test)     
proba=eclf.predict_proba(X_test)
acc_test_VC=metrics.accuracy_score(t_test, t_predicted)
print(acc_test_VC)

l=[]
for i in range(len(t_predicted)):
    l.append([t_predicted[i],max(proba[i])])
print(l) #l est composée des parties prédis par cette méthode et de des probabilités associées
    
#acc_test_VC=0.8
#t_test=array([ 2,  2,  3,  3,  2,  2,  2,  2,  2,  9,  2, 15,  2,  2,  2,  3,  1, 1,  2,  3])
#t_predicted=[[2, 0.9712766703637592], [2, 0.99430910093318592], [3, 0.86098736623887018], [3, 0.5884457851732906], [3, 0.58268244760264154], [2, 0.9731562699720856], [2, 0.86856987492290405], [2, 0.94763934659549298], [2, 0.9220303186499148], [3, 0.61218335822703851], [2, 0.59984401990706737], [2, 0.69808329923422607], [2, 0.63987059835374815], [2, 0.43559514819039524], [2, 0.96988738223283111], [3, 0.849999999784389], [2, 0.5706491632073839], [1, 0.54715190756106069], [2, 0.92464895225817356], [3, 0.79234395232005062]]

#acc_test_VC=0.85
#t_test=array([ 1,  2,  2,  3,  2,  2,  1, 14,  3,  2,  3,  2,  3,  6,  6,  3,  3, 2,  2,  2])
#t_predicted=[[1, 0.69415906225661295], [2, 0.94781037614113073], [2, 0.96063314521687215], [3, 0.96932183464016564], [2, 0.94994487625557511], [2, 0.91785361375664709], [1, 0.58337942667185505], [9, 0.39155604754960049], [3, 0.95224529696597693], [2, 0.67042579509405531], [3, 0.93168411449476118], [2, 0.95917525622830657], [3, 0.87991247371756143], [3, 0.44714432715071672], [3, 0.76889020522596385], [3, 0.91741100287234834], [3, 0.99989826071873589], [2, 0.96304139328176375], [2, 0.89596545412690587], [2, 0.97499829261133242]]

#acc_test=0.95
#t_test=array([2, 2, 3, 1, 3, 2, 2, 2, 2, 3, 9, 2, 2, 2, 2, 3, 8, 2, 2, 3])
#t_predicted=[[2, 0.55601018690010795], [2, 0.923538409545827], [3, 0.51085694093548795], [1, 0.64991854991360953], [3, 0.43039033680005334], [2, 0.77973823670194431], [2, 0.99421729713607987], [2, 0.92498420125183622], [2, 0.88878567838253075], [3, 0.54995290729270174], [9, 0.55592338564014232], [2, 0.88826646112813612], [2, 0.89740071577242475], [2, 0.9672205592080716], [2, 0.92498381096822557], [3, 0.9478081919480511], [2, 0.49325667420248359], [2, 0.8719929898698715], [2, 0.93091655132445594], [3, 0.57499999900326881]]