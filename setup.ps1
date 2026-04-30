py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
py manage.py migrate
py manage.py runserver