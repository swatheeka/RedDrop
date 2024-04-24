import sqlite3



def get_normal_range(parameter):
    normal_ranges = {
        'hemoglobin': (13.8, 17.2),  # (lower_bound, upper_bound)
        'pcv': (40, 54),
        'rbc_count': (4.5, 5.9),
        'mcv': (80, 100),
        'mch': (27, 33),
        'mchc': (32, 36),
        'rdw': (11.5, 14.5),
        'tlc': (4500, 11000),
        'nlr': (1,3),
        'platelet_count': (150000, 450000)
    }
    return normal_ranges.get(parameter)

def create_user_table():
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    conn.commit()
    conn.close()

def create_feedback_table():
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        feedback TEXT,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )''')
    conn.commit()
    conn.close()

def create_blood_test_table():
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE total_blood_count')
    cursor.execute('''CREATE TABLE IF NOT EXISTS total_blood_count (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        hemoglobin REAL,
                        pcv REAL,
                        rbc_count REAL,
                        mcv REAL,
                        mch REAL,
                        mchc REAL,
                        rdw REAL,
                        tlc REAL,
                        nlr REAL,
                        platelet_count REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username)   
                    )''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_feedback(username, feedback):
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (username, feedback) VALUES (?, ?)', (username, feedback))
    conn.commit()
    conn.close()

def add_blood_test_result(username, hemoglobin, pcv, rbc_count, mcv, mch, mchc, rdw, tlc, nlr, platelet_count):
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO total_blood_count (username, hemoglobin, pcv, rbc_count, mcv, mch, mchc, rdw, tlc, nlr, platelet_count)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
                   (username, hemoglobin, pcv, rbc_count, mcv, mch, mchc, rdw, tlc, nlr, platelet_count))
    conn.commit()
    conn.close()

def get_blood_test_result(username):
    conn = sqlite3.connect('reddrop.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM total_blood_count WHERE username = ? ORDER BY timestamp DESC''', (username,))    
    result = cursor.fetchone()
    conn.close()
    if result:
        # Extract blood test results from the database
        blood_test_results = {'hemoglobin': result[2],
            'pcv': result[3],
            'rbc_count': result[4],
            'mcv': result[5],
            'mch': result[6],
            'mchc': result[7],
            'rdw': result[8],
            'tlc': result[9],
            'nlr': result[10],
            'platelet_count': result[11]
        }
        return blood_test_results
    else:
        return None

def generate_recommendations(blood_test_results):
    recommendations = []
    if 'hemoglobin' in blood_test_results:
        value = blood_test_results['hemoglobin']
        if value:
            if value < 13.8:
                recommendations.append("Low hemoglobin levels may indicate anemia.")
            if value > 17.2:
                recommendations.append("High hemoglobin levels may indicate dehydration or other underlying conditions.")
        else:
            recommendations.append("No data available for hemoglobin.")
    
    if 'pcv' in blood_test_results:
        value = blood_test_results['pcv']
        if value:
            if value < 40:
                recommendations.append("Low PCV levels may indicate anemia.")
            if value > 54:
                recommendations.append("High PCV levels may indicate dehydration or other underlying conditions.")
        else:
            recommendations.append("No data available for PCV.")
    
    if 'rbc_count' in blood_test_results:
        value = blood_test_results['rbc_count']
        if value:
            if value < 4.5:
                recommendations.append("Low RBC count may indicate anemia.")
            if value > 5.9:
                recommendations.append("High RBC count may indicate dehydration or other underlying conditions.")
        else:
            recommendations.append("No data available for RBC count.")
    
    if 'mcv' in blood_test_results:
        value = blood_test_results['mcv']
        if value:
            if value < 80:
                recommendations.append("Low MCV levels may indicate microcytic anemia.")
            if value > 100:
                recommendations.append("High MCV levels may indicate macrocytic anemia.")
        else:
            recommendations.append("No data available for MCV.")
    
    if 'mch' in blood_test_results:
        value = blood_test_results['mch']
        if value:
            if value < 27:
                recommendations.append("Low MCH levels may indicate microcytic anemia.")
            if value > 33:
                recommendations.append("High MCH levels may indicate macrocytic anemia.")
        else:
            recommendations.append("No data available for MCH.")
    
    if 'mchc' in blood_test_results:
        value = blood_test_results['mchc']
        if value:
            if value < 32:
                recommendations.append("Low MCHC levels may indicate hypochromic anemia.")
            if value > 36:
                recommendations.append("High MCHC levels may indicate hyperchromic anemia.")
        else:
            recommendations.append("No data available for MCHC.")
    
    if 'rdw' in blood_test_results:
        value = blood_test_results['rdw']
        if value:
            if value < 11.5:
                recommendations.append("Low RDW levels may indicate anemia.")
            if value > 14.5:
                recommendations.append("High RDW levels may indicate anemia.")
        else:
            recommendations.append("No data available for RDW.")
    
    if 'tlc' in blood_test_results:
        value = blood_test_results['tlc']
        if value:
            if value < 4500:
                recommendations.append("Low TLC levels may indicate leukopenia.")
            if value > 11000:
                recommendations.append("High TLC levels may indicate leukocytosis.")
        else:
            recommendations.append("No data available for TLC.")
    
    if 'nlr' in blood_test_results:
        value = blood_test_results['nlr']
        if value:
            if value < 1:
                recommendations.append("Low NLR levels may indicate lower risk of inflammation.")
            if value > 3:
                recommendations.append("High NLR levels may indicate higher risk of inflammation.")
        else:
            recommendations.append("No data available for NLR.")
    
    if 'platelet_count' in blood_test_results:
        value = blood_test_results['platelet_count']
        if value:
            if value < 150000:
                recommendations.append("Low platelet count may indicate thrombocytopenia.")
            if value > 450000:
                recommendations.append("High platelet count may indicate thrombocytosis.")
        else:
            recommendations.append("No data available for platelet count.")
    
    return recommendations



