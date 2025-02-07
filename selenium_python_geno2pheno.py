import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import os
from itertools import islice

args = dict(zip(['script', 'input_file', 'output_dir'], sys.argv))

def create_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options)

def string_builder(keys, seq_dict):
    return ''.join(f'>{key}\n{seq_dict[key]}\n' for key in keys)

def log_file_string_creator(to_w):
    out_string = ""
    for line in to_w[1:]:
        parts = line.split()
        if len(parts) != 6 and parts[3] != 'B':
            out_string += "\n" + ",".join([parts[1], parts[2], parts[3], parts[6], parts[7]])
        else:
            out_string += "\n" + ",".join([parts[1], parts[2], parts[3], parts[4], parts[5]])
    return out_string

def get_geno2pheno_results(driver, txt_field):
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]').click()
    seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
    seq_field.send_keys(txt_field)
    driver.find_element(By.XPATH, '//*[@id="XactionCell"]/input').click()
    return driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/table[2]')

def new_input(driver):
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/table/tbody/tr/td[2]/input').click()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[1]/td/input').clear()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea').clear()

def parse_fasta(file_path):
    patID_seq = {}
    with open(file_path, 'r') as seq_file:
        lines = seq_file.readlines()
    seq_nextline_in = ""
    for i, line in enumerate(lines):
        if line.startswith('>'):
            id = line[1:].strip()
        else:
            seq_nextline_in += line.strip()
            if i + 1 == len(lines) or lines[i + 1].startswith('>'):
                patID_seq[id] = seq_nextline_in
                seq_nextline_in = ""
    return patID_seq

def process():
    patID_seq = parse_fasta(args['input_file'])

    output_dir = args.get('output_dir', '')
    if output_dir and not output_dir.endswith('/'):
        output_dir += '/'

    os.makedirs(output_dir, exist_ok=True)
    log_file_path = os.path.join(output_dir, 'Geno2PhenoTest_log.csv')

    with open(log_file_path, 'w') as log_file:
        log_file.write(
            ",".join(['ID', 'V3 Loop', 'Subtype', 'FPR', 'Percentage'])
        )

        driver = create_webdriver()
        driver.get('https://coreceptor.geno2pheno.org/')

        while patID_seq:
            batch_size = min(len(patID_seq), 50)
            cur_keys = list(islice(patID_seq, batch_size))
            txt_field = string_builder(cur_keys, patID_seq)
            table = get_geno2pheno_results(driver, txt_field)
            results_arr = table.text.split('\n')
            log_file.write(log_file_string_creator(results_arr))
            new_input(driver)
            for key in cur_keys:
                patID_seq.pop(key)

        driver.quit()

if __name__ == "__main__":
    process()
