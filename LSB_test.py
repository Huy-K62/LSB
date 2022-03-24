from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
import os


#Algorithm LSB
class LSB():
    def __init__(self):
        #super().__init__()
        self.bitsPerChar = 8 #8 bits per 1 char
        self.bitsPerPixel = 3 #can hide 3 bits per pixel
        self.maxBitStuffing = 2
        self.path_file_encode = None
        self.path_file_decode = None
        self.path_save_result = None

    #when click button "Start Hide Data", thiss function will be called
    def start_encode(self):

        #If you do not select the file, you will receive an error
        if(self.path_file_encode == None):
            messagebox.showerror('Error', "File not selected")
        else:
            #Get user entered data to hide in image and notify when successful
            newImg = self.LSB_encode(ent_password.get("1.0",'end-1c'), self.path_file_encode, "result")
            messagebox.showinfo('Notification', "Successfully hidden password")

    #when click button "Show hidden password", this function will be called
    def start_decode(self):
        #If you do not select the file, you will receive an error
        if(self.path_file_decode == None):
            messagebox.showerror('Error', "File not selected")
        else:
            #notify when successful and show password
            message = self.LSB_decode(self.path_file_decode)
            messagebox.showinfo('Show Password', message)
    
    #when click button "Choose Image" of the interface with the option hide data, this function will be called
    #This function will get the file path the user chooses to use
    def choose_image(self):
        #Open the folder in the computer to select the file
        file = filedialog.askopenfilename()
        self.path_file_encode = file

        #show the file path in a box
        path_image.insert(END, self.path_file_encode)

    #when click button "Choose Image" of the interface with the option extract data, this function will be called
    #This function will get the file path the user chooses to use
    def choose_image_with_password_hidden(self):
        #Open the folder in the computer to select the file
        file = filedialog.askopenfilename()
        self.path_file_decode = file

        #show the file path in a box
        path_image_hidden.insert(END, self.path_file_decode)
    
    #when click button "Save Image" of the interface with the option hide data, this function will be called
    #This function will get the folder path the user chooses to use
    def save_image(self):
        #choose where to save image
        file = filedialog.askdirectory()
        self.path_save_result = file

        #show the folder path in a box
        path_saveimage.insert(END, self.path_save_result)

    #return true when the number of bits that can be hidden per pixel is greater than the number of bits of the cipher
    def canEncode(self, message, image):
        #Get image size
        width, height = image.size
        #Each pixel can hide 3 bits, imageCapacity = the number of bits that an image can hide
        imageCapacity = width * height * self.bitsPerPixel
        #1 character is made up of 8 bits
        messageCapacity = (len(message) * self.bitsPerChar) - (self.bitsPerChar + self.maxBitStuffing)
        return imageCapacity >= messageCapacity

    #
    def createBinaryTriplePairs(self, message):
        #convert each character in the message to decimal and then to binary
        #then add 8 bit 0 to the end of list
        binaries = list("".join([bin(ord(i))[2:].rjust(self.bitsPerChar,'0') for i in message]) 
        + "".join(['0'] * self.bitsPerChar))
        #add bit 0 to the end of list
        binaries = binaries + ['0'] * (len(binaries) % self.bitsPerPixel)

        #split the list with each element containing 3 consecutive bits
        binaries = [binaries[i*self.bitsPerPixel:i*self.bitsPerPixel+self.bitsPerPixel] 
        for i in range(0,int(len(binaries) / self.bitsPerPixel))]
        return binaries

    #embed every bit of the message into every pixel of the image
    def embedBitsToPixels(self, binaryTriplePairs, pixels):
        #traverse all pixels of an image, 1 pixel has 3 RBG values, 
        #convert each R, G, and B value to binary
        binaryPixels = [list(bin(p)[2:].rjust(self.bitsPerChar,'0') for p in pixel) for pixel in pixels]

        #
        for i in range(len(binaryTriplePairs)):
                for j in range(len(binaryTriplePairs[i])):
                        binaryPixels[i][j] = list(binaryPixels[i][j])
                        #Assign the last bit of each R G B value in the image to each element in the sublist returned from the createBinaryTriplePairs function
                        binaryPixels[i][j][-1] = binaryTriplePairs[i][j]
                        binaryPixels[i][j] = "".join(binaryPixels[i][j])

        #After the assignment is complete, 
        #we again convert the binary value of each R G B in each pixel of the image to decimal
        newPixels = [tuple(int(p,2) for p in pixel) for pixel in binaryPixels]
        return newPixels

    #Hide password in image
    def LSB_encode(self, message, path_File, newImageFilename):
        #Open image
        img = Image.open(open(path_File, 'rb'))
        #Get image size 
        size = img.size
        if not self.canEncode(message, img):
            return None

        binaryTriplePairs = self.createBinaryTriplePairs(message)

        pixels = list(img.getdata())
        newPixels = self.embedBitsToPixels(binaryTriplePairs, pixels)

        #create RGB image new
        newImg = Image.new("RGB", size)
        #Copies pixel data from newPixels to this image
        newImg.putdata(newPixels)

        #save new image to the selected folder 
        finalFilename = newImageFilename + str(".png")
        result_path = os.path.join(self.path_save_result, finalFilename)
        newImg.save(result_path)
        #cv2.imwrite(str(save_image()) + newImageFilename,newImg)
        return newImg

    def getLSBsFromPixels(self, binaryPixels):
        totalZeros = 0
        binList = []
        #Traverse each binary-converted R G B element of each pixel in the image, 
        #if the last bit of each R G B element is bit 0, 
        #we change it to 1, if it's equal to 1, we change it to 0
        for binaryPixel in binaryPixels:
                for p in binaryPixel:
                        if p[-1] == '0':
                                totalZeros = totalZeros + 1
                        else:
                                totalZeros = 0
                        binList.append(p[-1])
                        if totalZeros == self.bitsPerChar:
                                return  binList

    #Extract hidden data
    def LSB_decode(self,path_File):
        #open image
        img = Image.open(open(path_File, 'rb'))

        pixels = list(img.getdata())

        #traverse all pixels of an image, 1 pixel has 3 RBG values, 
        #convert each R, G, and B value to binary
        binaryPixels = [list(bin(p)[2:].rjust(self.bitsPerChar,'0') 
        for p in pixel) for pixel in pixels]
        binList = self.getLSBsFromPixels(binaryPixels)
        #Iterates from the first element to len(binList) minus the 8 extra 0's after the encoder at the top
        #Concatenate the bits and convert back to decimal value (int("".join(binList[i:i+self.bitsPerChar]),2)),
        #from decimal value to character by character by setting chr () to force style
        message = "".join([chr(int("".join(binList[i:i+self.bitsPerChar]),2)) 
        for i in range(0,len(binList)-self.bitsPerChar,self.bitsPerChar)])
        return message


