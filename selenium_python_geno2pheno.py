import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from Bio.SeqIO import parse as SeqIO_parse

def ease_off_retry(i):
    time.sleep(5 * i)

class Geno2Pheno:
    seqs_valid = []
    seqs_invalid = []
    output_path = ""

    def __init__(self, input_path, job_id):
        self.input_path = input_path
        self.job_id = job_id or 'Geno2PhenoTest_log'
        self.create_webdriver()

    def read_fasta(self):
        seqs = []
        if os.path.isfile(self.input_path):
            self.output_path = os.path.dirname(self.input_path)
            if ".fa" in self.input_path:
                seqs.extend(
                    SeqIO_parse(self.input_path, "fasta")
                )
        else:
            self.output_path = self.input_path
            for filename in os.listdir(self.input_path):
                if ".fa" in filename:
                    file = os.path.join(self.input_path, filename)
                    seqs.extend(
                        SeqIO_parse(file, "fasta")
                    )
        return list(seqs)

    def create_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse_results(self, to_w):
        for line in to_w[1:]:
            parts = line.split(' ')
            if len(parts) == 6 or parts[3] == 'B':
                data = [parts[1], parts[2], parts[3], parts[4], parts[5]]
            else:
                data = [parts[1], parts[2], parts[3], parts[6], parts[7]]
            if self.validate_result(data):
                self.seqs_valid.append(data)
            else:
                self.seqs_invalid.append([data[0], line])

    def validate_result(self, row):
        return '%' in row[3] and '%' in row[4]

    def get_geno2pheno_results(self, txt_field):
        try:
            self.driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]').click()
            seq_field = self.driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
            seq_field.send_keys(txt_field)
            self.driver.find_element(By.XPATH, '//*[@id="XactionCell"]/input').click()
            result = self.driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/table[2]')
            result = result.text.split('\n')
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "data": e}

    def navigate_to_geno2pheno(self, attempt):
        try:
            self.driver.get('https://coreceptor.geno2pheno.org/')
            return True
        except Exception as e:
            if attempt < 10:
                ease_off_retry(attempt)
                self.navigate_to_geno2pheno(attempt + 1)
            else:
                return False

    def process(self):
        seqs: list = self.read_fasta()
        num_seqs = len(seqs)

        # group into sets of 50 to respect geno2pheno's limit
        grouped_seqs = [seqs[i:i + 50] for i in range(0, num_seqs, 50)]

        for group in grouped_seqs:
            self.process_group(group, 1)

        print("seqs_valid", self.seqs_valid)
        print("seqs_invalid", self.seqs_invalid)

        log_file_path = os.path.join(self.output_path, f"{self.job_id}.csv")

        with open(log_file_path, 'w') as log_file:
            if len(self.seqs_valid) > 0:
                log_file.write("ID,V3 Loop,Subtype,FPR,Percentage")
            for seq in self.seqs_invalid:
                log_file.write(",".join(seq))
            for seq in self.seqs_valid:
                log_file.write(",".join(seq))

        self.driver.quit()

    def process_group(self, group, attempt):
        navigated = self.navigate_to_geno2pheno(1)

        if not navigated:
            self.seqs_invalid.append(["Error: Failed to navigate to geno2pheno."])
            for seq in group:
                self.seqs_invalid.append([seq.id, "NETWORK ERROR: Please resubmit."])
            return False

        txt_field = ''.join(f'>{seq.id}\n{seq.seq}\n' for seq in group)
        result = self.get_geno2pheno_results(txt_field)

        if not result["success"]:
            if attempt < 3:
                ease_off_retry(attempt)
                self.process_group(group, attempt + 1)
            else:
                self.seqs_invalid.append(["Error: " + {result["data"]}])
                for seq in group:
                    self.seqs_invalid.append([seq.id, "NETWORK ERROR: Please resubmit."])
        else:
            self.parse_results(result["data"])

if __name__ == "__main__":
    args = dict(zip(['script', 'input_path', 'job_id'], sys.argv))
    input_path = args['input_path']
    job_id = args['job_id']
    geno2pheno = Geno2Pheno(input_path, job_id)
    geno2pheno.process()
