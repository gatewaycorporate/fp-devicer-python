import random

from devicer.benchmarks.data_generator import create_base_fingerprint, mutate

fp_identical = create_base_fingerprint(1)

random.seed(101)
fp_very_similar = mutate(fp_identical, "low")

random.seed(202)
fp_similar = mutate(fp_identical, "medium")

random.seed(303)
fp_different = mutate(fp_identical, "high")

random.seed(404)
fp_very_different = mutate(fp_identical, "extreme")
