# 数据库：入门

- [简介](#introduction)
    - [配置](#configuration)
    - [读写连接](#read-and-write-connections)
    - [PostgreSQL 连接池](#pooled-postgresql-connections)
- [运行 SQL 查询](#running-queries)
    - [使用多个数据库连接](#using-multiple-database-connections)
    - [在 Vitess 上运行分析查询](#running-analytical-queries-on-vitess)
    - [监听查询事件](#listening-for-query-events)
    - [监控累计查询时间](#monitoring-cumulative-query-time)
- [数据库事务](#database-transactions)
- [连接数据库 CLI](#connecting-to-the-database-cli)
- [检查数据库](#inspecting-your-databases)
- [监控数据库](#monitoring-your-databases)

<a name="introduction"></a>
## 简介

几乎所有现代 Web 应用都会与数据库交互。Laravel 支持多种数据库，让你能够通过原生 SQL、[流式查询构建器](/docs/{{version}}/queries)和 [Eloquent ORM](/docs/{{version}}/eloquent) 轻松操作数据库。目前，Laravel 官方支持以下五种数据库：

<div class="content-list" markdown="1">

- MariaDB 10.3+（[版本策略](https://mariadb.org/about/#maintenance-policy)）
- MySQL 5.7+（[版本策略](https://en.wikipedia.org/wiki/MySQL#Release_history)）
- PostgreSQL 10.0+（[版本策略](https://www.postgresql.org/support/versioning/)）
- SQLite 3.26.0+
- SQL Server 2017+（[版本策略](https://docs.microsoft.com/en-us/lifecycle/products/?products=sql-server)）

</div>

此外，你可以通过 MongoDB 官方维护的 `mongodb/laravel-mongodb` 包使用 MongoDB。更多信息请参阅 [Laravel MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/) 文档。

<a name="configuration"></a>
### 配置

Laravel 数据库服务的配置位于应用的 `config/database.php` 配置文件中。你可以在该文件中定义所有数据库连接，并指定默认使用的连接。文件中的大多数配置选项取自应用的环境变量，其中还提供了 Laravel 支持的大多数数据库系统的配置示例。

默认情况下，Laravel 的示例[环境配置](/docs/{{version}}/configuration#environment-configuration)可直接与 [Laravel Sail](/docs/{{version}}/sail) 配合使用。Sail 是一套用于在本地开发 Laravel 应用的 Docker 配置。你也可以根据本地数据库的需要自由修改数据库配置。

<a name="sqlite-configuration"></a>
#### SQLite 配置

SQLite 数据库保存在文件系统中的单个文件内。你可以在终端中使用 `touch` 命令创建一个新的 SQLite 数据库：`touch database/database.sqlite`。创建后，将数据库的绝对路径填入 `DB_DATABASE` 环境变量，即可让应用连接该数据库：

```ini
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
```

默认情况下，SQLite 连接会启用外键约束。如果要禁用外键约束，请将 `DB_FOREIGN_KEYS` 环境变量设置为 `false`：

```ini
DB_FOREIGN_KEYS=false
```

> [!NOTE]
> 如果你使用 [Laravel 安装器](/docs/{{version}}/installation#creating-a-laravel-project)创建应用，并选择 SQLite 作为数据库，Laravel 会自动创建 `database/database.sqlite` 文件，并为你运行默认的[数据库迁移](/docs/{{version}}/migrations)。

<a name="mssql-configuration"></a>
#### Microsoft SQL Server 配置

要使用 Microsoft SQL Server 数据库，请确保已安装 `sqlsrv` 和 `pdo_sqlsrv` PHP 扩展，以及这些扩展所需的依赖，例如 Microsoft SQL ODBC 驱动。

<a name="configuration-using-urls"></a>
#### 使用 URL 进行配置

通常，数据库连接需要通过 `host`、`database`、`username`、`password` 等多个配置值进行配置。每个配置值都有对应的环境变量。这意味着，在生产服务器上配置数据库连接信息时，你需要管理多个环境变量。

AWS、Heroku 等托管数据库服务提供商会提供一个数据库「URL」，将所有数据库连接信息包含在一个字符串中。数据库 URL 的示例如下：

```html
mysql://root:password@127.0.0.1/forge?charset=UTF-8
```

这些 URL 通常遵循以下标准格式：

```html
driver://username:password@host:port/database?options
```

为方便使用，Laravel 支持通过这些 URL 配置数据库，以替代多个独立配置项。如果存在 `url` 配置选项（或对应的 `DB_URL` 环境变量），Laravel 就会从中提取数据库连接信息和凭据。

<a name="read-and-write-connections"></a>
### 读写连接

有时，你可能希望对 SELECT 语句使用一个数据库连接，对 INSERT、UPDATE 和 DELETE 语句使用另一个连接。Laravel 让这种配置十分简单，无论你使用原生查询、查询构建器还是 Eloquent ORM，都会使用正确的连接。

下面的示例展示了如何配置读写连接：

```php
'mysql' => [
    'driver' => 'mysql',

    'read' => [
        'host' => [
            '192.168.1.1',
            '196.168.1.2',
        ],
    ],
    'write' => [
        'host' => [
            '192.168.1.3',
        ],
    ],
    'sticky' => true,

    'port' => env('DB_PORT', '3306'),
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
        (PHP_VERSION_ID >= 80500 ? \Pdo\Mysql::ATTR_SSL_CA : \PDO::MYSQL_ATTR_SSL_CA) => env('MYSQL_ATTR_SSL_CA'),
    ]) : [],
],
```

请注意，配置数组中添加了三个键：`read`、`write` 和 `sticky`。`read` 和 `write` 的值都是仅包含 `host` 键的数组。`read` 和 `write` 连接的其余数据库选项会从主 `mysql` 配置数组中合并而来。

只有需要覆盖主 `mysql` 数组中的值时，才需要在 `read` 和 `write` 数组中添加对应配置。因此，在本例中，「读」连接使用 `192.168.1.1` 作为主机，「写」连接使用 `192.168.1.3`。两个连接共享主 `mysql` 数组中的数据库凭据、前缀、字符集及所有其他选项。当 `host` 配置数组包含多个值时，每次请求都会随机选择一个数据库主机。

<a name="the-sticky-option"></a>
#### `sticky` 选项

`sticky` 是一个*可选*配置项，用于在当前请求周期内立即读取刚写入数据库的记录。如果启用了 `sticky` 选项，且当前请求周期内已执行过「写」操作，后续所有「读」操作都会使用「写」连接。这确保了本次请求中写入的数据可以在同一次请求中立即读回。你可以自行决定应用是否需要这种行为。

<a name="pooled-postgresql-connections"></a>
### PostgreSQL 连接池

许多 PostgreSQL 托管服务提供商通过 PgBouncer 或连接代理等服务提供事务模式的连接池。这类连接池很适合应用查询，但部分数据库结构操作、迁移和维护命令需要直接连接数据库。

要在 PostgreSQL 中使用事务连接池，请照常配置池化连接，并通过 `direct` 配置选项提供直连信息：

```php
'pgsql' => [
    'driver' => 'pgsql',
    // ...
    'pooled' => env('DB_POOLED', false),
    'direct' => array_filter([
        'host' => env('DB_DIRECT_HOST'),
        'port' => env('DB_DIRECT_PORT'),
        'username' => env('DB_DIRECT_USERNAME'),
        'password' => env('DB_DIRECT_PASSWORD'),
        'sslmode' => env('DB_DIRECT_SSLMODE'),
    ]),
],
```

将 PostgreSQL 连接配置为池化连接后，Laravel 会自动为该连接启用模拟预处理。直连会继承所有未在 `direct` 配置中明确指定的选项，并默认使用原生预处理。

Laravel 会自动对迁移、数据库结构的导出与恢复，以及 `db:wipe`、`db:show` 和 `db:table` 使用直连。启用池化模式并配置直连后，`db` 命令默认也使用直连；你可以传入 `--pooled` 选项，改用池化连接：

```shell
php artisan db --pooled
```

如果需要在应用中显式使用直连，请在连接名称后添加 `::direct` 后缀：

```php
DB::connection('pgsql::direct')->statement('create extension if not exists "uuid-ossp"');
```

<a name="running-queries"></a>
## 运行 SQL 查询

配置好数据库连接后，就可以使用 `DB` 门面运行查询。`DB` 门面为各类查询提供了对应的方法：`select`、`update`、`insert`、`delete` 和 `statement`。

<a name="running-a-select-query"></a>
#### 运行 Select 查询

要运行基本的 SELECT 查询，可以使用 `DB` 门面的 `select` 方法：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * 显示应用中所有用户的列表。
     */
    public function index(): View
    {
        $users = DB::select('select * from users where active = ?', [1]);

        return view('user.index', ['users' => $users]);
    }
}
```

`select` 方法的第一个参数是 SQL 查询，第二个参数是需要绑定到查询的参数值，通常是 `where` 子句中约束条件的值。参数绑定可以防范 SQL 注入。

`select` 方法始终以 `array` 的形式返回查询结果。数组中的每项结果都是一个 PHP `stdClass` 对象，代表数据库中的一条记录：

```php
use Illuminate\Support\Facades\DB;

$users = DB::select('select * from users');

foreach ($users as $user) {
    echo $user->name;
}
```

<a name="selecting-scalar-values"></a>
#### 查询标量值

有时，数据库查询的结果是一个标量值。Laravel 允许你通过 `scalar` 方法直接获取该值，无需再从记录对象中提取：

```php
$burgers = DB::scalar(
    "select count(case when food = 'burger' then 1 end) as burgers from menu"
);
```

<a name="selecting-multiple-result-sets"></a>
#### 查询多个结果集

如果应用调用的存储过程会返回多个结果集，你可以使用 `selectResultSets` 方法获取该存储过程返回的所有结果集：

```php
[$options, $notifications] = DB::selectResultSets(
    "CALL get_user_options_and_notifications(?)", [$request->user()->id]
);
```

<a name="using-named-bindings"></a>
#### 使用命名绑定

除了使用 `?` 表示参数绑定，你也可以使用命名绑定执行查询：

```php
$results = DB::select('select * from users where id = :id', ['id' => 1]);
```

<a name="running-an-insert-statement"></a>
#### 执行 Insert 语句

要执行 `insert` 语句，可以使用 `DB` 门面的 `insert` 方法。与 `select` 一样，该方法的第一个参数是 SQL 查询，第二个参数是绑定值：

```php
use Illuminate\Support\Facades\DB;

DB::insert('insert into users (id, name) values (?, ?)', [1, 'Marc']);
```

<a name="running-an-update-statement"></a>
#### 执行 Update 语句

`update` 方法用于更新数据库中的现有记录，并返回该语句影响的行数：

```php
use Illuminate\Support\Facades\DB;

$affected = DB::update(
    'update users set votes = 100 where name = ?',
    ['Anita']
);
```

<a name="running-a-delete-statement"></a>
#### 执行 Delete 语句

`delete` 方法用于删除数据库中的记录。与 `update` 一样，该方法会返回受影响的行数：

```php
use Illuminate\Support\Facades\DB;

$deleted = DB::delete('delete from users');
```

<a name="running-a-general-statement"></a>
#### 执行通用语句

有些数据库语句不返回任何值。对于这类操作，可以使用 `DB` 门面的 `statement` 方法：

```php
DB::statement('drop table users');
```

<a name="running-an-unprepared-statement"></a>
#### 执行未预处理语句

有时，你可能需要执行不绑定任何值的 SQL 语句。这时可以使用 `DB` 门面的 `unprepared` 方法：

```php
DB::unprepared('update users set votes = 100 where name = "Dries"');
```

> [!WARNING]
> 由于未预处理语句不绑定参数，可能受到 SQL 注入攻击。切勿在未预处理语句中使用用户可控的值。

<a name="implicit-commits-in-transactions"></a>
#### 隐式提交

在事务中使用 `DB` 门面的 `statement` 和 `unprepared` 方法时，务必避开会导致[隐式提交](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)的语句。这些语句会使数据库引擎间接提交整个事务，导致 Laravel 无法获知数据库当前的事务层级。创建数据库表就是一例：

```php
DB::unprepared('create table a (col varchar(1) null)');
```

所有会触发隐式提交的语句，请参阅 MySQL 手册中的[完整列表](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)。

<a name="using-multiple-database-connections"></a>
### 使用多个数据库连接

如果应用在 `config/database.php` 配置文件中定义了多个连接，你可以通过 `DB` 门面的 `connection` 方法访问各个连接。传给该方法的连接名称应对应 `config/database.php` 中列出的某个连接，或通过 `config` 辅助函数在运行时配置的连接：

```php
use Illuminate\Support\Facades\DB;

$users = DB::connection('sqlite')->select(/* ... */);
```

你可以通过连接实例的 `getPdo` 方法访问该连接底层的原始 PDO 实例：

```php
$pdo = DB::connection()->getPdo();
```

<a name="running-analytical-queries-on-vitess"></a>
### 在 Vitess 上运行分析查询

使用 PlanetScale 等 Vitess 数据库时，你可以通过 `olap` 方法，以 OLAP 工作负载执行分析查询：

```php
use Illuminate\Support\Facades\DB;

$totals = DB::connection('mysql')->olap(fn ($connection) => $connection->table('orders')
    ->selectRaw('customer_id, sum(total) as total')
    ->groupBy('customer_id')
    ->get()
);
```

Laravel 会同时设置读写连接的工作负载，并在回调结束后将其重置为 OLTP，即使回调抛出异常也会如此。`olap` 方法会返回回调的结果。对于未使用 Vitess 的 MySQL 连接，Laravel 会直接执行回调，不改变工作负载。

你可以通过 `isVitess` 方法判断 MySQL 连接是否使用了 Vitess：

```php
$isVitess = DB::connection('mysql')->isVitess();
```

<a name="listening-for-query-events"></a>
### 监听查询事件

如果希望应用每执行一条 SQL 查询就调用一个指定的闭包，可以使用 `DB` 门面的 `listen` 方法。这对记录查询日志或调试很有帮助。你可以在[服务提供者](/docs/{{version}}/providers)的 `boot` 方法中注册查询监听闭包：

```php
<?php

namespace App\Providers;

use Illuminate\Database\Events\QueryExecuted;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动应用服务。
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

<a name="monitoring-cumulative-query-time"></a>
### 监控累计查询时间

数据库查询耗时是现代 Web 应用常见的性能瓶颈。Laravel 可以在单次请求中累计查询数据库的时间过长时，调用你指定的闭包或回调。要使用此功能，请向 `whenQueryingForLongerThan` 方法传入查询时间阈值（毫秒）和闭包。你可以在[服务提供者](/docs/{{version}}/providers)的 `boot` 方法中调用该方法：

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
     * 注册应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动应用服务。
     */
    public function boot(): void
    {
        DB::whenQueryingForLongerThan(500, function (Connection $connection, QueryExecuted $event) {
            // 通知开发团队……
        });
    }
}
```

<a name="database-transactions"></a>
## 数据库事务

你可以使用 `DB` 门面的 `transaction` 方法，在数据库事务中执行一组操作。如果事务闭包抛出异常，事务会自动回滚，并重新抛出该异常。如果闭包执行成功，事务会自动提交。使用 `transaction` 方法时，无需手动回滚或提交：

```php
use Illuminate\Support\Facades\DB;

DB::transaction(function () {
    DB::update('update users set votes = 1');

    DB::delete('delete from posts');
});
```

<a name="handling-deadlocks"></a>
#### 处理死锁

`transaction` 方法接受一个可选的第二个参数，用于指定发生死锁时重试事务的次数。尝试次数耗尽后，会抛出异常：

```php
use Illuminate\Support\Facades\DB;

DB::transaction(function () {
    DB::update('update users set votes = 1');

    DB::delete('delete from posts');
}, attempts: 5);
```

<a name="manually-using-transactions"></a>
#### 手动使用事务

如果希望手动开启事务，并完全控制回滚与提交，可以使用 `DB` 门面的 `beginTransaction` 方法：

```php
use Illuminate\Support\Facades\DB;

DB::beginTransaction();
```

你可以通过 `rollBack` 方法回滚事务：

```php
DB::rollBack();
```

最后，可以通过 `commit` 方法提交事务：

```php
DB::commit();
```

> [!NOTE]
> `DB` 门面的事务方法同时控制[查询构建器](/docs/{{version}}/queries)和 [Eloquent ORM](/docs/{{version}}/eloquent) 的事务。

<a name="connecting-to-the-database-cli"></a>
## 连接数据库 CLI

要连接数据库的命令行界面（CLI），可以使用 `db` Artisan 命令：

```shell
php artisan db
```

如有需要，你可以指定数据库连接名称，以连接到默认连接以外的数据库连接：

```shell
php artisan db mysql
```

<a name="inspecting-your-databases"></a>
## 检查数据库

通过 `db:show` 和 `db:table` Artisan 命令，你可以了解数据库及其相关表的重要信息。要查看数据库概览，包括大小、类型、打开的连接数及各表摘要，可以使用 `db:show` 命令：

```shell
php artisan db:show
```

你可以通过 `--database` 选项传入数据库连接名称，指定要检查的连接：

```shell
php artisan db:show --database=pgsql
```

如果希望命令输出包含表的行数和数据库视图详情，可以分别添加 `--counts` 和 `--views` 选项。对于大型数据库，获取行数和视图详情可能较慢：

```shell
php artisan db:show --counts --views
```

此外，你还可以通过以下 `Schema` 方法检查数据库：

```php
use Illuminate\Support\Facades\Schema;

$tables = Schema::getTables();
$views = Schema::getViews();
$columns = Schema::getColumns('users');
$indexes = Schema::getIndexes('users');
$foreignKeys = Schema::getForeignKeys('users');
```

如果要检查应用默认连接以外的数据库连接，可以使用 `connection` 方法：

```php
$columns = Schema::connection('sqlite')->getColumns('users');
```

<a name="table-overview"></a>
#### 表概览

要查看数据库中单个表的概览，可以执行 `db:table` Artisan 命令。该命令会展示数据库表的总体信息，包括列、类型、属性、键和索引：

```shell
php artisan db:table users
```

<a name="monitoring-your-databases"></a>
## 监控数据库

使用 `db:monitor` Artisan 命令，可以让 Laravel 在数据库打开的连接数超过指定数量时，派发 `Illuminate\Database\Events\DatabaseBusy` 事件。

首先，将 `db:monitor` 命令安排为[每分钟运行一次](/docs/{{version}}/scheduling)。该命令接受要监控的数据库连接配置名称，以及触发事件前所允许的最大打开连接数：

```shell
php artisan db:monitor --databases=mysql,pgsql --max=100
```

仅安排该命令运行，并不会自动发送有关打开连接数的通知。当命令检测到数据库打开的连接数超过阈值时，会派发 `DatabaseBusy` 事件。你应在应用的 `AppServiceProvider` 中监听该事件，以便向你或开发团队发送通知：

```php
use App\Notifications\DatabaseApproachingMaxConnections;
use Illuminate\Database\Events\DatabaseBusy;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Notification;

/**
 * 启动应用服务。
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
