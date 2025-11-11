from post_service import PostService

def test_insert_and_get_latest():
    service = PostService()
    service.add_post("img.png", "hello", "negar")

    latest = service.get_latest_post()

    assert latest[0] == "img.png"
    assert latest[1] == "hello"
    assert latest[2] == "negar"
