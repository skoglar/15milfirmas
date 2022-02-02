#!/usr/bin/env python

import html
import time

import pymongo
from pymongo import MongoClient

from bs4 import BeautifulSoup
import requests

import os
import configparser

class Iniciativa:
    def __init__(self, nro, titulo, apoyos, link, diff):
        self.nro = nro
        self.titulo = titulo
        self.apoyo = apoyos
        self.link = link
        self.diff = 0

    def to_dict(self):
            return {
                'nro': self.nro,
                'titulo': self.titulo,
                'apoyo': self.apoyo,
                'link': self.link,
                'diff': self.diff
            }
    def to_list(self):
            return [self.nro, self.apoyo, self.titulo, self.link]

data = {}
url_iniciativas = "https://plataforma.chileconvencion.cl/m/iniciativa_popular/"
res = requests.get(url_iniciativas)

soup_iniciativas = BeautifulSoup(res.text, 'html.parser')
iniciativas = soup_iniciativas.select('.card.iniciativa')

for iniciativa in iniciativas:
    #Propiedades que nos interesan
    nro = iniciativa.find('a')['href'].replace('o/', '')
    titulo = iniciativa.find('h1').text.upper()
    apoyos = iniciativa.attrs["data-apoyos"]
    link = 'https://plataforma.chileconvencion.cl/m/iniciativa_popular/detalle?id=' + nro

    #put them in a dictionary
    data[nro] = Iniciativa(
        nro,
        titulo,
        int(apoyos),
        link,
        0
    )

orden = sorted(data, key=lambda nro: int(data[nro].apoyo))
orden.reverse()


config = configparser.ConfigParser()
configpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", ".db.ini"))
config.read(configpath)
DB_URI = config['PROD']['DB_URI']

client = MongoClient(DB_URI)
db = client.quincemilfirmas
admitidas = db.admitidas
siguientes = db.siguientes

i = 0
nro = orden[i]
iniciativa = data[nro]

d = []
while iniciativa.apoyo >= 15000:
    titulo = iniciativa.titulo.encode('iso-8859-1', errors='ignore').decode('iso-8859-1', errors='ignore')
    
    b = bytearray()
    b.extend(map(ord, titulo))
    #God damn double quotes man
    if(147 in b):
        b.pop(b.index(147))
    if(148 in b):
        b.pop(b.index(148))
    while(b'\x96' in b):
        b.pop(b.index(b'\x96'))
    iniciativa.titulo = b.decode('iso-8859-1')

    
    #Mongo
    query = {"nro" : iniciativa.nro}
    found = admitidas.find_one(query)
    found_sig = siguientes.find_one(query)
    if(found):
        if(found_sig):
            siguientes.delete_one(query)
        diff = iniciativa.apoyo - found['apoyo']
        update = { "$set" : { "apoyo" : iniciativa.apoyo, "diff": diff }}
        admitidas.update_one(query, update)
    else:
        admitidas.insert_one(iniciativa.to_dict())
    
    try:
        i += 1
        nro = orden[i]
        iniciativa = data[nro]
    except Exception as e:
        iniciativa = Iniciativa(0,0,-1,0,0)


contador = 10
for x in range(contador):
    nro = orden[i+x]
    iniciativa = data[nro]

    query = {"nro" : iniciativa.nro}
    found = siguientes.find_one(query)
    found_admit = admitidas.find_one(query)
    if(found):
        if(found_admit):
            siguientes.delete_one(query)
        else:
            diff = iniciativa.apoyo - found['apoyo']
            update = { "$set" : { "apoyo" : iniciativa.apoyo, "diff": diff }}
            siguientes.update_one(query, update)
    else:
        siguientes.insert_one(iniciativa.to_dict())

updatelog = "/home/sigma/15milfirmas/updated.txt"
with open(updatelog, 'w') as f:
    f.write(time.strftime("%d-%m-%Y — %H:%M:%S"))
