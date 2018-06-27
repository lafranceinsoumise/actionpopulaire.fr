class AbstractPaymentMode():
    can_retry = False

    @property
    def id(self):
        raise NotImplementedError('Must implement this property.')

    @property
    def payment_view(self):
        raise NotImplementedError('Must implement this property.')

    @property
    def url_fragment(self):
        return self.id

    @staticmethod
    def get_urls():
        """Returns additional urls associated with this payment mode

        :return:
        """
        return []
