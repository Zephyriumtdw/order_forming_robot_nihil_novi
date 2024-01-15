import cv2
from pyzbar import pyzbar

cam = cv2.VideoCapture(0)
'''while True:
	ret, image = cam.read()
	cv2.imshow('Imagetest',image)
	k = cv2.waitKey(1)
	if k != -1:
		break'''
ret, image = cam.read()
#cv2.imwrite('/home/hipster202009/Desktop/qr_screen/qr.jpg', image)
#cam.release()
#cv2.destroyAllWindows()

barcodes = pyzbar.decode(image)
for barcode in barcodes:
    barcodeData = barcode.data.decode("utf-8")
    barcodeType = barcode.type
    text = "{}".format(barcodeData)
    file = open('ttemp.txt', 'w+')
    file.write('start ')
    file.write(text)
    file.close()
    print (text)
