from datetime import datetime

from modapi.rest.holds.biz_logic import hold_biz_logic, release_by_mod_biz_logic
from modapi.rest.holds.domain import WORKING, HoldReleaseLogicRes, ON_HOLD

from modapi.auth import User


mod_user = User(user_id=1111111, name='M The Mod', username='mtm', is_moderator=True,
                is_admin=False, moderated_categories=['cs.LG'], email='a@example.com')

admin_user = User(user_id=99999, name='A The Admin',
                  username='ata', is_admin=True, email='ab@example.com')

sub_id = 3434343

    
def test_cannot_release_no_sub():
    result = release_by_mod_biz_logic(None, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), False)
    assert result.status_code == 404

def test_cannot_release_locked(mocker):
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason=hr
    exists.submit_time=datetime(2010, 5, 13, 0, 0, 0)
    exists.sticky_status=False
    exists.is_locked=True
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, None, True)
    assert result.status_code == 403
    result = release_by_mod_biz_logic(exists, 1234, mod_user, None, False)
    assert result.status_code == 403

    result = release_by_mod_biz_logic(exists, 1234, admin_user, None, True)
    assert result.status_code == 403
    result = release_by_mod_biz_logic(exists, 1234, admin_user, None, False)
    assert result.status_code == 403
    
    
def test_release_mod_hold_notfreeze(mocker):
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason=hr
    exists.submit_time=datetime(2010, 5, 13, 0, 0, 0)
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), False)
    assert result
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.release_to_status == 1

def test_release_mod_hold_freeze(mocker):
    FREEZE=True
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason=hr
    exists.submit_time=datetime(2010, 5, 13, 0, 0, 0)
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), FREEZE)
    assert result
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.release_to_status == 4


def test_release_bad_user(mocker):
    bad_user = mocker.patch('modapi.tables.arxiv_models.TapirUsers')
    bad_user.user_id=1111111
    bad_user.name='JustANonModUser'
    bad_user.username='mjanmu'
    bad_user.is_moderator=False
    bad_user.is_admin=False
    bad_user.moderated_categories=[]

    res = release_by_mod_biz_logic(None, 1234, bad_user, None, False)
    assert res
    assert res.status_code == 403

    res = release_by_mod_biz_logic(None, 1234, None, None, False)
    assert res
    assert res.status_code == 403

    res = hold_biz_logic(None, None, 1234, bad_user)
    assert res
    assert res.status_code == 403

    res = hold_biz_logic(None, None, 1234, None)
    assert res
    assert res.status_code == 403


def test_mod_cannot_release_admin_hold(mocker):
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason=None
    hr.user_id=1234
    hr.type="admin"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason =hr
    exists.submit_time='bogus-time'
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, None, True)
    assert result
    assert result.status_code == 403

    result = release_by_mod_biz_logic(exists, 1234, mod_user, None, False)
    assert result
    assert result.status_code == 403


def test_release_legacy_hold(mocker):
    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[]
    exists.hold_reason=[]
    exists.submit_time=datetime.now()
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, admin_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), False)
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.paper_id == 'submit/1234'
    assert "Release: legacy hold to submitted" in result.visible_comments

def test_admin_cannot_release_no_primary(mocker):
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason =hr
    exists.submit_time='bogus-time'
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification=None

    result = release_by_mod_biz_logic(exists, 1234, admin_user,
                                      lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert result
    assert result.status_code > 400

    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="nonresearch"
    hr.user_id=1234
    hr.type="admin"

    exists.hold_reasons=[hr]
    exists.hold_reason =hr

    result = release_by_mod_biz_logic(exists, 1234, admin_user,
                                      lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert result
    assert result.status_code > 400


def test_mod_cannot_release_no_primary(mocker):
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason =hr
    exists.submit_time='bogus-time'
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification=None

    result = release_by_mod_biz_logic(exists, 1234, mod_user,
                                      lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert result
    assert result.status_code > 400


def test_cannot_release_not_held(mocker):
    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=WORKING
    exists.submit_time='bogus-time'
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification=None
    result = release_by_mod_biz_logic(exists, 1234, admin_user,
                                      lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert result.status_code > 400

    
def test_relase_of_autohold(mocker):
    """Release of sub with auto-hold should clear the mod hold reason but leave the 
    submission in a legacy hold"""
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason=hr
    exists.submit_time=datetime(2010, 5, 13, 0, 0, 0)
    exists.sticky_status=False
    exists.auto_hold=True
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.clear_reason == True
    assert result.release_to_status == 2

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), False)
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.clear_reason == True
    assert result.release_to_status == 2


def test_relase_to_working(mocker):
    """Release of sub that should go to working status"""
    hr = mocker.patch('modapi.tables.arxiv_models.SubmissionHoldReason')
    hr.reason="discussion"
    hr.user_id=1234
    hr.type="mod"

    exists = mocker.patch('modapi.tables.arxiv_models.Submissions')
    exists.status=ON_HOLD
    exists.hold_reasons=[hr]
    exists.hold_reason=hr
    exists.submit_time=None
    exists.sticky_status=False
    exists.auto_hold=False
    exists.is_locked=False
    exists.doc_paper_id=None
    exists.primary_classification = 'cs.OH'

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), True)
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.clear_reason == True
    assert result.release_to_status == 0

    result = release_by_mod_biz_logic(exists, 1234, mod_user, lambda _: datetime.fromisoformat("2010-05-14T00:00:00+00:00"), False)
    assert isinstance(result, HoldReleaseLogicRes)
    assert result.clear_reason == True
    assert result.release_to_status == 0
