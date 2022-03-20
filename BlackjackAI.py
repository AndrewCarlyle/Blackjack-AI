#This file contains the AI portion of my final project

#List of all opposing players within the game and their cards. '?' = face down card
plrList = []

#Representation of the deck as the AI sees it. (It may know that there are some missing cards, but not which cards)
deck = []

def resetDeck():
    for i in range(1,14):
        for x in range(4):
            if i > 10:
                deck.append(10)
            else:
                deck.append(i)

#This function returns the decision to either hit (true) or stand (false)
#myCards - a list of all the cards that the AI has
#computerCards - a list where each element is a list, and each list has
#the value of the computer's face up cards, and the face down card represented
#by a -1
#deck - a list of cards currently in the deck
def makeDecision():
    currSums = getCurrSums()

    predSums = []

    #Unknown card prediction - an estimate of the value of the face down card
    ucPred = calculateUnknownCard()

    #This will happen very rarely but, if we know that all CPU's have busted (exluding their hidden card)
    #then we can stand
    cpuBust = True

    cpuSums = currSums[1:len(currSums)]

    for sum in cpuSums:
        predSums.append(sum + ucPred)

        if sum < 22:
            cpuBust = False

    #Standing if all other players have busted
    if cpuBust:
        return False

    #Calculating the probability that the next card will cause the AI to bust
    bustTotal = 0

    for card in deck:
        if card + currSums[0] > 21:
            bustTotal += 1

    bustProbability = bustTotal / len(deck)

    if bustProbability > 0.75:
        return False

    #This value is higher than 21 since the average value of the cards in the deck is skewed by the cards worth 10
    if currSums[0] + ucPred <= 23:
        return True

    return False
    decision = False

    #This is a list instead of a single value so that we can allow for situations where we have an ace
    myTotal = [0,0]

    for card in myCards:
        myTotal[0] += card

        if card == 1 and myTotal < 11:
            myTotal[1] += 11
        else:
            myTotal[1] += 1

    lowAceTotal = 0
    highAceTotal = 0

    for i in deck:
        lowAceTotal += i

        if i == 1:
            highAceTotal += 11
        else:
            highAceTotal += i

    lowAceExpected = lowAceTotal / len(deck)
    highAceExpected = highAceTotal / len(deck)

    return decision

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
