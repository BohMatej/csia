import random
mylist = [2, 3, 5]
myvariable = 5

def main():
    # localVariable = 1
    # print(globals())
    # print(locals())
    # print('localVariable' in globals())
    # print('unexisting' in locals())
    # print('mylist' in locals())
    # print(foo(mylist.copy()))
    # print(mylist)
    # print("-----")
    # print(myvariable)
    # global myvariable
    # myvariable = 10

    global successCondition
    successCondition = 5
    #print(successCondition)
    #bar(10)
    #print(successCondition)
    emptylist = []
    random.shuffle(emptylist)
    for item in emptylist:
        print(item)

    
def foo(target):
    target.append(6)
    return target

def bar(depth):
    global successCondition
    if depth == 0:
        return
    else:
        successCondition += 1
        bar(depth-1)

if __name__ == "__main__":
    main()