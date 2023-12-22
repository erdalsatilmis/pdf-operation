import pytesseract as pyts
import cv2 as cv
import pandas as pd
import numpy as np
from PreProcesses import get_grayscale, thresholding
from findOperations import clearDataFrame, findVerticalLines, getSoruKokuAndAnswerTextsCoordinates, rightLeftDetect
from drawings import drawResponseList, drawVerticalLines


def getData(defaultImg):
    height, width, channels = defaultImg.shape
    gray = get_grayscale(defaultImg)
    thresh = thresholding(gray)
    verticalLines = findVerticalLines(defaultImg, width, height)
    drawVerticalLines(gray, verticalLines)

    df = pyts.image_to_data(gray, output_type=pyts.Output.DICT,
                            lang="eng", config="--psm 6")
    dataFrame = pd.DataFrame(data=df)

    pageResponse = {
        "height": height,
        "width": width,
        "questionList": None
    }
    # sayfada dikey çizgi varsa
    if(len(verticalLines) != 0):
        if((verticalLines[0][1]-verticalLines[0][3] > height*0.7)):
            # print("long vertical line")
            # sayfa buyuk bir cizgiyle ikiye ayrılma durumu
            # sayfayı sol ve sag olarak iki parçaya bölüp
            # kelimeleri sag ve sol olarak iki parcada okuma
            leftTextsDf, rightTextsDf = rightLeftDetect(dataFrame, width)
            # left side
            leftCoordinatesList = getSoruKokuAndAnswerTextsCoordinates(
                leftTextsDf, width)
            # drawResponseList(defaultImg, leftCoordinatesList)
            # right side
            rightCoordinatesList = getSoruKokuAndAnswerTextsCoordinates(
                rightTextsDf, width)
            # drawResponseList(defaultImg, rightCoordinatesList)
            pageResponse["questionList"] = leftCoordinatesList + \
                rightCoordinatesList
        else:
            # print("short vertical line")
            lineY0 = verticalLines[0][3]
            lineY1 = verticalLines[0][1]
            cleanedTextDf = clearDataFrame(dataFrame, width)

            leftRightSideDf = cleanedTextDf[(
                cleanedTextDf["top"] > lineY0-10) & (cleanedTextDf["top"] < lineY1+10)]

            restOfPageDf = cleanedTextDf[(cleanedTextDf["top"] < lineY0-10) |
                                         (cleanedTextDf["top"] > lineY1+10)]

            leftTextsDf, rightTextsDf = rightLeftDetect(leftRightSideDf, width)

            leftCoordinatesList = getSoruKokuAndAnswerTextsCoordinates(
                leftTextsDf, width)
            # drawResponseList(defaultImg, leftCoordinatesList)

            rightCoordinatesList = getSoruKokuAndAnswerTextsCoordinates(
                rightTextsDf, width)
            # drawResponseList(defaultImg, rightCoordinatesList)

            restOfPageCoordinates = getSoruKokuAndAnswerTextsCoordinates(
                restOfPageDf, width)
            # drawResponseList(defaultImg, restOfPageCoordinates)
            pageResponse["questionList"] = leftCoordinatesList + \
                rightCoordinatesList + restOfPageCoordinates
    else:
        # sayfada dikey çizgi yoksa
        # tek soru veya sayfanın enine yayılmıs coklu soruların oldugu durum
        cleanedTextDf = clearDataFrame(dataFrame, width)
        coordinatesList = getSoruKokuAndAnswerTextsCoordinates(
            cleanedTextDf, width)
        # drawResponseList(defaultImg, coordinatesList)
        pageResponse["questionList"] = coordinatesList

    # cv.imshow("defaultImg", defaultImg)
    # cv.imshow("gray", gray)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return pageResponse
