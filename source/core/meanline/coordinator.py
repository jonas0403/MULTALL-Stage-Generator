# ------------------------------------------------------------------
# File:    source/core/meanline/coordinator.py
# Author:  Jonas Scholz
# Purpose: Outer TPR loop driving the split meanline step modules.
# ------------------------------------------------------------------

# Same meanline() signature and behavior as meanline.py:24. The outer
# per-stage loop (old :149-154) and TPR while-loop (old :151, :676) stay here;
# all computation moved to initialization/stage_iteration/tpr_convergence/
# results. meanline.py itself is untouched (backup for comparison).

from source.core.meanline.initialization import init_state
from source.core.meanline.stage_iteration import iterate_stage
from source.core.meanline.tpr_convergence import update_tpr, report_tpr_failure
from source.core.meanline.results import build_results


def meanline(thermo_data, meanline_data, diameter_data, plot_channel_contour):
    s = init_state(thermo_data, meanline_data, diameter_data)

    # --- MAINLOOP ---
    # Iterating over the stages
    while s['iter_count_TPR'] < s['max_iter_steps_TPR']:

        # Calculate all Stages
        for i in range(s['i_st']):
            iterate_stage(s, i)

        if update_tpr(s):
            break
    else: # This 'else' block executes if the while loop completes WITHOUT a 'break'
        report_tpr_failure(s)

    return build_results(s, plot_channel_contour)
