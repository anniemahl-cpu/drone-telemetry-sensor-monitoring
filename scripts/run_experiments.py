from pathlib import Path

from droneguard.experiments import sampling_rate_experiment

output = Path("reports")
output.mkdir(exist_ok=True)
result = sampling_rate_experiment()
result.to_csv(output / "sampling_rate_experiment.csv", index=False)
print(result.to_string(index=False))

