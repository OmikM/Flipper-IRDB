import os

protocols = ["NEC", "Sony SIRC", "RC5", "RC6", "Panasonic", "JVC", "Sharp", "Samsung", "Philips RC-5X", "Denon", "Toshiba", "Hitachi", "LG", "Whynter", "Bang & Olufsen"]

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
            if os.path.isfile(path):
                os.remove(ir_path)
            else:
                delete_folder(ir_path)
        else:
            return

def IRtotxts(path,f):
    print(f + " " + path)
    ir_path = path+f

    
        
    print(ir_path)
    prot = -1
    data = ""
    size = 0
    adress = ""
    with open(ir_path, "r", encoding="utf-8") as f:
        for line in f:
            if "name:" in line:
                name = line[6:]
                prot = 0
                print(name + '\n' + str(prot) + '\n' +data+ '\n' + str(size) + '\n' +adress)
            elif "type:" in line:
                if(line[6:] == "raw"):
                    prot = 0
            elif "protocol:" in line:
                if(line[10:] in protocols):
                    prot = protocols.index(line[10:])
                else:
                    print(protocols)
            elif "data:" in line:
                data = line[6:]
                size = len(data.split())

            elif "address:" in line:
                adress = line[9:]






directory = '/Users/Oskar/Documents/projects/Flipper-IRDB/old_data'


devices = os.listdir(directory)

i = 1

for d in devices:
    #print(directory+'/'+d)
    brands = os.listdir(directory+'/'+d)
    for b in brands:
        #print(b)
        files = brands = os.listdir(directory+'/'+d+'/'+b)
        for f in files:
            if(i>0):
                IRtotxts(directory+'/'+d+'/'+b + '/', f)
                i-=1

