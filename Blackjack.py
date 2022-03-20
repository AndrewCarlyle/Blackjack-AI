import BlackjackAI
import random

#List of cards currently in the deck
deck = []
#List of all the players in the game
players = []

#List of cards that are currently facedown
hiddenCards = []


#Can be used to automatically play a certain number of rounds, if the value is -1,
#then there will be a prompt at the end of each round
numRounds = [100000]

learning = [True]

class Player:
    def __init__(self, type, num):
        #Type is either AI controlled (true), or uses the "dealer strategy" (false)
        self.type = type
        self.cards = []
        #Set to true once a player is done hitting (they cannot change their mind once they choose to stand)
        self.done = False
        self.bust = False
        #Player number to identify each player
        self.num = num

        #Some basic stats
        self.winCount = 0
        self.tieCount = 0
        self.lossCount = 0
        self.bustCount = 0

    #Calculating a player's current score
    def getScore(self):        
        highCardSum = 0
        lowCardSum = 0

        for card in self.cards:
            #Counting the ace as 11, note that only one ace can be counted as 11 (11+11=22)
            if card == 1 and highCardSum == lowCardSum:
                highCardSum += 11
            else:
                highCardSum += card

            lowCardSum += card

        if highCardSum > 21:
            return lowCardSum
        else:
            return highCardSum

    def resetHand(self):
        self.bust = False
        self.cards = []
        self.done = False

    def showStats(self):
        print("Stats for player ", self.num)
        print("Wins: ", self.winCount)
        print("Ties: ", self.tieCount)
        print("Losses: ", self.lossCount)
        print("Busts: ", self.bustCount)
        print("====================================")

#Function that is used to start the main logic of the game
def startGame():
    #Shuffling the deck
    resetDeck()

    numPlayers = input('How many players will be playing in this game? ')

    #Input validation
    while not numPlayers.isdigit():
        numPlayers = input('How many player will be playing in this game (enter a number)? ')

    numPlayers = int(numPlayers)

    #Setting the max number of players in the game to 6
    if numPlayers > 6:
        numPlayers = 6
    elif numPlayers < 2:
        numPlayers = 2

    print("Player number 1 will play using the AI. The other ", (numPlayers - 1), " players will use the dealer method.")

    BlackjackAI.startGame(numPlayers)

    #Creating the "AI" player
    players.append(Player(True, 1))

    #Checking for each player if they will play by the dealer method or using the AI, and then creating the player object
    for i in range(numPlayers-1):
        players.append(Player(False, i+2))

    while True:
        startRound()

        response = "Y"

        if numRounds[0] == -1:
            response = input("Would you like to play another round? (Y/N) ")

        if learning[0] == True and numRounds[0] == 1:
            learning[0] = False
            numRounds[0] = 10000

            print("Stats during learning:")
            for plr in players:
                plr.showStats()
                plr.winCount = 0
                plr.tieCount = 0
                plr.lossCount = 0
                plr.bustCount = 0

        elif response == "N" or response == "n" or numRounds[0] == 1:
            break
        elif numRounds[0] > 0:
            numRounds[0] -= 1

        #Revealing the hidden cards at the end of the round
        BlackjackAI.showCards(hiddenCards)

        hiddenCards.clear()

    for plr in players:
        plr.showStats()

    cardTotal = 10
    print("Q-values for the state", cardTotal, ":")

    for key in sorted(BlackjackAI.qEstimates[cardTotal]):
        print(key, ": ", BlackjackAI.qEstimates[cardTotal][key])
        


def startRound():
    BlackjackAI.newRound()

    #Deal each player their first 2 cards
    initialDeal()

    #We can end the round right away if any players have a blackjack
    result = checkBlackjacks()

    if result == False:   
        doneHitting = False

        #Loops until all players have chosen to stand
        while not doneHitting:
            doneHitting = True

            for player in players:
                choice = False

                #A player cannot continue playing once they have stood
                if player.done == False and player.bust == False:
                    if player.type and player.done == False:
                        if learning[0]:
                            choice = BlackjackAI.makeDecision()
                        else:
                            choice = BlackjackAI.bestDecision()
                    else:
                        choice = cpuTurn(player)

                    #Drawing a card if the player chooses hit
                    if choice:
                        drawCard(player, False, False)
                        doneHitting = False
                    else:
                        player.done = True

    findWinner()

