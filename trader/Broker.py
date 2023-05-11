import time
import ccxt

from trader.Order import Order


class Broker:
    def __init__(self, config):
        self.exchange = config['exchange']

        ccxt_config = {
            "apiKey": config["api_key"],
            "secret": config["secret"],
            # "options": config["options"],
            "password": config["password"],
        }
        self.api: ccxt.Exchange.api = getattr(ccxt, self.exchange)(ccxt_config)

        self.sandbox_mode = False
        if "sandbox_mode" in config and config['sandbox_mode']:
            self.api.set_sandbox_mode(config['sandbox_mode'])
            self.sandbox_mode = True

    def get_balance(self, instrument) -> float:
        # instrument = self.base_currency if instrument is None else instrument
        all_balance = self.api.fetchBalance()
        if instrument in all_balance:
            return all_balance[instrument]['total']
        else :
            return 0
        # return self.api.fetchBalance()[instrument]["total"]

    def place_order(self, order: Order):

        side = "buy" if order.direction > 0 else "sell"
        # Submit the order
        placed_order = self.api.createOrder(
            symbol=order.instrument,
            type=order.order_type,
            side=side,
            amount=abs(order.size),
            # price=order.order_limit_price,
            # params=order.ccxt_params,
        )

        return placed_order

    def get_positions(self, instrument: str = None, **kwargs) -> dict:
        """Gets the current positions open on the account.

        Note that not all exchanges exhibit the same behaviour, and
        so caution must be taken when interpreting results. It is recommended
        to use the api directly and test with the exchange you plan to use
        to valid functionality.

        Parameters
        ----------
        instrument : str, optional
            The trading instrument name (symbol). The default is None.

        Returns
        -------
        open_positions : dict
            A dictionary containing details of the open positions.

        """
        for attempt in range(2):
            try:
                if instrument is None:
                    # Get all positions
                    if self.api.has["fetchPositions"]:
                        positions = self.api.fetchPositions(symbols=None, params=kwargs)
                        positions = self._convert_list(positions, item_type="position")

                    else:
                        raise Exception(
                            f"Exchange {self.exchange} does not have "
                            + "fetchPositions method."
                        )
                else:
                    # Get position in instrument provided
                    if self.api.has["fetchPosition"]:
                        position = self.api.fetchPosition(instrument, params=kwargs)
                        if position is not None:
                            positions = {instrument: self._native_position(position)}
                        else:
                            positions = {}

                    elif self.api.has["fetchPositions"]:
                        positions = self.api.fetchPositions(
                            symbols=[instrument], params=kwargs
                        )
                        positions = self._convert_list(positions, item_type="position")
                    else:
                        raise Exception(
                            f"Exchange {self.exchange} does not have "
                            + "fetchPosition method."
                        )

                # Completed without exception, break loop
                break

            except ccxt.errors.NetworkError:
                # Throttle then try again
                time.sleep(1)

        # Check for zero-positions
        positions_dict = {}
        for symbol, pos in positions.items():
            if pos.net_position != 0:
                positions_dict[symbol] = pos

        return positions_dict

    def _convert_list(self, items, item_type="order"):
        """Converts a list of trades or orders to a dictionary."""
        native_func = f"_native_{item_type}"
        id_key = "instrument" if item_type == "position" else "id"
        converted = {}
        for item in items:
            native = getattr(self, native_func)(item)
            converted[getattr(native, id_key)] = native
        return converted

    def fetchOHLCV(self, *args, **kwargs):
        if hasattr(self.api, "fetchOHLCV"):
            return self.api.fetchOHLCV(*args, **kwargs)
        raise "No fetchOHLCV function"

    def fetchTicker(self,*args,**kwargs):
        if hasattr(self.api,'fetchTicker'):
            return self.api.fetchTicker(*args,**kwargs)
        raise "No fetchTicker function"
