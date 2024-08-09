# Grafliq
A simple and pythonic way to query GraphQL endpoints without having to do 
any string manipulation.

Grafliq is a GraphQL client that provides a convenient way to handle GraphQL queries. 
Instead of building your query by manipulating and concatenating strings, you build 
your queries using function calls, eliminating all the complications and problems 
associated with string manipulation, and making maintenance an easy task.

## Important note
Grafliq only supports the `query` operation of GraphQL, there is no support 
for `mutations` and `subscriptions` and there will be none in the foreseeable future.

## Installing

**Install using pip**:

**`pip install grafliq`**

## Example using function calls as GraphQL operations (recommended)

Let's say we want to have a GraphQL query with the following structure:

```
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
        price(currency: "euro")
        model {
          name
          version
        }
        customer_rating(fromRatingDate: "2002-10-01") {
          count
          rates {
            average(decimalCount: 2)
            highest
            lowest
          }
        }
      }
    }
  }
}
```

We can generate the above query using the following Python code:

```python
from datetime import date
from grafliq.builder import GraphQL
from grafliq.query import NestedField, Quote, NoQuote, CustomizableField

query = GraphQL(
    endpoint='http://127.0.0.1:8080/graphql-api'
).category(
    name='household-appliances'
).electronics(
).gaming_consoles(
    'brand', 'name', 'color', 'discontinued', 'release_date',
    CustomizableField('price', currency="euro"),
    NestedField('model',
                'name', 'version'),
    NestedField('customer_rating',
                'count',
                NestedField('rates',
                            CustomizableField('average', decimalCount=2),
                            'highest', 'lowest'),
                fromRatingDate=date(2002, 10, 1)),
    fromReleaseDate=date(2000, 1, 1),
    fromPrice=Quote(150),
    discontinued=False,
    colors=NoQuote(['BLACK', 'WHITE', 'RED'])
)

"""
To get the query as a string, you can either do this:
"""

query_string1 = str(query)

"""
Or you can call `.generate()` on the query object:
"""

query_string2 = query.generate()

"""
If you pass the `endpoint` to the `GraphQL` initializer, you can 
call `.execute()` directly on the query object to call the remote API and get the result:
"""

result = query.execute()

"""
Note that if you have not passed the `endpoint` to the 
`GraphQL` initializer, by calling the `.execute()` function, an error will be raised.
"""
```

As shown in the example above, any operation available in the remote GraphQL API 
will be available as a function on the `GraphQL` object.

## Example using generic query

If you want to dynamically generate GraphQL queries 
(.ex in an automated script, from user input, ...), you can do this with 
the following example, which will generate exactly the same GraphQL query:

```python
from datetime import date
from grafliq.builder import GraphQL
from grafliq.query import NestedField, Quote, NoQuote, CustomizableField

query = GraphQL(
    endpoint='http://127.0.0.1:8080/graphql-api'
).query(
    'category',
    name='household-appliances'
).query(
    'electronics'
).query(
    'gaming_consoles',
    'brand', 'name', 'color', 'discontinued', 'release_date',
    CustomizableField('price', currency="euro"),
    NestedField('model',
                'name', 'version'),
    NestedField('customer_rating',
                'count',
                NestedField('rates',
                            CustomizableField('average', decimalCount=2),
                            'highest', 'lowest'),
                fromRatingDate=date(2002, 10, 1)),
    fromReleaseDate=date(2000, 1, 1),
    fromPrice=Quote(150),
    discontinued=False,
    colors=NoQuote(['BLACK', 'WHITE', 'RED'])
)
```

## Contribute to Grafliq development

I appreciate any kind of contribution to the development of Grafliq, 
especially to add support for mutations and subscriptions.
