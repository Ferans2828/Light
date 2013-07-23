'''
Created on 5 Jan 2013

This module contains some utilities for backing up file.
The motivation for this was to help me sort out video, picture files before backing them up.

The functions here were for my files.  I put in some extra conditions to make sure I was only 
renaming files I wanted to. You should tweek for your own needs.

Next up: 
-- tell you what files are not backed up.
-- create a CSV(s) of exactly what happened to what file

USeful unix commands to check things:
- diff //diskstation/photo/2012 ./pictures/2012

This is a silly edit to test source tree
@author: Alex
'''
import os
import time
import platform
from datetime import date
from datetime import datetime
from pprint import pprint
import logging
import sys
from pprint import pformat
from collections import defaultdict
import shutil
import os.path
from os import rename
import sys   
import subprocess
import re
from sets import Set

# Logging stuff
LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

rootDirectory = 'C:\\Users\\Alex\\Videos';

pic_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
music_exts = ('.mp3', '.wav')
video_exts = ('.MOD', '.mod', '.mp4', '.mpg', '.mpeg', '.avi', '.3gp')
doc_exts = ('.doc', '.txt', '.docx')

# dir's
alex_phone_dir_ms='G:\DCIM\Camera';
sharon_phone_dir_ms="C:\sharontemp";
alex_phone_dir=os.path.join('computer', 'GT-I9100', 'Phone', 'DCIM', 'Camera')
cannon_camcorder_dir='F:\SD_VIDEO\PRG001';

nas_temp_temp_dir="C:\\nastemp\\temp";
nastemp_dir="C:\\nastemp";

#
# DateTime formats
#
old_backup_format = "%d-%b-%Y-%H_%M_%S";
old_backup_format_long_month = "%d-%B-%Y-%H_%M_%S"; # same as above except month like July instead of Jul
alldigits_date_format = "%Y%m%d%H%M%S"  # example  20100606102217.mpg
# Example: 20121208_190835.mp4  
mp4_format_alex_phone = "%Y%m%d_%H%M%S";
newformat = "%Y-%m-%d_%H%M%S";

# mass storage tutorial

def main():
    # print python version
    set_up_logging();
    prompt_main_menu();
    
'''
Configures logging
'''
def set_up_logging(userLoggingLevel = logging.INFO):
    logging_level = LOGGING_LEVELS.get(userLoggingLevel, logging.ERROR)
    log = logging.getLogger()
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)
    log.setLevel(logging_level)
    log.addHandler(ch);

    # Now set up file.
    
    logfilename = datetime.now().strftime('fileutils_%H_%M_%a_%d_%b_%Y.log')

    fh = logging.FileHandler(logfilename)
    fh_fmt = logging.Formatter("%(levelname)s %(asctime)s %(process)d %(funcName)s(),%(lineno)d: %(message)s")
    fh.setFormatter(fh_fmt)
    fh.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.addHandler(fh);
    logging.info("@author Alex Stavliniski, Feb 2013")
    logging.debug("Running file utils at " + datetime.now().strftime("%H:%M" + " %a %d %b %Y") +
                    ", logfile is " + logfilename);
    logging.info("Python version %s" % (platform.python_version()))

def prompt_main_menu(): 
    while True:
        choice = raw_input("Do you want to: \n(1) Copy files from a device onto laptop? \n(2) Transfer files to External hard drive " + 
                           "\n(3) Transfer files to NAS \n(4) Utility functions \n(5) Make a cup of Teas? " + 
                           "\n(6) Exit.\n>");
        choice = int(choice)
        print ("You entered: %s " % choice);
        if 0 < choice < 7:
            break
    if choice == 1:
        copy_files_from_device()
    elif choice == 2:
        move_files_to_backup("")
    elif choice == 3:
        move_files_to_backup("")
    elif choice == 4:
        prompt_util_function();
    elif choice == 5:
        print("We don't do cups of tea!");
        prompt_main_menu();
    elif choice == 6:
        print("Bye Bye!");
        exit;
         
