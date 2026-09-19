# ------------------------------------------------------------------
# File:    source/core/meanline/tpr_convergence.py
# Author:  Jonas Scholz
# Purpose: Outer-loop machine TPR check and secant RPM update.
# ------------------------------------------------------------------

# Verbatim move of meanline.py:598-679. Only indentation, the state-dict
# prefix and translated comments differ. Returns True once the overall
# pressure ratio has converged (caller breaks the outer loop).

from source.logging import debug_log


def update_tpr(s):
    """Check machine TPR, update the RPM guess. True = converged."""
    i_st = s['i_st']

    # Overall Mashine Performance
    s['TPR_M']=s['p_t3'][i_st-1]/s['p_t1'][0]# TPR over all stages
    s['TPR_history'].append(s['TPR_M'])
    debug_log.debug(f"TPR_M={s['TPR_history']}", context="meanline_TPR")
    debug_log.debug(f"iter count = {s['iter_count_TPR']}", context="meanline_TPR")
    debug_log.debug(f"length TPR_history 1 = {len(s['TPR_history'])}", context="meanline_TPR")


    # Initialize both secant values
    if len(s['n_history']) == 1:
        # Adjust RPM to change TPR to match designed TPR
        if s['TPR_M'] < s['design_TPR']:
            # reduce RPM

            if s['iter_count_TPR'] == 0:
                s['n_history'].append(s['n_history'][0]*1.05)

        elif s['TPR_M'] > s['design_TPR']:
            # increase RPM

            if s['iter_count_TPR'] == 0:
                s['n_history'].append(s['n_history'][0]*0.95)


    # Secant Method to Calculate the next RPM
    if len(s['TPR_history']) >= 2:
        # Set current and old TPR Value for the Calculation
        curr_TPR = s['TPR_history'][-1]
        old_TPR = s['TPR_history'][-2]

        # Set current and old n Value for the Calculation
        curr_n = s['n_history'][-1]
        old_n = s['n_history'][-2]

        # Secant Calculation
        if abs(curr_TPR - old_TPR) > 1e-6: # Prevent Division by Zero
            next_n = curr_n - (curr_TPR - s['design_TPR']) * (curr_n - old_n) / ((curr_TPR-s['design_TPR']) - (old_TPR-s['design_TPR']))
        else:
            # Fallback strategy in case of no or very small TPR changes but not near the Design TPR
            tpr_warn = "Warning: No significant TPR changes. Applying a small linear adjustment."
            print(tpr_warn)
            debug_log.debug(tpr_warn, context="meanline_TPR")
            if curr_TPR < s['design_TPR']:
                next_n = curr_n * 1.02
            else:
                next_n = curr_n * 0.98

    else:
        # First iteration not enough values to calculate using the secant methode
        # Using second RPM value instead
        next_n = s['n_history'][s['iter_count_TPR'] + 1]

    # Set the old mean Diameter as the next guess for the inner loop for faster iterations

    # Update the List for the next Iteration
    s['n_history'].append(next_n)

    # Set global RPM to current guess

    s['n'] = [next_n] * i_st

    # Increase Iteration Count
    s['iter_count_TPR'] +=1







    if abs(s['TPR_M'] - s['design_TPR']) < s['conv_limit_TPR']:
        tpr_done = f"\nTotal Pressure Ratio has converged after {s['iter_count_TPR']} iterations. TPR = {s['TPR_M']:.3f} at RPM = {s['n'][0]:.0f}, massflow = {s['mflow']}"
        print(tpr_done)
        debug_log.debug(tpr_done, context="meanline_TPR")
        s['n'] = [curr_n] * i_st
        return True
    return False


def report_tpr_failure(s):
    """Warning for the outer while-else path (no convergence in 50 steps)."""
    tpr_fail = f"Warning: Total Pressure Ratio did not converge after {s['max_iter_steps_TPR']} iterations."
    print(tpr_fail)
    debug_log.debug(tpr_fail, context="meanline_TPR")
