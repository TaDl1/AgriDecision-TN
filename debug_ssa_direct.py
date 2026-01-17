
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from services.small_sample_analytics import SmallSampleAnalytics

print("Imported SSA from:", SmallSampleAnalytics)

ssa = SmallSampleAnalytics()
res = ssa.calculate_rar(n_followed_wait=0, n_ignored=0, failures_ignored=0, avg_loss=100)
print("Result for 0,0:", res)

res2 = ssa.calculate_rar(n_followed_wait=10, n_ignored=0, failures_ignored=0, avg_loss=100)
print("Result for 10,0:", res2)
