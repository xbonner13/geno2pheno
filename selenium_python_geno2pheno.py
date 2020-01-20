import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
from datetime import date
import re
import os
from itertools import islice

args = dict(zip(['script', 'input_file', 'driver_dir', 'output_dir', 'sleep_interval'], sys.argv))

if 'driver_dir' not in args:
    args['driver_dir'] = os.getcwd() + "/chromedriver"

if 'sleep_interval' in args:
    args['sleep_interval'] = int(args['sleep_interval'])
else:
    args['sleep_interval'] = 5

#build the string that goes into the text area
def string_builder(my_keys, my_dict):
    string = ""
    #print(len(my_keys))
    for key in range(len(my_keys)):
        #raw_input(my_keys[key])
        string = string + '>' + my_keys[key] + '\n' + my_dict[my_keys[key]] + '\n'
    #print(string)
    return string

#write the results to the log file
# TODO: make a way to put the subtype B and other subtypes in the log file
def log_file_string_creator(to_w):
    out_string = ""
    #raw_input(len(to_w))
    #print("In the log File function")
    for i in range(len(to_w)):
        if i != 0:
            line = to_w[i].split(' ')

            if len(line) == 6:
                out_string = out_string + '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5] #generate the log file string
                #print(line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5])
            else:
                #print(len(line))
                #raw_input(line)
                if line[3] == 'B':
                    out_string = out_string + '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5]
                    #print(line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[4] + '\t\t\t\t' + line[5])
                else:
                    out_string = out_string + '\n' + line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[6] + '\t\t\t\t' + line[7]
                    #print(line[1] + '\t\t\t\t' + line[2] + '\t\t\t\t' + line[3] + '\t\t\t\t' + line[6] + '\t\t\t\t' + line[7])
    #print("Left the log file function!")
    #raw_input(out_string)
    return out_string

#extract the coreceptor table from the website
def get_geno2pheno_results():
    #select the significance level
    select_level = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]')
    select_level.click()
    seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
    seq_field.send_keys(txt_field)
    #print("This is the next line!")
    time.sleep(args['sleep_interval']) #Let the user actually see something!

    #click the align predicted button
    go = driver.find_element(By.XPATH,'//*[@id="XactionCell"]/input')
    go.click()

    time.sleep(args['sleep_interval'])
    t_results = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]')

    return t_results

#write the good CCR5 sequences to a fasta file
def write_fasta(results_arr, patID_seq):
    #print("In the write fasta file function!")
    for i in range(len(results_arr)):
        #raw_input(results_arr[i].split(' ')[1])
        #print(results_arr[i][4])
        #raw_input(results_arr[i].split())
        results_eles = results_arr[i].split()

        if i != 0:
            test_value = results_eles[4][0:len(results_eles[4]) - 1]

            try:
                test_value = float(test_value)
                if results_eles[3] == 'B':
                    if  test_value > 7.0:
                        #raw_input("If condition reached!" + results_eles[4] + "<- FPR")
                        #raw_input(patID_seq[results_arr[i][1]])
                        seq_to_write = re.sub("(.{64})", "\\1\n", patID_seq[results_arr[i].split(' ')[1]], 0, re.DOTALL)
                        fasta_out_file.write('>' + results_arr[i].split(' ')[1] + '\n' + seq_to_write + '\n')
            except Exception as e:
                #print("Subtype: " + results_eles[3])
                if results_eles[3] == 'B':
                    #raw_input("If statement of exception and subtype is B!")

                    test_value = float(results_eles[4][0:len(results_eles[4]) - 1])
                    #raw_input(results_eles)

                    #print(type(test_value))
                    #print("This is the test value: " + test_value)
                    if test_value > 7.0:

                        #if the prodiction is still subtype B add it to the fasta file else do not add it
                        #print("Inside the if condition from the fasta!  So the FPR should be less than 7.0")

                        seq_to_write = re.sub("(.{64})", "\\1\n", patID_seq[results_arr[i].split(' ')[1]], 0, re.DOTALL)
                        fasta_out_file.write('>' + results_arr[i].split(' ')[1] + '\n' + seq_to_write + '\n')

            #print(test_value)
            #raw_input(type(test_value))

    #print("leaving the fasta file function")
    return 0

def new_input():
    input_resub = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/table/tbody/tr/td[2]/input') #get input button
    input_resub.click()
    #raw_input()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[1]/td/input').clear()
    driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea').clear()
#dictionary to hold the data
patID_seq = {}
seq_nextline_in = ""
c_i = 0
#raw_input(today)
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
    #raw_input(lines[c_i] + str(c_i))
    if line[0] == '>':
        id = line[1:(len(line) -1)]
        #raw_input(next(seq_file))
    #builds protein sequence line by line in fasta
    if line[0] != '>':
        seq_nextline_in = seq_nextline_in + line.rstrip()
    #see if next line is the beginning of a new sequence
    try:
        if lines[c_i + 1][0] == '>':
            patID_seq[id] = seq_nextline_in
            #print(patID_seq)
            #print('Next seq reached!')
            seq_nextline_in = ""
    except IndexError:
        #print(id + '\n')
        patID_seq[id] = seq_nextline_in
        #print('Input File Read!')
    c_i = c_i + 1


#path to the webdriver
#string_builder(list(islice(patID_seq, 20)), patID_seq)
#raw_input

#progress bar generation
tw = 40
sys.stdout.write("[%s]" % (" " * tw))
sys.stdout.flush()
sys.stdout.write("\b" * (tw+1)) # return to start of line, after '['
new_prog = 0.0

orig_len = len(patID_seq)

