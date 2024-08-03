
import qianfan
import os
import re
from pyserini.search.lucene import LuceneSearcher
import timeout_decorator
import json

os.environ["QIANFAN_AK"] = "RCpD2o
os.environ["QIANFAN_SK"] = "hg9G8Q"
def generate_prompt(tvd,lang):

    with open('../prompt.txt','r') as f:
        ff = f.read()
    prompt = ff +"\n"+ "\"" + tvd + "\"." + "\nI always extract 6 aspects from the original text according to the order of their appearance, namely Vulnerability Type, Root Cause, Affected Product, Impact, Attacker Type and Attack Vector. However, each of these aspects may not be present, and their order is not fixed."
    prompt = prompt + "\n}\n" + "The following are the results (in English) extracted from the original text in Task: "
    return prompt





import threading
import time

def ask_LLM(prompt):
    class RequestThread(threading.Thread):
        def __init__(self, prompt, event):
            threading.Thread.__init__(self)
            self.prompt = prompt
            self.event = event
            self.response = None

        def run(self):
            try:
                self.response = qianfan.ChatCompletion().do(messages=[{"role":"user","content":self.prompt}])
            finally:
                self.event.set()  # Signal that the request is complete

    while True:
        event = threading.Event()
        request_thread = RequestThread(prompt, event)
        request_thread.start()
        event.wait(timeout=120)  # Wait for 2 minutes

        if request_thread.is_alive():
            print("Request timed out. Retrying...")
            request_thread.join()  # Ensure the thread is terminated before retrying
        else:
            return request_thread.response.body['result']


def regular(text): 
    lang = 'eng'
    if lang == 'chn':
        pattern = r'(\d+)\. (.*?)是(.*?)。'
    if lang == 'eng':
        pattern = r'(\d+)\. "(.*?)" is the (.*?)\.'
    if lang == 'jap':
        pattern = r'(\d+)\. (.*?)は(.*?です)。'
    matches = re.findall(pattern, text)
    

    result = {}
    for match in matches:
        result[match[2]] = match[1]
    r=[text, result]
    return r

def count_repeating_letters(x, y):
    count = 0  
    for letter in x.lower():  
        if letter in y.lower():  
            count += 1  
    return min(count/len(x), count/len(y)) 


def find_similay_keyaspect_type(ext_dir):
    stand_dir = {'attected product':[],'vulnerability type':[],'root cause':[],'impact':[],'attacker type':[],'attack vector':[]}
    for i in ext_dir:
        stand_keys = list(stand_dir.keys())
        max_index = [count_repeating_letters(j,i) for j in stand_keys].index(max([count_repeating_letters(j,i) for j in stand_keys]))
        stand_dir[stand_keys[max_index]] = ext_dir[i]
    return stand_dir

def judge_include(tvd, keyaspect):

    prompt = 'Sentence1: \"' + keyaspect + '\";\n' + 'Sentence2: \"' + tvd + '\";\n'
    prompt = prompt + 'Do you think all the information in sentence 1 is included in sentence 2?\n'
    prompt = prompt + 'You just need to answer: yes or no. No need to give any reason.'
    res = ask_LLM(prompt)
    # print(res)
    if 'no' in res.lower():
        return False
    else:
        return True

    

def count_repeated_words(sentence1, sentence2):

    def tokenize(s):
        return s.split()

    words1 = tokenize(sentence1)
    words2 = tokenize(sentence2)

    word_set1 = set(words1)


    repeated_count = 0
    for word in words2:
        if word in word_set1:
            repeated_count += 1
    return max(repeated_count/len(words1),repeated_count/len(words2))

def re_verfy(tvd, keyaspecttype, keyaspect):
    prompt = "TVD: \"" + tvd +'\";\n' + keyaspecttype+ ": \"" + keyaspect + '\";\n'
    prompt = prompt + 'Do you think the ' + keyaspecttype + ' of TVD is ' + keyaspect + '?\n'
    prompt = prompt + 'Please answer yes or no. No need to answer the reason.'
    res = ask_LLM(prompt)
    if 'no' in res.lower():
        return False
    else:
        return True
    
