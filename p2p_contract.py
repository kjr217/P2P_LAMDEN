# import currency
S = Hash(default_value=0)
owner = Variable()
settings = Hash()
bets = Hash()
bet_names = Hash()
validators = Hash()

# change owners, transfer function, and deadlines

@construct
def seed():
    S['me'] = 500
    S['you'] = 1000
    S['kevin'] = 50
    S['me2'] = 500
    S['contract_balance'] = 0
    owner.set('me')
    settings['min_bet'] = 15
    settings['max_bets'] = 40
    settings['validator_deposit_percent'] = 0.5
    settings['validation_deadline'] = datetime.timedelta(days=1)
    settings['list'] = ['min_bet', 'max_bets' 'validator_deposit_percent', 'validation_deadline']
    validators['list'] = ['me']

@export
def transfer(amount:int, to: str):
    sender = ctx.caller
    balance = S[sender]
    assert balance >= amount, 'not enough'
    S[sender] -= amount
    S[to] += amount

@export
def transfer_from(amount:int, to: str, fro: str):
    sender = ctx.caller
    balance = S[sender]
    assert balance >= amount, 'not enough'
    S[fro] -= amount
    S[to] += amount


@export
def redeem_funds():
    sender = ctx.caller
    assert bets[sender, 'funds'] is not None, 'You have no funds to redeem'
    assert bets[sender, 'funds'] > 0, 'You have no funds to redeem'
    funds = bets[sender, 'funds']
    bets[sender, 'funds'] = 0
    transfer_from(amount=funds, to=sender, fro='contract_balance')
    # currency.transfer(amount=funds, to=sender)


@export
def transfer_ownership(new_owner: str):
    assert owner.get() == ctx.caller, 'haha'
    owner.set(new_owner)


@export
def assign_validator(validator: str, revoke: bool):
    assert owner.get() == ctx.caller, 'Only the contract owner can assign a new validator'
    if revoke:
        validators['list'].remove(validator)
    if not revoke:
        validators['list'].append(validator)


@export
def create_bet(bet_id: str, amount: int, opposing_amount: int, title: str,
               deadline: datetime.datetime):
    sender = ctx.caller
    assert amount >= settings['min_bet'], "Bet is not large enough, min_bet is " + str(settings['min_bet'])
    assert opposing_amount >= settings['min_bet'], "Bet is not large enough, min_bet is " + str(settings['min_bet'])
    assert bets[bet_id, 'amount_left'] is None, 'Game with ID ' + str(bet_id) + ' already exists'
    assert deadline > now, 'Deadline cannot be in the past'
    validation_deposit_left = amount * settings['validator_deposit_percent']
    validation_deposit_right = opposing_amount * settings['validator_deposit_percent']
    bet = amount + validation_deposit_left
    assert_balance(bet)
    # currency.transfer_from(amount=bet, to=ctx.this, main_account=sender)
    transfer(amount=bet, to='contract_balance')
    # bets[bet_id] = [amount_left, amount_right, validation_deposit_left, validation_deposit_right, player_left,
    # player_right, title, deadline, decision]
    bets[bet_id] = [amount, opposing_amount, validation_deposit_left, validation_deposit_right, sender, None, title, deadline]
    bets[bet_id, 'amount_left'] = amount
    bets[bet_id, 'amount_right'] = opposing_amount
    bets[bet_id, 'validation_deposit_left'] = validation_deposit_left
    bets[bet_id, 'validation_deposit_right'] = validation_deposit_right
    bets[bet_id, 'player_left'] = sender
    bets[bet_id, 'locked'] = False
    bets[bet_id, 'deadline'] = deadline
    bets[bet_id, 'decision'] = []
    bets[bet_id, 'removal'] = []
    bets[sender, 'funds'] = 0
    if bet_names['names'] is not None:
        names = bet_names['names']
        names.append([bet_id, title])
        bet_names['names'] = names
    else:
        bet_names['names'] = [[bet_id, title]]


