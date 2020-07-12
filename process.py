import re
import gzip
import glob

# it turns out the names of species can be shortened occasionally (this breaks file names) - get rid of non letters
regex = re.compile('[^a-zA-Z]')

for fname in glob.glob("refseq_base/*.fna.gz"):
    print(fname)

    with gzip.open(fname) as f:
        
        data = f.read().decode('utf-8').split("\n")

        curr_org = "" # this will contain the organisms name in binomial nomenclature with a _ between the two words
        concatted = "" # this will contain the current sequence concattenated into one line (needed for some of the dl tools)
        curr_header = "" # this will contain the header for the current sequence

        for l in data:
            if ">" in l:
                # we've got a line with a header in it - write down the data that we've gathered up 
                # and fetch the new organism and header info
                if concatted != "":
                    with open("nucl/nucl_"+curr_org, "a") as wf:
                        wf.write(curr_header+"\n")
                        wf.write(concatted+"\n")
                    concatted = ""

                curr_org = "_".join([regex.sub('', x) for x in l.split(" ")[1:3]])
                curr_header = l.strip()
            else:
                # this is a sequence line - just keep concatting till we hit a header
                concatted += l.strip()
                
# this generates files that kaiju databases will be made out of - the header format they expect is <counter_prefix>_<ncbi_taxid>
org_counters = {} # this will keep track of the counter prefixes

for fname in glob.glob("refseq_prot/refseq/release/*/*.gbff.gz"):
    print(fname)
    
    with gzip.open(fname) as f:
        data = f.read().decode('utf-8').split("\n")
        
        curr_org = "" # same as before - binomial nomenclature name with a _ between the words
        concatted = "" # same as before - ref sequence concatted into a single line
        curr_header = "" # this will hold only part of the header (the ncbi tax id)
        do_concat = False 
        
        for l in data:
            if "DEFINITION" in l:
                # we've hit a block for a new organism - clear out what we have and fetch the new organisms name
                if concatted != "":
                    with open("prot/prot_"+curr_org, "a") as wf:
                        wf.write(">"+str(org_counters[curr_header])+"_"+curr_header+"\n")
                        wf.write(concatted+"\n")
                    concatted = ""
                    org_counters[curr_header] += 1
                curr_org = "_".join([regex.sub('', x) for x in l.split(" ")[2:4]])
            elif "/db_xref=\"taxon:" in l:
                # we've found the taxid for the next bunch of sequences - save it
                curr_header = l.split(":")[1].split("\"")[0]
                
                if curr_header not in org_counters:
                    org_counters[curr_header] = 1
            elif "/translation=\"" in l:
                # we've found the beggining of a sequence - start concatting
                do_concat = True
                concatted += l.split("\"")[1].strip()
            elif "                     " not in l:
                # we've found the end of the sequence - dump everything we've got and increment the counter prefix
                # (the format is a bit funky - easiest way I've found is to check for whitespaces at 
                # the beginnig - if there's a flag for a new block the chunk of uninterrupted whitespaces will
                # be a lot shorter)
                if concatted != "":
                    with open("prot/prot_"+curr_org, "a") as wf:
                        wf.write(">"+str(org_counters[curr_header])+"_"+curr_header+"\n")
                        wf.write(concatted+"\n")
                    concatted = ""
                    org_counters[curr_header] += 1
                do_concat = False
            elif do_concat:
                # we're somewhere inbetween the beginning and the end of the current sequence - keep gathering up the refernce data
                concatted += l.replace("\"", "").strip()
        