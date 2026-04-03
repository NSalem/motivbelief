#%% 

import numpy as np
import pandas as pd

from motivbelief.psychofun import psychofun
from motivbelief.confmodels import simulate_act_conf
import pickle
import os


sLevels = [-38,-9,-5,-3,-1,1,3,5,9,38]
pRightObs = [0.0308,0.1675,0.2842,0.34,0.4496,0.5504, 0.66, 0.7158, 0.8325, 0.9692] 
incLevels = [-1,0,1]

cohs = np.unique(np.abs(sLevels))
s = []
inc = []
nreps = 8

for irep in range(nreps):
    for iinc in incLevels:
        for ic in sLevels:
            s.append(ic)
            inc.append(iinc)

s =np.array(s)
#inc = np.array(inc)
    
files = ["results/fits_choice/pars_choice_exp1a_Free.p",
         "results/fits_choice/pars_choice_exp2_Free.p"]

os.makedirs("results/sims", exist_ok=True)


pars = []
for ifile in files:
    f = open(ifile,"rb")
    fit = pickle.load(f)
    # get choice parameters
    pars.append(fit['pars_choice'])

pars = np.concatenate(pars)

##specify incentive bias magnitude 
w_v = 0.15

##specify models 
model_names = ['act','intent','confirm']
models = [
    {'w_v':w_v,'mismatch_coef':1},
    {'w_v':w_v,'mismatch_coef':-1},
    {'w_v':w_v,'mismatch_coef':0},
]

#make function to simulate action based on pright for the corresponding slevel
def sim_observed_action(s,pRight):
    p =  np.array([np.interp(s, sLevels, pRight) for s in s])
    #action -1 or 1
    a = np.random.binomial(1,p)
    a = 2*a-1
    return a,p

#%%simulate for different mismatch hanlding stragies
np.random.seed(42)
df_sim_all_models = []
for imod, model in enumerate(models): 
    df_sim_mod = pd.DataFrame()
    for nsub in range(len(pars)):
            for ngroup,choiceType in enumerate(['Free','Observed']):
                
                df = pd.DataFrame({'stim':s,'incentive':inc}) 
                pars_choice = pars[nsub]

                pardict = model.copy()
                if choiceType=='Observed':
                    a,_ = sim_observed_action(s,pRightObs)
                    df['a'] = a

                pardict.update({'sigma':pars_choice[0],
                                'choice_bias':pars_choice[1],
                                'p_lapse':pars_choice[2],
                                })
                   
                df_sim_sub = simulate_act_conf(df,pardict)
                df_sim_sub['participant'] = nsub+1
                df_sim_sub['choiceType'] = choiceType
                df_sim_mod = pd.concat([df_sim_mod,df_sim_sub])
    
    df_sim_mod['coh'] = np.abs(df_sim_mod['stim'])
    # Simulated datasets live under results/sims
    df_sim_mod.to_csv(f"results/sims/sims_{model_names[imod]}.csv", index=False)