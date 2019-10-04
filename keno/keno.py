# keno.py
#
# Support data for keno probabilities

from __future__ import division   # makes 2/3 return floating point


import math

def ncr(n, k):
    ''' Returns number of combinations of choosing "r" items out of "n" total

    num_combinations(n,k) = n! / ( k! x (n-k)! )  for 0 <= k <= n
    '''
    assert 0 <= k <= n

    f = math.factorial
    return f(n) / f(k) / f(n-k)



class Bet():
    ''' Represents a keno bet.
        Has:
          num_game_spots   How many numbers picked for a game
          num_hit          How many matched
    '''
    def __init__(self, num_game_spots, num_hit) :
        assert 0 <= num_hit <= num_game_spots

        self.num_game_spots = num_game_spots
        self.num_hit        = num_hit


class MassKeno() :
    ''' Payouts and game size for Massachusetts keno '''
    num_nums  = 80 # How many numbers in the game
    num_picks = 20 # How many numbers selected by house out of num_nums

    # Value: $ payout on $1.00  Key: Bet (num_game_spots, num_hit)
    # https://www.masslottery.com/games/keno.html
    payouts = {Bet(1,1) : 2.50,

               Bet(2,2) : 5.00,
               Bet(2,1) : 1.00,

               Bet(3,3) : 25.00,
               Bet(3,2) :  2.50,


               Bet(4,4) : 100.00,
               Bet(4,3) :   4.00,
               Bet(4,2) :   1.00,

               Bet(5,5) : 450.00,
               Bet(5,4) :  20.00,
               Bet(5,3) :   2.00,

               Bet(6,6) : 1600.00,
               Bet(6,5) :   50.00,
               Bet(6,4) :    7.00,
               Bet(6,3) :    1.00,

               Bet(7,7) : 5000.00,
               Bet(7,6) :  100.00,
               Bet(7,5) :   20.00,
               Bet(7,4) :    3.00,
               Bet(7,3) :    1.00,

               Bet(8,8) : 15000.00,
               Bet(8,7) :  1000.00,
               Bet(8,6) :    50.00,
               Bet(8,5) :    10.00,
               Bet(8,4) :     2.00,
                          
               Bet(9,9) : 40000.00,
               Bet(9,8) :  4000.00,
               Bet(9,7) :   200.00,
               Bet(9,6) :    25.00,
               Bet(9,5) :     5.00,
               Bet(9,4) :     1.00,

               Bet(10,10) : 100000.00,
               Bet(10, 9) :  10000.00,
               Bet(10, 8) :   500.00,
               Bet(10, 7) :    80.00,
               Bet(10, 6) :    20.00,
               Bet(10, 5) :     2.00,
               Bet(10, 0) :     2.00,

               Bet(11,11) : 500000.00,
               Bet(11,10) :  15000.00,
               Bet(11, 9) :   1500.00,
               Bet(11, 8) :    250.00,
               Bet(11, 7) :     50.00,
               Bet(11, 6) :     10.00,
               Bet(11, 5) :      1.00,
               Bet(11, 0) :      2.00,

               Bet(12,12) : 1000000.00,
               Bet(12,11) :   25000.00,
               Bet(12,10) :    2500.00,
               Bet(12,9) :     1000.00,
               Bet(12,8) :      150.00,
               Bet(12,7) :       25.00,
               Bet(12,6) :        5.00,
               Bet(12,0) :        4.00,
        }


    def restricted_payout(self, num_game_spots) :
        ''' Some games restrict the payout to a maximum amount for ALL players and
        split the winnings amoung multiple players.  In other words, if too many
        people pick the winning number, they won't all get what is advertised in payouts{}

        This return True if that is the case for "num_game_spots"
        '''
        return  num_game_spots == 12  or  \
                num_game_spots == 11  or  \
                num_game_spots == 10


    # This is what lottery says are the odds of winning
    # key: num_game_spots value: probability of winning in that game
    # https://www.masslottery.com/games/keno.html
    lottery_probability_of_winning = {}
    lottery_probability_of_winning[ 1] = 1.0 /  4.0
    lottery_probability_of_winning[ 2] = 1.0 /  2.27
    lottery_probability_of_winning[ 3] = 1.0 /  6.55
    lottery_probability_of_winning[ 4] = 1.0 /  3.86
    lottery_probability_of_winning[ 5] = 1.0 / 10.34
    lottery_probability_of_winning[ 6] = 1.0 /  6.19
    lottery_probability_of_winning[ 7] = 1.0 /  4.23
    lottery_probability_of_winning[ 8] = 1.0 /  9.77
    lottery_probability_of_winning[ 9] = 1.0 /  6.53
    lottery_probability_of_winning[10] = 1.0 /  9.05
    lottery_probability_of_winning[11] = 1.0 /  7.63
    lottery_probability_of_winning[12] = 1.0 / 15.73


    # The odds of various "bonus" values
    # You double your bet and winnings get multiplied by a bonus
    # key: multiplier  value: probability of selection
    bonus={}
    bonus[ 1] = 1.0 /   1.75  # No bonus
    bonus[ 3] = 1.0 /   3.0
    bonus[ 4] = 1.0 /  15.0
    bonus[ 5] = 1.0 /  40.0
    bonus[10] = 1.0 / 234.0
    def bonus_sanity_check(self) :
        ''' returns True lottery stated probabilitys sum to one. '''
        # sum all the probabilities
        tot_prob = 0.0
        for prob in self.bonus.values() :
            tot_prob += prob

        # Close enuf to one?
        return abs(1.0 - tot_prob) <= 0.01


    def __init__(self) :
        ''' Computes expected value of a $1 bet in all games in "expected_values{}"
        Computes probability of winning for all games in "probability_of_winning{}"
        Both keyed by "num_game_spots"
        '''

        ### Sanity check some static Class variables
        assert self.bonus_sanity_check()

        ### compute the expected bonus multiplier
        self.expected_bonus_multiplier = 0
        for mult in self.bonus :
            self.expected_bonus_multiplier += mult * self.bonus[mult]

        ### Computes expected values of all num_game_spots sans bonus
        self.expected_values = {} # key:spot value:expected value

        # Accumulate all the possible winnings for each spot
        for bet in self.payouts :
            spot = bet.num_game_spots # How many numbers selected

            if spot not in self.expected_values :
                # First time we've seen this spot
                # Create it with initial $1 bet
                self.expected_values[spot] = -1.00
        
            # accumulate expected winnings
            self.expected_values[spot] += ( self.odds(bet) * self.payouts[bet] )

        ### Computes expected values of all num_game_spots playing the bonus
        # Accumulate all the possible winnings for each spot
        # games with restricted_payout do not allow a bonus
        self.expected_values_with_bonus = {} # key:spot value:expected value
        for bet in self.payouts :
            spot = bet.num_game_spots # How many numbers selected

            # Bonus available?
            if self.restricted_payout(spot) :
                continue # nope

            # Compute bonus expected value
            if spot not in self.expected_values_with_bonus :
                # First time we've seen this spot
                # Create it with initial $1 bet and $1 bonus play
                self.expected_values_with_bonus[spot] = -2.00
        
            # accumulate expected winnings
            self.expected_values_with_bonus[spot] += ( self.odds(bet) *
                                                       self.payouts[bet] *
                                                       self.expected_bonus_multiplier)

        ### Compute probability of winning a given game
        self.probability_of_winning = {} # key:spot value:probability
        for bet in self.payouts :
            spot = bet.num_game_spots # How many numbers selected

            if spot not in self.probability_of_winning :
                # First time we've seen this spot
                # See it with no probability
                self.probability_of_winning[spot] = 0.00
        
            # accumulate probabilities
            self.probability_of_winning[spot] += self.odds(bet)


            

    def odds( self, bet ) :
        ''' Returns probability of winning bet.
        Bet is: num_game_spots, num_hit
        '''
        assert bet.num_game_spots >= bet.num_hit

        # See http://www.reviewpokerrooms.com/casino-games/keno/odds.html
        # Match the variable names of formulas on the above web site for easier reading
        n=bet.num_game_spots
        k=bet.num_hit
        _80=self.num_nums
        _20=self.num_picks
        _60=_80 - _20

        # It gives two solutions which should be the same
        ans1 = ncr(n,k) * ncr( _80-n, _20-k) / ncr(_80, _20)
        ans2 = ncr(_20,k) * ncr( _60, (n-k)) / ncr(80,n)
        
        # Sanity check
        assert abs(ans1 - ans2) <  (0.00000001 * ans1)

        # We just pick one
        return ans1


