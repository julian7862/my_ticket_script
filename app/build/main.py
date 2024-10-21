import time
import os
import ddddocr
import paddlehub as hub
import cv2
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import faulthandler
faulthandler.enable()


# # 開始計時
# start_time = time.time()

# # 初始化 ddddocr
# ocr = ddddocr.DdddOcr()

# # 讀取圖像並進行 OCR 分析
# image = open("/Users/julian/Downloads/captcha.png", "rb").read()
# result = ocr.classification(image)

# # 結束計時
# end_time = time.time()

# # 輸出結果和執行時間
# print(f"Result: {result}")
# print(f"Time taken: {end_time - start_time:.4f} seconds")



# 开始计时
start_time = time.time()

# # 初始化 ddddocr
# ocr = ddddocr.DdddOcr()

# 初始化 PaddleHub OCR 模型
ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=False)  # mkldnn加速僅在CPU下有效

# 定义图像所在的目录
image_dir = '/Users/julian/my_ticket_script/dddd_trainer/downloaded_images_training_data_copy_2/'  # 假设脚本与目录在同一位置

# 初始化真實標籤和預測標籤的列表
y_true = []
y_pred = []

# 遍歷目錄中的所有 png 文件
for filename in os.listdir(image_dir):
    if filename.endswith('.png'):
        # 提取真實標籤，即文件名 '_' 前的字符串
        # 例如，文件名為 '1234_fjidajfiajdf.png'，那麼真實標籤就是 '1234'
        label = filename.split('_')[0]

        # 讀取圖像並進行 OCR 分析
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)
        result = ocr.recognize_text(images=[image])

        # 提取 OCR 模型的預測結果
        predicted_text = result[0]['data'][0]['text'] if result[0]['data'] else ""

        # 將真實標籤和預測結果添加到列表中
        y_true.append(label)
        y_pred.append(predicted_text)

        # 判斷預測是否成功
        if predicted_text == label:
            status = '成功'
        else:
            status = '失敗'

        # 打印真實標籤、預測結果和狀態
        print(f"文件名: {filename}, 真實標籤: {label}, 預測結果: {predicted_text}, 預測{status}")

# 結束計時
end_time = time.time()

# 計算準確率、精確率、召回率和 F1-score
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='weighted', zero_division=1)
recall = recall_score(y_true, y_pred, average='weighted', zero_division=1)
f1 = f1_score(y_true, y_pred, average='weighted', zero_division=1)

# 輸出結果和執行時間
print(f"\n準確率 (Accuracy): {accuracy:.4f}")
print(f"精確率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1-score: {f1:.4f}")
print(f"執行時間: {end_time - start_time:.4f} 秒")

# 輸出詳細的分類報告
print("\n分類報告 (Classification Report):")
print(classification_report(y_true, y_pred, zero_division=1))


