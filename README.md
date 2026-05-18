# DP-Web-Cam-Recorder
Free web-cam recorder app. An experiment in the use of AI in coding.

I am an engineer and have been in the automotive engineering industry for over 40 years, my background is in electronic engineering (Loughborough University, UK, many moons ago!).
My main area of expertise is in automation and the use of industrial PLC's. I have seen the development of the modern day pc from its early days of the 8086 and original IBM XT models to what it is now.
I am conversant in many computer languages but do not ascribe to any one in particular, my knowledge is more on underlying programming concepts.
I am a trouble-shooter and would probably describe myself as more of a controls/systems engineer rather than en electronics engineer, my mode of operandus is to use the most appropriate tool, including programming languages, to effect a solution to the problem I am working on.

This project came about after a conversation with my sons, one a medical doctor and the other researching a Phd on mathematical proof theory (so you can imagine how high-brow this would have been), on how AI is developing and the practical uses of the various engines available (applications that are not just directed at the social media genre).
In my opinion the biggest leap and of most practical impact is in the field of medicine. Let's hope AI can help us to eliminate cancer, parkinsons, dementia,.... the list is long.

One of the things discussed during our conversation was that the next step in software development would be where you would just ask the AI to give you a routine to slot in to your program.
This got me thinking on how far this could be taken with todays AI.

A friend of mine had commented once on how useless he found the MS offerings for a web-cam and how the other offerings on the internet were either not suitable or functional and described them as either 'crapware' or 'bloatware'.
Instead of jumping straight in and writing an application with my programming knowledge. I decided to try and write an application using AI exclusively to do the coding.

For my experiment I decided to use ChatGPT.

I asked what programming language would be best suited to create a self contained single .exe program to preview and capture my laptops built-in camera.
There were some suggestions including the use of C#, .NET, and Python. All involved using some external libraries for video encoding.
I wanted to use all free tools and freely available libraries to make this project accessible to everyone. The best option was Python.
After installing Python I was not too impressed with the IDLE editor, also lacking was an IDE that would help make the design of a GUI easier.
A bit of searching and trying out some solutions I opted to use GuiPy as my IDE, it has a plethora of features, the most useful of which are the code checker and the ability to design a GUI much like using MS Visual Studio. I highly recommend it (https://guipy.de/doku.php?id=start).

I started off with a basic concept of what it should look like using GuiPy's GUI editor sticking to TTK controls.
I then copied and fed the whole script into ChatGPT and asked it to help me program a preview window within the bounds of the frame I had created.
This was followed by other questions on coding the buttons creating overlays, etc.
I followed guidelines on installing extra libraries or packages, namely 'Pillow', 'OpenCV-python', and 'FFMpeg' (only FFMpeg.exe is required, https://ffmpeg.org/)
At each stage I tested by running the script, and every fault or issue was fed back into ChatGPT to give a solution.
I also looked at some of the suggested features recommended by ChatGPT and asked to have them included.

I ended up with a web-cam recorder that has the following features:
  - ✔ Live webcam preview
  - ✔ H.264 recording
  - ✔ Multi-camera support
  - ✔ Timestamp overlay
  - ✔ Blinking REC indicator
  - ✔ Automatic file splitting
  - ✔ Quality presets
  - ✔ Open save folder button
  - ✔ Standalone EXE support

ChatGPT instructed me on the use of Pyinstaller to create a single .exe files that would include all necessary modules (see Make.bat for the automated Pyinstaller command).

Other than using GuiPy and editing, copying and pasting, at no point did I do any coding.
I learned that to improve ChatGPT responses you must give as much information as possible, but you must also be very specific when asking for what you want.

The experiment was a success. I've included the .py script that you can study and use (under the GPL
