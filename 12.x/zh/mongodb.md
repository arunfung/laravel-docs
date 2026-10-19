
# MongoDB

- [简介](#introduction)
- [安装](#installation)
    - [MongoDB驱动](#mongodb-driver)
    - [启动MongoDB服务](#starting-a-mongodb-server)
    - [安装Laravel MongoDB包](#install-the-laravel-mongodb-package)
- [配置](#configuration)
- [功能特性](#features)

<a name="introduction"></a>
## 简介

[MongoDB](https://www.mongodb.com/resources/products/fundamentals/why-use-mongodb)是最受欢迎的NoSQL文档型数据库之一，以其高写入负载（适用于分析或物联网场景）和高可用性（轻松设置自动故障转移的副本集）著称。它还能轻松实现分片以支持水平扩展，并拥有强大的查询语言支持聚合、文本搜索和地理空间查询。

与SQL数据库以行列形式存储数据不同，MongoDB中的每条记录都是以BSON（数据的二进制表示形式）格式存储的文档。应用程序可以JSON格式检索这些信息，支持多种数据类型包括文档、数组、嵌套文档和二进制数据等。

在Laravel中使用MongoDB前，我们推荐通过Composer安装`mongodb/laravel-mongodb`扩展包。该包由MongoDB官方维护，虽然PHP原生支持MongoDB驱动，但[Laravel MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/)扩展包提供了与Eloquent等Laravel功能的深度集成：

```shell
composer require mongodb/laravel-mongodb
```

<a name="installation"></a>
## 安装

<a name="mongodb-driver"></a>
### MongoDB驱动

连接MongoDB数据库需要`mongodb` PHP扩展。若使用[Laravel Herd](https://herd.laravel.com)本地开发或通过`php.new`安装PHP，系统已预装该扩展。如需手动安装可通过PECL：

```shell
pecl install mongodb
```

更多关于安装MongoDB PHP扩展的信息，请参阅[MongoDB PHP扩展安装指南](https://www.php.net/manual/en/mongodb.installation.php)。

<a name="starting-a-mongodb-server"></a>
### 启动MongoDB服务

MongoDB社区版可用于本地运行MongoDB，支持Windows、macOS、Linux系统及Docker容器安装。具体安装方法请参考[官方MongoDB社区版安装指南](https://docs.mongodb.com/manual/administration/install-community/)。

在`.env`文件中配置MongoDB服务器连接字符串：

```ini
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DATABASE="laravel_app"
```

如需云端托管MongoDB，推荐使用[MongoDB Atlas](https://www.mongodb.com/cloud/atlas)。若要从本地应用访问MongoDB Atlas集群，需[在集群网络设置中添加您的IP地址](https://www.mongodb.com/docs/atlas/security/add-ip-address-to-list/)到项目IP访问列表。

MongoDB Atlas连接字符串同样可在`.env`中配置：

```ini
MONGODB_URI="mongodb+srv://<用户名>:<密码>@<集群>.mongodb.net/<数据库名>?retryWrites=true&w=majority"
MONGODB_DATABASE="laravel_app"
```

<a name="install-the-laravel-mongodb-package"></a>
### 安装Laravel MongoDB扩展包

最后使用Composer安装Laravel MongoDB扩展包：

```shell
composer require mongodb/laravel-mongodb
```

> [!注意]
> 若未安装`mongodb` PHP扩展，扩展包安装将失败。请注意PHP的CLI配置与Web服务器配置可能不同，需确保两个环境均已启用该扩展。

<a name="configuration"></a>
## 配置

您可以通过应用的`config/database.php`配置文件来配置MongoDB连接。在该文件中添加使用`mongodb`驱动的连接配置：

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

完成配置后，您可以在应用中使用`mongodb`扩展包和数据库连接来获得以下强大功能：

- [使用Eloquent](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/eloquent-models/)将模型存储在MongoDB集合中。除了标准Eloquent功能外，Laravel MongoDB包还提供了嵌入式关系等额外特性，并可直接访问MongoDB驱动执行原始查询和聚合管道等操作
- [使用查询构建器](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/query-builder/)编写复杂查询
- 专为MongoDB优化的[缓存驱动](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/cache/)，利用TTL索引自动清除过期缓存
- 使用`mongodb`[队列驱动](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/queues/)分发和处理队列任务
- 通过[Flysystem的GridFS适配器](https://flysystem.thephpleague.com/docs/adapter/gridfs/)[在GridFS中存储文件](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/filesystems/)
- 大多数使用数据库连接或Eloquent的第三方包均可与MongoDB兼容

要了解更多关于MongoDB和Laravel的使用方法，请参阅MongoDB的[快速入门指南](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/quick-start/)。
