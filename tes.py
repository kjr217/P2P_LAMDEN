import unittest
from contracting.client import ContractingClient
from contracting.stdlib.bridge.time import Datetime

client = ContractingClient()

with open('./p2p_contract.py') as f:
    code = f.read()
    client.submit(code, name='p2p_contract')


class MyTestCase(unittest.TestCase):


    # create bet tests

    def test_create_bet_min_bet_fail(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.create_bet(
                bet_id=bet_id,
                amount=20,
                opposing_amount=-40,
                title="Test cases",
                deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
            ))

    def test_create_bet_existing_id(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0))

        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.create_bet(
                bet_id=bet_id,
                amount=20,
                opposing_amount=40,
                title="Test cases",
                deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
            ))

    def test_create_bet(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )

        print(str(p2p_contract.quick_read('bet_names', 'names')))
        print(str(p2p_contract.quick_read(variable='bets', key=bet_id + ':amount_left')))
        print(str(p2p_contract.quick_read(variable='bets', key=bet_id + ':title')))
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 470)

    def test_create_bet_insufficient_funds(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.create_bet(
                bet_id=bet_id,
                amount=500,
                opposing_amount=40,
                title="Test cases",
                deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
            ))

    # transfer ownership tests
    def test_transfer_ownership(self):
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.transfer_ownership(
            new_owner='you'
        )

        self.assertEqual(p2p_contract.quick_read('owner'), 'you')

        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.transfer_ownership(
            new_owner='me'
        )
        self.assertEqual(p2p_contract.quick_read('owner'), 'me')

    def test_transfer_ownership_impostor(self):
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.transfer_ownership(
                new_owner='you'
            ))

    # validator tests
    def test_validator_success(self):
        # 0 for false, 1 for true
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.assign_validator(
            validator='you',
            revoke=0
        )

        self.assertEqual(p2p_contract.quick_read(variable='validators', key='list'), ['me', 'you'])

        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.assign_validator(
            validator='you',
            revoke=1
        )
        self.assertEqual(p2p_contract.quick_read(variable='validators', key='list'), ['me'])

    def test_validator_not_owner(self):
        # 0 for false, 1 for true
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')

        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.assign_validator(
                validator='you',
                revoke=0
            ))

    # settings tests
    def test_settings_success(self):
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.change_settings(
            setting='min_bet',
            new_value=20
        )

        self.assertEqual(p2p_contract.quick_read(variable='settings', key='min_bet'), 20)

    def test_settings_not_owner(self):
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')

        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.change_settings(
                setting='min_bet',
                new_value=30
            ))

    def test_settings_not_setting(self):
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')

        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.change_settings(
                setting='kevin',
                new_value=30
            ))

    # does not work as intended but no workaround, since an owner function, should be ok
    def test_settings_wrong_dtype(self):
        # NEED TO MAKE SURE ALL SETTINGS ARE PUT IN PROPERLY
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.change_settings(
            setting='min_bet',
            new_value='20'
        )

        self.assertEqual(p2p_contract.quick_read(variable='settings', key='min_bet'), '20')

    # cancel bet tests
    def test_cancel_bet(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.cancel_bet(
            bet_id=bet_id
        )
        self.assertEqual(p2p_contract.quick_read(variable='bets', key=bet_id + ':amount_left'), None)
        self.assertNotIn(bet_id, p2p_contract.quick_read(variable='bet_names', key='names'))

    def test_cancel_bet_no_bet(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.cancel_bet(
            bet_id=bet_id
        )
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.cancel_bet(
                bet_id=bet_id
            )
        )

    def test_cancel_bet_locked(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )

        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.cancel_bet(
                bet_id=bet_id
            )
        )

    def test_cancel_bet_not_in_bet(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.cancel_bet(
                bet_id=bet_id
            )
        )

    # cancel and redeem

    def test_cancel_redeem(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.cancel_bet(
            bet_id=bet_id
        )
        self.assertEqual(p2p_contract.quick_read(variable='bets', key=bet_id + ':amount_left'), None)
        self.assertNotIn(bet_id, p2p_contract.quick_read(variable='bet_names', key='names'))
        print(p2p_contract.quick_read(variable='bets', key='me' + ':funds'))

        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 500)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me' + ':funds'), 0)
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 0)

    def test_join_bet_success(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )
        self.assertEqual(p2p_contract.quick_read(variable='bets', key=bet_id + ':player_right'), 'you')
        self.assertEqual(p2p_contract.quick_read(variable='bets', key=bet_id + ':locked'), True)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 0)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me' + ':funds'), 0)

    def test_join_wrong_id(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'

        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.join_bet(
                bet_id="kevin",
                amount=60
            )
        )

    def test_join_locked(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60)

        client.signer = 'kevin'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.join_bet(
                bet_id=bet_id,
                amount=60
            )
        )

    # def test_join_deadline(self):

    def test_join_non_exact_amount(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.join_bet(
                bet_id=bet_id,
                amount=500
            )
        )

    def test_join_insufficient_funds(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'kevin'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.join_bet(
                bet_id=bet_id,
                amount=60
            )
        )

    def test_join_cancelled_bet(self):
        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )

        client.signer = 'me'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.cancel_bet(
            bet_id=bet_id,
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.join_bet(
                bet_id=bet_id,
                amount=60
            )
        )

    # malicious bet removal tests
    def test_remove_mali_success(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.remove_malicious_bet(
            bet_id=bet_id
        )

        print(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'))
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()

        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()

        self.assertEqual(p2p_contract.quick_read('S', 'me2'), 498)
        self.assertEqual(p2p_contract.quick_read('S', 'you'), 996)
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 6)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 0)

    def test_remove_mali_success_1p(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.remove_malicious_bet(
            bet_id=bet_id
        )

        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()

        self.assertEqual(p2p_contract.quick_read('S', 'me2'), 498)
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 2)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 0)

    def test_remove_mali_not_owner(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )

        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.remove_malicious_bet(
                bet_id=bet_id
            )
        )

    # amicable bet removal tests

    def test_remove_ami(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.remove_amicable_bet(
            bet_id=bet_id
        )
        print(p2p_contract.quick_read(variable='bets', key=bet_id + ':removal'))
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.remove_amicable_bet(
            bet_id=bet_id
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()

        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.redeem_funds()

        self.assertEqual(p2p_contract.quick_read('S', 'me2'), 500)
        self.assertEqual(p2p_contract.quick_read('S', 'you'), 1000)
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 0)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 0)

    def test_remove_ami_1p(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.remove_amicable_bet(
                bet_id=bet_id
            )
        )

    def test_remove_ami_no_bet(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )

        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.remove_amicable_bet(
                bet_id="x"
            )
        )

    def test_remove_ami_not_in(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.remove_amicable_bet(
                bet_id=bet_id
            )
        )

    def test_remove_ami_repeat(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.remove_amicable_bet(
            bet_id=bet_id
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.remove_amicable_bet(
                bet_id=bet_id
            )
        )

    # validation tests
    def create_join(self):
        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 2, 15, 12, 12, 12, 0)
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.join_bet(
            bet_id=bet_id,
            amount=60
        )

    def test_validate_success_l(self):
        self.create_join()

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=1
        )

        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 0)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 520)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 70)

    def test_validate_success_r(self):
        self.create_join()

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=0
        )

        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 80)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 80)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 510)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 0)

    def test_validate_wrong_id(self):
        self.create_join()

        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.validate(
                bet_id='t',
                winner=1
            )
        )


    def test_validate_not_validator(self):
        self.create_join()

        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.validate(
                bet_id='bet_id',
                winner=1
            )
        )

    # def test_validate_deadline(self):
    #     self.create_join()
    #
    #     client.signer = 'me'
    #     # set now in contract
    #     p2p_contract = client.get_contract('p2p_contract')
    #     self.assertRaises(
    #         AssertionError,
    #         lambda: p2p_contract.validate(
    #             bet_id='bet_id',
    #             winner=1
    #         )
    #     )

    def test_validate_1dec_winner(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=1
        )
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 70)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 520)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 0)

    def test_validate_1dec_loser(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=0
        )
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 10)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 520)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 60)

    def test_validate_2dec_dispute(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=1
        )
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 70)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 520)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 0)

    def test_validate_2dec_loser_deceit(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=1
        )
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 70)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 520)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 0)

    def test_validate_2dec_winner_deceit(self):
        self.create_join()
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.validate(
            bet_id='bet_id',
            winner=1
        )
        self.assertEqual(p2p_contract.quick_read('S', 'contract_balance'), 80)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 60)
        self.assertEqual(p2p_contract.quick_read('S', 'me'), 510)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 20)

    def test_det_outcome_success_left(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 70)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 20)

    def test_det_outcome_success_right(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=1
        )
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='me2' + ':funds'), 10)
        self.assertEqual(p2p_contract.quick_read(variable='bets', key='you' + ':funds'), 80)

    def test_det_outcome_dispute(self):
        self.create_join()
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )

        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.determine_outcome(
                bet_id='bet_id',
                outcome=0
            )
        )

    def test_det_outcome_x2(self):
        self.create_join()
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.determine_outcome(
                bet_id='bet_id',
                outcome=0
            )
        )

    def test_det_outcome_impostor(self):
        self.create_join()
        client.signer = 'you'
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.determine_outcome(
            bet_id='bet_id',
            outcome=0
        )
        client.signer = 'me'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.determine_outcome(
                bet_id='bet_id',
                outcome=0
            )
        )

    def test_det_outcome_1p(self):

        client.signer = 'me2'
        bet_id = "bet_id"
        p2p_contract = client.get_contract('p2p_contract')
        p2p_contract.create_bet(
            bet_id=bet_id,
            amount=20,
            opposing_amount=40,
            title="Test cases",
            deadline=Datetime(2021, 1, 15, 12, 12, 12, 0)
        )
        client.signer = 'me2'
        p2p_contract = client.get_contract('p2p_contract')
        self.assertRaises(
            AssertionError,
            lambda: p2p_contract.determine_outcome(
                bet_id='bet_id',
                outcome=0
            )
        )


if __name__ == '__main__':
    unittest.main()
