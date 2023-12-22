import cv2 as cv


def drawVerticalLines(src, verticalLines):
    for line in verticalLines:
        cv.line(src, (line[0], line[1]),
                (line[2], line[3]), (255, 100, 0), 2, cv.LINE_AA)


def drawSiks(src, sikList):
    for sik in sikList:
        cv.rectangle(src, (sik["x0"], sik["y0"]),
                     (sik["x1"], sik["y1"]), (0, 255, 0), 3)


def drawQnums(src, qNUmList):
    for qNum in qNUmList:
        cv.rectangle(src, (qNum["x0"], qNum["y0"]),
                     (qNum["x1"], qNum["y1"]), (0, 0, 255), 3)


def drawQKoku(src, x0, y0, x1, y1):
    cv.rectangle(src, (x0, y0),
                 (x1, y1), (255, 0, 0), 3)


def drawAnswerText(src, x0, y0, x1, y1):
    cv.rectangle(src, (x0, y0),
                 (x1, y1), (150, 150, 150), 2)


def drawResponseList(src, corrdinateList):
    drawQnums(src, [questionObj["qNumTextAttr"]
                    for questionObj in corrdinateList])
    for leftCoor in corrdinateList:
        soruKokuCoor = leftCoor["soruKokuCoordinates"]
        drawQKoku(
            src, soruKokuCoor["x0"], soruKokuCoor["y0"], soruKokuCoor["x1"], soruKokuCoor["y1"])
        drawSiks(src, [
            answerObj["answerText"] for answerObj in leftCoor["answersCoordinatesList"]])
        for cordObj in leftCoor["answersCoordinatesList"]:
            drawAnswerText(src, cordObj["x0"],
                           cordObj["y0"], cordObj["x1"], cordObj["y1"])
