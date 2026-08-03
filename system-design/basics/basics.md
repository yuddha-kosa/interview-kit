System design:

1. Cassandra/scylla DB
2. DynamoDB/DragonFly
3. MongoDB
4. CockroachDB
5. Relation Databases (Postgres(indexing, join etc))
6. Elastic - inverted indexes/TypeSense
7. InfluxDB- ClickHouse
8. Redis
9. MemCache
10. Blob storage - (S3)
11. Kafka/RedPanda
12. RabbitMQ
13. SQS
14. Orchestration technology like conductor
15. CDN
16. Web socket
17. APIs
18. HTTP
19. GRPC
20. GraphQL
21. Gateways (Kong)
22. Load Balancer
23. DNS (Networking- subnet, networking layers)
24. Firewall
25. Microservice architecture
26. Service oriented architecture
27. Security (SHA, signature verification, symmetric and asymmetric encryption (ECDH, DSA, RSA))
28. Kubernetes
29. Docker
30. GA
31. HPA
32. Node scaler
33. CAP - consistently, availability and partition tolerance
34. Fault tolerance 
35. JWT- token
36. OTel
37. Scale (Multi write, read)
38. Back pressure handling
39. Throttling
40. Sharding- hash-based sharding, Range-based, Directory-based sharding, hotspots, adding new nodes
41. Partitioning (partition vs sharding)
42. Caching
43. Indexing- partial, composite, GIN, GIST, B-Tree, geospatial indexes, hash index
44. Consistent hashing
45. Data modelling
46. Vector databases
47. Zookeeper
48. Flink ??
49. SnowFlake
50. Raft consensus  algorithm
51. Redundancy, failover, and recovery mechanisms.
52. Fanout-on-read vs fanout-on-write
53. Cursor vs offset pagination
54. Rate limiting
55. FK constraints
56. Normalization and denormalization.
57. Cache stampede, In-process caching 
58. Fuzzy logic




Server-Sent Events (SSE): SSE is unidirectional - the client makes an initial HTTP request to open the connection, and then the server pushes data down that connection (like live scores or notifications). The client can't send additional data over the same SSE connection

WebSockets: They handle true bidirectional communication where both sides send messages freely (like chat or live collaboration). SSE is simpler to implement and works better with standard HTTP infrastructure, but WebSockets are necessary when clients need to push data back to the server frequently.

gRPC: It is used for internal service-to-service communication when performance is critical. It uses binary serialization and HTTP/2, making it significantly faster than JSON over HTTP.

Load balancing: Layer 7 load balancers operate at the application level and can route based on the actual HTTP request content. You can send API calls to one service and web page requests to another. Layer 4 load balancers work at the TCP level and are faster but dumber. They just distribute connections without looking at the content. For WebSockets, you typically need Layer 4 balancing because you're maintaining a persistent TCP connection.


Offset pagination uses a fixed starting point and skips a specific number of records (e.g., "skip 100, take 10").
Cursor pagination uses a unique identifier from the last retrieved item as a marker to fetch the next batch (e.g., "give me 10 items after ID 100").

A foreign key constraint is a database rule that ensures "referential integrity" between two tables. It links a column (or group of columns) in one table (the child) to a unique column—usually the primary key—in another table (the parent).Why use a foreign key constraint?Essentially, it prevents you from making mistakes that would break the connection between your data.Prevents Orphaned Records: It ensures you can't add a record to the child table if its reference doesn't exist in the parent table. For example, you can't create an Order for a Customer ID that isn't in your Customers list.Blocks Invalid Deletions: It stops you from deleting a record in the parent table if there are still records in the child table pointing to it.Maintains Consistency: It keeps your relational data accurate across multiple tables.
Rules that define what happens when a parent record is updated or deleted, such as CASCADE (auto-delete children) or RESTRICT (block the action).

 Geospatial queries in Postgres, PostGIS is a popular extension. These external indexes typically sync from your primary database via change data capture (CDC), meaning the search index will lag slightly behind the primary database. The data you read from the search index is going to be stale by some small amount, but for search use cases that's almost always acceptable. The tradeoff is worth it because it lets you search in ways your main database can't handle.

 Sharding creates new problems you need to address. Cross-shard transactions become nearly impossible, so you need to design your shard boundaries to avoid them. If a user transfer in your banking app requires updating accounts on different shards, you'll need distributed transactions or sagas, which are complex and slow.
 Hot spots happen when one shard gets disproportionate traffic (think Taylor Swift's shard getting hammered while others sit idle). And resharding is painful. You can't just add a new shard without moving massive amounts of data around.