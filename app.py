from flask import Flask, render_template, request, jsonify
import os
import joblib
import pandas as pd
import json

app = Flask(__name__)

# --- FUNGSI MEMUAT MODEL AI ---
def load_model():
    # Menggunakan model baru
    MODEL_PATH = "model/attrition_prediction_model.pkl" 
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        return None
    except Exception as e:
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
    prediction = None

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
            
            # Prediksi
            try:
                pred = model.predict(df_input)[0]
                if str(pred).strip().lower() in ['1', 'yes', 'true', 'berisiko']:
                    # The original dataset 'attrition' column is 'Yes'/'No'
                    prediction = "Karyawan Berisiko Keluar (Yes)"
                elif str(pred).strip().lower() in ['0', 'no', 'false', 'bertahan']:
                    prediction = "Karyawan Kemungkinan Bertahan (No)"
                else:
                    prediction = f"Hasil: {pred}"
            except Exception as e:
                prediction = f"Error saat prediksi: {str(e)}"
        else:
            prediction = "Gagal memuat model .pkl. Pastikan scikit-learn sudah versi 1.6.1"

    return render_template("predict_view.html", prediction=prediction)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)