def CWE_Score_LLM(tvd, keyaspecttype, keyaspect, cwe_des):
    prompt = "TVD: \"" + tvd +'\";\n' + keyaspecttype+ " of TVD: \"" + keyaspect + '\";\n'
    prompt = prompt + 'CWE of TVD: \"' + cwe_des + '\";\n'
    prompt = prompt + 'Please rate the consistency level of \"' + keyaspect + '\" and \"' + cwe_des + '\" (1-5 points, you only need to output one number from 1-5).\n'
    prompt = prompt + '1: Completely unrelated. Any key information element in \"' + cwe_des + '\" is not related to \"' + keyaspect + '\".\n'
    prompt = prompt + '2: There are some related ones. A certain element in \"' + cwe_des + '\" may be related to \"' + keyaspect + '\" in some uncommon situations.\n'
    prompt = prompt + '3: Related. In some common cases, an element in \"' + cwe_des + '\"  may be related to '  + keyaspect + '\".\n'
    prompt = prompt + '4: Relatively relevant. There are many elements in \"' + cwe_des + '\" that are related to ' + keyaspect + '\".\n'
    prompt = prompt + '5: Completely consistent. \"' + keyaspect + '\" directly appears in ' + cwe_des + '\", and other elements can also indirectly confirm that \"' + keyaspect + '\" is correct.'
    prompt = prompt + 'Noting：you only need to output one number from 1-5. No explanation needed.'
    res = ask_LLM(prompt)
    print(res)
    if '1' in res: return 1 
    if '2' in res: return 2
    if '3' in res: return 3 
    if '4' in res: return 4 
    if '5' in res:
        return 5
    else:
        return 2.5


ssearcher = LuceneSearcher.from_prebuilt_index('wikipedia-dpr')

def information_retrieval(query, num_results=3):
    hits = ssearcher.search(query, num_results)
    paragraphs = []
    for i in range(len(hits)):
        doc = ssearcher.doc(hits[i].docid)
        json_doc = json.loads(doc.raw())
        paragraphs.append(json_doc['contents'])
    return paragraphs

def retrieve_wiki_records(query):
    num_results = 3
    paragraphs = information_retrieval(query, num_results)
    return '\n'.join(paragraphs)
    
    
def NET_Score_LLM(tvd, keyaspecttype, keyaspect, cwe_des):
    cwe_des1 = cwe_des
    cwe_des = 'Background of TVD'
    prompt = "TVD: \"" + tvd +'\";\n' + keyaspecttype+ " of TVD: \"" + keyaspect + '\";\n'
    prompt = prompt + 'Background of TVD: \"' + cwe_des1 + '\";\n'
    prompt = prompt + 'Please rate the consistency level of \"' + keyaspect + '\" and \"' + cwe_des + '\" (1-5 points, you only need to output one number from 1-5).\n'
    prompt = prompt + '1: Completely unrelated. Any key information element in \"' + cwe_des + '\" is not related to \"' + keyaspect + '\".\n'
    prompt = prompt + '2: There are some related ones. A certain element in \"' + cwe_des + '\" may be related to \"' + keyaspect + '\" in some uncommon situations.\n'
    prompt = prompt + '3: Related. In some common cases, an element in \"' + cwe_des + '\"  may be related to '  + keyaspect + '\".\n'
    prompt = prompt + '4: Relatively relevant. There are many elements in \"' + cwe_des + '\" that are related to ' + keyaspect + '\".\n'
    prompt = prompt + '5: Completely consistent. \"' + keyaspect + '\" directly appears in ' + cwe_des + '\", and other elements can also indirectly confirm that \"' + keyaspect + '\" is correct.'
    prompt = prompt + 'Noting：you only need to output one number from 1-5. No explanation needed.'
    res = ask_LLM(prompt)
    # print(res)
    if '1' in res: return 1 
    if '2' in res: return 2
    if '3' in res: return 3 
    if '4' in res: return 4 
    if '5' in res:
        return 5
    else:
        return 2.5    

    
    
    
def merge(sentence_list):
    prompt = 'From the perspective of information entropy, please help me merge the following sentences. The requirement is to merge them into the smallest number of sentences, and the merged sentence should contain all the information of the previous sentence without adding any new information. Note: It is not necessary to merge them into one sentence. If there is no information overlap between the two sentences, there is no need to merge them\n'
    
    for i in range(len(sentence_list)):
        prompt = prompt + str(i) + '. ' + sentence_list[i] + '\n'
    res = ask_LLM(prompt)
    return res
    
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    





