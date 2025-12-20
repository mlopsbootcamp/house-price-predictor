# 🏠 IT5414 - House Price Predictor

Dự án Machine Learning end-to-end dự đoán giá nhà, áp dụng các nguyên tắc MLOps.

---

## 📦 Cấu trúc dự án

```
IT5414-house-price-predictor/
├── configs/                    # Cấu hình model
│   └── model_config.yaml
├── data/
│   ├── raw/                    # Dữ liệu gốc
│   └── processed/              # Dữ liệu đã xử lý
├── deployment/
│   └── mlflow/                 # Docker Compose cho MLflow
├── models/
│   └── trained/                # Model và preprocessor đã train
├── notebooks/                  # Jupyter notebooks thử nghiệm
├── src/
│   ├── api/                    # FastAPI backend
│   ├── data/                   # Script xử lý dữ liệu
│   ├── features/               # Feature engineering
│   └── models/                 # Training scripts
├── streamlit_app/              # Giao diện Streamlit
├── Dockerfile                  # Docker cho FastAPI
├── docker-compose.yaml         # Orchestration
└── requirements.txt
```

---

## 🛠️ Yêu cầu hệ thống

- **Python**: 3.10 hoặc 3.11
- **Docker Desktop**: [Download](https://www.docker.com/products/docker-desktop/)
- **Git**: [Download](https://git-scm.com/)
- **Anaconda/Miniconda** (khuyến nghị): [Download](https://docs.conda.io/en/latest/miniconda.html)

---

## 🚀 Hướng dẫn cài đặt và chạy

### Bước 1: Clone repository

```bash
git clone https://github.com/hidrochin/IT5414-house-price-predictor
cd IT5414-house-price-predictor
```

### Bước 2: Tạo môi trường Python

```bash
# Sử dụng Conda (khuyến nghị)
conda create -n it5414 python=3.10
conda activate it5414

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 3: Cài đặt Docker Desktop

1. Tải Docker Desktop tại https://www.docker.com/products/docker-desktop/
2. Chọn **Download for Windows – AMD64**
3. Cài đặt với tùy chọn **Use WSL 2**
4. Khởi động Docker Desktop
5. Kiểm tra: `docker --version`

### Bước 4: Khởi động MLflow

```bash
cd deployment/mlflow
docker compose up -d
```

Truy cập MLflow UI: http://localhost:5555

### Bước 5: Training Model

```bash
# Quay lại thư mục gốc
cd ../..

# 1. Xử lý dữ liệu
python src/data/run_processing.py \
  --input data/raw/house_data.csv \
  --output data/processed/cleaned_house_data.csv

# 2. Feature engineering
python src/features/engineer.py \
  --input data/processed/cleaned_house_data.csv \
  --output data/processed/featured_house_data.csv \
  --preprocessor models/trained/preprocessor.pkl

# 3. Train model
python src/models/train_model.py \
  --config configs/model_config.yaml \
  --data data/processed/featured_house_data.csv \
  --models-dir models \
  --mlflow-tracking-uri http://localhost:5555
```

### Bước 6: Chạy ứng dụng với Docker

```bash
# Build và khởi động
docker compose up -d

# Kiểm tra trạng thái
docker ps
```

---

## 🌐 Truy cập ứng dụng

| Dịch vụ | URL | Mô tả |
|---------|-----|-------|
| **Streamlit UI** | http://localhost:8501 | Giao diện người dùng |
| **FastAPI** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **MLflow** | http://localhost:5555 | Experiment tracking |

---

## 📡 Sử dụng API

### Health Check

```bash
curl http://localhost:8000/health
```

### Dự đoán giá nhà

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sqft": 1500,
    "bedrooms": 3,
    "bathrooms": 2,
    "location": "suburban",
    "year_built": 2000,
    "condition": "Good"
  }'
```

**Response:**
```json
{
  "predicted_price": 382536.69,
  "confidence_interval": [344283.02, 420790.36],
  "features_importance": {},
  "prediction_time": "2025-12-14T03:45:41"
}
```

---

## 🔄 Quản lý Docker

```bash
# Xem logs
docker compose logs -f

# Dừng tất cả containers
docker compose down

# Rebuild sau khi sửa code
docker compose build
docker compose up -d
```

---

## 📁 Các file quan trọng

| File | Mô tả |
|------|-------|
| `Dockerfile` | Build FastAPI backend |
| `streamlit_app/Dockerfile` | Build Streamlit frontend |
| `docker-compose.yaml` | Orchestrate cả 2 services |
| `configs/model_config.yaml` | Cấu hình model (algorithm, hyperparameters) |
| `models/trained/house_price_model.pkl` | Model đã train |
| `models/trained/preprocessor.pkl` | Preprocessor cho features |

---

## 🧪 Model Performance

- **Algorithm**: XGBoost
- **MAE**: 17,497.87
- **R² Score**: 0.9779

---

## 👨‍💻 Thành viên nhóm



## 📝 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

**IT5414 - Machine Learning Course Project**
