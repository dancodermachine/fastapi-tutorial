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
If your model takes time to make predictions, it may be interesting to **cache** the results: if the prediction for a particular input has already been done, it makes sense to return the same result we saved on disk rather than running the computations again.
```python
import contextlib
import os
import joblib
from fastapi import Depends, FastAPI, status
from pydantic import BaseModel
from sklearn.pipeline import Pipeline

class PredictionInput(BaseModel):
    """
    Validate the request payload
    """
    text: str

class PredictionOutput(BaseModel):
    """
    Return a structured JSON response
    """
    category: str

# `location`, which is the directory path where Joblib will store the results. Joblib automatically saves cached results on the hard disk.
memory = joblib.Memory(location="cache.joblib")

# We added an `ignore` argument to the decorator, which allows us to tell Joblib to not take into account some arguments in the caching mechanism. Here, we excluded the `model` argument.
@memory.cache(ignore=["model"])
def predict(model: Pipeline, text: str) -> int:
    prediction = model.predict([text])
    return prediction[0]

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

    def predict(self, input: PredictionInput) -> PredictionOutput:
        """Runs a prediction"""
        if not self.model or not self.targets:
            raise RuntimeError("Model is not loaded")
        prediction = predict(self.model, input.text)
        category = self.targets[prediction]
        return PredictionOutput(category=category)

newgroups_model = NewsgroupsModel()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    We are implementing a lifespan handler to call `load_model`. This way, we are making sure that the model is loaded during application startup and is ready to use.
    """
    newgroups_model.load_model()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/prediction")
def prediction(
    output: PredictionOutput = Depends(newgroups_model.predict),
) -> PredictionOutput:
    return output

# We added a `delete/cache` route so that we can clear the whole Joblib cache with an HTTP request. The `clear` method on the `memory` object removes all the Joblib cache files on the disk.
@app.delete("/cache", status_code=status.HTTP_204_NO_CONTENT)
def delete_cache():
    memory.clear()
```

Joblib is implemented to work synchronously. Nevertheless, it's performing long I/O operations: it reads and writes cache files on the hard disk. Hence, it will block the process and won't be able to answer other requests while this is happening.

To solve this, FastAPI implements a neat mechanism: *if you define a path operation function or a dependency as a standard, non-async function, it'll run it in a separate thread*. This means that blocking operations, such as synchronous file reading, won't block the main process. In a sense, we could say it mimics an asynchronous operation.

Rule of thumbs:
* If the functions don't invovle long I/O operations (file reading, network requests, and so on), define them as `async`.
* If they involve I/O operatons, see the following:
    - Try to choose libraries that are compatible with asynchronous I/O, as we saw for databases or HTTP clients. In this case, your functions will be async.
    - If it's not possible, which is the case for Joblib caching, define them as standard functions. FastAPI will run them is a separate thread.

Since Joblib is completely synchronous at making I/O operations, we switched the path operations and the dependency method so that they were synchronous, standard methods.