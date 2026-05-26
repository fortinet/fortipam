import sys
import yaml

Buffer_Size = 8*1024*1024
O_FILE = 'new_dst.conf'

def valid_conf_header(conf_file):
    '''
    Check conf_file header
    Return: (build_number, encryption_flag)
    '''
    line_list = []
    head_flag, enc_flag  = False, False
    with open(conf_file,"r") as fid:
        while True:
            line = fid.readline()
            if line.strip() == "config system global": 
                head_flag = True
                break
            if len(line) == 0: break
            line_list.append(line)
            if "#private-encryption-key=" in line: enc_flag = True

    if head_flag == False:
        print(f"\nError:  config header is not located as \" config system global\" NOT found!")
        sys.exit(1)
    
    if line_list[0][:19] not in ["#config-version=FPA","#config-version=SRA"]:
        print("\nError: Failed to check configuration header line-1, not FPA or SRA configuration")
        print(f"    {line_list[0]}")
        sys.exit(1)
    
    return (line_list[2], enc_flag)

def get_table_sum(f_id,table_name,start_idx,start_line, end_line):
    '''
    Purpose: Decode a whole content in a table to "Common" and "Entries"
    Input:  f_id: bin mode f_id; table_name is string
    Return: {'table_name':table_name,
             'sum': 
                    {'common':[line1, line2,...], 
                      Entry_1_Name:[start_idx,end_idx],
                      Entry_2_Name:[start_idx,end_idx]... 
                      ...}
            }
    '''
    if 'b' not in f_id.mode:
        print(f"Error: get_table_sum() Please using bin mode to open file {f_id.name}")
        sys.exit(1)
    table_sum = {"table_name":table_name,"sum":{"common":[]}}
    stack_seq = []
    
    f_id.seek(start_idx)
    b_line = f_id.readline()
    offline = 1
    offset  = len(b_line)
    if b"config " != b_line.strip()[:7]:
        print(f"\nError: failed to decode table. {f_id.name}:{table_name}:{start_line+offline+1}.  'config ' line not found. ")
        print(f"    {b_line}")
        sys.exit(1)
    for _ in range(1,end_line-start_line):
        b_line = f_id.readline()
        s_line = b_line.decode("utf-8")
        offline += 1
        offset += len(b_line)
        if b"edit " == b_line.strip()[:5]:
            stack_seq.append(s_line)
            if len(stack_seq) == 1:
                entry_name = s_line.strip()
                table_sum["sum"][entry_name] = [start_idx + offset - len(b_line),0]
            else:
                pre_prefix = len(stack_seq[-2]) - len(stack_seq[-2].lstrip())
                cur_prefix = len(s_line) - len(s_line.lstrip())
                if cur_prefix <= pre_prefix:
                    print(f"\nError: 'next' maybe missed\n    Same indentation of 2 'edit ...' in {f_id.name}:'{table_name}':{start_line+offline+1} ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                
        elif b"next" == b_line.strip()[:4]:
            if len(stack_seq) == 0:
                print(f"\nError: !!!\n    No 'edit' matching with 'next'. {f_id.name}:{table_name}.")
                print(f"    {stack_seq}")
                sys.exit(1)
            stack_seq.pop()
            if len(stack_seq) == 0:
                table_sum["sum"][entry_name][1] = start_idx+offset
        else:
            if len(stack_seq) == 0:
                table_sum["sum"]["common"].append(s_line)
        
    b_line = f_id.readline()
    if b"end" != b_line.strip():
        print(f"\nError: failed to decode table. {f_id.name}:'{table_name}':{start_line+offline+1} . 'end' line not found")
        print(f"    {b_line}")
        sys.exit(1)
        
    return table_sum
                

def get_file_sum(conf_file):
    '''
    Input:  a standard PAM configuration file
    Return: {"file_name":confi_file,
             "sum": 
                   {table_1: {'line':[start_line,end_line],'idx':[start_idx,end_idx]}, 
                    table_2: {'line':[start_line,end_line],'idx':[start_idx,end_idx]},
                   ...}
            }
    '''
    file_sum = {"file_name":conf_file,"sum":{}}
    stack_seq = []
    with open(conf_file,'rb') as fid:
        cur_line, cur_idx = 0 ,0
        while True:
            b_line = fid.readline()
            s_line = b_line.decode("utf-8")
            if not b_line: break
            
            cur_line  += 1
            cur_idx += len(b_line)
            if b"config " == b_line.strip()[:7]:
                if len(stack_seq) > 0:
                    if stack_seq[-1] == "\"": continue
                stack_seq.append(s_line) 
                if len(stack_seq) == 1: 
                    table_name =s_line.strip()  
                    file_sum["sum"][table_name] = {'line': [cur_line,0], 'idx':[cur_idx-len(b_line),0]}
                else:
                    pre_cmd = stack_seq[-2]
                    pre_prefix = len(pre_cmd) - len(pre_cmd.lstrip())
                    cur_prefix = len(s_line) - len(s_line.strip())
                    if cur_prefix <= pre_prefix:
                        print(f"\nError: 'end' maybe missed\n    Indentation of lastest 'config ...' should be greater than previos comand {conf_file}:{cur_line}. ")
                        print(f"    {stack_seq}")
                        sys.exit(1) 
            elif b"end" == b_line.strip():
                if len(stack_seq) > 0:
                    if stack_seq[-1] == "\"": continue
                if len(stack_seq) == 0:
                    print(f"\nError: missing 'config'\n    No  'config' matching with current line of 'end' in {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                pre_cmd = stack_seq[-1]
                if pre_cmd.strip()[:6] != 'config':
                    print(f"\nError: missing 'config'\n    No  'config' matching with current line of 'end' in {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                if pre_cmd.find("config") != s_line.find("end"):
                    print(f"Error: indentation'\n    Indentation of 'config' and 'end' not matching. {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                stack_seq.pop()
                if len(stack_seq) == 0:
                    file_sum["sum"][table_name]["line"][1]  = cur_line    
                    file_sum["sum"][table_name]["idx"][1]   = cur_idx
            elif b"edit " == b_line.strip()[:5]:
                if len(stack_seq) > 0:
                    if stack_seq[-1] == "\"": continue
                stack_seq.append(s_line)
                if len(stack_seq) >= 2: 
                    pre_cmd = stack_seq[-2]
                    pre_prefix = len(pre_cmd) - len(pre_cmd.lstrip())
                    cur_prefix = len(s_line) - len(s_line.strip())
                    if cur_prefix <= pre_prefix:
                        print(f"\nError: indentation\n     Indentation of lastest 'edit ...' should greater than previos. {conf_file}:{cur_line}. ")
                        print(f"    {stack_seq}")
                        sys.exit(1)
                    if (s_line.strip()[5] == "\"") and (s_line.strip()[-1] != "\""):
                        print(f"\nError: edit line error. \" not pair !")
                        print(f"    {conf_file}:{cur_line}. ")
                        sys.exit(1)
            elif b"next"  == b_line.strip():
                if len(stack_seq) > 0:
                    if stack_seq[-1] == "\"": continue
                if len(stack_seq) == 0:
                    print(f"\nError: not in config scope, no 'edit' matching \n    No  'edit' matching with current line of 'next' in {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                pre_cmd = stack_seq[-1]
                if pre_cmd.strip()[:4] != 'edit':
                    print(f"\nError: not correct 'edit' matching \n    No  'edit' matching with current line of 'next' in {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                if pre_cmd.find("edit") != s_line.find("next"):
                    print(f"Error: indentation'\n    Indentation of 'edit' and 'next' not matching. {conf_file}:{cur_line}. ")
                    print(f"    {stack_seq}")
                    sys.exit(1)
                stack_seq.pop()
            else:
                n_s_line = s_line.replace("\\\\\\\"","")   #:  \\\" is application layer charactors
                n_s_line = n_s_line.replace("\\\"","")     #:  \" is application layer charactors
                if n_s_line.count("\"")%2 != 0:
                    if len(stack_seq) == 0:
                        print(f"\nError: \" is not pair")
                    elif stack_seq[-1] == "\"":
                        stack_seq.pop()
                    else:
                        stack_seq.append("\"")

        if len(stack_seq) != 0:
            print(f"\nError: missing 'end'\n    No 'end' matching with 'config' in {conf_file}:{cur_line}. !")
            print(f"    {stack_seq}")
            sys.exit(1)

    return file_sum

def write_buffer(s_fid,start_idx,end_idx,d_fid):
    s_fid.seek(start_idx)
    remaining = end_idx - start_idx
    while remaining > 0:
        chunk_size = min(Buffer_Size, remaining)
        content = s_fid.read(chunk_size).decode('utf-8')
        #print(f"--------------------\n{content}\n--------------------")
        if not content: break
        d_fid.write(content)
        start_idx += len(content)
        remaining -= len(content)
    return start_idx
    
#######################################################
#                    Program Start                    #
#                                                     #
#######################################################
if sys.version_info <=(3,7):
    print("The tool need python3.7+")
    sys.exit(0)

with open("pam_conf.yaml", "r") as file:
    import_list = yaml.safe_load(file)

try:
    s_file = sys.argv[1]
except:
    s_file = "src.conf"
try:
    d_file = sys.argv[2]
except:
    d_file = "dst.conf"

try:
    with open(s_file,'r') as fid:
        pass
except FileNotFoundError:
    print(f"{s_file}  NOT exisit !")
    sys.exit(1)
try:
    with open(d_file,'r') as fid:
        pass
except FileNotFoundError:
    print(f"{d_file}  NOT exisit !")
    sys.exit(1)
print(f"Source Config: {s_file}\nDestination Config: {d_file}")

    
################# Scan  & Validate src.conf and dst.conf ################
print("\n-------------------Checking src.conf and dst.conf-----------------")
s_conf_ver, s_conf_enc = valid_conf_header(s_file)
src_file_sum = get_file_sum(s_file)
s_table_list = list(src_file_sum['sum'])

d_conf_ver, d_conf_enc = valid_conf_header(d_file)
dst_file_sum = get_file_sum(d_file)
d_table_list = list(dst_file_sum['sum'])

if s_conf_ver != d_conf_ver:
    resp=input("The version between src conf and dst conf are Different. Do you want to continue: [Y or N]")
    if resp.upper() != 'Y': sys.exit(0)

if s_conf_enc != d_conf_enc:
    print("Error: The encryption flag in src conf and dst conf, are Different!")
    sys.exit(1)

if len(s_table_list)==0 or len(d_table_list)==0:
    print("Error: No tables found in src.conf or dst.conf\n")
    sys.exit(1)


match_list =[]
for table_name in d_table_list:
    try:
        pos = s_table_list.index(table_name)
    except Exception as error:
        print(f"\n\nError: {table_name} in {d_file}, NOT found in {s_file}.")
        print(error)
        sys.exit(1)

    if len(match_list) >= 1:
        if pos <= match_list[-1]:
            print(f"\n\nError: table sequence between {s_file} and {d_file} is different.")
            print(f"{table_name} ")
            sys.exit(1)
    match_list.append(pos)
'''
for idx in range(len(match_list) - 1):
    if match_list[idx] > match_list[idx+1]:
        print(f"\n\nError: table sequence between {s_file} and {d_file} is different.")
        sys.exit(1)
'''
print("Pass")
################# Start to Merge ########################################
print("\n------------------ Start to merge---------------------") 
s_fid = open(s_file,'rb')
d_fid = open(d_file,'rb')
o_fid = open(O_FILE,'w',encoding='utf-8')

table_name = d_table_list[0]
for _ in range(1,dst_file_sum['sum'][table_name]['line'][0]):
    b_line = d_fid.readline()
    s_line = b_line.decode('utf-8')
    o_fid.write(s_line)

for table_name in s_table_list:
    if table_name[7:] in import_list['Override']:
        print(f"[Override Table]: {table_name}")
        table_start_idx = src_file_sum['sum'][table_name]['idx'][0]
        s_fid.seek(table_start_idx)
        start_line, end_line = src_file_sum['sum'][table_name]['line']
        #print(start_line,end_line)
        for _ in range(start_line,end_line+1):
            b_line = s_fid.readline()
            s_line = b_line.decode('utf-8')
            o_fid.write(s_line)
            #print(line,end='')     

    elif table_name[7:] in import_list['Exempt'].keys():
        print(f"[Merge Table]: {table_name}")
        o_fid.write(table_name+"\n")
        start_idx, end_idx = dst_file_sum['sum'][table_name]['idx']
        start_line, end_line = dst_file_sum['sum'][table_name]['line']
        dst_table_sum = get_table_sum(d_fid,table_name,start_idx, start_line,end_line)
        for key,value in dst_table_sum['sum'].items():
            if key == 'common':
                for cmd in dst_table_sum['sum']['common']:
                    o_fid.write(cmd)
            else:
                entry_name = key.split(" ")[-1].replace('"','')
                if entry_name in import_list['Exempt'][table_name[7:]]:
                    print(f'    Keep entry: {d_fid.name}-"{key}"')
                    start_idx, end_idx = dst_table_sum['sum'][key]
                    write_buffer(d_fid,start_idx,end_idx,o_fid)
             
        start_idx, end_idx   = src_file_sum['sum'][table_name]['idx']
        start_line, end_line = src_file_sum['sum'][table_name]['line']
        src_table_sum = get_table_sum(s_fid,table_name,start_idx, start_line,end_line)
        for key,value in src_table_sum['sum'].items():
            if key != 'common':
                entry_name = key.split(" ")[-1].replace('"','')
                if entry_name not in import_list['Exempt'][table_name[7:]]:
                    print(f'    Add entry: {s_fid.name}-"{key}"')
                    start_idx, end_idx = src_table_sum['sum'][key]
                    write_buffer(s_fid,start_idx,end_idx,o_fid)
        o_fid.write("end\n")
        
    else:
        if table_name in d_table_list:
            table_start_idx = dst_file_sum['sum'][table_name]['idx'][0]
            d_fid.seek(table_start_idx)
            start_line, end_line = dst_file_sum['sum'][table_name]['line']
            for _ in range(start_line,end_line+1):
                b_line = d_fid.readline()
                s_line = b_line.decode('utf-8')
                o_fid.write(s_line)
                #print(line,end='')
                
s_fid.close()
d_fid.close()
o_fid.close()                      
################# Validate merged file ########################################
print(f"\n--------------Verifying created {O_FILE}--------------------")
out_file_sum = get_file_sum(O_FILE)
o_table_list = list(out_file_sum['sum'])
with open(O_FILE, 'rb') as o_fid:
    for table_name in o_table_list:
        start_idx, end_idx   = out_file_sum['sum'][table_name]['idx']
        start_line, end_line = out_file_sum['sum'][table_name]['line']
        get_table_sum(o_fid,table_name,start_idx, start_line,end_line)

        
print(f"------------------------Finised!---------------------")
print(f"Please check output file {O_FILE}")

                


        
      
      


    

