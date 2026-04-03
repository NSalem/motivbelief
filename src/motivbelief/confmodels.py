import numpy as np
from scipy.stats import norm
from motivbelief.psychofun import psychofun_inv

def simulate_act_conf(df, pardict):
    '''
    Simulate action and confidence for a given dataframe of stimuli and incentives.
    
    df: dataframe of stimuli and incentives
        'stim': stimulus
        'incentive': incentive
        'a': action (optional, to simulate observed condition)
    pardict: dictionary of parameters
    
    returns: dataframe of simulated action and confidence
        'stim': stimulus
        'incentive': incentive
        'a': action
        'conf': confidence
    '''
        
    sigma = pardict.get('sigma', 1e-4) # noise at the individual channel level
    choice_bias = pardict.get('choice_bias', 0)
    p_lapse = pardict.get('p_lapse', 0)
    sigma_conf = pardict.get('sigma_conf', 0)
    conf_bias = pardict.get('conf_bias', 0)
    w_0 = pardict.get('w_0', 0.0)
    w_v = pardict.get('w_v', 0.0)    # Valence bias (default 0) that is modulated by incentive.
    mismatch_coef = pardict.get('mismatch_coef', 1)     # Mismatch handling parameter (scaling the mismatch effect)
   
    # Get stimuli and incentives from dataframe
    stim = df['stim'].values
    
    #check for actions already in df
    if 'a' in df.columns:
        a = df['a'].values
    else:
        a = None
    
    # 'incentive' is used for the valence effect:
    incentive = df.get('incentive', np.zeros_like(stim)).values

    # get noise for Xbel (double the variance of the individual channels, since it's the difference)
    sigma_diff = np.sqrt(2 * sigma ** 2)
    
    stim = np.array(stim)
    ntrials = len(stim)

    s_r = np.abs(stim * (stim > 0))   # coherence towards right
    s_l = np.abs(stim * (stim < 0))  # coherence towards left

    noise_r = np.random.normal(0, sigma, ntrials)
    noise_l = np.random.normal(0, sigma, ntrials)
    
    # Lapse in decision: if lapseTrial==1, evidence is set to 0.
    lapse_trial = (np.random.rand(ntrials) <= p_lapse).astype(int)


    xr = (1 - lapse_trial) * (s_r + noise_r)
    xl = (1 - lapse_trial) * (s_l + noise_l)

    Xdiff = xr - xl  # covert evidence before bias
    # Compute decision if not provided

    choice_covert = np.sign(xr - xl + choice_bias)*(1 - lapse_trial)

    if a is None:
        a = choice_covert
        a[a == 0] = np.random.choice([-1, 1], size=np.sum(a == 0))

    # Inversion of negative values
    xl_pos = xl * (xl > 0) - xr * (xr < 0)
    xr_pos = xr * (xr > 0) - xl * (xl < 0)

    # Compute evidence for chosen and unchosen options directly.
    x_chosen = np.where(a > 0, xr_pos, xl_pos)
    x_unchosen = np.where(a > 0, xl_pos, xr_pos)
    
    # Recompute covert choice from the confidence evidence as a placeholder.
    mismatch_indicator = ((a != choice_covert) & (choice_covert != 0)).astype(float)
 
    # Define a factor that equals mismatch_coef on mismatch trials and 1 on match trials.
    factor = np.where(mismatch_indicator == 1, mismatch_coef, 1.0)
    
    # Compute the weight for chosen and unchosen evidence
    # When no mismatch, weight = w0 + (w1 + w_v * incentive); when mismatch, the bias term is scaled by mismatch_coef.
    w = 1 + factor * (w_0 + w_v * incentive)
    w_u = 1- factor * (w_0 + w_v * incentive)
    
    # Now compute the confidence evidence as the weighted difference:
    conf_noise = np.random.normal(0, sigma_conf, ntrials)
    Xconf = w * x_chosen - w_u * x_unchosen + conf_noise + conf_bias

    sigma_total = np.sqrt(sigma_diff**2 + sigma_conf**2)   
    
    ## Bayesian confidence transformation ##
    muHat = psychofun_inv([choice_bias, sigma_total, p_lapse], 0.75)
    xlimU = norm.ppf(1 - 1e-10, muHat, sigma_total)
    xlimL = norm.ppf(1e-10, muHat, sigma_total)
    XconfTrunc = np.clip(Xconf, xlimL, xlimU)
    pC = norm.pdf(XconfTrunc, muHat, sigma_total)
    pU = norm.pdf(XconfTrunc, -muHat, sigma_total)
    conf = pC / (pC + pU)
    conf = conf.clip(1e-4, 1 - 1e-4)
    
    df = df.copy()
    df['a'] = a.T
    df['Xdiff'] = Xdiff.T
    df['correct'] = (np.sign(a) == np.sign(stim))*1
    df['conf'] = conf.T*100
    
    return df