@export
def join_bet(bet_id: str, amount: float):
    sender = ctx.caller
    assert bets[bet_id, 'amount_left'] is not None, bet_id + ' does not exist'
    assert not bets[bet_id, 'locked'], 'This bet is full'
    assert sender != bets[bet_id, 'player_left'], 'You are already in this bet'
    assert bets[bet_id, 'deadline'] > now, 'The deadline for this contract has passed'
    bet = bets[bet_id, 'amount_right'] + bets[bet_id, 'validation_deposit_right']
    assert amount == bet, 'Your deposit amount must be exactly the required bet and validation fee, this is ' + str(bet)
    assert_balance(bet)
    transfer(amount=bet, to="contract_balance")
    # currency.transfer_from(amount=bet, to=ctx.this, main_account=sender)
    bets[bet_id, 'player_right'] = sender
    bets[bet_id][5] = sender
    bets[bet_id, 'locked'] = True
    if bets[sender, 'funds'] is None:
        bets[sender, 'funds'] = 0

@export
def validate(bet_id: str, winner: bool):
    # True means left, False means right
    sender = ctx.caller
    assert bets[bet_id, 'amount_left'] is not None, 'Bet does not exist'
    assert sender in validators['list'], 'Only certified validators may validate disputed bets'
    assert bets[bet_id, 'deadline'] + settings['validation_deadline'] < now, 'Not past deadline yet'
    decisions = bets[bet_id, 'decision']
    if winner:
        winner_wallet = bets[bet_id, 'player_left']
        loser_wallet = bets[bet_id, 'player_right']
        if len(decisions) == 1 and winner_wallet != decisions[0][0]:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right']
            validator_fee = bets[bet_id, 'validation_deposit_left']
            bets[loser_wallet, 'funds'] += bets[bet_id, 'validation_deposit_right']
        elif len(decisions) == 2 and winner_wallet == decisions[1][0] and loser_wallet == decisions[1][1]:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right']
            validator_fee = bets[bet_id, 'validation_deposit_left']
            bets[loser_wallet, 'funds'] += bets[bet_id, 'validation_deposit_right']
        else:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right'] + bets[
                bet_id, 'validation_deposit_left']
            validator_fee = bets[bet_id, 'validation_deposit_right']
    elif not winner:
        winner_wallet = bets[bet_id, 'player_right']
        loser_wallet = bets[bet_id, 'player_left']
        if len(decisions) == 1 and winner_wallet != decisions[0][0]:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right']
            validator_fee = bets[bet_id, 'validation_deposit_right']
            bets[loser_wallet, 'funds'] += bets[bet_id, 'validation_deposit_left']
        elif len(decisions) == 2 and winner_wallet == decisions[1][0] and loser_wallet == decisions[1][1]:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right']
            validator_fee = bets[bet_id, 'validation_deposit_right']
            bets[loser_wallet, 'funds'] += bets[bet_id, 'validation_deposit_left']
        else:
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right'] + bets[
                bet_id, 'validation_deposit_right']
            validator_fee = bets[bet_id, 'validation_deposit_left']
    bets[winner_wallet, 'funds'] += amount
    transfer_from(amount=validator_fee, to=sender, fro='contract_balance')
    # currency.transfer(amount=validator_fee, to=sender)
    remove_game(bet_id)

@export
def remove_malicious_bet(bet_id: str):
    # necessary as a precaution and preventative measure against malicious actors creating bad bets,
    # such as offensive bets or potential exploits. This is left at the discretion of the owner and will not be used
    # unless absolutely necessary.
    assert owner.get() == ctx.caller, 'Only the owner can remove a malicious bet'
    player_left = bets[bet_id, 'player_left']
    amount_left = bets[bet_id, 'amount_left'] + (bets[bet_id, 'validation_deposit_left'] * 0.8)
    bets[player_left, 'funds'] += amount_left
    owner_fee = (bets[bet_id, 'validation_deposit_left'] * 0.2)
    if bets[bet_id, 'player_right'] is not None:
        player_right = bets[bet_id, 'player_right']
        amount_right = bets[bet_id, 'amount_right'] + (bets[bet_id, 'validation_deposit_right'] * 0.8)
        bets[player_right, 'funds'] += amount_right
        owner_fee += (bets[bet_id, 'validation_deposit_right'] * 0.2)
    transfer(amount=owner_fee, to=ctx.caller)
    # currency.transfer(amount=owner_fee, to=ctx.caller)
    remove_game(bet_id)