def prompt_util_function():         
    while True:
        choice = raw_input("Do you want to: \n(1) Rename files to the correct yy-mm-dd format" +
                           " \n(2) Find dodgy named files like _001, _002 _003?" + 
                           " \n(3) Get info about a dir?" +  
                            "\n(4) Move file formats into correct dirs?" +    
                            "\n(5) Compare files in two directories?" +                    
                           " \n(6) flatten files?" + 
                           " \n>");
        choice = int(choice)
        print ("You entered: %s " % choice);
        if 0 < choice < 8:
            break
    if choice == 1:
        rename_files_for_user();
    elif choice == 2:
        util_find_dodgy_files();
    elif choice == 3:
        util_get_info_about_dir();
    elif choice == 4:
        util_move_file_into_correct_format_dirs();
    elif choice == 5:
        util_compare_files();
    elif choice == 6:
        util_flatten_files();
    elif choice == 7:
        prompt_main_menu();
    prompt_main_menu();
    
def util_get_info_about_dir():
    user_dir = raw_input("Specify dir? \n>");
    countFiletypes(user_dir);
    prompt_util_function();

def util_move_file_into_correct_format_dirs():
    base_dir = raw_input("Specify the base dir that you think might have files of a certain format in the wrong dir? \n>")
    
    # check for videos in photos
    for root, dirs, files in os.walk(base_dir + "\photo"):
        for filename in files:
            # only check files in correct name formate
            filename_without_ext = os.path.splitext(filename)[0];
            if not re.match(r'\d{4}-\d{2}-\d{2}_\d{6}$', filename_without_ext):
                continue; 
            ext = os.path.splitext(filename)[-1].lower();
            if ext in video_exts:
                # 1. Tell the user what these files are.
                # 2. Offer to move

                year_of_file = filename[0:4]
                destdir = base_dir + "\\video";
                new_file_path = destdir + '\\' + year_of_file + '\\' + filename;
                from_path = root + "\\" + filename;
                move_file = raw_input("Move file: %s to %s (Y)es? \n>" % (from_path, new_file_path)); 
                if move_file == "Y" or move_file == "y" or move_file == "Yes":
                    # get the year of the file
                    print("Moving file %s to %s..." % (from_path, new_file_path));
                    shutil.move(from_path, new_file_path) 
    
    # check for pictures in videos.
    # 1. Tell the user what thes files are.
    # 2. Offer to move.
    prompt_util_function();
    
def util_compare_files():
    files_to_compare_choice = raw_input("Compare (p)hotos, (v)ideos?")
    if files_to_compare_choice == "p":
       files_to_compare = "photo"
    else:
        files_to_compare = "video" 
    # TBD
    # prompt user for dir1 
    # prompt user for dir2
    dir1_files = Set();
    dir2_files = Set();
    
    dir1 = raw_input("Input dir1? \n>");
    fulldir1 = dir1 + "\\" + files_to_compare
    print("Looking at files from %s ..." % fulldir1);
    for root, dirs, files in os.walk(fulldir1):
        for filename in files:
            dir1_files.add(filename)
    
    dir2 = raw_input("Input dir2? \n>");
    fulldir2 = dir2 + "\\" +  files_to_compare;
    print("Looking at files from %s ..." % fulldir2);
    for root, dirs, files in os.walk(fulldir2):
        for filename in files:
            dir2_files.add(filename)
            
    in_dir1_not_dir2 = dir1_files - dir2_files;
    in_dir2_not_dir1 = dir2_files - dir1_files;
    if len(in_dir1_not_dir2) == 0:
        print("There is nothing in %s that is not in %s" % (fulldir1, fulldir2));
    else:
        print("In %s but not %s..." % (fulldir1, fulldir2))
        print(pformat(sorted(list(in_dir1_not_dir2))));
    
    if len(in_dir2_not_dir1) == 0:
        print("There is nothing in %s that is not in %s" % (fulldir2, fulldir1));
    else:
        print("In %s but not %s..." % (fulldir2, fulldir1))
        print(pformat(sorted(list(in_dir2_not_dir1))));
    
    prompt_util_function();

