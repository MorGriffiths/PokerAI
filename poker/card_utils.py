import numpy as np
import copy
import hand_recognition.datatypes as dt

def convert_numpy_to_rust(vectors):
    cards = []
    for vector in vectors:
        np_suit = np.floor(np.divide(vector,13)).astype(int)
        rank = np.subtract(vector,np.multiply(np_suit,13))
        rank = np.add(rank,2)
        suit = dt.Globals.SUIT_DICT[np_suit]
        cards.append([rank,suit])
    return cards

def convert_numpy_to_2d(vectors):
    cards = []
    for vector in vectors:
        np_suit = np.floor(np.divide(vector,13)).astype(int)
        rank = np.subtract(vector,np.multiply(np_suit,13))
        rank = np.add(rank,2)
        cards.append([rank,np_suit])
    return cards

def cards_to_planes(cards):
    new_cards = copy.deepcopy(cards)
    plane = np.ndarray((len(new_cards),2))
    for i,card in enumerate(new_cards):
        plane[i][0] = card[0]
        plane[i][1] = card[1]
    return plane
    
#2d
def suits_to_str(cards):
    new_cards = copy.deepcopy(cards)
    for card in new_cards:
        card[1] = dt.Globals.SUIT_DICT[card[1]]
    return new_cards

#2d
def suits_to_num(cards):
    new_cards = copy.deepcopy(cards)
    for card in new_cards:
        card[1] = dt.Globals.REVERSE_SUIT_DICT[card[1]]
    return new_cards

#takes 2d vector of numbers, turns into (1,4) matrix of numbers between 0-51
#returns np.array
def to_52_vector(vector):
    rank = np.transpose(vector)[:][0]
    suit = np.transpose(vector)[1][:]
    rank = np.subtract(rank,2)
    return np.add(rank,np.multiply(suit,13))

#takes (1,4) vector of numbers between 0-51 and turns into 2d vector of numbers between 0-13 and 1-4
#returns list
def to_2d(vector):
    if type(vector) == np.ndarray or type(vector) == list:
    #    print()
        suit = np.floor(np.divide(vector,13))
        suit = suit.astype(int)
        rank = np.subtract(vector,np.multiply(suit,13))
        rank = np.add(rank,2)
        combined = np.concatenate([rank,suit])
        length = int(len(combined) / 2)
        hand_length = len(vector)
        hand = [[combined[x],combined[x+hand_length]] for x in range(length)]
    else:
        suit = np.floor(np.divide(vector,13))
        suit = suit.astype(int)
        rank = np.subtract(vector,np.multiply(suit,13))
        rank = np.add(rank,2)
        hand = [[rank,suit]]
        print(hand,'hand')
    #print(hand,'combined')
    return hand
    
#takes (1,4) numpy vector of numbers between 0-51 and returns 1 hot encoded vector
#returns list of numpy vectors
def to_1hot(vect):
    hand = []
    for card in vect:
        vector = np.zeros(52)
        vector[card] = 1
        hand.append(vector)
    return hand

#takes (1,52) 1 hot encoded vector and makes it (1,53)
#returns np.array
def hot_pad(vector):
    temp = np.copy(vector)
    padding = np.reshape(np.zeros(len(temp)),(len(temp),1))
    temp = np.hstack((temp,padding))
    return temp

#Takes 1hot encoded vector
#returns (1,4) 52 encoded vector
def from_1hot(vect):
    new_hand = []
    for card in vect:
        #print(card)
        i, = np.where(card == 1)
        #print(i)
        new_hand.append(i)
    return new_hand

#Takes 1 hot encoded padded vector and returns 1 hot encoded vector
def remove_padding(vect):
    if len(vect[0]) != 53:
        raise ValueError("1 Hot vector must be padded")
    new_hand = []
    for card in vect:
        new_hand.append(card[:-1])
    return new_hand
    
def convert_str_to_1hotpad(hand):
    vector1 = suits_to_num(hand)
    vector2 = to_52_vector(vector1)
    vector3 = to_1hot(vector2)
    vector4 = hot_pad(vector3)
    return vector4

def convert_1hotpad_to_str(hand):
    vector_unpad = remove_padding(hand)
    vector_unhot = from_1hot(vector_unpad)
    vector_un1d = to_2d(vector_unhot)
    vector_unnum = suits_to_str(vector_un1d)
    return vector_unnum

def convert_52_to_str(hand):
    vector_un1d = to_2d(hand)
    vector_unnum = suits_to_str(vector_un1d)
    return vector_unnum