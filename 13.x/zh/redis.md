# Redis

- [简介](#introduction)
- [配置](#configuration)
    - [集群](#clusters)
    - [Predis](#predis)
    - [PhpRedis](#phpredis)
- [与 Redis 交互](#interacting-with-redis)
    - [事务](#transactions)
    - [命令流水线](#pipelining-commands)
- [发布与订阅](#pubsub)

<a name="introduction"></a>
## 简介

[Redis](https://redis.io) 是一个开源的高级键值存储系统。由于键可以存储[字符串](https://redis.io/docs/latest/develop/data-types/strings/)、[哈希表](https://redis.io/docs/latest/develop/data-types/hashes/)、[列表](https://redis.io/docs/latest/develop/data-types/lists/)、[集合](https://redis.io/docs/latest/develop/data-types/sets/)和[有序集合](https://redis.io/docs/latest/develop/data-types/sorted-sets/)，它也常被称为数据结构服务器。

在 Laravel 中使用 Redis 前，建议先通过 PECL 安装 [PhpRedis](https://github.com/phpredis/phpredis) PHP 扩展。与纯 PHP 包相比，该扩展的安装过程更复杂，但对于大量使用 Redis 的应用，可能提供更好的性能。如果你使用 [Laravel Sail](/docs/{{version}}/sail)，应用的 Docker 容器中已经安装了此扩展。

如果无法安装 PhpRedis 扩展，可以通过 Composer 安装 `predis/predis` 包。Predis 是一个完全用 PHP 编写的 Redis 客户端，无需额外扩展：

```shell
composer require predis/predis
```

<a name="configuration"></a>
## 配置

你可以在 `config/database.php` 配置文件中设置应用的 Redis 连接。该文件中的 `redis` 数组包含应用使用的 Redis 服务器配置：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug((string) env('APP_NAME', 'laravel')).'-database-'),
    ],

    'default' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_DB', '0'),
    ],

    'cache' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'username' => env('REDIS_USERNAME'),
        'password' => env('REDIS_PASSWORD'),
        'port' => env('REDIS_PORT', '6379'),
        'database' => env('REDIS_CACHE_DB', '1'),
    ],

],
```

配置文件中定义的每个 Redis 服务器都需要指定名称、主机和端口，除非使用一个 URL 来表示整个 Redis 连接：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug((string) env('APP_NAME', 'laravel')).'-database-'),
    ],

    'default' => [
        'url' => 'tcp://127.0.0.1:6379?database=0',
    ],

    'cache' => [
        'url' => 'tls://user:password@127.0.0.1:6380?database=1',
    ],

],
```

<a name="configuring-the-connection-scheme"></a>
#### 配置连接协议

默认情况下，Redis 客户端使用 `tcp` 协议连接 Redis 服务器。你可以在服务器的配置数组中设置 `scheme` 选项，启用 TLS / SSL 加密：

```php
'default' => [
    'scheme' => 'tls',
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
],
```

<a name="clusters"></a>
### 集群

如果应用使用 Redis 服务器集群，应在 Redis 配置的 `clusters` 键下定义集群。该配置键默认不存在，需要在应用的 `config/database.php` 配置文件中添加：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug((string) env('APP_NAME', 'laravel')).'-database-'),
    ],

    'clusters' => [
        'default' => [
            [
                'url' => env('REDIS_URL'),
                'host' => env('REDIS_HOST', '127.0.0.1'),
                'username' => env('REDIS_USERNAME'),
                'password' => env('REDIS_PASSWORD'),
                'port' => env('REDIS_PORT', '6379'),
                'database' => env('REDIS_DB', '0'),
            ],
        ],
    ],

    // ...
],
```

默认情况下，`options.cluster` 的值为 `redis`，因此 Laravel 会使用原生 Redis 集群。它能够妥善处理故障转移，是合适的默认选择。

使用 Predis 时，Laravel 还支持客户端分片。但客户端分片不处理故障转移，因此主要适用于临时缓存数据，且这些数据仍可从另一个主数据存储中获取。

要改用客户端分片，可以从应用的 `config/database.php` 配置文件中移除 `options.cluster` 配置项：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'clusters' => [
        // ...
    ],

    // ...
],
```

<a name="predis"></a>
### Predis

要让应用通过 Predis 包与 Redis 交互，请确保 `REDIS_CLIENT` 环境变量的值为 `predis`：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'predis'),

    // ...
],
```

除了默认配置选项，Predis 还支持为每个 Redis 服务器定义额外的[连接参数](https://github.com/nrk/predis/wiki/Connection-Parameters)。要使用这些选项，请将其添加到应用 `config/database.php` 文件中对应的 Redis 服务器配置：

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'read_write_timeout' => 60,
],
```

<a name="phpredis"></a>
### PhpRedis

默认情况下，Laravel 使用 PhpRedis 扩展与 Redis 通信。所使用的客户端由 `redis.client` 配置项决定，该配置项通常取自 `REDIS_CLIENT` 环境变量：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    // ...
],
```

除了默认配置选项，PhpRedis 还支持以下连接参数：`name`、`persistent`、`persistent_id`、`prefix`、`read_timeout`、`retry_interval`、`max_retries`、`backoff_algorithm`、`backoff_base`、`backoff_cap`、`timeout` 和 `context`。你可以将这些选项添加到 `config/database.php` 文件中的 Redis 服务器配置：

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'read_timeout' => 60,
    'context' => [
        // 'auth' => ['username', 'secret'],
        // 'stream' => ['verify_peer' => false],
    ],
],
```

