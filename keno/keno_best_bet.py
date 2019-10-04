#!/usr/bin/env python
# keno_best_bet
#
# 2019-10-02 tc@DinkumSoftware.com  Initial
#
# Prints the expected value of all mass keno bets
#
# State of massachusetts keno payouts

from keno import *


if __name__ == "__main__" :

    # All the keno data
    mk = MassKeno()

    ### Print what the expected bonus multiplier is
    print "Expected bonus multiplier: %0.3f" % mk.expected_bonus_multiplier
    print

    ### Print all the expected values (both with and without bonus)
    # From best to worst
    ev  = mk.expected_values
    bev = mk.expected_values_with_bonus

    # Make a list of (expected_value, spot)
    # We append a B to spot to distinguish bonus from non-bonus
    # So we can sort it
    evl = []
    for spot in ev :
        evl.append( (ev[spot], str(spot)) )
    for spot in bev :    
        evl.append( (bev[spot], str(spot) + 'B') )

    # sort and print it
    evl.sort(reverse=True)

    #      123456789.123456789.123456"
    #        ssssss     $-v.vvv      
    print "# Spots/game Expected Value on $1.00 bet"
    for (evalue, spot) in evl :
        print "%8s     $%5.3f %s" % (spot, evalue, '*' if mk.restricted_payout(spot) else ' ')
    print "# * means winnings restricted by number of winners"

    # Line break
    print


    ### Print all probabilities of winning, best to worst
    # Make a list of (probability, spot) so we can sort it
    pl = []
    for spot in mk.probability_of_winning :
        pl.append( (mk.probability_of_winning[spot], spot ) )
    pl.sort(reverse=True)

    #      123456789.123456789.123456"
    #        ssssss     v.vvv      
    print "# Spots/game Probability of winning"
    for (prob,spot) in pl :
        print "%8d      %5.3f" % (spot, prob)

