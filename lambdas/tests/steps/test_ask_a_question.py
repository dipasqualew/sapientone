from pytest_bdd import scenario


FEATURE = __file__.split("/")[-1][5:-3] + ".feature"


@scenario(FEATURE, "Unauthenticated users can't ask questions")
def test_add_text_and_metadata_to_an_existing_index():
    pass


@scenario(FEATURE, "Authenticated users can ask questions")
def test_authenticated_users_can_ask_questions():
    pass
