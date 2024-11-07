import cv2
import math
from object_detection import ObjectDetection

od = ObjectDetection()
cap = cv2.VideoCapture('videos/los_angeles.mp4')
tracking_objs = {}
trajectories = {} # точка появления авто и точка, где его последний раз видели (по ним стоим траекторию)
tracking_frames = {} # сколько кадров была машина на экране
tracking_id = 0
cadr = 0
waiting_list = {} # список машин, которые пропали с экрана
speeds = {} # итоговая скорость машин (пикселей/кадр)

while True:
    cadr += 1
    ret, frame = cap.read()
    center_point_now = []
    (class_ids, scores, boxes) = od.detect(frame)
    for box in boxes:
        (x, y, w, h) = box
        cx = int(x + (w//2))
        cy = int(y + (h//2))
        app = True
        # Не добавляем дубликаты
        for pt in center_point_now:
            dist = math.hypot(cx - pt[0], cy - pt[1])
            if dist < 30:
                app = False
        if app:
            if cy > 550: # не добавляем машины в далеке
                center_point_now.append((cx, cy))
        #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
    cv2.line(frame, (0, 550), (1920, 550), (0, 255, 0), 1)
    #cv2.line(frame, (50, 540), (70, 540), (0, 255, 0), 3)





    for key in tracking_objs.keys():
        # обновление значений с словаре
        for pt in center_point_now:
            dist = math.hypot(tracking_objs[key][0] - pt[0], tracking_objs[key][1] - pt[1])
            if trajectories[key][1] == (0, 0):
                max_dist = 40
                if dist < max_dist:
                    tracking_objs[key] = pt
            else:
                ((x1, y1), (x2, y2)) = trajectories[key]
                k = (x2 - x1) / (y2 - y1 + 0.0000001)
                delta_x = abs(pt[0] - ((pt[1] - y1) * k + x1))
                if dist < 90 and delta_x < 10:
                    tracking_objs[key] = pt

    # обработка waiting_list
    list2del = []
    list2restore = []
    for key in waiting_list.keys():
        ((x, y), c) = waiting_list[key]
        if cadr - c > 3: # если не видели машину дольше 3 кадров, то ее удалим
            list2del.append(key)
        else:
            for pt in center_point_now:
                dist = math.hypot(x - pt[0], y - pt[1])
                if trajectories[key][1] == (0, 0): 
                    max_dist = 40
                    if dist < max_dist:
                        tracking_objs[key] = pt
                        list2restore.append(key)
                else:
                    ((x1, y1), (x2, y2)) = trajectories[key]
                    k =  (x2-x1)/(y2-y1+0.0000001)
                    delta_x = abs(pt[0] - ((pt[1]-y1)*k+x1))
                    #print(pt, k, key, delta_x)
                    if dist < 100 and delta_x < 15:

                        tracking_objs[key] = pt
                        list2restore.append(key)
    # восстанавливаем машины в основной словарь
    for key in list2restore:
        del waiting_list[key]
    # удаляем машины, которые не появились, выводим их скорость
    for key in list2del:
        # вывод скоростей
        if trajectories[key][1] != (0, 0): # если машину видели не 1 раз (иначе мало данных)
            way = math.hypot(trajectories[key][0][0]-trajectories[key][1][0], trajectories[key][0][1]-trajectories[key][1][1])
            speed = way//tracking_frames[key]-3
            speeds[key] = speed
            print(f'Скорость автомобиля {key} равна {speed} пиксилей/кадр')
        del waiting_list[key]
        del trajectories[key]
        del tracking_frames[key]


    # проверяем, не появились ли дубликаты
    new_dict = {}
    for key in tracking_objs.keys():
        if not(tracking_objs[key] in new_dict.values()):
            new_dict[key] = tracking_objs[key]

        else:
            old_key = -1
            for k1 in new_dict.keys():
                if new_dict[k1] == tracking_objs[key] and k1 > key:
                    old_key = k1
            if old_key != -1:
                del new_dict[old_key]
                new_dict[key] = tracking_objs[old_key]

    tracking_objs = new_dict



    # обновление траекторий и кадров
    for key in tracking_frames.keys():
        tracking_frames[key] += 1
    for key in trajectories.keys():
        if key in tracking_objs.keys():
            trajectories[key] = (trajectories[key][0], tracking_objs[key])


    for pt in center_point_now:
        # добавление значений в словарь
        if not(pt in tracking_objs.values()):
            trajectories[tracking_id] = (pt, (0,0))
            tracking_frames[tracking_id] = 1
            tracking_objs[tracking_id] = pt
            tracking_id += 1



    # 'ставим на учет' пропавшие машины
    keys2del = []
    for key in tracking_objs.keys():
        if not(tracking_objs[key] in center_point_now):
            keys2del.append(key)

    for key in keys2del:
        waiting_list[key] = (tracking_objs[key], cadr)
        del tracking_objs[key]

    # отображение id машин
    for object_id, pt in tracking_objs.items():
        cv2.circle(frame, pt, 3, (0, 0, 255), -1)
        cv2.putText(frame, f'{object_id}', (pt[0], pt[1]-7), 0, 1, (0, 0, 255), thickness=1)

    cv2.imshow('Frame', frame)
    cv2.waitKey(1)
