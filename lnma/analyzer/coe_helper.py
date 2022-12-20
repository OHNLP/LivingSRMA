
L0 = '0' # Not applicable
L1 = '1' # No serious
L2 = '2' # Serious 
L3 = '3' # Very serious
L4 = '4' # ?

def judge_risk_of_bias(
    is_all_low, 
    is_all_high, 
    subg_pval, 
    per_high_stus,
    user_judgement=None
):
    if user_judgement is not None:
        return user_judgement

    if is_all_low:
        return L1
    
    if is_all_high:
        return L2
    
    if subg_pval >= 0.05:
        return L1
    else:
        if per_high_stus >= 0.5:
            return L3
        else:
            return L2


def judge_inconsistency(
    i2
):
    '''
    Judge the inconsistency by i^2
    '''
    if i2 < 0.5:
        return L1

    else:
        return L2


def judge_publication_bias(
    n_stus, 
    eggers_test_p_value
):
    '''
    Judge publication bias by number of studies and Egger's Test P-value
    '''
    if n_stus < 10:
        return L0 # Not applicable

    if eggers_test_p_value < 0.05:
        return L2 # Strongly suspected

    return L1 # Undetected


def judge_imprecision():
    return L0


def judge_indirectness():
    return L0