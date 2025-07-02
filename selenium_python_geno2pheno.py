import sys
import os
import time
import traceback
import tempfile
from io import StringIO
from Bio.SeqIO import parse as SeqIO_parse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

UNIQUE_SEQ_ID = "XiaoBao"
DUMMY_SEQ = f""">{UNIQUE_SEQ_ID}
AAATTAACCCCGATCTGTGTTACTTTAAATTGCACTGATGATTGGAATACTACTAATGGGAATACTACCAATGGGAATGCTAATAATACCACTGGTAATAGTTTGGAAAGAGAAAAAGGAGAAATAAAGAAATGCTCTTTCAATATCACCACAAGCATAAAAGAAAAGAAAAAAGACTATGCATTCTTTTATAAGCTTGATATAGTACAAATAGATGATAGTGATAATAATAGTAATAGTTATAGGTTGATAAATTGTAACACCTAGTACAGTACAATGTACACATGGAATTAAGCCAGTAGTGTCCACTCAACTGCTGCTAAATGGCAGCCTAGCAGAAGAAGAGATAGTGATTAGATCTGACAATTTCTCGGACAATGCTAAAAACATAATAGTGCAGCTGAAGGAACCCATAGAAATTATTTGTATAAGACCCCATAACAATACAAGAAAAAGTATACATATGGGACCAGGAAAGCCTTTTTTGCAACAGGAGACGTAATAGGAGACATAAGACAA"""

def create_webdriver():
    options = webdriver.ChromeOptions()

    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--enable-logging')
    options.add_argument('--v=1')

    if "DOCKER_ENV" in os.environ:
        options.binary_location = "/usr/bin/chromium"
        return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    else:
        profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")
        options.add_argument(f"--user-data-dir={profile_dir}")
        return webdriver.Chrome(options=options)

def ease_off_retry(attempt):
    time.sleep(5 * attempt)

class Geno2Pheno:
    def __init__(self, input_path, job_id):
        self.input_path = input_path
        self.job_id = job_id or 'Geno2PhenoTest_log'
        self.output_path = ""
        self.results = []
        self.driver = create_webdriver()

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def wait_for(self, by, selector, timeout=600):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def read_fasta(self):
        seqs = []
        if os.path.isfile(self.input_path):
            self.output_path = os.path.dirname(self.input_path)
            if self.input_path.endswith((".fa", ".fasta")):
                seqs = list(SeqIO_parse(self.input_path, "fasta"))
        else:
            self.output_path = self.input_path
            for filename in os.listdir(self.input_path):
                if filename.endswith((".fa", ".fasta")):
                    file = os.path.join(self.input_path, filename)
                    seqs.extend(SeqIO_parse(file, "fasta"))
        return list(seqs)

    def fetch_results(self, txt_field):
        try:
            # Visit Geno2Pheno page
            self.driver.get('https://coreceptor.geno2pheno.org/')
            # Set significance level to 15%
            select = self.wait_for(By.CSS_SELECTOR, 'select[name="slev_cxcr4"]')
            Select(select).select_by_value('8')
            # Enter sequences
            self.wait_for(By.CSS_SELECTOR, 'textarea[name="v3seq"]').send_keys(txt_field)
            # Submit form
            self.wait_for(By.CSS_SELECTOR, 'input[name="go"][value="Go"]').click()
            # Extract result table
            table = self.wait_for(By.XPATH, "//center/following-sibling::table[1]")
            # Skip header row
            rows = table.find_elements(By.XPATH, ".//tr[position() > 1]")
            # Convert each row (skipping first column) into CSV line
            lines = []
            for row in rows:
                cells = row.find_elements(By.XPATH, ".//td[position() > 1]")
                lines.append(",".join(cell.text.strip() for cell in cells))
            # Remove dummy sequence result
            lines = [line for line in lines if UNIQUE_SEQ_ID not in line]
            return {"success": True, "data": lines}
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return {"success": False, "data": e}

    def process_group(self, group, attempt=1):
        txt_field = ''.join(f'>{seq.id}\n{seq.seq}\n' for seq in group)
        result = self.fetch_results(txt_field)
        if not result["success"] and attempt < 3:
            ease_off_retry(attempt)
            self.process_group(group, attempt + 1)
        elif not result["success"]:
            for seq in group:
                self.results.append(f"{seq.id}: Network Error")
        else:
            self.results += result["data"]

    def process(self):
        seqs = self.read_fasta()
        grouped = [seqs[i:i + 25] for i in range(0, len(seqs), 25)]
        time.sleep(10) # Initial wait for WebDriver readiness
        for group in grouped:
            if len(group) == 1:
                dummy = list(SeqIO_parse(StringIO(DUMMY_SEQ), "fasta"))[0]
                group.append(dummy)
            self.process_group(group)
        out_file = os.path.join(self.output_path, f"{self.job_id}.csv")
        with open(out_file, 'w') as f:
            f.write("HEADER,V3-LOOP,SUBTYPE,FPR,PERCENTILE,COMMENT\n")
            f.write('\n'.join(self.results))

if __name__ == "__main__":
    _, input_path, job_id = sys.argv
    Geno2Pheno(input_path, job_id).process()