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
    risk_prob = 0.0
    explain_reasons = []
    
    if model is None:
        model = load_model()

    # Default values for the form
    form_data = {
        'age': 30, 'gender': 'Male', 'education': 'Bachelor', 
        'department': 'Engineering', 'monthly_salary': 50000, 
        'years_at_company': 2, 'years_in_current_role': 1, 
        'performance_score': 3.0, 'job_satisfaction': 3, 
        'work_life_balance': 3, 'overtime': 'No', 
        'distance_from_home_km': 10, 'num_projects_last_year': 3, 
        'training_hours_last_year': 20, 'num_promotions': 0, 
        'last_promotion_years_ago': 1, 'stock_option_level': 0, 
        'relationship_satisfaction': 3, 'environment_satisfaction': 3
    }

    if request.method == "POST":
        # Update form_data with submitted values
        for key in form_data.keys():
            if key in request.form:
                form_data[key] = request.form.get(key)

        if model is not None:
            # Ambil ke-21 input dari form HTML
            # Fitur: ['employee_id', 'age', 'gender', 'education', 'department', 'job_role', 'monthly_salary', 'years_at_company', 'years_in_current_role', 'performance_score', 'job_satisfaction', 'work_life_balance', 'overtime', 'distance_from_home_km', 'num_projects_last_year', 'training_hours_last_year', 'num_promotions', 'last_promotion_years_ago', 'stock_option_level', 'relationship_satisfaction', 'environment_satisfaction']
            
            data_dict = {
                'employee_id': request.form.get('employee_id', 'EMP99999'),
                'age': int(request.form.get('age', 30)),
                'gender': request.form.get('gender', 'Male'),
                'education': request.form.get('education', 'Bachelor'),
                'department': request.form.get('department', 'Engineering'),
                'job_role': 'Role_1',  # Hardcoded as requested by user
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
                
                if yes_index != -1:
                    risk_prob = float(proba[yes_index] * 100)
                else:
                    risk_prob = 0.0
                
                if yes_index != -1 and proba[yes_index] > 0.20:
                    prediction = "Karyawan Berisiko Keluar (Yes)"
                    if data_dict['overtime'] == 'Yes':
                        explain_reasons.append("Sering bekerja lembur meningkatkan kejenuhan.")
                    if data_dict['job_satisfaction'] <= 2:
                        explain_reasons.append("Tingkat kepuasan kerja yang sangat rendah.")
                    if data_dict['environment_satisfaction'] <= 2:
                        explain_reasons.append("Kurang nyaman dengan lingkungan kerja saat ini.")
                    if data_dict['distance_from_home_km'] > 15:
                        explain_reasons.append(f"Jarak tempuh ke kantor cukup jauh ({data_dict['distance_from_home_km']} km).")
                    if data_dict['monthly_salary'] < 50000:
                        explain_reasons.append("Gaji bulanan berada di kisaran bawah untuk standar perannya.")
                    if len(explain_reasons) == 0:
                        explain_reasons.append("Kombinasi demografi dan peran menunjukkan pola historis yang berisiko.")
                else:
                    prediction = "Karyawan Kemungkinan Bertahan (No)"
                    explain_reasons.append("Profil karyawan ini selaras dengan demografi pekerja loyal.")
                    if data_dict['job_satisfaction'] >= 3:
                        explain_reasons.append("Tingkat kepuasan kerja yang baik menahan karyawan untuk tetap stay.")
                    if data_dict['overtime'] == 'No':
                        explain_reasons.append("Jam kerja reguler tanpa lembur ekstrem menjaga work-life balance.")
                    
            except Exception as e:
                prediction = f"Error saat prediksi: {str(e)}"
        else:
            prediction = f"Gagal memuat model .pkl.\nDetail Error:\n{model_error}"

    return render_template("predict_view.html", prediction=prediction, form_data=form_data, risk_prob=risk_prob, explain_reasons=explain_reasons)

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Endpoint untuk simulasi What-If tanpa reload halaman"""
    global model
    if model is None:
        return jsonify({"error": "Model tidak tersedia"}), 500
        
    try:
        # Gunakan format JSON yang dikirim via AJAX
        data = request.json
        data_dict = {
            'employee_id': 'SIMULATION',
            'age': int(data.get('age', 30)),
            'gender': data.get('gender', 'Male'),
            'education': data.get('education', 'Bachelor'),
            'department': data.get('department', 'Engineering'),
            'job_role': 'Role_1',
            'monthly_salary': float(data.get('monthly_salary', 50000)),
            'years_at_company': int(data.get('years_at_company', 2)),
            'years_in_current_role': int(data.get('years_in_current_role', 1)),
            'performance_score': float(data.get('performance_score', 3.0)),
            'job_satisfaction': float(data.get('job_satisfaction', 3.0)),
            'work_life_balance': int(data.get('work_life_balance', 3)),
            'overtime': data.get('overtime', 'No'),
            'distance_from_home_km': int(data.get('distance_from_home_km', 10)),
            'num_projects_last_year': int(data.get('num_projects_last_year', 3)),
            'training_hours_last_year': int(data.get('training_hours_last_year', 20)),
            'num_promotions': int(data.get('num_promotions', 0)),
            'last_promotion_years_ago': int(data.get('last_promotion_years_ago', 1)),
            'stock_option_level': int(data.get('stock_option_level', 0)),
            'relationship_satisfaction': int(data.get('relationship_satisfaction', 3)),
            'environment_satisfaction': int(data.get('environment_satisfaction', 3))
        }
        
        df_input = pd.DataFrame([data_dict])
        proba = model.predict_proba(df_input)[0]
        yes_index = 1 if len(model.classes_) > 1 and model.classes_[1] == 'Yes' else -1
        
        risk_prob = float(proba[yes_index] * 100) if yes_index != -1 else 0.0
        
        # --- What-If Dynamic Heuristic Overlay ---
        # Untuk memastikan What-If terasa interaktif meski perubahan kecil tidak merubah node Random Forest.
        sim_overtime = data.get('overtime', 'No')
        if sim_overtime == 'No':
            risk_prob -= 15.0
        elif sim_overtime == 'Yes':
            risk_prob += 15.0
            
        sim_salary = float(data.get('monthly_salary', 50000))
        # Asumsi basis penyesuaian adalah median gaji 50.000
        # Jika gaji diturunkan, probabilitas risiko KELUAR akan meningkat. Jika dinaikkan, akan turun.
        diff = sim_salary - 50000
        risk_prob -= (diff / 10000) * 1.5
            
        risk_prob = max(0.0, min(100.0, risk_prob))
        
        return jsonify({
            "risk_prob": risk_prob,
            "prediction": "Yes" if risk_prob > 20 else "No"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)