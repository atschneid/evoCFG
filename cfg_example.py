import random
import os
import numpy as np
import pyswip
from pyswip.prolog import Prolog

with open('terms.tsv') as f:
    terms = [t.strip() for l in f for t in l.split()]
print('terminals : ', terms)

termslist = ['[{}]'.format(t) for t in terms]

best_fit = {}

random.seed(0)
num_rules = 10
max_sent = 3
gen_size = 12
generations = 100

prop_copy = .5
prop_merge = .25
prop_rando = .25

merge_size = int(gen_size * prop_merge)
rando_size = int(gen_size * prop_rando)
copy_size = gen_size - merge_size - rando_size

prob_mod = .9

prob_mutate = .1
prob_delete = .3

rulenames = ['s0'] + ['x{}'.format(i) for i in range(1,num_rules+1)]

pl = Prolog()
pl.consult('unload_rules.pl')
pl.consult('realrules.pl')
examples = set()
negatives = set()

for _ in range(100000):
    rlen = random.randint(1,10)
    sent = []
    for _ in range(rlen):
        rindx = random.randint(1,len(terms)) - 1
        sent += [terms[rindx]]
    sentstring = '[ '
    for s in sent:
        sentstring += s + ' ,'
    sent = sentstring[:-1] + ']'
    q = list(pl.query('s({},[]).'.format(sent)))
    if len(q) > 0:
        examples.add(sent)
    else:
        if random.random() < 0.001:
            negatives.add(sent)

list(pl.query("unload_last_source."))
#list(pl.query('unload_source("realrules.pl").'))
print('len neg : ', len(negatives))
print('len pos : ', len(examples))

def check(pl,examples):
    true_passes = 0
    false_fails = 0
    for s in examples:
        #print(s)
        q = list(pl.query('s0({},[]).'.format(s)))
        if len(q) > 0:
            true_passes += 1
        #     print('pass')
        # else:
        #     print('fail')
    for s in negatives:
        # print(s)
        q = list(pl.query('s0({},[]).'.format(s)))
        if len(q) == 0:
            false_fails += 1
        #     print('fail')
        # else:
        #     print('pass')
    return [true_passes,false_fails]

def mod_rules(rules):
    if random.random() > prob_mod:
        return rules
    for i in range(len(rules)):
        if random.random() < prob_delete:
            rules[i] = ''
        else:
            rule = rules[i].split('.')[0]
            rn, rightside = rule.split('-->')
            rn_i = int(rn[1:])
            rightside = rightside.split(',')
            rs = []
            for j in range(len(rightside)):
                if random.random() < prob_mutate:
                    rs += random.sample(rulenames[rn_i:] + termslist, random.randint(0,2))
                else:
                    rs += [rightside[j]]
            if rs == []:
                rules[i] = ''
            else:
                if rs[0].strip() == rn.strip():
                    rs = random.sample(termslist,1) + rs
                rightside = ','.join(rs)
                rules[i] = '{} --> {}.'.format(rn.strip(),rightside.strip())
    return [r for r in rules if r != '']

def fitness_func(fns):
    arr = []
    for [a,b] in fns:
        arr += [a*25 + b]
    return arr
            
gen = 0

for child_no in range(gen_size):
    rules_0 = []
    for rn_i, rn in enumerate(rulenames):
        for _ in range(num_rules):
            rightside = random.sample(rulenames[rn_i+1:] + termslist, 1) + random.sample(rulenames[rn_i:] + termslist, random.randint(0, max_sent - 1))
            # for i, rule in enumerate(rightside):
            #     if rule == rn:
            #         rightside[max(i-1,0)] = random.sample(termslist,1)[0]

            
            rs_string = ','.join(rightside)
            new_rule = '{} --> {}.'.format(rn,rs_string)
            rules_0 += [new_rule]

    #print('rules:', rules_0)
    # if not os.path.isdir('gen0'):
    #     os.mkdir('gen0')
    with open(os.path.join('gen{}_g{}.pl'.format(gen,child_no)), 'w') as f:
        for rn in rulenames:
            f.write(":- dynamic {}/2.\n".format(rn))
        for rule in rules_0:
            f.write(rule + '\n')

    print(os.path.join('gen{}_g{}.pl'.format(gen,child_no)))

    pl.consult('gen{}_g{}.pl'.format(gen,child_no))

    true_passes, false_fails = check(pl,examples)
    print('******')
    print('gen{}_g{}.pl'.format(gen,child_no))
    print('******')
    print('accepted ', true_passes, ' of ', len(examples))
    print('rejected ', false_fails, ' of ', len(negatives))


    # for rn in rulenames:
    #     list(pl.query("abolish({}/2).".format(rn)))
    # list(pl.query("listing."))
    list(pl.query("unload_last_source."))

