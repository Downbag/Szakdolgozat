# -*- coding: utf-8 -*-
"""multprocalg.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1USKGOYa8txzvNBb9XF3vosd50d2CyV_i
"""

import sys
import random as rnd
from multiprocessing import Process, Queue
from datetime import datetime
import pyopencl as cl
import numpy as np

sys.setrecursionlimit(5000)

class DiederElem:
  global static_csoport_rendje
  global static_n

  def __init__(self, ap, bp):
    static_csoport_rendje=8
    static_n=3
    self.aPow=ap
    self.bPow=bp


  def inverz(self):
    if self.bPow==1:
      obj=DiederElem(self.aPow, self.bPow)
      return obj
    else:
      obj=DiederElem((pow(2,static_n-1)-self.aPow)%(static_csoport_rendje/2), 0)
      return obj


  def __mul__(self, other):
    a1=np.array([self.aPow], dtype=np.int32)
    b1=np.array([self.bPow], dtype=np.int32)
    a2=np.array([other.aPow], dtype=np.int32)
    b2=np.array([other.bPow], dtype=np.int32)

    apowResult= np.empty(1, dtype=np.int32)
    bpowResult= np.empty(1, dtype=np.int32)

    ctx=cl.create_some_context()
    queue=cl.CommandQueue(ctx)

    mf=cl.mem_flags
    a1Buff=cl.Buffer(ctx, mf.READ_ONLY|mf.COPY_HOST_PTR, hostbuf=a1)
    b1Buff=cl.Buffer(ctx, mf.READ_ONLY|mf.COPY_HOST_PTR, hostbuf=b1)
    a2Buff=cl.Buffer(ctx, mf.READ_ONLY|mf.COPY_HOST_PTR, hostbuf=a2)
    b2Buff=cl.Buffer(ctx, mf.READ_ONLY|mf.COPY_HOST_PTR, hostbuf=b2)
    apowResBuff=cl.Buffer(ctx, mf.WRITE_ONLY, apowResult.nbytes)
    bpowResBuff=cl.Buffer(ctx, mf.WRITE_ONLY, bpowResult.nbytes)

    kernel_code="""
    __kernel void multiplyDieder
    (
      __global const int* a1,
      __global const int* b1,
      __global const int* a2,
      __global const int* b2,
      __global int* aResult,
      __global int* bResult,
      const int static_n
    )
    {
      int i=get_global_id(0);
      int mod=1<<(static_n-1)
      
      int apow;
      if (b1[i]==1) 
      {
        apow=a1[i]+mod-a2[i];
      }
      else
      {
        apow=a1[i]+a2[i];
      }
      
      int bpow;
      if ((b1[i]==0 && b2[i]==1) || (b1[i]==1 && b2[i]==0))
      {
        bpow=1;
      }
      else
      {
        bpow=0;
      }
      
      apow=apow%mod;
      
      aResult[i]=apow;
      bResult[i]=bpow;
    }
    """

    program=cl.Program(ctx, kernel_code).build()
    program.multiplyDieder(queue, (1,), None, a1Buff, b1Buff, a2Buff, b2Buff, apowResBuff, bpowResBuff, np.int32(static_n))
    cl.enqueue_copy(queue, apowResult, apowResBuff)
    cl.enqueue_copy(queue, bpowResult, bpowResBuff)

    obj=DiederElem(apowResult[0],bpowResult[0])
    return obj

  def __str__(self):
    if(self.aPow==0 and self.bPow==0): return "1"
    if(self.aPow==0 and self.bPow==1): return "b"
    if(self.aPow==1 and self.bPow==0): return "a"
    if(self.aPow==1 and self.bPow==1): return "ab"
    if(self.bPow==0): return "a^"+str(self.aPow)
    return "a^"+str(self.aPow)+"b"

  def __eq__(self, other):
    return self.aPow == other.aPow and self.bPow == other.bPow

class DiederCsoport:
  #elemek=[]
  def __init__(self, db):
    self.elemek=[]
    for i in range(0,int(db/2)):

      self.elemek.append(DiederElem(i,0))
      self.elemek.append(DiederElem(i,1))

  #elemek=[]
  #indexelés még kell

