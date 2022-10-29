import cv2
import numpy as np
import  os

# Cac duong mau do la phat hien duong thang
# Cac duong mau vang la khung phat hien vung bang de cat anh

working_directory = os.getcwd()
image = cv2.imread(working_directory + "\Images\Anh1.jpg")
h_image, w_image, c_image = image.shape
cdst = image.copy()

### Tien xu ly
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Chuyen ve anh xam
smooth_img = cv2.GaussianBlur(gray_img, (5, 5), 0)  # Lam min anh
im_bw = cv2.adaptiveThreshold(smooth_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8)  # Nhi phan anh

edges = cv2.Canny(im_bw, 100, 200, None, 3)  # Phat hien canh de xu ly Hough
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
        if abs(l[3] - l[1]) < h_image / 60 and abs(l[2] - l[0]) > w_image * 2 / 3:  # Neu la duong ngang thi them vao
            sum_avg_horizontal_line += l[2] - l[0]
            horizontal_lines_tmp.append(l)
        if abs(l[2] - l[0]) < w_image / 40:  # Neu la duong doc thi them vao
            sum_avg_vertical_line += l[2] - l[0]
            vertical_lines_tmp.append(l)

# Khong phat hien duong thang ngang hoac doc thi ket thuc chuong trinh
if (len(horizontal_lines_tmp) == 0 and len(vertical_lines_tmp) == 0) \
        or (len(horizontal_lines_tmp) == 1 and len(vertical_lines_tmp) == 0) \
        or (len(horizontal_lines_tmp) == 0 and len(vertical_lines_tmp) == 1):
    quit()


x1 = x2 = y1 = y2 = 0

# TH1: Khong phat hien duoc duong ngang nao, chi co cac duong doc
if len(horizontal_lines_tmp) == 0:
    avg_vertical_line = sum_avg_vertical_line / len(vertical_lines_tmp)
    for i in range(0, len(vertical_lines_tmp)):
        l = vertical_lines_tmp[i]
        if abs(l[2] - l[0]) >= avg_vertical_line * 0.99:
            vertical_lines.append(l)


    def sortX(val):
        return val[0]


    # Sap xep lai cac duong thang theo thu tu tu trai sang phai
    vertical_lines.sort(key=sortX)

    sum_top_point = sum_bot_point = 0

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

        sum_top_point += l[1]
        sum_bot_point += l[3]
        cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv2.LINE_AA)

    ver_line_avg_pos_top = int(sum_top_point / len(vertical_lines))
    ver_line_avg_pos_bot = int(sum_bot_point / len(vertical_lines))

    crop_vertical_lines = []
    for i in range(0, len(vertical_lines)):
        l = vertical_lines[i]
        if abs(l[1] - ver_line_avg_pos_top) < avg_vertical_line / 10 \
                and abs(l[3] - ver_line_avg_pos_bot) < avg_vertical_line / 10:
            crop_vertical_lines.append(l)

    y1 = ver_line_avg_pos_top
    y2 = ver_line_avg_pos_bot
    x1 = int((crop_vertical_lines[0][0] + crop_vertical_lines[0][2]) / 2)
    x2 = int((crop_vertical_lines[-1][0] + crop_vertical_lines[-1][2]) / 2)

# TH2: Phat hien duoc cac duong ngang
else:
    avg_horizontal_line = sum_avg_horizontal_line / len(horizontal_lines_tmp)
    avg_vertical_line = 0
    if horizontal_lines_tmp is not None:
        for i in range(0, len(horizontal_lines_tmp)):
            l = horizontal_lines_tmp[i]
            if abs(l[2] - l[0]) >= avg_horizontal_line * 0.99:
                horizontal_lines.append(l)
    if len(vertical_lines_tmp) != 0:
        avg_vertical_line = sum_avg_vertical_line / len(vertical_lines_tmp)
        for i in range(0, len(vertical_lines_tmp)):
            l = vertical_lines_tmp[i]
            if abs(l[2] - l[0]) >= avg_vertical_line * 0.99:
                vertical_lines.append(l)


    def sortX(val):
        return val[0]


    def sortY(val):
        return val[1]


    # Sap xep lai cac duong thang theo thu tu tu tren xuong duoi
    horizontal_lines.sort(key=sortY)

    # Sap xep lai cac duong thang theo thu tu tu trai sang phai
    vertical_lines.sort(key=sortX)

    sum_left_point = sum_right_point = 0
    sum_top_point = sum_bot_point = 0

    if horizontal_lines is not None:
        for i in range(0, len(horizontal_lines)):
            l = horizontal_lines[i]
            sum_left_point += l[0]
            sum_right_point += l[2]
            cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv2.LINE_AA)

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

        sum_top_point += l[1]
        sum_bot_point += l[3]
        cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv2.LINE_AA)

    # Cac duong thang ngang la it nhieu nhat, nen ta lay duong ngang lam chuan
    # Neu nhu thieu duong ngang thi moi xet den duong thang dung

    # Loc lai cac duong thang ngang, sao cho chi con cac duong co vi tri gan giong nhau nhat
    crop_horizontal_lines = []
    if horizontal_lines is not None:
        hor_line_avg_pos_left = int(sum_left_point / len(horizontal_lines))
        hor_line_avg_pos_right = int(sum_right_point / len(horizontal_lines))
        for i in range(0, len(horizontal_lines)):
            l = horizontal_lines[i]
            if abs(l[0] - hor_line_avg_pos_left) < avg_horizontal_line / 10 \
                    and abs(l[2] - hor_line_avg_pos_right) < avg_horizontal_line / 10:
                crop_horizontal_lines.append(l)

    x1 = x2 = y1 = y2 = 0

    if crop_horizontal_lines is not None:
        l1 = crop_horizontal_lines[0]
        l2 = crop_horizontal_lines[-1]

        # Truong hop 1: Chi co 1 duong ngang
        # Ta phai xet them cac duong doc (dieu nay co the tao nen ti le loi cao)
        if (l2[1] + l2[3]) / 2 - (l1[1] + l1[3]) / 2 < h_image / 100:
            if len(vertical_lines) != 0:
                ver_line_avg_pos_top = int(sum_top_point / len(vertical_lines))
                ver_line_avg_pos_bot = int(sum_bot_point / len(vertical_lines))

                x1 = int(sum_left_point / len(horizontal_lines))
                x2 = int(sum_right_point / len(horizontal_lines))
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

        # Truong hop 2: Co cac duong ngang cach xa nhau
        else:
            x1 = int(sum_left_point / len(horizontal_lines))
            x2 = int(sum_right_point / len(horizontal_lines))
            y1 = int((l1[1] + l1[3]) / 2)
            y2 = int((l2[1] + l2[3]) / 2)

cv2.line(cdst, (x1, y1), (x2, y1), (25, 183, 227), 3, cv2.LINE_AA)
cv2.line(cdst, (x1, y2), (x2, y2), (25, 183, 227), 3, cv2.LINE_AA)
cv2.line(cdst, (x1, y1), (x1, y2), (25, 183, 227), 3, cv2.LINE_AA)
cv2.line(cdst, (x2, y1), (x2, y2), (25, 183, 227), 3, cv2.LINE_AA)

cv2.imshow('detectedLines', cv2.resize(cdst, (480, 640)))
img_crop = image[y1:y2, x1:x2]
cv2.imshow('Crop', cv2.resize(img_crop, (480, 640)))
cv2.waitKey()