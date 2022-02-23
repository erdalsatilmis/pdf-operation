from io import BytesIO
import os
import pdf2image
import base64


def pdfConvert(pdfByte):
    # poppler kurulması gerek.
    # https://github.com/oschwartz10612/poppler-windows/releases
    #current_directory = os.getcwd()
    #final_directory = os.path.join(current_directory, r'pdfOutput\sectionId1')
    # if not os.path.exists(final_directory):
    #    os.makedirs(final_directory)
    # output_folder=final_directory,
    pages = pdf2image.convert_from_bytes(
        pdfByte, fmt='jpeg', thread_count=20)
    responseData = []
    for pagePIL in pages:
        buff = BytesIO()
        pagePIL.save(buff, format="jpeg")
        img_str = buff.getvalue()
        responseData.append(img_str)

    return responseData