<a name="retry-and-backoff-configuration"></a>
#### 重试与退避配置

`retry_interval`、`max_retries`、`backoff_algorithm`、`backoff_base` 和 `backoff_cap` 选项用于配置 PhpRedis 客户端重新连接 Redis 服务器的方式。支持的退避算法包括：`default`、`decorrelated_jitter`、`equal_jitter`、`exponential`、`uniform` 和 `constant`：

```php
'default' => [
    'url' => env('REDIS_URL'),
    'host' => env('REDIS_HOST', '127.0.0.1'),
    'username' => env('REDIS_USERNAME'),
    'password' => env('REDIS_PASSWORD'),
    'port' => env('REDIS_PORT', '6379'),
    'database' => env('REDIS_DB', '0'),
    'max_retries' => env('REDIS_MAX_RETRIES', 3),
    'backoff_algorithm' => env('REDIS_BACKOFF_ALGORITHM', 'decorrelated_jitter'),
    'backoff_base' => env('REDIS_BACKOFF_BASE', 100),
    'backoff_cap' => env('REDIS_BACKOFF_CAP', 1000),
],
```

发生短暂的连接故障后，Laravel 会自动重试一次安全的读取命令。你可以使用 `command_retries` 选项，配置所有 Redis 命令的重试次数：

```php
'default' => [
    // ...
    'command_retries' => env('REDIS_COMMAND_RETRIES', 0),
],
```

Predis 3.4.0 及更高版本通过 `Retry` 类内置了重试和退避支持。你可以使用 `max_retries` 选项配置重试次数，使用 `retry` 选项配置退避策略。`retry` 应为一个数组，以以下策略类之一作为键：`NoBackoff`、`EqualBackoff` 或 `ExponentialBackoff`：

```php
use Predis\Retry\Strategy\ExponentialBackoff;

'default' => [
    'url' => env('REDIS_URL'),
    // ...
    'retry' => [
        ExponentialBackoff::class => [
            env('REDIS_BACKOFF_BASE', 100),
            env('REDIS_BACKOFF_CAP', 1000),
            true, // 启用抖动……
        ],
    ],
    'max_retries' => env('REDIS_MAX_RETRIES', 3),
],
```

将 Predis 用于 Redis 集群时，可以在集群配置的 `parameters` 选项中定义重试配置：

```php
use Predis\Retry\Strategy\NoBackoff;

'clusters' => [
    'default' => [
        // ...
    ],
],

'options' => [
    'cluster' => env('REDIS_CLUSTER', 'redis'),
    'parameters' => [
        'retry' => [
            NoBackoff::class => [],
        ],
        'max_retries' => env('REDIS_MAX_RETRIES', 3),
    ],
],
```

<a name="unix-socket-connections"></a>
#### Unix 套接字连接

Redis 连接也可以使用 Unix 套接字。当 Redis 实例与应用位于同一台服务器上时，这样可以省去 TCP 连接的开销，提高性能。要使用 Unix 套接字，请将 `REDIS_HOST` 环境变量设为 Redis 套接字路径，并将 `REDIS_PORT` 设为 `0`：

```env
REDIS_HOST=/run/redis/redis.sock
REDIS_PORT=0
```

<a name="phpredis-serialization"></a>
#### PhpRedis 序列化与压缩

PhpRedis 扩展支持多种序列化器和压缩算法，可以通过 Redis 配置中的 `options` 数组进行设置：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug((string) env('APP_NAME', 'laravel')).'-database-'),
        'serializer' => Redis::SERIALIZER_MSGPACK,
        'compression' => Redis::COMPRESSION_LZ4,
    ],

    // ...
],
```

目前支持的序列化器包括：`Redis::SERIALIZER_NONE`（默认）、`Redis::SERIALIZER_PHP`、`Redis::SERIALIZER_JSON`、`Redis::SERIALIZER_IGBINARY` 和 `Redis::SERIALIZER_MSGPACK`。

支持的压缩算法包括：`Redis::COMPRESSION_NONE`（默认）、`Redis::COMPRESSION_LZF`、`Redis::COMPRESSION_ZSTD` 和 `Redis::COMPRESSION_LZ4`。

<a name="interacting-with-redis"></a>
## 与 Redis 交互

你可以调用 `Redis` [门面](/docs/{{version}}/facades)上的各种方法与 Redis 交互。`Redis` 门面支持动态方法，因此你可以在门面上调用任意 [Redis 命令](https://redis.io/commands)，命令会直接传递给 Redis。以下示例通过调用 `Redis` 门面的 `get` 方法，执行 Redis 的 `GET` 命令：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Redis;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * 显示指定用户的资料。
     */
    public function show(string $id): View
    {
        return view('user.profile', [
            'user' => Redis::get('user:profile:'.$id)
        ]);
    }
}
```

