from sklearn import linear_model
from sklearn.metrics import mean_squared_error
import scipy.sparse as sps
import numpy as np
import math
import random
from sklearn.model_selection import GridSearchCV
import pickle
import statsmodels.api as sm

random.seed(1234)
def normalize_labels(label):
   x = []
   minprecision = 0.001
   maxprecision = 30
   for i in label:
      if i < minprecision:
         i = minprecision
      elif i > maxprecision:
         i = maxprecision
      m = -math.log(i/maxprecision)
      x.append(m)

   return x

################# reading labels
data_path = "/scratch/user/mostafa_karimi/CPI/final_data/Baseline/"
label_path_train=data_path+"train_IC50"
label_train = []
f = open(label_path_train, "r")
length_train=0
for line in f:
    if (line[0]=="<")or(line[0]==">"):
            print("Inequality in IC50!!!\n")
    else:
            label_train.append(float(line))
            length_train = length_train+1

f.close()
label_train = normalize_labels(label_train)


label_path_test=data_path+"test_IC50"
label_test = []
f = open(label_path_test, "r")
length_test=0
for line in f:
    if (line[0]=="<")or(line[0]==">"):
            print("Inequality in IC50!!!\n")
    else:
            label_test.append(float(line))
            length_test = length_test+1

f.close()
label_test = normalize_labels(label_test)

label_path_ER=data_path+"ER_IC50"
label_ER = []
f = open(label_path_ER, "r")
length_ER=0
for line in f:
    if (line[0]=="<")or(line[0]==">"):
            print("Inequality in IC50!!!\n")
    else:
            label_ER.append(float(line))
            length_ER = length_ER+1

f.close()
label_ER = normalize_labels(label_ER)


label_path_GPCR=data_path+"GPCR_IC50"
label_GPCR = []
f = open(label_path_GPCR, "r")
length_GPCR=0
for line in f:
    if (line[0]=="<")or(line[0]==">"):
            print("Inequality in IC50!!!\n")
    else:
            label_GPCR.append(float(line))
            length_GPCR = length_GPCR+1

f.close()
label_GPCR = normalize_labels(label_GPCR)


label_path_kinase=data_path+"channel_IC50"
label_kinase = []
f = open(label_path_kinase, "r")
length_kinase=0
for line in f:
    if (line[0]=="<")or(line[0]==">"):
            print("Inequality in IC50!!!\n")
    else:
            label_kinase.append(float(line))
            length_kinase = length_kinase+1

f.close()
label_kinase = normalize_labels(label_kinase)

##################  reading compound features
data_path = "/scratch/user/mostafa_karimi/CPI/final_data/RNN_features/"
feature_ER = np.zeros((length_ER,768))
textfile1 = open(data_path+"ER_smile_feature")
textfile2 = open(data_path+"ER_fasta_feature")
count=0
while length_ER > count:
    x = textfile1.readline()
    y = textfile2.readline()
    x = x.strip()
    y = y.strip()
    result1 = np.array([list(map(float, x.split()))])
    result2 = np.array([list(map(float, y.split()))])
    result = np.concatenate((result1, result2), axis=1)
    feature_ER[count,]=result
    count = count+1

feature_GPCR = np.zeros((length_GPCR,768))
textfile1 = open(data_path+"GPCR_smile_feature")
textfile2 = open(data_path+"GPCR_fasta_feature")
count=0
while length_GPCR > count:
    x = textfile1.readline()
    y = textfile2.readline()
    x = x.strip()
    y = y.strip()
    result1 = np.array([list(map(float, x.split()))])
    result2 = np.array([list(map(float, y.split()))])
    result = np.concatenate((result1, result2), axis=1)
    feature_GPCR[count,]=result
    count = count+1

feature_kinase = np.zeros((length_kinase,768))
textfile1 = open(data_path+"channel_smile_feature")
textfile2 = open(data_path+"channel_fasta_feature")
count=0
while length_kinase > count:
    x = textfile1.readline()
    y = textfile2.readline()
    x = x.strip()
    y = y.strip()
    result1 = np.array([list(map(float, x.split()))])
    result2 = np.array([list(map(float, y.split()))])
    result = np.concatenate((result1, result2), axis=1)
    feature_kinase[count,]=result
    count = count+1

feature_train = np.zeros((length_train,768))
textfile1 = open(data_path+"train_smile_feature")
textfile2 = open(data_path+"train_fasta_feature")
count=0
while length_train > count:
    x = textfile1.readline()
    y = textfile2.readline()
    x = x.strip()
    y = y.strip()
    result1 = np.array([list(map(float, x.split()))])
    result2 = np.array([list(map(float, y.split()))])
    result = np.concatenate((result1, result2), axis=1)
    feature_train[count,]=result
    count = count+1

