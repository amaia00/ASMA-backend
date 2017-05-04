
class PositionGPS:
    """

    """

    def __init__(self, latitude, longitude):
        """

        :param latitude:
        :param longitude:
        """
        self._latitude = latitude
        self._longitude = longitude

    def get_latitude(self):
        """

        :return:
        """
        return self._latitude

    def get_longitude(self):
        """

        :return:
        """
        return self._longitude

    def to_string(self):
        """

        :return:
        """
        print("Longitud: ", self._longitude, "Latitude: ", self._longitude)


class Entity:
    """

    """

    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        self._id = kwargs.get('id')
        self._name = kwargs.get('name', '')
        self._type = kwargs.get('type', '')
        self._position_gps = PositionGPS(latitude=kwargs.get('latitude', 0),
                                         longitude=kwargs.get('longitude', 0))

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_position_gps(self):
        return self._position_gps

    def to_string(self):
        print("Name: ", self._name, "Type: ", self._type, self._position_gps.to_string())


class EntityGeoNames(Entity):
    """

    """

    def __init__(self, **kwargs
                 ):
        super().__init__(**kwargs)
        self._feature_class = kwargs.get('feature_class')
        self._feature_code = kwargs.get('feature_code')

    def get_feature_class(self):
        return self._feature_class

    def get_feature_code(self):
        return self._feature_code

    def to_string(self):
        print("Name: ", self._name, self._position_gps.to_string(), "Type class: ",
              self._feature_class, "Type code", self._feature_code)