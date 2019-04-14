import main


def test_index():
    main.db.create_all()

    main.app.testing = True
    client = main.app.test_client()

    r = client.get('/', environ_base={'REMOTE_ADDR': '127.0.0.1'})
    assert r.status_code == 200
    assert '127.0' in r.data.decode('utf-8')
