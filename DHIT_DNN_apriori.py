# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:51:02 2019

@author: arash
"""

import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.callbacks import ModelCheckpoint
from keras.utils import plot_model
from scipy.stats import norm 

#%%
#Class of problem to solve 2D decaying homogeneous isotrpic turbulence
class DHIT:
    def __init__(self,n_snapshots,nx,ny):
        
        '''
        initialize the DHIT class
        
        Inputs
        ------
        n_snapshots : number of snapshots available
        nx,ny : dimension of the snapshot

        '''
        
        self.nx = nx
        self.ny = ny
        self.n_snapshots = n_snapshots
        self.f_train,self.ue_train,self.f_test,self.ue_test = self.gen_data()
        
    def gen_data(self):
        
        '''
        data generation for training and testing CNN model

        '''
        
        n_snapshots_train = self.n_snapshots #- 10
        n_snapshots_test = 50
        
        f_train  = np.zeros(shape=(n_snapshots_train, self.nx+1, self.ny+1, 5), dtype='double')
        ue_train = np.zeros(shape=(n_snapshots_train, self.nx+1, self.ny+1, 1), dtype='double')
        
        f_test  = np.zeros(shape=(n_snapshots_test, self.nx+1, self.ny+1, 5), dtype='double')
        ue_test = np.zeros(shape=(n_snapshots_test, self.nx+1, self.ny+1, 1), dtype='double')
        
        for n in range(1,n_snapshots_train+1):
            file_input = "spectral/Re_4000/uc/uc_"+str(n)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_train[n-1,:,:,0] = data_input
            
            file_input = "spectral/Re_4000/vc/vc_"+str(n)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_train[n-1,:,:,1] = data_input
            
            file_input = "spectral/Re_4000/uuc/uuc_"+str(n)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_train[n-1,:,:,2] = data_input
            
            file_input = "spectral/Re_4000/uvc/uvc_"+str(n)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_train[n-1,:,:,3] = data_input
            
            file_input = "spectral/Re_4000/vvc/vvc_"+str(n)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_train[n-1,:,:,4] = data_input
                       
            file_output = "spectral/Re_4000/true_shear_stress/t_"+str(n)+".csv"
            data_output = np.genfromtxt(file_output, delimiter=',')
            data_output = data_output.reshape((3,self.nx+1,self.ny+1))
            ue_train[n-1,:,:,0] = data_output[0,:,:] # tau_11
            
        for n in range(1,n_snapshots_test+1):
            p = n #+ n_snapshots_train
            file_input = "spectral/Re_8000/uc/uc_"+str(p)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_test[n-1,:,:,0] = data_input
            
            file_input = "spectral/Re_8000/vc/vc_"+str(p)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_test[n-1,:,:,1] = data_input
            
            file_input = "spectral/Re_8000/uuc/uuc_"+str(p)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_test[n-1,:,:,2] = data_input
            
            file_input = "spectral/Re_8000/uvc/uvc_"+str(p)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_test[n-1,:,:,3] = data_input
            
            file_input = "spectral/Re_8000/vvc/vvc_"+str(p)+".csv"
            data_input = np.genfromtxt(file_input, delimiter=',')
            f_test[n-1,:,:,4] = data_input
                       
            file_output = "spectral/Re_8000/true_shear_stress/t_"+str(p)+".csv"
            data_output = np.genfromtxt(file_output, delimiter=',')
            data_output = data_output.reshape((3,self.nx+1,self.ny+1))
            ue_test[n-1,:,:,0] = data_output[0,:,:] # tau_11
            
        return f_train, ue_train, f_test, ue_test
    
#%%
#A Convolutional Neural Network class
class DNN:
    def __init__(self,x_train,y_train,nf,nl):
        
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
        self.nf = nf
        self.nl = nl
        self.model = self.DNN(x_train,y_train,nf,nl)
        
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
        
        model = Sequential()
        input_layer = Input(shape=(self.nf,))
        
        x = Dense(120, activation='relu',  use_bias=True)(input_layer)
        x = Dense(120, activation='relu',  use_bias=True)(x)
        x = Dense(120, activation='relu',  use_bias=True)(x)
        x = Dense(120, activation='relu',  use_bias=True)(x)
        x = Dense(120, activation='relu',  use_bias=True)(x)
        x = Dense(120, activation='relu',  use_bias=True)(x)
        
        output_layer = Dense(nl, activation='linear', use_bias=True)(x)
        
        model = Model(input_layer, output_layer)
        
        return model

    def DNN_compile(self,optimizer):
        
        '''
        compile the CNN model
        
        Inputs
        ------
        optimizer: optimizer of the CNN

        '''
        
        self.model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['accuracy'])
        
    def DNN_train(self,epochs,batch_size,filepath):
        
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
        
        filepath = filepath
        checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]
        
        history_callback = self.model.fit(self.x_train,self.y_train,epochs=epochs,batch_size=batch_size, 
                                          validation_split= 0.15,callbacks=callbacks_list)
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
        plt.semilogy(epochs, loss_, 'b', label='Training loss')
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
        
        y_test = self.model.predict(x_test)
        return y_test
    
    def DNN_info(self):
        
        '''
        print the CNN model summary
        '''
        
        self.model.summary()
        plot_model(self.model, to_file='dnn_model.png')
     
        
#%%
# generate training and testing data for CNN
obj = DHIT(n_snapshots=50,nx=64,ny=64)

x_train,y_train = obj.f_train,obj.ue_train
x_test,y_test = obj.f_test,obj.ue_test

nt,nx,ny,nci=x_train.shape
nt,nx,ny,nco=y_train.shape 

#%%
# train the CNN model and predict for the test data
model=DNN(x_train,y_train,nx,ny,nci,nco)

model.DNN_info()

model.DNN_compile(optimizer='adam')

history_callback = model.CNN_train(epochs=1000,batch_size=32,'dnn_best_model.hd5')

loss, val_loss = model.CNN_history(history_callback)

y_test = model.DNN_predict(x_test)


#%%
# histogram plot for shear stresses along with probability density function 
# PDF formula: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
nx = 64
ny = 64

y11t = y_test[49,:,:,0].flatten()
mut = np.mean(y11t)
sigmat = np.std(y11t)

y11p = y_pred[49,:,:,0].flatten()
mup = np.mean(y11p)
sigmap = np.std(y11p)

ts = np.genfromtxt('spectral/Re_8000/smag_shear_stress/ts_50.csv', delimiter=',') 
ts = ts.reshape((3,nx+1,ny+1))
y11s = ts[0,:,:].flatten()
#y11s = ts[1,:,:].flatten()
#y11s = ts[2,:,:].flatten()
mus = np.mean(y11s)
sigmas = np.std(y11s)

num_bins = 64

fig, axs = plt.subplots(1,2,figsize=(10,4.5))
axs[0].set_yscale('log')

# the histogram of the data
ntrue, binst, patchest = axs[0].hist(y11t, num_bins, histtype='step', alpha=1, color='r',zorder=5,
                                 linewidth=2.0,range=(-4*sigmat,4*sigmat),density=True,label="True")

npred, binsp, patchesp = axs[0].hist(y11p, num_bins, histtype='step', alpha=1,color='b',zorder=10,
                                 linewidth=2.0,range=(-4*sigmat,4*sigmat),density=True,label="CNN")

nsmag, binss, patchess = axs[0].hist(y11s, num_bins, histtype='step', alpha=1,color='g',zorder=10,
                                 linewidth=2.0,range=(-4*sigmat,4*sigmat),density=True,label="Smag")

x_ticks = np.arange(-4*sigmat, 4.1*sigmat, sigmat)                                  
x_labels = [r"${} \sigma$".format(i) for i in range(-4,5)]


axs[0].set_title(r"$\tau_{22}$")
axs[0].set_xticks(x_ticks)                                                           
axs[0].set_xticklabels(x_labels)              

# Tweak spacing to prevent clipping of ylabel
axs[0].legend()

x_plott = np.linspace(min(y11t), max(y11t), 1000)
x_plotp = np.linspace(min(y11p), max(y11p), 1000)
x_plots = np.linspace(min(y11s), max(y11s), 1000)

axs[1].plot(x_plott, norm.pdf(x_plott, mut, sigmat), 'r-', lw=3, label="True")
axs[1].plot(x_plotp, norm.pdf(x_plotp, mup, sigmap), 'b-', lw=3, label="CNN")
axs[1].plot(x_plots, norm.pdf(x_plots, mus, sigmas), 'g-', lw=3, label="Smag")       
                                                    
axs[1].legend(loc='best')

axs[1].set_xlim(-4*sigmat,4*sigmat)  
axs[1].set_title(r"$\tau_{22}$")                     
axs[1].set_xticks(x_ticks)                                                           
axs[1].set_xticklabels(x_labels)              

fig.tight_layout()
plt.show()

fig.savefig("extrapolation_t11.pdf", bbox_inches = 'tight')

#%%
# contour plot of shear stresses
fig, axs = plt.subplots(1,3,sharey=True,figsize=(10.5,3.5))

cs = axs[0].contourf(y_test[4,:,:,0].T, 120, cmap = 'jet', interpolation='bilinear')
axs[0].text(0.4, -0.1, 'True', transform=axs[0].transAxes, fontsize=14, va='top')

cs = axs[1].contourf(y_test[4,:,:,0].T, 120, cmap = 'jet', interpolation='bilinear')
axs[1].text(0.4, -0.1, 'CNN', transform=axs[1].transAxes, fontsize=14, va='top')

cs = axs[2].contourf(ts[0,:,:].T, 120, cmap = 'jet', interpolation='bilinear')
axs[2].text(0.4, -0.1, 'Smag', transform=axs[2].transAxes, fontsize=14, va='top')

fig.tight_layout() 

fig.subplots_adjust(bottom=0.15)

cbar_ax = fig.add_axes([0.22, -0.05, 0.6, 0.04])
fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
plt.show()

