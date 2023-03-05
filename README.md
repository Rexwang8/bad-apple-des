# Bad Apple!! But it's encrypted with DES

https://youtu.be/HV5g7U7V21s

![[Pasted image 20230305011436.png]]

DES_Image.py excluded from repo as it is a part of Purdue ECE 404 HW2, for academic integrity purposes.

---

### Key Statistics

Encryption - 64 bit DES
key - "badapple"
Code book size - 700k
Rough Code book optimization amount - 90-95%

---


I got the idea for this from this video https://youtu.be/g8CcqQPHNfo

Since I was taking ECE 404 during that semester, I remembered that DES functioned similarly to ECB with the blocks.

To process the video, I downloaded it, split it into 6572 frames and downscaled each one to be 120x90 pixels, to make it easier. This meant there were still 11000 pixels per frame. I interpreted each RGB pixel as one ascii value (from 0-255) and I set 8 to a block to fit the DES 64 bit block size. I set the key to "badapple" and also floored all RGB values to the nearest 5. I modified my HW2 DES_Image encryption with an additional dynamically generated codebook, totaling over 650k kvp entries at the end. (accumulates more entries as it goes). I was modifying my code as I went. At the start, it took over 15s per frame but at the end it was down to about 1s per frame on average. Once i had all the frames, I used moviepy to assemble it into a video and to superimpose the original video onto it. 

At the end, I has a surprisingly coherent video. I noticed that pure white and pure black mapped to a single consistent value but having even a little variance produced wildly different hex values. (see the 700k+ kvp mappings). With the code book, I was able to save a lot of time, roughly 90% of my compute time for that step, making encryption only take ~20% of the total compute. Adding all the steps and experimentation time, the project took me about 10 hours to finish. I'm happy with how it turned out and the time it took to accomplish it.

### Gallery

---


![[Pasted image 20230305005616.png]]

![[Pasted image 20230305005626.png]]

![[Pasted image 20230305005643.png]]

