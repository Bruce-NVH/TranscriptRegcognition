import cv2
import numpy
import numpy as np
import os

# Cac duong mau do la phat hien duong thang
# Cac duong mau vang la khung phat hien vung bang de cat anh

working_directory = os.getcwd()
IMAGE = cv2.imread(working_directory + "\Images\Anh5.jpg")
detectedLinesImg = IMAGE.copy()


def sortX(val):
    return val[0]


def sortY(val):
    return val[1]


def preprocess(image, level):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Chuyen ve anh xam
    smooth_img = cv2.GaussianBlur(gray_img, (level, level), 0)  # Lam min anh
    im_bw = cv2.adaptiveThreshold(smooth_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15,
                                  8)  # Nhi phan anh
    return im_bw


def findHorAndVerLines(image, rawImg):
    h_image, w_image, c_image = rawImg.shape

    edges = cv2.Canny(image, 100, 200, None, 3)  # Phat hien canh de xu ly Hough]
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 250, None, None, h_image)

    horizontal_lines_tmp = []
    horizontal_lines = []
    vertical_lines_tmp = []
    vertical_lines = []

    # 2 bien nay dung de tinh chieu dai trung binh cac doan thang
    sum_avg_horizontal_line = 0
    sum_avg_vertical_line = 0

    if lines is not None:
        for i in range(0, len(lines)):
            l = lines[i][0]
            if abs(l[3] - l[1]) < h_image / 30 and abs(
                    l[2] - l[0]) > w_image * 2 / 3:  # Neu la duong ngang thi them vao
                sum_avg_horizontal_line += abs(l[2] - l[0])
                horizontal_lines_tmp.append(l)
            if abs(l[2] - l[0]) < w_image / 20:  # Neu la duong doc thi them vao
                sum_avg_vertical_line += abs(l[3] - l[1])
                vertical_lines_tmp.append(l)

    # Khong phat hien duong thang ngang hoac doc thi ket thuc chuong trinh
    if (len(horizontal_lines_tmp) == 0 and len(vertical_lines_tmp) == 0) \
            or (len(horizontal_lines_tmp) == 1 and len(vertical_lines_tmp) == 0) \
            or (len(horizontal_lines_tmp) == 0 and len(vertical_lines_tmp) == 1):
        return None, None

    # TH1: Khong phat hien duoc duong ngang nao, chi co cac duong doc
    if len(horizontal_lines_tmp) == 0:
        avg_vertical_line = sum_avg_vertical_line / len(vertical_lines_tmp)
        for i in range(0, len(vertical_lines_tmp)):
            l = vertical_lines_tmp[i]
            if abs(l[3] - l[1]) >= avg_vertical_line * 0.75:
                vertical_lines.append(l)

        # Sap xep lai cac duong thang theo thu tu tu trai sang phai
        vertical_lines.sort(key=sortX)

        for i in range(0, len(vertical_lines)):
            l = vertical_lines[i]

            # Kiem tra da la diem noi tu tren xuong duoi chua
            if l[1] > l[3]:
                l0 = l[0]
                l1 = l[1]
                l[0] = l[2]
                l[1] = l[3]
                l[2] = l0
                l[3] = l1
        return None, vertical_lines

    # TH2: Phat hien duoc cac duong ngang
    else:
        avg_horizontal_line = sum_avg_horizontal_line / len(horizontal_lines_tmp)
        if horizontal_lines_tmp is not None:
            for i in range(0, len(horizontal_lines_tmp)):
                l = horizontal_lines_tmp[i]
                if abs(l[2] - l[0]) >= avg_horizontal_line * 0.99:
                    horizontal_lines.append(l)
        if len(vertical_lines_tmp) != 0:
            avg_vertical_line = sum_avg_vertical_line / len(vertical_lines_tmp)
            for i in range(0, len(vertical_lines_tmp)):
                l = vertical_lines_tmp[i]
                if abs(l[3] - l[1]) >= avg_vertical_line * 0.75:
                    vertical_lines.append(l)

        # Sap xep lai cac duong thang theo thu tu tu tren xuong duoi
        horizontal_lines.sort(key=sortY)

        # Sap xep lai cac duong thang theo thu tu tu trai sang phai
        vertical_lines.sort(key=sortX)

        for i in range(0, len(vertical_lines)):
            l = vertical_lines[i]

            # Kiem tra da la diem noi tu tren xuong duoi chua
            if l[1] > l[3]:
                l0 = l[0]
                l1 = l[1]
                l[0] = l[2]
                l[1] = l[3]
                l[2] = l0
                l[3] = l1

        return horizontal_lines, vertical_lines


