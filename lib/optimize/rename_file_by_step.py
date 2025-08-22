import os

if __name__ == "__main__": 

    dirToRenameFile = './input_data'

    entries = os.listdir(dirToRenameFile)

    i = 0
    nameTofind= "Step " + str(i) + " "
    for entry in entries:
        for entry2 in entries:
            nameTofind= "Step " + str(i) + " "
            nameToAdd =  "Step" + str(i) + "_"
            if(entry.find(nameTofind) != -1) :
                if(entry[:len(nameToAdd) - 1] != nameToAdd):
                    print(nameToAdd)
                    os.rename(dirToRenameFile + "/" + entry, dirToRenameFile + "/" + nameToAdd + entry)
                # print(entry, " vs ", nameTofind, entry.find(nameTofind))
            i += 1
        i = 0