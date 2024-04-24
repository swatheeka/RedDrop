from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import *

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change this to a secure random value in production

create_user_table()
create_feedback_table()
create_blood_test_table()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        if get_user_by_username(username):
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        create_user(username, password)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']
    
    user = get_user_by_username(username)
    if user and user[2] == password:  # user[2] is the password stored in the database
        session['username'] = username  # Add username to the session
        flash('Login successful', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard page after successful login
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))




@app.route('/dashboard')
def dashboard():        
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('index'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_text = request.form['feedback']
        if feedback_text:
            add_feedback(session['username'], feedback_text)  # Assuming feedback is stored in the database
            flash('Feedback submitted successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please provide feedback', 'error')
    return render_template('feedback.html')

# Ailment Based Tests route
@app.route('/ailment_tests')
def ailment_tests():
    if 'username' in session:
        # Add your logic for generating and displaying ailment-based tests
        return render_template('ailment_tests.html')
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('index'))

# General Blood Test Report route
@app.route('/general_report', methods=['GET', 'POST'])
def general_report():
    if 'username' in session:
        if request.method == 'POST':
            # Get blood test results from the form
            hemoglobin = request.form.get('hemoglobin')
            pcv = request.form.get('pcv')
            rbc_count = request.form.get('rbc_count')
            mcv = request.form.get('mcv')
            mch = request.form.get('mch')
            mchc = request.form.get('mchc')
            rdw = request.form.get('rdw')
            tlc = request.form.get('tlc')
            nlr = request.form.get('nlr')
            platelet_count = request.form.get('platelet_count')
            # Add the blood test results to the database
            add_blood_test_result(session['username'], hemoglobin, pcv, rbc_count, mcv, mch, mchc, rdw, tlc, nlr, platelet_count)
            flash('Blood test results submitted successfully', 'success')
            return redirect(url_for('blood_test_result'))
        return render_template('general_report.html')
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('index'))


@app.route('/blood_test_result')
def blood_test_result():
    if 'username' in session:
        blood_test_results = get_blood_test_result(session['username'])
        
        result_table = {}
        for parameter, value in blood_test_results.items():
            if value:
                normal_range = get_normal_range(parameter)
                if normal_range is not None:
                    low, high = normal_range
                    if low <= value <= high:
                        status = 'Normal'
                    elif value < low:
                        status = 'Low'
                    else:
                        status = 'High'
                else:
                    status = 'Data not given'
                
                result_table[parameter] = {'value': value, 'status': status, 'expected_range': normal_range}
        
        filtered_results = {parameter: value for parameter, value in blood_test_results.items() if value}
        recommendations = generate_recommendations(filtered_results)
        
        return render_template('blood_test_result.html', results=result_table, recommendations=recommendations)
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('index'))

@app.route('/cholesterol_results', methods=['GET', 'POST'])
def cholesterol_results():
    if request.method == 'POST':
        # Retrieve form data
        gender = request.form.get('gender')
        total_cholesterol = request.form.get('total_cholesterol')
        triglycerides = request.form.get('triglycerides')
        hdl_cholesterol = request.form.get('hdl_cholesterol')
        ldl_cholesterol = request.form.get('ldl_cholesterol')
        vldl_cholesterol = request.form.get('vldl_cholesterol')
        non_hdl_cholesterol = request.form.get('non_hdl_cholesterol')
        
        # Create dictionary to store form data
        form_data = {
            'Gender': gender,
            'Total Cholesterol (mg/dL)': total_cholesterol,
            'Triglycerides (mg/dL)': triglycerides,
            'HDL Cholesterol (mg/dL)': hdl_cholesterol,
            'LDL Cholesterol (mg/dL)': ldl_cholesterol,
            'VLDL Cholesterol (mg/dL)': vldl_cholesterol,
            'Non-HDL Cholesterol (mg/dL)': non_hdl_cholesterol
        }
        
        # Filter out blank values
        form_data = {key: value for key, value in form_data.items() if value.strip()}
        
        # Check if any form data is provided
        if not form_data:
            return render_template('cholesterol_results.html', error_message="Please fill in at least one parameter.")
        
        # Process form data
        results = {}
        for parameter, value in form_data.items():
            if parameter == 'Gender':
                continue  # Skip processing gender
            value = float(value)
            status = get_status(parameter, value)
            range_value = get_range(parameter, gender)
            results[parameter] = {'value': value, 'status': status, 'range': range_value}
        
        # Generate recommendations
        recommendations = generate_cholesterol_recommendations(results)
        
        return render_template('cholesterol_results_page.html', results=results, recommendations=recommendations)
    
    return render_template('cholesterol_test.html')

def get_status(parameter, value):
    if parameter == 'HDL Cholesterol (mg/dL)':
        return 'Normal' if value >= 40 else 'Low'
    elif parameter == 'Gender':
        return None  # Gender doesn't have a status
    else:
        # Add status determination logic for other parameters if needed
        return 'Normal' if value <= 200 else 'High'

def get_range(parameter, gender):
    if parameter == 'Total Cholesterol (mg/dL)':
        return '< 200 mg/dL'
    elif parameter == 'Triglycerides (mg/dL)':
        return '< 150 mg/dL'
    elif parameter == 'HDL Cholesterol (mg/dL)':
        if gender == 'M':
            return 'Men: > 40 mg/dL <br> Women: > 50 mg/dL'
        else:
            return 'Women: > 50 mg/dL <br> Men: > 40 mg/dL'
    elif parameter == 'LDL Cholesterol (mg/dL)':
        return '< 130 mg/dL'
    elif parameter == 'VLDL Cholesterol (mg/dL)':
        return '5-40 mg/dL'
    elif parameter == 'Non-HDL Cholesterol (mg/dL)':
        return '< 130 mg/dL'
    else:
        return None


def generate_cholesterol_recommendations(results):
    recommendations = []
    for parameter, data in results.items():
        if data['status'] == 'High':
            recommendations.append(f"Elevated {parameter} levels are associated with increased cardiovascular risk.")
        elif data['status'] == 'Low':
            recommendations.append(f"Low {parameter} levels may indicate a lower risk of cardiovascular disease.")
    return recommendations


if __name__ == '__main__':
    app.run(debug=True)
