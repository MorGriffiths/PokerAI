from torch import Tensor as T
import numpy as np

ACTION_DICT = {0:'check',1:'fold',2:'call',3:'bet',4:'raise',5:'unopened'}
REVERSE_ACTION_DICT = {v:k for k,v in ACTION_DICT.items()}
ACTION_ORDER = {0:'check',1:'fold',2:'call',3:'bet',4:'raise'}
ACTION_MASKS = {
        0:T([1,0,0,1,0]),
        1:T([0,0,0,0,0]),
        2:T([1,0,0,0,1]),
        3:T([0,1,1,0,1]),
        4:T([0,1,1,0,1]),
        5:T([1,0,0,1,0])
        }

"""
High is noninclusive
"""
class RANKS(object):
    HIGH = 15
    LOW = 2

class SUITS(object):
    HIGH = 4
    LOW = 0

class LimitTypes:
    POT_LIMIT = 'pot_limit'
    NO_LIMIT = 'no_limit'
    LIMIT = 'limit'

class OutputTypes:
    TIERED = 'tiered'
    FLAT = 'flat'

class GameTypes:
    HOLDEM = 'holdem'
    OMAHAHI = 'omaha_hi'
    OMAHAHILO = 'omaha_hi_lo'

class Positions:
    SB = 'SB'
    BB = 'BB'
    ALL = ['SB','BB']

class Street:
    RIVER = 'river'
    TURN = 'turn'
    FLOP = 'flop'
    PREFLOP = 'preflop'

class Actions:
    CHECK = 'check'
    BET = 'bet'
    CALL = 'call'
    FOLD = 'fold'
    RAISE = 'raise'
    UNOPENED = 'unopened'

class AgentTypes:
    SPLIT = 'split'
    SINGLE = 'single'
    SPLIT_OBS = 'split_obs'
    ALL = [SPLIT,SINGLE,SPLIT_OBS]

BLIND_DICT = {
    Positions.BB : T([1]),
    Positions.SB : T([0.5])
}

class BaseHoldem(object):
    def __init__(self):
        self.starting_street = 0
        self.state_params = {}
        self.state_params['ranks'] = list(range(2,15))
        self.state_params['suits'] = list(range(0,4))
        self.state_params['cards_per_player'] = 2
        self.state_params['n_players'] = 2
        self.state_params['stacksize'] = 10
        self.state_params['pot'] = 2
        self.state_params['game_turn'] = 0
        self.rule_params = {
            'unopened_action' : T([5]),
            'mask_dict' :  ACTION_MASKS,
            'action_dict' : ACTION_ORDER,
            'betsizes' : T([0.5,1.]),
            'blinds': BLIND_DICT,
            'bettype' : LimitTypes.LIMIT,
            'mapping': {
                'state':{
                    'suit':T([1,3]).long(),
                    'rank':T([0,2]).long(),
                    'hand':T([0,1,2,3]).long(),
                    'board':T([4,5,6,7,8,9,10,11,12,13]).long(),
                    'board_ranks':T([4,6,8,10,12]).long(),
                    'board_suits':T([5,7,9,11,13]).long(),
                    'street':T([14]).long(),
                    'hero_position':T([15]).long(),
                    'vil_position':T([16]).long(),
                    'previous_action':T([17]).long(),
                    'previous_betsize':T([18]).long(),
                    'hero_stack':T([19]).long(),
                    'villain_stack':T([20]).long(),
                    'amnt_to_call':T([21]).long(),
                    'pot_odds':T([22]).long(),
                    'hand_board':T([0,1,2,3,4,5,6,7,8,9,10,11,12,13]).long(),
                    'ordinal':T([14,15,16,17]).long(),
                    'continuous':T([18,19,20,21,22]).long()
                    },
                'observation':{
                    'suit':T([1,3]).long(),
                    'rank':T([0,2]).long(),
                    'hand':T([0,1,2,3]).long(),
                    'vil_hand':T([4,5,6,7]).long(),
                    'vil_ranks':T([4,6]).long(),
                    'vil_suits':T([5,7]).long(),
                    'board':T([8,9,10,11,12,13,14,15,16,17]).long(),
                    'board_ranks':T([8,10,12,14,16]).long(),
                    'board_suits':T([9,11,13,15,17]).long(),
                    'street':T([18]).long(),
                    'hero_position':T([19]).long(),
                    'vil_position':T([20]).long(),
                    'previous_action':T([21]).long(),
                    'previous_betsize':T([22]).long(),
                    'hero_stack':T([23]).long(),
                    'villain_stack':T([24]).long(),
                    'amnt_to_call':T([25]).long(),
                    'pot_odds':T([26]).long(),
                    'hand_board':T([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]).long(),
                    'ordinal':T([18,19,20,21]).long(),
                    'continuous':T([22,23,24,25,26]).long()
                }
            }
        }

