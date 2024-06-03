#!/usr/bin/python3

list = [8,6,3,2,5,4,1,7]

print(list)

nswaps=1

while(nswaps>0):
    print('Let us try to do some swaps!')
    nswaps=0
    for i in range(len(list)-1):
        if(list[i]>list[i+1]): # swap!!!!
            temp=list[i]
            list[i]=list[i+1]
            list[i+1]=temp
            nswaps+=1
            print('Swap!!!')
            print(list)

    print('There were ',nswaps,' swaps.')
    print(list)

print('We are done and let us print the final answer:')
print(list)