def findCropPoint(image, horizontalLines, verticalLines):
    h_image, w_image, c_image = image.shape

    # TH1: Khong phat hien duoc duong ngang nao, chi co cac duong doc
    if horizontalLines is None:
        sum_top_point = sum_bot_point = 0
        sum_vertical_line = 0
        for i in range(0, len(verticalLines)):
            l = verticalLines[i]
            sum_top_point += l[1]
            sum_bot_point += l[3]
            sum_vertical_line += abs(l[3] - l[1])

        ver_line_avg_pos_top = int(sum_top_point / len(verticalLines))
        ver_line_avg_pos_bot = int(sum_bot_point / len(verticalLines))
        avg_vertical_line = int(sum_vertical_line / len(verticalLines))

        crop_vertical_lines = []
        for i in range(0, len(verticalLines)):
            l = verticalLines[i]
            if abs(l[1] - ver_line_avg_pos_top) < avg_vertical_line / 10 \
                    and abs(l[3] - ver_line_avg_pos_bot) < avg_vertical_line / 10:
                crop_vertical_lines.append(l)

        y1 = ver_line_avg_pos_top
        y2 = ver_line_avg_pos_bot
        x1 = int((crop_vertical_lines[0][0] + crop_vertical_lines[0][2]) / 2)
        x2 = int((crop_vertical_lines[-1][0] + crop_vertical_lines[-1][2]) / 2)

        cv2.line(image, (x1, y1), (x2, y1), (25, 183, 227), 2, cv2.LINE_AA)
        cv2.line(image, (x1, y2), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)
        cv2.line(image, (x1, y1), (x1, y2), (25, 183, 227), 2, cv2.LINE_AA)
        cv2.line(image, (x2, y1), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)

        return x1, x2, y1, y2

    # TH2: Phat hien duoc cac duong ngang
    else:
        # Cac duong thang ngang la it nhieu nhat, nen ta lay duong ngang lam chuan
        # Neu nhu thieu duong ngang thi moi xet den duong thang dung

        # Loc lai cac duong thang ngang, sao cho chi con cac duong co vi tri gan giong nhau nhat
        crop_horizontal_lines = []
        sum_left_point = sum_right_point = 0
        sum_horizontal_line = 0
        for i in range(0, len(horizontalLines)):
            l = horizontalLines[i]
            sum_left_point += l[0]
            sum_right_point += l[2]
            sum_horizontal_line += abs(l[2] - l[0])

        hor_line_avg_pos_left = int(sum_left_point / len(horizontalLines))
        hor_line_avg_pos_right = int(sum_right_point / len(horizontalLines))
        avg_horizontal_line = int(sum_horizontal_line / len(horizontalLines))

        for i in range(0, len(horizontalLines)):
            l = horizontalLines[i]
            if abs(l[0] - hor_line_avg_pos_left) < avg_horizontal_line / 10 \
                    and abs(l[2] - hor_line_avg_pos_right) < avg_horizontal_line / 10:
                crop_horizontal_lines.append(l)

        l1 = crop_horizontal_lines[0]
        l2 = crop_horizontal_lines[-1]

        # Truong hop 1: Chi co 1 duong ngang hoac 2 duong ngang rat gan
        # Ta phai xet them cac duong doc (dieu nay co the tao nen ti le loi cao)
        if (l2[1] + l2[3]) / 2 - (l1[1] + l1[3]) / 2 < h_image / 100:
            x1 = x2 = y1 = y2 = 0
            if len(verticalLines) != 0:
                sum_top_point = sum_bot_point = 0
                for i in range(0, len(verticalLines)):
                    l = verticalLines[i]
                    sum_top_point += l[1]
                    sum_bot_point += l[3]

                ver_line_avg_pos_top = int(sum_top_point / len(verticalLines))
                ver_line_avg_pos_bot = int(sum_bot_point / len(verticalLines))

                x1 = hor_line_avg_pos_left
                x2 = hor_line_avg_pos_right

                # Duong ngang nam dau bang
                if (l1[1] + l1[3]) / 2 < (ver_line_avg_pos_top + ver_line_avg_pos_bot) / 3:
                    y1 = int((l1[1] + l1[3]) / 2)
                    y2 = ver_line_avg_pos_bot
                # Duong ngang nam giua bang
                elif (l1[1] + l1[3]) / 2 < (ver_line_avg_pos_top + ver_line_avg_pos_bot) * 2 / 3:
                    y1 = ver_line_avg_pos_top
                    y2 = ver_line_avg_pos_bot
                # Duong ngang nam cuoi bang
                else:
                    y1 = ver_line_avg_pos_top
                    y2 = int((l2[1] + l2[3]) / 2)

                cv2.line(image, (x1, y1), (x2, y1), (25, 183, 227), 2, cv2.LINE_AA)
                cv2.line(image, (x1, y2), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)
                cv2.line(image, (x1, y1), (x1, y2), (25, 183, 227), 2, cv2.LINE_AA)
                cv2.line(image, (x2, y1), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)

                return x1, x2, y1, y2
            else:
                return None, None, None, None

        # Truong hop 2: Co cac duong ngang cach xa nhau
        else:
            x1 = int(sum_left_point / len(horizontalLines))
            x2 = int(sum_right_point / len(horizontalLines))
            y1 = int((l1[1] + l1[3]) / 2)
            y2 = int((l2[1] + l2[3]) / 2)

            cv2.line(image, (x1, y1), (x2, y1), (25, 183, 227), 2, cv2.LINE_AA)
            cv2.line(image, (x1, y2), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)
            cv2.line(image, (x1, y1), (x1, y2), (25, 183, 227), 2, cv2.LINE_AA)
            cv2.line(image, (x2, y1), (x2, y2), (25, 183, 227), 2, cv2.LINE_AA)

            return x1, x2, y1, y2

