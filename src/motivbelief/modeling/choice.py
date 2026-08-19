
import numpy as np
from scipy.stats import norm,logistic
import pandas as pd
import os
from scipy.optimize import minimize

from motivbelief.modeling.optimize import log_prior, DEFAULT_CHOICE_PRIORS

def psychofun(theta,stim, pd = 'normal'):
    """Psychometric function based on logistic/normal CDF and lapses"""
    
    if pd == 'logistic':
        dist = logistic
    elif pd == 'normal':
        dist = norm
        
    mu = theta[0]          # bias
    sigma = theta[1]       # slope/noise
    lapse = theta[2]       # lapse rate
    if len(theta) == 4:    # lapse bias
        lapse_bias = theta[3];
    else:
        lapse_bias = 0.5   # if theta has only three elements, assume symmetric lapses
    
    p_right = dist.cdf(stim,loc=-mu,scale=sigma)    # Probability of responding "rightwards", without lapses
    p_right = lapse*lapse_bias + (1-lapse)*p_right # Adding lapses

    return p_right

def psychofun_inv(theta,p_right, pd= 'normal'):
    
    """Psychometric function based on logistic/normal CDF and lapses"""

    if pd == 'logistic':
        dist = logistic
    elif pd == 'normal':
        dist = norm
        
    mu = theta[0]          # bias
    sigma = theta[1]       # slope/noise
    lapse = theta[2]       # lapse rate
    if len(theta) == 4:    # lapse bias
        lapse_bias = theta[3];
    else:
        lapse_bias = 0.5   # if theta has only three elements, assume symmetric lapses
    
    # p_right = norm.cdf(stim,loc=mu,scale=sigma)    # Probability of responding "rightwards", without lapses
    # p_right = lapse*lapse_bias + (1-lapse)*p_right # Adding lapses
    p_right_prime = (p_right-lapse*lapse_bias)/(1-lapse)    
    stim = dist.ppf(p_right_prime,loc=mu,scale = sigma)
    
    return stim

def psychofun_ll(params,df,cfg,stimcol='stim',choicecol='a'):
    stim= np.array([df[stimcol]])
    a = np.array(df[choicecol])
    # conf = np.array(df['conf'])
    pardict = {}
    for npar, ipar in enumerate(cfg['parnames']):
        pardict[ipar] = params[npar]

    for key,value in cfg['fixedpars'].items():
        pardict[key] = value
    sens_noise = pardict.get('sens_noise', 0)
    sens_bias = pardict.get('sens_bias', 0)
    lapse = pardict.get('p_lapse', 0)

    stim = np.array(stim,dtype=float)
    ntrials = stim.shape[1]

    pRight = norm.cdf(stim+sens_bias,0,np.sqrt(2*sens_noise**2))
    pRight = lapse*0.5 + (1-lapse)*pRight
    pA = pRight*(a==1)+(1-pRight)*(a==-1)
    pA = pA.clip(1e-10,1-1e-10)
    ll = np.nansum(np.log(pA))
    if not np.isfinite(ll):
        return -np.inf

    ll_prior = log_prior(pardict, cfg['parnames'], cfg.get('priors', DEFAULT_CHOICE_PRIORS))
    if not np.isfinite(ll_prior):
        return -np.inf

    return ll + ll_prior