#create an object of class LSB
object = LSB()
#create a window from Tkinter
window = Tk()
#Add a title to the window
window.title('Least Significant Bit')
#create another frame
extract_data = Frame(window)
#Set the size of the window with unmodifiable mode
window.geometry('700x300')
window.resizable(False, False)

#When the "Hide Data" button is clicked, hide the interface of option "Extract Data"
def change_to_hide_data(label, password, save, text_path_image, text_path_save, start, choose):
    extract_data.forget()
    label.pack()
    password.pack()
    choose.pack()
    text_path_image.pack()
    save.pack()
    text_path_save.pack()
    start.pack()
    choose.pack()

#When the "Extract" Data" button is clicked, hide the interface of option "Hide Data"
def change_to_extract_data(label, password, save, text_path_image, text_path_save, start, choose):
    extract_data.pack()
    label.forget()
    password.forget()
    save.forget()
    start.forget()
    choose.forget()
    text_path_image.forget() 
    text_path_save.forget()

var = IntVar()
#Create "Options" label on the interface
lbl1 = Label(window, text="Options", font=("Times New Roman", 13))
lbl1.pack(anchor = NW) #position of label (anchor = NW) - 

#Create radio button "btn_hide" to show data hiding interface, 
#call to function "change_to_hide_data" to expose the interface that implements data hiding 
#and hide the interface that performs cryptographic extraction
btn_hide = Radiobutton(window, text="Hide Data", variable=var, value=1, font=("Times New Roman", 13), 
command=lambda:change_to_hide_data(lbl,ent_password,btn_save_image,
path_image,path_saveimage,btn_start, btn_choose_image))
btn_hide.pack(anchor = W) #position of button "Hide Data"

#Create radio button "btn_extract" to show the interface that performs cryptographic extraction
btn_extract = Radiobutton(window, text="Extract Data", variable=var, value=2, font=("Times New Roman", 13), 
command=lambda:change_to_extract_data(lbl,ent_password,btn_save_image,
path_image,path_saveimage,btn_start, btn_choose_image))
btn_extract.pack(anchor = W )

#Create "Enter Password" label
lbl = Label(window, text="Enter Password", font=("Times New Roman", 13))
lbl.pack()

#Create a box to enter the password to hide in the photo
ent_password = Text(window, width = 60,height = 1.4, bd=3)
ent_password.pack()

#Create button choose image
btn_choose_image = Button(window, text="Choose Image",font=("Times New Roman", 13), 
command=object.choose_image)
btn_choose_image.pack()

#Create a box showing the selected image path
path_image = Text(window, width = 60, height = 1.4,  bd=3)
path_image.pack()

#Create a button to choose the path to save the image
btn_save_image = Button(window, text="Save Image", font=("Times New Roman", 13), 
command=object.save_image)
btn_save_image.pack()

#create a box showing the selected path
path_saveimage = Text(window, width = 60 ,height = 1.4,bd=3)
path_saveimage.pack()

#Create a button to choose the path to save the image with password hidden
btn_choose_image_with_password_hidden = Button(extract_data, text="Choose an image with a password", 
font=("Times New Roman", 13), command=object.choose_image_with_password_hidden)
btn_choose_image_with_password_hidden.pack()

#Create a box showing the selected image path
path_image_hidden = Text(extract_data, width = 60, height = 1.4,  bd=3)
path_image_hidden.pack()

#Create a button to show hidden password
btn_show_key = Button(extract_data, text="Show hidden password", font=("Times New Roman", 13), 
    command=object.start_decode)
btn_show_key.pack()

#Create a button to start using the LSB algorithm to hide the password into the image
btn_start = Button(window, text="Start Hide Data", font=("Times New Roman", 13), 
command=object.start_encode)
btn_start.pack()

window.mainloop()