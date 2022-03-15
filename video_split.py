# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 12:34:45 2020

@author: gweiss01
"""

import sys
import numpy as np
import pandas as pd
import cv2
import os
import pdb

import tkinter
from tkinter.filedialog import askdirectory,askopenfilename
from tkinter.simpledialog import askstring

#tkinter.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

global prevRightROI
global prevLeftROI

def getVideo(vidPath):
     # show an "Open" dialog box and return the path to the selected file
    global prevRightROI
    global prevLeftROI
    vid_name = os.path.splitext(os.path.basename(vidPath))[0]
    print(vidPath)
    cap = cv2.VideoCapture(vidPath)
    cap.set(cv2.CAP_PROP_POS_FRAMES,1800)
    ret, frame = cap.read()
    leftFromFile = rightFromFile =""
    try:
        leftFromFile,rightFromFile = os.path.basename(vidPath).split("_")
        rightFromFile=rightFromFile[:-4]
    except: pass
    cv2.rectangle(frame,(int(prevLeftROI[0]),int(prevLeftROI[1])),(int(prevLeftROI[0]+prevLeftROI[2]),int(prevLeftROI[1]+prevLeftROI[3])),color=(255,200,200),thickness=2)
    leftROI = list(cv2.selectROI("Select Left Mouse, then Press ENTER"+vid_name,frame))
    # leftROI[3]=leftROI[2] make the roi square
    if leftROI==[0,0,0,0]: leftROI = prevLeftROI
    else: prevLeftROI = leftROI
    cv2.rectangle(frame,(int(prevLeftROI[0]),int(prevLeftROI[1])),(int(prevLeftROI[0]+prevLeftROI[2]),int(prevLeftROI[1]+prevLeftROI[3])),color=(255,200,200),thickness=2)
    cv2.imshow("Currently Selected Left ROI",frame)
    leftMouse = askstring("Enter Mouse ID's (Cancel for Prev Vid)","Left Mouse",initialvalue=leftFromFile)
    if leftMouse == None:
        cv2.destroyWindow("Select Left Mouse, then Press ENTER"+vid_name)
        return pd.Series([])
    cv2.rectangle(frame,(int(prevRightROI[0]),int(prevRightROI[1])),(int(prevRightROI[0]+prevRightROI[2]),int(prevRightROI[1]+prevRightROI[3])),color=(255,200,200),thickness=2)    
    rightROI = list(cv2.selectROI("Select Right Mouse, then Press ENTER"+vid_name,frame))
    # rightROI[3]=rightROI[2] makes the roi square
    if rightROI==[0,0,0,0]: rightROI = prevRightROI
    else: prevRightROI = rightROI
    cv2.rectangle(frame,(int(prevRightROI[0]),int(prevRightROI[1])),(int(prevRightROI[0]+prevRightROI[2]),int(prevRightROI[1]+prevRightROI[3])),color=(255,200,200),thickness=2)
    cv2.imshow("Currently Selected Right ROI",frame)
    rightMouse = askstring("Enter Mouse ID's (Cancel for Prev Vid)","Right Mouse",initialvalue=rightFromFile)
    if rightMouse == None:
        cv2.destroyWindow("Select Right Mouse, then Press ENTER"+vid_name)
        return pd.Series([])
#    leftROI[2] = leftROI[3] = rightROI[2] = rightROI[3] = max([leftROI[2],leftROI[3],rightROI[2],rightROI[3]])
    vidPath = pd.DataFrame({'path':[vidPath],'leftID':[leftMouse],'rightID':[rightMouse], 'leftROI':[leftROI], 'rightROI':[rightROI]})
    # When everything done, release the video capture object
    cap.release()
    # Closes all the frames
    cv2.destroyAllWindows()
    return vidPath







# #single file input
# file_path = askopenfilename()
# currentVideo = getVideo(file_path)
# vidPaths = vidPaths.append(currentVideo)
# folderName=os.path.dirname(file_path)


def cropVideo(vidPath):
    path=vidPath['path'][0]
    folderName=os.path.dirname(path)
    leftROI = vidPath['leftROI'][0]
    if leftROI[2] > leftROI[3]:
        leftDim = (300,int(300*(leftROI[3]/leftROI[2])))
    else:
        leftDim = (int(300*(leftROI[2]/leftROI[3])),300)
    rightROI = vidPath['rightROI'][0]
    if rightROI[2] > rightROI[3]:
        rightDim = (300,int(300*(rightROI[3]/rightROI[2])))
    else:
        rightDim = (int(300*(rightROI[2]/rightROI[3])),300)
    cap = cv2.VideoCapture(path)
    codec = cv2.VideoWriter_fourcc('X','V','I','D')
    fps = cap.get(cv2.CAP_PROP_FPS)
    ret, frame = cap.read() #advance and read frame

    leftOut = cv2.VideoWriter(folderName+r'/split_videos/'+vidPath['leftID'][0]+'.MP4',codec, fps, leftDim)
    rightOut = cv2.VideoWriter(folderName+r'/split_videos/'+vidPath['rightID'][0]+'.MP4',codec, fps,rightDim)
    
    
    
    for j in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1)):
        ret, frame = cap.read() #advance and read frame
        
        if ret:
            leftCropped = frame[int(leftROI[1]):int(leftROI[1]+leftROI[3]), int(leftROI[0]):int(leftROI[0]+leftROI[2])]
     
            rightCropped =frame[int(rightROI[1]):int(rightROI[1]+rightROI[3]), int(rightROI[0]):int(rightROI[0]+rightROI[2])]

            leftResized = cv2.resize(leftCropped, leftDim, interpolation = cv2.INTER_AREA)
            rightResized = cv2.resize(rightCropped, rightDim, interpolation = cv2.INTER_AREA)
            
            leftOut.write(leftResized)
            
            rightOut.write(rightResized)

        
        print("Video " + vidPath['leftID'][0],int(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1) - j)


    leftOut.release()
    rightOut.release()


import multiprocessing
from multiprocessing import Pool
#batch folder input
if __name__ == '__main__':
    folderName = askdirectory()
    fileList = [file for file in os.listdir(folderName) if file.endswith(('.MPG','.MP4'))]
    i=0
    vidPaths = pd.DataFrame(columns=['path','leftID','rightID','folderName'])
    prevRightROI = [0,0,0,0]
    prevLeftROI = [0,0,0,0]
    try:
        os.mkdir(folderName+r'/split_videos/')
    except:
        pass

    #loops through the files asking for rois
    while i < len(fileList):
        fileName=fileList[i]
        currentVideo = getVideo(folderName+r"/"+fileName)
        if currentVideo.empty:
            i-=1
            if i < 0: i=0
        else:
            vidPaths = vidPaths.append(currentVideo)
            i+=1
#This is for non-multithreaded testing
    # for i in range(len(vidPaths['path'])):
    #     cropVideo(vidPaths.iloc[[i]])
    
    
#This is for multithreading
    jobs = []
    print('processing....')
    for i in range(len(vidPaths['path'])):
        j=vidPaths.iloc[[i]]
        jobs.append(j)
    with Pool(5) as p:
        p.map(cropVideo, jobs)
    print("Done!")
        
    tkinter.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
