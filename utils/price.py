import json


class Price:
    """
    Price Class for calculating the electricity bill
    """

    def __init__(self, price_list, step):
        # price_list is a list of dicts with keys 'from', 'to', 'cost'
        # step is the time step in minutes
        # price_list must be sorted by 'from'
        # 'from' and 'to' are in minutes
        # 'cost' is in cents
        # 'from' and 'to' are inclusive

        self.price_list = price_list

        # Convert time to units of step
        for i, price_data in enumerate(price_list):
            price_data['from'] //= step
            price_data['to'] //= step
            price_data['cost'] *= step / 60
            if i > 0:
                price_data['from'] += 1
            self.price_list[i] = price_data

    def get_price(self, time):
        # time is in units of step
        for price_data in self.price_list:
            if price_data['from'] <= time <= price_data['to']:
                # Found the price
                return price_data['cost']
        raise Exception('No price for time {}'.format(time))

    def get_total_price(self, time):
        return sum(self.get_price(t) for t in range(time))

    def __call__(self, time):
        return self.get_price(time)

    def __str__(self):
        return json.dumps(self.price_list, indent=4)