'''
user specifies directory for files to be renamed.
'''
def rename_files_for_user():
    while True:
        user_dir = raw_input("Specifiy the dir that contains the files you want to rename (e.g. C:\\nastemp\\temp)?\n>");
        confirm = raw_input("%s, are you sure? (Y)es or (N)o\n>" % user_dir);        
        if confirm == "Y" or confirm == "y" or confirm == "Yes":
            checkOnly = raw_input("Do you want to check what they will be renamed to first? (Y)es or (N)o \n>")
            if checkOnly == "N" or checkOnly == "n" or checkOnly == "No":
                checkFlag = False;
            else:
                checkFlag = True;
            rename_files_in_directory_using_last_updatetime(user_dir, pic_exts + video_exts, checkFlag);
            break;

def copy_files_from_device():
    check_dir_empty("C:\\nastemp");
    import_user_files()

# Asks the users where they want to import files from
def import_user_files():
    print("PLEASE, whatever you are copying from please delete unwanted files first. Avoid garbage in / garbage out")
    while True:
        choice = raw_input("Do you want to: \n(1) Import from Alex's phone mass storage \n(2) Import from Sharon's phone \n(3) Import from camcorder \n(4) Import from camcorder \n(5) Something else \n(6) Exit\n>");
        choice = int(choice)
        print ("You entered: %s " % choice);
        if 0 < choice < 7:
            break
    if choice == 1:
        import_from_alex_phone_ms()
    elif choice == 2:
        import_from_sharon_phone()
    elif choice == 3:
        import_from_cannon_camcorder()
    elif choice == 4:
        import_from_cannon_camcorder()
    elif choice == 6:
        print("Goodbye!")
        sys.exit()
         
    else:
        print("That was not 1-6")

def import_from_alex_phone_ms():
    check_mass_storage_enabled();      
    print("Reading Alex's phone dir is %s" % sharon_phone_dir_ms);
    import_files_from_device(sharon_phone_dir_ms, pic_exts + video_exts);

def import_files_from_device(import_dir, file_types) :
    print("Importing files of type %s from %s " %(str(file_types), import_dir))
    totalFiles = countFiletypes(import_dir);
    
    if (totalFiles < 10):
        if (totalFiles == 0):
            continueOption = raw_input("There are no files to copy. Are you sure the phone is connected?\n>");
        else:
            continueOption = raw_input("There are less than ten files to copy. Continue?\n>");

        if continueOption == "No" or continueOption == "N" or continueOption == "n":
            print("Ok dude bye bye!")
            return; 
    
    # now copy 
    for root, dirs, files in os.walk(import_dir):
        for filename in files:
            # only copy pics and videos
            # check ext
            ext = os.path.splitext(filename)[-1].lower();
            if ext in file_types:
                longFilename = root + "\\" + filename;  
                print("Copying filename=%s to %s" % (longFilename, nas_temp_temp_dir));
                shutil.copy(longFilename, nas_temp_temp_dir);
            else:
                print("Not copying filename=%s" % filename);
    
            
    # rename files
    rename_files_in_directory_using_last_updatetime(nas_temp_temp_dir, pic_exts + video_exts, False);
                
    # TBD            
    # tag files
    # tagFiles(alex_phone_dir_ms, "alex's phone");
    
    print("STOP! Everything is in C:\nastemp\temp \n You must now: \n1. Remove Junk photos \n2. Tag the files.\n It is VERY important this is done. Use MS photo gallery");
    subprocess.call("C:\\Program Files (x86)\\Windows Live\\Photo Gallery\\WLXPhotoGallery.exe")
    print(" MARES SURE YOU DO THAT ! Bye Bye!");
    sys.exit();
    
def check_mass_storage_enabled() :   
    while True:
        mass_storage_choice = str(raw_input("Have you enabled USB mass storage on the phone Y(Y)es or No?\n>"));
        print("Wait a sec")
        if mass_storage_choice == "y" or mass_storage_choice == "Y" or mass_storage_choice == "Yes":
            print("Connected! Good stuff dude.")
            break
        else: 
            print("Not connected! Go to settings /  USB Mass storage / Connect storage to PC")     


def move_files_to_backup(dir_to_move_to):
    move_to_correct_nastemp_dirs();
    copy_nastemp_to_external_device(dir_to_move_to);
 
    
# Move to correct pre dirs
def move_to_correct_nastemp_dirs():
    while True:
        input = raw_input("Are you flipping SURE you have removed all junk photos / videos and left only top quality in %s (y) or (n)?\n>" % nas_temp_temp_dir)
        if input == "y":
            break;
    while True:
        input = raw_input("Are you flipping sure you have tagged all photos in %s using MS photo gallery?\n>" % nas_temp_temp_dir);
        if input == "y":
            break;        
    print("Moving photos to nastemp yearly directories...");
    move_files_to_year(nas_temp_temp_dir, "C:\\nastemp\\photo", pic_exts);
    print("Moving photos to nastemp yearly directories...");
    move_files_to_year(nas_temp_temp_dir, "C:\\nastemp\\video", video_exts);
    
    # at the end of this the temo directory should be empty otherwise fail.
    check_dir_empty(nas_temp_temp_dir)
    # NEXT Up do video, music, audio

def copy_nastemp_to_external_device(dir_to_move_to):
    if dir_to_move_to == None or dir_to_move_to == "":
        while True:
            dir_to_move_to = raw_input("You did not specify a directory to move to, enter one dude and use \\ for a single \\. \n>");
            if dir_to_move_to != "":
               break;   
    print("Copying the files in %s to %s" % (nastemp_dir, dir_to_move_to));
    countFiletypes(nastemp_dir); 
    print("Starting copy...");    
    for root, dirs, files in os.walk(nastemp_dir):
        for filename in files:
            longFilename = root + "\\" + filename;
            # remove the C:\nastemp
            full_path_to_move_to = dir_to_move_to + root[10:]; 
            if not os.path.isfile(full_path_to_move_to):
                print("Copying filename=%s to dir=%s" % (longFilename, full_path_to_move_to));
                logging.info("Copying filename=%s to dir=%s" % (longFilename, full_path_to_move_to));
                shutil.copy(longFilename, full_path_to_move_to);
            else:
                print("Not copying filename %s to dir %s, because it is already there" % (longFilename, full_path_to_move_to))
    print("Finished copy");
    prompt_main_menu();


    
def import_from_sharon_phone():
    check_mass_storage_enabled();      
    print("Reading Sharon's phone dir is %s" % sharon_phone_dir_ms);
    import_files_from_device(sharon_phone_dir_ms, pic_exts + video_exts);
    
def import_from_cannon_camcorder():
    print("Camcorder path is %s" % cannon_camcorder_dir)
    # Have to rename camcorder video files first.
    rename_files_in_directory_using_last_updatetime(cannon_camcorder_dir, pic_exts + video_exts, False)
    import_files_from_device(cannon_camcorder_dir, pic_exts + video_exts);

def import_from_camera():
    print("Camera path is")
    


'''
Renames files in a directory that have .mod extension to be of the form 
YEAR_MONTH_DAY_TIME_COUNTER_VALUE, where the datetime is last modified datetime
of the file. The idea is here that it is much easier to sort your media files if they are
named by timestamp of when they were taken rather than some arbitrary name. It also makes it easier 
to sort them and back them up
Renames to format:
2012-May-23-17:42
'''
def rename_files_in_directory_using_last_updatetime(rootDir, file_exts, safteymode=True):
    for root, dirs, files in os.walk(rootDir, topdown='true'):
        # print dir contents before rename
        print("Dir %s currently contains:" % root)
        print(pformat(sorted(os.listdir(root))));
        counter = 1;
        for filename in files: 
            ext = os.path.splitext(filename)[-1].lower();
            if (ext in file_exts):
                # check filename not already in file format
                filename_without_ext = os.path.splitext(filename)[0];
                if re.match(r'\d{4}-\d{2}-\d{2}_\d{6}$', filename_without_ext):
                    continue  # already converted leave it alone
                elif re.match(r'\d{1,2}-\w{3}-\d{4}-\d{1,2}_\d{1,2}_\d{1,2}$', filename_without_ext):
                    # Format is like: 31-Mar-2013-14_24_36.jpg
                    newfilename = util_convert_old_date_format_to_new(old_backup_format, filename);
                elif re.match(r'\d{1,2}-\[a-z][A-Z]{3,}-\d{4}-\d{1,2}_\d{1,2}_\d{1,2}$', filename_without_ext):
                    # Format is like: 31-Mar-2013-14_24_36.jpg
                    newfilename = util_convert_old_date_format_to_new(old_backup_format_long_month, filename);
                elif re.match(r'\d{2}-\w{3}-\d{4}-\d{2}_\d{2}_\d{2}_\d{1,}$', filename_without_ext):
                    # Format is like: 31-Mar-2013-14_24_36.jpg
                    raise Exception("Cannot rename" + filename_without_ext);
                elif re.match(r'\d{8}_\d{6}$', filename_without_ext): 
                    # This will deals with the likes of 20121208_190835.mp4  that come from 
                    # Alex's phone
                    newfilename = util_convert_old_date_format_to_new(mp4_format_alex_phone, filename);
                elif re.match(r'\d{14}$', filename_without_ext):
                    # Deals with the like of 20100904154910
                    newfilename = util_convert_old_date_format_to_new(alldigits_date_format, filename);
                else:     
                    statbuf = os.path.getmtime(root + '\\' + filename)
                    t = datetime.fromtimestamp(statbuf);
                    counter += 1;
                    # Some good tips on time formats here: http://www.tutorialspoint.com/python/time_strptime.htm
                    # The old format I was using was: "%d-%b-%Y-%H_%M_%S". I changed to make it easier to orde things         
                    newfilename = t.strftime("%Y-%m-%d_%H%M%S") + ext;
                print('Dir= %s, renaming file %s to %s' % (root, filename, newfilename))
                # check if file already exists
                
                counter = 0;
                while (os.path.exists(root + "\\" + newfilename)):
                    counter += 1;
                    print("%s is already there dude, going to try a slight change to..." % newfilename);
                    newfilename = filename_without_ext[0:18] + str(counter % 60) + ext;
                
                if not safteymode:
                    try:
                        os.rename(root + '\\' +  filename, root + '\\' + newfilename);
                    except RuntimeError:   # this was except FileExistsError in python 3.3
                        logging.info("file %s already exists " % newfilename);
                        raise Exception;
                        # Alex temp out
                        # newfilename = t.strftime("%d-%b-%Y-%H_%M_%S") + '_' + str(counter) + ext; 
                        # os.rename(root + '\\' +  filename, root + '\\' + newfilename)
        # print dir contents after rename
        print(pformat(sorted(os.listdir(root))));


''' 
finds dodgy names files such as:
06-Apr-2008-11_42_18_1090.jpg and give an option to have it renamed to 06-Apr-2008-11_42_18.jpg
'''
def util_find_dodgy_files():
    include_all_bad = raw_input("Include all dodgy files not just the ones like: 20-Jul-2012-18_36_47_34.jpg " + 
                                   "\n (Y)es or (N)o?" + 
                                   "\n>");
    
    dir = raw_input("Enter the root dir for where you want to check for dodgy files. \n>")
    dodgy_files = [];
    for root, dirs, files in os.walk(dir, topdown='true'):
        for filename in files: 
            filename_without_ext = os.path.splitext(filename)[0];
            if re.match(r'\d{2}-\w{3,}-\d{4}-\d{2}_\d{2}_\d{2}_\d{1,}$', filename_without_ext):
                dodgy_files.append(root + "\\" + filename);
            elif not re.match(r'\d{4}-\d{2}-\d{2}_\d{6}$', filename_without_ext) and (include_all_bad == "Y" or include_all_bad == "y"):
                dodgy_files.append(root + "\\" + filename);
                
    print(pformat(sorted(dodgy_files)));
    
    if (len(dodgy_files) == 0):
        print("Well done Batman, I can't find any dodgey names files")
        prompt_main_menu();
    
    choice = raw_input("Hope you enjoyed having your sloppy file names pointed out to you, would you like them renamed,"  +
                       "\n(Y)es or (N)o?" + 
                       "\n>");
                       
    allfilenames = [];
    if choice == "y" or choice == "Y" or choice == "Yes":
        for root, dirs, files in os.walk(dir, topdown='true'):
            for filename in files:
                allfilenames.append(filename); 
                filename_without_ext = os.path.splitext(filename)[0];
                if re.match(r'\d{2}-\w{3,}-\d{4}-\d{2}_\d{2}_\d{1,}_\d{1,}$', filename_without_ext):
                    ext =  os.path.splitext(filename)[-1].lower();
                    # valie file names can only have 01-Jan-2008-00_00_00 characters
                    newfilename = filename_without_ext[0:20] + ext;
                    counter = 0;
                    while (newfilename in allfilenames):
                        counter += 1;
                        print("%s is already there dude, going to try a slight change..." % newfilename);
                        newfilename = filename_without_ext[0:18] + str(counter % 60) + ext;
                    print("renaming %s to %s"  % (root + "\\" + filename, root + "\\" + newfilename));
                    allfilenames.append(newfilename);
                    shutil.move(root + "\\" + filename, root + "\\" + newfilename);
                    

''' 
Puts all files in a subdirectory of a directory into the directory
'''
def util_flatten_files():
    dir_to_flatten = raw_input("Enter dir to flatten?");
    for root, dirs, files in os.walk(dir_to_flatten):
        if root == dir_to_flatten:
            continue;
        for file in files:
            if file == "Thumbs.db" or file == ".picasa.ini":  # who cares?
                continue;
            original_file = root+ '\\' + file
            print("Moving file %s to %s" % (original_file, dir_to_flatten))
            shutil.move(original_file, dir_to_flatten) 
    
'''
converts dates from 31-Mar-2013-14_24_36.jpg to 2013-03-31_1424_36.jpg
Utiliy method for legacy files. Not used in normal backups.
'''
def util_convert_old_date_format_to_new(oldformat, olddate_filename):

    ext =  os.path.splitext(olddate_filename)[-1].lower();
    filename_without_ext = os.path.splitext(olddate_filename)[0];
    
    newdate = datetime.strptime(filename_without_ext, oldformat);
    newfilename = datetime.strftime(newdate, newformat) + ext;
    return newfilename;
  

    
    
# Move a file with a year in the time stamp to the appropriate folder
def move_files_to_year(rootDir, destDir, files_exts):
    print("Moving files of type %s to yearly directories, from %s to %s" % (str(files_exts), rootDir, destDir))
    countFiletypes(rootDir);
    years = ('2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013')
    for root, dirs, files in os.walk(rootDir):
        for file in files:
            ext = os.path.splitext(file)[-1].lower();
            if ext in files_exts:
                for year in years:
                    year_of_file = file[0:4]
                    if year_of_file == year:
                        existingfile = root + '\\' + file;
                        newfile = destDir + '\\' + year + '\\' + file
                        logging.info("Moving file %s to %s" % (existingfile, newfile))
                        shutil.move(existingfile, newfile)                     
            

# outputs the number of various file types in directory 
def countFiletypes(rootDir):
    print("Currently, the dir: %s has:" % str(rootDir));
    jpeg_counter = 0;
    jpg_counter = 0;
    png_counter = 0;
    gif_counter = 0;
    avi_counter = 0;
    mpg_counter = 0;
    mpeg_counter = 0;
    gp_counter= 0;
    mp4_counter = 0;
    mod_counter = 0;
    counters = {".jpeg": jpeg_counter, 
        ".jpg": jpg_counter,
        ".png": png_counter,
        ".gif": gif_counter,
        ".avi": avi_counter,
        ".mpg": mpg_counter,
        ".mpeg": mpeg_counter,
        ".3gp": gp_counter,
        ".mp4": mp4_counter,
        ".mod":mod_counter
    }
    totalCounter = 0;
    for root, dirs, files in os.walk(rootDir, topdown='true'):
        for filename in files:
            ext = os.path.splitext(filename)[-1].lower();
            if(ext in counters):
                counter = counters[ext];
                counter+=1;
                counters[ext]= counter;
                totalCounter += 1;
    for k, v in sorted(counters.items()):
        print("Number of %s files = %i" % (k, v));
    return totalCounter;
        
def check_dir_empty(checkdir):
    logging.info(">>check_dir_empty " + checkdir)
    filesLeftOver = [];
    for root, dir, files in os.walk(checkdir, topdown='true'):
        for filename in files:
             filesLeftOver.append("Root=%s ,dir=%s, filename=%s" % (root, dir, filename));
              
    if (len(filesLeftOver) > 0):
        logging.info ("nastemp not empty " + pformat(filesLeftOver))
        raise Exception("nastemp dir not empty!!!  Please clear it out before running script");
    else:
        logging.info("nastemp dir empty")
    
    
if __name__ == '__main__':    
    main();