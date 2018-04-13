from apps.strategy.models.abstract_strategy import AbstractStrategy

class MultyCurrencyStrategy(AbstractStrategy):
    # TODO: in case of multicurrency strategy, add additional currencies
    # and overload constructor with one more parameter

    additional_currency_pairs = None  # should be [ (BTC,2), (ETH,0) ... ]

    def __init__(self, parameters, additional_currency_pairs):
        super(MultyCurrencyStrategy, self).__init__(parameters)
        self.additional_currency_pairs = additional_currency_pairs