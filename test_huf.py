# -*- coding: utf-8 -*-
import operator
import struct
import os
import codecs

class HuffmanNode:
    def __init__(self, s=0, f=0, lp = None, rp = None, l=None, r=None, c = ''):
        self.symbol = s ## symbol
        self.frequency = f ## ilosc wystapien
        self.left_parent = lp ## mamy rodzica, jesli rodzic.left == my to my.left_parent == rodzic
        self.right_parent = rp ## jw
        self.left = l ## lewy potome
        self.right = r ## prawy potomek
        self.code = c ## slowo kodowe

    def __str__(self): ## wypisanie obiektu
        return str(self.symbol) + ' ' + str(self.frequency)

    def __repr__(self): ## wypisywanie iteracyjne
        return str(self.symbol) + ' ' + str(self.frequency) + ' ' + str(self.code)

def read_bytes(file_name, d): ## odczyt z pliku
    with open(file_name, 'rb') as f:
        byte = f.read(1)
        while byte != b"":
            try:
                if ord(byte) != 65279:
                    if ord(byte) in d.keys():
                        d[ord(byte)] += 1
                    else:
                        d[ord(byte)] = 1
            except TypeError:
                break
            byte = f.read(1)

def sort_model(dir): ## zwraca posortowana tablice, rzutuje slownik na tablice
    return sorted(dir.items(), key=operator.itemgetter(1))

def to_class(tab): ## rzutuje posortowana tablice na klase
    new_tab = []
    for t in tab:
        new_tab.append(HuffmanNode(t[0], t[1]))

    return new_tab

def write_frequencies(tab, file_name): ## zapis tablicy klas do pliku
    myFile = open(file_name, 'w')
    myFile.write(str(len(tab))+'\n')
    for t in tab:
        myFile.write(str(t.symbol)+':'+str(t.frequency)+'\n')


def write_model(file_name, tab):
    with open(file_name, 'w') as f:
        for t in tab:
            f.write(str(t[0]) + ':' + str(t[1]) + '\n')

def read_model(file_name):
    tab = []
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for l in lines:
            tab.append([int(l.split(':')[0]), l.split(':')[1][:-1]])

def generate_huffman_tree(tab):
    temp_array = tab[:]
    new_array = []

    iter = 0
    while len(temp_array) > 1:
        new = HuffmanNode('%d#' % iter, temp_array[0].frequency + temp_array[1].frequency,
                            l=temp_array[0], r=temp_array[1])
        temp_array[0].left_parent = new ## ustawienie parenta
        temp_array[1].right_parent = new  ## ustawienie parenta
        new_array.append(new)
        temp_array.pop(0) ## wywalamy 0 element
        temp_array.pop(0) ## znowu, czyli jakby pierwszy
        temp_array.append(new) ## dodajemy nowo utworzony

        temp_array.sort(key=lambda x: x.frequency, reverse=False) ## sortowanie pod wzgledem frequency
        iter += 1

    return new_array

def describe(tab):
    for t in tab:

        if t.parent.left == t:
            print(t.symbol, 'lewy syn' ,t.parent, t.parent.parent)
        else:
            print(t.symbol, 'prawy syn' ,t.parent, t.parent.parent)

def walk_tree(array):
    for a in array:
        current = a
        code = ''
        while current.parent != None:
            p = a.parent

            if p.left == a:
                code += '0'
                print('l')
            else:
                code += '1'
                print('r')

            current = current.parent
            #print(code)
        a.code = swap(code)

def walk_tree2(array):
    for a in array:
        current = a
        code = ''

        while current.left_parent != None or current.right_parent != None:
            if current.left_parent:
                code += '0'
                current = current.left_parent
            else:
                code += '1'
                current = current.right_parent
        a.code = code[::-1] ## odwracamy kod

def check(tab):
    for i in range(len(tab)):
        for j in range(len(tab)):
            if i == j:
                continue
            if tab[j].code.find(tab[i].code) == 0:
                print(tab[j].code, tab[i].code)
                print('blad')

def encode_to_binary(file_name, model_array): ## notka: tlumaczenie znakow na 0,1 dziala
    code = ''
    with open(file_name, 'rb') as f: ## zaspisuje kod w postaci stringa z zerami i jedynkami
        zakodowane = open('zakodowane', 'wb')
        byte = f.read(1)
        while byte != b"":
            for m in model_array:
                if ord(byte) == m[0]:
                    code += m[1]
                    break
            if len(code) >=8:
                temp_code = code[:8]
                code = code[8:]
                zakodowane.write(struct.pack('B', int(temp_code, 2)))

            byte = f.read(1)

        lenght = len(code)
        if lenght != 0:
            code = '0'*(8-lenght) + code
            zakodowane.write(struct.pack('B', int(code,2)))
        zakodowane.close()

        return 8-lenght

def decode_from_binary(tab, amount_of_zeros, minimal, amount_of_words):
    ############## ODCZYTANIE Z BINARNEGO DO STRINGA 0,1##########
    decoded_string = ''
    iter = 0
    with open('zakodowane', 'rb') as f:
        odkodowane = open('odkodowane', 'wb')
        pom_code = ''
        quit = False

        byte = f.read(1)
        while byte != b'':
            decoded_string += '{0:08b}'.format(ord(byte))
            byte = f.read(1)

            while len(decoded_string) >= minimal:
                iter += 1
                if pom_code == '':
                    pom_code = decoded_string[:minimal]
                    decoded_string = decoded_string[minimal:]
                else:
                    pom_code += decoded_string[0]
                    decoded_string = decoded_string[1:]

                if iter == amount_of_words:
                    pom_code = decoded_string[8-amount_of_zeros:]
                    quit = True

                for t in tab:
                    if pom_code == t[1]:
                        if t[0] <= 255:
                            odkodowane.write(struct.pack('B', int(bin(t[0])[2:],2)))
                        else:
                            odkodowane.write(struct.pack('h', int(bin(t[0])[2:],2)))
                        pom_code = ''
            if quit:
                break

    odkodowane.close()

def make_array(tab): ## zmienia tablice obiektow na tablice
    arr = []
    for t in tab:
        arr.append([t.symbol, t.code])

    return arr

def search_minimal(array):
    return len(array[-1][1])

def calculate_words(array):
    sum = 0
    for a in array:
        sum += a.frequency

    print(sum)

if __name__ == '__main__':
    file = 'tekst.txt'
    dir = {}
    print(file)
    read_bytes(file, dir) ## zapisuje do slownika symbol : frequency
    sorted_dir = sort_model(dir) ## sortuje slownik i rzutuje na tablice
    class_tab = to_class(sorted_dir) ## rzutuje tablice na tablice klas
    write_frequencies(class_tab, 'frequency.txt') ## zapis modelu do pliku
    arr = generate_huffman_tree(class_tab) ## generujemy drzewo huffmana
    walk_tree2(class_tab) ## przechodzimy od lisci do korzenia i tworzymy slowa kodowe
    #check(class_tab) ## funckaj sprawdzajaca poprawne zakodowanie
    ilosc_slow = calculate_words(class_tab)
    model_array = make_array(class_tab)
    write_model('model.txt', model_array)
    read_model('model.txt')
    min = search_minimal(model_array)

    zeros = encode_to_binary(file, model_array)
    print('decoding')
    dec_code = decode_from_binary(model_array, zeros, min, ilosc_slow)
