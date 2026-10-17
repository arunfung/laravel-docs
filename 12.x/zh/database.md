
# 数据库：入门

-   [简介](#introduction)
    -   [配置](#configuration)
    -   [读写分离连接](#read-and-write-connections)
-   [运行 SQL 查询](#running-queries)
    -   [使用多个数据库连接](#using-multiple-database-connections)
    -   [监听查询事件](#listening-for-query-events)
    -   [监控累计查询时间](#monitoring-cumulative-query-time)
-   [数据库事务](#database-transactions)
-   [连接数据库 CLI](#connecting-to-the-database-cli)
-   [检查数据库](#inspecting-your-databases)
-   [监控数据库](#monitoring-your-databases)

## 简介

几乎所有现代 Web 应用都会与数据库交互。Laravel 让你在各种受支持的数据库中进行交互变得极其简单，无论是使用原生 SQL、[流畅的查询构建器](/docs/laravel/12.x/queries)，还是 [Eloquent ORM](/docs/laravel/12.x/eloquent)。目前，Laravel 官方提供了对以下五种数据库的一方支持：

<div class="content-list" markdown="1">

-   MariaDB 10.3+ ([版本策略](https://mariadb.org/about/#maintenance-policy))
-   MySQL 5.7+ ([版本策略](https://en.wikipedia.org/wiki/MySQL#Release_history))
-   PostgreSQL 10.0+ ([版本策略](https://www.postgresql.org/support/versioning/))
-   SQLite 3.26.0+
-   SQL Server 2017+ ([版本策略](https://docs.microsoft.com/en-us/lifecycle/products/?products=sql-server))

</div>

此外，MongoDB 也通过 `mongodb/laravel-mongodb` 包获得支持，该包由 MongoDB 官方维护。更多信息请查看 [Laravel MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/) 文档。

### 配置

Laravel 的数据库服务配置位于应用的 `config/database.php` 配置文件中。在这个文件里，你可以定义所有的数据库连接，并指定默认使用的连接。此文件中的大多数配置选项都由应用的环境变量驱动。Laravel 支持的多数数据库系统在此文件中都提供了示例。



默认情况下，Laravel 的示例 [环境配置](/docs/laravel/12.x/configuration#environment-configuration) 已经可以与 [Laravel Sail](/docs/laravel/12.x/sail) 一起使用，Sail 是一个用于在你的本地机器上开发 Laravel 应用程序的 Docker 配置。
然而，你可以根据本地数据库的需要自由修改数据库配置。

#### SQLite 配置

SQLite 数据库包含在你文件系统中的一个单独文件内。你可以在终端中使用 `touch` 命令来创建一个新的 SQLite 数据库：`touch database/database.sqlite`。
数据库创建完成后，你可以很容易地配置你的环境变量来指向这个数据库，只需在 `DB_DATABASE` 环境变量中放置数据库的绝对路径即可：

```ini
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
```

默认情况下，SQLite 连接会启用外键约束。如果你想禁用它们，你应该将 `DB_FOREIGN_KEYS` 环境变量设置为 `false`：

```ini
DB_FOREIGN_KEYS=false
```

> [!注意]
> 如果你使用 [Laravel 安装器](/docs/laravel/12.x/installation#creating-a-laravel-project) 来创建你的 Laravel 应用程序并选择 SQLite 作为数据库，Laravel 将会自动为你创建一个 `database/database.sqlite` 文件并运行默认的 [数据库迁移](/docs/laravel/12.x/migrations)。

#### Microsoft SQL Server 配置

要使用 Microsoft SQL Server 数据库，你应该确保你已经安装了 `sqlsrv` 和 `pdo_sqlsrv` PHP 扩展，以及它们可能需要的任何依赖，比如 Microsoft SQL ODBC 驱动。

#### 使用 URL 进行配置


通常，数据库连接是通过多个配置值来配置的，比如 `host`、`database`、`username`、`password` 等。
这些配置值中的每一个都有其对应的环境变量。
这意味着，当你在生产服务器上配置数据库连接信息时，你需要管理多个环境变量。

一些托管数据库提供商（例如 AWS 和 Heroku）会提供一个单一的数据库 “URL”，其中包含了数据库的所有连接信息并以一个字符串的形式存在。
一个示例数据库 URL 看起来可能如下：

```html
mysql://root:password@127.0.0.1/forge?charset=UTF-8
```

这些 URL 通常遵循一个标准的模式约定：

```html
driver://username:password@host:port/database?options
```
为了方便起见，Laravel 支持这些 URL 作为使用多个配置选项配置数据库的一种替代方案。
如果存在 `url`（或对应的 `DB_URL` 环境变量）配置选项，它将被用来提取数据库连接和凭据信息。

### 读写连接

有时候，你可能希望对 `SELECT` 语句使用一个数据库连接，而对 `INSERT`、`UPDATE` 和 `DELETE` 语句使用另一个数据库连接。
Laravel 让这一切变得轻而易举，并且无论你使用的是原生查询、查询构建器，还是 Eloquent ORM，都会始终使用正确的连接。

要查看读/写连接应该如何配置，让我们来看这个示例：

```php
'mysql' => [
    'read' => [
        'host' => [
            '192.168.1.1',
            '196.168.1.2',
        ],
    ],
    'write' => [
        'host' => [
            '196.168.1.3',
        ],
    ],
    'sticky' => true,

    'database' => env('DB_DATABASE', 'laravel'),
    'username' => env('DB_USERNAME', 'root'),
    'password' => env('DB_PASSWORD', ''),
    'unix_socket' => env('DB_SOCKET', ''),
    'charset' => env('DB_CHARSET', 'utf8mb4'),
    'collation' => env('DB_COLLATION', 'utf8mb4_unicode_ci'),
    'prefix' => '',
    'prefix_indexes' => true,
    'strict' => true,
    'engine' => null,
    'options' => extension_loaded('pdo_mysql') ? array_filter([
        PDO::MYSQL_ATTR_SSL_CA => env('MYSQL_ATTR_SSL_CA'),
    ]) : [],
],
```



请注意，配置数组中添加了三个键：`read`、`write` 和 `sticky`。
`read` 和 `write` 键的值是数组，且数组中包含一个单一的键：`host`。
`read` 和 `write` 连接的其他数据库选项将会从主 `mysql` 配置数组中合并。

只有当你想要覆盖主 `mysql` 数组中的值时，才需要在 `read` 和 `write` 数组中放置项目。
因此，在本例中，`192.168.1.1` 将被用作 “读” 连接的主机，而 `192.168.1.3` 将被用作 “写” 连接的主机。
数据库凭据、前缀、字符集以及主 `mysql` 数组中的所有其他选项将会在两个连接中共享。
当 `host` 配置数组中存在多个值时，每个请求都会随机选择一个数据库主机。

#### sticky 选项

`sticky` 选项是一个*可选*值，用于允许在当前请求周期内立即读取已写入数据库的记录。
如果启用了 `sticky` 选项，并且在当前请求周期内对数据库执行了 “写” 操作，那么之后的任何 “读” 操作都会使用 “写” 连接。
这确保了在请求周期内写入的任何数据都可以在同一请求中立即被读回。
是否需要这种行为，由你来决定是否适合你的应用程序。

## 运行 SQL 查询

一旦你配置了数据库连接，就可以使用 `DB` facade 来运行查询。
`DB` facade 提供了针对每种类型查询的方法：`select`、`update`、`insert`、`delete` 和 `statement`。



#### 运行 Select 查询

要运行一个基本的 SELECT 查询，你可以在 `DB` facade 上使用 `select` 方法：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * 显示应用程序中所有用户的列表。
     */
    public function index(): View
    {
        $users = DB::select('select * from users where active = ?', [1]);

        return view('user.index', ['users' => $users]);
    }
}
```

传递给 `select` 方法的第一个参数是 SQL 查询，而第二个参数是需要绑定到查询中的任何参数绑定。
通常，这些是 `where` 子句约束的值。参数绑定提供了防止 SQL 注入的保护。

`select` 方法总是返回一个结果的 `array`。数组中的每个结果都是一个 PHP 的 `stdClass` 对象，用来表示数据库中的一条记录：

```php
use Illuminate\Support\Facades\DB;

$users = DB::select('select * from users');

foreach ($users as $user) {
    echo $user->name;
}
```

#### 选择标量值

有时你的数据库查询可能会返回一个单一的标量值。
Laravel 允许你直接使用 `scalar` 方法来获取这个值，而不是必须从记录对象中获取查询的标量结果：

```php
$burgers = DB::scalar(
    "select count(case when food = 'burger' then 1 end) as burgers from menu"
);
```

#### 选择多个结果集

如果你的应用程序调用了返回多个结果集的存储过程，你可以使用 `selectResultSets` 方法来获取存储过程返回的所有结果集：

```php
[$options, $notifications] = DB::selectResultSets(
    "CALL get_user_options_and_notifications(?)", $request->user()->id
);
```



#### 使用命名绑定

除了使用 `?` 来表示参数绑定之外，你还可以使用命名绑定来执行查询：

```php
$results = DB::select('select * from users where id = :id', ['id' => 1]);
```

#### 执行 Insert 语句

要执行 `insert` 语句，你可以在 `DB` facade 上使用 `insert` 方法。和 `select` 一样，该方法的第一个参数是 SQL 查询，第二个参数是绑定的值：

```php
use Illuminate\Support\Facades\DB;

DB::insert('insert into users (id, name) values (?, ?)', [1, 'Marc']);
```

#### 执行 Update 语句

`update` 方法用于更新数据库中已有的记录。该方法会返回被该语句影响的行数：

```php
use Illuminate\Support\Facades\DB;

$affected = DB::update(
    'update users set votes = 100 where name = ?',
    ['Anita']
);
```

#### 执行 Delete 语句

`delete` 方法用于删除数据库中的记录。与 `update` 一样，该方法会返回被影响的行数：

```php
use Illuminate\Support\Facades\DB;

$deleted = DB::delete('delete from users');
```

#### 执行通用语句

某些数据库语句不会返回任何值。对于这类操作，你可以使用 `DB` facade 的 `statement` 方法：

```php
DB::statement('drop table users');
```

#### 执行未预处理语句

有时你可能需要执行一个不绑定任何值的 SQL 语句。这时你可以使用 `DB` facade 的 `unprepared` 方法：

```php
DB::unprepared('update users set votes = 100 where name = "Dries"');
```

> [!警告]
> 由于未预处理语句不会绑定参数，它们可能容易受到 SQL 注入攻击。你绝对不要在未预处理语句中使用用户可控的值。



#### 隐式提交

当在事务中使用 `DB` facade 的 `statement` 和 `unprepared` 方法时，你必须小心避免会导致 [隐式提交](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html) 的语句。
这些语句会导致数据库引擎间接提交整个事务，从而使 Laravel 无法获知数据库的事务级别。
此类语句的一个示例是创建数据库表：

```php
DB::unprepared('create table a (col varchar(1) null)');
```

请参考 MySQL 手册，查看 [所有会触发隐式提交的语句列表](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)。

### 使用多个数据库连接

如果你的应用在 `config/database.php` 配置文件中定义了多个连接，你可以通过 `DB` facade 提供的 `connection` 方法来访问每一个连接。
传递给 `connection` 方法的连接名称应当对应于 `config/database.php` 配置文件中列出的某个连接，或使用 `config` 助手在运行时配置：

```php
use Illuminate\Support\Facades\DB;

$users = DB::connection('sqlite')->select(/* ... */);
```

你可以通过连接实例上的 `getPdo` 方法来访问底层的原始 PDO 实例：

```php
$pdo = DB::connection()->getPdo();
```

### 监听查询事件

如果你想要指定一个闭包来处理应用执行的每一条 SQL 查询，你可以使用 `DB` facade 的 `listen` 方法。
这种方法对记录查询日志或调试很有用。
你可以在 [服务提供者](/docs/laravel/12.x/providers) 的 `boot` 方法中注册查询监听闭包：

```php
<?php

<?php

namespace App\Providers;

use Illuminate\Database\Events\QueryExecuted;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册任意的应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动任意的应用服务。
     */
    public function boot(): void
    {
        DB::listen(function (QueryExecuted $query) {
            // $query->sql;
            // $query->bindings;
            // $query->time;
            // $query->toRawSql();
        });
    }
}

```



### 监控累计查询时间

现代 Web 应用的一个常见性能瓶颈是它们在查询数据库上花费的时间。
值得庆幸的是，当 Laravel 在单次请求中查询数据库花费过多时间时，它可以调用你指定的闭包或回调。
要开始使用，请为 `whenQueryingForLongerThan` 方法提供一个查询时间阈值（毫秒为单位）和一个闭包。
你可以在 [服务提供者](/docs/laravel/12.x/providers) 的 `boot` 方法中调用此方法：

```php
<?php

namespace App\Providers;

use Illuminate\Database\Connection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\ServiceProvider;
use Illuminate\Database\Events\QueryExecuted;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册任意应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动任意应用服务。
     */
    public function boot(): void
    {
        DB::whenQueryingForLongerThan(500, function (Connection $connection, QueryExecuted $event) {
            // 通知开发团队...
        });
    }
}
```

## 数据库事务

你可以使用 `DB` facade 提供的 `transaction` 方法，在数据库事务中运行一组操作。
如果事务闭包中抛出异常，事务将自动回滚，并且异常会被重新抛出。
如果闭包执行成功，事务将自动提交。
使用 `transaction` 方法时，你无需担心手动回滚或提交：

```php
use Illuminate\Support\Facades\DB;

DB::transaction(function () {
    DB::update('update users set votes = 1');

    DB::delete('delete from posts');
});
```

#### 处理死锁

`transaction` 方法接受一个可选的第二个参数，该参数定义当发生死锁时事务应重试的次数。
一旦这些尝试用尽，将会抛出异常：

```php
use Illuminate\Support\Facades\DB;

DB::transaction(function () {
    DB::update('update users set votes = 1');

    DB::delete('delete from posts');
}, 5);
```



#### 手动使用事务

如果你希望手动启动一个事务，并且完全控制回滚和提交，你可以使用 `DB` facade 提供的 `beginTransaction` 方法：

```php
use Illuminate\Support\Facades\DB;

DB::beginTransaction();
```

你可以通过 `rollBack` 方法回滚事务：

```php
DB::rollBack();
```

最后，你可以通过 `commit` 方法提交事务：

```php
DB::commit();
```

> [!注意]
> `DB` facade 的事务方法控制 [查询构建器](/docs/laravel/12.x/queries) 和 [Eloquent ORM](/docs/laravel/12.x/eloquent) 的事务。


## 连接数据库 CLI

如果你希望连接到数据库的命令行界面（CLI），你可以使用 `db` Artisan 命令：

```shell
php artisan db
```

如有需要，你可以指定数据库连接名称，以连接非默认的数据库连接：

```shell
php artisan db mysql
```

## 检查你的数据库

使用 `db:show` 和 `db:table` Artisan 命令，你可以获得数据库及其相关表的重要信息。
要查看数据库概览，包括大小、类型、打开的连接数，以及表的摘要，你可以使用 `db:show` 命令：

```shell
php artisan db:show
```

你可以通过 `--database` 选项，指定要检查的数据库连接名称：

```shell
php artisan db:show --database=pgsql
```

如果你希望在命令输出中包含表行数和数据库视图详情，可以分别提供 `--counts` 和 `--views` 选项。
在大型数据库中，检索行数和视图详情可能会很慢：

```shell
php artisan db:show --counts --views
```



此外，你可以使用以下 `Schema` 方法来检查你的数据库：

```php
use Illuminate\Support\Facades\Schema;

$tables = Schema::getTables();
$views = Schema::getViews();
$columns = Schema::getColumns('users');
$indexes = Schema::getIndexes('users');
$foreignKeys = Schema::getForeignKeys('users');
```

如果你希望检查一个不是应用默认连接的数据库连接，你可以使用 `connection` 方法：

```php
$columns = Schema::connection('sqlite')->getColumns('users');
```

#### 表概览

如果你希望获得数据库中单个表的概览，你可以执行 `db:table` Artisan 命令。
该命令提供数据库表的总体概览，包括列、类型、属性、键和索引：

```shell
php artisan db:table users
```

## 监控你的数据库

使用 `db:monitor` Artisan 命令，你可以指示 Laravel 在数据库管理的打开连接数超过指定数量时，派发一个 `Illuminate\Database\Events\DatabaseBusy` 事件。

要开始使用，你应该安排 `db:monitor` 命令[每分钟运行一次](/docs/laravel/12.x/scheduling)。
该命令接受要监控的数据库连接配置名称，以及在派发事件之前可容忍的最大打开连接数：

```shell
php artisan db:monitor --databases=mysql,pgsql --max=100
```

仅仅安排此命令运行不足以触发通知以警告打开连接数。
当命令检测到数据库的打开连接数超过阈值时，将派发一个 `DatabaseBusy` 事件。
你应该在应用的 `AppServiceProvider` 中监听此事件，以便向你或开发团队发送通知：

```php
use App\Notifications\DatabaseApproachingMaxConnections;
use Illuminate\Database\Events\DatabaseBusy;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Notification;

/**
 * 启动任意应用服务。
 */
public function boot(): void
{
    Event::listen(function (DatabaseBusy $event) {
        Notification::route('mail', 'dev@example.com')
            ->notify(new DatabaseApproachingMaxConnections(
                $event->connectionName,
                $event->connections
            ));
    });
}
```
