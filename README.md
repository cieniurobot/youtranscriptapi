# Youtube transcripion API
Service can load youtube video transcription by video id.


## Requirements:
- Python 3.6
- docker
- docker-compose
- pipenv


Run locally:
```bash
$ export FLASK_APP=app.py
$ flask run
 * Running on http://127.0.0.1:5000/
```

Run by docker-compose:
```bash
docker-compose up
```

Run build using docker compose:
```bash
$ fab build
$ cd build
$ docker-compose up --build --force-recreate
```

Deploy to server by ssh:
```bash
$ fab deploy --hosts <here host which is configured in ~/.ssh/config>
```

## Usage
To get JWT token use:
```
POST /auth HTTP/1.1
Host: vps696120.ovh.net:8001
Content-Type: application/json
Cache-Control: no-cache
Postman-Token: 2f27731c-1c05-160c-0db4-6f5f0547258b

{
	"username": "test",
	"password": "test"
}
```

Get transcription by youtube video ID:
```
GET /transcript/37wZ2oIzuR4 HTTP/1.1
Host: vps696120.ovh.net:8001
Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NzQzNTE5NjAsImlhdCI6MTU3NDM1MTY2MCwibmJmIjoxNTc0MzUxNjYwLCJpZGVudGl0eSI6MX0.hkcS1SCX8JQa8MLdbNOfov0aVT2gYVxHQH6TidRaZNE

```
