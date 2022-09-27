import pytest

from modapi import userstore

@pytest.mark.asyncio
async def test_userstore(get_test_db):
    db = next(get_test_db())
    user = await userstore.getuser(-1, db)
    assert user is None

    brandon = await userstore.getuser(246231, db)
    assert brandon
    assert brandon.is_moderator
    assert 'q-bio.NC' in brandon.moderated_categories

    nobody = await userstore.getuser_by_nick('fakename-should-not-be-in-db', db)
    assert nobody is None

    lowjack = await userstore.getuser_by_nick('lowjack', db)
    assert lowjack

    # get from cache
    lowjack = await userstore.getuser_by_nick('lowjack', db)
    assert lowjack

    assert userstore.invalidate_user(246231)
    assert not userstore.invalidate_user(246231)

@pytest.mark.asyncio
async def test_by_email(get_test_db):
    db = next(get_test_db())
    user = await userstore.get_user_by_email('no-mail@example.com', db)
    assert user
    
    user = await userstore.get_user_by_email('other-no-mail@example.com', db)
    assert user
    
    user = await userstore.get_user_by_email('no-mailx234@example.com', db)
    assert user
    
    user = await userstore.get_user_by_email('no-mail-rw@example.com', db)
    assert user
    
    user = await userstore.get_user_by_email('no-mail-randomreader@example.com', db)
    assert user
    
    user = await userstore.get_user_by_email('qa-tools-sa@arxiv-proj.iam.gserviceaccount.com', db)
    assert user
    
    
@pytest.mark.asyncio
async def test_archives(get_test_db):
    db = next(get_test_db())
    user = await userstore.getuser(9999, db)
    assert user.moderated_archives ==  ['astro-ph', 'cond-mat', 'physics']
    assert user.moderated_categories == ['astro-ph.HE']
