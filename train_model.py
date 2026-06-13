import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

# 1. Load Dataset
df = pd.read_csv('employee_attrition_performance.csv')

# Sesuaikan nama kolom target (misal Attrition)
target_col = 'Attrition' if 'Attrition' in df.columns else 'attrition'

# 2. Pisahkan Fitur dan Target
# Hapus employee_id karena tidak relevan
if 'employee_id' in df.columns:
    df = df.drop('employee_id', axis=1)

X = df.drop(target_col, axis=1)
y = df[target_col]

# 3. Definisikan kolom numerik dan kategorikal
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

# 4. Buat Preprocessing Pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 5. Buat Model Pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42))
])

# 6. Latih Model
print("Melatih model dengan scikit-learn versi lokal...")
pipeline.fit(X, y)

# 7. Simpan Model
os.makedirs('model', exist_ok=True)
model_path = 'model/attrition_prediction_model.pkl'
joblib.dump(pipeline, model_path)
print(f"Model berhasil disimpan ke {model_path}")
