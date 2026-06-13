import re

filepath = r'c:\laragon\www\UASDs\templates\predict_view.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace number inputs
for field in ['age', 'distance_from_home_km', 'monthly_salary', 'years_at_company', 'years_in_current_role', 'num_projects_last_year', 'training_hours_last_year', 'num_promotions', 'last_promotion_years_ago']:
    # e.g., name="age" value="30"
    html = re.sub(fr'name="{field}" value="\d+"', f'name="{field}" value="{{{{ form_data.{field} }}}}"', html)

# 2. Replace range inputs and their outputs
for field in ['performance_score', 'job_satisfaction', 'environment_satisfaction', 'relationship_satisfaction', 'work_life_balance', 'stock_option_level']:
    # Replace value="3.0" or similar in the input tag
    html = re.sub(fr'name="{field}"(.*?)value="[\d\.]+"', f'name="{field}"\\1value="{{{{ form_data.{field} }}}}"', html)
    # The output tag is right below it
    html = re.sub(fr'(name="{field}".*?mt-2">\s*<output[^>]*>)[\d\.]+(</output>)', fr'\1{{{{ form_data.{field} }}}}\2', html, flags=re.DOTALL)

# 3. Replace select options (remove hardcoded ' selected' first)
html = html.replace(' selected>', '>')

selects = {
    'gender': ['Male', 'Female', 'Other'],
    'education': ['High School', 'Bachelor', 'Master', 'PhD'],
    'department': ['Engineering', 'Sales', 'R&D', 'HR', 'Finance', 'Marketing', 'Operations', 'Legal'],
    'overtime': ['No', 'Yes']
}

for select_name, options in selects.items():
    for val in options:
        html = html.replace(f'<option value="{val}">', f'<option value="{val}" {{% if form_data.{select_name} == "{val}" %}}selected{{% endif %}}>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)
print('Patched predict_view.html successfully.')
