
# Redis

- [介绍](#introduction)
- [配置](#configuration)
    - [集群](#clusters)
    - [Predis](#predis)
    - [PhpRedis](#phpredis)
- [与Redis交互](#interacting-with-redis)
    - [事务](#transactions)
    - [管道命令](#pipelining-commands)
- [发布与订阅](#pubsub)

<a name="introduction"></a>
## 简介
[Redis](https://redis.io) 是一个开源的高级键值存储系统。由于键可以包含[字符串](https://redis.io/docs/data-types/strings/)、[哈希表](https://redis.io/docs/data-types/hashes/)、[列表](https://redis.io/docs/data-types/lists/)、[集合](https://redis.io/docs/data-types/sets/)和[有序集合](https://redis.io/docs/data-types/sorted-sets/)，因此它通常被称为数据结构服务器。

在将Redis与Laravel结合使用之前，我们建议您通过PECL安装并使用 [PhpRedis PHP](https://github.com/phpredis/phpredis)扩展。与用户级PHP包相比，此扩展的安装过程更为复杂，但对于大量使用Redis的应用程序而言，可能会带来更好的性能。如果您使用的是 [Laravel Sail](/docs/laravel/12.x/sail)，则此扩展已在应用程序的Docker容器中安装。

如果你无法安装 PhpRedis 扩展，可以通过 Composer 安装 predis/predis 包。Predis是一个完全用PHP编写的Redis客户端，不需要任何额外的扩展：

```shell
composer require predis/predis:^2.0
```

<a name="configuration"></a>
## 配置

您可以通过config/database.php配置文件来配置应用程序的Redis设置。在此文件中，您将看到一个redis数组，其中包含应用程序所使用的Redis服务器：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
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



在你的配置文件中定义的每个 Redis 服务器都必须有名称、主机和端口，除非你定义了单个 URL 来表示 Redis 连接：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
    ],

    'default' => [
        'url' => 'tcp://127.0.0.1:6379?database=0',
    ],

    'cache' => [
        'url' => 'tls://user:password@127.0.0.1:6380?database=1',
    ],

],
```

#### 配置连接协议

默认情况下，Redis 客户端在连接 Redis 服务器时会使用 `tcp` 协议；但是，你可以通过在 Redis 服务器的配置数组中指定 `scheme` 配置选项来使用 TLS / SSL 加密：

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

### 集群配置

如果你的应用使用 Redis 服务器集群，你应该在 Redis 配置的 `clusters` 键下定义这些集群。该配置键默认不存在，所以你需要在应用的 `config/database.php` 配置文件中创建它：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
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



默认情况下，由于 `options.cluster` 配置值设置为 `redis`，Laravel 会使用原生的 Redis 集群。Redis 集群是一个很好的默认选项，因为它能够优雅地处理故障转移。

Laravel 还支持在使用 Predis 时进行客户端分片（client-side sharding）。但是客户端分片不处理故障转移，因此它主要适用于可从其他主数据存储获取的临时缓存数据。

如果你希望使用客户端分片而不是原生 Redis 集群，可以在应用的 `config/database.php` 配置文件中移除 `options.cluster` 配置值：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'clusters' => [
        // ...
    ],

    // ...
],
```

### Predis

如果你希望应用通过 Predis 包与 Redis 交互，应确保 `REDIS_CLIENT` 环境变量的值为 `predis`：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'predis'),

    // ...
],
```

除了默认配置选项外，Predis 支持为每个 Redis 服务器定义额外的[连接参数](https://github.com/nrk/predis/wiki/Connection-Parameters)。要使用这些额外的配置选项，可以将它们添加到应用 `config/database.php` 中对应的 Redis 服务器配置：

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

### PhpRedis

默认情况下，Laravel 使用 PhpRedis 扩展与 Redis 通信。Laravel 用于与 Redis 通信的客户端由 `redis.client` 配置选项决定，该选项通常反映 `REDIS_CLIENT` 环境变量的值：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    // ...
],
```



除了默认配置选项外，PhpRedis 还支持以下额外的连接参数：`name`、`persistent`、`persistent_id`、`prefix`、`read_timeout`、`retry_interval`、`max_retries`、`backoff_algorithm`、`backoff_base`、`backoff_cap`、`timeout` 和 `context`。你可以将这些选项添加到 `config/database.php` 中的 Redis 服务器配置中：

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

#### Unix 套接字连接

Redis 连接也可以配置为使用 Unix 套接字而非 TCP。当应用程序和 Redis 实例在同一台服务器上时，这可以通过消除 TCP 开销来提高性能。要使用 Unix 套接字连接 Redis，请将 `REDIS_HOST` 环境变量设置为 Redis 套接字路径，并将 `REDIS_PORT` 环境变量设置为 `0`：

```env
REDIS_HOST=/run/redis/redis.sock
REDIS_PORT=0
```

#### PhpRedis 序列化与压缩

PhpRedis 扩展还可以配置使用多种序列化器和压缩算法。这些算法可以通过 Redis 配置中的 `options` 数组进行配置：

```php
'redis' => [

    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_').'_database_'),
        'serializer' => Redis::SERIALIZER_MSGPACK,
        'compression' => Redis::COMPRESSION_LZ4,
    ],

    // ...
],
```

目前支持的序列化器包括：`Redis::SERIALIZER_NONE`（默认）、`Redis::SERIALIZER_PHP`、`Redis::SERIALIZER_JSON`、`Redis::SERIALIZER_IGBINARY` 和 `Redis::SERIALIZER_MSGPACK`。



支持的压缩算法包括：`Redis::COMPRESSION_NONE`（默认）、`Redis::COMPRESSION_LZF`、`Redis::COMPRESSION_ZSTD` 和 `Redis::COMPRESSION_LZ4`。

## 与 Redis 交互

你可以通过调用 `Redis` [Facade](/docs/laravel/12.x/facades) 上的各种方法与 Redis 进行交互。`Redis` Facade 支持动态方法，这意味着你可以在 Facade 上调用任意 [Redis 命令](https://redis.io/commands)，命令会直接传递给 Redis。在这个示例中，我们通过调用 `Redis` Facade 的 `get` 方法来执行 Redis 的 `GET` 命令：

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

如上所述，你可以在 `Redis` Facade 上调用 Redis 的任意命令。Laravel 使用魔术方法将命令传递给 Redis 服务器。如果某个 Redis 命令需要参数，你应当将参数传递给 Facade 对应的方法：

```php
use Illuminate\Support\Facades\Redis;

Redis::set('name', 'Taylor');

$values = Redis::lrange('names', 5, 10);
```

或者，你可以使用 `Redis` Facade 的 `command` 方法向服务器发送命令，第一个参数为命令名称，第二个参数为参数数组：

```php
$values = Redis::command('lrange', ['name', 5, 10]);
```

#### 使用多个 Redis 连接

你的应用程序 `config/database.php` 配置文件允许定义多个 Redis 连接/服务器。你可以使用 `Redis` Facade 的 `connection` 方法获取特定 Redis 连接：

```php
$redis = Redis::connection('connection-name');
```



要获取默认 Redis 连接的实例，你可以调用 `connection` 方法而不传递任何额外参数：

```php
$redis = Redis::connection();
```

### 事务

`Redis` Facade 的 `transaction` 方法提供了对 Redis 原生 `MULTI` 和 `EXEC` 命令的便捷封装。`transaction` 方法只接受一个闭包作为参数。该闭包会接收一个 Redis 连接实例，你可以在闭包中向该实例发出任意命令。闭包内发出的所有 Redis 命令将作为一个单一的原子事务执行：

```php
use Redis;
use Illuminate\Support\Facades;

Facades\Redis::transaction(function (Redis $redis) {
    $redis->incr('user_visits', 1);
    $redis->incr('total_visits', 1);
});
```

> [!警告]
> 定义 Redis 事务时，你不能从 Redis 连接中检索任何值。请记住，事务是作为单一原子操作执行的，并且直到整个闭包完成执行命令后才会真正执行。

#### Lua 脚本

`eval` 方法提供了另一种方式，可以在单一原子操作中执行多个 Redis 命令。不过，`eval` 方法的好处是可以在操作过程中与 Redis 键值进行交互和检查。Redis 脚本是用 [Lua 编程语言](https://www.lua.org) 编写的。

`eval` 方法刚开始可能会让人有些害怕，但我们可以通过一个基本示例来入门。`eval` 方法需要几个参数：首先，将 Lua 脚本（字符串形式）传递给方法；其次，传递脚本要操作的键数量（整数）；第三，传递这些键的名称；最后，可以传递脚本中需要访问的其他附加参数。



在这个例子中，我们将增加一个计数器的值，检查它的新值，如果第一个计数器的值大于五，则增加第二个计数器的值。最后返回第一个计数器的值：

```php
$value = Redis::eval(<<<'LUA'
    local counter = redis.call("incr", KEYS[1])

    if counter > 5 then
        redis.call("incr", KEYS[2])
    end

    return counter
LUA, 2, 'first-counter', 'second-counter');
```

> [!警告]
> 有关 Redis 脚本的更多信息，请查阅 [Redis 文档](https://redis.io/commands/eval)

### 命令流水线


有时你可能需要执行几十个 Redis 命令。与每条命令都单独发送网络请求相比，你可以使用 `pipeline` 方法。`pipeline` 方法接收一个闭包参数，该闭包会接收一个 Redis 实例。你可以向该实例发出所有命令，这些命令会一次性发送到 Redis 服务器，从而减少网络请求次数。命令仍会按照发出的顺序执行：

```php
use Redis;
use Illuminate\Support\Facades;

Facades\Redis::pipeline(function (Redis $pipe) {
    for ($i = 0; $i < 1000; $i++) {
        $pipe->set("key:$i", $i);
    }
});
```

## 发布/订阅（Pub / Sub）

Laravel 提供了对 Redis `publish` 和 `subscribe` 命令的便捷接口。这些命令允许你在指定的“频道”上监听消息。你可以从另一个应用程序或者使用其他编程语言向该频道发布消息，实现应用和进程间的通信。

首先，我们使用 `subscribe` 方法设置一个频道监听器。由于调用 `subscribe` 方法会启动一个长时间运行的进程，因此通常将其放在 [Artisan 命令](/docs/laravel/12.x/artisan) 中：

```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Redis;

class RedisSubscribe extends Command
{
    /**
     * 控制台命令的名称和签名
     *
     * @var string
     */
    protected $signature = 'redis:subscribe';

    /**
     * 控制台命令的描述
     *
     * @var string
     */
    protected $description = '订阅一个 Redis 频道';

    /**
     * 执行控制台命令
     */
    public function handle(): void
    {
        Redis::subscribe(['test-channel'], function (string $message) {
            echo $message;
        });
    }
}

```



现在我们可以使用 `publish` 方法向频道发布消息：

```php
use Illuminate\Support\Facades\Redis;

Route::get('/publish', function () {
    // ...

    Redis::publish('test-channel', json_encode([
        'name' => 'Adam Wathan'
    ]));
});
```

#### 通配符订阅

使用 `psubscribe` 方法，你可以订阅一个通配符频道，这在捕获所有频道的消息时非常有用。频道名称会作为第二个参数传递给闭包：

```php
Redis::psubscribe(['*'], function (string $message, string $channel) {
    echo $message;
});

Redis::psubscribe(['users.*'], function (string $message, string $channel) {
    echo $message;
});
```
