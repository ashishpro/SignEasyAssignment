# Document Management Service


## Postman Documentation
- [Review POSTMAN API documentation]

## Swagger Details
- Make sure DEBUG=True in settings.py
- python manage.py runserver 0.0.0.0:8792 
>`Some api(s) show incorrect field type and required fields in the serializer. Go through the Postman or PDF documentation`
```bash
http://0.0.0.0:8792/swagger
```
## Open API Documentation
- Make sure DEBUG=True in settings.py 
- python manage.py runserver 0.0.0.0:8792 
>`Some api(s) show incorrect field type and ?required fields in the serializer. Go through the Postman or PDF documentation`
```bash
http://0.0.0.0:8792/redoc
```

## Docker Setup
>Make sure docker and docker-compose are pre-installed

- build Dockerfile

```bash 
docker-compose -d build
```

- create and run container

```bash
docker-compose up -d
```

- stop docker-compose
```bash
docker-compose stop
```

[review postman api documentation]: <https://documenter.getpostman.com/view/4330514/UVXkmaHX>