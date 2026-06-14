import cv2
import numpy as np
import time
import random
import os
import pygame

pygame.mixer.init()
lagu_file = 'freedom_dive.mp3'
durasi = 266.0

def muat_lagu():
    if os.path.exists(lagu_file):
        pygame.mixer.music.load(lagu_file)
    else:
        print(f"PERINGATAN: File {lagu_file} tidak ditemukan! Game berjalan tanpa lagu.")

def generate_rhythm_sequence(durasi):
    sequence = []
    bpm = 222.22
    sec_per_beat = 60 / bpm 
    spawn_interval = sec_per_beat * 2
    audio_offset = 1.2 

    total_notes = int((durasi - audio_offset) / spawn_interval)
    last_zone = -1
    
    for i in range(total_notes):
        spawn = audio_offset + (i * spawn_interval)
        
        new_zone = random.randint(1, 9)
        while new_zone == last_zone:
            new_zone = random.randint(1, 9)
            
        last_zone = new_zone
        
        sequence.append({
            "zone": new_zone,
            "spawn_time": spawn,
            "hit_time": spawn + 1.2, 
            "status": "pending"
        })
    return sequence

game_state = "PLAYING"

score = perfect_count = good_count = miss_count = 0


active_feedbacks = []

start_time = time.time()
pause_start_time = 0
total_paused_duration = 0
current_time = 0

rhythm_sequence = generate_rhythm_sequence(durasi)

def reset_game():
    global score, perfect_count, good_count, miss_count, rhythm_sequence
    global start_time, total_paused_duration, game_state, current_time, active_feedbacks
    score = perfect_count = good_count = miss_count = 0
    rhythm_sequence = generate_rhythm_sequence(durasi)
    active_feedbacks.clear()
    total_paused_duration = 0
    current_time = 0
    start_time = time.time()
    game_state = "PLAYING"
    muat_lagu()
    if os.path.exists(lagu_file):
        pygame.mixer.music.play()

weapon_img = cv2.imread('weapon.png', cv2.IMREAD_UNCHANGED)
if weapon_img is None:
    print("Jalankan generate_weapon.py terlebih dahulu!")
    exit()
weapon_h, weapon_w = weapon_img.shape[:2]

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

