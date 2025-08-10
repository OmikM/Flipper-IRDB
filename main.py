import os

protocols = ["RAW","NEC", "Sony SIRC", "RC5", "RC6", "Panasonic", "JVC", "Sharp", "Samsung32", "Philips RC-5X", "Denon", "Toshiba", "Hitachi", "LG", "Whynter", "Bang & Olufsen", "Kaseikyo"]
count = 0

def delete_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            delete_folder(file_path)  # recursive call for subfolders
    os.rmdir(folder_path)

def cleardata(path,f):
    ir_path = path+f

    if not os.path.isfile(ir_path):
        delete_folder(ir_path)
        return


    if(f[-2:]!="ir"):
        os.remove(ir_path)
        return

    try: 
        with open(ir_path, encoding="latin1") as f:
            content = f.read()
    except Exception as e:
        print(e)
        yn = bool(input("delete file"))
        if yn:
            if os.path.isfile(ir_path):
                os.remove(ir_path)
            else:
                delete_folder(ir_path)
        else:
            return
        
def write_f(name, prot, data, size, adr, path_fol, command):
    global count
    if data=="":
        data, size = build_ir_code(prot, adr, command)

    # print(data)

    path_file = path_fol + "/" + name + ".txt"
    os.makedirs(os.path.dirname(path_file), exist_ok=True)


    try:
        count+=1
        with open(path_file, "w", encoding="utf-8") as f:
            f.write("4" + "\n")
            f.write(str(prot)+ "\n")
            f.write(str(data) + "\n")
            f.write(str(size) + "\n")
            f.write(str(adr))

    except:
        print(path_file)
        return


def build_ir_code(p, address, command, toggle=0):

    if p == 1:
        address_byte = address & 0xFF
        inv_address = (~address_byte) & 0xFF
        command_byte = command & 0xFF
        inv_command = (~command_byte) & 0xFF
        val = (address_byte) | (inv_address << 8) | (command_byte << 16) | (inv_command << 24)
        bits = 32

    elif p == 2:
        # Sony: command in higher bits, address lower 5 bits
        val = ((command & 0x7F) << 5) | (address & 0x1F)
        bits = 12  # Usually 12, can be 15 or 20

    elif p == 3:
        # RC5 & Philips RC-5X are similar, 14 bits total
        val = 0
        val |= (1 << 13)             # Start bit
        val |= (toggle & 1) << 12    # Toggle bit
        val |= (address & 0x1F) << 6
        val |= (command & 0x3F)
        bits = 14

    elif p == 4:
        val = 0
        val |= (toggle & 1) << 19
        val |= (address & 0xFF) << 11
        val |= (command & 0xFF) << 3
        bits = 20

    elif p == 5:
        # Panasonic (Kaseikyo)
        manufacturer = address & 0xFFFF  # 16 bits
        addr = (command >> 8) & 0xFF      # Sometimes command is split
        cmd = command & 0xFF
        checksum = (addr + cmd) & 0xFF
        val = (manufacturer) | (addr << 16) | (cmd << 24) | (checksum << 32)
        bits = 48

    elif p == 6:
        # JVC: 8-bit address + 8 or 16 bit command, usually 16 bits here
        val = (address & 0xFF) << 8 | (command & 0xFF)
        bits = 16

    elif p == 7:
        # Sharp: 7 bits address + 8 bits command = 15 bits
        val = (address & 0x7F) << 8 | (command & 0xFF)
        bits = 15

    elif p == 8:
        # Samsung32 (NEC variant with 32 bits)
        val = (address & 0xFF) | ((~address & 0xFF) << 8) | ((command & 0xFF) << 16) | ((~command & 0xFF) << 24)
        bits = 32

    elif p == 9:
        # Denon: 5-bit address + 8-bit command + 1-bit inverted command = 14 bits total
        inv_command = (~command) & 1
        val = (address & 0x1F) << 9 | (command & 0xFF) << 1 | inv_command
        bits = 14

    elif p == 10:
        # Toshiba: 16-bit command (including address and command), varies by device
        val = command & 0xFFFF
        bits = 16

    elif p == 11:
        # Hitachi: 8-bit address + 8-bit command, total 16 bits
        val = (address & 0xFF) << 8 | (command & 0xFF)
        bits = 16

    elif p == 12:
        # LG: 8-bit address + 8-bit command + 12 bits unknown (fixed)
        fixed = 0xFFF  # usually fixed pattern in low bits
        val = (address & 0xFF) << 20 | (command & 0xFF) << 12 | fixed
        bits = 28

    elif p == 13:
        # Whynter AC remotes, 16-bit address + 16-bit command
        val = (address & 0xFFFF) << 16 | (command & 0xFFFF)
        bits = 32

    elif p == 14:
        # B&O: usually 16-bit command only
        val = command & 0xFFFF
        bits = 16

    elif p == 15:
        # Kaseikyo (Panasonic family) 48 bits (similar to Panasonic)
        manufacturer = address & 0xFFFF
        addr = (command >> 8) & 0xFF
        cmd = command & 0xFF
        checksum = (addr + cmd) & 0xFF
        val = (manufacturer) | (addr << 16) | (cmd << 24) | (checksum << 32)
        bits = 48
    else:
        print(p)
        val,bits = 0,0

    return val, bits

def IRtotxts(path,f, dir_n):
    ir_path = path+f

    data,name = "",""
    prot,adress,size,command = 0,0,-1,0
    val = 0
    

    dir_n = dir_n + "/" + f[:-3]

    with open(ir_path, "r", encoding="utf-8") as f:
        for line in f:
            if "name:" in line:
                print(name)
                if(name == "Aux"):
                    return
                name = line[6:-1]
                prot = 0

            elif "type:" in line:
                if(line[6:-1] == "raw"):
                    prot = 0

            elif "protocol:" in line:
                if(line[10:-1] in protocols):
                    prot = protocols.index(line[10:-1])
                else:
                    print(line[10:-1])
                    return

            elif "data:" in line:
                data = line[6:-1]
                size = len(data.split())

            elif "address:" in line:
                adress = int(("".join(line[9:-1].split())), 16)

            elif "command:" in line:
                command = int(("".join(line[9:-1].split())), 16)

            elif (line == '# \n' or line == '#\n') and name !="" :
                write_f(name, prot, data, size, adress, dir_n, command)

    write_f(name, prot, data, size, adress, dir_n, command)

                






directory = '/Users/Oskar/Documents/projects/Flipper-IRDB/old_data'
dir_n = '/Users/Oskar/Documents/projects/Flipper-IRDB/new_data'



devices = os.listdir(directory)

i = 1000000

for d in devices:
    brands = os.listdir(directory+'/'+d)
    for b in brands:
        files = brands = os.listdir(directory+'/'+d+'/'+b)
        for f in files:
            if(i>0):
                IRtotxts(directory+'/'+d+'/'+b + '/', f, dir_n+'/'+d+'/'+b )
                # cleardata(directory+'/'+d+'/'+b + '/', f)
                i-=1
print(count)