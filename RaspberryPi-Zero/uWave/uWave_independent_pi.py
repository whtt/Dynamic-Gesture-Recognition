
# coding: utf-8

# In[1]:

import numpy as np
from sklearn.model_selection import train_test_split
from scipy.stats import skew, kurtosis
from scipy.signal import hilbert
from sklearn.ensemble import ExtraTreesClassifier
from time import time


# In[2]:

path = './assets/uWaveGestureLibrary/'

def load_data():
    print ("Loading dataset...")
    data, labels = [], []
    for us in range(1, 9):
        da, la = [], []
        for day in range(1, 8):
            for ges in range(1, 9):
                fx = path + "U" + str(us) + " (" + str(day) + ")/"
                fy = fx + letters[us-1] + "_Template_Acceleration" + str(ges) + "-"
                for ges_inst in range(1, 11):
                    fz = fy + str(ges_inst) + '.txt'
                    d = np.loadtxt(fz).reshape(-1, 3)
                    da.append(d)
                    la.append(ges)
        data.append(da)
        labels.append(la)
    data = np.array(data)
    labels = np.array(labels)
    
    return data, labels
        
letters = ['A', 'C', 'E', 'H', 'J', 'M', 'R', 'Z']
data_set, data_label = load_data()

print ("Dataset: ", data_set.shape)
print ("Labels: ", data_label.shape)


# In[3]:

data_sets = np.array(data_set[0]).reshape(1, -1)
data_sets = np.hstack((data_sets, data_set[1].reshape(1, -1)))
data_sets = np.hstack((data_sets, data_set[2][:224].reshape((1, -1))))
data_sets = np.hstack((data_sets, data_set[2][225:].reshape(1, -1)))
data_sets = np.hstack((data_sets, data_set[3:6].reshape(1, -1)))
data_sets = np.hstack((data_sets, data_set[6][:404].reshape(1, -1)))
data_sets = np.hstack((data_sets, data_set[6][405:].reshape(1, -1)))
data_sets = np.hstack((data_sets, data_set[7].reshape(1, -1)))
data_sets = data_sets.reshape(-1, 1)
# print (data_sets.shape)


# In[4]:

data_labels = np.array(data_label[0]).reshape(1, -1)
data_labels = np.hstack((data_labels, data_label[1].reshape(1, -1)))
data_labels = np.hstack((data_labels, data_label[2][:224].reshape((1, -1))))
data_labels = np.hstack((data_labels, data_label[2][225:].reshape(1, -1)))
data_labels = np.hstack((data_labels, data_label[3:6].reshape(1, -1)))
data_labels = np.hstack((data_labels, data_label[6][:404].reshape(1, -1)))
data_labels = np.hstack((data_labels, data_label[6][405:].reshape(1, -1)))
data_labels = np.hstack((data_labels, data_label[7].reshape(1, -1)))
data_labels = data_labels.reshape(-1, 1)
# print (data_labels.shape)


# In[5]:

print ("Running Train-Test Split among users...")
Xtrain = data_sets[:3918]
Xtest = data_sets[3918:]
ytrain = data_labels[:3918]
ytest = data_labels[3918:]


# In[6]:

# print ("X_train: ", Xtrain.shape)
# print ("X_test: ", Xtest.shape)
# print ("y_train: ", ytrain.shape)
# print ("y_test: ", ytest.shape)


# In[7]:

def feature_extraction(X):
    
    crosscorr, correlations = [], []
    minimum = np.min(X, axis=0)
    maximum = np.max(X, axis=0)
    feature_fft = np.fft.rfft(X, axis=0)
    feature_fft = np.abs(feature_fft)
    
    feature = np.mean(X, axis=0) # 1 Mean
    
    feature = np.concatenate((feature, skew(X, axis=0)))  # 2 Skew
    
    feature = np.concatenate((feature, kurtosis(X, axis=0))) # 3 Kurtosis

    correlations.append(np.corrcoef(X[:, 0], X[:, 1])[0][1])
    correlations.append(np.corrcoef(X[:, 1], X[:, 2])[0][1])
    correlations.append(np.corrcoef(X[:, 0], X[:, 2])[0][1])
    feature = np.concatenate((feature, correlations)) # 4 Pearson-Moment Corrcoefs
    
    crosscorr.append(np.correlate(X[:, 0], X[:, 1]))
    crosscorr.append(np.correlate(X[:, 1], X[:, 2]))
    crosscorr.append(np.correlate(X[:, 0], X[:, 2]))
    crosscorr = np.array(crosscorr).flatten()
    feature = np.concatenate((feature, crosscorr)) # 5 Cross-correlations
    
    energy = np.sum(feature_fft ** 2, axis=0)
    feature = np.concatenate((feature, energy)) # 6 FFT Energy
    
    hilbert_trans = np.imag(hilbert(X, axis=0))
    hilbert_minimum = np.min(hilbert_trans, axis=0)
    hilbert_maximum = np.max(hilbert_trans, axis=0)
    
    feature = np.concatenate((feature, np.mean(hilbert_trans, axis=0))) # 7 Hilbert Mean

    feature = np.concatenate((feature, skew(hilbert_trans, axis=0))) # 8 Hilbert Skew

    feature = np.concatenate((feature, hilbert_minimum)) # 9 Hilbert Minimum
    
    feature = np.concatenate((feature, hilbert_maximum)) # 10 Hilbert Maximum
    
    hilbert_energy = np.sum(hilbert_trans ** 2, axis=0)
    feature = np.concatenate((feature, hilbert_energy)) # 11 Hilbert Energy
    
    return feature


# In[8]:

feature_set_train, feature_set_test = [], []

for i in range(Xtrain.shape[0]):
    for j in range(Xtrain.shape[1]):
        feature_set_train.append(feature_extraction(Xtrain[i][j]))

for i in range(Xtest.shape[0]):
    for j in range(Xtest.shape[1]):
        feature_set_test.append(feature_extraction(Xtest[i][j]))

feature_sets_train = np.array(feature_set_train)
feature_sets_test = np.array(feature_set_test)

print ("Loading Feature Set Matrix...")
print ("FeatureSet Train: ", feature_sets_train.shape)
print ("FeatureSet Test: ", feature_sets_test.shape)


# In[9]:

ytrain = ytrain.reshape(-1, )
ytest = ytest.reshape(-1, )
# print ("ytrain Reshaped!")


# In[10]:

Emodel = ExtraTreesClassifier(n_estimators=100)
Emodel.fit(feature_sets_train, ytrain)


# In[11]:

t1 = time()
pred = Emodel.predict(feature_sets_test[0].reshape(1, -1))
print ("Running the Classifier, Sony Independent mode... ")
print ("Predicted Label: ", pred[0])
t2 = time()
print ("Time taken per prediction (in sec): ", t2-t1)


# In[ ]:



