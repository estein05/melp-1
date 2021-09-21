# import modules
import melp
import multiprocessing as mp
import subprocess
from glob import glob
from functools import partial
import numpy as np


#defining the functions with multithreading support
def mt_tileHitRateHID(input_files, output_files, npz, i):
    calls = melp.TileHitRate(input_files[0][i], output_files[i], output_files[i]+"edep")
    print("read file ", i+1)
    print("started thread ", i+1)
    calls.tileHitRateHID()
    if npz == True:
        calls.saveNpz()


def mt_hitAngleTID(input_files, output_files, txt, npz, binned, angle, i):
    calls = melp.TileHitAngle(input_files[0][i], output_files[i])
    print("read file ", i+1)
    print("started thread ", i+1)
    calls.hitAngleTID(angle=angle)
    if txt == True:
        calls.saveTxt()
    if npz == True:
        calls.saveNpz()
    if binned == True:
        calls.saveBinned()


def mt_hitAngleHelix(input_files, output_files, txt, npz, binned, i):
    calls = melp.TileHitAngle(input_files[0][i], output_files[i])
    print("read file ", i+1)
    print("started thread ", i+1)
    calls.hitAngleHelix()
    if txt == True:
        calls.saveTxt()
    if npz == True:
        calls.saveNpz()
    if binned == True:
        calls.saveBinned()



def run_mt(function_str, src, args): 
#function_str: pass function as str, src: directory of root files to analyse, args: arguments for parallelized function
    # set used threads
    unused_threads = 2 #set the number of threads you don't want to use
    print("-----------------------")
    print("Available threads = ",mp.cpu_count())
    print("Used threads = ",mp.cpu_count() - unused_threads)
    print("-----------------------")

    input_files = []
    output_files = []


    # get list of input files
    input_files.append(glob(src)) 

    # generate list of output files
    for j in range(len(input_files[0])):
        output_files.append("out"+str(j+1))


    # map multiprocessing pool
    pool = mp.Pool(mp.cpu_count() - unused_threads)
    if function_str == "mt_tileHitRateHID":
        func = partial(mt_tileHitRateHID, input_files, output_files, args)
        pool.map(func, [i for i in range(len(input_files[0]))])
        pool.close()

    elif function_str == "mt_hitAngleTID":
        func = partial(mt_hitAngleTID, input_files, output_files, *args)
        pool.map(func, [i for i in range(len(input_files[0]))])
        pool.close()

    elif function_str == "mt_hitAngleHelix":
        func = partial(mt_hitAngleHelix, input_files, output_files, *args)
        pool.map(func, [i for i in range(len(input_files[0]))])
        pool.close()