class Holdem(object):
    def __init__(self):
        H = BaseHoldem()
        self.rule_params = H.rule_params
        self.state_params = H.state_params
        self.state_params['stacksize'] = 2.
        self.state_params['pot']= 2.
        self.rule_params['betsizes'] = T([0.5,1.])
        self.starting_street = 3


class BaseOmaha(object):
    def __init__(self):
        self.starting_street = 0
        self.state_params = {}
        self.state_params['ranks'] = list(range(2,15))
        self.state_params['suits'] = list(range(0,4))
        self.state_params['cards_per_player'] = 4
        self.state_params['n_players'] = 2
        self.state_params['stacksize'] = 10
        self.state_params['pot'] = 2
        self.state_params['game_turn'] = 0
        self.rule_params = {
            'unopened_action' : T([5]),
            'mask_dict' :  ACTION_MASKS,
            'action_dict' : ACTION_ORDER,
            'betsizes' : T([0.5,1.]),
            'blinds': BLIND_DICT,
            'bettype' : LimitTypes.POT_LIMIT,
            'mapping': {
                'state':{
                    'suit':T([1,3,5,7]).long(),
                    'rank':T([0,2,4,6]).long(),
                    'hand':T([0,1,2,3,4,5,6,7]).long(),
                    'board':T([8,9,10,11,12,13,14,15,16,17]).long(),
                    'board_ranks':T([8,10,12,14,16]).long(),
                    'board_suits':T([9,11,13,15,17]).long(),
                    'street':T([18]).long(),
                    'hero_position':T([19]).long(),
                    'vil_position':T([20]).long(),
                    'previous_action':T([21]).long(),
                    'previous_betsize':T([22]).long(),
                    'hero_stack':T([23]).long(),
                    'villain_stack':T([24]).long(),
                    'amnt_to_call':T([25]).long(),
                    'pot_odds':T([26]).long(),
                    'hand_board':T([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]).long(),
                    'ordinal':T([18,19,20,21]).long(),
                    'continuous':T([22,23,24,25,26]).long()
                    },
                'observation':{
                    'suit':T([1,3,5,7]).long(),
                    'rank':T([0,2,4,6]).long(),
                    'hand':T([0,1,2,3,4,5,6,7]).long(),
                    'vil_hand':T([8,9,10,11,12,13,14,15]).long(),
                    'vil_ranks':T([8,10,12,14]).long(),
                    'vil_suits':T([9,11,13,15]).long(),
                    'board':T([16,17,18,19,20,21,22,23,24,25]).long(),
                    'board_ranks':T([16,18,20,22,24]).long(),
                    'board_suits':T([17,19,21,23,25]).long(),
                    'street':T([26]).long(),
                    'hero_position':T([27]).long(),
                    'vil_position':T([28]).long(),
                    'previous_action':T([29]).long(),
                    'previous_betsize':T([30]).long(),
                    'hero_stack':T([31]).long(),
                    'villain_stack':T([32]).long(),
                    'amnt_to_call':T([33]).long(),
                    'pot_odds':T([34]).long(),
                    'hand_board':T([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]).long(),
                    'ordinal':T([26,27,28,29]).long(),
                    'continuous':T([30,31,32,33,34]).long()
                }
            }
        }

