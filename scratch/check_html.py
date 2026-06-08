from app import app

with app.app_context():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['role'] = 'admin'
            sess['user_name'] = 'Administrator'
        response = client.get('/medicines')
        html = response.data.decode('utf-8')
        print("Occurrences:")
        for i, line in enumerate(html.splitlines()):
            if 'editMedModal' in line or 'restockModal' in line:
                print(f"Line {i+1}: {line.strip()}")