#Dealing each player their first 2 cards
def initialDeal():
    for plr in players:
        plr.resetHand()
        
        #"AI" card is visible to the AI
        if plr.num == 1:
            drawCard(plr, False, True)
        #First CPU card is invisible
        else:
            drawCard(plr, True, True)
        drawCard(plr, False, True)

#Making a decision for any computer players that play by the dealer strategy
def cpuTurn(player):
    highCardSum = 0
    lowCardSum = 0

    for card in player.cards:
        #Counting the ace as 11, note that only one ace can be counted as 11 (11+11=22)
        if card == 1 and highCardSum == lowCardSum:
            highCardSum += 11
        else:
            highCardSum += card

        lowCardSum += card

    #If their sum is greater than 21, then we count the ace as a 1
    if highCardSum > 21:
        highCardSum = lowCardSum

    #The dealer has to hit on anything lower than 17
    if highCardSum < 17:
        return True
    else:
        return False

#Randomly drawing a card from the deck and dealing it to the player
#Facedown is true if this is a card that would be placed facedown (hidden)
def drawCard(player, faceDown, initialDeal):
    card = deck.pop()

    prevScore = player.getScore()

    player.cards.append(card)

    total = 0
    for card in player.cards:
        total += card

    if (not faceDown):
        BlackjackAI.notify(card, player.num)
    else:
        BlackjackAI.notify(-1, player.num)
        hiddenCards.append(card)

    if total > 21:
        player.bust = True
        player.bustCount += 1
        if  learning[0] == True:
            #BlackjackAI.updateQValue(prevScore, -0.1, 0)
            pass
    elif not initialDeal and learning[0] == True:
        BlackjackAI.updateQValue(prevScore, 1, 0)


    if deck == []:
        resetDeck()
        
#Checks after the initial deal to see if any players have a blackjack
def checkBlackjacks():
    for plr in players:
        if plr.getScore() == 21:
            return True

    return False

def findWinner():
    #Using a list here in case multiple players have the same score and tie
    winners = []
    winningScore = 0

    for player in players:
        if player.getScore() == winningScore:
            winners.append(player)
        elif player.getScore() > winningScore and player.getScore() <= 21:
            winners = [player]
            winningScore = player.getScore()

    for plr in players:
        if numRounds[0] == -1:
            print("Score for player ", plr.num, ": ", plr.getScore())

        if plr not in winners:
            plr.lossCount += 1

    for plr in winners:
        if len(winners) > 1:
            if numRounds[0] == -1:
                print("Player ",plr.num,", you tied this round.")
            plr.tieCount += 1
            if player.type == True and learning[0] == True:
                BlackjackAI.updateQValue(plr.getScore(), 0, 1)
        else:
            if numRounds[0] == -1:
                print("Congratulations player ",plr.num,", you win!")
            plr.winCount += 1
            if plr.type == True and learning[0] == True:
                BlackjackAI.updateQValue(plr.getScore(), 1, 1)

    if not players[0] in winners and learning[0] == True:
        BlackjackAI.updateQValue(players[0].getScore(), -1, 1)

#"Shuffling" the deck. For the sake of simplicity, we will assume that we are playing 
#with at least two different decks, so whatever cards are in play when the deck is emptied
#will not be missing when the deck is reset
def resetDeck():
    if numRounds[0] == -1:
        print("Shuffling...")
    for i in range(1,14):
        for x in range(4):
            if i > 10:
                deck.append(10)
            else:
                deck.append(i)

    BlackjackAI.notifyShuffle()

    random.shuffle(deck)

startGame()
