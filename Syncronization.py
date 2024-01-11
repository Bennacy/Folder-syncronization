import sys
import os
import keyboard
import schedule
import time
from datetime import datetime
import filecmp
import shutil



run = True
iteration = 0

def _stop(log_path):
    global run
    run = False

    f = open(log_path, 'a')
    f.write('\n\n-------------Ended syncronization-------------')
    print('\n\n-------------Ended syncronization-------------')
    f.close()
    exit()


def _log(message, log):
    print(message)
    log.write(message)


#! Recursively clear a folder of its contents, and then delete the newly empty folder
def clear_directory(path):
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            clear_directory(file_path)
            os.rmdir(file_path)



def check_files(source, replica, log, original = False):
    #! Test for errors locating the 'Source' and 'Replica' folders
    if not (os.path.exists(source_path) and os.path.exists(replica_path)):
        print('\tInvalid folder paths!')
        _stop(log_path)
        return
    
    source_files = os.listdir(source)
    replica_files = os.listdir(replica)
    changed = False
    
    #! Run through every file in the 'Source' folder, and check to see if a matching file exists in the 'Replica' folder
    #! If not, either update an existing file, or create an entirely new one if necessary
    for file in source_files:
        match = True
        source_filepath = os.path.join(source, file)
        replica_filepath = os.path.join(replica, file)

        #! Test for non-existing file at given path
        if not os.path.exists(replica_filepath):
            path_type = 'file'
            if os.path.isdir(source_filepath):
                path_type = 'folder'
            _log('\tCreated ' + path_type + ' "' + str(source_filepath) + '"\n', log)
            match = False
            changed = True
        
        #! Test for outdated file at given path
        if match:
            if os.path.isfile(source_filepath) or os.path.islink(source_filepath):
                match = filecmp.cmp(source_filepath, replica_filepath)
                if not match:
                    changed = True
                    _log('\tUpdated file "' + str(source_filepath) + '"\n', log)
                    
            elif os.path.isdir(source_filepath):
                check_files(source_filepath, replica_filepath, log)

        #! If an earlier test proved true, copy from 'Source' to 'Replica'
        if not match:
            changed = True
            if os.path.isfile(source_filepath) or os.path.islink(source_filepath):
                shutil.copy(source_filepath, replica_filepath)
            elif os.path.isdir(source_filepath):
                shutil.copytree(source_filepath, replica_filepath)
    
    #! Run through every file in the 'Replica' folder, and look for files that do not exist in the 'Source' folder
    #! If any such files are found, delete them from the 'Replica' folder
    for file in replica_files:
        source_filepath = os.path.join(source, file)
        replica_filepath = os.path.join(replica, file)

        if not os.path.exists(source_filepath):
            changed = True

            if os.path.isfile(replica_filepath) or os.path.islink(replica_filepath):
                os.unlink(replica_filepath)
                _log('\tDeleted file "' + str(source_filepath) + '"\n', log)
                
            elif os.path.isdir(replica_filepath):
                #! Custom made way of emptying and deleting folders, in case use of shutil is not preferable
                # clear_directory(replica_filepath)
                # os.rmdir(replica_filepath)
                
                shutil.rmtree(replica_filepath)
                _log('\tDeleted folder "' + str(source_filepath) + '"\n', log)

    if not changed and original:
        _log('\tNo changes\n', log)



def syncronize_folders(source_path = None, replica_path = None, log_path = None):
    #! Test for errors locating the 'Source' and 'Replica' folders
    if not (os.path.exists(source_path) and os.path.exists(replica_path)):
        print('\tInvalid folder paths!')
        _stop(log_path)
        return

    global iteration
    log = open(log_path, "a")
    _log('Iteration ' + str(iteration) + ':\n(' + datetime.now().strftime("%b %d, %Y %H:%M:%S") + ')\n', log)

    check_files(source_path, replica_path, log, True)

    _log('\n\n', log)
    log.close()
    iteration = iteration+1





if __name__ == "__main__":
    os.system('cls')


    #! Tests for valid arguments and folder directories
    enough_args = len(sys.argv) == 5
    if not enough_args:
        print('\nInvalid command line arguments!\n(Syncronization time, Source path, Replica path, Log path)')
        exit()
    else:
        wait_time = int(sys.argv[1])
        source_path = sys.argv[2]
        replica_path = sys.argv[3]
        log_path = sys.argv[4]

    if not os.path.isdir(source_path):
        print('Source folder could not be found at "' + source_path + '"')
        exit()
    if not os.path.isdir(replica_path):
        print('Replica folder could not be found at "' + replica_path + '"')
        exit()
    if not os.path.isfile(log_path):
        print('Log file could not be found at "' + log_path + '"')
        exit()


    #! Clear old log file, can be removed if not necessary
    f = open(log_path, "w")
    f.write('')
    f.close()

    #! Run the sync function once so that the user does not need to wait for the specified time before the first operation
    syncronize_folders(source_path, replica_path, log_path)
    #! Currently uses seconds as the delay, but can be changed to minutes/hours for actual use
    j = schedule.every(wait_time).seconds.do(syncronize_folders, source_path, replica_path, log_path)
    #! Added hotkey to easily end the process, can be removed
    keyboard.add_hotkey('escape', _stop, {log_path})
    
    while run:
        schedule.run_pending()
        time.sleep(1)