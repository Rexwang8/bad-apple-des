import cv2
import os
import numpy

import DES_Image
import BitVector

import time
import mappings

import moviepy.editor as mp

SHORTCUTMAPPINGS = mappings.mappings


def main():
    #splitframes()
    #downscale()
    #ApplyEncryptionToFrame()
    #AssembleFramesIntoVideo()
    superimposevideosourceintooutput()
    pass
    
 
def superimposevideosourceintooutput():
    print(f"gathering video clips...")
    originalvideo = mp.VideoFileClip("basource.mp4")
    finalvideo = mp.VideoFileClip("audio_outputDES2.avi", target_resolution=(90, 120))
    
    print(f"setting video clips...")
    #we want the original video in the top left corner and the final video to take up the rest of the screen (whole screen)
    originalvideo = originalvideo.set_pos(("right","top"))
    originalvideo = originalvideo.resize(0.25)
    
    finalvideo = finalvideo.set_pos(("left","top"))
    finalvideo = finalvideo.resize(6)
    
    #we want to mute the original video
    originalvideo = originalvideo.volumex(0)
    
    #set both to start at the same time
    finalvideo = finalvideo.set_start(0)
    originalvideo = originalvideo.set_start(0)
    originalvideo = originalvideo.set_end(finalvideo.duration)
    
    
    print(f"combining video clips...")
    combined = mp.CompositeVideoClip([finalvideo, originalvideo])
    #save the video
    combined.write_videofile("finalvideo2.mp4")
    
    
    
     
    
    
def AssembleFramesIntoVideo():
    framesfolder = 'outputDES2'
    framesPaths = [img for img in os.listdir(framesfolder) if img.endswith(".jpg")]
    sortedFramePaths = sorted(framesPaths, key=lambda x: int(x.split('.')[0].split('frame')[1]))
    framecount = len(sortedFramePaths)
    
    #print(f"sortedFramePaths: {sortedFramePaths}")
    frames = list()
    
    for i in range(0, framecount):
        frames.append(cv2.imread(os.path.join(framesfolder, sortedFramePaths[i]), cv2.IMREAD_COLOR))
    
    #debug - write out all frames to the debug folder from the frames variable
    #delete and remake the debug folder if it already exists
    '''
    if os.path.exists('debug'):
        os.system('rmdir /s /q debug')
    os.mkdir('debug')
    
    for i in range(0, framecount):
        print(f"frame {i} / {len(frames)}")
        print(f"Type of frames[i]: {type(frames[i])}")
        newimg = frames[i]
        cv2.imwrite(f'debug/frame{i}.jpg',newimg)
    
    '''

    timeOFOVideo = 219

    
    fps = framecount / timeOFOVideo
    print(f"Target FPS: {fps}")
    
    outputvideoname = 'outputDES2.avi'
    width = 120
    height = 90
    
    video = cv2.VideoWriter(outputvideoname, 0, fps, (width, height))
    for image in frames:
        video.write(image)
        
        
    
    
    
        
    cv2.destroyAllWindows()
    video.release()
    
    #get audio from original video
    ovideoname = 'basource.mp4'
    if(not os.path.exists("audio.wav")):
        os.system(f"ffmpeg -i {ovideoname} -ab 192000 -vn audio.wav")
        time.sleep(3)
    
    #add audio to new video
    if(os.path.exists(f"audio_{outputvideoname}")):
        os.remove(f"audio_{outputvideoname}")
    os.system(f"ffmpeg -i {outputvideoname} -i audio.wav -c copy -map 0:v:0 -map 1:a:0 audio_{outputvideoname}")
    print("done")
    
    

