
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
        return L0, "RR_ROB_L0_01", "Not all studies are evaluated"

    if vals['user_judgement'] is None:
        pass
    elif vals['user_judgement'] == '':
        pass
    else:
        # I don't why but user said something
        return vals['user_judgement'], "RR_ROB_USER_JUDGEMENT", "User judgement"

    if vals['is_all_low']:
        return L1, "RR_ROB_L1_01", "All studies are low risk"
    
    if vals['is_all_high']:
        return L2, "RR_ROB_L2_01|All studies are high risk or some concerns"
    
    if vals['subg_pval'] >= 0.05:
        return L1, "RR_ROB_L1_02", "A few studies are high risk or some concerns but not significant"
    else:
        if vals['per_high_stus'] >= 0.5:
            return L3, "RR_ROB_L3_01", "Most studies are high risk or some concerns"
        else:
            return L2, "RR_ROB_L2_02", "Some studies are high risk or some concerns"


def judge_inconsistency(vals):
    '''
    Judge the inconsistency by i^2

    vals contains
    {
        'i2': i2,
        'heter_pval': heter_pval,
        'major_sm_cate': major_sm_cate,
        'major_sm_cnt': major_sm_cnt,
        'is_major_in_same_category': is_major_in_same_category,
    },
    '''
    if (vals['i2'] < 0.5 or vals['heter_pval'] < 0.1):
        return L1, "RR_INC_L1_01", "I-sq is less than 50%"

    if (vals['is_major_in_same_category']):
        return L1, "RR_INC_L1_02", "Most of the studies' point estimates within the same category of the pooled effect size"

    else:
        return L2, "RR_INC_L2_01", "Most of the studies' point estimates are not within the same category of the pooled effect size"


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
        return L0, "RR_PBB_L0_01", "Not enough studies for evaluation"

    if vals['egger_test_p_value'] >= 0.05:
        return L1, "RR_PBB_L1_01", "Egger's regression test P-value is greater than 0.05"

    if vals['difference_sm'] > 0.2:
        return L2, "RR_PBB_L2_01", "Adjusted trim/fill estimate shows >20% less benefit than pooled estimate"

    else:
        return L1, "RR_PBB_L1_02", "Adjusted trim/fill estimate shows <20% less benefit than pooled estimate"


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
                return L4, "RR_IMP_L4_01", "Both -/+ user-provided T are included in the CI of RD"
            else:
                return L3, "RR_IMP_L3_01", "Only the user-provided T is included in the CI of RD"
        else:
            if (vals['is_both_200p1000_included_in_ci_of_rd']):
                return L4, "RR_IMP_L4_02", "Both -/+ 200/1,000 are included in the CI of RD"
            else:
                return L3, "RR_IMP_L3_02", "Only the null(0) is included in the CI of RD"
    else:
        if (vals['is_relative_effect_large']):
            if (vals['ma_size'] >= vals['ois']):
                return L1, "RR_IMP_L1_01", "The CI of RD doesn't include T and the MA size is greater than OIS"

            elif (vals['ma_size'] >= vals['ois'] * 0.5):
                return L2, "RR_IMP_L2_01", "The CI of RD doesn't include T and the MA size is between 50-100% OIS"

            else:
                return L3, "RR_IMP_L3_03", "The CI of RD doesn't include T and the MA size is less than 50% OIS"
        else:
            return L1, "RR_IMP_L1_02", "The CI of RD doesn't include T and the relative effect is not large"


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
        return L0, 'RR_IND_L0_01', "Not enough studies"

    if vals['n_ind_na'] > 0:
        return L0, 'RR_IND_L0_02', "Some studies are not evaluated"

    # get the percentage of very close studies
    percentage_very_close = vals['n_very_close'] / vals['n_studies']

    if percentage_very_close >= 0.75:
        return L1, "RR_IND_L1_01", ">75% of studies show very close"
    
    if vals['n_not_close'] == 0:
        return L2, "RR_IND_L2_01", "<75% of studies show very close and none is not close"

    return L3, "RR_IND_L3_01", "<75% of studies show very close and >1 is not close"
