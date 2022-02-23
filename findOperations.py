import cv2 as cv
import numpy as np
from tempUtils import tempSiklarList, tempQNumList, aSiklarList, bSiklarList, cSiklarList, dSiklarList, eSiklarList
import pandas as pd
import math


def findVerticalLines(src, srcWidth, srcHeight):
    edges = cv.Canny(src, 0, 255, apertureSize=3)
    lines = cv.HoughLinesP(image=edges, rho=1, theta=np.pi/180, threshold=50,
                           lines=np.array([]), minLineLength=srcHeight*0.3, maxLineGap=50)
    a, b, c = lines.shape
    verticalLines = []
    for i in range(a):
        srcMidPoint = srcWidth/2
        line = lines[i][0]
        if((line[0] == line[2]) & (srcMidPoint-5 < line[0]) & (srcMidPoint+5 > line[0])):
            verticalLines.append(line)
    return verticalLines


def getQnumsAndSikList(df, srcWidth, isTwoSection):
    answersDf = df[df["text"].astype(str).str[:2].isin(tempSiklarList)].sort_values(
        by=['top'], ascending=True)
    answersDf["width"] = 26
    qNumsDf = df[(df["text"].isin(tempQNumList))].sort_values(
        by=['top'], ascending=True)
    # soru numaralarının ortalama positiolarını alıp
    # bu pozisyondan büyük olanları listeden çıkarma.
    # soru kalıbının içinde gördüü 1. 2. vb textleri soru olarak algılamaması için...
    qNumPositionMean = np.mean([qNumRow["left"]
                               for i, qNumRow in qNumsDf.iterrows()])
    print("qNumPositionMean ->", qNumPositionMean)
    if(not math.isnan(qNumPositionMean)):
        qNumsDf = qNumsDf[qNumsDf["left"] <= int(qNumPositionMean)+2]

    return answersDf, qNumsDf


def rightLeftDetect(df, srcwidth):
    leftTexts = df[(df["left"]+df["width"] < srcwidth/2-10) &
                   (df["text"] != "")]
    leftTexts["x1"] = leftTexts["left"]+leftTexts["width"]
    rightIgnore = srcwidth - (srcwidth*0.1)
    rightTexts = df[(df["left"] > srcwidth/2+10) &
                    (df["text"] != "") & (df["left"] < rightIgnore)]
    rightTexts["x1"] = rightTexts["left"]+rightTexts["width"]
    return leftTexts, rightTexts


def clearDataFrame(df, srcwidth):
    rightIgnore = srcwidth - (srcwidth*0.1)
    cleanedDf = df[(df["text"] != "") & (df["left"] < rightIgnore)]
    cleanedDf["x1"] = cleanedDf["left"]+cleanedDf["width"]
    return cleanedDf


def matchQnumsAndAnswers(QNumDf, SikDf):
    qNumAndAnswersList = []
    for i in range(len(QNumDf.index)):
        thisQSiks = None
        if(i+1 == len(QNumDf.index)):
            thisQSiks = SikDf[(
                SikDf["top"] > QNumDf.iloc[i]["top"])]
        else:
            thisQSiks = SikDf[(SikDf["top"] > QNumDf.iloc[i]["top"]) & (
                QNumDf.iloc[i+1]["top"] > SikDf["top"])]

        qSiksList = thisQSiks.to_dict(orient="records")
        qNumText = QNumDf.to_dict(orient="records")[i]
        qNumAndAnswersList.append({
            "qNumText": qNumText,
            "answersList": qSiksList
        })
    return qNumAndAnswersList


def getSoruKokuCoordinates(sideTextDf, questionAndAnswers):
    soruKokuTexts = sideTextDf[(sideTextDf["top"] > questionAndAnswers["qNumText"]["top"]) & (
        questionAndAnswers["answersList"][0]["top"] > sideTextDf["top"])]
    x0 = questionAndAnswers["qNumText"]["left"] + \
        questionAndAnswers["qNumText"]["width"]+20
    y0 = questionAndAnswers["qNumText"]["top"]-10
    y1 = questionAndAnswers["answersList"][0]["top"]-20
    x1 = soruKokuTexts[soruKokuTexts["x1"]
                       == soruKokuTexts["x1"].max()].head(1).x1.item()+10
    qNum = questionAndAnswers["qNumText"]

    return x0, y0, x1, y1


