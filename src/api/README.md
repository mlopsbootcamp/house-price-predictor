## Intructions to build Container Image for this FastAPI App 

Create the Dockerfile in the root of the source code (`house-prcice-predictor`). 

Following is all the information you would need to start building the container image for this app 


  * Base Image : `python:3.11-slim`
  * To install dependencies: `pip install requirements.txt`
  * Port: `8000`
  * Launch Command : `uvicorn main:app --host 0.0.0.0 --port 8000`

Directory structure inside the container should look like this 

```
/app
  main.py
  schemas.py
  inference.py
  requirements.txt
  /models
     /trained
         house_price_model.pkl
         preprocessor.pkl
```

