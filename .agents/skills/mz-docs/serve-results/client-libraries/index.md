# Client libraries

Connect via client libraries/SQL drivers

Applications can use various common language-specific PostgreSQL client
libraries to interact with Materialize and **create relations**, **execute
queries** and **stream out results**.

> **Note:** Client libraries tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if PostgreSQL is supported, it's **not guaranteed** that the same integration will work out-of-the-box.

| Language | Tested drivers                                                  | Notes                                                 |
| -------- | --------------------------------------------------------------- | ----------------------------------------------------- |
| Go       | [`pgx`](https://github.com/jackc/pgx)                           | See the [Go cheatsheet](/serve-results/client-libraries/golang/).       |
| Java     | [PostgreSQL JDBC driver](https://jdbc.postgresql.org/)          | See the [Java cheatsheet](/serve-results/client-libraries/java-jdbc/).  |
| Node.js  | [`node-postgres`](https://node-postgres.com/)                   | See the [Node.js cheatsheet](/serve-results/client-libraries/node-js/). |
| PHP      | [`pdo_pgsql`](https://www.php.net/manual/en/ref.pgsql.php)      | See the [PHP cheatsheet](/serve-results/client-libraries/php/).         |
| Python   | [`psycopg2`](https://pypi.org/project/psycopg2/)                | See the [Python cheatsheet](/serve-results/client-libraries/python/) and its [SQLAlchemy section](/serve-results/client-libraries/python/#sqlalchemy). |
| Ruby     | [`pg` gem](https://rubygems.org/gems/pg/)                       | See the [Ruby cheatsheet](/serve-results/client-libraries/ruby/).       |
| Rust     | [`postgres-openssl`](https://crates.io/crates/postgres-openssl) | See the [Rust cheatsheet](/serve-results/client-libraries/rust/).       |

👋 _Is there another client library you'd like to use with Materialize? Submit a
[feature
request](https://github.com/MaterializeInc/materialize/discussions/new?category=feature-requests&labels=A-integration)._

## Pages in this section

- [Golang cheatsheet](/serve-results/client-libraries/golang/index.md): Use Go to connect, insert, manage, query and stream from Materialize.
- [Java cheatsheet](/serve-results/client-libraries/java-jdbc/index.md): Use the PostgreSQL JDBC Driver to connect, insert, manage, query and stream from Materialize.
- [Node.js cheatsheet](/serve-results/client-libraries/node-js/index.md): Use Node.js to connect, insert, manage, query and stream from Materialize.
- [PHP cheatsheet](/serve-results/client-libraries/php/index.md): Use PHP PDO to connect, insert, manage, query and stream from Materialize.
- [Python cheatsheet](/serve-results/client-libraries/python/index.md): Use Python to connect, insert, manage, query and stream from Materialize.
- [Ruby cheatsheet](/serve-results/client-libraries/ruby/index.md): Use Ruby to connect, insert, manage, query and stream from Materialize.
- [Rust cheatsheet](/serve-results/client-libraries/rust/index.md): Use Rust postgres-openssl to connect, insert, manage, query and stream from Materialize.
