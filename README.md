# Ewaste-fastapi

> A **FastAPI**-powered app for *detecting & classifying electronic waste (e-waste)* using YOLO deep learning.  
> **Upload** photos of devices and get instant detection—with bounding boxes!

***

## 🚀 Features

- ⚡ **FastAPI Backend:** Blazing-fast, modern API.
- 🖼 **YOLO Detection:** Deep learning to spot e-waste in your pics.
- 📤 **Easy Upload:** Drag & drop or API-ready.
- 🔲 **Visual Results:** Returned images are automatically annotated.
- 🗃 **REST API:** Connect with your own workflows.
- 📝 **Swagger Docs:** Instant API playground (`/docs`).

***

## 📦 Setup & Installation


Requirements

- Python 3.8+
- FastAPI, Uvicorn
- Pillow, Numpy
- Pydantic
- Ultralytics YOLO


```sh
# Get the code
git clone https://github.com/Dexter0013/ewaste-fastapi.git
cd ewaste-fastapi

# Optional: virtual environment
python -m venv venv
source venv/bin/activate

# Install reqs
pip install -r requirements.txt
```

***

## ▶️ Running the App

```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

- Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

***

## 🖼 Usage

### Upload an Image

- **Endpoint:** `POST /predict`
- **Data:** `file` (image)

```sh
curl -F "file=@your-image.jpg" http://localhost:8000/predict --output detected.jpg
```

- 🔳 Gets you: *Image with e-waste items highlighted!*

***

## 📁 Project Structure

```text
ewaste-fastapi/
│
├── main.py           # API app & endpoints
├── utils.py          # Model & image helpers
├── yolov8.pt         # YOLO weights
├── requirements.txt
└── README.md
```

***

## 🛠 Customization

- **Change the YOLO model?** Simply swap the weights in your project folder.
- **New classes? Retrain.** (Use your dataset if needed.)

***

## 🍀 License

Released under the **MIT License**.

***

## 🤝 Contributing

Pull requests and feedback welcome!

***

## 💬 Contact

Use [GitHub Issues](https://github.com/Dexter0013/ewaste-fastapi/issues) or start a thread in Discussions.

***


  
  
