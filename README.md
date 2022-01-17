# Document Management Service

## Postman Documentation
- [Review POSTMAN API documentation]

## Swagger Details
- Make sure DEBUG=True in settings.py
- python manage.py runserver 0.0.0.0:8792 
>`Some api(s) show incorrect field type and required fields in the serializer. Go through the Postman documentation`
```bash
http://0.0.0.0:8792/swagger
```
## Open API Documentation
- Make sure DEBUG=True in settings.py 
- python manage.py runserver 0.0.0.0:8792 
>`Some api(s) show incorrect field type and required fields in the serializer. Go through the Postman documentation`
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

## Media File Sample
##### Original file in document
![Original_File](https://drive.google.com/uc?export=view&id=1UZQhKgABZZnIDlGMkbVGe_gW-FDRGxMz "Original File")
##### Edited file uploaded in document
![Updated_File](https://drive.google.com/uc?export=view&id=13bllk1rK8R8_tRy-9TXI5jXfpOZZPMh6 "Updated File")
##### Diff file in documentVersion
![Diff_File](https://drive.google.com/uc?export=view&id=1eHuc0F6sA-YU3seukthleRDRfx4tpy9o "Diff File")

[review postman api documentation]: <https://documenter.getpostman.com/view/4330514/UVXkmaHX>