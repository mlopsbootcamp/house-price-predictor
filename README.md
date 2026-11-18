## Setting up Learning/Development Environment 

Start by installing 

  * Python 
  * Git 
  * Visual Studio Code (or alternate editor)
  * [UV Package Manager for Python](https://github.com/astral-sh/uv)  
  * [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Podman Desktop](https://podman-desktop.io/)



## Preparing Environemt 

Clone the Repo 

```
git clone xxx 
cd xxx
```

Setup Virtual Environment with UV 

```
uv venv --python python3.11
source .venv/bin/activate
```

Install necessary packages 

```
uv pip install -r requirements.txt
```

Setup MLFlow 

```
cd deployment/mlflow
docker compose -f mlflow-docker-compose.yml up -d  
docker compose ps 

# If you are using podman, use this instead 
podman compose -f mlflow-docker-compose.yml up -d
podman compose ps 
```


### If you want to use JupyterLab (Optional)

Optinally setup and launch Jupyterlab as

```
uv python -m jupyterlab
python -m jupyterlab
```

## Model Workflow 

Data Processing 

```
python src/data/run_processing.py --input data/raw/house_data.csv --output data/processed/cleaned_house_data.csv 
```

Feature Engineering 

```
python src/features/engineer.py \
  --input data/processed/cleaned_house_data.csv \
  --output data/processed/featured_house_data.csv \
  --preprocessor models/trained/preprocessor.pkl
```

Modeling Experimentation 

```
python src/models/train_model.py \
    --config configs/model_config.yaml \
    --data data/processed/featured_house_data.csv \
    --models-dir models \
    --mlflow-tracking-uri http://localhost:5555
```
