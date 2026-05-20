# martin fowler

Catalog of Patterns of Enterprise Application Architecture

Martin Fowler

05 March 2003

Enterprise applications are about the display, manipulation,
    and storage of large amounts of often complex data; together with the support or
    automation of business processes with that data. Examples include
    reservation systems, financial systems, supply chain systems, and many
    others that run modern business. Enterprise applications have their own
    particular challenges and solutions, and they are different from embedded
    systems, control systems, telecoms, or desktop productivity software.

The book
Patterns of Enterprise Application
    Architecture
 collects together patterns that I, and my colleagues,
    have seen in these systems over the years. They include such topics as
    layering, structuring business logic, structuring a web user interface,
    linking in-memory data to a relational database, and handling session state
    in stateless environments. This site contains short summaries of these
    patterns, with deep links to the relevant chapters for the online eBook publication on
    oreilly.com (marked on this page with
).

Domain Logic Patterns

Transaction Script

Organizes business logic by procedures where each procedure handles
a single request from the presentation.

Domain Model

An object model of the domain that incorporates both behavior and data.

Table Module

A single instance that handles the business logic for all rows in a database table or view.

Service Layer

Defines an application's boundary with a layer of services that
establishes a set of available operations and coordinates the
application's response in each operation.

Data Source Architectural Patterns

Table Data Gateway

An object that acts as a gateway to a database table. One instance handles all the rows in the table.

Row Data Gateway

An object that acts as a gateway to a single record in a data
source. There is one instance per row.

Active Record

An object that wraps a row in a database table or view, encapsulates
the database access, and adds domain logic on that data.

Data Mapper

A layer of mappers that moves data between objects and a database while keeping them independent of each other and the mapper itself.

Object-Relational Behavioral Patterns

Unit of Work

Maintains a list of objects affected by a business
transaction and coordinates the writing out of changes and the
resolution of concurrency problems.

Identity Map

Ensures that each object gets loaded only once by keeping
every loaded object in a map. Looks up objects using the map when
referring to them.

Lazy Load

An object that doesn't contain all of the data you need
but knows how to get it.

Object-Relational Structural Patterns

Identity Field

Saves a database ID field in an object to maintain identity between
an in-memory object and a database row.

Inheritance Mappers

A structure to organize database mappers that handle
inheritance hierarchies.

Foreign Key Mapping

Maps an association between objects to a foreign
key reference between tables.

Association Table Mapping

Saves an association as a table with foreign keys to the tables
that are linked by the association.

Dependent Mapping

Has one class perform the database mapping for a child
class.

Embedded Value

Maps an object into several fields of another object's
table.

Serialized LOB

Saves a graph of objects by serializing them into a single
large object (LOB), which it stores in a database field.

Single Table Inheritance

Represents an inheritance hierarchy of classes as a single
table that has columns for all the fields of the various
classes.

Class Table Inheritance

Represents an inheritance hierarchy of classes with one
table for each class.

Concrete Table Inheritance

Represents an inheritance hierarchy of classes with one
table per concrete class in the hierarchy.

Object-Relational Metadata Mapping Patterns

Metadata Mapping

Holds details of object-relational mapping in metadata.

Query Object

An object that represents a database query.

Repository

Mediates between the domain and data mapping layers using a
collection-like interface for accessing domain objects.

Web Presentation Patterns

Model View Controller

Splits user interface interaction into three distinct roles.

Page Controller

An object that handles a request for a specific
page or action on a Web site.

Front Controller

A controller that handles all requests for a Web site.

Template View

Renders information into HTML by embedding markers in an
HTML page.

Transform View

A view that processes domain data element by element and
transforms it into HTML.

Two Step View

Turns domain data into HTML in two steps: first by forming
some kind of logical page, then rendering the logical page into
HTML.

Application Controller

A centralized point for handling screen navigation and the
flow of an application.

Distribution Patterns

Remote Facade

Provides a coarse-grained facade on fine-grained objects to
improve efficiency over a network.

Data Transfer Object

An object that carries data between processes in order to
reduce the number of method calls.

Offline Concurrency Patterns

Optimistic Offline Lock

Prevents conflicts between concurrent business transactions
by detecting a conflict and rolling back the transaction.

Pessimistic Offline Lock

Prevents conflicts between concurrent business transactions
by allowing only one business transaction at a time to access
data.

Coarse-Grained Lock

Locks a set of related objects with a single lock.

Implicit Lock

Allows framework or layer supertype code to acquire offline
locks.

Session State Patterns

Client Session State

Stores session state on the client.

Server Session State

Keeps the session state on a server system in a serialized form

Database Session State

Stores session data as committed data in the database.

Base Patterns

Gateway

An object that encapsulates access to an external system or
resource.

Service Stub

Removes dependence upon problematic services during testing.
WSDL

Record Set

An in-memory representation of tabular data.

Mapper

An object that sets up a communication between two
independent objects.

Layer Supertype

A type that acts as the supertype for all types in its
layer.

Separated Interface

Defines an interface in a separate package from its
implementation.

Registry

A well-known object that other objects can use to find
common objects and services.

Value Object

A small simple object, like money or a date range, whose
equality isn't based on identity.

Money

Represents a monetary value.

Special Case

A subclass that provides special behavior for particular
cases.

Plugin

Links classes during configuration rather than
compilation.

Notes

This page had a design refresh in July 2024, but the content is still the
    same as its original 2003 publication.

Many of these sketch diagrams in the patterns demonstrate the rather poor
    GIF output of Visio at that time. The nice diagrams were redrawn for me by
    David Heinemeier Hansson