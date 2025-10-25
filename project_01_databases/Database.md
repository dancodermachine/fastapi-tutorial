# Database
The role of a database is to store data in a structured way, preserve the integrity of the data, and offer a query language that enables you to retrieve this data when an application needs it.
* Relational databases, with their associated SQL query language.
    - Each entity, or object, of the application is stored in tables.
    - Each of those tables will have several columns representing the attributes of the entity.
    - Each table can be in a relationship with others, with rows referring to other rows in other tables.
    - Each row in a relational database has an identifier, called a **primary key**. This is unique in the table and allows you to uniquely identify this row. Therefore, it's possible to use this key in another table to reference it. We call this a **foreign key**: the key is foreign in the sense that it refers to another table.

* NoSQL databases.
    - Key-value stores, such as Redis.
    - Graph databases, such as Neo4j.
    - Document-oriented databases, such as MongoDB.
    - Store all the information of a given object inside a single **document**.
    - Documents are stored in **collections**.
    - Increase query performance by limiting the neeed to look at several collections.

## SQL Database with SQLAlchemy

## MongoDB