## Setup ⚡

```sh
pip install -r requirements.txt
```

## Run
```sh
flask run
```

## Pm2
```sh
pm2 start "flask run -h 0.0.0.0 -p 5000" --name "bot"
```