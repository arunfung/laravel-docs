# 并发

- [介绍](#introduction)
- [运行并发任务](#running-concurrent-tasks)
    - [命名结果](#named-results)
    - [任务超时](#task-timeouts)
- [延迟并发任务](#deferring-concurrent-tasks)

<a name="introduction"></a>
## 介绍

有时，你可能需要执行多个互不依赖的耗时任务。在许多情况下，并发执行这些任务可以显著提高性能。Laravel 的 `Concurrency` 门面提供了一个简单、便捷的 API，用于并发执行闭包。

<a name="how-it-works"></a>
#### 工作原理

Laravel 通过序列化给定的闭包，并将其分派给一个隐藏的 Artisan CLI 命令来实现并发。该命令会反序列化这些闭包，并在各自的 PHP 进程中调用它们。闭包调用完成后，结果值会被序列化并传回父进程。

`Concurrency` 门面支持三种驱动：`process`（默认）、`fork` 和 `sync`。

与默认的 `process` 驱动相比，`fork` 驱动性能更好，但它只能在 PHP 的 CLI 上下文中使用，因为 PHP 不支持在 Web 请求期间创建进程分支。使用 `fork` 驱动之前，需要安装 `spatie/fork` 扩展包：

```shell
composer require spatie/fork
```

`sync` 驱动主要用于测试场景。当你希望禁用所有并发，并直接在父进程中依次执行给定的闭包时，可以使用该驱动。

<a name="running-concurrent-tasks"></a>
## 运行并发任务

要运行并发任务，可以调用 `Concurrency` 门面的 `run` 方法。`run` 方法接受一个闭包数组，这些闭包将在子 PHP 进程中同时执行：

```php
use Illuminate\Support\Facades\Concurrency;
use Illuminate\Support\Facades\DB;

[$userCount, $orderCount] = Concurrency::run([
    fn () => DB::table('users')->count(),
    fn () => DB::table('orders')->count(),
]);
```

要使用指定的驱动，可以调用 `driver` 方法：

```php
$results = Concurrency::driver('fork')->run(...);
```

或者，如果要更改默认的并发驱动，应通过 `config:publish` Artisan 命令发布 `concurrency` 配置文件，并更新该文件中的 `default` 选项：

```shell
php artisan config:publish concurrency
```

<a name="named-results"></a>
### 命名结果

如果希望按名称而不是按位置访问并发任务的结果，可以提供一个由闭包组成的关联数组。每个结果都将使用其对应闭包的相同键名返回：

```php
use Illuminate\Support\Facades\Concurrency;
use Illuminate\Support\Facades\DB;

$results = Concurrency::run([
    'users' => fn () => DB::table('users')->count(),
    'orders' => fn () => DB::table('orders')->count(),
]);

$userCount = $results['users'];
$orderCount = $results['orders'];
```

<a name="task-timeouts"></a>
### 任务超时

使用 `process` 驱动（默认驱动）时，可以向 `run` 方法传入超时时间，指定并发任务在被终止前允许运行的最大秒数：

```php
use Illuminate\Support\Facades\Concurrency;
use Illuminate\Support\Facades\DB;

[$userCount, $orderCount] = Concurrency::run([
    fn () => DB::table('users')->count(),
    fn () => DB::table('orders')->count(),
], timeout: 30);
```

如果希望以更具表达力的方式定义超时时间，也可以传入 `CarbonInterval` 实例：

```php
use Illuminate\Support\Facades\Concurrency;

use function Illuminate\Support\seconds;

Concurrency::run([...], timeout: seconds(30));
```

<a name="deferring-concurrent-tasks"></a>
## 延迟并发任务

如果希望并发执行一组闭包，但不关心这些闭包返回的结果，可以考虑使用 `defer` 方法。调用 `defer` 方法时，给定的闭包不会立即执行。Laravel 会在 HTTP 响应发送给用户后并发执行这些闭包：

```php
use App\Services\Metrics;
use Illuminate\Support\Facades\Concurrency;

Concurrency::defer([
    fn () => Metrics::report('users'),
    fn () => Metrics::report('orders'),
]);
```