@export
def remove_amicable_bet(bet_id: str):
    # necessary in case both parties decide to end a bet.
    sender = ctx.caller
    assert bets[bet_id, 'amount_left'] is not None, 'Bet does not exist'
    assert bets[bet_id, 'locked'], 'Your bet has not been matched yet, you can call cancel_bet instead'
    assert sender == bets[bet_id, 'player_left'] or sender == bets[bet_id, 'player_right'], 'You are not a part of this bet'
    assert sender not in bets[
        bet_id, 'removal'], 'You have already submitted a removal request, you must wait for your opponent'
    bets[bet_id, 'removal'].append(sender)
    if len(bets[bet_id, 'removal']) == 2:
        player_left = bets[bet_id, 'player_left']
        amount_left = bets[bet_id, 'amount_left'] + bets[bet_id, 'validation_deposit_left']
        bets[player_left, 'funds'] += amount_left
        player_right = bets[bet_id, 'player_right']
        amount_right = bets[bet_id, 'amount_right'] + bets[bet_id, 'validation_deposit_right']
        bets[player_right, 'funds'] += amount_right
        remove_game(bet_id)

@export
def cancel_bet(bet_id: str):
    sender = ctx.caller
    assert bets[bet_id, 'amount_left'] is not None, 'Bet does not exist'
    assert not bets[bet_id, 'locked'], 'The game is locked'
    assert sender == bets[bet_id, 'player_left'], 'You are not in the bet'
    amount = bets[bet_id, 'amount_left']
    validation = bets[bet_id, 'validation_deposit_left']
    bets[sender, 'funds'] += amount + validation
    remove_game(bet_id)

@export
def determine_outcome(bet_id: str, outcome: bool):
    # True means you won, False means you lost
    sender = ctx.caller
    assert bets[bet_id, 'amount_left'] is not None, bet_id + ' does not exist'
    assert deadline < now, 'The deadline has not passed yet'
    assert bets[bet_id, 'locked'], 'This bet was not matched, please remove the bet instead'
    assert sender == bets[bet_id, 'player_right'] or sender == bets[bet_id, 'player_left'], 'You are not part of this bet'
    decision = bets[bet_id, 'decision']
    if len(decision) == 1:
        assert sender != decision[0][0], "You have already made a decision"
    elif len(decision) == 2:
        assert decision[0][1] == decision[1][1], "This bet is disputed and must be resolved by a validator"
    if sender == bets[bet_id, 'player_left']:
        player_left = sender
        player_right = bets[bet_id, 'player_right']
        if outcome:
            dec = player_left
        else:
            dec = player_right
    else:
        player_left = bets[bet_id, 'player_left']
        player_right = sender
        if outcome:
            dec = player_right
        else:
            dec = player_left
    decision.append([sender, dec])
    if len(decision) == 2:
        make_decision(bet_id, decision, player_left, player_right)
    else:
        bets[bet_id, 'decision'] = decision


def make_decision(bet_id, decision, player_left, player_right):
    if decision[0][1] == decision[1][1]:
        if player_left == decision[0][1]:
            winner_wallet = player_left
            loser_wallet = player_right
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right'] + bets[
                bet_id, 'validation_deposit_left']
            validation = bets[bet_id, 'validation_deposit_right']
        elif player_right == decision[0][1]:
            winner_wallet = player_right
            loser_wallet = player_left
            amount = bets[bet_id, 'amount_left'] + bets[bet_id, 'amount_right'] + bets[
                bet_id, 'validation_deposit_right']
            validation = bets[bet_id, 'validation_deposit_left']
        bets[winner_wallet, 'funds'] += amount
        bets[loser_wallet, 'funds'] += validation
        remove_game(bet_id)

@export
def change_settings(setting: str, new_value: Any):
    assert owner.get() == ctx.caller, 'You are not authorised to change settings'
    assert setting in settings['list'], "Not a configurable setting"
    settings[setting] = new_value


def remove_game(bet_id: str):
    bets[bet_id, 'amount_left'] = None
    bets[bet_id, 'amount_right'] = None
    bets[bet_id, 'validation_deposit_left'] = None
    bets[bet_id, 'validation_deposit_right'] = None
    bets[bet_id, 'player_left'] = None
    bets[bet_id, 'player_right'] = None
    bets[bet_id, 'locked'] = None
    bets[bet_id, 'deadline'] = None
    bets[bet_id, 'decision'] = None
    bets[bet_id, 'removal'] = None
    names = bet_names['names']
    title = bets[bet_id][6]
    bets[bet_id] = None
    names.remove([bet_id, title])
    bet_names['names'] = names


def assert_balance(balance: int):
    sender = ctx.caller
    sender_balance = S[sender]
    assert sender_balance >= balance, 'Bet amount exceeds available token balance, please note the validation fee'
