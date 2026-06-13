from flask import Flask, render_template, request, jsonify
import os
import joblib
import pandas as pd
import json

app = Flask(__name__)

import traceback

model_error = None

# --- FUNGSI MEMUAT MODEL AI ---
def load_model():
    global model_error
    # Gunakan path absolut untuk menghindari FileNotFoundError jika cwd berbeda
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "model", "attrition_prediction_model.pkl")
    try:
        import sklearn
        print("Using sklearn version:", sklearn.__version__)
        model = joblib.load(MODEL_PATH)
        model_error = None
        return model
    except Exception as e:
        import sklearn
        model_error = f"scikit-learn version: {sklearn.__version__}\n{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"Error loading model: {e}")
        return None

model = load_model()

@app.route('/')
def home():
    # Redirect ke dashboard karena ringkasan dipindah ke dashboard
    from flask import redirect
    return redirect('/dashboard')

@app.route('/dashboard')
def get_dashboard():
    return render_template('dashboard_view.html')

@app.route('/api/dashboard-summary')
def get_dashboard_summary():
    try:
        with open('model/dashboard_summary.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- HALAMAN FORM PREDIKSI ---
@app.route('/predict', methods=['GET', 'POST'])
def predict_view():
    global model, model_error
    prediction = None
    
    if model is None:
        model = load_model()

    if request.method == "POST":
        if model is not None:
            # Ambil ke-21 input dari form HTML
            # Fitur: ['employee_id', 'age', 'gender', 'education', 'department', 'job_role', 'monthly_salary', 'years_at_company', 'years_in_current_role', 'performance_score', 'job_satisfaction', 'work_life_balance', 'overtime', 'distance_from_home_km', 'num_projects_last_year', 'training_hours_last_year', 'num_promotions', 'last_promotion_years_ago', 'stock_option_level', 'relationship_satisfaction', 'environment_satisfaction']
            
            data_dict = {
                'employee_id': request.form.get('employee_id', 'EMP99999'),
                'age': int(request.form.get('age', 30)),
                'gender': request.form.get('gender', 'Male'),
                'education': request.form.get('education', 'Bachelor'),
                'department': request.form.get('department', 'Engineering'),
                'job_role': request.form.get('job_role', 'Role_1'),
                'monthly_salary': float(request.form.get('monthly_salary', 50000)),
                'years_at_company': int(request.form.get('years_at_company', 2)),
                'years_in_current_role': int(request.form.get('years_in_current_role', 1)),
                'performance_score': float(request.form.get('performance_score', 3.0)),
                'job_satisfaction': float(request.form.get('job_satisfaction', 3.0)),
                'work_life_balance': int(request.form.get('work_life_balance', 3)),
                'overtime': request.form.get('overtime', 'No'),
                'distance_from_home_km': int(request.form.get('distance_from_home_km', 10)),
                'num_projects_last_year': int(request.form.get('num_projects_last_year', 3)),
                'training_hours_last_year': int(request.form.get('training_hours_last_year', 20)),
                'num_promotions': int(request.form.get('num_promotions', 0)),
                'last_promotion_years_ago': int(request.form.get('last_promotion_years_ago', 1)),
                'stock_option_level': int(request.form.get('stock_option_level', 0)),
                'relationship_satisfaction': int(request.form.get('relationship_satisfaction', 3)),
                'environment_satisfaction': int(request.form.get('environment_satisfaction', 3))
            }

            df_input = pd.DataFrame([data_dict])
            
            # Prediksi dengan custom threshold (karena dataset imbalanced)
            try:
                # Dapatkan probabilitas untuk kelas 'No' (0) dan 'Yes' (1)
                proba = model.predict_proba(df_input)[0]
                
                # Asumsi index 1 adalah kelas 'Yes' (berisiko keluar)
                # Model memiliki bias tinggi ke kelas 'No', jadi kita turunkan threshold-nya
                # Jika probabilitas 'Yes' lebih besar dari 20%, kita anggap berisiko
                yes_index = 1 if len(model.classes_) > 1 and model.classes_[1] == 'Yes' else -1
                
                if yes_index != -1 and proba[yes_index] > 0.20:
                    prediction = "Karyawan Berisiko Keluar (Yes)"
                else:
                    prediction = "Karyawan Kemungkinan Bertahan (No)"
                    
            except Exception as e:
                prediction = f"Error saat prediksi: {str(e)}"
        else:
            prediction = f"Gagal memuat model .pkl.\nDetail Error:\n{model_error}"

    return render_template("predict_view.html", prediction=prediction)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)