def getAnswerTextCoordinates2(questionAndAnswers, soruKokuCoordinates):
    # soruKokuCoordinates -> (x0, y0, x1, y1)
    answersLayout = getAnswersStructure(questionAndAnswers)
    funReturnList = []
    numOfAnswers = len(questionAndAnswers["answersList"])
    if(answersLayout == "VERTICAL"):
        print("VERTICAL detect")
        for answerIndex, currAns in enumerate(questionAndAnswers["answersList"]):
            if(answerIndex+1 == numOfAnswers):
                # son seçenekte buraya girer
                heightMean = np.mean([list["y1"]-list["y0"]
                                     for list in funReturnList])
                funReturnList.append({
                    "answerText": {
                        "x0": currAns["left"],
                        "x1": currAns["left"] + currAns["width"],
                        "y0": currAns["top"],
                        "y1": currAns["top"] + currAns["height"],
                        "text": currAns["text"]
                    },
                    "x0": currAns["left"]+currAns["width"]+5,
                    "y0": currAns["top"]-5,
                    "x1": soruKokuCoordinates[2],
                    "y1": currAns["top"] + int(heightMean)
                })
            else:
                # son secenek degilse
                nextAns = questionAndAnswers["answersList"][answerIndex+1]
                funReturnList.append({
                    "answerText": {
                        "x0": currAns["left"],
                        "x1": currAns["left"] + currAns["width"],
                        "y0": currAns["top"],
                        "y1": currAns["top"] + currAns["height"],
                        "text": currAns["text"]
                    },
                    "x0": currAns["left"]+currAns["width"]+5,
                    "y0": currAns["top"]-5,
                    "x1": soruKokuCoordinates[2],
                    "y1": nextAns["top"]-10
                })
    elif(answersLayout == "HORIZONTAL_TABLE"):
        print("HORIZONTAL_TABLE detect")
        minLeftOfAnswers = min(answer["left"]
                               for answer in questionAndAnswers["answersList"])
        maxLeftOfAnswers = max(answer["left"]
                               for answer in questionAndAnswers["answersList"])

        answersMidPoint = minLeftOfAnswers + ((
            maxLeftOfAnswers - minLeftOfAnswers)/2)
        leftSideList = []
        rightSideList = []
        for answerIndex, currAns in enumerate(questionAndAnswers["answersList"]):
            if(answerIndex != 4):
                if(currAns["left"] < answersMidPoint):
                    # print("sol taraf")
                    leftSideList.append(currAns)
                elif(currAns["left"] > answersMidPoint):
                    # print("sag taraf")
                    rightSideList.append(currAns)
            else:
                # E) seçeneği varsa(özel koşul)
                rightSideList.append(currAns)

        for leftAnsIdx, leftAnswer in enumerate(leftSideList):
            # print("leftAnswer ->", leftAnswer)
            if(leftAnsIdx < len(rightSideList)):
                rightAnswer = rightSideList[leftAnsIdx]
                funReturnList.append({
                    "answerText": {
                        "x0": leftAnswer["left"],
                        "x1": leftAnswer["left"] + leftAnswer["width"],
                        "y0": leftAnswer["top"],
                        "y1": leftAnswer["top"] + leftAnswer["height"],
                        "text": leftAnswer["text"]
                    },
                    "x0": leftAnswer["left"]+leftAnswer["width"]+5,
                    "y0": leftAnswer["top"]-5,
                    "x1": rightSideList[leftAnsIdx]["left"]-5,
                    "y1": leftAnswer["top"] + leftAnswer["height"]+5
                })
                funReturnList.append({
                    "answerText": {
                        "x0": rightAnswer["left"],
                        "x1": rightAnswer["left"] + rightAnswer["width"],
                        "y0": rightAnswer["top"],
                        "y1": rightAnswer["top"] + rightAnswer["height"],
                        "text": rightAnswer["text"]
                    },
                    "x0": rightAnswer["left"]+rightAnswer["width"]+5,
                    "y0": rightAnswer["top"]-5,
                    "x1": soruKokuCoordinates[2],
                    "y1": leftAnswer["top"] + rightAnswer["height"]+5
                })
    elif(answersLayout == "ONE_LINE_HORIZONTAL"):
        print("ONE_LINE_HORIZONTAL ->")
        for answerIndex, currAns in enumerate(questionAndAnswers["answersList"]):
            if(answerIndex+1 != numOfAnswers):
                nextAns = questionAndAnswers["answersList"][answerIndex+1]
                funReturnList.append({
                    "answerText": {
                        "x0": currAns["left"],
                        "x1": currAns["left"] + currAns["width"],
                        "y0": currAns["top"],
                        "y1": currAns["top"] + currAns["height"],
                        "text": currAns["text"]
                    },
                    "x0": currAns["left"]+currAns["width"]+5,
                    "y0": currAns["top"]-5,
                    "x1": nextAns["left"],
                    "y1": nextAns["top"] + nextAns["height"]
                })
            else:
                funReturnList.append({
                    "answerText": {
                        "x0": currAns["left"],
                        "x1": currAns["left"] + currAns["width"],
                        "y0": currAns["top"],
                        "y1": currAns["top"] + currAns["height"],
                        "text": currAns["text"]
                    },
                    "x0": currAns["left"]+currAns["width"]+5,
                    "y0": currAns["top"]-5,
                    "x1": soruKokuCoordinates[2],
                    "y1": currAns["top"] + currAns["height"]+5
                })
    return funReturnList


