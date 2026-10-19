# MongoDB

- [简介](#introduction)
- [安装](#installation)
    - [MongoDB 驱动](#mongodb-driver)
    - [启动 MongoDB 服务器](#starting-a-mongodb-server)
    - [安装 Laravel MongoDB 扩展包](#install-the-laravel-mongodb-package)
- [配置](#configuration)
- [功能特性](#features)

<a name="introduction"></a>
## 简介

[MongoDB](https://www.mongodb.com/resources/products/fundamentals/why-use-mongodb) 是最受欢迎的 NoSQL 文档型数据库之一。它能够承受高写入负载，适用于数据分析或物联网场景；同时易于配置支持自动故障转移的副本集，提供高可用性。它还可以通过分片实现水平扩展，并提供强大的查询语言，用于聚合、文本搜索和地理空间查询。

SQL 数据库以表中的行或列存储数据，而 MongoDB 中的每条记录都是一个 BSON 文档，即数据的二进制表示形式。应用可以以 JSON 格式获取这些信息。MongoDB 支持多种数据类型，包括文档、数组、内嵌文档和二进制数据。

在 Laravel 中使用 MongoDB 前，建议通过 Composer 安装 `mongodb/laravel-mongodb` 扩展包。`laravel-mongodb` 由 MongoDB 官方维护。PHP 可通过 MongoDB 驱动原生支持 MongoDB，而 [Laravel MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/) 扩展包则进一步提供了与 Eloquent 及其他 Laravel 功能的集成：

```shell
composer require mongodb/laravel-mongodb
```

<a name="installation"></a>
## 安装

<a name="mongodb-driver"></a>
### MongoDB 驱动

连接 MongoDB 数据库需要 `mongodb` PHP 扩展。如果你使用 [Laravel Herd](https://herd.laravel.com) 在本地开发，或通过 `php.new` 安装 PHP，系统中已经安装了该扩展。如需手动安装，可以使用 PECL：

```shell
pecl install mongodb
```

你也可以使用 PHP 官方扩展安装工具 [PIE](https://github.com/php/pie) 安装该扩展：

```shell
pie install mongodb/mongodb-extension
```

关于 MongoDB PHP 扩展安装的更多信息，请参阅 [MongoDB PHP 扩展安装指南](https://www.php.net/manual/en/mongodb.installation.php)。

<a name="starting-a-mongodb-server"></a>
### 启动 MongoDB 服务器

你可以使用 MongoDB 社区版在本地运行 MongoDB。它支持安装在 Windows、macOS、Linux 上，也可以通过 Docker 容器运行。具体安装方法请参阅 [MongoDB 社区版官方安装指南](https://docs.mongodb.com/manual/administration/install-community/)。

你可以在 `.env` 文件中设置 MongoDB 服务器的连接字符串：

```ini
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DATABASE="laravel_app"
```

如果需要在云端托管 MongoDB，可以考虑使用 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)。
要从本地应用访问 MongoDB Atlas 集群，需要[在集群的网络设置中将你的 IP 地址](https://www.mongodb.com/docs/atlas/security/add-ip-address-to-list/)添加到项目的 IP 访问列表。

MongoDB Atlas 的连接字符串也可以在 `.env` 文件中设置：

```ini
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority"
MONGODB_DATABASE="laravel_app"
```

<a name="install-the-laravel-mongodb-package"></a>
### 安装 Laravel MongoDB 扩展包

最后，使用 Composer 安装 Laravel MongoDB 扩展包：

```shell
composer require mongodb/laravel-mongodb
```

> [!NOTE]
> 如果未安装 `mongodb` PHP 扩展，扩展包将无法安装。命令行与 Web 服务器使用的 PHP 配置可能不同，请确保两者均已启用该扩展。

<a name="configuration"></a>
## 配置

你可以在应用的 `config/database.php` 配置文件中设置 MongoDB 连接。在该文件中添加一个使用 `mongodb` 驱动的 `mongodb` 连接：

```php
'connections' => [
    'mongodb' => [
        'driver' => 'mongodb',
        'dsn' => env('MONGODB_URI', 'mongodb://localhost:27017'),
        'database' => env('MONGODB_DATABASE', 'laravel_app'),
    ],
],
```

<a name="features"></a>
## 功能特性

完成配置后，你可以在应用中通过 `mongodb` 扩展包和数据库连接使用以下功能：

- [使用 Eloquent](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/eloquent-models/) 将模型存储在 MongoDB 集合中。除了标准 Eloquent 功能，Laravel MongoDB 扩展包还提供了内嵌关系等功能。你也可以通过该扩展包直接访问 MongoDB 驱动，执行原生查询和聚合管道等操作。
- [通过查询构造器编写复杂查询](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/query-builder/)。
- [相似度搜索或向量搜索](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/fundamentals/vector-search/)：使用向量嵌入和 Eloquent 的 `vectorSearch` 方法。
- `mongodb` [缓存驱动](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/cache/)针对 MongoDB 特性进行了优化，例如通过 TTL 索引自动清除过期缓存项。
- [派发和处理队列任务](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/queues/)：使用 `mongodb` 队列驱动。
- [在 GridFS 中存储文件](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/filesystems/)：通过 [Flysystem 的 GridFS 适配器](https://flysystem.thephpleague.com/docs/adapter/gridfs/)。
- [全文搜索](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/scout/)：使用 `mongodb` Scout 引擎。
- 大多数使用数据库连接或 Eloquent 的第三方扩展包都可以与 MongoDB 配合使用。

要进一步了解如何在 Laravel 中使用 MongoDB，请参阅 MongoDB 的[快速入门指南](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/quick-start/)。