def ApplyEncryptionToFrame():
    #consts
    WIDTH = 120
    HEIGHT = 90
    KEYINTEXT = 'badapple'
    FSTART = 6570
    FEND = FSTART + 2
    ESTIMATEDTIME = 7
    FLAG_TREATALLRBGASSAME = True
    
    shortcuts = 0
    nonshortcuts = dict()
    
    #start timer
    timestart = time.time()
    
    timeparse = 0
    startparse = time.time()
    timeparse_Conversion = 0
    startparse_Conversion = time.time()
    timeparse_append = 0
    startparse_append = time.time()
    timeencrypt = 0
    startencrypt = time.time()
    timewrite = 0
    startwrite = time.time()
    blocksCount = 0
    
    for framenum in range(FSTART, FEND):
        startparse = time.time()
        #get the first frame and print its dimensions
        f = cv2.imread(f'frames_2_120x90/frame{framenum}.jpg')

        #turn frame into a numpy array
        nparr = numpy.array(f)
    
        #each pixel should be represented by three ascii characters, print out in one string
        arrofdata = list()
        timeparse += (time.time() - startparse)
        startparse_Conversion = time.time()
        for i in range(0,HEIGHT):
            for j in range(0,WIDTH):
                
                r, g, b = convertPixel(nparr[i,j], FLAG_TREATALLRBGASSAME)
                
                if(FLAG_TREATALLRBGASSAME):
                    arrofdata.append(r)
                else:
                    arrofdata.append(r)
                    arrofdata.append(g)
                    arrofdata.append(b)
    
        timeparse_Conversion += (time.time() - startparse_Conversion)
        startparse_append = time.time()
        arrofnumbers = list()
        #for each number in the array, convert to ascii and print
        for i in range(0, len(arrofdata)):
            arrofnumbers.append(chr(arrofdata[i]))
    
        timeparse_append += (time.time() - startparse_append)
        startencrypt = time.time()
            
        key = DES_Image.permuteKey(KEYINTEXT)    
        round_keys = DES_Image.generate_round_keys( key )
        
        print(f"frame {framenum} / {FEND}")
        
        listofasciinumbers, shortcuts, nonshortcuts, blocksCount = desimg(arrofnumbers, round_keys, key, shortcuts, nonshortcuts, blocksCount)
        print(f"all shortcuts: {shortcuts} , all nonshortcuts {len(nonshortcuts)}")
        timeencrypt = (time.time() - startencrypt)
        startwrite = time.time()
    
        #take these numbers as (r,g,b) and set the pixels of the image to these values
        for i in range(0,HEIGHT):
            for j in range(0,WIDTH):
                if(FLAG_TREATALLRBGASSAME):
                    v = listofasciinumbers[(i * WIDTH + j)]
                    nparr[i,j,0] = v
                    nparr[i,j,1] = v
                    nparr[i,j,2] = v
                else:
                    nparr[i,j,0] = listofasciinumbers[(i * WIDTH + j)]
                    nparr[i,j,1] = listofasciinumbers[(i * WIDTH + j) + 1]
                    nparr[i,j,2] = listofasciinumbers[(i * WIDTH + j) + 2]
                
                #print(f"({i},{j}): {nparr[i,j,0]} {nparr[i,j,1]} {nparr[i,j,2]}")
                
        
            
        #convert numpy array back to image
        newimg = cv2.cvtColor(nparr, cv2.COLOR_BGR2RGB)
    
        #write to the outputDES folder
        cv2.imwrite(f'outputDES2/frame{framenum}.jpg', newimg)
        
        timewrite += (time.time() - startwrite)
    
    
    startwrite = time.time()
    
    #printed in ""(num) - "originalhashvalue: hashedvalue", ""format
    
    filetooutput = open("output.txt", "w")
    filetooutput.close()
    filetooutput = open("output.txt", "a")
    #get number of different non-shortcuts, floor divide by 5, multiply by 5
    numdiv5 = (len(nonshortcuts) // 5) * 5
    top10 = sorted(nonshortcuts.items(), key=lambda x: x[1], reverse=True)[:numdiv5]
    for i in range(0, len(top10), 5):
        originalhash1, finalhash1, num1 = top10[i][0], top10[i][1][1], top10[i][1][0]
        originalhash2, finalhash2, num2 = top10[i+1][0], top10[i+1][1][1], top10[i+1][1][0]
        originalhash3, finalhash3, num3 = top10[i+2][0], top10[i+2][1][1], top10[i+2][1][0]
        originalhash4, finalhash4, num4 = top10[i+3][0], top10[i+3][1][1], top10[i+3][1][0]
        originalhash5, finalhash5, num5 = top10[i+4][0], top10[i+4][1][1], top10[i+4][1][0]
        
        #print(f"{i+1}) {num1 + num2 + num3 + num4 + num5}  --  \"{originalhash1}\": \"{finalhash1}\", \"{originalhash2}\": \"{finalhash2}\", \"{originalhash3}\": \"{finalhash3}\", \"{originalhash4}\": \"{finalhash4}\", \"{originalhash5}\": \"{finalhash5}\",")
        filetooutput.write(f"\"{originalhash1}\": \"{finalhash1}\", \"{originalhash2}\": \"{finalhash2}\", \"{originalhash3}\": \"{finalhash3}\", \"{originalhash4}\": \"{finalhash4}\", \"{originalhash5}\": \"{finalhash5}\",\n")
    
    
    timewrite += (time.time() - startwrite)
    
    timeend = time.time()
    
    timeelasped = timeend - timestart
    numberofframes = FEND - FSTART
    esttime = numberofframes * ESTIMATEDTIME
    timeSave = esttime - timeelasped
    percentsave = (timeSave / esttime) * 100
    
    print(f"Size of mapping dictionary: {len(SHORTCUTMAPPINGS)}")
    print(f"From frame {FSTART} to frame {FEND}, {numberofframes} frames were processed")
    print(f"Number of shortcuts used: {shortcuts}, {shortcuts / (blocksCount) * 100}% of blocks")
    print(f"Time Elasped: {timeelasped:0.2f} seconds\nEstimated Time: {esttime} seconds\nTime Saved: {timeSave:0.2f} seconds\nPercent Saved: {percentsave:0.2f}%")
    breakdowntime = timeparse_Conversion + timeencrypt + timewrite + timeparse + timeparse_append
    print(f"Percent of time spent parsing (before conversion): {timeparse / breakdowntime * 100:0.2f}%")
    print(f"Percent of time spent parsing (conversion): {timeparse_Conversion / breakdowntime * 100:0.2f}%")
    print(f"Percent of time spent parsing (after conversion): {timeparse_append / breakdowntime * 100:0.2f}%")
    print(f"Percent of time spent encrypting: {timeencrypt / breakdowntime * 100:0.2f}%")
    print(f"Percent of time spent writing: {timewrite / breakdowntime * 100:0.2f}%")
    
    print("--------------------")
    print(f"Amount of non-shortcuts: {len(nonshortcuts)}")
    


def splitframes():
    vidcap = cv2.VideoCapture('NA - 【東方】Bad Apple!! ＰＶ【影絵】.mp4')
    success,image = vidcap.read()
    count = 0
    #make folder to store frames
    os.mkdir('frames_2')
    while success:
        cv2.imwrite("frames_2/frame%d.jpg" % count, image)     # save frame as JPEG file      
        success,image = vidcap.read()
        print('Read a new frame: ', success, count)
        count += 1
        
   
def downscale():
    framesfolder = 'frames_2/'
    newframesfolder = 'frames_2_120x90/'
    
    #open the folder, for each file in folder, downscale to 120x90, save to new folder
    count = 0
    os.mkdir(newframesfolder)
    for filename in os.listdir(framesfolder):
        img = cv2.imread(framesfolder + filename)
        img = cv2.resize(img, (120, 90))
        cv2.imwrite(newframesfolder + filename, img)
        count += 1
        print(f"Resized {count} frames") 
   
   
def desimg(data, rc, key, shortcuts = 0, nc=dict(), blocksCount = 0):
    asciichars = list()
    
    
    while (len(data) > 0):
        FLAG_SHORTCUT = True
        
        
        
        #set of the first 8 numbers in a text format
        block = BitVector.BitVector(textstring = data[0:8])
        if(len(block) < 64):
            block = block + BitVector.BitVector(size = 64 - len(block))
            
        data = data[8:]
        blocksCount += 1
        hexval = block.get_bitvector_in_hex()
        originalhexval = hexval
        
        #check if block is in the list of shortcuts
        if(SHORTCUTMAPPINGS.get(hexval) != None):
            hexval = SHORTCUTMAPPINGS[hexval]
            shortcuts += 1
        else:
            FLAG_SHORTCUT = False


        
        
        if(FLAG_SHORTCUT == False):
            #we will check if it is empty
            if(len(block) == 0):
                break
            elif (len(block) < 64):
                #padding
                block.pad_from_right(64 - len(block))
            
           
            for round in range(16):
                block = DES_Image.feistel_64bit(block, rc[round])
            
            block = block[32:] + block[:32]
         
            #get the encrypted text by taking hex values of each character
            hexval = block.get_bitvector_in_hex()
            #print(f"hexval: {hexval}, originalhexval: {originalhexval}")
            if(nc.get(originalhexval) == None):
                nc[originalhexval] = (1, hexval)
            else:
                nc[originalhexval] = (nc[originalhexval][0] + 1, hexval)


            
        #turn hex values into a list of binary numbers
        for i in range(0,len(hexval),2):
            asciichars.append(int(hexval[i:i+2], 16))
    return asciichars, shortcuts, nc, blocksCount
    
   
def convertPixel(pixel, flag_treat):
    if(flag_treat):
        v = pixel[0]
        if(v < 125):
            v = v - (v % 5)
        elif (v > 125):
            v = v + (5 - (v % 5))
                    
        #ensure not below 0 or above 255
        v = max(0, min(v, 255))
        return (v, v, v)
    else:
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        if(r < 125):
            r = r - (r % 5)
            g = g - (g % 5)
            b = b - (b % 5)
        elif (r > 125):
            r = r + (5 - (r % 5))
            g = g + (5 - (g % 5))
            b = b + (5 - (b % 5))
            
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))
        return (r, g, b)
    
if __name__ == '__main__':
    main()