import fastapi
from fastapi_sqlalchemy import endpoints, models


def test_login_get(session, app, client):
    template = "<html>${title}</html>"
    endpoint = endpoints.LoginEndpoint(secret="s0secret", template=template)

    @app.get("/login")
    async def _get():
        return await endpoint.on_get()

    res = client.get("/login")
    assert res.status_code == 200
    assert res.text == "<html>FastAPI-SQLAlchemy</html>"


def test_login_post(engine, session, app, client):

    # FIXME: hack
    User = models.base.MODEL_MAPPING.get("User")
    if not User:
        class User(models.User):
            __abstract__ = False

    models.BASE.metadata.create_all(engine)
    user = User(username="alice")
    user.password = "test123"
    session.add(user)
    session.commit()
    user = session.merge(user)

    endpoint = endpoints.LoginEndpoint(secret="s0secret")

    @app.post("/login")
    async def _post(
            username: str = fastapi.Form(None),
            password: str = fastapi.Form(None)
    ):
        return await endpoint.on_post(username, password)

    res = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "test123",
        }
    )
    assert res.status_code == 303
    assert res.headers.get("location") == "/"

    data = res.json()
    assert data["id"] == str(user.id)
