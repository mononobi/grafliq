import requests

from grafliq.query import Query


class GraphQL:
    """
    this class is the query builder and manager for graphql api.

    you should create an instance of this class, and then build your query accordingly.
    it can (and is supposed to) be used in method chain style.
    every operation which is available on your graphql api can be used on this object as a
    function with the same name. alternatively you can also create queries using the generic
    `.query()` function of this object. the two modes can be used interchangeably.

    to get the graphql query as a string, you can either use `str(graphql)` or
    alternatively call `.generate()` on this object. to execute the query and get the
    results without the need to get the query as a string, you can call `.execute()` on
    this object. note that you should set the `endpoint` when instantiating this object
    to be able to use `.execute()` function.

    NOTE 1:
    by default all arguments will be quoted in the final query except for bool, int and float
    arguments. to force a bool, int or float argument to be quoted in the final query, you can
    pass them wrapped into a `Quote(value)` object.

    NOTE 2:
    if some arguments of a function should not be quoted in the final query, you can
    pass them wrapped into a `NoQuote(value)` object.

    NOTE 3:
    both `.execute()` and `.generate()` functions can be configured to reset the current
    object after a successful call, so that the same object can be used for new queries.
    but `str(graphql)` usage, does not support resetting the current object.

    -------------------------------------------------------------------------------------

    let's assume that we want to have a graphql query with the following structure:

    {
      category(name: "household-appliances") {
        electronics {
          gaming_consoles(
            fromReleaseDate: "2000-01-01"
            fromPrice: "150"
            discontinued: false
            colors: [BLACK, WHITE, RED]
          ) {
            brand
            name
            color
            discontinued
            release_date
            price
            model {
              name
              version
            }
            customer_rating {
              count
              rates {
                average
                highest
                lowest
              }
            }
          }
        }
      }
    }

    we can accomplish this through any of the following approaches:

    -------------------------------------------------------------------------------------

    ex. 1 (using `.execute()`):

    results = GraphQL(endpoint='http://127.0.0.1:8080/graphql-api').category(
        name='household-appliances'
    ).electronics(
    ).gaming_consoles(
        'brand', 'name', 'color', 'discontinued', 'release_date', 'price',
        NestedField('model',
                    'name', 'version'),
        NestedField('customer_rating',
                    'count',
                    NestedField('rates', 'average', 'highest', 'lowest')),
        fromReleaseDate=date(2000, 1, 1),
        fromPrice=Quote(150),
        discontinued=False,
        colors=NoQuote(['BLACK', 'WHITE', 'RED'])
    ).execute(reset=True)

    -------------------------------------------------------------------------------------

    ex. 2 (using `str(graphql)`):

    graphql = GraphQL().category(
        name='household-appliances'
    ).electronics(
    ).gaming_consoles(
        'brand', 'name', 'color', 'discontinued', 'release_date', 'price',
        NestedField('model',
                    'name', 'version'),
        NestedField('customer_rating',
                    'count',
                    NestedField('rates', 'average', 'highest', 'lowest')),
        fromReleaseDate=date(2000, 1, 1),
        fromPrice=Quote(150),
        discontinued=False,
        colors=NoQuote(['BLACK', 'WHITE', 'RED'])
    )
    query = str(graphql)

    -------------------------------------------------------------------------------------

    ex. 3 (using `.generate()`):

    query = GraphQL(reset_on_generate=True).category(
        name='household-appliances'
    ).electronics(
    ).gaming_consoles(
        'brand', 'name', 'color', 'discontinued', 'release_date', 'price',
        NestedField('model',
                    'name', 'version'),
        NestedField('customer_rating',
                    'count',
                    NestedField('rates', 'average', 'highest', 'lowest')),
        fromReleaseDate=date(2000, 1, 1),
        fromPrice=Quote(150),
        discontinued=False,
        colors=NoQuote(['BLACK', 'WHITE', 'RED'])
    ).generate()

    -------------------------------------------------------------------------------------

    ex. 4 (same as the previous example but using `.query()` function):

    query = GraphQL(reset_on_generate=True).query(
        'category',
        name='household-appliances'
    ).query(
        'electronics'
    ).query(
        'gaming_consoles',
        'brand', 'name', 'color', 'discontinued', 'release_date', 'price',
        NestedField('model',
                    'name', 'version'),
        NestedField('customer_rating',
                    'count',
                    NestedField('rates', 'average', 'highest', 'lowest')),
        fromReleaseDate=date(2000, 1, 1),
        fromPrice=Quote(150),
        discontinued=False,
        colors=NoQuote(['BLACK', 'WHITE', 'RED'])
    ).generate()
    """

    def __init__(self,
                 endpoint: str = None,
                 reset_on_execute: bool = False,
                 reset_on_generate: bool = False):
        """
        initializes an instance of GraphQL.

        :param str endpoint: the graphql endpoint to execute the queries against.
                             if not provided, the `.execute()` function of this object
                             cannot be called and will raise an exception.
        :param bool reset_on_execute: reset this object after each successful `.execute()` call,
                                      so that the same object can be used for other queries.
                                      defaults to False if not provided.
        :param bool reset_on_generate: reset this object after each successful `.generate()` call,
                                       so that the same object can be used for other queries.
                                       defaults to False if not provided.
        """

        self._endpoint = endpoint
        self._reset_on_execute = reset_on_execute
        self._reset_on_generate = reset_on_generate
        self._queries: list[Query] = []

    def __getattr__(self, name: str) -> Query:
        """
        this method is overridden to be able to support available graphql operations on the fly.

        note that this method will only be called if the attribute is not already defined
        on the object, so the GraphQL object will no longer throw attribute errors since
        any missing attribute will be interpreted as a query name in graphql.

        :param str name: name of the attribute (graphql operation).
        :rtype: Query
        """

        return Query(name, self)

    def __str__(self) -> str:
        return self.generate(reset=False)

    def __repr__(self) -> str:
        return str(self)

    def _should_reset(self, priority_flag: bool, global_flag: bool) -> bool:
        """
        gets a value indicating that the state of this object should be reset.

        the status will be determined based on the two types of the provided flags.

        :param bool priority_flag: the flag with precedence over the `global_flag`.
        :param bool global_flag: the global flag which will take effect only if the
                                 `priority_flag` has not been set.
        :rtype: bool
        """

        if priority_flag is not None:
            return priority_flag

        return global_flag

    def add_query(self, query: Query):
        """
        adds the provided query into the list of queries.

        :param Query query: query to be added.
        """

        self._queries.append(query)

    def query(self, _query_name: str, *fields: str, **arguments) -> "GraphQL":
        """
        creates a query and adds it to the available queries.

        the GraphQL object will be returned.

        this method has only been implemented to provide the ability to create the
        queries using a generic method instead of attributes (which is the preferred way).

        :param str _query_name: query name (the name of the operation in graphql api).
        :param str | CustomizableField | NestedField fields: field names of the query.
        :keyword arguments: any arguments which this operation accepts in graphql api.
        :rtype: GraphQL
        """

        query = Query(_query_name, self)
        return query(*fields, **arguments)

    def generate(self, reset: bool = None) -> str:
        """
        generates the corresponding graphql query.

        :param bool reset: reset this object after a successful `.generate()` call,
                           so that the same object can be used for other queries.
                           this value has precedence over the `reset_on_generate` flag.
                           defaults to None if not provided and the `reset_on_generate`
                           flag will take effect.
        :rtype: str
        """

        query = ''
        child = None
        for item in reversed(self._queries):
            query = item.generate(child)
            child = query

        result = self.remove_duplicate_spaces(query)

        if self._should_reset(reset, self._reset_on_generate):
            self.reset()

        return result

    def execute(self, reset: bool = None, query_key: str = 'query', **kwargs) -> dict:
        """
        executes the graphql query against the configured graphql api and returns the results.

        :param bool reset: reset this object after a successful `.execute()` call,
                           so that the same object can be used for other queries.
                           this value has precedence over the `reset_on_execute` flag.
                           defaults to None if not provided and the `reset_on_execute`
                           flag will take effect.
        :param str query_key: the key to be put in request's json body before sending the
                              request to graphql endpoint. defaults to `query` if not
                              provided.
        :keyword kwargs: any extra keyword arguments that should be passed
                         to `requests.post()` method. ex. headers, auth, cookies, etc.
        :rtype: dict
        """

        if not self._endpoint:
            raise ValueError('GraphQL "endpoint" has not been set and '
                             'the query cannot be executed.')

        response = requests.post(url=self._endpoint, json={query_key: str(self)}, **kwargs)
        response.raise_for_status()
        result = response.json()

        if self._should_reset(reset, self._reset_on_execute):
            self.reset()

        return result

    def reset(self):
        """
        resets the current state of this object so that it can be used for a new query.
        """

        self._queries.clear()

    @staticmethod
    def remove_duplicate_spaces(query: str) -> str:
        """
        removes duplicate spaces from a query.

        :param str query: query to be revised.
        :rtype: str
        """

        return ' '.join(query.split())