class OmahaHI(object):
    def __init__(self):
        K = BaseOmaha()
        self.starting_street = 3
        self.rule_params = K.rule_params
        self.state_params = K.state_params
        self.state_params['stacksize'] = 5.
        self.state_params['pot']= 2.
        self.rule_params['betsizes'] = np.array([0.5,1.])

class OmahaHILO(object):
    def __init__(self):
        ## NOT IMPLEMENTED ##
        K = BaseHoldem()
        self.starting_street = 0
        self.rule_params = K.rule_params
        self.state_params = K.state_params
        self.state_params['stacksize'] = 5.
        self.state_params['pot']= 2.
        self.rule_params['betsizes'] = np.array([0.5,1.])

class Globals:
    GameTypeDict = {
        GameTypes.HOLDEM:Holdem(),
        GameTypes.OMAHAHI:OmahaHI(),
        GameTypes.OMAHAHILO:OmahaHILO(),
    }
    POSITION_DICT = {Positions.SB:Positions.SB,Positions.BB:Positions.BB}
    POSITION_MAPPING = {'SB':0,'BB':1,'BTN':2}
    PLAYERS_POSITIONS_DICT = {2:['SB','BB'],3:['SB','BB','BTN'],4:['SB','BB','CO','BTN'],5:['SB','BB','MP','CO','BTN'],6:['SB','BB','UTG','MP','CO','BTN']}
    HEADSUP_POSITION_DICT = {
        0:['SB','BB'],
        1:['BB','SB'],
        2:['BB','SB'],
        3:['BB','SB']
    }
    ACTION_DICT = {0:'check',1:'fold',2:'call',3:'bet',4:'raise',5:'unopened'}
    ACTION_ORDER = {0:'check',1:'fold',2:'call',3:'bet',4:'raise'}
    REVERSE_ACTION_ORDER = {v:k for k,v in ACTION_ORDER.items()}
    ACTION_MASKS = ACTION_MASKS
    POKER_RANK_DICT = {v:v for v in range(2,11)}
    BROADWAY = {11:'J',12:'Q',13:'K',14:'A'}
    for k,v in BROADWAY.items():
        POKER_RANK_DICT[k] = v
    POKER_SUIT_DICT = {0:'s',1:'h',2:'d',3:'c'}
    BLIND_DICT = BLIND_DICT
    BETSIZE_DICT = {
        2: T([0.5,1.]),
        3: T([0.3,0.6,1.]),
        4: T([0.25,0.5,0.75,1.]),
        5: T([0.2,0.4,0.6,0.8,1.]),
        11: T([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.])
    }
    # Takes street as key
    ADDITIONAL_BOARD_CARDS = {
        0 : 0,
        1 : 3,
        2 : 1,
        3 : 1
    }
    # Takes street as key
    INITIALIZE_BOARD_CARDS = {
        0 : 0,
        1 : 3,
        2 : 4,
        3 : 5
    }
    STREET_DICT = {
        0:Street.PREFLOP,
        1:Street.FLOP,
        2:Street.TURN,
        3:Street.RIVER
    }
    REVERSE_STREET_DICT = {v:k for k,v in STREET_DICT.items()}
    HAND_LENGTH_DICT = {
        'holdem':2,
        'omaha_hi':4,
        'omaha_hi_lo':4
    }
    STARTING_INDEX = { 
        2:{
            0:0,
            1:1,
            2:1,
            3:1
        },
        3: {
            0:0,
            1:0,
            2:0,
            3:0
        }
    }
    STARTING_AGGRESSION = {
        0:(4,1),
        1:(5,0),
        2:(5,0),
        3:(5,0)
    }
    ACTION_MASKS = {
            0:np.array([1,0,0,1,0]),
            1:np.array([0,0,0,0,0]),
            2:np.array([1,0,0,0,1]),
            3:np.array([0,1,1,0,1]),
            4:np.array([0,1,1,0,1]),
            5:np.array([1,0,0,1,0])
            }

    BOARD_UPDATE = {
        1:(0,6),
        2:(6,8),
        3:(8,10)
    }
    POSITION_INDEX = {
        0:'SB',
        1:'BB',
        2:'BTN'
    }
    NAME_INDEX = {v:k for k,v in POSITION_INDEX.items()}
