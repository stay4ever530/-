# 绿萝叶片健康检测系统

基于 YOLOv8n 的绿萝（Epipremnum aureum）叶片健康检测桌面应用，支持上传叶片照片自动识别健康/不健康状态。

## 功能

- 上传绿萝叶片照片（JPG/PNG/WEBP）
- 置信度阈值滑块调节
- 单次检测：标注框 + 检测列表
- 对比检测：同一图片高低阈值并排对比
- PyQt5 桌面界面，Windows 原生体验

## 安装

```bash
git clone https://github.com/yourname/lvluo-detector.git
cd lvluo-detector
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

或双击 `启动服务器.bat`（Windows）

## 打包为 EXE

```bash
build_exe.bat
```

生成的 EXE 在 `dist/` 目录下。

## 项目结构

```
lvluo-detector/
├── main.py            # 程序入口
├── gui.py             # PyQt5 界面
├── model.py           # YOLO 模型推理
├── best.pt            # 训练好的模型权重
├── requirements.txt   # 依赖
├── build_exe.bat      # 打包脚本
└── samples/           # 测试样本图片
```

## 模型信息

- 算法：YOLOv8n
- 类别：健康 / 不健康（2 分类）
- mAP50：0.547
- 模型大小：6.0 MB
- 训练图片：108 张

## 界面截图

（运行后截图放这里）

## 环境要求

- Python 3.7+
- Windows 10/11
- 推荐 NVIDIA GPU（CPU 也可运行，较慢）
