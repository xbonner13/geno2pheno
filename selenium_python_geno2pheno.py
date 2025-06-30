from io import StringIO
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from Bio.SeqIO import parse as SeqIO_parse
from selenium.webdriver.support.ui import Select

def ease_off_retry(i):
    time.sleep(5 * i)

unique_seq_id = "XiaoBao"
unique_sample_string = f">{unique_seq_id}\nAAATTAACCCCGATCTGTGTTACTTTAAATTGCACTGATGATTGGAATACTACTAATGGGAATACTACCAATGGGAATGCTAATAATACCACTGGTAATAGTTTGGAAAGAGAAAAAGGAGAAATAAAGAAATGCTCTTTCAATATCACCACAAGCATAAAAGAAAAGAAAAAAGACTATGCATTCTTTTATAAGCTTGATATAGTACAAATAGATGATAGTGATAATAATAGTAATAGTTATAGGTTGATAAATTGTAACACCTAGTACAGTACAATGTACACATGGAATTAAGCCAGTAGTGTCCACTCAACTGCTGCTAAATGGCAGCCTAGCAGAAGAAGAGATAGTGATTAGATCTGACAATTTCTCGGACAATGCTAAAAACATAATAGTGCAGCTGAAGGAACCCATAGAAATTATTTGTATAAGACCCCATAACAATACAAGAAAAAGTATACATATGGGACCAGGAAAGCCTTTTTTGCAACAGGAGACGTAATAGGAGACATAAGACAA"

class Geno2Pheno:
    input_path = ""
    output_path = ""
    job_id = ""
    results = []

    def __init__(self, input_path, job_id):
        self.input_path = input_path
        self.job_id = job_id or 'Geno2PhenoTest_log'

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
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_geno2pheno_results(self, txt_field):
        # docs on By.CSS_SELECTOR https://saucelabs.com/resources/blog/selenium-tips-css-selectors
        driver = self.create_webdriver()
        data = {}
        try:
            # navigate to the geno2pheno page
            driver.get('https://coreceptor.geno2pheno.org/')
            time.sleep(10)
            # select Significance level 15%
            select_element = driver.find_element(By.CSS_SELECTOR, 'select[name="slev_cxcr4"]')
            select_obj = Select(select_element)
            select_obj.select_by_value('8')
            # fill sequence input textarea
            seq_field = driver.find_element(By.CSS_SELECTOR, 'textarea[name="v3seq"]')
            seq_field.send_keys(txt_field)
            # click on the submit button
            driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Go"]').click()
            time.sleep(10)
            # Click on the CSV button
            driver.find_element(By.CSS_SELECTOR, 'input[name="viewResSec"]').click()
            time.sleep(10)
            # Get the entire page text and remove the header line
            page_text = driver.find_element(By.CSS_SELECTOR, "body").text
            print(f"Page text: {page_text}")
            result = page_text.split('\n')
            result = result[1:]
            if len(result) == 2: # Remove items containing unique_seq_id
                result = [item for item in result if unique_seq_id not in item]
            data = {"success": True, "data": result}
        except Exception as e:
            print(f"Error: {e}")
            data = {"success": False, "data": e}
        finally:
            driver.quit()
        return data

    def process(self):
        seqs: list = self.read_fasta()
        num_seqs = len(seqs)

        # group into sets of 50 to respect geno2pheno's limit
        grouped_seqs = [seqs[i:i + 50] for i in range(0, num_seqs, 50)]

        for group in grouped_seqs:
            if len(group) == 1: # handle G2P case for single sequence
                seq_file = StringIO(unique_sample_string)
                seq = SeqIO_parse(seq_file, "fasta")
                group.append(seq)
            self.process_group(group, 1)

        log_file_path = os.path.join(self.output_path, f"{self.job_id}.csv")

        with open(log_file_path, 'w') as log_file:
            log_file.write("ID,V3 Loop,Subtype,FPR,Percentage\n")
            log_file.write('\n'.join(self.results))

    def process_group(self, group, attempt):
        txt_field = ''.join(f'>{seq.id}\n{seq.seq}\n' for seq in group)
        result = self.get_geno2pheno_results(txt_field)

        if not result["success"]:
            if attempt < 3:
                ease_off_retry(attempt)
                self.process_group(group, attempt + 1)
            else:
                for seq in group:
                    self.results.append(f"{seq.id}: Network Error")
        else:
            self.results += result["data"]

if __name__ == "__main__":
    args = dict(zip(['script', 'input_path', 'job_id'], sys.argv))
    input_path = args['input_path']
    job_id = args['job_id']
    geno2pheno = Geno2Pheno(input_path, job_id)
    geno2pheno.process()
