We'll guide you through **how to set up, install dependencies, and run the project**.

## **📌 1. Set Up Your Environment**

Create a new virtual environment (`venv`)
### **On Windows (PowerShell)**
```powershell
python -m venv venv
```

Since you've already created a virtual environment (`venv`), activate it first.

### **On Windows (PowerShell)**
```powershell
cd /path/to/smart_shopping
venv\Scripts\activate
```

### **On macOS/Linux (Terminal)**
```bash
cd /path/to/smart_shopping
source venv/bin/activate
```

---

## **📌 2. Install Dependencies**
Your `requirements.txt` should contain all necessary libraries. Install them with:
```powershell
pip install -r requirements.txt
```
If `requirements.txt` is missing, you may need to manually install:
```powershell
pip install fastapi uvicorn streamlit pandas plotly requests pyyaml
```

---

## **📌 3. Set Up Database (If Required)**
Your project has a `database/` directory with `db_manager.py` and `seed_data.py`. You likely need to **initialize the database**.

Check inside `seed_data.py`, and if it contains an initialization script, run:
```powershell
python database/seed_data.py
```

---

## **📌 4. Run the Backend API (FastAPI)**
Your **API is in `api/main.py`**, likely using **FastAPI**.

Start the API server:
```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Now, **your API is running at**:  
👉 `http://localhost:8000/docs` (Swagger API Docs)  
👉 `http://localhost:8000/` (Root API)

---

## **📌 5. Run the Frontend UI (Streamlit)**
Your `ui.py` uses **Streamlit** for visualization. To launch it:
```powershell
streamlit run ui.py
```
This will open your app in a browser.

---

## **📌 6. Testing API Endpoints**
Once the API is running, test it with:

```powershell
curl http://localhost:8000
```
or use **Postman** or `requests` in Python:
```python
import requests
response = requests.get("http://localhost:8000")
print(response.json())
```

---

## **📌 7. Convert Data (If Required)**
Your project contains `convert_data.py`. If this is for **preprocessing customer/product data**, run it:
```powershell
python convert_data.py
```

---

## **📌 8. Automate with a Single Script**
Instead of running each command manually, create a script **run_project.ps1**:

```powershell
# PowerShell script to automate setup & run
venv\Scripts\activate
pip install -r requirements.txt
python database/seed_data.py  # Setup database
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "api.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -NoNewWindow -FilePath "streamlit" -ArgumentList "run ui.py"
```

Run it:
```powershell
powershell -ExecutionPolicy Bypass -File run_project.ps1
```

---

## **📌 9. Debugging Common Issues**
- **ModuleNotFoundError**: Ensure you installed dependencies:  
  ```powershell
  pip install -r requirements.txt
  ```
- **Port Conflict (8000)**:  
  Find the process using it and kill it:
  ```powershell
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- **Database Errors**: Ensure database schema is initialized via `seed_data.py`.
  
- ### **📌 Fixing Installation Issues**

If you face any **issues** with your installation:
1. `sqlite3==1.0.0` **does not exist** as a separate package (SQLite is built into Python).
2. Some packages require a different Python version (your **NumPy**, **scikit-learn** issue).

---

#### **🔹 Solution 1: Upgrade Python (If Needed)**
Some packages (like **scikit-learn** and **NumPy**) might not support your Python version.

Check your Python version:
```powershell
python --version
```
✅ If it's **below Python 3.8**, **upgrade** Python to **3.8+ or 3.9+** (recommended).

You can download the latest Python from:  
🔗 [Python Official Website](https://www.python.org/downloads/)

---

#### **🔹 Solution 2: Upgrade Pip**
You are also using an **old version of `pip`**. Upgrade it first:
```powershell
python -m pip install --upgrade pip
```

---

#### **🔹 Solution 3: Reinstall Dependencies**
After removing `sqlite3` and upgrading `pip`, try reinstalling:
```powershell
pip install -r requirements.txt
```
If you still face issues with NumPy or scikit-learn, install them separately first:
```powershell
pip install numpy==1.26.0 scikit-learn==1.3.1
```
Then retry:
```powershell
pip install -r requirements.txt
```

---

#### **🔹 Solution 4: Create a New Virtual Environment**
If the issue persists, recreate the virtual environment:
```powershell
# Remove existing venv (Only if you don't have important packages)
rm -r venv  # Use 'rd /s /q venv' on Windows

# Create a new virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux

# Upgrade pip again
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### ✅ **1. Fix Ollama Model Issue**
Run the following command to check installed models:
```sh
ollama list
```
If `"llama3"` isn't listed, install it:
```sh
ollama pull llama3
```

---

#### **🔹 Summary of Fixes**
✅ **Upgrade Python** (if needed)  
✅ **Upgrade pip** using `python -m pip install --upgrade pip`  
✅ **Reinstall dependencies** with `pip install -r requirements.txt`  
✅ **Create a new virtual environment** if errors persist  
✅ **Fix Ollama Model Issue** → Install `"llama3"` or use `"llama2"`.

---

---

## **📌 Summary**
| **Step**        | **Command** |
|----------------|------------|
| Activate venv | `venv\Scripts\activate` |
| Install Libraries | `pip install -r requirements.txt` |
| Initialize DB | `python database/seed_data.py` |
| Run API | `uvicorn api.main:app --reload` |
| Run UI | `streamlit run ui.py` |
| Automate | `powershell -File run_project.ps1` |
