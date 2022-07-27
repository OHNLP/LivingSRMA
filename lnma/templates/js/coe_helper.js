var coe_helper = {

    // values
    Y: 'Y',
    PY: 'PY',
    PN: 'PN',
    N: 'N',
    NI: 'NI',
    NA: 'NA',

    // risk
    LOW: 'L',
    HIGH: 'H',
    SOME: 'M',

    isNA: function(v) {
        if (v == null || v == 'NA' || v == '') {
            return true;
        }
        return false;
    },

    fmt_value: function(v) {
        if (this.isNA(v)) {
            return 'NA';
        }

        // convert to upper case 
        var _v = v.toLocaleUpperCase();

        if (['Y', 'PY', 'PN', 'N', 'NI'].indexOf(_v)>=0) {
            return _v;

        } else {
            // what???
            return 'NA';
        }
    },

    fmt_domain: function(v) {
        if (this.isNA(v)) {
            return 'NA';
        }

        // convert to upper case 
        var _v = v.toLocaleUpperCase();

        if (['L', 'M', 'H'].indexOf(_v)>=0) {
            return _v;
        } else {
            // what???
            return 'NA';
        }
    },

    /**
     * Get a domain value based on aj and ar
     * 
     * @param {string} aj Assessor judgement
     * @param {string} ar Algorithm result
     * @returns string
     */
    get_domain: function(aj, ar) {
        aj = this.fmt_domain(aj);
        ar = this.fmt_domain(ar);

        // Assessor Judgement has higher priority
        if (aj == this.NA) {
            return ar;
        } else {
            return aj;
        }
    },

    /**
     * Overall risk-of-bias judgement
     * 
     * @param {string} d1 judgement on domain 1
     * @param {string} d2 judgement on domain 2
     * @param {string} d3 judgement on domain 3
     * @param {string} d4 judgement on domain 4
     * @param {string} d5 judgement on domain 5
     * @returns 
     */
    judge_rob_overall: function(d1, d2, d3, d4, d5) {
        // check values first
        d1 = this.fmt_domain(d1);
        d2 = this.fmt_domain(d2);
        d3 = this.fmt_domain(d3);
        d4 = this.fmt_domain(d4);
        d5 = this.fmt_domain(d5);
        
        var ret = this.NA;

        with (this) {
            if (d1 == LOW && d2 == LOW && d3 == LOW && d4 == LOW && d5 == LOW) {
                // low risk of bias for all domains
                ret = LOW;

            } else if (d1 == HIGH || d2 == HIGH || d3 == HIGH || d4 == HIGH || d5 == HIGH) {
                // high risk of bias in at least one domain
                ret = HIGH;
                
            } else {
                var n_some = 0;
                if (d1 == SOME) { n_some += 1; }
                if (d2 == SOME) { n_some += 1; }
                if (d3 == SOME) { n_some += 1; }
                if (d4 == SOME) { n_some += 1; }
                if (d5 == SOME) { n_some += 1; }
                
                if (n_some >= 2) {
                    // some concerns for multiple domains
                    ret = HIGH;
                }

                var n_na = 0;
                if (d1 == NA) { n_na += 1; }
                if (d2 == NA) { n_na += 1; }
                if (d3 == NA) { n_na += 1; }
                if (d4 == NA) { n_na += 1; }
                if (d5 == NA) { n_na += 1; }

                if (n_na == 0 && n_some == 1) {
                    // some concerns in at least one domain for this result, 
                    // but not to be at high risk of bias for any domain
                    ret = SOME;
                }
                
            }
        }

        console.log('* judge_rob_overall:', ret, '<-', d1, d2, d3, d4, d5);
        return ret;
    },

    /**
     * Judge the D1 for risk of bias
     * 
     * @param {string} q1 Q1.1 Allocation sequence random?
     * @param {string} q2 Q1.2 Allocation sequence concealed?
     * @param {string} q3 Q1.3 Baseline imblances suggest a problem?
     * @returns L/M/H/NA
     */
    judge_rob_d1: function(q1, q2, q3) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);

        // Algorithm for suggested judgement of 
        // risk of bias arising from the randomization process
        var ret = this.NA;

        with (this) {
            if (q2 == Y || q2 == PY) {
                if (q1 == Y || q1 == PY || q1 == NI) {
                    if (q3 == N || q3 == PN || q3 == NI) {
                        ret = LOW;

                    } else if (q3 == Y || q3 == PY) {
                        ret = SOME;
                    }

                } else if (q1 == N || q1 == PN) {
                    ret = SOME;
                }

            } else if (q2 == NI) {
                if (q3 == N || q3 == PN || q3 == NI) {
                    ret = SOME;

                } else if (q3 == Y || q3 == PY) {
                    ret = HIGH;
                } 

            } else if (q2 == N || q2 == PN) {
                ret = HIGH;

            } else {
                // q2 is NA
            }
        }
        console.log('* judge_rob_d1:', ret, '<-', q1, q2, q3);
        return ret;
    },

    /**
     * Judge the D2 for risk of bias
     * 
     * Two types, a for effect of assignment to intervention, 
     * b for effect of adhering to intervention.
     * 
     * @param {string} type type of D2
     * @param {string} q1 Q2.1
     * @param {string} q2 Q2.2
     * @param {string} q3 Q2.3
     * @param {string} q4 Q2.4
     * @param {string} q5 Q2.5
     * @param {string} q6 Q2.6
     * @param {string} q7 Q2.7
     * @returns L/M/H/NA
     */
    judge_rob_d2: function(type, q1, q2, q3, q4, q5, q6, q7) {
        if (type == 'a') {
            return this.judge_rob_d2_a(q1, q2, q3, q4, q5, q6, q7);

        } else if (type == 'b') {
            return this.judge_rob_d2_b(q1, q2, q3, q4, q5, q6);

        }

        return this.NA;
    },

    /**
     * Judge the D2 for risk of bias
     * 
     * Domain 2: Risk of bias due to deviations from the intended interventions (effect of assignment to intervention)
     * 
     * @param {string} q1 Q2.1
     * @param {string} q2 Q2.2
     * @param {string} q3 Q2.3
     * @param {string} q4 Q2.4
     * @param {string} q5 Q2.5
     * @param {string} q6 Q2.6
     * @param {string} q7 Q2.7
     * @returns L/M/H/NA
     */
    judge_rob_d2_a: function(q1, q2, q3, q4, q5, q6, q7) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);
        q4 = this.fmt_value(q4);
        q5 = this.fmt_value(q5);
        q6 = this.fmt_value(q6);
        q7 = this.fmt_value(q7);

        // check each parts
        var P1 = this.NA;
        var P2 = this.NA;
        var ret = this.NA;

        with (this) {
            // decide P1
            if ((q1 == N || q1 == PN) && (q2 == N || q2 == PN)) {
                P1 = this.LOW;

            } else if ((q1 == Y || q1 == PY || q1 == NI) || (q2 == Y || q2 == PY || q2 == NI)) {
                if (q3 == N || q3 == PN) {
                    P1 = this.LOW;

                } else if (q3 == NI) {
                    P1 = this.SOME;

                } else if (q3 == Y || q3 == PY) {
                    if (q4 == N || q4 == PN) {
                        P1 = this.SOME;

                    } else if (q4 == Y || q4 == PY || q4 == NI) {
                        if (q5 == Y || q5 == PY) {
                            P1 = this.SOME;

                        } else if (q5 == N || q5 == PN || q5 == NI) {
                            P1 = this.HIGH;

                        } else {
                            // q5 is NA?
                        }
                    }
                }

            } else {
                // has NA in q1 or q2
            }

            // decide P2
            if (q6 == Y || q6 == PY) {
                P2 = this.LOW;

            } else if (q6 == N || q6 == PN || q6 == NI) {
                if (q7 == N || q7 == PN) {
                    P2 = this.SOME;

                } else if (q7 == Y || q7 == PY || q7 == NI) {
                    P2 = this.HIGH;
                }
            }

            // final decision
            if (P1 == LOW && P2 == LOW) {
                ret = this.LOW;

            } else if (P1 == HIGH || P2 == HIGH) {
                ret = this.HIGH;

            } else {
                if (P1 == SOME || P2 == SOME) {
                    ret = this.SOME;
                }
            }
            
        }

        console.log('* judge_rob_d2_a:', ret, '<-', q1, q2, q3, q4, q5, q6, q7);
        return ret;
    },

    /**
     * Judge the D2 for risk of bias
     * 
     * Domain 2: Risk of bias due to deviations from the intended interventions (effect of adhering to intervention)
     * 
     * @param {string} q1 Q2.1
     * @param {string} q2 Q2.2
     * @param {string} q3 Q2.3
     * @param {string} q4 Q2.4
     * @param {string} q5 Q2.5
     * @param {string} q6 Q2.6
     * @param {string} q7 Q2.7
     * @returns L/M/H/NA
     */
    judge_rob_d2_b: function(q1, q2, q3, q4, q5, q6) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);
        q4 = this.fmt_value(q4);
        q5 = this.fmt_value(q5);
        q6 = this.fmt_value(q6);

        // start
        var ret = this.NA;
        
        with (this) {
            function _chk_q6(q6) {
                if (q6 == Y || q6 == PY) {
                    return SOME;

                } else if (q6 == N || q6 == PN || q6 == NI) {
                    return HIGH;
                }

                return NA;
            }

            function _chk_q456(q4, q5, q6) {
                if ((q4 == NA || q4 == N || q4 == PN) && (q5 == NA || q5 == N || q5 == PN)) {
                    return LOW;

                } else if ((q4 == Y || q4 == PY || q4 == NI) || (q5 == Y || q5 == PY || q5 == NI)) {
                    return _chk_q6(q6);
                }

                return NA;
            }

            if ((q1 == N || q1 == PN) && (q2 == N || q2 == PN)) {
                ret = _chk_q456(q4, q5, q6);

            } else if ((q1 == Y || q1 == PY || q1 == NI) || (q2 == Y || q2 == PY || q2 == NI)) {

                if (q3 == NA || q3 == Y || q3 == PY) {
                    ret = _chk_q456(q4, q5, q6);

                } else if (q3 == N || q3 == PN || q3 == NI) {
                    ret = _chk_q6(q6);
                }
            }

        }

        console.log('* judge_rob_d2_b:', ret, '<-', q1, q2, q3, q4, q5, q6);
        return ret;
    },


    /**
     * Judge the D3 for risk of bias
     * 
     * @param {string} q1 Q3.1
     * @param {string} q2 Q3.2
     * @param {string} q3 Q3.3
     * @param {string} q4 Q3.4
     * @returns L/M/H/NA
     */
    judge_rob_d3: function(q1, q2, q3, q4) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);
        q4 = this.fmt_value(q4);

        // check
        var ret = this.NA;

        with (this) {
            if (q1 == Y || q1 == PY) {
                ret = LOW;

            } else if (q1 == N || q1 == PN || q1 == NI) {
                if (q2 == Y || q2 == PY) {
                    ret = LOW;

                } else if (q2 == N || q2 == PN || q2 == NI) {
                    if (q3 == N || q3 == PN) {
                        ret = LOW;

                    } else if (q3 == Y || q3 == PY || q3 == NI) {
                        if (q4 == N || q4 == PN) {
                            ret = this.SOME;

                        } else if (q4 == Y || q4 == PY || q4 == NI) {
                            ret = this.HIGH;

                        }
                    }
                }
            }

        }

        console.log('* judge_rob_d3:', ret, '<-', q1, q2, q3, q4);
        return ret;
    },

    /**
     * Judge the D4 for risk of bias
     * 
     * @param {string} q1 Q4.1
     * @param {string} q2 Q4.2
     * @param {string} q3 Q4.3
     * @param {string} q4 Q4.4
     * @param {string} q5 Q4.5
     * @returns L/M/H/NA
     */
    judge_rob_d4: function(q1, q2, q3, q4, q5) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);
        q4 = this.fmt_value(q4);
        q5 = this.fmt_value(q5);

        // check
        var ret = this.NA;

        with (this) {
            if (q1 == Y || q1 == PY) {
                ret = this.HIGH;

            } else if (q1 == N || q1 == PN || q1 == NI) {
                if (q2 == Y || q2 == PY) {
                    ret = this.HIGH;

                } else if (q2 == N || q2 == PN) {
                    if (q3 == N || q3 == PN) {
                        ret = LOW;

                    } else if (q3 == Y || q3 == PY || q3 == NI) {
                        if (q4 == N || q4 == PN) {
                            ret = LOW;

                        } else if (q4 == Y || q4 == PY || q4 == NI) {
                            if (q5 == N || q5 == PN) {
                                ret = this.SOME;

                            } else if (q5 == Y || q5 == PY || q5 == NI) {
                                ret = this.HIGH;
                            }
                        }
                    }
                } else if (q2 == NI) {
                    if (q3 == N || q3 == PN) {
                        ret = this.SOME;

                    } else if (q3 == Y || q3 == PY || q3 == NI) {
                        if (q4 == N || q4 == PN) {
                            ret = this.SOME;

                        } else if (q4 == Y || q4 == PY || q4 == NI) {
                            if (q5 == N || q5 == PN) {
                                ret = this.SOME;

                            } else if (q5 == Y || q5 == PY || q5 == NI) {
                                ret = this.HIGH;
                            }
                        }
                    }
                }
            }

        }

        console.log('* judge_rob_d4:', ret, '<-', q1, q2, q3, q4, q5);
        return ret;
    },


    /**
     * Judge the D4 for risk of bias
     * 
     * @param {string} q1 Q5.1
     * @param {string} q2 Q5.2
     * @param {string} q3 Q5.3
     * @returns L/M/H/NA
     */
    judge_rob_d5: function(q1, q2, q3) {
        // check values first
        q1 = this.fmt_value(q1);
        q2 = this.fmt_value(q2);
        q3 = this.fmt_value(q3);

        // start judgement
        var ret = this.NA;

        with (this) {

            if ((q2 == Y || q2 == PY) || (q3 == Y || q3 == PY)) {
                ret = HIGH;

            } else if ((q2 == N || q2 == PN) && (q3 == N || q3 == PN)) {
                if (q5 == Y || q5 == PY) {
                    ret = LOW;

                } else if (q5 == N || q5 == PN || q5 == NI) {
                    ret = this.SOME;

                }
            } else if (q2 == NI || q3 == NI) {
                ret = this.SOME;
            }

        }

        console.log('* judge_rob_d5:', ret, '<-', q1, q2, q3);
        return ret;
    },

    get_overall_coe: function(decision) {
        var risk_of_bias = parseInt(''+decision.risk_of_bias);
        var inconsistency = parseInt(''+decision.inconsistency);
        var indirectness = parseInt(''+decision.indirectness);
        var imprecision = parseInt(''+decision.imprecision);
        var publication_bias = parseInt(''+decision.publication_bias);

        var vals = [
            risk_of_bias,
            inconsistency,
            indirectness,
            imprecision,
            publication_bias
        ];
        var cnt = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0
        };
        for (let i = 0; i < vals.length; i++) {
            const val = vals[i];
            cnt[val] += 1;
        }

        var ret = 0;
        if (cnt[1] == 5) {
            // 1 in all factors
            ret = 1;
            
        } else if (cnt[1] == 4 && cnt[2] == 1) {
            // 2 in any one factor
            ret = 2;

        } else if ((cnt[1] == 4 && cnt[3] == 1) || 
                   (cnt[1] == 3 && cnt[2] == 2) ||
                   (cnt[1] == 3 && cnt[2] == 1 && cnt[3] == 1)) {
            // 3 in any one factor or 2 in two factors
            ret = 3;

        } else if (cnt[4] >= 1 || cnt[3] >= 2 || cnt[2] >= 3) {
            // 4 in any one factor, or 3 in two factors, or 2 in three
            ret = 4;

        } else {
            // what???
        }

        // convert to string
        return '' + ret;
    },

    /**
     * Get the value of a specific domain in coe
     * 
     * @param {Object} coe Certainty of Evidence object
     */
    get_val_from_coe: function(coe, type, domain) {
        // the CoE may be not available
        if (typeof(coe) == 'undefined' ||
            coe == null) {
            return 'NA';
        }

        // may not source type? aj or 
        if (!coe.hasOwnProperty(type)) {
            return 'NA';
        }

        // may not have decision?
        if (!coe[type].hasOwnProperty('decision')) {
            return 'NA';
        }

        // no such domain???
        if (!coe[type].decision.hasOwnProperty(domain)) {
            if (domain == 'overall') {
                // need to convert the 
                return this.get_overall_coe(coe[type].decision);
            } else {
                return 'NA';
            }
        }

        var val = coe[type].decision[domain];

        return val;
    },

    val_to_label: function(val, domain) {
        // convert to string
        var v = "" + val;
        var ret = "NA";

        // check if the followings
        if (['risk_of_bias', 'imprecision', 'inconsistency', 'indirectness'].includes(domain)) {
            if (['0', '1', '2', '3', '4'].includes(v)) {
                ret = {
                    '0': 'Not specified',
                    '1': 'No serious',
                    '2': 'Serious',
                    '3': 'Very serious',
                    '4': 'Very serious'
                }[v];
            } else {
                ret = 'NA';
            }

        } else if (['incoherence', 'intransitivity'].includes(domain)) {
            if (['0', '1', '2', '3'].includes(v)) {
                ret = {
                    '0': 'Not applicable',
                    '1': 'No serious',
                    '2': 'Serious',
                    '3': 'Very serious'
                }[v];
            } else {
                ret = 'NA';
            }

        } else if (domain == 'publication_bias') {
            if (['0', '1', '2'].includes(v)) {
                ret = {
                    '0': 'Not applicable',
                    '1': 'Undetected',
                    '2': 'Strongly suspected'
                }[v];
            } else {
                ret = 'NA'
            }

        } else if (domain == 'importance') {
            if (['0', '1', '2']) {
                ret = {
                    '0': 'Not applicable',
                    '1': 'Important',
                    '2': 'Critical'
                }[v];
            } else {
                ret = 'NA';
            }

        } else if (domain == 'overall') {
            if (['0', '1', '2', '3', '4'].includes(v)) {
                ret = {
                    '0': 'NA',
                    '1': 'Very Low',
                    '2': 'Low',
                    '3': 'Moderate',
                    '4': 'High'
                }[v];
            } else {
                ret = 'NA'
            }

        } else {
            ret = v;
        }

        return ret;
    }
};
