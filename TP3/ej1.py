############################################################################################
#                                                                                          #
#                              PROCESAMIENTO DE IMÁGENES 1                                 #
#                                 TRABAJO PRÁCTICO N°3                                     #
#                                                                                          #
#          GRUPO N°16: Gonzalo Asad, Sergio Castells, Agustín Alsop, Rocio Hachen          #
#                                                                                          #
#                               Problema 1 - Cinco dados                                   #
#                                                                                          #
############################################################################################

# Librerías
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import false
from customlib import *
import os

os.makedirs("./frames", exist_ok = True)  # Si no existe, crea la carpeta 'frames' en el directorio actual.

# --- Leer un video --------------------------------------------
for video in range(1, 5):
    cap = cv2.VideoCapture(f'./videos/tirada_{video}.mp4')  # Abre el archivo de video especificado ('tirada_1.mp4') para su lectura.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Obtiene el ancho del video en píxeles usando la propiedad CAP_PROP_FRAME_WIDTH.
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Obtiene la altura del video en píxeles usando la propiedad CAP_PROP_FRAME_HEIGHT.
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Obtiene los cuadros por segundo (FPS) del video usando CAP_PROP_FPS.
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Obtiene el número total de frames en el video usando CAP_PROP_FRAME_COUNT.
    out = cv2.VideoWriter(f'./videos/resultado_tirada_{video}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width,height))
    frame_number = 0
    aux_mov = 0  ####
    centroids_ant = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
    dice_values = [0, 0, 0, 0, 0]

    while (cap.isOpened()): # Verifica si el video se abrió correctamente.

        ret, frame = cap.read() # 'ret' indica si la lectura fue exitosa (True/False) y 'frame' contiene el contenido del frame si la lectura fue exitosa.
        
        if ret == True:
            
            frame = cv2.resize(frame, dsize=(int(width/3), int(height/3))) # Redimensiona el frame capturado.
            
            # Detección de Región de Interés (paño)
            if frame_number == 0:
                x_ini, x_fin, y_ini, y_fin = roiDetect(img=frame, percent=5, thresh=110, save=False)


            if (frame_number) > 0: # Ver de Eliminar esto
                frame_crop = frame[y_ini:y_fin, x_ini:x_fin]

                frame_crop_bgr = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2LAB)   

                L, A, B = cv2.split(frame_crop_bgr) 

                # Detección de Centroides
                flag, centroids, stats = centroidsDetect(img=A, th_min=95, min_area=100, max_area=900, jump=1)
    
                # Deteccíon de Movimiento
                motion = True
                if flag:   # Se detectaron los 5 dados
                    motion = motionDetector(centroids_ant, centroids, thresh=1)
                    if not motion and aux_mov < 3:
                        aux_mov += 1
                            
                    centroids_ant = centroids

                if motion and aux_mov > 0:
                    aux_mov -= 1    

                if aux_mov == 3:
                    quieto = True
                if aux_mov == 0:
                    quieto = False    

                ######
                max_area = 900
                min_area = 100
                pos_dado = 0
                for stat in stats:
                    x,y,w,h,a = stat
                    if a < max_area and a > min_area:
                        if a < ((x_fin-x_ini)*(y_fin-y_ini)*0.95):
                            cv2.rectangle(frame_crop, (x, y), (x+w, y+h), (255, 0, 0), 1)

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            # if not motion:
                            if quieto:
                                
                                if dice_values[pos_dado] == 0:
                                    # Obtención del valor del dado
                                    value = diceValue(img=L, x_cord=x, y_cord=y, width=w, height=h)
                                    dice_values[pos_dado] = value

                                cv2.putText(frame_crop, f'N {dice_values[pos_dado]}', (x, y-5), font, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
                                pos_dado += 1
                                
                # Si se tienen todos los valores
                if sum(dice_values) > 0:
                    result = gameAnalyzer(dice_values)

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 2
                    thickness = 2

                    # Calcular el tamaño del texto
                    (text_width, text_height), baseline = cv2.getTextSize(f'{result}', font, font_scale, thickness)

                    # Calcular el punto de inicio para centrar el texto
                    x = (frame.shape[1] - text_width) // 2  # Centro horizontal
                    y = 600 #(frame.shape[0] + text_height) // 2  # Centro vertical

                    # Escribir el texto en el centro de la imagen
                    cv2.putText(frame, f'{result}', (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
                  

            cv2.imshow('Frame', frame) # Imprime frame
            frame = cv2.resize(frame, (width, height))
            out.write(frame)

            # cv2.imwrite(os.path.join("frames", f"frame_{frame_number}.jpg"), frame) # Guarda el frame en el archivo './frames/frame_{frame_number}.jpg'.

            frame_number += 1
            if cv2.waitKey(25) & 0xFF == ord('q'): # Espera 25 milisegundos a que se presione una tecla. Si se presiona 'q' se rompe el bucle y se cierra la ventana.
                break
        else:  
            break  
    #print(frame_number)

    cap.release() # Libera el objeto 'cap', cerrando el archivo.
    out.release() # Libera el objeto 'out', cerrando el archivo.
    cv2.destroyAllWindows() # Cierra todas las ventanas abiertas.