class Modes(object):
    TRAIN = 'train'
    BUILD = 'build'
    EXAMINE = 'examine'

class DataTypes(object):
    THIRTEENCARD = 'thirteencard'
    NINECARD = 'ninecard'
    FIVECARD = 'fivecard'
    TENCARD = 'tencard'
    BLOCKERS = 'blockers'
    PARTIAL = 'partial'

class Encodings(object):
    TWO_DIMENSIONAL = '2d'
    THREE_DIMENSIONAL = '3d'

class LearningCategories(object):
    MULTICLASS_CATEGORIZATION = 'multiclass_categorization'
    BINARY_CATEGORIZATION = 'binary_categorization'
    REGRESSION = 'regression'

class Globals(object):
    HAND_TYPE_DICT = {
                0:'Straight_flush',
                1:'Four_of_a_kind',
                2:'Full_house',
                3:'Flush',
                4:'Straight',
                5:'Three_of_a_kind',
                6:'Two_pair',
                7:'One_pair',
                8:'High_card'
            }
    HAND_TYPE_FILE_DICT = {'Hand_type_'+v:k for k,v in HAND_TYPE_DICT.items()}
    DatasetCategories = {
        DataTypes.FIVECARD : LearningCategories.MULTICLASS_CATEGORIZATION,
        DataTypes.NINECARD : LearningCategories.MULTICLASS_CATEGORIZATION,
        DataTypes.TENCARD : LearningCategories.REGRESSION,
        DataTypes.THIRTEENCARD : LearningCategories.REGRESSION,
        DataTypes.PARTIAL : LearningCategories.REGRESSION,
        DataTypes.BLOCKERS : LearningCategories.BINARY_CATEGORIZATION
    }
    SUIT_DICT = {
        0:'s',
        1:'h',
        2:'d',
        3:'c'
    }
    REVERSE_SUIT_DICT = {v:k for k,v in SUIT_DICT.items()}
    INPUT_SET_DICT = {
        'train' : 'train_set_size',
        'test' : 'test_set_size',
        'val' : 'val_set_size'
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