如上所述，你可以在 `Redis` 门面上调用任意 Redis 命令。Laravel 通过魔术方法将命令传递给 Redis 服务器。如果命令需要参数，请将它们传给门面上对应的方法：

```php
use Illuminate\Support\Facades\Redis;

Redis::set('name', 'Taylor');

$values = Redis::lrange('names', 5, 10);
```

你也可以使用 `Redis` 门面的 `command` 方法向服务器发送命令。该方法的第一个参数是命令名称，第二个参数是参数值数组：

```php
$values = Redis::command('lrange', ['name', 5, 10]);
```

<a name="using-multiple-redis-connections"></a>
#### 使用多个 Redis 连接

你可以在应用的 `config/database.php` 配置文件中定义多个 Redis 连接或服务器，再通过 `Redis` 门面的 `connection` 方法获取指定连接：

```php
$redis = Redis::connection('connection-name');
```

调用 `connection` 方法时不传参数，即可获取默认 Redis 连接的实例：

```php
$redis = Redis::connection();
```

<a name="transactions"></a>
### 事务

`Redis` 门面的 `transaction` 方法封装了 Redis 原生的 `MULTI` 和 `EXEC` 命令。该方法只接受一个闭包参数，闭包会接收一个 Redis 连接实例，你可以向该实例发送任意命令。闭包内发送的所有 Redis 命令都会在同一个原子事务中执行：

```php
use Redis;
use Illuminate\Support\Facades;

Facades\Redis::transaction(function (Redis $redis) {
    $redis->incr('user_visits', 1);
    $redis->incr('total_visits', 1);
});
```

> [!WARNING]
> 定义 Redis 事务时，不能从 Redis 连接中读取值。事务会作为一个原子操作执行，只有整个闭包完成命令的提交后，这些命令才会真正执行。

#### Lua 脚本

`eval` 方法也可以在一个原子操作中执行多条 Redis 命令，并且允许在操作过程中读取和修改 Redis 键值。Redis 脚本使用 [Lua 编程语言](https://www.lua.org)编写。

初次接触 `eval` 可能觉得复杂，我们先看一个基本示例。该方法依次接受以下参数：Lua 脚本字符串、脚本要操作的键的数量（整数），以及这些键的名称。最后，还可以传入脚本中需要访问的其他参数。

以下示例先递增第一个计数器并检查新值。如果新值大于 5，就递增第二个计数器，最后返回第一个计数器的值：

```php
$value = Redis::eval(<<<'LUA'
    local counter = redis.call("incr", KEYS[1])

    if counter > 5 then
        redis.call("incr", KEYS[2])
    end

    return counter
LUA, 2, 'first-counter', 'second-counter');
```

> [!WARNING]
> 关于 Redis 脚本的更多信息，请参阅 [Redis 文档](https://redis.io/commands/eval)。

<a name="pipelining-commands"></a>
### 命令流水线

有时需要执行数十条 Redis 命令。你可以使用 `pipeline` 方法，将命令一次性发送到 Redis 服务器，减少网络往返次数。该方法接受一个闭包参数，闭包会接收一个 Redis 实例，你可以向该实例发送所有命令。命令仍会按发送顺序执行：

```php
use Redis;
use Illuminate\Support\Facades;

Facades\Redis::pipeline(function (Redis $pipe) {
    for ($i = 0; $i < 1000; $i++) {
        $pipe->set("key:$i", $i);
    }
});
```

<a name="pubsub"></a>
## 发布与订阅

Laravel 为 Redis 的 `publish` 和 `subscribe` 命令提供了便捷接口。你可以监听指定「频道」上的消息，也可以从其他应用，甚至使用其他编程语言向该频道发布消息，方便应用和进程之间通信。

首先，使用 `subscribe` 方法设置频道监听器。由于调用该方法会启动一个长时间运行的进程，我们将它放在 [Artisan 命令](/docs/{{version}}/artisan)中：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Redis;

class RedisSubscribe extends Command
{
    /**
     * 控制台命令的名称和签名。
     *
     * @var string
     */
    protected $signature = 'redis:subscribe';

    /**
     * 控制台命令的描述。
     *
     * @var string
     */
    protected $description = 'Subscribe to a Redis channel';

    /**
     * 执行控制台命令。
     */
    public function handle(): void
    {
        Redis::subscribe(['test-channel'], function (string $message) {
            echo $message;
        });
    }
}
```

现在可以使用 `publish` 方法向频道发布消息：

```php
use Illuminate\Support\Facades\Redis;

Route::get('/publish', function () {
    // ...

    Redis::publish('test-channel', json_encode([
        'name' => 'Adam Wathan'
    ]));
});
```

<a name="wildcard-subscriptions"></a>
#### 通配符订阅

使用 `psubscribe` 方法，可以通过通配符订阅频道，从而接收所有匹配频道的消息。频道名称会作为第二个参数传给闭包：

```php
Redis::psubscribe(['*'], function (string $message, string $channel) {
    echo $message;
});

Redis::psubscribe(['users.*'], function (string $message, string $channel) {
    echo $message;
});
```
