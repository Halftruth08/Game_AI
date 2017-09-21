# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 11:53:50 2017

@author: Aaron
"""
from tkinter import *

#==============================================================================
# root = Tk()
# var = StringVar()
# var.set('hello')
# 
# l = Label(root, textvariable = var)
# l.pack()
# 
# t = Entry(root, textvariable = var)
# t.pack()
# 
# root.mainloop()
#==============================================================================
# from Tkinter import *
# 
# master = Tk()
# 
# v = IntVar()
# 
# Radiobutton(master, text="One", variable=v, value=1).pack(anchor=W)
# Radiobutton(master, text="Two", variable=v, value=2).pack(anchor=W)
# 
# mainloop()
#==============================================================================
#==============================================================================

n=15#length of dictionary
from tkinter import *
import time
fields = 'Last Name', 'First Name', 'Job', 'Country'
prompt="Which word below is most related to"
def fetch(entries):
   for entry in entries:
      field = entry[0]
      text  = entry[1].get()
      print('%s: "%s"' % (field, text)) 
def wrout(keyw,dnry,ii):
    print('%s: "%s"' % (keyw, dnry[ii]))

def makeform(root, fields, keyw):
   entries = []
   title=Frame(root)
   tlab=Label(title,text=keyw)
   
   title.pack(side=TOP, fill=X, padx=5, pady=5)
   tlab.pack(side=TOP, fill=X)
   entries.append((title,tlab))
#==============================================================================
#    for field in fields:
#       row = Frame(root)
#       lab = Label(row, width=15, text=field, anchor='w')
#       ent = Entry(row)
#       row.pack(side=TOP, fill=X, padx=5, pady=5)
#       lab.pack(side=LEFT)
#       ent.pack(side=RIGHT, expand=YES, fill=X)
#       entries.append((field, ent))
#==============================================================================
   
   return entries

if __name__ == '__main__':
   root = Tk()
   dictionary=["apple","cook","star","ocean"]#,"tool","shower","year","anchor","north"
            #,"mouse","song","house","diamond","orange","steam"]
   #dictionary = args #!!figure out how to pass in dictionary
   Dnry={}
   dnry={}
   dnry2={}
   ordered={}
   indicies={}
   for i in range(len(dictionary)):
       Dnry[i]=dictionary[i]
       dnry[i]=dictionary[i]
   
   for i in range(len(dictionary)):
       #keyw=dictionary[i]
       #dnry=Dnry#pass in original word list
       for i5 in Dnry:
           dnry[i5]=Dnry[i5]
       keyw=dnry.pop(i)
       ordered[keyw]=[]
       indicies[i]=[]
       for i3 in dnry:
           dnry2[i3]=dnry[i3]
       
       varl={}
       k=0
       buttons={}
       for ii in dnry:
           varl[ii]=StringVar()
       for ii in varl:
           varl[ii].set(dnry[ii])
        
       title=Frame(root)
       pt=Label(title,text=prompt)
       tlab=Label(title,text=keyw)
   
       title.pack(side=TOP, fill=X, padx=5, pady=5)
       tlab.pack(side=TOP, fill=X)
       #root.bind('<Return>', (lambda event, e=ents: fetch(e)))
       k=0
       row = [Frame(root)]
       row[0].pack(side=TOP, fill=X, padx=5, pady=5)
       v=IntVar()
       for ii in dnry:
           #buttons[ii]=Button(row, textvariable=varl[ii],
            #                     command=(print(varl[ii].get()))
           buttons[ii]=Radiobutton(row[len(row)-1], text=dnry[ii], variable=v, value=ii)#.pack(anchor=W)
           k=k+1
           if k==5:
               k=0
               row.append(Frame(root))
               row[len(row)-1].pack(side=TOP, fill=X, padx=5, pady=5)
               buttons[ii].pack(side=LEFT, padx=5, pady=5)
           else:
               buttons[ii].pack(side=LEFT, padx=5, pady=5)
       def press():
           time.sleep(0.1)
           ordered[keyw].append(dnry2.pop(v.get()))
           indicies[i].append(v.get())
           #print(dnry2)
           buttons[v.get()].destroy()
           if len(dnry2)==1:
               for i4 in dnry2:
                   ordered[keyw].append(dnry2[i4])
                   indicies[i].append(i4)
                   buttons[i4].destroy()
               title.destroy()
               tlab.destroy()
               for i6 in row: 
                   i6.destroy()
               root.quit()
               #print(indicies)
               
           
       
       #read=StringVar(value=dnry[v])
       #b1 = Button(root, text='Show',
       #       command=(lambda e=ents: fetch(e)))
      # b1.pack(side=LEFT, padx=5, pady=5)
       #b2 = Button(root, text='Quit', command=root.configure())
       #b2.pack(side=LEFT, padx=5, pady=5)
       #Label(root,textvariable=v).pack(side=LEFT, padx=5, pady=5)
       root.bind('<ButtonRelease>',(lambda event, e=v.get(): press()))
       root.mainloop()
       #root.after(cancel)
   print(indicies)
