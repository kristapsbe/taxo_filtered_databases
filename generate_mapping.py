import re
import gzip
import glob
import json

regex = re.compile('[^a-zA-Z]')
only_not_nums = re.compile('[^0-9]')
only_nums = re.compile('[0-9]')

mapping = {}

for fname in glob.glob("refseq_prot/refseq/release/*/*.gbff.gz"):
    print(fname)
    
    with gzip.open(fname) as f:
        data = f.read().decode('utf-8').split("\n")
        
        curr_org = "" 
        curr_header = "" 
        accession_data = []
        
        for l in data:
            if "DEFINITION" in l:
                curr_org = "_".join([regex.sub('', x) for x in l.split(" ")[2:4]])
                
                if curr_org not in mapping:
                    mapping[curr_org] = {}
            elif "ACCESSION" in l:
                tmp = l.split(" ")[3:]
                accession_data = []
                
                for x in tmp:
                    if '-' in x:
                        num_len = len(only_not_nums.sub('', x.split("-")[0]))
                        affix = only_nums.sub('', x.split("-")[0])
                        
                        for n in range(int(only_not_nums.sub('', x.split("-")[0])), int(only_not_nums.sub('', x.split("-")[1]))+1):
                            accession_data.append(affix+str(n).zfill(num_len))
                    else:
                        accession_data.append(x)
            elif "/db_xref=\"taxon:" in l:
                # we've found the taxid for the next bunch of sequences - save it
                mapping[curr_org][l.split(":")[1].split("\"")[0]] = accession_data

with open('mapping.json', 'w') as file:
     file.write(json.dumps(mapping))