#locate the driver
options = Options()
options.add_argument("--headless")
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(args['driver_dir'], chrome_options=options)
driver.get('https://coreceptor.geno2pheno.org/');

while len(patID_seq) != 0:

    #print('Length of patID_seq: ' + str(len(patID_seq)) + '\n')
    if len(patID_seq) < 50:
    #    print('last of the file!\n')
        if len(patID_seq) == 1:
            #raw_input(patID_seq.keys)
            id = patID_seq.keys()[0]
            #raw_input(id)
            seq = patID_seq[id]
            #raw_input(seq )
            select_level = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]') #selecting sig_level
            select_level.click()
            seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
            time.sleep(args['sleep_interval']) #Let the user actually see something!
            seq_field.send_keys('>' + id + '\n' + seq)
            go = driver.find_element(By.XPATH,'//*[@id="XactionCell"]/input')
            go.click()
            #raw_input("After go is clicked!")
            verify_id = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td') #get the ID back
            #raw_input("Id has been verified! " + verify_id.text)
            p_subtype = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[1]/td/table/tbody/tr[5]/td') #predicted subtype
            #raw_input("predicted subtype! " + p_subtype.text)
            predictor = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/b') #get prediction
            #raw_input("Predictor has been found! " + predictor.text)
            fPR = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[3]/center') # get FPR
            #raw_input("fpr! " + fPR.text)
            consensus = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[3]/td/table')
            #raw_input(consensus.text.split('\n')[0].split(' '))
            con_seq = consensus.text.split('\n')[0]
            con_seq = re.findall('(?<=:).*$', con_seq)
            #raw_input(con_seq[0].replace(' ', ''))
            log_file.write('\n' + verify_id.text + '\t\t\t\t' + con_seq[0].replace(' ', '') + '\t\t\t\t' + p_subtype.text + '\t\t\t\t' + fPR.text)

            #raw_input("After log file!")
            if predictor.text[4:9] != 'CXCR4':
            #         print(fPR.text)

                seq_to_write = re.sub("(.{64})", "\\1\n", seq, 0, re.DOTALL)
                #print(seq_to_write)
                fasta_out_file.write('>' + id + '\n' + seq_to_write + '\n')
                #print('>' + id + '\n' + seq_to_write + '\n')
            patID_seq.pop(id)
            #raw_input("Done with one seq test!")

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
    #    print('\n')
        cur_keys = list(islice(patID_seq, 50)) #grab 50 keys from dict
        txt_field = string_builder(cur_keys, patID_seq)

        table = get_geno2pheno_results()
        results_arr = str(table.text).split('\n')
        to_write_log = log_file_string_creator(results_arr)

        log_file.write(to_write_log)
        # log_file.write( + "\t\t\t" + predictor.text + "\t\t\t" +  + '\n')

        #if FPR is < 7 do not add it to the fasta`
        write_fasta(results_arr, patID_seq)

        [patID_seq.pop(key) for key in cur_keys]
        new_input()

    time.sleep(args['sleep_interval'])
    #display how much progress has been made
    prev_prog = new_prog
    new_prog = (40 - (len(patID_seq)/float(orig_len))*40)
    up_prog = new_prog - prev_prog
    #raw_input(up_prog)
    sys.stdout.write("="*int(round(up_prog)))
    sys.stdout.flush()


    #raw_input()

#finish updating progress bar
sys.stdout.write("]\n")
print("One Moment.  Preparing Your Files!")
time.sleep(args['sleep_interval'])
#raw_input('pause')

# dirpath = os.getcwd()
# #raw_input(dirpath)
# driver = webdriver.Chrome(dirpath + "/chromedriver")
# driver.get('https://coreceptor.geno2pheno.org/');


# for cur_key in patID_seq:
#     seq = patID_seq[cur_key]
#     id = cur_key
#     #raw_input(id + '->' + seq)
#     #time.sleep(5) # Let the user actually see something!
#     identifier = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[1]/td/input')
#     time.sleep(5)
#     identifier.send_keys(id)
#     time.sleep(5) # Let the user actually see something!
#     select_level = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[5]/td/select/option[8]') #select the significance level
#     select_level.click()
#     #raw_input("selecting significance level!")
#     seq_field = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea')
#     time.sleep(5) #Let the user actually see something!
#     seq_field.send_keys(seq)
#     #time.sleep(1)
#     go = driver.find_element(By.XPATH,'//*[@id="XactionCell"]/input')
#     go.click()
#     time.sleep(5)
#     #raw_input("The wait is over!")
#     verify_id = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[1]/td/table/tbody/tr[1]/td') #get the ID back
#     predictor = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/b') #get prediction
#     fPR = driver.find_element(By.XPATH,'//*[@id="g2pmain"]/div/table[2]/tbody/tr[4]/td/table/tbody/tr[2]/td[3]/center') # get FPR
#     log_file.write(verify_id.text + "\t\t\t" + predictor.text + "\t\t\t" + fPR.text + '\n')
#     #raw_input(predictor.text[4:9])
#     if predictor.text[4:9] != 'CXCR4':
#         print(fPR.text)
#         seq_to_write = re.sub("(.{64})", "\\1\n", seq, 0, re.DOTALL)
#         fasta_out_file.write('>' + id + '\n' + seq_to_write + '\n')
#     #time.sleep(3)
#     input_resub = driver.find_element(By.XPATH, '//*[@id="g2pmain"]/table/tbody/tr/td[2]/input') #get input button
#     input_resub.click()
#     #raw_input()
#     driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[1]/td/input').clear()
#     driver.find_element(By.XPATH, '//*[@id="g2pmain"]/div/center/table/tbody/tr[8]/td/textarea').clear()


log_file.close()
fasta_out_file.close()
driver.quit()
