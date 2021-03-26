# LONK
For when your links are too lonk.

# Running
To run `uwsgi` for production, run `poetry run uwsgi <options>`, for instance:
```shell
docker run -p 5000:5000 \
  -v $(pwd)/lonk:/opt/lonk/lonk \
  --rm lonk \
  poetry run uwsgi \
    --python-path /opt/lonk \
    -s 0.0.0.0:5000 \
    --mount /=lonk.app:app
```
…of course, you should add more uwsgi options to establish
[sane defaults](https://www.techatbloomberg.com/blog/configuring-uwsgi-production-deployment/)
on a production instance,
but this is just for a self-contained example.

For a development setup, you might want to run:
```shell
docker run -p 5001:5000 \
  -v $(pwd)/lonk:/opt/lonk/lonk \
  -e FLASK_ENV=development \
  --rm lonk \
  poetry run flask run
```
See also [this doc](https://flask.palletsprojects.com/en/1.1.x/cli/)
on how to configure the flask cli.
