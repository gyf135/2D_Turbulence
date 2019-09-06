# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:51:02 2019

@author: Suraj Pawar
"""

import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential, Model, load_model
from keras.layers import Dense, Dropout, Input
from keras.callbacks import ModelCheckpoint
from keras.utils import plot_model
from keras import optimizers
from scipy.stats import norm 
from keras import backend as K
from sklearn.preprocessing import MinMaxScaler
from numpy.random import seed
seed(1)
from tensorflow import set_random_seed
set_random_seed(2)
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import RandomizedSearchCV, KFold
from sklearn.model_selection import train_test_split
from keras.regularizers import l2
from utils import *
import os

#%%
#Class of problem to solve 2D decaying homogeneous isotrpic turbulence
class DHIT:
    def __init__(self,nx,ny,nxf,nyf,freq,n_snapshots,n_snapshots_train,n_snapshots_test,
                 istencil,ifeatures,ilabel):
        
        '''
        initialize the DHIT class
        
        Inputs
        ------
        n_snapshots : number of snapshots available
        nx,ny : dimension of the snapshot

        '''
        
        self.nx = nx
        self.ny = ny
        self.nxf = nxf
        self.nyf = nyf
        self.freq = freq
        self.n_snapshots = n_snapshots
        self.n_snapshots_train = n_snapshots_train
        self.n_snapshots_test = n_snapshots_test
        self.istencil = istencil
        self.ifeatures = ifeatures
        self.ilabel = ilabel
        
        self.uc = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.vc = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.ucx = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.ucy = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.vcx = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.vcy = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.ucxx = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.ucyy = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.vcxx = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.vcyy = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.t11 = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.t12 = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.t22 = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        self.nu = np.zeros(shape=(self.n_snapshots, self.nx+1, self.ny+1), dtype='double')
        
        for m in range(1,self.n_snapshots+1):
            folder = "data_"+ str(self.nxf) + "_" + str(self.nx) + "_V2"
            
            file_input = "spectral/"+folder+"/uc/uc_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.uc[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/vc/vc_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.vc[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/ucx/ucx_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.ucx[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/ucy/ucy_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.ucy[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/vcx/vcx_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.vcx[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/vcy/vcy_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.vcy[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/ucxx/ucxx_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.ucxx[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/ucyy/ucyy_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.ucyy[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/vcxx/vcxx_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.vcxx[m-1,:,:] = data_input
            
            file_input = "spectral/"+folder+"/vcyy/vcyy_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.vcyy[m-1,:,:] = data_input
            
            file_output = "spectral/"+folder+"/true_shear_stress/t_"+str(self.freq*m)+".csv"
            data_output = np.genfromtxt(file_output, delimiter=',')
            data_output = data_output.reshape((3,self.nx+1,self.ny+1))
            self.t11[m-1,:,:] = data_output[0,:,:]
            self.t12[m-1,:,:] = data_output[1,:,:]
            self.t22[m-1,:,:] = data_output[2,:,:]
            
            file_input = "spectral/"+folder+"/nu_smag/nus_"+str(self.freq*m)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            self.nu[m-1,:,:] = data_input
            
        self.x_train,self.y_train = self.gen_train_data()
        self.x_test,self.y_test = self.gen_test_data()
        
    def gen_train_data(self):
        
        '''
        data generation for training and testing CNN model

        '''
        
        # train data
        for m in range(1,self.n_snapshots_train+1):            
            nx,ny = self.nx, self.ny
            nt = int((nx-1)*(ny-1))
            
            if self.istencil == 1 and self.ifeatures == 1:
                x_t = np.zeros((nt,90))
            elif self.istencil == 1 and self.ifeatures == 2:
                x_t = np.zeros((nt,18))
            elif self.istencil == 2 and self.ifeatures == 1:
                x_t = np.zeros((nt,10))
            elif self.istencil == 2 and self.ifeatures == 2:
                x_t = np.zeros((nt,2))
            
            if self.ilabel == 1:
                y_t = np.zeros((nt,3))
            elif self.ilabel == 2:
                y_t = np.zeros((nt,1))
            
            n = 0
            
            if istencil == 1 and ifeatures == 1:
                for i in range(1,nx):
                    for j in range(1,ny):
                        x_t[n,0:9] = self.uc[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,9:18] = self.vc[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,18:27] = self.ucx[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,27:36] = self.ucy[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,36:45] = self.vcx[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,45:54] = self.vcy[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,54:63] = self.ucxx[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,63:72] = self.ucyy[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,72:81] = self.vcxx[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,81:90] = self.vcyy[m-1,i-1:i+2,j-1:j+2].flatten()
                        n = n+1
            
            elif istencil == 1 and ifeatures == 2:  
                for i in range(1,nx):
                    for j in range(1,ny):
                        x_t[n,0:9] = self.uc[m-1,i-1:i+2,j-1:j+2].flatten()
                        x_t[n,9:18] = self.vc[m-1,i-1:i+2,j-1:j+2].flatten()
                        n = n+1
            
            elif istencil == 2 and ifeatures == 1:
                for i in range(1,nx):
                    for j in range(1,ny):
                        x_t[n,0] = self.uc[m-1,i,j]
                        x_t[n,1] = self.vc[m-1,i,j]
                        x_t[n,2] = self.ucx[m-1,i,j]
                        x_t[n,3] = self.ucy[m-1,i,j]
                        x_t[n,4] = self.vcx[m-1,i,j]
                        x_t[n,5] = self.vcy[m-1,i,j]
                        x_t[n,6] = self.ucxx[m-1,i,j]
                        x_t[n,7] = self.ucyy[m-1,i,j]
                        x_t[n,8] = self.vcxx[m-1,i,j]
                        x_t[n,9] = self.vcyy[m-1,i,j]
                        n = n+1
                                                
            elif istencil == 2 and ifeatures == 2:
                for i in range(1,nx):
                    for j in range(1,ny):
                        x_t[n,0:9] = self.uc[m-1,i,j]
                        x_t[n,9:18] = self.vc[m-1,i,j]
                        n = n+1
            
            n = 0
            if ilabel == 1:
                for i in range(1,nx):
                    for j in range(1,ny):
                        y_t[n,0], y_t[n,1], y_t[n,2] = self.t11[m-1,i,j], self.t12[m-1,i,j], self.t22[m-1,i,j]
                        n = n+1
                        
            elif ilabel == 2:
                for i in range(1,nx):
                    for j in range(1,ny):
                        y_t[n,0] = self.nu[m-1,i,j]
                        n = n+1       
            
            if m == 1:
                x_train = x_t
                y_train = y_t
            else:
                x_train = np.vstack((x_train,x_t))
                y_train = np.vstack((y_train,y_t))
        
        return x_train, y_train
    
    def gen_test_data(self):
        
        # test data
        m = self.n_snapshots_test
        nx,ny = self.nx, self.ny
        nt = int((nx-1)*(ny-1))

        if self.istencil == 1 and self.ifeatures == 1:
                x_t = np.zeros((nt,90))
        elif self.istencil == 1 and self.ifeatures == 2:
            x_t = np.zeros((nt,18))
        elif self.istencil == 2 and self.ifeatures == 1:
            x_t = np.zeros((nt,10))
        elif self.istencil == 2 and self.ifeatures == 2:
            x_t = np.zeros((nt,2))
        
        if self.ilabel == 1:
            y_t = np.zeros((nt,3))
        elif self.ilabel == 2:
            y_t = np.zeros((nt,1))
        
        n = 0
        
        if istencil == 1 and ifeatures == 1:
            for i in range(1,nx):
                for j in range(1,ny):
                    x_t[n,0:9] = self.uc[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,9:18] = self.vc[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,18:27] = self.ucx[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,27:36] = self.ucy[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,36:45] = self.vcx[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,45:54] = self.vcy[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,54:63] = self.ucxx[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,63:72] = self.ucyy[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,72:81] = self.vcxx[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,81:90] = self.vcyy[m-1,i-1:i+2,j-1:j+2].flatten()
                    n = n+1
            
        elif istencil == 1 and ifeatures == 2:  
            for i in range(1,nx):
                for j in range(1,ny):
                    x_t[n,0:9] = self.uc[m-1,i-1:i+2,j-1:j+2].flatten()
                    x_t[n,9:18] = self.vc[m-1,i-1:i+2,j-1:j+2].flatten()
                    n = n+1
        
        elif istencil == 2 and ifeatures == 1:
            for i in range(1,nx):
                for j in range(1,ny):
                    x_t[n,0] = self.uc[m-1,i,j]
                    x_t[n,1] = self.vc[m-1,i,j]
                    x_t[n,2] = self.ucx[m-1,i,j]
                    x_t[n,3] = self.ucy[m-1,i,j]
                    x_t[n,4] = self.vcx[m-1,i,j]
                    x_t[n,5] = self.vcy[m-1,i,j]
                    n = n+1
                                            
        elif istencil == 2 and ifeatures == 2:
            for i in range(1,nx):
                for j in range(1,ny):
                    x_t[n,0:9] = self.uc[m-1,i,j]
                    x_t[n,9:18] = self.vc[m-1,i,j]
                    n = n+1
        
        n = 0
        if ilabel == 1:
            for i in range(1,nx):
                for j in range(1,ny):
                    y_t[n,0], y_t[n,1], y_t[n,2] = self.t11[m-1,i,j], self.t12[m-1,i,j], self.t22[m-1,i,j]
                    n = n+1
                    
        elif ilabel == 2:
            for i in range(1,nx):
                for j in range(1,ny):
                    y_t[n,0] = self.nu[m-1,i,j]
                    n = n+1   
        
        x_test = x_t
        y_test = y_t
        
        return x_test, y_test
    
    
#%%
#A Convolutional Neural Network class
class DNN:
    def __init__(self,x_train,y_train,x_valid,y_valid,nf,nl,n_layers,n_neurons,lr):
        
        '''
        initialize the CNN class
        
        Inputs
        ------
        x_train : input features of the DNN model
        y_train : output label of the DNN model
        nf : number of input features
        nl : number of output labels
        '''
        
        self.x_train = x_train
        self.y_train = y_train
        self.x_valid = x_valid
        self.y_valid = y_valid
        self.nf = nf
        self.nl = nl
        self.n_layers = n_layers
        self.n_neurons = n_neurons
        self.lr = lr
        self.model = self.DNN(x_train,y_train,nf,nl)
    
    def coeff_determination(self,y_true, y_pred):
        SS_res =  K.sum(K.square( y_true-y_pred ))
        SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
        return ( 1 - SS_res/(SS_tot + K.epsilon()) )
        
    def DNN(self,x_train,y_train,nf,nl):
        
        '''
        define CNN model
        
        Inputs
        ------
        x_train : input features of the DNN model
        y_train : output label of the DNN model
        nf : number of input features
        nl : number of output labels
        
        Output
        ------
        model: DNN model with defined activation function, number of layers
        '''
        
        # L2 regularization: kernel_regularizer=l2(0.001)
        model = Sequential()
        #model.add(Dropout(0.2))
        input_layer = Input(shape=(self.nf,))
        
        x = Dense(self.n_neurons[0], activation='relu',  use_bias=True)(input_layer)
        for i in range(1,self.n_layers):
            x = Dense(self.n_neurons[i], activation='relu',  use_bias=True)(x)
        
        output_layer = Dense(nl, activation='linear', use_bias=True)(x)
        
        model = Model(input_layer, output_layer)
        
        adam = optimizers.Adam(lr=self.lr, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        model.compile(loss='mean_squared_error', optimizer=adam, metrics=['mse'])
        
        return model

    def DNN_compile(self):
        
        '''
        compile the CNN model
        
        Inputs
        ------
        optimizer: optimizer of the CNN

        '''
        
        adam = optimizers.Adam(lr=self.lr, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        self.model.compile(loss='mean_squared_error', optimizer=adam, metrics=['mse'])
        
    def DNN_train(self,epochs,batch_size):
        
        '''
        train the CNN model
        
        Inputs
        ------
        epochs: number of epochs of the training
        batch_size: batch size of the training
        
        Output
        ------
        history_callback: return the loss history of CNN model training
        '''
        
        filepath = "dnn_best_model.hd5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]
        
        history_callback = self.model.fit(self.x_train,self.y_train,epochs=epochs,batch_size=batch_size, 
                                          validation_data= (self.x_valid,self.y_valid),callbacks=callbacks_list)
        return history_callback
    
    def DNN_history(self, history_callback):
        
        '''
        get the training and validation loss history
        
        Inputs
        ------
        history_callback: loss history of CNN model training
        
        Output
        ------
        loss: training loss history of CNN model training
        val_loss: validation loss history of CNN model training
        '''
        
        loss = history_callback.history["loss"]
        val_loss = history_callback.history["val_loss"]
        
        epochs = range(1, len(loss) + 1)
        plt.figure()
        plt.semilogy(epochs, loss, 'b', label='Training loss')
        plt.semilogy(epochs, val_loss, 'r', label='Validation loss')
        plt.title('Training and validation loss')
        plt.legend()
        plt.show()

        return loss, val_loss
            
    def DNN_predict(self,x_test):
        
        '''
        predict the label for input features
        
        Inputs
        ------
        x_test: test data (has same shape as input features used for training)
        
        Output
        ------
        y_test: predicted output by the CNN (has same shape as label used for training)
        '''
        
        custom_model = load_model('dnn_best_model.hd5')
                                  #custom_objects={'coeff_determination':self.coeff_determination})
        y_test = custom_model.predict(x_test)
        return y_test
    
    def DNN_info(self):
        
        '''
        print the CNN model summary
        '''
        
        self.model.summary()
        plot_model(self.model, to_file='dnn_model.png')
     
        
#%%
# generate training and testing data for CNN
l1 = []
with open('dnn.txt') as f:
    for l in f:
        l1.append((l.strip()).split("\t"))

nxf, nyf = np.int64(l1[0][0]), np.int64(l1[0][0])
nx, ny = np.int64(l1[1][0]), np.int64(l1[1][0])
n_snapshots = np.int64(l1[2][0])
n_snapshots_train = np.int64(l1[3][0])   
n_snapshots_test = np.int64(l1[4][0])        
freq = np.int64(l1[5][0])
istencil = np.int64(l1[6][0])    # 1: nine point, 2: single point
ifeatures = np.int64(l1[7][0])   # 1: 6 features, 2: 2 features 
ilabel = np.int64(l1[8][0])      # 1: SGS (tau), 2: eddy-viscosity (nu)

#%% 
# hyperparameters initilization
n_layers = 2
n_neurons = [60,60]
lr = 0.001

#%%
obj = DHIT(nx=nx,ny=ny,nxf=nxf,nyf=nyf,freq=freq,n_snapshots=n_snapshots,n_snapshots_train=n_snapshots_train, 
           n_snapshots_test=n_snapshots_test,istencil=istencil,ifeatures=ifeatures,ilabel=ilabel)

data,labels= obj.x_train,obj.y_train
x_test,y_test = obj.x_test,obj.y_test

#%%
# scaling between (-1,1)
sc_input = MinMaxScaler(feature_range=(-1,1))
sc_input = sc_input.fit(data)
data_sc = sc_input.transform(data)

sc_output = MinMaxScaler(feature_range=(-1,1))
sc_output = sc_output.fit(labels)
labels_sc = sc_output.transform(labels)

x_test_sc = sc_input.transform(x_test)

#%%
x_train, x_valid, y_train, y_valid = train_test_split(data_sc, labels_sc, test_size=0.4 , shuffle= True)

ns_train,nf = x_train.shape
ns_train,nl = y_train.shape 

#%%
# train the CNN model and predict for the test data
model=DNN(x_train,y_train,x_valid,y_valid,nf,nl,n_layers,n_neurons,lr)
model.DNN_info()
#model.DNN_compile()

#%%
history_callback = model.DNN_train(epochs=10,batch_size=256)#,model_name="dnn_best_model.hd5")
loss, val_loss = model.DNN_history(history_callback)

#%%
#y_pred = model.DNN_predict(x_test)
y_pred_sc = model.DNN_predict(x_test_sc)
y_pred = sc_output.inverse_transform(y_pred_sc)

export_resutls(y_test, y_pred, ilabel, nxf, nx, n='trial', nn = 1)

#%%
folder = "data_"+ str(nxf) + "_" + str(nx) + "_V2"
m = n_snapshots*freq
file_input = "spectral/"+folder+"/smag_shear_stress/ts_"+str(m)+".csv"
ts = np.genfromtxt(file_input, delimiter=',')
ts = ts.reshape((3,nx+1,ny+1))
t11s = ts[0,:,:]
t12s = ts[1,:,:]
t22s = ts[2,:,:]

#%%
# histogram plot for shear stresses along with probability density function 
# PDF formula: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
num_bins = 64

fig, axs = plt.subplots(1,3,figsize=(12,4))
axs[0].set_yscale('log')
axs[1].set_yscale('log')
axs[2].set_yscale('log')

# the histogram of the data
axs[0].hist(y_test[:,0].flatten(), num_bins, histtype='step', alpha=1, color='r',zorder=5,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,0]),4*np.std(y_test[:,0])),density=True,label="True")

axs[0].hist(y_pred[:,0].flatten(), num_bins, histtype='step', alpha=1,color='b',zorder=10,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,0]),4*np.std(y_test[:,0])),density=True,label="DNN")

axs[0].hist(t11s.flatten(), num_bins, histtype='step', alpha=1,color='g',zorder=10,
            linewidth=2.0,range=(-4*np.std(y_test[:,0]),4*np.std(y_test[:,0])),density=True,label=r"Dynamic")

x_ticks = np.arange(-4*np.std(y_test[:,0]), 4.1*np.std(y_test[:,0]), np.std(y_test[:,0]))                                  
x_labels = [r"${} \sigma$".format(i) for i in range(-4,5)]
axs[0].set_title(r"$\tau_{11}$")
axs[0].set_xticks(x_ticks)                                                           
axs[0].set_xticklabels(x_labels)              
axs[0].legend()

#------#
axs[1].hist(y_test[:,1].flatten(), num_bins, histtype='step', alpha=1, color='r',zorder=5,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,1]),4*np.std(y_test[:,1])),density=True,label="True")

axs[1].hist(y_pred[:,1].flatten(), num_bins, histtype='step', alpha=1,color='b',zorder=10,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,1]),4*np.std(y_test[:,1])),density=True,label="DNN")

axs[1].hist(t12s.flatten(), num_bins, histtype='step', alpha=1,color='g',zorder=10,
            linewidth=2.0,range=(-4*np.std(y_test[:,1]),4*np.std(y_test[:,1])),density=True,label=r"Dynamic")

x_ticks = np.arange(-4*np.std(y_test[:,1]), 4.1*np.std(y_test[:,1]), np.std(y_test[:,1]))                                  
x_labels = [r"${} \sigma$".format(i) for i in range(-4,5)]
axs[1].set_title(r"$\tau_{12}$")
axs[1].set_xticks(x_ticks)                                                           
axs[1].set_xticklabels(x_labels)              
axs[1].legend()

#------#
axs[2].hist(y_test[:,2].flatten(), num_bins, histtype='step', alpha=1, color='r',zorder=5,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,2]),4*np.std(y_test[:,2])),density=True,label="True")

axs[2].hist(y_pred[:,2].flatten(), num_bins, histtype='step', alpha=1,color='b',zorder=10,
                                 linewidth=2.0,range=(-4*np.std(y_test[:,2]),4*np.std(y_test[:,2])),density=True,label="DNN")

axs[2].hist(t22s.flatten(), num_bins, histtype='step', alpha=1,color='g',zorder=10,
            linewidth=2.0,range=(-4*np.std(y_test[:,2]),4*np.std(y_test[:,2])),density=True,label=r"Dynamic")

x_ticks = np.arange(-4*np.std(y_test[:,2]), 4.1*np.std(y_test[:,2]), np.std(y_test[:,2]))                                  
x_labels = [r"${} \sigma$".format(i) for i in range(-4,5)]
axs[2].set_title(r"$\tau_{22}$")
axs[2].set_xticks(x_ticks)                                                           
axs[2].set_xticklabels(x_labels)              
axs[2].legend()

fig.tight_layout()
plt.show()

fig.savefig("ts_dnn4.pdf", bbox_inches = 'tight')
