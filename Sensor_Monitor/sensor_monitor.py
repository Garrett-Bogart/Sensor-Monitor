from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import re

parent_categories = {}
parent_names = []
distances_calculated = False

def find_first_order(word):
    first_order_categories = ["Clocks", "Temperatures", "Load", "Fans", "Controls", "Data", " Powers", " Voltages",
                              "Sensor Min Value Max"]
    for pattern in first_order_categories:
        result = re.search(pattern, word)
        if result != None:
            return True
    return False

def find_second_order(word):
    pattern_float = r"\d+\.\d*"  # looks for a floating point number
    pattern_MHz = r"\d+ MHz"  # looks for # MHz

    compiled_float = re.compile(pattern_float)
    compiled_MHz = re.compile(pattern_MHz)
    resultf = compiled_float.search(word)
    if resultf != None:
        return True
    resultM = compiled_MHz.search(word)
    if resultM != None:
        return True
    return False

def delete_file(created_files):
    file_name = created_files[0]
    try:
        os.remove(file_name)
        created_files.remove(file_name)
        print("deleted " + file_name)
    except:
        print("could not find or remove: " + file_name)

def find_parent_names(list_data):
    for i in range(len(list_data)):
        if find_first_order(list_data[i]) == False and find_second_order(list_data[i]) == False:  #parent scope
            parent_names.append([list_data[i],i+1])
            continue

def distance(data_len):
    #print("calculating distances")
    for i in range(len(parent_names)):
        if i+1 >= len(parent_names):
            parent_names[i].append(data_len -parent_names[i][1])
            #print(parent_names)
            return
        else:
            parent_names[i].append(parent_names[i+1][1]-parent_names[i][1])
    distances_calculated = True
    #print("distances calculated")

def add_first_order_to_parent_categories(list_data,data_len):
    #print("check if distances have been calculated")
    if distances_calculated == False:
        distance(data_len) #ex [['  DESKTOP-R981UNK', 1], ['  HP 1962', 1], ['  Intel Core i7-4700MQ', 24], ['  Generic Memory', 6], ['  TOSHIBA MQ01ABD100', 4]]
    #print("distances have been calculated")
    for parent in parent_names:
        #print("appending values from list_data")
        temp = []
        if parent[2] >1:
            start = parent[1]
            stop = parent[2]+start-1
            if parent[1]+parent[2] == len(list_data):
                stop = len(list_data)
            while start != stop:
                temp.append(list_data[start])
                start+=1
            parent_categories[parent[0]] = temp

    #print(parent_categories)

def scrape(list_data,file):
    #print("finding parent names")
    if not parent_names:
        find_parent_names(list_data)
    #print("finding first order categories")
    add_first_order_to_parent_categories(list_data,len(list_data))
    #print("printing pretty file")
    pretty_print(file)
    #print("finished scrape")

def pretty_print(file):
    for parent in parent_categories:
        temp = parent_categories[parent]
        file.write("\t"+str(parent)+"\n")
        for data in temp:
            temp2 = data.rsplit(" ")
            if len(temp2) <= 3:
                file.write("\t\t"+str(data)+"\n")
            else:
                file.write("\t\t\t"+str(data)+"\n")
    parent_categories.clear()

def start(file):
    try:
        temp = []
        local_time = time.localtime()
        total_seconds = 0
        file.write(str(local_time[3] % 12) + ":" + str(local_time[4]) + ":" + str(local_time[5]) + "\n")
        #print("wrote: " + str(local_time[3] % 12) + ":" + str(local_time[4]) + ":" + str(local_time[5]) + "\n")
        while total_seconds <= 55:
            driver.refresh()
            time.sleep(5)
            local_time = time.localtime()
            file.write(str(local_time[3] % 12) + ":" + str(local_time[4]) + ":" + str(local_time[5]) + "\n")
            #print("wrote: " + str(local_time[3] % 12) + ":" + str(local_time[4]) + ":" + str(local_time[5]) + "\n")
            element = driver.find_elements(By.TAG_NAME, "tr")
            for data in element:
                temp.append(data.text)
            scrape(temp,file)
            #print("done with scrape: "+str((total_seconds/5)+1))
            total_seconds += 5
    except:
        print("exception happened in start")

def main():
    file_count = 0
    created_files = []
    file_path = input("file path")
    while 1:
        #print(file_path)
        file = open(file_path+"\\data"+str(file_count)+".txt","w")
        created_files.append(file_path+"\\data"+str(file_count)+".txt")
        #print("data"+str(file_count)+".txt opened")
        file_count+=1
        start(file)
        file.close()
        if len(created_files) > 3:
            delete_file(created_files)
# instance of firefox driver
driver = webdriver.Firefox()
# go to the page
url = input("enter the url: ")
driver.get(url)
main()