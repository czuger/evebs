"""Tests for _compute_potentials (pure) and _generate_potential_assets (DB)."""
import pytest

from esi.download_my_blueprints import _compute_potentials, _generate_potential_assets
from tests.factories import make_item, make_bpc_asset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _acts(can_copy=False, invention_products=None):
    return {'can_copy': can_copy, 'invention_products': invention_products or []}


def _potentials(db, user):
    from evebs.models import BpcAsset
    return {a.eve_item_id: a.potential_type
            for a in BpcAsset.query.filter_by(user_id=user.id, is_potential=True).all()}


# ---------------------------------------------------------------------------
# _compute_potentials — pure unit tests, no DB needed
# ---------------------------------------------------------------------------

class TestComputePotentials:
    def test_no_assets_gives_empty(self):
        assert _compute_potentials(set(), set(), {}) == {}

    def test_bpo_can_copy_no_bpc(self):
        acts = {100: _acts(can_copy=True)}
        assert _compute_potentials({100}, set(), acts) == {100: 'copy'}

    def test_bpo_already_has_real_bpc_no_copy_potential(self):
        acts = {100: _acts(can_copy=True)}
        assert _compute_potentials({100}, {100}, acts) == {}

    def test_bpo_cannot_copy_no_potential(self):
        acts = {100: _acts(can_copy=False)}
        assert _compute_potentials({100}, set(), acts) == {}

    def test_bpo_no_activities_no_potential(self):
        assert _compute_potentials({100}, set(), {}) == {}

    # --- invention from real BPC ---

    def test_real_bpc_invention_gives_invent(self):
        acts = {100: _acts(invention_products=[200])}
        result = _compute_potentials(set(), {100}, acts)
        assert result == {200: 'invent'}

    # --- invention from BPO only ---

    def test_bpo_only_invention_gives_copy_invent(self):
        acts = {100: _acts(invention_products=[200])}
        result = _compute_potentials({100}, set(), acts)
        assert result == {200: 'copy_invent'}

    # --- BPO + real BPC: invent wins ---

    def test_bpo_and_bpc_invention_gives_invent(self):
        acts = {100: _acts(can_copy=True, invention_products=[200])}
        result = _compute_potentials({100}, {100}, acts)
        assert result == {200: 'invent'}

    def test_invent_beats_copy_invent_regardless_of_queue_order(self):
        # Two paths to 300: one via real BPC (invent), one via BPO (copy_invent)
        acts = {
            100: _acts(invention_products=[300]),   # real BPC → invent
            200: _acts(invention_products=[300]),   # real BPO only → copy_invent
        }
        result = _compute_potentials({200}, {100}, acts)
        assert result[300] == 'invent'

    # --- BPO with copy+invent combo ---

    def test_bpo_copy_and_invent(self):
        acts = {100: _acts(can_copy=True, invention_products=[200])}
        result = _compute_potentials({100}, set(), acts)
        assert result == {100: 'copy', 200: 'copy_invent'}

    # --- already owns the target ---

    def test_already_owns_t2_bpc_no_potential(self):
        acts = {100: _acts(invention_products=[200])}
        result = _compute_potentials(set(), {100, 200}, acts)
        assert 200 not in result

    def test_already_owns_t2_bpo_no_potential(self):
        acts = {100: _acts(invention_products=[200])}
        result = _compute_potentials({100, 200}, set(), acts)
        assert 200 not in result

    # --- transitive chains ---

    def test_transitive_bpc_chain_all_invent(self):
        # T1 BPC → T2 invent → T3 invent (T2 is a BPC, so T3 is also 'invent')
        acts = {
            100: _acts(invention_products=[200]),
            200: _acts(invention_products=[300]),
        }
        result = _compute_potentials(set(), {100}, acts)
        assert result == {200: 'invent', 300: 'invent'}

    def test_transitive_bpo_chain_all_copy_invent(self):
        # T1 BPO only → T2 copy_invent → T3 copy_invent
        acts = {
            100: _acts(can_copy=True, invention_products=[200]),
            200: _acts(invention_products=[300]),
        }
        result = _compute_potentials({100}, set(), acts)
        assert result == {100: 'copy', 200: 'copy_invent', 300: 'copy_invent'}

    def test_transitive_upgrade_mid_chain(self):
        # T1 BPO only → T2 copy_invent; T2 also reachable via T0 real BPC → T2 invent
        # The 'invent' path should win and T2's own products should be 'invent'
        acts = {
            100: _acts(invention_products=[200]),   # BPO only
            50:  _acts(invention_products=[200]),   # real BPC
            200: _acts(invention_products=[300]),
        }
        result = _compute_potentials({100}, {50}, acts)
        assert result[200] == 'invent'
        assert result[300] == 'invent'

    # --- cycle guard ---

    def test_cycle_does_not_infinite_loop(self):
        # A → B → A
        acts = {
            100: _acts(invention_products=[200]),
            200: _acts(invention_products=[100]),
        }
        result = _compute_potentials(set(), {100}, acts)
        assert 200 in result
        assert result[200] == 'invent'
        assert 100 not in result   # 100 is already real, skipped


