import re
import subprocess
import statistics
import textwrap

if __name__ == "__main__":
    num_examples = 50

    lean_results = []
    hydra_default = []
    hydra_no_width_cmd = []

    lean_dir = "/Users/user/Projects/lean-mlir"
    hydra_dir = "/Users/user/Projects/souper"

    timeout_s = 30
    num_runs = 3

    lean_regex = re.compile(r"\[Elab\.command\]\s+\[(\d+\.\d+)\]")
    hydra_regex = re.compile(r"Took (\d+\.\d+) seconds")

    avg_time_per_test_case = {}

    for i in range(1, num_examples + 1):
        print(f"------  Processing Test {i} ------------")

        hydra_default_cmd = [
            f"{hydra_dir}/cmake-build-debug/generalize",
            "-relational",
            "-souper-debug-level=5",
            f"hydra-tests/{i}.opt",
        ]

        hydra_no_width_cmd = hydra_default_cmd + ["-no-width"]

        command_by_name = {
            "lean": [
                "lake",
                "env",
                "lean",
                f"{lean_dir}/SSA/Experimental/Bits/Fast/GeneralizerTests/{i}.lean",
            ],
            "hydra": hydra_default_cmd,
            "hydra-no-width": hydra_no_width_cmd,
        }

        cwd_by_name = {
            "lean": lean_dir,
            "hydra": hydra_dir,
            "hydra-no-width": hydra_dir,
        }

        regex_by_name = {
            "lean": lean_regex,
            "hydra": hydra_regex,
            "hydra-no-width": hydra_regex,
        }

        for name, command in command_by_name.items():
            print(f"Running {name} command: {command}")
            try:
                time_total = 0
                for j in range(num_runs):
                    result = subprocess.run(
                        command,
                        cwd=cwd_by_name[name],
                        capture_output=True,
                        text=True,
                        timeout=timeout_s,
                    )
                    output = str(result.stdout + "\n" + result.stderr)

                    if j == 0:
                        print(f"{name} output: {output}")

                    regex = regex_by_name[name]
                    match = regex.search(output)
                    if not match:
                        raise ValueError(
                            f"Could not match regex after running {command} "
                        )

                    duration = float(match.group(1))
                    print(f"Parsed duration for command: {duration}")

                    time_total += duration

                avg_time = time_total / num_runs

                res_for_name = avg_time_per_test_case.get(name, {})
                res_for_name[i] = round(avg_time, 3)
                avg_time_per_test_case[name] = res_for_name

            except subprocess.TimeoutExpired as e:
                print(f"TIMEOUT: {name} command timed out for test case {i}")
            except subprocess.CalledProcessError as e:
                print(f"FAILURE: {name} command failed:")
                print(e.stdout)
                print(e.stderr)

        print(
            f"Average Time Taken Per Test Case After Run {i}: {avg_time_per_test_case}"
        )

    print(f"Average Time Per Test Case: {avg_time_per_test_case}")

    print(f"---Average Time Taken for All Test Cases---")
    print(f"Lean: {statistics.mean(avg_time_per_test_case["lean"].values())}")
    print(f"Hydra: {statistics.mean(avg_time_per_test_case["hydra"].values())}")
    print(
        f"Hydra (No Width): {statistics.mean(avg_time_per_test_case["hydra-no-width"].values())}"
    )
