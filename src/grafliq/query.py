from string import Template


class QuotationManager:
    """
    a helper class that can be used to wrap function arguments that should be
    forced to be quoted or not quoted in the final graphql query.
    """

    def __init__(self, value):
        """
        initializes an instance of QuotationManager.

        :param value: the actual value.
        """

        self._value = value

    def __str__(self) -> str:
        return self.perform_quotation(self._value)

    def __repr__(self) -> str:
        return str(self)

    @property
    def original_value(self):
        """
        gets the original value which is wrapped inside this object.

        :returns: the original value.
        """

        return self._value

    def _perform_quotation(self, value) -> str:
        """
        performs the required quotation on the value.

        this method must be implemented in subclasses.

        NOTE:
        the `value` argument will always be an actual single value not a `Quote` or
        `NoQuote` or `DefaultQuote` instance or a list of items.

        :param value: the actual value to perform quotation on.
        :rtype: str
        """

        raise NotImplementedError()

    def perform_quotation(self, value) -> str:
        """
        performs the required quotation on the value.

        :param value: the value to perform quotation on.
        :rtype: str
        """

        if isinstance(value, QuotationManager):
            return str(value)

        if isinstance(value, (list, tuple, set)):
            processed_values = []
            for item in value:
                processed_values.append(self.perform_quotation(item))
            return '[' + ', '.join(str(item) for item in processed_values) + ']'

        if isinstance(value, dict):
            processed_values = {}
            for name, item in value.items():
                processed_values[name] = self.perform_quotation(item)
            return '{' + ', '.join(f'{name}: {str(item)}' for name, item in processed_values.items()) + '}'

        return self._perform_quotation(value)


class NoQuote(QuotationManager):
    """
    a helper class that can be used to wrap function arguments that should
    not be quoted in the final graphql query.
    """

    def _perform_quotation(self, value) -> str:
        """
        performs the required quotation on the value.

        NOTE:
        the `value` argument will always be an actual single value not a `Quote` or
        `NoQuote` or `DefaultQuote` instance or a list of items.

        :param value: the actual value to perform quotation on.
        :rtype: str
        """

        if isinstance(value, bool):
            return f'{str(value).lower()}'

        return f'{value}'


class Quote(QuotationManager):
    """
    a helper class that can be used to force arguments to be quoted in the final graphql query.
    """

    def _perform_quotation(self, value) -> str:
        """
        performs the required quotation on the value.

        NOTE:
        the `value` argument will always be an actual single value not a `Quote` or
        `NoQuote` or `DefaultQuote` instance or a list of items.

        :param value: the actual value to perform quotation on.
        :rtype: str
        """

        return f'"{value}"'


class DefaultQuote(QuotationManager):
    """
    a helper class that can be used to apply default quoting rules to the arguments in the final graphql query.

    default rules:

    - bool, int and float fields will not be quoted.
    - every other field type will be quoted.
    """

    def _perform_quotation(self, value) -> str:
        """
        performs the required quotation on the value.

        NOTE:
        the `value` argument will always be an actual single value not a `Quote` or
        `NoQuote` or `DefaultQuote` instance or a list of items.

        :param value: the actual value to perform quotation on.
        :rtype: str
        """

        if isinstance(value, (bool, int, float)):
            return str(NoQuote(value))

        return str(Quote(value))


class CustomizableField:
    """
    a helper class to be used to define graphql query fields which
    also accept arguments.
    """

    def __init__(self, name: str, **arguments):
        """
        initializes an instance of CustomizableField.

        :param str name: field name.
        :keyword arguments: any arguments which this field accepts in graphql api.
        """

        self._name = name
        self._arguments = arguments

    def __str__(self) -> str:
        all_args = ''
        if self._arguments:
            args = []
            for name, value in self._arguments.items():
                prepared_argument = prepare_argument(name, value)
                args.append(prepared_argument)

            all_args = '(' + ', '.join(args) + ')'

        return f'{self._name}{all_args}'

    def __repr__(self) -> str:
        return str(self)


class NestedField(CustomizableField):
    """
    a helper class to be used to define graphql query fields which
    contain another object instead of a single value.
    this field type also accepts arguments.
    """

    def __init__(self, name: str, *fields, **arguments):
        """
        initializes an instance of NestedField.

        :param str name: nested field name.
        :param str | CustomizableField | NestedField fields: field names of the nested field.
        :keyword arguments: any arguments which this field accepts in graphql api.
        """

        super().__init__(name, **arguments)

        self._fields = fields

    def __str__(self) -> str:
        return Template('${name} {${fields}}').substitute(
            name=super().__str__(), fields=' '.join(str(item) for item in self._fields))

    def __repr__(self) -> str:
        return str(self)


class Query:
    """
    graphql query object.

    this class's objects are callable as well, and they will return the GraphQL object.
    it is defined this way to allow method chain calls on the GraphQL object.
    """

    def __init__(self, name: str, graphql):
        """
        initializes an instance of Query.

        :param str name: query name (the name of the operation in graphql api).
        :param GraphQL graphql: graphql object which this query belongs to.
        """

        self._name = name
        self._fields = []
        self._arguments = {}
        self._graphql = graphql

    def __call__(self, *fields: str | CustomizableField | NestedField, **arguments):
        """
        by calling the Query object it will be added to GraphQL object's queries.

        the GraphQL object will be returned.

        :param str | CustomizableField | NestedField fields: field names of the query.
        :keyword arguments: any arguments which this operation accepts in graphql api.
        :rtype: GraphQL
        """

        self._fields = fields
        self._arguments = arguments
        self._graphql.add_query(self)
        return self._graphql

    def __str__(self) -> str:
        return self.generate()

    def __repr__(self) -> str:
        return str(self)

    def generate(self, child: str = None) -> str:
        """
        generates the corresponding graphql query for this query object.

        :param str child: a child operation that should be wrapped in this query.
        :rtype: str
        """

        args = []
        all_args = ''
        if self._arguments:
            for name, value in self._arguments.items():
                prepared_argument = prepare_argument(name, value)
                args.append(prepared_argument)

            all_args = '(' + ', '.join(args) + ')'

        if child is None:
            child = ''

        if self._fields and child:
            raise Exception(f'Query [{self._name}] cannot have both fields and child operation.')

        all_fields = ''
        if self._fields:
            all_fields = ' '.join(str(field) for field in self._fields)
            all_fields = '{' + all_fields + '}'

        result = '{' + f'{self._name}{all_args}{all_fields or child}' + '}'
        return result


def prepare_argument(name: str, value) -> str:
    """
    prepares the given argument to be put in the graphql query.

    :param str name: argument name.
    :param value: argument value.
    :rtype: str
    """

    value = prepare_value(value)
    return f'{name}: {value}'


def prepare_value(value) -> str:
    """
    prepares the given value to be put in the graphql query.

    :param value: the value to be prepared.
    :rtype str
    """

    if isinstance(value, QuotationManager):
        return str(value)

    return str(DefaultQuote(value))
