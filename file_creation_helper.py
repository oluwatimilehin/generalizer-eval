import subprocess
import textwrap

if __name__ == "__main__":
    num_examples = 50

    for i in range(10, num_examples + 1):
        file_name = f"/Users/user/Projects/lean-mlir/SSA/Experimental/Bits/Fast/GeneralizerTests/{i}.lean"
        result = subprocess.run(
            [
                "touch",
                file_name,
            ],
            capture_output=True,
            text=True,
        )

        lean_code = textwrap.dedent(
            """\
            import SSA.Experimental.Bits.Fast.Generalize

            set_option trace.profiler true
            set_option trace.profiler.threshold 1
            set_option trace.Generalize true

            variable {x y : BitVec 8}
        """
        )

        with open(file_name, "w") as f:
            f.write(lean_code.strip() + "\n")
