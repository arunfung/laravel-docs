# Concurrency

- [介绍](#introduction)
- [运行并发任务](#running-concurrent-tasks)
- [延迟并发任务](#deferring-concurrent-tasks)

<a name="introduction"></a>
## 介绍

有时你可能需要执行几个相互独立的慢任务。在多数情况下，通过并发执行任务可以实现显著的性能提升。Laravel的 `Concurrency` 门面提供了一个简单、方便的API来并发执行闭包。

<a name="how-it-works"></a>
#### 工作原理

Laravel 通过序列化给定的闭包并将其分派给一个隐藏的 Artisan CLI 命令来实现并发，该命令会取消序列化闭包并在自己的 PHP 进程中调用它。调用闭包后，结果值被序列化回父进程。

`并发` 门面支持三个驱动程序：`process`（默认），`fork`，和`sync`。

`fork` 驱动程序与默认的 `process` 驱动程序相比，提供了改进的性能，但它只能在 PHP 的 CLI 上下文中使用，因为 PHP 不支持在 Web 请求期间进行分叉。在使用 `fork` 驱动程序之前，您需要安装 `spatie/fork` 包：

```shell
composer require spatie/fork
```

`sync` 驱动主要在你测试期间，想禁用所有并发，并在父进程中按顺序简单地执行给定的闭包时使用

<a name="running-concurrent-tasks"></a>
## 运行并发任务

要运行并发任务，您可以调用 `Concurrency` 门面的 `run` 方法。 `run` 方法接受一个应在子 PHP 进程中同时执行的闭包数组：

```php
use Illuminate\Support\Facades\Concurrency;
use Illuminate\Support\Facades\DB;

[$userCount, $orderCount] = Concurrency::run([
    fn () => DB::table('users')->count(),
    fn () => DB::table('orders')->count(),
]);
```



要使用特定的驱动程序，你可以使用 `driver` 方法：

```php
$results = Concurrency::driver('fork')->run(...);
```

或者，要更改默认并发驱动程序，你应该通过 `config:publish` Artisan命令发布 `concurrency` 配置文件，并在文件中更新`default`选项：

```shell
php artisan config:publish concurrency
```

<a name="deferring-concurrent-tasks"></a>
## 延迟并发任务

如果你想并发执行一系列闭包，但又对那些闭包返回的结果不感兴趣，你应该考虑使用 `defer` 方法。当调用 `defer` 方法时，给定的闭包不会立即执行。相反，Laravel 会在向用户发送 HTTP 响应后并发执行这些闭包：

```php
use App\Services\Metrics;
use Illuminate\Support\Facades\Concurrency;

Concurrency::defer([
    fn () => Metrics::report('users'),
    fn () => Metrics::report('orders'),
]);
```
