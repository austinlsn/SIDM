"""Module to define miscellaneous helper methods"""

import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep


def print_list(l):
    """Print one list element per line"""
    print('\n'.join(l))

def print_debug(name, val, print_mode=True):
    """Print variable name and value"""
    if print_mode:
        print(f"{name}: {val}")

def partition_list(l, condition):
    """Given a single list, return separate lists of elements that pass or fail a condition"""
    passes = []
    fails = []
    for x in l:
        if condition(x):
            passes.append(x)
        else:
            fails.append(x)
    return passes, fails

def flatten(x):
    """Flatten arbitrarily nested list or dict"""
    # https://stackoverflow.com/questions/2158395/
    flattened_list = []
    def loop(sublist):
        if isinstance(sublist, dict):
            sublist = sublist.values()
        for item in sublist:
            if isinstance(item, (dict, list)):
                loop(item)
            else:
                flattened_list.append(item)
    loop(x)
    return flattened_list

def add_unique_and_flatten(flattened_list, x):
    """Flatten arbitrarily nested list or dict, keeping only unique items"""
    # https://stackoverflow.com/questions/2158395/
    def loop(sublist):
        if isinstance(sublist, dict):
            sublist = sublist.values()
        for item in sublist:
            if isinstance(item, (dict, list)):
                loop(item)
            elif item not in flattened_list:
                flattened_list.append(item)
    loop(x)
    return flattened_list

def dR(obj1, obj2):
    """Return dR between obj1 and the nearest obj2"""
    return obj1.nearest(obj2, return_metric=True)[1]


# def genmatch(obj1, obj2, iterations):
#     remaining_obj2 = obj2
#     for i in range(iterations):
#         matched_obj2[i] = obj1.nearest(obj2)
#         remaining_obj2.remove()
#         matched_obj1[i] = obj1
        
    
    
# genmatch function requires dR function above it. 'threshold' is maximum dR for matching
# this matches on first-come-first-serve basis, rather than checking which dR is absolute smallest and matching those
def genmatch(objs1, objs2, threshold):
    remaining_objs1 = objs1
    remaining_objs2 = objs2
    matched_objs1 = []
    matched_objs2 = []
    
    

    while len(remaining_objs1) > 0:
        neighbor_objs2, r = remaining_objs1.nearest(remaining_objs2, return_metric=True)
        for i in range(len(neighbor_objs2)):
            print(neighbor_objs2[i])
            print(r[i])
            if np.all(r[i]) < threshold:
                if neighbor_objs2[i] not in matched_objs2: 
                    matched_objs1.append(objs1[i])
                    matched_objs2.append(neighbor_objs2[i])
                    remaining_objs1.remove(objs1[i])
                    remaining_objs2.remove(neighbor_objs2[i])
                else: # if match is a duplicate, re-calculate nearest() using remaining objects
                    break
            else: # if r from nearest() doesn't meet threshold, remove those objects entirely
                remaining_objs1.remove(objs1[i])
                remaining_objs2.remove(neighbor_objs2[i])    
    """
    for _, obj1 in enumerate(objs1):
        Mobj2, r = obj1[1].nearest(remaining_objs2, axis=None, return_metric=True)
        # obj1[1] is obj1 definition (as opposed to obj1 name). Allows for broadcasting (cartesian product::scalar*array)
        M2 = np.argmin(r)
        if Mobj2[M2] not in matched_obj2: 
            matched_obj2.append(Mobj2[M2])

        if r < threshold:
            matched_objs2.append(Mobj2)
            matched_objs1.append(obj1)
            remaining_objs2.remove(Mobj2) # remove matched object so it isn't matched twice
    """
    """
    temp_objs2, minRs = objs1.nearest(objs2, return_metric=True)
    
    for M2, r in enumerate(minRs):
        if r < threshold: 
            if temp_objs2[M2] not in matched_objs2:
                matched_objs1.append(objs1[M2])
                matched_objs2.append(temp_objs2[M2])

            
    matched_objs2 = set(matched_objs2) # 'set()' removes duplicates
    
    print(temp_objs2)
    """   
    """Return lists of obj1s which have matches, and matched obj2s"""
    return matched_objs1, matched_objs2

def lxy(obj):
    """Return transverse distance between production and decay vertices"""
    return (obj.dauvtx - obj.vtx).r

def set_plot_style(style='cms', dpi=50):
    """Set plotting style using mplhep"""
    if style == 'cms':
        plt.style.use(hep.style.CMS)
    else:
        raise NotImplementedError
    plt.rcParams['figure.dpi'] = dpi

def plot(hists, skip_label=False, **kwargs):
    """Plot using hep.hist(2d)plot and add cms labels"""
    dim = len(hists[0].axes) if isinstance(hists, list) else len(hists.axes)
    if dim == 1:
        h = hep.histplot(hists, **kwargs)
    elif dim == 2:
        h = hep.hist2dplot(hists, **kwargs)
    else:
        raise NotImplementedError(f"Cannot plot {dim}-dimensional hist")
    if not skip_label:
        hep.cms.label()
    return h

def load_yaml(cfg):
    """Load yaml files and return corresponding dict"""
    cwd = os.path.dirname(os.path.abspath(__file__))
    with open(f"{cwd}/{cfg}", encoding="utf8") as yaml_cfg:
        return yaml.safe_load(yaml_cfg)

def make_fileset(samples, ntuple_version, location_cfg="../configs/ntuple_locations.yaml"):
    """Make fileset to pass to processor.runner"""
    if ntuple_version != "ffntuple_v4":
        raise NotImplementedError("Only ffntuple_v4 ntuples have been implemented")
    locations = load_yaml(location_cfg)[ntuple_version]
    fileset = {}
    for sample in samples:
        base_path = locations["path"] + locations["samples"][sample]["path"]
        file_list = [base_path + f for f in locations["samples"][sample]["files"]]
        fileset[sample] = file_list
    return fileset

def check_bit(array, bit_num):
    """Return boolean stored in the bit_numth bit of array"""
    return (array & pow(2, bit_num)) > 0

def get_hist_mean(hist):
    """Return mean of 1D histogram"""
    return np.atleast_1d(hist.profile(axis=0).view())[0].value
