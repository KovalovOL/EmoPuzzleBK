from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from models import load_emotion_model, load_face_cascade
from myutils import process_image
import cv2

router = APIRouter()

# Загружаем модели при старте приложения
model = None
face_cascade = None

@router.on_event("startup")
async def load_models():
    global model, face_cascade
    model = load_emotion_model()
    face_cascade = load_face_cascade()

@router.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        target_emotion = (await websocket.receive_text()).lower()
        
        while True:
            frame_data = await websocket.receive_bytes()
            if process_image(frame_data, target_emotion, model, face_cascade):
                await websocket.send_text(f"Знайдено емоцію: {target_emotion}")
                break
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cv2.destroyAllWindows()
        await websocket.close()

@router.get("/", response_class=HTMLResponse)
async def get_client():
    return """
    <html>
    <head>
        <title>Emotion Detection Client</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .video-container {
                display: flex;
                gap: 20px;
            }
            video {
                border: 1px solid #ccc;
                background: #000;
            }
            button {
                padding: 10px 15px;
                background: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 4px;
            }
            button:disabled {
                background: #cccccc;
            }
            input {
                padding: 8px;
                width: 200px;
            }
            .status {
                padding: 10px;
                border-radius: 4px;
            }
            .active {
                background: #e7f7e7;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Детектор емоцій</h1>
        
            <div>
                <input type="text" id="targetEmotion" placeholder="Введіть емоцію (напр. happy)">
                <button id="startBtn" onclick="startDetection()">Старт</button>
                <button id="stopBtn" onclick="stopDetection()" disabled>Стоп</button>
            </div>
        
            <div class="video-container">
                <div>
                    <h3>Ваша камера:</h3>
                    <video id="webcam" width="400" height="300" autoplay muted></video>
                </div>
            </div>
        
            <div id="status" class="status">Статус: Неактивний</div>
        </div>

    <script>
        let ws = null;
        let mediaStream = null;
        let intervalId = null;
        const webcamElement = document.getElementById('webcam');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const statusElement = document.getElementById('status');

        async function startDetection() {
            const targetEmotion = document.getElementById('targetEmotion').value.toLowerCase().trim();
            
            if (!targetEmotion) {
                alert("Будь ласка, введіть емоцію для пошуку");
                return;
            }

            try {
                // Отримуємо доступ до камери
                mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
                webcamElement.srcObject = mediaStream;
                
                // Підключаємося до WebSocket сервера
                ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`);
                
                // Оновлюємо UI
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusElement.textContent = "Статус: Підключення...";
                statusElement.className = "status";

                ws.onopen = () => {
                    statusElement.textContent = "Статус: Активний (шукаємо " + targetEmotion + ")";
                    statusElement.className = "status active";
                    ws.send(targetEmotion);
                    
                    // Починаємо відправляти кадри на сервер
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    intervalId = setInterval(() => {
                        if (ws.readyState === WebSocket.OPEN) {
                            canvas.width = webcamElement.videoWidth;
                            canvas.height = webcamElement.videoHeight;
                            ctx.drawImage(webcamElement, 0, 0);
                            
                            // Конвертуємо в JPEG для зменшення розміру
                            canvas.toBlob(blob => {
                                const reader = new FileReader();
                                reader.onload = () => ws.send(reader.result);
                                reader.readAsArrayBuffer(blob);
                            }, 'image/jpeg', 0.85);
                        }
                    }, 200); // Відправляємо 5 кадрів на секунду
                };

                ws.onmessage = (event) => {
                    statusElement.textContent = "Статус: " + event.data;
                    alert(event.data);
                    stopDetection();
                };

                ws.onerror = (error) => {
                    console.error("WebSocket error:", error);
                    statusElement.textContent = "Статус: Помилка з'єднання";
                };

                ws.onclose = () => {
                    statusElement.textContent = "Статус: Відключено";
                    statusElement.className = "status";
                };

            } catch (error) {
                console.error("Error:", error);
                statusElement.textContent = "Статус: Помилка: " + error.message;
                stopDetection();
            }
        }

        function stopDetection() {
            // Зупиняємо відправку кадрів
            if (intervalId) clearInterval(intervalId);
            
            // Закриваємо WebSocket з'єднання
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
            
            // Вимикаємо камеру
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
                webcamElement.srcObject = null;
            }
            
            // Оновлюємо UI
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    </script>
</body>
</html>
    """