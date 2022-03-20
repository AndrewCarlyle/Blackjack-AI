#This file contains the AI portion of my final project

import random

#List of all opposing players within the game and their cards. '?' = face down card
plrList = []

qEstimates = {}

gamma = 0.9
alpha = 0.2

for i in range(2, 32):
    qEstimates[i] = {}

#Representation of the deck as the AI sees it. (It may know that there are some missing cards, but not which cards)
deck = []

def resetDeck():
    for i in range(1,14):
        for x in range(4):
            if i > 10:
                deck.append(10)
            else:
                deck.append(i)

def getMax(total, predVal):
    if not predVal in qEstimates[total]:
        return 0
    elif total > 21:
        return qEstimates[total][predVal][1]
    elif qEstimates[total][predVal][0] > qEstimates[total][predVal][1]:
        return qEstimates[total][predVal][0]
    else:
        return qEstimates[total][predVal][1]

def bestDecision():
    currSums = getCurrSums()

    #Unknown card prediction - an estimate of the value of the face down card
    ucPred = calculateUnknownCard()

    roundedPred = round(ucPred * 2) / 2

    if not roundedPred in qEstimates[currSums[0]]:
        if currSums[0] > 16:
            return False
        else:
            return True
    elif qEstimates[currSums[0]][roundedPred][0] > qEstimates[currSums[0]][roundedPred][1]:
        return True
    else:
        return False

#This function returns the decision to either hit (true) or stand (false)
def makeDecision():
    currSums = getCurrSums()

    #Unknown card prediction - an estimate of the value of the face down card
    ucPred = calculateUnknownCard()

    roundedPred = round(ucPred * 2) / 2

    #Setting the inital Q-values for this state
    if not roundedPred in qEstimates[currSums[0]]:
        if currSums[0] < 11:
            qEstimates[currSums[0]][roundedPred] = [1,0]
        elif currSums[0] > 21:
            qEstimates[currSums[0]][roundedPred] = [-1,0]
        else:
            qEstimates[currSums[0]][roundedPred] = [0,0]

    exploreChance = random.randint(1,10)

    predTotalAfterHit = round(currSums[0] + ucPred)

    if exploreChance == 1:
        qEstimates[currSums[0]][roundedPred][0] += alpha * (0 + gamma * getMax(predTotalAfterHit, roundedPred) - qEstimates[currSums[0]][roundedPred][0])
        return True
    elif exploreChance == 2:
        qEstimates[currSums[0]][roundedPred][1] += alpha * (0 + gamma * getMax(currSums[0], roundedPred) - qEstimates[currSums[0]][roundedPred][1])
        return False
    elif qEstimates[currSums[0]][roundedPred][0] <= qEstimates[currSums[0]][roundedPred][1]:
        qEstimates[currSums[0]][roundedPred][1] += alpha * (0 + gamma * getMax(currSums[0], roundedPred) - qEstimates[currSums[0]][roundedPred][1])
        return False
    else:
        qEstimates[currSums[0]][roundedPred][0] += alpha * (0 + gamma * getMax(predTotalAfterHit, roundedPred) - qEstimates[currSums[0]][roundedPred][0])
        return True

#Updating the Q-value at the end of a round
def updateQValue(state, reward, action):
    ucPred = round(calculateUnknownCard() * 2) / 2

    if not ucPred in qEstimates[state]:
        qEstimates[state][ucPred] = [0, 0]

    if action == 1:
        qEstimates[state][ucPred][action] += alpha * (reward + gamma * qEstimates[state][ucPred][action] - qEstimates[state][ucPred][action])
    else:    
        qEstimates[state][ucPred][action] += alpha * (reward + gamma * getMax(state, ucPred) - qEstimates[state][ucPred][action])

def startGame(numPlayers):
    for i in range(numPlayers):
        plrList.append([])

def newRound():
    for i in range(len(plrList)):
        plrList[i] = []

def notify(card, playerNum):
    plrList[playerNum-1].append(card)

    if card != -1:
        deck.remove(card)

def notifyShuffle():
    for i in range(1,14):
        for x in range(4):
            if i > 10:
                deck.append(10)
            else:
                deck.append(i)

#Computing the expected value of the next card
def expectedVal():
    sum = 0
    highAceSum = 0

    for card in deck:
        if card == 1:
            highAceSum += 11
        else:
            highAceSum += card
        
        sum += card

    return (sum / len(deck), highAceSum / len(deck))

#Compute the sums of all the known cards for each player
def getCurrSums():
    sumList = []

    for plr in plrList:
        lowSum = 0
        highSum = 0

        for num in plr:
            if num != -1:
                if num == 1 and highSum < 11:
                    highSum += 11
                else:
                    highSum += num

                lowSum += num

        if highSum > 21:
            highSum = lowSum

        sumList.append(highSum)
    return sumList



#Keeping track of the card remove from the deck at the end of the round
def showCards(cardList):
    for card in cardList:
        deck.remove(card)

def calculateUnknownCard():
    sum = 0

    for card in deck:
        #Ace will usually be used as an 11, so we will count it this way for our prediction
        if card == 1:
            sum += 1
        else:
            sum += card

    return sum / len(deck)