class F2DiederElem:

  def __init__(self, reszhalmaz):
    self.reszhalmaz=list()
    for elem in reszhalmaz:
      self.reszhalmaz.append(elem)

  def __eq__(self,other):
    for elemx in self.reszhalmaz:
      init=False
      for elemy in other.reszhalmaz:
        if(elemx.__eq__(elemy)):
          init=True
      if not init:
        return False
    return True

  def __ne__(self,other):
    return not self.__eq__(other)


  def isItIn(self, elem):
    for elemin in self.reszhalmaz:
      if(elemin==elem):
        return True
    return False

  def where(self, elem):
    for index in range(0,len(self.reszhalmaz)):
      if self.reszhalmaz[index]==elem:
        return index




  def __mul__(self, other):

    #temp = [DiederElem(elemx.aPow, elemx.bPow) * DiederElem(elemy.aPow, elemy.bPow) for elemx in self.reszhalmaz for elemy in other.reszhalmaz]
    temp=[]
    for elemx in self.reszhalmaz:
      for elemy in other.reszhalmaz:
        temp.append(elemy*elemx)
    result=[]
    for szorzat in temp:
      tempelem=F2DiederElem(result)
      if tempelem.isItIn(szorzat):
        #print(tempelem.where(szorzat))
        #print(szorzat)
        #print(tempelem)
        #input()
        result=[item for item in result if item!=szorzat]
        #result.pop(tempelem.where(szorzat))
      else:
        result.append(szorzat)

    #print(F2DiederElem(result))
    return F2DiederElem(result)


  def inverz(self):
    osszeg=F2DiederElem([DiederElem(0,0)])
    szorzat=self
    while True:
      osszeg=osszeg*szorzat
      szorzat*=szorzat
      if len(szorzat.reszhalmaz)==1 and str(szorzat).__contains__('1'):
        return osszeg
      if len(szorzat.reszhalmaz)==0: return F2DiederElem([])

  def __str__(self):
    if len(self.reszhalmaz)==0:
      return '0'
    sb=str(self.reszhalmaz[0])
    for i in range(1,len(self.reszhalmaz)):
      sb=sb+' + '+str(self.reszhalmaz[i])
    return sb

class F2D2nCsoportElem:
  def __init__(self):
    self.poziciok=[]
    self.poziciok.append(0)

  def jelenlegiElem(self):
    diederek=[]
    csoport=DiederCsoport(static_csoport_rendje)
    for i in self.poziciok:
      diederek.append(csoport.elemek[i])
    return F2DiederElem(diederek)


  def lepes(self):
    for i in range(len(self.poziciok)-1,-1, -1):
      if self.poziciok[i]<static_csoport_rendje-1:
        j=1
        problema_fent_all=True
        while problema_fent_all:
          if (self.poziciok.__contains__(self.poziciok[i]+j)): j=j+1
          else: problema_fent_all=False
        if self.poziciok[i] + j < static_csoport_rendje:
          self.poziciok[i]=self.poziciok[i]+j
        else:
          i=i+1
          continue
        return True
      elif (i==0 and len(self.poziciok)<static_csoport_rendje):
        self.poziciok.append(0); self.poziciok.append(0)
        for j in range(len(self.poziciok)):
          self.poziciok[j]=j
        if len(self.poziciok)>static_csoport_rendje: break
        return True
      else:
        self.poziciok[i]=-1
        j=0
        problema_fent_all=True
        while problema_fent_all:
          if self.poziciok.__contains__(j): j=j-1
          elif j>static_csoport_rendje: break
          else: problema_fent_all=False
        self.poziciok[i]=j
    return False

  def kovetkezoElem(self):
    return self.lepes()

  def __str__(self):
    return str(self.jelenlegiElem)


path="path"
delem=DiederElem(0,0)
static_base_elem=F2DiederElem([DiederElem(0,0)])
static_csoport_rendje=1024
static_n=10
csoport=DiederCsoport(static_csoport_rendje)
maxered=8 #2:8; 3:16; 4:32; 4:64; 5:128; 6:256; 7:512; 8?:1024


def kommutator(x,y):
  return (x.inverz()*y.inverz()*x*y)