muat_lagu()
if os.path.exists(lagu_file):
    pygame.mixer.music.play()

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    grid_w, grid_h = w // 3, h // 3

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'): 
        break 
    elif key == ord('p'):
        if game_state == "PLAYING":
            game_state = "PAUSED"
            pause_start_time = time.time()
            if os.path.exists(lagu_file): pygame.mixer.music.pause()
        elif game_state == "PAUSED":
            game_state = "PLAYING"
            total_paused_duration += (time.time() - pause_start_time)
            if os.path.exists(lagu_file): pygame.mixer.music.unpause()
    elif key == ord('r'):
        reset_game()

    if game_state == "GAMEOVER":
        overlay = frame.copy()
        cv2.rectangle(overlay, (0,0), (w,h), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        cv2.putText(frame, "TRACK COMPLETED", (w//2 - 180, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,0), 3)
        cv2.putText(frame, f"TOTAL SCORE: {score}", (w//2 - 150, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(frame, f"PERFECT: {perfect_count}", (w//2 - 150, 220), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, f"GOOD: {good_count}", (w//2 - 150, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(frame, f"MISS: {miss_count}", (w//2 - 150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.putText(frame, "Press 'R' to Retry or 'Q' to Quit", (w//2 - 200, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2)
        
        cv2.imshow("Mage Rhythm", frame)
        continue

    if game_state == "PAUSED":
        overlay = frame.copy()
        cv2.rectangle(overlay, (0,0), (w,h), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        cv2.putText(frame, "PAUSED", (w//2 - 100, h//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,0), 3)
        cv2.putText(frame, "Press 'P' Resume | 'R' Restart | 'Q' Quit", (w//2 - 260, h//2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.imshow("Mage Rhythm", frame)
        continue

    current_time = time.time() - start_time - total_paused_duration
    
    if current_time >= durasi:
        game_state = "GAMEOVER"
        if os.path.exists(lagu_file): pygame.mixer.music.stop()
        continue

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([100, 100, 50], dtype=np.uint8)
    upper_skin = np.array([130, 255, 255], dtype=np.uint8)
    
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cx, cy = 0, 0
    hand_detected = False
    is_fist = False
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area > 1000:
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            
            if hull_area > 0:
                solidity = float(area) / hull_area
            else:
                solidity = 0

            if solidity > 0.88:
                is_fist = True

            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                hand_detected = True
                
                y1, y2 = max(0, cy - weapon_h//2), min(h, cy + weapon_h//2)
                x1, x2 = max(0, cx - weapon_w//2), min(w, cx + weapon_w//2)
                
                if (x2 - x1) == weapon_w and (y2 - y1) == weapon_h:
                    alpha_channel = weapon_img[:, :, 3] / 255.0
                    alpha_3d = np.dstack((alpha_channel, alpha_channel, alpha_channel))
                    roi = frame[y1:y2, x1:x2]
                    weapon_rgb = weapon_img[:, :, :3]
                    
                    blended = (weapon_rgb * alpha_3d + roi * (1 - alpha_3d)).astype(np.uint8)
                    frame[y1:y2, x1:x2] = blended

    for i in range(1, 3):
        cv2.line(frame, (i * grid_w, 0), (i * grid_w, h), (100, 100, 100), 1)
        cv2.line(frame, (0, i * grid_h), (w, i * grid_h), (100, 100, 100), 1)
        
    current_zone = -1
    if hand_detected:
        current_zone = ((cy // grid_h) * 3) + ((cx // grid_w) + 1)

    for target in rhythm_sequence:
        if target["spawn_time"] <= current_time <= (target["hit_time"] + 0.4):
            if target["status"] == "pending":
                tz_col, tz_row = (target["zone"] - 1) % 3, (target["zone"] - 1) // 3
                tx1, ty1 = tz_col * grid_w, tz_row * grid_h
                tx2, ty2 = tx1 + grid_w, ty1 + grid_h
                cx_grid, cy_grid = tx1 + grid_w // 2, ty1 + grid_h // 2
                
                progress = (current_time - target["spawn_time"]) / (target["hit_time"] - target["spawn_time"])
                progress = min(1.0, max(0.0, progress))
                
                cur_w, cur_h = int(grid_w * progress), int(grid_h * progress)
                
                cv2.rectangle(frame, (tx1+5, ty1+5), (tx2-5, ty2-5), (255, 0, 255), 2)
                bx1, by1 = cx_grid - cur_w // 2, cy_grid - cur_h // 2
                bx2, by2 = cx_grid + cur_w // 2, cy_grid + cur_h // 2
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 255, 255), max(1, int(4 * progress)))
                
                time_diff = abs(current_time - target["hit_time"])
                
                if current_zone == target["zone"] and progress >= 0.7:
                    if is_fist: 
                        if time_diff <= 0.2:
                            score += 100
                            perfect_count += 1
                            active_feedbacks.append({"text": "PERFECT!", "time": current_time, "x": cx_grid - 70, "y": cy_grid, "color": (0, 255, 0)})
                            target["status"] = "hit"
                        elif time_diff <= 0.4:
                            score += 50
                            good_count += 1
                            active_feedbacks.append({"text": "GOOD!", "time": current_time, "x": cx_grid - 45, "y": cy_grid, "color": (0, 255, 255)})
                            target["status"] = "hit"
                    
        elif current_time > target["hit_time"] + 0.4 and target["status"] == "pending":
            target["status"] = "miss"
            miss_count += 1

            tz_col, tz_row = (target["zone"] - 1) % 3, (target["zone"] - 1) // 3
            cx_grid = (tz_col * grid_w) + (grid_w // 2)
            cy_grid = (tz_row * grid_h) + (grid_h // 2)
            
            active_feedbacks.append({"text": "MISS!", "time": current_time, "x": cx_grid - 40, "y": cy_grid, "color": (0, 0, 255)})

    cv2.putText(frame, f"SCORE: {score}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(frame, f"TIME: {current_time:.1f}/{durasi}s", (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    new_feedbacks = []
    for fb in active_feedbacks:
        time_elapsed = current_time - fb["time"]
        if time_elapsed < 0.8: 
            float_y = int(fb["y"] - (time_elapsed * 40))
            cv2.putText(frame, fb["text"], (fb["x"], float_y), cv2.FONT_HERSHEY_DUPLEX, 0.8, fb["color"], 2)
            new_feedbacks.append(fb) 
            
    active_feedbacks = new_feedbacks 

    cv2.imshow("Deteksi Masking", mask)
    cv2.imshow("Mage Rhythm", frame)

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()