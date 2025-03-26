import unittest
from selenium_python_geno2pheno import Geno2Pheno
import os

test_input_samples = "./input/unaligned_input.fasta"

class TestMyFunctions(unittest.TestCase):
    # e2e for ./selenium_python_geno2pheno.py
    def test_submission_results(self):
        job_id = "job_id"
        expected_output_file = f"./input/test/{job_id}.csv"
        actual_output_file = f"./input/{job_id}.csv"

        geno2pheno = Geno2Pheno(test_input_samples, job_id)
        geno2pheno.process()

        self.assertTrue(os.path.exists(test_input_samples))
        self.assertTrue(os.path.exists(expected_output_file))

        # assert that expected_output_file has the same content as ./test_output.csv
        with open(expected_output_file, 'r') as f:
            expected_output = f.read()
        with open(actual_output_file, 'r') as f:
            actual_output = f.read()
        self.assertEqual(expected_output.strip(), actual_output.strip())

if __name__ == '__main__':
    unittest.main()