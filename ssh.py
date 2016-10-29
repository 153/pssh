#/usr/bin/python3
from subprocess import call
import time, os

time_form = '%Y-%m-%d %H:%M'
a_loc = "adds.txt"
r_dir = "./remote/"

# initialize the file with `localhost 0000000000'

def fancy_time(utime='', mode=''):
    if not utime:
        utime = int(time.time())
    else:
        utime = int(utime)
    if mode == 'unix':
        return str(utime)
    htime = time.localtime(utime)
    htime = time.strftime(time_form, htime)
    if mode == "human":
        return htime
    else:
        return [utime, htime]

def time_diff(time_a, time_b):
    # takes 2 unix timestamps as input,
    # returns 2 largest datetime units
    time_c = time_a - time_b        
    consts = [1, 1, 60, 3600, 86400, 604800, 2629746, 31556952]
    abbrv  = ['', 's', 'm', 'h', 'd', 'w', 'm', 'y']
    string = []
    
    for n, i in enumerate(consts):
        if i > time_c:
            tmp = time_c
            string.append(str(tmp//consts[n-1]) + abbrv[n-1])
            if abbrv[n-1] == 's':
                break
            while tmp >= consts[n-1]:
                tmp -= consts[n-1]
            string.append(str(tmp//consts[n-2]) + abbrv[n-2])
            break

    return " ".join(string)

def add_addr():
    where = input("Please enter the host you wish to access.\n> ")
    call(["ssh-copy-id", where])
    with open(a_loc, 'a') as add:
        add.write(where + " 0000000000\n")
        
def rem_addr():
    adds = loadr('a')
    for n, i in enumerate(adds):
        print(n, "-", i)
    where = input("Please select which host you would like to remove:\n> ")
    try:
        where = int(where.strip())
        if 0 <= where < len(adds):
            print("Really remove", adds[where] + "?")
            conf = input("[y/n] ").strip()
            if conf == 'y':
                print("Deleting", adds[where] + "...")
                loadr('r', where)
                print("...Returning home.")
        else:
            print("Invalid number.\nh")
            rem_addr()
            
    except:
        print("Sorry, the address could not be removed.")

def mount_rfs():
    print(r_dir)
    addies = loadr('a')

    if len(addies) > 1:
        prompt = "[0-{0}] ".format(len(addies) -1)
        print("The addresses you can mount are:\n")
    else:
        prompt = "[0] "
        print("The address you can mount is:\n")
    for n, i in enumerate(addies):
        print("* {0}) {1}".format(n, i))
    print("\nWhich one would you like to mount?\n")

    choice = input(prompt).strip()
    host = None

    try:
        if 0 <= int(choice) < len(addies):
            host = addies[int(choice)]
    except:
        pass
    
    if not host:
        print("Your selection is invalid.")
        x = input("Would you still like to try mounting?\n[y/n] ").strip().lower()
        if x == 'y':
            mount_rfs()
        else:
            return
        
    print("Connecting...")
    if len(os.listdir(r_dir)) == 0:
        wai = os.getcwd()
        print("Connected at", loadr('c', int(choice)))
        print("Mounting, end session with Control-D.\n")
        call(["sshfs", host + ":", r_dir])
        os.chdir(r_dir)
        call(["bash"])
        os.chdir(wai)
        call(["fusermount", "-u", r_dir])
        print("\n\nUnmounted.")
    else:
        print("\nPlease make sure that", r_dir, "exists and is empty.")

    
def loadr(d_mod='a', choi=0):
    # a -- list of addresses without time info
    # c -- update address 'choi' as last connected now
    # r -- remove address 'choi'
    # t -- present addresses with "time since"
    t_now = fancy_time()
    
    with open(a_loc, 'r') as adds:
        adds = adds.read().splitlines()
        for n, i in enumerate(adds):
            adds[n] = adds[n].split(" ")
        
    if d_mod == 'a':
        for n, i in enumerate(adds):
            adds[n] = adds[n][0]
        return adds
            
    elif d_mod == 'c':
        adds[choi][1] = str(t_now[0])
        adds = sorted(adds, key=lambda x: int(x[1]), reverse=True)
        for n, i in enumerate(adds):
            adds[n] = " ".join(i)
        adds = "\n".join(adds)
        with open(a_loc, 'w') as new_adds:
            new_adds.write(adds+"\n")
        return t_now[1]
    
    elif d_mod == 'r':
        del adds[choi]
        for n, i in enumerate(adds):
            adds[n] = ' '.join(i)
        adds = '\n'.join(adds)
        with open(a_loc, 'w') as new_adds:
            new_adds.write(adds+'\n')
        return None
        
    elif d_mod == 't':
        t_list = []
        for n, i in enumerate(adds):
            x = [i[0], time_diff(t_now[0], int(i[1]))]
            t_list.append(x)
        return t_list        

def keygen():
    print("Generating SSH key...")
    call(["ssh-keygen"])
    
def opts(mo="s"):
    opts = {'a': "add", 'd': "delete", 'm': "mount", 'q': "keygen"}
    if mo == "s":
        o_string = []
        for i in sorted(opts.keys()):
            o_string.append("[" + i + "] " + opts[i])
        return " ".join(o_string)
    elif mo == "k":
        return(sorted(opts.keys()))
    elif mo == 'a':
        add_addr()
    elif mo == 'd':
        rem_addr()
    elif mo == 'm':
        mount_rfs()
    elif mo == 'q':
        keygen()
    

def cprompt():
    print("*"*50)
    print(" "+ opts())
    print("*"*50)
    addies = loadr('t')
    if len(addies) > 1:
        prompt = "[0-{0}] ".format(len(addies) -1)
        print("The addresses you can connect to are:\n")
    else:
        prompt = "[0] "
        print("The address you can connect to is:\n")
    for n, i in enumerate(addies):
        print("* {0}) {1}\n   {2}".format(n, i[0], i[1]))
        
    print("\nWhich one would you like to connect to?\n")
    print("You can also add an entry with 'a' or remove one with 'r'")
    choice = input(prompt).strip()
    try:
        if 0 <= int(choice) < len(addies):
            l_connect = fancy_time()
            print("Connected at", loadr('c', int(choice)))
            call(["ssh", addies[int(choice)][0]])

    except:
        if choice[0].lower() in opts('k'):
            print(choice.strip())
            opts(choice.strip()[0].lower())

    cprompt()

def main():
    if not os.path.isfile(a_loc):
        with open(a_loc, "x") as add:
            init = "localhost 0000000000\n"
            add.write(init)
        print("Initialized addressbook.")
    if not os.path.isfile(r_dir) and not os.path.isdir(r_dir):
        os.mkdir(r_dir)
        print("Created remote mounting directory.")
    cprompt()

main()