feature_test = np.zeros((length_test,768))
textfile1 = open(data_path+"test_smile_feature")
textfile2 = open(data_path+"test_fasta_feature")
count=0
while length_test > count:
    x = textfile1.readline()
    y = textfile2.readline()
    x = x.strip()
    y = y.strip()
    result1 = np.array([list(map(float, x.split()))])
    result2 = np.array([list(map(float, y.split()))])
    result = np.concatenate((result1, result2), axis=1)
    feature_test[count,]=result
    count = count+1

####### pre-processing

scaler = preprocessing.StandardScaler().fit(feature_train)
feature_train = scaler.transform(feature_train)
feature_test = scaler.transform(feature_test)
feature_ER = scaler.transform(feature_ER)
feature_kinase = scaler.transform(feature_kinase)
feature_GPCR = scaler.transform(feature_GPCR)

######### Lasoo model
ridge = linear_model.Ridge (alpha = .5)
alphas = np.logspace(-4, 4, 9)
tuned_parameters = [{'alpha': alphas}]
n_folds = 10
clf = GridSearchCV(ridge, tuned_parameters, cv=n_folds)
clf.fit(feature_train,label_train)

print("train error:")
y_pred = clf.predict(feature_train)
print(mean_squared_error(label_train,y_pred))

results = sm.OLS(y_pred,sm.add_constant(label_train)).fit()
print(results.summary())

print("test error:")
y_pred = clf.predict(feature_test)
print(mean_squared_error(label_test,y_pred))

results = sm.OLS(y_pred,sm.add_constant(label_test)).fit()
print(results.summary())

print("ER error:")
y_pred = clf.predict(feature_ER)
print(mean_squared_error(label_ER,y_pred))

results = sm.OLS(y_pred,sm.add_constant(label_ER)).fit()
print(results.summary())


print("kinase error:")
y_pred = clf.predict(feature_kinase)
print(mean_squared_error(label_kinase,y_pred))

results = sm.OLS(y_pred,sm.add_constant(label_kinase)).fit()
print(results.summary())


print("GPCR error:")
y_pred = clf.predict(feature_GPCR)
print(mean_squared_error(label_GPCR,y_pred))

results = sm.OLS(y_pred,sm.add_constant(label_GPCR)).fit()
print(results.summary())


#########  Saving model
ridge_pkl_filename = 'ridge_20182101.pkl'
ridge_model_pkl = open(ridge_pkl_filename, 'wb')
pickle.dump(clf,ridge_model_pkl)
ridge_model_pkl.close()

########## Saving prediction test
ridge_pkl_test_filename = 'ridge_20182101_test_pred.pkl'
ridge_test_pkl = open(ridge_pkl_test_filename, 'wb')
pickle.dump(y_pred,ridge_test_pkl)
ridge_test_pkl.close()

######### Saving Real label test
ridge_pkl_test_filename = 'ridge_20182101_test_real_lable.pkl'
ridge_test_pkl = open(ridge_pkl_test_filename, 'wb')
pickle.dump(label_test,ridge_test_pkl)
ridge_test_pkl.close()

########## Saving prediction ER
ridge_pkl_ER_filename = 'ridge_20182101_ER_pred.pkl'
ridge_ER_pkl = open(ridge_pkl_ER_filename, 'wb')
pickle.dump(y_pred,ridge_ER_pkl)
ridge_ER_pkl.close()

######### Saving Real label ER
ridge_pkl_ER_filename = 'ridge_20182101_ER_real_lable.pkl'
ridge_ER_pkl = open(ridge_pkl_ER_filename, 'wb')
pickle.dump(label_ER,ridge_ER_pkl)
ridge_ER_pkl.close()

########## Saving prediction kinase
ridge_pkl_kinase_filename = 'ridge_20182101_kinase_pred.pkl'
ridge_kinase_pkl = open(ridge_pkl_kinase_filename, 'wb')
pickle.dump(y_pred,ridge_kinase_pkl)
ridge_kinase_pkl.close()

######### Saving Real label kinase
ridge_pkl_kinase_filename = 'ridge_20182101_kinase_real_lable.pkl'
ridge_kinase_pkl = open(ridge_pkl_kinase_filename, 'wb')
pickle.dump(label_kinase,ridge_kinase_pkl)
ridge_kinase_pkl.close()

########## Saving prediction GPCR
ridge_pkl_GPCR_filename = 'ridge_20182101_GPCR_pred.pkl'
ridge_GPCR_pkl = open(ridge_pkl_GPCR_filename, 'wb')
pickle.dump(y_pred,ridge_GPCR_pkl)
ridge_GPCR_pkl.close()

######### Saving Real label GPCR
ridge_pkl_GPCR_filename = 'ridge_20182101_GPCR_real_lable.pkl'
ridge_GPCR_pkl = open(ridge_pkl_GPCR_filename, 'wb')
pickle.dump(label_GPCR,ridge_GPCR_pkl)
ridge_GPCR_pkl.close()
