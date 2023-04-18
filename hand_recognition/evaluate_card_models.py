import torch.nn.functional as F
from torch.nn import DataParallel
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.optim.lr_scheduler import MultiStepLR,StepLR
import torch
import numpy as np
import os
import time
import sys
import copy
from torch import optim
from random import shuffle
from collections import deque

from plot import plot_data
from data_loader import return_trainloader
import datatypes as dt
from networks import *
from network_config import NetworkConfig
from data_utils import load_data,return_ylabel_dict,load_handtypes,return_handtype_data_shapes,unspool,generate_category_weights

"""
Creating a hand dataset for training and evaluating networks.
Full deck
Omaha
"""

def load_weights(net):
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(examine_params['load_path']))
    else: 
        net.load_state_dict(torch.load(examine_params['load_path'],map_location=torch.device('cpu')))

def train_network(data_dict,agent_params,training_params):
    device = agent_params['network_params']['gpu1']
    net = training_params['network'](agent_params['network_params'])
    if training_params['resume']:
        load_weights(net)
    count_parameters(net)
    # if torch.cuda.device_count() > 1:
    #     dist.init_process_group("gloo", rank=rank, world_size=world_size)
    #     net = DDP(net)
    net.to(device)
    if 'category_weights' in data_dict:
        criterion = training_params['criterion'](data_dict['category_weights'].to(device))
    else:
        criterion = training_params['criterion']()
    optimizer = optim.Adam(net.parameters(), lr=0.003)
    lr_stepsize = training_params['epochs'] // 5
    lr_stepper = MultiStepLR(optimizer=optimizer,milestones=[lr_stepsize*2,lr_stepsize*3,lr_stepsize*4],gamma=0.1)
    scores = []
    val_scores = []
    score_window = deque(maxlen=100)
    val_window = deque(maxlen=100)
    for epoch in range(training_params['epochs']):
        losses = []
        for i, data in enumerate(data_dict['trainloader'], 1):
            sys.stdout.write('\r')
            # get the inputs; data is a list of [inputs, targets]
            inputs, targets = data.values()
            targets = targets.to(device)#.cuda() if torch.cuda.is_available() else targets
            # zero the parameter gradients
            optimizer.zero_grad()
            # unspool hand into 60,5 combos
            if training_params['five_card_conversion'] == True:
                inputs = unspool(inputs)
            if training_params['one_hot'] == True:
                inputs = torch.nn.functional.one_hot(inputs)
            outputs = net(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            sys.stdout.write("[%-60s] %d%%" % ('='*(60*(i+1)//len(data_dict['trainloader'])), (100*(i+1)//len(data_dict['trainloader']))))
            sys.stdout.flush()
            sys.stdout.write(f", training sample {(i+1):.2f}")
            sys.stdout.flush()
        print('outputs',outputs.shape)
        print(f'\nMaximum value {torch.max(torch.softmax(outputs,dim=-1),dim=-1)[0]}, Location {torch.argmax(torch.softmax(outputs,dim=-1),dim=-1)}')
        print('targets',targets[:100])
        lr_stepper.step()
        score_window.append(loss.item())
        scores.append(np.mean(score_window))
        net.eval()
        val_losses = []
        for i, data in enumerate(data_dict['valloader'], 1):
            sys.stdout.write('\r')
            inputs, targets = data.values()
            targets = targets.cuda() if torch.cuda.is_available() else targets
            if training_params['five_card_conversion'] == True:
                inputs = unspool(inputs)
            if training_params['one_hot'] == True:
                inputs = torch.nn.functional.one_hot(inputs)
            val_preds = net(inputs)
            val_loss = criterion(val_preds, targets)
            val_losses.append(val_loss.item())
            sys.stdout.write("[%-60s] %d%%" % ('='*(60*(i+1)//len(data_dict['valloader'])), (100*(i+1)//len(data_dict['valloader']))))
            sys.stdout.flush()
            sys.stdout.write(f", validation sample {(i+1):.2f}")
            sys.stdout.flush()
            if i == 100:
                break
        print('\nguesses',torch.argmax(val_preds,dim=-1)[:100])
        print('targets',targets[:100])
        val_window.append(sum(val_losses))
        val_scores.append(np.mean(val_window))
        net.train()
        print(f"\nTraining loss {np.mean(score_window):.4f}, Val loss {np.mean(val_window):.4f}, Epoch {epoch}")
        torch.save(net.state_dict(), training_params['save_path'])
    print('')
    # Save graphs
    loss_data = [scores,val_scores]
    loss_labels = ['Training_loss','Validation_loss']
    plot_data(f'{network.__name__}_Handtype_categorization',loss_data,loss_labels)
    # check each hand type
    if 'y_handtype_indexes' in data_dict:
        net.eval()
        for handtype in data_dict['y_handtype_indexes'].keys():
            mask = data_dict['y_handtype_indexes'][handtype]
            inputs = data_dict['valX'][mask]
            if training_params['five_card_conversion'] == True:
                inputs = unspool(inputs)
            if training_params['one_hot'] == True:
                inputs = torch.nn.functional.one_hot(inputs)
            if inputs.size(0) > 0:
                val_preds = net(inputs)
                val_loss = criterion(val_preds, data_dict['valY'][mask])
                print(f'test performance on {training_params["labels"][handtype]}: {val_loss}')
        net.train()
    # cleanup()

def train_classification(dataset_params,agent_params,training_params):
    dataset = load_data(dataset_params['data_path'])
    trainloader = return_trainloader(dataset['trainX'],dataset['trainY'],category='classification')
    valloader = return_trainloader(dataset['valX'],dataset['valY'],category='classification')
    data_dict = {
        'trainloader':trainloader,
        'valloader':valloader
        # 'y_handtype_indexes':y_handtype_indexes
    }
    if dataset_params['datatype'] == f'{dt.DataTypes.HANDRANKSFIVE}':
        category_weights = generate_category_weights()
        data_dict['category_weights'] = category_weights
    print('Data shapes',dataset['trainX'].shape,dataset['trainY'].shape,dataset['valX'].shape,dataset['valY'].shape)
    # dataset['trainY'] = dataset['trainY'].long()
    # dataset['valY'] = dataset['valY'].long()
    # target = dt.Globals.TARGET_SET[dataset_params['datatype']]
    # y_handtype_indexes = return_ylabel_dict(dataset['valX'],dataset['valY'],target)

    # print('Target values',np.unique(dataset['trainY'],return_counts=True),np.unique(dataset['valY'],return_counts=True))
    train_network(data_dict,agent_params,training_params)

def train_regression(dataset_params,agent_params,training_params):
    dataset = load_data(dataset_params['data_path'])
    trainloader = return_trainloader(dataset['trainX'],dataset['trainY'],category='regression')
    valloader = return_trainloader(dataset['valX'],dataset['valY'],category='regression')

    print('Data shapes',dataset['trainX'].shape,dataset['trainY'].shape,dataset['valX'].shape,dataset['valY'].shape)
    # print(np.unique(dataset['trainY'],return_counts=True),np.unique(dataset['valY'],return_counts=True))
    data_dict = {
        'trainloader':trainloader,
        'valloader':valloader
    }
    train_network(data_dict,agent_params,training_params)

def validate_network(dataset_params,params):
    device = params['network_params']['gpu1']
    examine_params = params['examine_params']
    net = examine_params['network'](params['network_params'])
    load_weights(net)
    net.to(device)
    net.eval()

    bad_outputs = []
    bad_labels = []
    dataset = load_data(dataset_params['data_path'])
    trainloader = return_trainloader(dataset['valX'],dataset['valY'],category='classification')
    # valloader = return_trainloader(dataset['valX'],dataset['valY'],category='classification')
    for i, data in enumerate(trainloader, 1):
        sys.stdout.write('\r')
        # get the inputs; data is a list of [inputs, targets]
        inputs, targets = data.values()
        targets = targets.cuda() if torch.cuda.is_available() else targets
        outputs = net(inputs)
        bool_mask = torch.argmax(torch.softmax(outputs,dim=-1),dim=-1) != targets
        print(bool_mask.any())
        if bool_mask.any():
            print(outputs[bool_mask])
            print(targets[bool_mask])
            bad_outputs.append(output[bool_mask])
            bad_labels.append(targets[bool_mask])
        sys.stdout.write("[%-60s] %d%%" % ('='*(60*(i+1)//len(trainloader)), (100*(i+1)//len(trainloader))))
        sys.stdout.flush()
        sys.stdout.write(f", training sample {(i+1):.2f}")
        sys.stdout.flush()
    print(f'Number of incorrect guesses {len(bad_outputs)}')
    print(f'Bad guesses {bad_labels}')
    print(f'Missed labels {bad_labels}')


def check_network(dataset_params,params):
    messages = {
        dt.LearningCategories.REGRESSION:'Enter in a category [0,1,2] to pick the desired result [-1,0,1]',
        dt.LearningCategories.MULTICLASS_CATEGORIZATION:'Enter in a handtype from 0-8',
        dt.LearningCategories.BINARY_CATEGORIZATION:'Enter in a blocker type from 0-1'
    }
    output_mapping = {
        dt.LearningCategories.MULTICLASS_CATEGORIZATION:F.softmax,
        dt.LearningCategories.REGRESSION:lambda x: x,
        dt.LearningCategories.BINARY_CATEGORIZATION:lambda x: x
    }
    target_mapping = {
        dt.DataTypes.NINECARD:{i:i for i in range(9)},
        dt.DataTypes.FIVECARD:{i:i for i in range(9)},
        dt.DataTypes.HANDRANKSNINE:{i:dt.Globals.HAND_STRENGTH_SAMPLING[i] for i in range(9)},
        dt.DataTypes.HANDRANKSFIVE:{i:dt.Globals.HAND_STRENGTH_SAMPLING[i] for i in range(9)},
        dt.DataTypes.THIRTEENCARD:{i:i-1 for i in range(0,3)},
        dt.DataTypes.TENCARD:{i:i-1 for i in range(0,3)},
        dt.DataTypes.PARTIAL:{i:i-1 for i in range(0,3)},
        dt.DataTypes.BLOCKERS:{i:i for i in range(0,2)},
    }
    target = dt.Globals.TARGET_SET[dataset_params['datatype']]
    output_map = output_mapping[dataset_params['learning_category']]
    mapping = target_mapping[dataset_params['datatype']]
    message = messages[dataset_params['learning_category']]
    examine_params = params['examine_params']
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    net = examine_params['network'](params['network_params'])
    load_weights(net)
    net = net.to(device)
    net.eval()

    dataset = load_data(dataset_params['data_path'])
    valX = dataset['valX']
    valY = dataset['valY']
    y_handtype_indexes = return_ylabel_dict(valX,valY,target)

    while 1:
        human_input = input(message)
        while not human_input.isdigit():
            print('Improper input, must be digit')
            human_input = input(message)
        if callable(mapping[int(human_input)]) == True:
            category = mapping[int(human_input)]()
        else:
            category = mapping[int(human_input)]
        indicies = y_handtype_indexes[category]
        if len(indicies) > 0:
            print('indicies',indicies.size())
            rand_index = torch.randint(0,indicies.size(0),(1,))
            rand_hand = indicies[rand_index]
            print(f'Evaluating on: {valX[rand_hand]}')
            if torch.cuda.is_available():
                out = net(torch.tensor(valX[rand_hand]).unsqueeze(0).cuda())
            else:
                out = net(torch.tensor(valX[rand_hand]).unsqueeze(0))
            print(f'Network output: {output_map(out,dim=-1)}, Maximum value {torch.max(output_map(out,dim=-1))}, Location {torch.argmax(output_map(out,dim=-1))}')
            print(f'Actual category: {valY[rand_hand]}')
        else:
            print('No instances of this, please try again')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=
        """
        Train and evaluate networks on card representations\n\n
        use ```python cards.py -M examine``` to check handtype probabilities
        use ```python cards.py -d random``` to train on predicting winners
        use ```python cards.py``` to train on predicting handtypes
        """)

    parser.add_argument('-d','--datatype',
                        default=dt.DataTypes.HANDRANKSNINE,type=str,
                        metavar=f"[{dt.DataTypes.THIRTEENCARD},{dt.DataTypes.TENCARD},{dt.DataTypes.NINECARD},{dt.DataTypes.FIVECARD},{dt.DataTypes.PARTIAL},{dt.DataTypes.BLOCKERS},{dt.DataTypes.HANDRANKSFIVE},{dt.DataTypes.HANDRANKSNINE}]",
                        help='Which dataset to train on')
    parser.add_argument('-m','--mode',
                        metavar=f"[{dt.Modes.TRAIN}, {dt.Modes.EXAMINE}, {dt.Modes.VALIDATE}]",
                        help='Pick whether you want to train or examine a network',
                        default='train',type=str)
    parser.add_argument('-r','--random',dest='randomize',
                        help='Randomize the dataset. (False -> the data is sorted)',
                        default=True,type=bool)
    parser.add_argument('--encode',metavar=[dt.Encodings.TWO_DIMENSIONAL,dt.Encodings.THREE_DIMENSIONAL],
                        help='Encoding of the cards: 2d -> Hand (4,2). 3d -> Hand (4,13,4)',
                        default=dt.Encodings.TWO_DIMENSIONAL,type=str)
    parser.add_argument('-e','--epochs',
                        help='Number of training epochs',
                        default=10,type=int)
    parser.add_argument('--resume',
                        help='resume training from an earlier run',
                        action='store_true')
    parser.set_defaults(resume=False)


    args = parser.parse_args()

    print('OPTIONS',args)

    learning_category = dt.Globals.DatasetCategories[args.datatype]
    network = NetworkConfig.DataModels[args.datatype]
    network_name = NetworkConfig.DataModels[args.datatype].__name__
    network_path = os.path.join('checkpoints',learning_category,network_name)
    print(f'Loading model {network_path}')

    examine_params = {
        'network':network,
        'load_path':network_path
    }
    dataset_params = {
        'encoding':args.encode,
        'datatype':args.datatype,
        'learning_category':learning_category,
        'data_path':os.path.join('data',dt.Globals.DatasetCategories[args.datatype],args.datatype)
    }
    agent_params = {
        'learning_rate':2e-3,
        'network':NetworkConfig.DataModels[args.datatype],
        'save_dir':'checkpoints',
        'save_path':network_path,
        'load_path':network_path
    }
    network_params = {
        'seed':346,
        'state_space':(13,2),
        'nA':dt.Globals.ACTION_SPACES[args.datatype],
        'channels':13,
        'kernel':2,
        'batchnorm':True,
        'conv_layers':1,
        'gpu1': torch.device("cuda:0" if torch.cuda.is_available() else "cpu"),
        'gpu2': torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    }
    training_params = {
        'resume':args.resume,
        'epochs':args.epochs,
        'five_card_conversion':False,
        'one_hot':False,
        'criterion':NetworkConfig.LossFunctions[dataset_params['learning_category']],
        'network': network,
        'save_path':network_path,
        'labels':dt.Globals.LABEL_DICT[args.datatype],
        'gpu1': torch.device("cuda:0" if torch.cuda.is_available() else "cpu"),
        'gpu2': torch.device("cuda:1" if torch.cuda.is_available() else "cpu"),
    }
    multitrain_params = {
        'conversion_list':[False],#,False],#[,True],
        'onehot_list':[False],#,False],#[,True]
        'networks':[HandClassificationV2],#HandClassification,HandClassificationV2,HandClassificationV3,HandClassificationV4],#,
    }
    agent_params['network_params'] = network_params
    agent_params['examine_params'] = examine_params
    agent_params['multitrain_params'] = multitrain_params
    tic = time.time()
    if args.mode == dt.Modes.EXAMINE:
        check_network(dataset_params,agent_params)
    elif args.mode == dt.Modes.VALIDATE:
        validate_network(dataset_params,agent_params)
    elif args.mode == dt.Modes.TRAIN:
        print(f'Evaluating {network_name} on {args.datatype}, {dataset_params["learning_category"]}')
        if learning_category == dt.LearningCategories.MULTICLASS_CATEGORIZATION or learning_category == dt.LearningCategories.BINARY_CATEGORIZATION:
            train_classification(dataset_params,agent_params,training_params)
        elif learning_category == dt.LearningCategories.REGRESSION:
            train_regression(dataset_params,agent_params,training_params)
        else:
            raise ValueError(f'{args.datatype} datatype not understood')
    else:
        raise ValueError(f'{args.mode} Mode not understood')
    toc = time.time()
    print(f'Evaluation took {(toc-tic)/60} minutes')
    