def getAnswersStructure(questionAndAnswers):
    first = questionAndAnswers["answersList"][0]
    last = questionAndAnswers["answersList"][-1]
    firstx0 = first["left"]
    firsty0 = first["top"]
    lastx1 = last["left"] + last["width"]
    lasty1 = last["top"] + last["height"]
    boxWidth = lastx1 - firstx0
    boxHeight = lasty1 - firsty0

    if(boxWidth >= boxHeight):
        if(boxHeight > 30):
            return "HORIZONTAL_TABLE"
        elif(boxHeight <= 30):
            return "ONE_LINE_HORIZONTAL"
    else:
        return "VERTICAL"


def getSoruKokuAndAnswerTextsCoordinates(textsDf, srcWidth):
    funResList = []
    answerDf, QNumDf = getQnumsAndSikList(
        textsDf, srcWidth, isTwoSection=True)
    QNumAndAnswersList = matchQnumsAndAnswers(QNumDf, answerDf)
    for QuestionAndAnswers in QNumAndAnswersList:
        if(len(QuestionAndAnswers["answersList"]) != 0):
            qNumText = QuestionAndAnswers["qNumText"]
            x0, y0, x1, y1 = getSoruKokuCoordinates(
                textsDf, QuestionAndAnswers)
            list = getAnswerTextCoordinates2(
                QuestionAndAnswers, (x0, y0, x1, y1))
            funResList.append({
                "qNumTextAttr": {
                    "x0": qNumText["left"],
                    "x1": qNumText["left"] + qNumText["width"],
                    "y0": qNumText["top"],
                    "y1": qNumText["top"] + qNumText["height"],
                    "text": qNumText["text"]
                },
                "soruKokuCoordinates": {
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1
                },
                "answersCoordinatesList": list
            })
    validatedList = validatePositions(funResList)
    return validatedList


def validatePositions(funResList):
    validateResList = funResList
    for questionIndex in range(len(validateResList)):
        qNumText = validateResList[questionIndex]["qNumTextAttr"]
        answers = validateResList[questionIndex]["answersCoordinatesList"]
        validateResList[questionIndex]["answersCoordinatesList"] = [
            answer for answer in answers if answer["answerText"]["x0"] > qNumText["x1"]]
    return validateResList
