# Simpan sebagai training_yolov8.py
from ultralytics import YOLO
import multiprocessing

# Load model
model = YOLO('yolov8n.pt')  # Ganti dengan path ke model yang sudah dilatih sebelumnya jika ada untuk 'transfer learning')
def main():
    # Konfigurasi training
    model.train(
        data=r"D:\obstacle-detection-system\training\dataset_config\data.yaml",
        epochs=100,             
        imgsz=320,              
        batch=16,               
        workers=0,              # Ubah workers ke 0 untuk menghindari masalah multiprocessing
        patience=20,            
        optimizer='AdamW',      
        cos_lr=True,            
        weight_decay=0.0005,    
        pretrained=True,        
        device='0',             
        plots=True,             
        save=True,              
        save_period=10,         
        project='raspi_model_3b',  
        name='yolov8n_optimized' 
    )
    
    # # Ekspor model ke format yang optimum
    # model_path = 'raspi_model/yolov8n_optimized7/weights/best.pt'
    # trained_model = YOLO(model_path)
    
    # # Ekspor ke format ONNX
    # trained_model.export(format='onnx', dynamic=True, simplify=True)

if __name__ == '__main__':
    # Penting: tambahkan ini untuk Windows
    multiprocessing.freeze_support()
    main()