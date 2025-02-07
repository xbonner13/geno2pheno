import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
from datetime import date
import re
import os
from itertools import islice

args = dict(zip(['script', 'input_file', 'output_dir', 'sleep_interval'], sys.argv))

if 'sleep_interval' in args:
    args['sleep_interval'] = int(args['sleep_interval'])
else:
    args['sleep_interval'] = 5

def create_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    return driver

#build the string that goes into the text area
def string_builder(my_keys, my_dict):
    string = ""
    for key in range(len(my_keys)):
        string = string + '>' + my_keys[key] + '\n' + my_dict[my_keys[key]] + '\n'
    return string

#write the results to the log file
# TODO: make a way to put the subtype B and other subtypes in the log file
def log_file_string_creator(to_w):
    out_string = ""
    j = len(to_w)
    for i in range(1, j):
        line = to_w[i].split(' ')
        if len(line) == 6:
            out_string += '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5] #generate the log file string
        else:
            if line[3] == 'B':
                out_string += '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5]
            else:
                out_string += '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[6] + '\t\t\t\t' + line[7]
    return out_string

#extract the coreceptor table from the website
def get_geno2pheno_results():
    #select the significance level
    select_level = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]')
    select_level.click()
    seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
    seq_field.send_keys(txt_field)
    time.sleep(args['sleep_interval'])
    #click the align predicted button
    go = driver.find_element(By.XPATH,'//*[@id="XactionCell"]/input')
    go.click()
    time.sleep(args['sleep_interval'])
    t_results = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]')
    return t_results

#write the good CCR5 sequences to a fasta file
def write_fasta(results_arr, patID_seq):
    j = len(results_arr)
    for i in range(1, j):
        results_eles = results_arr[i].split()
        test_value = results_eles[4][0:len(results_eles[4]) - 1]
        try:
            test_value = float(test_value)
            if results_eles[3] == 'B':
                if  test_value > 7.0:
                    seq_to_write = re.sub("(.{64})", "\\1\n", patID_seq[results_arr[i].split(' ')[1]], 0, re.DOTALL)
                    fasta_out_file.write('>' + results_arr[i].split(' ')[1] + '\n' + seq_to_write + '\n')
        except Exception as e:
            if results_eles[3] == 'B':
                test_value = float(results_eles[4][0:len(results_eles[4]) - 1])
                if test_value > 7.0: #if the prodiction is still subtype B add it to the fasta file else do not add it
                    seq_to_write = re.sub("(.{64})", "\\1\n", patID_seq[results_arr[i].split(' ')[1]], 0, re.DOTALL)
                    fasta_out_file.write('>' + results_arr[i].split(' ')[1] + '\n' + seq_to_write + '\n')
    return 0

def new_input():
    input_resub = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/table/tbody/tr/td[2]/input') #get input button
    input_resub.click()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[1]/td/input').clear()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea').clear()

#dictionary to hold the data
patID_seq = {}
seq_nextline_in = ""
c_i = 0

#output log for writting results
#file for the sequences that should be included
if 'output_dir' in args:
    os.system('mkdir -p ' + args['output_dir'])
    log_file = open(args['output_dir'] + 'Geno2PhenoTest_log', 'w')
    fasta_out_file = open(args['output_dir'] + 'Geno2PhenoTest.fasta', 'w')
else:
    today = str(date.today())
    log_file = open('Geno2PhenoTest' + today + '_log', 'w')
    fasta_out_file = open('Geno2PhenoTest' + today + '.fasta', 'w')

log_file.write('ID\t\t\t\tV3 Loop\t\t\t\tSubtype\t\t\t\tFPR\t\t\t\tpercentage')

with open(sys.argv[1], 'r') as seq_file:
    lines = seq_file.readlines()
for line in lines:
    if line[0] == '>':
        id = line[1:(len(line) -1)]
    #builds protein sequence line by line in fasta
    if line[0] != '>':
        seq_nextline_in += line.rstrip()
    #see if next line is the beginning of a new sequence
    try:
        if lines[c_i + 1][0] == '>':
            patID_seq[id] = seq_nextline_in
            seq_nextline_in = ""
    except IndexError:
        patID_seq[id] = seq_nextline_in
    c_i += 1

if args['sleep_interval'] > 0:
    tw = 40
    sys.stdout.write("[%s]" % (" " * tw))
    sys.stdout.flush()
    sys.stdout.write("\b" * (tw+1))
    new_prog = 0.0

orig_len = len(patID_seq)

#locate the driver
driver = create_webdriver()
driver.get('https://coreceptor.geno2pheno.org/');

while len(patID_seq) != 0:
    if len(patID_seq) < 50:
        if len(patID_seq) == 1:
            id = patID_seq.keys()[0]
            seq = patID_seq[id]
            select_level = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]') #selecting sig_level
            select_level.click()
            seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
            time.sleep(args['sleep_interval'])
            seq_field.send_keys('>' + id + '\n' + seq)
            go = driver.find_element(By.XPATH,'//*[@id="XactionCell"]/input')
            go.click()
            verify_id = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td') #get the ID back
            p_subtype = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[1]/td/table/tbody/tr[5]/td') #predicted subtype
            predictor = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/b') #get prediction
            fPR = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[3]/center') # get FPR
            consensus = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[3]/td/table')
            con_seq = consensus.text.split('\n')[0]
            con_seq = re.findall('(?<=:).*$', con_seq)
            log_file.write('\n' + verify_id.text + '\t\t\t\t' + con_seq[0].replace(' ', '') + '\t\t\t\t' + p_subtype.text + '\t\t\t\t' + fPR.text)
            if predictor.text[4:9] != 'CXCR4':
                seq_to_write = re.sub("(.{64})", "\\1\n", seq, 0, re.DOTALL)
                fasta_out_file.write('>' + id + '\n' + seq_to_write + '\n')
            patID_seq.pop(id)
        else:
            cur_keys = list(islice(patID_seq, len(patID_seq))) #grab the last set of keys from the dict
            txt_field = string_builder(cur_keys, patID_seq)
            table = get_geno2pheno_results()
            results_arr = str(table.text).split('\n')
            to_write_log = log_file_string_creator(results_arr)
            log_file.write(to_write_log)
            write_fasta(results_arr, patID_seq)
            new_input()
            [patID_seq.pop(key) for key in cur_keys]
    else:
        cur_keys = list(islice(patID_seq, 50)) #grab 50 keys from dict
        txt_field = string_builder(cur_keys, patID_seq)
        table = get_geno2pheno_results()
        results_arr = str(table.text).split('\n')
        to_write_log = log_file_string_creator(results_arr)
        log_file.write(to_write_log)
        #if FPR is < 7 do not add it to the fasta`
        write_fasta(results_arr, patID_seq)
        [patID_seq.pop(key) for key in cur_keys]
        new_input()
    if args['sleep_interval'] > 0: #display how much progress has been made
        time.sleep(args['sleep_interval'])
        prev_prog = new_prog
        new_prog = (40 - (len(patID_seq)/float(orig_len))*40)
        up_prog = new_prog - prev_prog
        sys.stdout.write("="*int(round(up_prog)))
        sys.stdout.flush()

if args['sleep_interval'] > 0: #finish updating progress bar
    sys.stdout.write("]\n")
    print("One Moment.  Preparing Your Files!")
    time.sleep(args['sleep_interval'])

log_file.close()
fasta_out_file.close()
driver.quit()