# Test code
import unittest

class KenoTest(unittest.TestCase) :
    def test_ncr(self):
        self.assertEqual(ncr( 1, 1),   1.0)
        self.assertEqual(ncr( 3, 1),   3.0)

        # ncr(10, 4)
        nf   = 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1
        kf   =  4 * 3 * 2 * 1
        nmkf =  6 * 5 * 4 * 3 * 2 * 1
        self.assertEqual( ncr(10,4),   nf / (kf * nmkf) )

    def test_odds(self) :
        mk = MassKeno()

        # Answers from http://www.reviewpokerrooms.com/casino-games/keno/odds.html
        num_spots=9
        prob_of_n_matches={0:  6.374783835335 / 100,
                           1: 22.066559430007 / 100,
                           2: 31.642613522274 / 100,
                           8:  0.003259245500 / 100,
                           9:  0.000072427678 / 100 }

        # Compare the odds of all the bets we have answers for
        num_places_reqd_for_equality = 10
        for num_hits in prob_of_n_matches :
            self.assertAlmostEqual( mk.odds( (num_spots, num_hits)),  prob_of_n_matches[num_hits],
                                    num_places_reqd_for_equality)


        # answers from https://www.masslottery.com/games/keno.html
        num_places_reqd_for_equality = 4  # The lottery odds calculations aren't very good
        self.assertAlmostEqual (mk.odds(( 1,1)), 1.0/  4.00, num_places_reqd_for_equality)
        self.assertAlmostEqual (mk.odds(( 2,2)), 1.0/ 16.63, num_places_reqd_for_equality)
        self.assertAlmostEqual (mk.odds((12,8)), 1.0/980.78, num_places_reqd_for_equality)



if __name__ == "__main__" :    
    unittest.main()
        
