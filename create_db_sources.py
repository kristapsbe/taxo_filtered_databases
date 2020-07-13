import os
import gzip
import glob
import json
import random

random.seed(42)

# extracted from 
# https://www.nature.com/articles/s41587-018-0008-8#MOESM4
#
# https://static-content.springer.com/esm/art%3A10caevow9Voomu.1038%2Fs41587-018-0008-8/MediaObjects/41587_2018_8_MOESM7_ESM.xlsx
valid_species = [
    'eggerthella_lenta',
    'clostridium_symbiosum',
    'bacteroides_eggerthii',
    'lactobacillus_plantarum',
    'ruminococcus_lactaris',
    'enterococcus_avium',
    'parabacteroides_distasonis',
    'clostridium_leptum',
    'prevotella_sp',
    'coprococcus_sp',
    'anaerostipes_sp',
    'bacillus_coagulans',
    'lactobacillus_gasseri',
    'enterobacter_sp',
    'bacteroides_clarus',
    'parabacteroides_merdae',
    'enterococcus_durans',
    'lactococcus_lactis',
    'propionibacterium_sp',
    'anaerofustis_stercorihominis',
    'roseburia_inulinivorans',
    'clostridium_innocuum',
    'eubacterium_biforme',
    'enterococcus_faecalis',
    'holdemania_filiformis',
    'enterococcus_saccharolyticus',
    'roseburia_hominis',
    'clostridium_nexile',
    'ruminococcus_gnavus',
    'bacteroides_faecis',
    'clostridium_sp',
    'ruminococcus_bromii',
    'collinsella_intestinalis',
    'dorea_sp',
    'bacteroides_plebeius',
    'bacteroides_oleiciplenus',
    'bacteroides_sp',
    'parabacteroides_gordonii',
    'bifidobacterium_pseudolongum',
    'burkholderiales_bacterium',
    'clostridium_bolteae',
    'coprococcus_catus',
    'clostridium_asparagiforme',
    'streptococcus_lutetiensis',
    'bifidobacterium_stercoris',
    'acidaminococcus_sp',
    'parabacteroides_sp',
    'erysipelatoclostridium_ramosum',
    'clostridium_butyricum',
    'bifidobacterium_adolescentis',
    'odoribacter_sp',
    'tannerella_sp',
    'clostridium_clostridioforme',
    'clostridiales_bacterium',
    'bacteroides_stercoris',
    'solobacterium_moorei',
    'enterococcus_casseliflavus',
    'bacteroides_salyersiae',
    'ruminococcus_sp',
    'klebsiella_pneumoniae',
    'erysipelotrichaceae_bacterium',
    'coprobacillus_sp',
    'bacteroides_uniformis',
    'clostridium_perfringens',
    'lactobacillus_casei',
    'catenibacterium_sp',
    'dorea_formicigenerans',
    'clostridium_spiroforme',
    'lactobacillus_ruminis',
    'bacteroides_caccae',
    'roseburia_sp',
    'mitsuokella_multacida',
    'bacteroides_intestinalis',
    'prevotella_stercorea',
    'blautia_sp',
    'bacillus_licheniformis',
    'odoribacter_splanchnicus',
    'bifidobacterium_animalis',
    'bacteroides_fragilis',
    'bacteroides_cellulosilyticus',
    'fusobacterium_ulcerans',
    'citrobacter_sp',
    'bacillus_sonorensis',
    'faecalibacterium_prausnitzii',
    'bifidobacterium_pseudocatenulatum',
    'bacteroides_coprocola',
    'bacteroides_ovatus',
    'streptococcus_sp',
    'eubacterium_dolichum',
    'eubacterium_ventriosum',
    'staphylococcus_warneri',
    'bacteroides_coprophilus',
    'bacteroides_stercorirosoris',
    'eubacterium_hallii',
    'ruminococcus_torques',
    'ruminococcus_obeum',
    'clostridium_hathewayi',
    'enterobacter_cloacae',
    'alistipes_indistinctus',
    'bifidobacterium_bifidum',
    'dorea_longicatena',
    'coprococcus_eutactus',
    'fusobacterium_mortiferum',
    'enterococcus_asini',
    'firmicutes_bacterium',
    'bacteroides_xylanisolvens',
    'bacteroides_vulgatus',
    'clostridium_sordellii',
    'lachnospiraceae_bacterium',
    'lactobacillus_salivarius',
    'bifidobacterium_longum',
    'veillonella_atypica',
    'streptococcus_gordonii',
    'escherichia_coli',
    'veillonella_sp',
    'prevotella_copri',
    'paraprevotella_clara',
    'dielma_fastidiosa',
    'butyrateproducing_bacterium',
    'faecalibacterium_sp',
    'collinsella_tanakaei',
    'eubacterium_eligens',
    'faecalibacterium_cf',
    'butyricimonas_virosa',
    'streptococcus_parasanguinis',
    'veillonella_parvula',
    'bacillus_cereus',
    'megamonas_funiformis',
    'roseburia_intestinalis',
    'megamonas_rupellensis',
    'weissella_cibaria',
    'alistipes_sp',
    'bacteroides_thetaiotaomicron',
    'coprococcus_comes',
    'eubacterium_rectale',
    'clostridium_citroniae',
    'weissella_confusa',
    'fusobacterium_varium',
    'streptococcus_anginosus',
    'lactobacillus_fermentum',
    'bacteroides_nordii',
    'streptococcus_salivarius',
    'eubacterium_sp',
    'lactococcus_garvieae',
    'streptococcus_mutans',
    'streptococcus_equinus',
    'streptococcus_pasteurianus',
    'prevotella_disiens',
    'streptococcus_vestibularis',
    'lactobacillus_amylovorus',
    'paenibacillus_polymyxa',
    'bacteroides_dorei',
    'subdoligranulum_sp'
]

