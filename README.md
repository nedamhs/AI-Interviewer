##Setup Instructions

1) Install Dependencies:
```
pip install -r requirements.txt
npm install
```

2) Build packages
```
npm run build
```

3) Generate API Schema
```
python ./manage.py spectacular --color --file schema.yml
```

4) Run python server
```
python ./manage.py runserver
```

5) Access API documentation, by navigating to:
```
http://localhost:8000/api/documentation
```