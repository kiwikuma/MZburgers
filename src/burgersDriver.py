from pylab import *
from padding import *
import numpy as np
from myffts import *
from RHSfunctions import *
close("all")
if not os.path.exists('Solution'):
   os.makedirs('Solution')

def advanceQ_RK4(main):
  Q0 = zeros(size(main.Q),dtype='complex')
  Q0[:] = main.Q[:]
  rk4const = array([1./4,1./3,1./2,1.])
  for i in range(0,4):
    main.computeRHS(main)
    main.Q = Q0 + main.dt*rk4const[i]*main.RHS
    main.Q2U()

## Setup Solution
class variables:
  def __init__(self,turb_model,N,k,uhat,u,t,kc,dt,nu):
    self.t = t
    self.kc = kc
    self.dt = dt
    self.nu = nu
    self.tauhat = zeros((N/2+1),dtype='complex')
    self.u = zeros(N)
    self.u[:] = u[:]
    self.uhat = zeros((N/2+1),dtype='complex')
    self.uhat[:] = uhat[:]
    self.turb_model = turb_model
    self.k = k
    self.Esave = 0.5*sum(self.uhat*conj(self.uhat))
    self.Dsave = 0
    self.Esave_resolved = 0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc]))
    self.Dsave_resolved = 0
    self.tsave = zeros(0)
    self.tsave = append(self.tsave,self.t)
    self.tsave_full = zeros(0)
    self.tsave_full = append(self.tsave_full,self.t)
    self.uhatsave = zeros( (size(self.uhat),1),dtype = 'complex')
    self.uhatsave[:,0] = self.uhat
    self.tauhatsave = zeros( (size(self.uhat),1),dtype = 'complex')
    self.usave = zeros( (size(self.u),1),dtype = 'complex')
    self.usave[:,0] = self.u[:]
    self.Delta = pi/self.kc
    #=======================================
    ## DNS Setup
    #=======================================
    if (turb_model == 0):
      self.Q = zeros((N/2+1),dtype='complex')
      self.Q[:] = uhat[:]
      def U2Q():
        self.Q[:] = self.uhat[:]
      def Q2U():
        self.uhat[:] = self.Q[:]
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_DNS 

      def computeSGS(uhat,kc):
        N = (size(uhat)-1)*2
        G = ones(size(uhat))
        G[kc::] = 0
        uhat_filt = G*uhat
        uhat_pad = pad_r(uhat,1)
        uhat_filt_pad = pad_r(uhat_filt,1)
        ureal = myifft(uhat_pad)*sqrt(N)*3./2.
        u_filtreal = myifft(uhat_filt_pad)*sqrt(N)*3./2.
        c = unpad_r(myfft(ureal*ureal)/(3./2.*sqrt(N)),1)
        c_filt = unpad_r(myfft(u_filtreal*u_filtreal)/(3./2.*sqrt(N)),1)
        tauhat = 0.5*(G*c - c_filt)
        return tauhat
      self.computeSGS = computeSGS
      self.tauhatsave[:,0] = self.computeSGS(self.uhat,self.kc)
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.tsave_full = append(self.tsave_full,self.t)

      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved)    
    #=======================================
    ## t-model setup
    #=======================================
    if (turb_model == 1):
      self.Q = zeros((N/2+1),dtype='complex')
      self.Q[:] = uhat[:]
      def U2Q():
        self.Q[:] = self.uhat[:]
      def Q2U():
        self.uhat[:] = self.Q[:]
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_tmodel 
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.tsave_full = append(self.tsave_full,self.t)
      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved)    

    #======================================
    ## First Order Finite Memory Setup
    #=======================================
    if (turb_model == 2):
      self.dt0 = 0.13
      self.Q = zeros(2*(N/2+1),dtype='complex')
      self.w0hat = zeros(size(self.uhat),dtype='complex')
      def U2Q():
        self.Q[0::2] = self.uhat[:]
        self.Q[1::2] = self.w0hat[:]
      def Q2U():
        self.uhat[:] = self.Q[0::2]
        self.w0hat[:] = self.Q[1::2]
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_FM1 
      self.w0Esave = sum(self.w0hat*conj(self.w0hat))
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.w0Esave = append(self.w0Esave,sum(self.w0hat*conj(self.w0hat)))
        self.tsave_full = append(self.tsave_full,self.t)
      self.w0hatsave = zeros( (size(self.w0hat),1),dtype = 'complex')
      self.w0hatsave[:,0] = self.w0hat
      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.w0hat[:]
        self.w0hatsave = append(self.w0hatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved,w0hat=self.w0hatsave)    

    #======================================
    ## Second Order Finite Memory Setup
    #=======================================
    if (turb_model == 3):
      self.dt0 = 0.13
      self.dt1 = 0.07
      self.Q = zeros(3*(N/2+1),dtype='complex')
      self.w0hat = zeros(size(self.uhat),dtype='complex')
      self.w1hat = zeros(size(self.uhat),dtype='complex')
      def U2Q():
        self.Q[0::3] = self.uhat[:]
        self.Q[1::3] = self.w0hat[:]
        self.Q[2::3] = self.w1hat[:]
      def Q2U():
        self.uhat[:]  = self.Q[0::3]
        self.w0hat[:] = self.Q[1::3]
        self.w1hat[:] = self.Q[2::3]
      self.w0Esave = sum(self.w0hat*conj(self.w0hat))
      self.w1Esave = sum(self.w1hat*conj(self.w1hat))
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.w0Esave = append(self.w0Esave,sum(self.w0hat*conj(self.w0hat)))
        self.w1Esave = append(self.w1Esave,sum(self.w1hat*conj(self.w1hat)))
        self.tsave_full = append(self.tsave_full,self.t)
      self.w0hatsave = zeros( (size(self.w0hat),1),dtype = 'complex')
      self.w0hatsave[:,0] = self.w0hat
      self.w1hatsave = zeros( (size(self.w1hat),1),dtype = 'complex')
      self.w1hatsave[:,0] = self.w1hat
      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.w0hat[:]
        self.w0hatsave = append(self.w0hatsave,tmp,1)
        tmp[:,0] = self.w1hat[:]
        self.w1hatsave = append(self.w1hatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved,w0hat=self.w0hatsave,w1hat=self.w1hatsave) 

      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_FM2 
    #======================================
    ## Third Order Finite Memory Setup
    #=======================================
    if (turb_model == 4):
      self.dt0 = 0.01
      self.dt1 = 0.01
      self.dt2 = 0.01
      self.Q = zeros(4*(N/2+1),dtype='complex')
      self.w0hat = zeros(size(self.uhat),dtype='complex')
      self.w1hat = zeros(size(self.uhat),dtype='complex')
      self.w2hat = zeros(size(self.uhat),dtype='complex')
      def U2Q():
        self.Q[0::4] = self.uhat[:]
        self.Q[1::4] = self.w0hat[:]
        self.Q[2::4] = self.w1hat[:]
        self.Q[3::4] = self.w2hat[:]
      def Q2U():
        self.uhat[:]  = self.Q[0::4]
        self.w0hat[:] = self.Q[1::4]
        self.w1hat[:] = self.Q[2::4]
        self.w2hat[:] = self.Q[3::4]
      self.w0Esave = sum(self.w0hat*conj(self.w0hat))
      self.w1Esave = sum(self.w1hat*conj(self.w1hat))
      self.w2Esave = sum(self.w2hat*conj(self.w2hat))
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.w0Esave = append(self.w0Esave,sum(self.w0hat*conj(self.w0hat)))
        self.w1Esave = append(self.w1Esave,sum(self.w1hat*conj(self.w1hat)))
        self.w2Esave = append(self.w2Esave,sum(self.w2hat*conj(self.w2hat)))
        self.tsave_full = append(self.tsave_full,self.t)
      self.w0hatsave = zeros( (size(self.w0hat),1),dtype = 'complex')
      self.w0hatsave[:,0] = self.w0hat
      self.w1hatsave = zeros( (size(self.w1hat),1),dtype = 'complex')
      self.w1hatsave[:,0] = self.w1hat
      self.w2hatsave = zeros( (size(self.w2hat),1),dtype = 'complex')
      self.w2hatsave[:,0] = self.w2hat

      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.w0hat[:]
        self.w0hatsave = append(self.w0hatsave,tmp,1)
        tmp[:,0] = self.w1hat[:]
        self.w1hatsave = append(self.w1hatsave,tmp,1)
        tmp[:,0] = self.w2hat[:]
        self.w2hatsave = append(self.w2hatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved,w0hat=self.w0hatsave,w1hat=self.w1hatsave,w2hat=self.w2hatsave) 

      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_FM3 


    if (turb_model == 5):
      self.dt0 = 0.13
      self.dt1 = 0.07
      self.dt2 = 0.07
      self.Q = zeros(4*(N/2+1),dtype='complex')
      self.w0hat = zeros(size(self.uhat),dtype='complex')
      self.w1hat = zeros(size(self.uhat),dtype='complex')
      self.w2hat = zeros(size(self.uhat),dtype='complex')
      def U2Q():
        self.Q[0::4] = self.uhat[:]
        self.Q[1::4] = self.w0hat[:]
        self.Q[2::4] = self.w1hat[:]
        self.Q[3::4] = self.w2hat[:]
      def Q2U():
        self.uhat[:]  = self.Q[0::4]
        self.w0hat[:] = self.Q[1::4]
        self.w1hat[:] = self.Q[2::4]
        self.w2hat[:] = self.Q[3::4]
      self.w0Esave = sum(self.w0hat*conj(self.w0hat))
      self.w1Esave = sum(self.w1hat*conj(self.w1hat))
      self.w2Esave = sum(self.w2hat*conj(self.w2hat))
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.w0Esave = append(self.w0Esave,sum(self.w0hat*conj(self.w0hat)))
        self.w1Esave = append(self.w1Esave,sum(self.w1hat*conj(self.w1hat)))
        self.w2Esave = append(self.w2Esave,sum(self.w2hat*conj(self.w2hat)))
        self.tsave_full = append(self.tsave_full,self.t)
      ## Make functions objects
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_CM3 

    if (turb_model == 6):
      self.Cs = 0.2
      self.Q = zeros((N/2+1),dtype='complex')
      self.Q[:] = uhat[:]
      def U2Q():
        self.Q[:] = self.uhat[:]
      def Q2U():
        self.uhat[:] = self.Q[:]
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_tmodel 
      def saveHook1():
        self.Esave = append(self.Esave,0.5*sum(self.uhat*conj(self.uhat)) )
        self.Dsave = append(self.Dsave,1./dt*(self.Esave[-1] - self.Esave[-2]))
        self.Esave_resolved = append(self.Esave_resolved,0.5*sum(self.uhat[0:self.kc]*conj(self.uhat[0:self.kc])) )
        self.Dsave_resolved = append(self.Dsave_resolved,1./dt*(self.Esave_resolved[-1] - self.Esave_resolved[-2]))
        self.tsave_full = append(self.tsave_full,self.t)
      def saveHook2():
        tmp = zeros((size(self.uhat),1),dtype = 'complex')
        tmp[:,0] = self.uhat[:]
        self.uhatsave = append(self.uhatsave,tmp,1)
        tmp[:,0] = self.tauhat[:]
        self.tauhatsave =  append(self.tauhatsave,tmp,1)
        tmp = zeros((size(self.u),1),dtype='complex')
        tmp[:,0] = self.u
        self.usave = append(self.usave,tmp,1)
        self.tsave = append(self.tsave,self.t)
      def saveHookFinal():
        np.savez('Solution/stats',uhat=self.uhatsave,t=self.tsave,tf=self.tsave_full,k = k,x=x,u=self.usave,tauhat=self.tauhatsave,Energy=self.Esave,\
         Energy_resolved=self.Esave_resolved,Dissipation=self.Dsave,Dissipation_resolved=self.Dsave_resolved)    
      ## Make functions objects
      self.U2Q = U2Q
      self.Q2U = Q2U
      self.computeRHS = RHS_Smagorinsky 


    self.RHS = zeros(size(self.Q),dtype='complex')
    self.saveHook1 = saveHook1
    self.saveHook2 = saveHook2
    self.saveHookFinal = saveHookFinal

uhat[-1] = 0
main = variables(turb_model,N,k,uhat,u,t,kc,dt,nu) 



ion()
itera = 0
w0Esave = zeros(1)


while (main.t <= et):
  main.U2Q()
  advanceQ_RK4(main)
  main.t += dt
  print(main.t)
  main.saveHook1()
  if (itera%10 == 0):
    main.saveHook2()
    if (live_plot == 1):
      clf()
      plot(x,u)
      main.u = myifft(main.uhat)*sqrt(N)
      plot(x,main.u)
      pause(0.00000001)
  itera += 1

main.saveHookFinal()
