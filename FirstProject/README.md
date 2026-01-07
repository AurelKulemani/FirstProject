# Redi Hair Studio (Django + Bootstrap)

Bilingual website (English 🇬🇧 / Albanian 🇦🇱) inspired by modern salon/barbershop layouts.
- Pages: Home, About, Contact
- Dynamic Services from database
- Contact form: validation + saves messages to DB (viewable in Django Admin)
- Responsive (Bootstrap 5)

## 1) Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

## 2) Load sample services (optional)

```bash
python manage.py loaddata core/fixtures/initial_data.json
```

## 3) Create admin user

```bash
python manage.py createsuperuser
```

## 4) Run

```bash
python manage.py runserver
```

Open:
- Website: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Language switch
Use the EN / SQ buttons in the navbar.


## Running the project

```bash
cd backend
python manage.py runserver
```
