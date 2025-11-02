# Traditional ML Endpoints
How to serve thousands of prediction requests.

`Joblib` provides tools for efficiently saving Python objects to disk, such as large arrays of data or function results: this operation is generally called **dumping**.

## Dumping
```python
import joblib
model_targets_tuple = (model, newsgroups_training.target_names)
joblib.dump(model_targets_tuple, model_file)
```
Notice that we don't dump the model variable alone, instead, we wrap it in a tuple, along with the name of the categories, `target_names`. This allow us to retrieve the actual name of the category after the prediction has been made without us having to reload the training dataset.
## Loading
```python
import os
import joblib
from sklearn.pipeline import Pipeline

# Load the model
model_file = os.path.join(os.path.dirname(__file__), "newsgroups_model.joblib")
loaded_model: tuple[Pipeline, list[str]] = joblib.load(model_file)
model, targets = loaded_model

# Run a prediction
p = model.predict(["computer cpu memory ram"])
print(targets[p[0]])
```
## Endpoint
```python
import contextlib
import os
import joblib
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sklearn.pipeline import Pipeline

class PredictionInput(BaseModel):
    text: str

class PredictionOutput(BaseModel):
    category: str

class NewsgroupsModel:
    model: Pipeline | None = None
    targets: list[str] | None = None

    def load_model(self) -> None:
        """Loads the model"""
        model_file = os.path.join(os.path.dirname(__file__), "newsgroups_model.joblib")
        loaded_model: tuple[Pipeline, list[str]] = joblib.load(model_file)
        model, targets = loaded_model
        self.model = model
        self.targets = targets

    async def predict(self, input: PredictionInput) -> PredictionOutput:
        """Runs a prediction"""
        if not self.model or not self.targets:
            raise RuntimeError("Model is not loaded")
        prediction = self.model.predict([input.text])
        category = self.targets[prediction[0]]
        return PredictionOutput(category=category)

newgroups_model = NewsgroupsModel()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    newgroups_model.load_model()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/prediction")
async def prediction(
    output: PredictionOutput = Depends(newgroups_model.predict),
) -> PredictionOutput:
    return output
```