# ---------------------------------------------------------------------------
# _generate_potential_assets — integration tests with real DB
# ---------------------------------------------------------------------------

class TestGeneratePotentialAssets:

    def _make_bp_item(self, db, item_id, slug):
        return make_item(db, item_id=item_id, slug=slug)

    def _make_real_bpo(self, db, user, item):
        return make_bpc_asset(db, user, item, quantity=1, is_blueprint_copy=False)

    def _make_real_bpc(self, db, user, item):
        return make_bpc_asset(db, user, item, quantity=1, is_blueprint_copy=True)

    # bp_to_produced maps blueprintTypeID → produced_type_id.
    # Tests use the same numeric ID for both (simplest valid setup, since
    # BpcAsset.eve_item_id FK only requires the EveItem to exist).

    def test_inserts_copy_potential(self, db, user):
        item = self._make_bp_item(db, 100, 'bp-100')
        self._make_real_bpo(db, user, item)
        db.session.commit()

        acts = {100: _acts(can_copy=True)}
        _generate_potential_assets(user, acts, {100: 100})

        result = _potentials(db, user)
        assert result == {100: 'copy'}

    def test_inserts_copy_invent_when_bpo_only(self, db, user):
        item = self._make_bp_item(db, 100, 'bp-100')
        make_item(db, item_id=200, slug='bp-200')
        self._make_real_bpo(db, user, item)
        db.session.commit()

        acts = {100: _acts(can_copy=True, invention_products=[200])}
        _generate_potential_assets(user, acts, {100: 100, 200: 200})

        result = _potentials(db, user)
        assert result.get(200) == 'copy_invent'

    def test_inserts_invent_when_real_bpc_exists(self, db, user):
        item = self._make_bp_item(db, 100, 'bp-100')
        make_item(db, item_id=200, slug='bp-200')
        self._make_real_bpc(db, user, item)
        db.session.commit()

        acts = {100: _acts(invention_products=[200])}
        _generate_potential_assets(user, acts, {100: 100, 200: 200})

        result = _potentials(db, user)
        assert result == {200: 'invent'}

    def test_skips_entry_with_no_produced_type(self, db, user):
        item = self._make_bp_item(db, 100, 'bp-100')
        self._make_real_bpo(db, user, item)
        db.session.commit()

        # Blueprint 100 has no manufacturing activity → not in bp_to_produced
        acts = {100: _acts(can_copy=True)}
        _generate_potential_assets(user, acts, {})

        result = _potentials(db, user)
        assert result == {}

    def test_stale_potentials_are_replaced(self, db, user):
        item = self._make_bp_item(db, 100, 'bp-100')
        make_item(db, item_id=200, slug='bp-200')
        make_item(db, item_id=300, slug='bp-300')
        self._make_real_bpc(db, user, item)
        db.session.commit()

        # First run: invents 200
        _generate_potential_assets(user, {100: _acts(invention_products=[200])}, {100: 100, 200: 200})

        # Second run: activities changed, now invents 300 instead
        _generate_potential_assets(user, {100: _acts(invention_products=[300])}, {100: 100, 300: 300})

        result = _potentials(db, user)
        assert 200 not in result
        assert result.get(300) == 'invent'

    def test_does_not_generate_potential_for_already_owned(self, db, user):
        item_100 = self._make_bp_item(db, 100, 'bp-100')
        item_200 = self._make_bp_item(db, 200, 'bp-200')
        self._make_real_bpc(db, user, item_100)
        self._make_real_bpo(db, user, item_200)  # user already owns T2
        db.session.commit()

        acts = {100: _acts(invention_products=[200])}
        _generate_potential_assets(user, acts, {100: 100, 200: 200})

        result = _potentials(db, user)
        assert 200 not in result

    def test_two_users_do_not_interfere(self, db, user):
        from evebs.models import User
        from datetime import datetime, timedelta

        other = User(uid='999', name='Other', provider='eve_online_sso',
                     token='t2', renew_token='r2',
                     expires_on=datetime.utcnow() + timedelta(hours=1),
                     initialization_finalized=True)
        db.session.add(other)

        item = self._make_bp_item(db, 100, 'bp-100')
        make_item(db, item_id=200, slug='bp-200')
        self._make_real_bpc(db, user, item)
        db.session.commit()

        acts = {100: _acts(invention_products=[200])}
        bp_to_produced = {100: 100, 200: 200}
        _generate_potential_assets(user, acts, bp_to_produced)
        _generate_potential_assets(other, acts, bp_to_produced)

        from evebs.models import BpcAsset
        user_pots = BpcAsset.query.filter_by(user_id=user.id, is_potential=True).count()
        other_pots = BpcAsset.query.filter_by(user_id=other.id, is_potential=True).count()
        assert user_pots == 1
        assert other_pots == 0