with open('mapping.json', 'r') as file:
     mapping = json.load(file)

selected = {
    "full_refseq": { # FULL REFSEQ
        "taxid": {species:list(taxids.keys()) for species,taxids in mapping.items()}
    },
    "only_first": { # EACH SPECIES ONLY USES THE FIRST TAXID THAT REPRESENTS IT
        "taxid": {species:[list(taxids.keys())[0]] for species,taxids in mapping.items()}
    },
    "each_random_1": { # EACH SPECIES USES A RANDOM TAXID TO REPRESENT IT #1
        "taxid": {species:[list(taxids.keys())[random.randrange(len(taxids.keys()))]] for species,taxids in mapping.items()}
    },
    "each_random_2": { # EACH SPECIES USES A RANDOM TAXID TO REPRESENT IT #2
        "taxid": {species:[list(taxids.keys())[random.randrange(len(taxids.keys()))]] for species,taxids in mapping.items()}
    },
    "each_random_3": { # EACH SPECIES USES A RANDOM TAXID TO REPRESENT IT #3
        "taxid": {species:[list(taxids.keys())[random.randrange(len(taxids.keys()))]] for species,taxids in mapping.items()}
    },
    "random_30_1": { # USE A RANDOM SET OF 30% OF ALL TAXID #1
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.3] for species,taxids in mapping.items()}
    },
    "random_30_2": { # USE A RANDOM SET OF 30% OF ALL TAXID #2
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.3] for species,taxids in mapping.items()}
    },
    "random_30_3": { # USE A RANDOM SET OF 30% OF ALL TAXID #3
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.3] for species,taxids in mapping.items()}
    },
    "random_10_1": { # USE A RANDOM SET OF 10% OF ALL TAXID #1
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.1] for species,taxids in mapping.items()}
    },
    "random_10_2": { # USE A RANDOM SET OF 10% OF ALL TAXID #1
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.1] for species,taxids in mapping.items()}
    },
    "random_10_3": { # USE A RANDOM SET OF 10% OF ALL TAXID #1
        "taxid": {species:[x for x in list(taxids.keys()) if random.random() < 0.1] for species,taxids in mapping.items()}
    }
}

selected["full_refseq"]["accessionid"] = {species:sum(list(taxids.values()), []) for species,taxids in mapping.items()}
selected["only_first"]["accessionid"] = {species:taxids[list(taxids.keys())[0]] for species,taxids in mapping.items()} 
selected["each_random_1"]["accessionid"] = {species:taxids[list(taxids.keys())[list(taxids.keys()).index(selected["each_random_1"]["taxid"][species][0])]] for species,taxids in mapping.items()}
selected["each_random_2"]["accessionid"] = {species:taxids[list(taxids.keys())[list(taxids.keys()).index(selected["each_random_2"]["taxid"][species][0])]] for species,taxids in mapping.items()}
selected["each_random_3"]["accessionid"] = {species:taxids[list(taxids.keys())[list(taxids.keys()).index(selected["each_random_3"]["taxid"][species][0])]] for species,taxids in mapping.items()}
selected["random_30_1"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_30_1"]["taxid"][species]], []) for species,taxids in mapping.items()} 
selected["random_30_2"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_30_2"]["taxid"][species]], []) for species,taxids in mapping.items()} 
selected["random_30_3"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_30_3"]["taxid"][species]], []) for species,taxids in mapping.items()} 
selected["random_10_1"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_10_1"]["taxid"][species]], []) for species,taxids in mapping.items()} 
selected["random_10_2"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_10_2"]["taxid"][species]], []) for species,taxids in mapping.items()} 
selected["random_10_3"]["accessionid"] = {species:sum([x for z,x in taxids.items() if z in selected["random_10_3"]["taxid"][species]], []) for species,taxids in mapping.items()} 

write_next = {k:False for k in selected.keys()}

for k,_ in selected["full_refseq"]["taxid"].items(): # just looping through all of the species
    print(k)
    
    with open("prot/prot_"+k, "r") as f:
        r = f.readline()
        while r:
            for sk,sv in selected.items():
                if ">" in r:
                    if r.split("_")[1].strip() in sv["taxid"][k]:
                        write_next[sk] = True
                        with open("db_files/"+sk+"_prot.fa", "a") as wf:
                            wf.write(r)
                    else:
                        write_next[sk] = False
                elif write_next[sk]:
                    with open("db_files/"+sk+"_prot.fa", "a") as wf:
                        wf.write(r)

            r = f.readline()
                
    with open("nucl/nucl_"+k, "r") as f:
        r = f.readline()
        while r:
            for sk,sv in selected.items():
                if ">" in r:
                    if r.split(" ")[0].split(".")[0][1:] in sv["accessionid"][k]:
                        write_next[sk] = True
                        with open("db_files/"+sk+"_nucl.fa", "a") as wf:
                            wf.write(r)
                    else:
                        write_next[sk] = False
                elif write_next[sk]:
                    with open("db_files/"+sk+"_nucl.fa", "a") as wf:
                        wf.write(r)

            r = f.readline()