def extendCropImg(img, x_1, x_2, y_1, y_2):
    h_image, w_image, c_image = img.shape

    if x_1 - 5 > 0:
        x_1 -= 5
    else:
        x_1 = 0

    if x_2 + 5 < w_image:
        x_2 += 5
    else:
        x_2 = w_image

    if y_1 - 5 > 0:
        y_1 -= 5
    else:
        y_1 = 0

    if y_2 + 5 < h_image:
        y_2 += 5
    else:
        y_2 = h_image

    return x_1, x_2, y_1, y_2


im_bw = preprocess(IMAGE, 5)
(horizontal_lines, vertical_lines) = findHorAndVerLines(im_bw, IMAGE)

# Ve cac duong thang ngang va doc
for i in range(0, len(horizontal_lines)):
    l = horizontal_lines[i]
    cv2.line(detectedLinesImg, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 2, cv2.LINE_AA)
for i in range(0, len(vertical_lines)):
    l = vertical_lines[i]
    cv2.line(detectedLinesImg, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 2, cv2.LINE_AA)

_x1, _x2, _y1, _y2 = findCropPoint(detectedLinesImg, horizontal_lines, vertical_lines)
x1, x2, y1, y2 = extendCropImg(IMAGE, _x1, _x2, _y1, _y2)


cv2.imshow('detectedLines', cv2.resize(detectedLinesImg, (480, 640)))
img_crop = IMAGE[y1:y2, x1:x2]
cv2.imshow('Crop', cv2.resize(img_crop, (480, 640)))
cv2.waitKey()

#
# ####################### NHAN DIEN CAC DUONG THANG DOC###############################
#

img_crop_bw = preprocess(img_crop, 5)
#
# vertical = numpy.copy(img_crop_bw)
# rows = vertical.shape[0]
# verticalSize = rows // 700
# verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (4, verticalSize))
# vertical = cv2.erode(vertical, verticalStructure)
# vertical = cv2.dilate(vertical, verticalStructure)
# cv2.imshow('vertical', cv2.resize(vertical, (480, 640)))

imgCropHorLines, imgCropVerLines = findHorAndVerLines(img_crop_bw, img_crop)
detectedLinesImgCrop = img_crop.copy()



# for i in range(0, len(imgCropHorLines)):
#     l = imgCropHorLines[i]
#     cv2.line(detectedLinesImgCrop, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 2, cv2.LINE_AA)
for i in range(0, len(imgCropVerLines)):
    l = imgCropVerLines[i]
    cv2.line(detectedLinesImgCrop, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 2, cv2.LINE_AA)

# cv2.imshow('imbw', cv2.resize(img_crop_bw, (480, 640)))
cv2.imshow('detectedLinesImgCrop', cv2.resize(detectedLinesImgCrop, (480, 640)))
cv2.waitKey()