def reszfeloldas(lista,ered):
  f2diederek=[]
  for i in range(0,int(len(lista))-1,2):
    f2diederek.append(kommutator(lista[i],lista[i+1]))
    #print(str(f2diederek))
    #input()
  if len(f2diederek)==1:
    if str(f2diederek)=='1':
      return ered
    return ered+1

  return reszfeloldas(f2diederek, ered+1)

def randomElem(q):
  diederek=[]
  hossz=int(rnd.randint(1,int(static_csoport_rendje/2))*2-1)
  i=0
  while i<hossz:
    temp=rnd.choice(csoport.elemek)
    if temp not in diederek:
      diederek.append(temp)
      i=i+1

  q.put(F2DiederElem(diederek))


def reszfeloldas2(x,y,z,ered):
  iz=kommutator(x,y)
  iy=kommutator(x,z)
  ix=kommutator(y,z)
  if(iz==static_base_elem and iy==static_base_elem and ix==static_base_elem):
    return ered+1
  return reszfeloldas2(ix,iy,iz,ered+1)

def reszfeloldas3(tomb, ered):
  temp=[]
  temp.append(kommutator(tomb[1],tomb[2]))
  temp.append(kommutator(tomb[0],tomb[2]))
  temp.append(kommutator(tomb[0],tomb[1]))
  szamlalo=0
  for elem in temp:
    if elem==static_base_elem:
      szamlalo+=1
  if szamlalo==3:
    return ered+1
  else:
    return reszfeloldas3(temp,ered+1)

def modszer1(queue):
  q=Queue()
  processes=[]
  for _ in range(3):
    processes.append(Process(target=randomElem, args=(q,)))
  for process in processes:
    process.start()
  elemek=[]
  for _ in range(len(processes)):
    elemek.append(q.get())
  for process in processes:
    process.join()
  queue.put(reszfeloldas3(elemek,0))

def modszer2():
  ered=0
  x=F2D2nCsoportElem()
  y=F2D2nCsoportElem()
  z=F2D2nCsoportElem()
  while ered<maxered:
    ered=reszfeloldas2(x.jelenlegiElem(),y.jelenlegiElem(),z.jelenlegiElem(),0)
    #print(f"{str(x.jelenlegiElem())} és {str(y.jelenlegiElem())} és {str(z.jelenlegiElem())} feloldási hossza: {ered}")
    if not z.kovetkezoElem():
      z=F2D2nCsoportElem()
      if not y.kovetkezoElem():
        y=F2D2nCsoportElem()
        if not x.kovetkezoElem():
          return False
  return True

def modszer3():
  f2diederek=[]
  for i in range(0,pow(2,maxered-1)):
    a=randomElem()
    b=randomElem()
    if kommutator(a,b)!=static_base_elem:
      f2diederek.append(kommutator(a,b))
    else: i=i-1
  ered=reszfeloldas(f2diederek,1)
  return ered


if __name__=="__main__":
  ered=0
  szalszam=100
  if input("Akarja a 3-as random elem generátort használni? (igen/nem) ")=="igen":
    szamlal=1
    while ered<maxered:
      start=datetime.now()

      q = Queue()
      processes = []
      for _ in range(szalszam):
        processes.append(Process(target=modszer1, args=(q,)))
      for process in processes:
        process.start()
      eredek = []
      for _ in range(len(processes)):
        eredek.append(q.get())
      for process in processes:
        process.join()

      ered=max(eredek)
      print("Az eredmény jelenleg: " + str(ered))
      print("Futási idő: " + str(datetime.now() - start))
      szamlal=szamlal+1
  print("Az eredmény: "+str(ered))

  if input("Akarja a teljes csoport 3-as feloldását? (igen/nem)")=="igen":
    if(modszer2()):
      print("A maximális várható eredmény megkapható")
    else:
      print("A maximális várható eredmény nem kapható meg")

  szamlalo=1
  while ered!=maxered:
    ered=modszer3()
    print(str(szamlalo)+". részfeloldás eredménye: "+str(ered))
    szamlalo=szamlalo+1
  if(ered==maxered):
    print("Sikeres lefutás, az eredmény a maximális várható eredmény")
  else:
    print("Sikeres lefutás, de az eredmény nem a maxinális várható eredmény")