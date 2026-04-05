import cv2
from deepface import DeepFace
import time
import threading

kamera = cv2.VideoCapture(0)
print("Kamera acildi. Cikis icin 'q' bas.")

sonuc = {"duygu": "bekleniyor", "stres": 0, "seviye": "BASLIYOR", "renk": (255, 255, 255)}
analiz_devam = False

def analiz_yap(frame):
    global analiz_devam
    try:
        a = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False, detector_backend="opencv")
        skorlar = a[0]["emotion"]
        duygu = a[0]["dominant_emotion"]
        stres = skorlar.get("angry", 0) + skorlar.get("fear", 0) + skorlar.get("disgust", 0)
        
        if stres > 50:
            seviye, renk = "YUKSEK STRES!", (0, 0, 255)
        elif stres > 25:
            seviye, renk = "ORTA STRES", (0, 165, 255)
        else:
            seviye, renk = "SAKIN", (0, 255, 0)

        sonuc.update({"duygu": duygu, "stres": stres, "seviye": seviye, "renk": renk})
    except:
        pass
    analiz_devam = False

son_analiz = time.time()

while True:
    ret, frame = kamera.read()
    if not ret:
        break

    simdi = time.time()
    if simdi - son_analiz >= 3 and not analiz_devam:
        analiz_devam = True
        son_analiz = simdi
        t = threading.Thread(target=analiz_yap, args=(frame.copy(),))
        t.daemon = True
        t.start()

    cv2.putText(frame, f"Duygu: {sonuc['duygu']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Stres: %{sonuc['stres']:.0f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, sonuc["renk"], 2)
    cv2.putText(frame, sonuc["seviye"], (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, sonuc["renk"], 2)

    cv2.imshow("Oyun Stres Olcer", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
kamera.release()
cv2.destroyAllWindows()

if sonuc["stres"] > 0:
        print(f"\nOrtalama stres skoru: %{sonuc['stres']:.0f}")
        print(f"Son duygu durumu: {sonuc['duygu']}")