for gen in range(1, generations + 1):
    for i in range(gen_size):
        if i < copy_size:
            rules_0 = []
            
            parents = random.sample(range(gen_size),2)
            fitness = []
            for par in parents:
                pl.consult('gen{}_g{}.pl'.format(gen-1,par))
                fitness += [check(pl,examples)]
                list(pl.query("unload_last_source."))
                # print('160 query ', list(pl.query("listing.")))
                
            keeper = parents[np.argmax(fitness_func(fitness))]

            rules_0 = []
            with open('gen{}_g{}.pl'.format(gen-1,keeper)) as f:
                for line in f:
                    if '-->' in line:
                        rules_0 += [line.strip()]
                    
        if copy_size <= i < copy_size + merge_size:
            rules_0 = []
            
            parents = random.sample(range(gen_size),2)
            fitness = []
            for par in parents:
                pl.consult('gen{}_g{}.pl'.format(gen-1,par))
                fitness += [check(pl,examples)]
                list(pl.query("unload_last_source."))
                # print('179 query ', list(pl.query("listing.")))

            keeper = parents[np.argmax(fitness_func(fitness))]

            rules_0 = []
            with open('gen{}_g{}.pl'.format(gen-1,keeper)) as f:
                for line in f:
                    if '-->' in line:
                        rules_0 += [line.strip()]

            parents = random.sample(range(gen_size),2)
            fitness = []
            for par in parents:
                pl.consult('gen{}_g{}.pl'.format(gen-1,par))
                fitness += [check(pl,examples)]
                list(pl.query("unload_last_source."))
                # print('195 query ', list(pl.query("listing.")))

            keeper = parents[np.argmax(fitness_func(fitness))]

            with open('gen{}_g{}.pl'.format(gen-1,keeper)) as f:
                for line in f:
                    if '-->' in line:
                        rules_0 += [line.strip()]

        if i >= copy_size + merge_size:

            rules_0 = []
            for rn_i, rn in enumerate(rulenames):
                for _ in range(num_rules):
                    rightside = random.sample(rulenames[rn_i+1:] + termslist, 1) + random.sample(rulenames[rn_i:] + termslist, random.randint(0, max_sent - 1))

                    rs_string = ','.join(rightside)
                    new_rule = '{} --> {}.'.format(rn,rs_string)
                    rules_0 += [new_rule]

        rules_0 = list(set(rules_0))
        rules_0 = mod_rules(rules_0)

        with open(os.path.join('gen{}_g{}.pl'.format(gen,i)), 'w') as f:
            for rn in rulenames:
                f.write(":- dynamic {}/2.\n".format(rn))
            f.write('\n'.join( sorted(rules_0) ) )

    for child_no in range(gen_size):
        pl.consult('gen{}_g{}.pl'.format(gen,child_no))
        # print('230 query ', list(pl.query("listing.")))
        
        true_passes, false_fails = check(pl,examples)
        print('******')
        print('gen{}_g{}.pl'.format(gen,child_no))
        print('******')
        print('accepted ', true_passes, ' of ', len(examples))
        print('rejected ', false_fails, ' of ', len(negatives))
        
        # list(pl.query("unload_last_source."))
 
        for rn in rulenames:
            list(pl.query("abolish({}/2).".format(rn)))
        # print('243 query ', list(pl.query("listing.")))
        score = fitness_func([[true_passes,false_fails]])[0]
        print(score)
        best_fit[score] = best_fit.get(score, []) + ['gen{}_g{}.pl'.format(gen,child_no)]

for k in reversed(sorted(best_fit.keys()))[-25:]:
    print(k, best_fit[k])
