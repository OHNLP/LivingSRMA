
L0 = '0' # Not applicable
L1 = '1' # No serious
L2 = '2' # Serious 
L3 = '3' # Very serious
L4 = '4' # ?

def judge_risk_of_bias(vals):
    '''
    Judge the risk of bias by given conditions

    vals contains:
    {
        'n_rob_na': n_rob_na,
        'is_all_low': is_all_low,
        'is_all_high': is_all_high,
        'subg_pval': subg_pval,
        'per_high_stus': per_high_stus,
        'user_judgement': cfg['rob_user_judgement']
    }
    '''
    if vals['n_rob_na'] != 0:
        # some studies are not evaluated by reviewer yet
        return L0

    if vals['user_judgement'] is not None or \
        vals['user_judgement'] != '':
        return vals['user_judgement']

    if vals['is_all_low']:
        return L1
    
    if vals['is_all_high']:
        return L2
    
    if vals['subg_pval'] >= 0.05:
        return L1
    else:
        if vals['per_high_stus'] >= 0.5:
            return L3
        else:
            return L2


def judge_inconsistency(vals):
    '''
    Judge the inconsistency by i^2

    vals contains
    {
        'i2': i2,
        'heter_pval': heter_pval
    },
    '''
    if (vals['i2'] < 0.5 or vals['heter_pval'] < 0.1):
        return L1

    else:
        return L2


def judge_publication_bias(
    vals
):
    '''
    Judge publication bias by number of studies and Egger's Test P-value

    vals contains:
    {
        'n_studies': n_studies,
        'egger_test_p_value': egger_test_p_value,
        'pooled_sm': pooled_sm,
        'adjusted_sm': adjusted_sm,
        'difference_sm': difference_sm
    }
    '''
    if vals['n_studies'] < 10:
        return L1 # Not serious

    if vals['egger_test_p_value'] >= 0.05:
        return L1 # Not serious

    if vals['difference_sm'] > 0.2:
        return L2 # Serious

    else:
        return L1 # Not serious


def judge_imprecision(
    vals
):
    '''
    the vals contains:
    {
        't': imp_t,
        'is_t_user_provided': cfg['is_t_user_provided'],
        'sm': pma_pooled_effect,
        'ci_of_sm': ci_of_sm,
        'is_relative_effect_large': is_relative_effect_large,
        'p1': p1,
        'rd': imp_rd,
        'ci_of_rd': ci_of_rd,
        'is_t_included_in_ci_of_rd': is_t_included_in_ci_of_rd,
        'is_both_ts_included_in_ci_of_rd': is_both_ts_included_in_ci_of_rd,
        'is_both_200p1000_included_in_ci_of_rd': is_both_200p1000_included_in_ci_of_rd,
        'ois': OIS,
        'ma_size': ma_size
    },
    '''
    if (vals['is_t_included_in_ci_of_rd']):
        if (vals['is_t_user_provided']):
            if (vals['is_both_ts_included_in_ci_of_rd']):
                return L4
            else:
                return L3
        else:
            if (vals['is_both_200p1000_included_in_ci_of_rd']):
                return L4
            else:
                return L3
    else:
        if (vals['is_relative_effect_large']):
            if (vals['ma_size'] >= vals['ois']):
                return L1
            elif (vals['ma_size'] >= vals['ois'] * 0.5):
                return L2
            else:
                return L3
        else:
            return L1


def judge_indirectness(
    vals
):
    '''
    Judge indirectness by the numbers of each category

    vals contains:
    {
        "n_very_close": n_very_close,
        "percentage_very_close": percentage_very_close,
        "n_moderately_close": n_moderately_close,
        "n_not_close": n_not_close,
        "n_ind_na": n_ind_na,
        "n_studies": n_studies
    }
    '''
    if vals['n_studies'] == 0:
        return L0

    if vals['n_ind_na'] > 0:
        return L0

    # get the percentage of very close studies
    percentage_very_close = vals['n_very_close'] / vals['n_studies']

    if percentage_very_close >= 0.75:
        return L1
    
    if vals['n_not_close'] == 0:
        return L2

    return L3
