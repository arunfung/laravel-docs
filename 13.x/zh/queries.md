# 数据库：查询构建器

- [简介](#introduction)
- [运行数据库查询](#running-database-queries)
    - [分块处理结果](#chunking-results)
    - [惰性流式处理结果](#streaming-results-lazily)
    - [聚合](#aggregates)
- [Select 语句](#select-statements)
- [原始表达式](#raw-expressions)
- [联接](#joins)
- [并集](#unions)
- [基本 Where 子句](#basic-where-clauses)
    - [Where 子句](#where-clauses)
    - [Or Where 子句](#or-where-clauses)
    - [Where Not 子句](#where-not-clauses)
    - [Where Any / All / None 子句](#where-any-all-none-clauses)
    - [JSON Where 子句](#json-where-clauses)
    - [其他 Where 子句](#additional-where-clauses)
    - [逻辑分组](#logical-grouping)
- [高级 Where 子句](#advanced-where-clauses)
    - [Where Exists 子句](#where-exists-clauses)
    - [子查询 Where 子句](#subquery-where-clauses)
    - [全文 Where 子句](#full-text-where-clauses)
    - [向量相似度子句](#vector-similarity-clauses)
- [排序、分组、条数限制和偏移量](#ordering-grouping-limit-and-offset)
    - [排序](#ordering)
    - [分组](#grouping)
    - [条数限制和偏移量](#limit-and-offset)
- [条件子句](#conditional-clauses)
- [插入语句](#insert-statements)
    - [插入或更新](#upserts)
- [更新语句](#update-statements)
    - [更新 JSON 列](#updating-json-columns)
    - [自增与自减](#increment-and-decrement)
- [删除语句](#delete-statements)
- [悲观锁](#pessimistic-locking)
- [可复用的查询组件](#reusable-query-components)
- [调试](#debugging)

<a name="introduction"></a>
## 简介

Laravel 的数据库查询构建器提供了便捷的链式接口，用于创建和运行数据库查询。它可以执行应用中的大多数数据库操作，并且兼容 Laravel 支持的所有数据库系统。

Laravel 查询构建器使用 PDO 参数绑定来保护应用免受 SQL 注入攻击。作为查询绑定传给查询构建器的字符串，无需额外清理或过滤。

> [!WARNING]
> PDO 不支持绑定列名。因此，切勿让用户输入决定查询中引用的列名，包括「order by」子句中的列名。

<a name="running-database-queries"></a>
## 运行数据库查询

<a name="retrieving-all-rows-from-a-table"></a>
#### 从表中获取所有行

你可以使用 `DB` 门面的 `table` 方法开始查询。该方法会为指定表返回一个查询构建器实例，你可以链式添加更多约束，最后通过 `get` 方法获取查询结果：

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
        $users = DB::table('users')->get();

        return view('user.index', ['users' => $users]);
    }
}
```

`get` 方法返回包含查询结果的 `Illuminate\Support\Collection` 实例，其中每项结果都是 PHP `stdClass` 对象。你可以通过对象上与列同名的属性访问各列的值：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')->get();

foreach ($users as $user) {
    echo $user->name;
}
```

> [!NOTE]
> Laravel 集合提供了多种强大的数据映射和归约方法。更多信息请参阅[集合文档](/docs/{{version}}/collections)。

<a name="retrieving-a-single-row-column-from-a-table"></a>
#### 从表中获取单行或单列

如果只需从数据库表中获取一行，可以使用 `DB` 门面的 `first` 方法。该方法会返回单个 `stdClass` 对象：

```php
$user = DB::table('users')->where('name', 'John')->first();

return $user->email;
```

如果希望获取单行，并在找不到匹配行时抛出 `Illuminate\Database\RecordNotFoundException` 异常，可以使用 `firstOrFail` 方法。如果未捕获 `RecordNotFoundException`，系统会自动向客户端返回 404 HTTP 响应：

```php
$user = DB::table('users')->where('name', 'John')->firstOrFail();
```

如果不需要整行，可以使用 `value` 方法从记录中提取单个值。该方法会直接返回指定列的值：

```php
$email = DB::table('users')->where('name', 'John')->value('email');
```

要根据 `id` 列的值获取单行，请使用 `find` 方法：

```php
$user = DB::table('users')->find(3);
```

<a name="retrieving-a-list-of-column-values"></a>
#### 获取单列值的列表

如果希望获取包含单列值的 `Illuminate\Support\Collection` 实例，可以使用 `pluck` 方法。下面的示例会获取用户 `title` 列的值集合：

```php
use Illuminate\Support\Facades\DB;

$titles = DB::table('users')->pluck('title');

foreach ($titles as $title) {
    echo $title;
}
```

你可以向 `pluck` 方法传入第二个参数，指定结果集合以哪一列的值作为键：

```php
$titles = DB::table('users')->pluck('title', 'name');

foreach ($titles as $name => $title) {
    echo $title;
}
```

<a name="chunking-results"></a>
### 分块处理结果

如果需要处理数千条数据库记录，可以考虑使用 `DB` 门面的 `chunk` 方法。该方法每次获取一小块结果，并将其传给闭包处理。例如，下面会以每块 100 条记录的方式读取整个 `users` 表：

```php
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

DB::table('users')->orderBy('id')->chunk(100, function (Collection $users) {
    foreach ($users as $user) {
        // ...
    }
});
```

在闭包中返回 `false`，即可停止处理后续分块：

```php
DB::table('users')->orderBy('id')->chunk(100, function (Collection $users) {
    // 处理记录……

    return false;
});
```

如果在分块处理过程中更新数据库记录，分块结果可能发生意外变化。如果打算在分块处理时更新已获取的记录，最好改用 `chunkById` 方法。该方法会根据记录的主键自动对结果分页：

```php
DB::table('users')->where('active', false)
    ->chunkById(100, function (Collection $users) {
        foreach ($users as $user) {
            DB::table('users')
                ->where('id', $user->id)
                ->update(['active' => true]);
        }
    });
```

由于 `chunkById` 和 `lazyById` 方法会向查询添加自己的「where」条件，通常应将你自己的条件放入闭包中进行[逻辑分组](#logical-grouping)：

```php
DB::table('users')->where(function ($query) {
    $query->where('credits', 1)->orWhere('credits', 2);
})->chunkById(100, function (Collection $users) {
    foreach ($users as $user) {
        DB::table('users')
            ->where('id', $user->id)
            ->update(['credits' => 3]);
    }
});
```

> [!WARNING]
> 在分块回调中更新或删除记录时，修改主键或外键可能影响分块查询，导致某些记录未被包含在分块结果中。

<a name="streaming-results-lazily"></a>
### 惰性流式处理结果

`lazy` 方法与 [chunk 方法](#chunking-results)类似，都会分块执行查询。但 `lazy()` 不会将每个分块传给回调，而是返回一个 [LazyCollection](/docs/{{version}}/collections#lazy-collections)，让你可以像处理单个数据流一样处理结果：

```php
use Illuminate\Support\Facades\DB;

DB::table('users')->orderBy('id')->lazy()->each(function (object $user) {
    // ...
});
```

同样，如果打算在遍历已获取的记录时更新它们，最好改用 `lazyById` 或 `lazyByIdDesc` 方法。这些方法会根据记录的主键自动对结果分页：

```php
DB::table('users')->where('active', false)
    ->lazyById()->each(function (object $user) {
        DB::table('users')
            ->where('id', $user->id)
            ->update(['active' => true]);
    });
```

> [!WARNING]
> 在遍历过程中更新或删除记录时，修改主键或外键可能影响分块查询，导致某些记录未被包含在结果中。

<a name="aggregates"></a>
### 聚合

查询构建器还提供了多种获取聚合值的方法，例如 `count`、`max`、`min`、`avg` 和 `sum`。你可以在构建查询后调用这些方法：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')->count();

$price = DB::table('orders')->max('price');
```

你也可以将这些方法与其他子句结合，进一步控制聚合值的计算方式：

```php
$price = DB::table('orders')
    ->where('finalized', 1)
    ->avg('price');
```

<a name="determining-if-records-exist"></a>
#### 判断记录是否存在

要判断是否存在符合查询约束的记录，可以使用 `exists` 和 `doesntExist` 方法，无需使用 `count`：

```php
if (DB::table('orders')->where('finalized', 1)->exists()) {
    // ...
}

if (DB::table('orders')->where('finalized', 1)->doesntExist()) {
    // ...
}
```

<a name="select-statements"></a>
## Select 语句

<a name="specifying-a-select-clause"></a>
#### 指定 Select 子句

你可能并不总是需要选择数据库表中的所有列。使用 `select` 方法，可以为查询指定自定义的「select」子句：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')
    ->select('name', 'email as user_email')
    ->get();
```

`distinct` 方法可以让查询返回去重后的结果：

```php
$users = DB::table('users')->distinct()->get();
```

如果已经有一个查询构建器实例，并希望向现有的 select 子句添加列，可以使用 `addSelect` 方法：

```php
$query = DB::table('users')->select('name');

$users = $query->addSelect('age')->get();
```

<a name="raw-expressions"></a>
## 原始表达式

有时，你可能需要在查询中插入任意字符串。要创建原始字符串表达式，可以使用 `DB` 门面的 `raw` 方法：

```php
$users = DB::table('users')
    ->select(DB::raw('count(*) as user_count, status'))
    ->where('status', '<>', 1)
    ->groupBy('status')
    ->get();
```

> [!WARNING]
> 原始语句会以字符串的形式直接插入查询，因此务必谨慎，避免引入 SQL 注入漏洞。

<a name="raw-methods"></a>
### 原始表达式方法

除了 `DB::raw`，还可以使用以下方法将原始表达式插入查询的不同部分。**请记住，Laravel 无法保证使用原始表达式的查询不受 SQL 注入攻击。**

<a name="selectraw"></a>
#### `selectRaw`

`selectRaw` 方法可以替代 `addSelect(DB::raw(/* ... */))`。该方法的第二个参数是可选的绑定值数组：

```php
$orders = DB::table('orders')
    ->selectRaw('price * ? as price_with_tax', [1.0825])
    ->get();
```

<a name="whereraw-orwhereraw"></a>
#### `whereRaw / orWhereRaw`

`whereRaw` 和 `orWhereRaw` 方法可以向查询插入原始「where」子句。这些方法的第二个参数是可选的绑定值数组：

```php
$orders = DB::table('orders')
    ->whereRaw('price > IF(state = "TX", ?, 100)', [200])
    ->get();
```

<a name="havingraw-orhavingraw"></a>
#### `havingRaw / orHavingRaw`

`havingRaw` 和 `orHavingRaw` 方法可以将原始字符串用作「having」子句。这些方法的第二个参数是可选的绑定值数组：

```php
$orders = DB::table('orders')
    ->select('department', DB::raw('SUM(price) as total_sales'))
    ->groupBy('department')
    ->havingRaw('SUM(price) > ?', [2500])
    ->get();
```

<a name="orderbyraw"></a>
#### `orderByRaw`

`orderByRaw` 方法可以将原始字符串用作「order by」子句：

```php
$orders = DB::table('orders')
    ->orderByRaw('updated_at - created_at DESC')
    ->get();
```

<a name="groupbyraw"></a>
#### `groupByRaw`

`groupByRaw` 方法可以将原始字符串用作 `group by` 子句：

```php
$orders = DB::table('orders')
    ->select('city', 'state')
    ->groupByRaw('city, state')
    ->get();
```

<a name="joins"></a>
## 联接

<a name="inner-join-clause"></a>
#### 内联接子句

查询构建器也可以为查询添加联接子句。要执行基本的「内联接」，可以使用查询构建器实例的 `join` 方法。第一个参数是要联接的表名，其余参数用于指定联接的列约束。你甚至可以在单个查询中联接多个表：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')
    ->join('contacts', 'users.id', '=', 'contacts.user_id')
    ->join('orders', 'users.id', '=', 'orders.user_id')
    ->select('users.*', 'contacts.phone', 'orders.price')
    ->get();
```

<a name="left-join-right-join-clause"></a>
#### 左联接与右联接子句

如果要执行「左联接」或「右联接」，可以使用 `leftJoin` 或 `rightJoin` 方法。这些方法的签名与 `join` 相同：

```php
$users = DB::table('users')
    ->leftJoin('posts', 'users.id', '=', 'posts.user_id')
    ->get();

$users = DB::table('users')
    ->rightJoin('posts', 'users.id', '=', 'posts.user_id')
    ->get();
```

<a name="cross-join-clause"></a>
#### 交叉联接子句

你可以使用 `crossJoin` 方法执行「交叉联接」。交叉联接会生成第一个表与被联接表之间的笛卡尔积：

```php
$sizes = DB::table('sizes')
    ->crossJoin('colors')
    ->get();
```

<a name="advanced-join-clauses"></a>
#### 高级联接子句

你也可以指定更复杂的联接子句。将闭包作为 `join` 方法的第二个参数传入，闭包会接收一个 `Illuminate\Database\Query\JoinClause` 实例，让你可以为「join」子句指定约束：

```php
DB::table('users')
    ->join('contacts', function (JoinClause $join) {
        $join->on('users.id', '=', 'contacts.user_id')->orOn(/* ... */);
    })
    ->get();
```

如果要在联接中使用「where」子句，可以使用 `JoinClause` 实例的 `where` 和 `orWhere` 方法。这些方法会将列与值进行比较，而不是比较两个列：

```php
DB::table('users')
    ->join('contacts', function (JoinClause $join) {
        $join->on('users.id', '=', 'contacts.user_id')
            ->where('contacts.user_id', '>', 5);
    })
    ->get();
```

<a name="subquery-joins"></a>
#### 子查询联接

你可以使用 `joinSub`、`leftJoinSub` 和 `rightJoinSub` 方法将查询与子查询联接。这些方法都接收三个参数：子查询、子查询的表别名，以及定义关联列的闭包。下面的示例会获取用户集合，每条用户记录还包含该用户最近发布的博客文章的 `created_at` 时间戳：

```php
$latestPosts = DB::table('posts')
    ->select('user_id', DB::raw('MAX(created_at) as last_post_created_at'))
    ->where('is_published', true)
    ->groupBy('user_id');

$users = DB::table('users')
    ->joinSub($latestPosts, 'latest_posts', function (JoinClause $join) {
        $join->on('users.id', '=', 'latest_posts.user_id');
    })->get();
```

<a name="lateral-joins"></a>
#### 横向联接

> [!WARNING]
> 目前，PostgreSQL、MySQL >= 8.0.14 和 SQL Server 支持横向联接。

你可以使用 `joinLateral` 和 `leftJoinLateral` 方法与子查询执行「横向联接」。这些方法都接收两个参数：子查询及其表别名。联接条件应在子查询的 `where` 子句中指定。横向联接会针对每一行求值，并且可以引用子查询外部的列。

下面的示例会获取用户集合及每个用户最近的三篇博客文章。每个用户在结果集中最多产生三行，每行对应其中一篇文章。联接条件在子查询中通过 `whereColumn` 子句指定，并引用当前用户行：

```php
$latestPosts = DB::table('posts')
    ->select('id as post_id', 'title as post_title', 'created_at as post_created_at')
    ->whereColumn('user_id', 'users.id')
    ->orderBy('created_at', 'desc')
    ->limit(3);

$users = DB::table('users')
    ->joinLateral($latestPosts, 'latest_posts')
    ->get();
```

<a name="unions"></a>
## 并集

查询构建器还提供了便捷的方法，将两个或多个查询合并为「并集」。例如，你可以先创建一个查询，再使用 `union` 方法将其与其他查询合并：

```php
use Illuminate\Support\Facades\DB;

$usersWithoutFirstName = DB::table('users')
    ->whereNull('first_name');

$users = DB::table('users')
    ->whereNull('last_name')
    ->union($usersWithoutFirstName)
    ->get();
```

除了 `union`，查询构建器还提供了 `unionAll` 方法。使用 `unionAll` 合并查询时，不会移除重复结果。`unionAll` 的方法签名与 `union` 相同。

<a name="basic-where-clauses"></a>
## 基本 Where 子句

<a name="where-clauses"></a>
### Where 子句

你可以使用查询构建器的 `where` 方法添加「where」子句。最基本的调用需要三个参数：第一个是列名，第二个是数据库支持的任意运算符，第三个是要与该列的值进行比较的值。

例如，以下查询会获取 `votes` 列等于 `100` 且 `age` 列大于 `35` 的用户：

```php
$users = DB::table('users')
    ->where('votes', '=', 100)
    ->where('age', '>', 35)
    ->get();
```

为方便使用，如果只需判断列是否 `=` 给定值，可以将该值作为 `where` 的第二个参数传入。Laravel 会默认使用 `=` 运算符：

```php
$users = DB::table('users')->where('votes', 100)->get();
```

你也可以向 `where` 方法传入关联数组，快速查询多个列：

```php
$users = DB::table('users')->where([
    'first_name' => 'Jane',
    'last_name' => 'Doe',
])->get();
```

如前所述，你可以使用数据库系统支持的任何运算符：

```php
$users = DB::table('users')
    ->where('votes', '>=', 100)
    ->get();

$users = DB::table('users')
    ->where('votes', '<>', 100)
    ->get();

$users = DB::table('users')
    ->where('name', 'like', 'T%')
    ->get();
```

你还可以向 `where` 函数传入条件数组。数组中的每一项也应是数组，包含通常传给 `where` 方法的三个参数：

```php
$users = DB::table('users')->where([
    ['status', '=', '1'],
    ['subscribed', '<>', '1'],
])->get();
```

> [!WARNING]
> PDO 不支持绑定列名。因此，切勿让用户输入决定查询中引用的列名，包括「order by」子句中的列名。

> [!WARNING]
> MySQL 和 MariaDB 在比较字符串与数字时，会自动将字符串转换为整数。非数字字符串会被转换为 `0`，可能导致意外结果。例如，表中某行的 `secret` 列为 `aaa`，执行 `User::where('secret', 0)` 仍会返回该行。为避免此问题，请在查询前将所有值转换为适当的类型。

<a name="or-where-clauses"></a>
### Or Where 子句

链式调用查询构建器的 `where` 方法时，各「where」子句会通过 `and` 运算符连接。你也可以使用 `orWhere` 方法，通过 `or` 运算符连接子句。`orWhere` 接受的参数与 `where` 相同：

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhere('name', 'John')
    ->get();
```

如果需要用括号对「or」条件分组，可以将闭包作为 `orWhere` 方法的第一个参数传入：

```php
use Illuminate\Database\Query\Builder;

$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhere(function (Builder $query) {
        $query->where('name', 'Abigail')
            ->where('votes', '>', 50);
        })
    ->get();
```

上述示例会生成以下 SQL：

```sql
select * from users where votes > 100 or (name = 'Abigail' and votes > 50)
```

> [!WARNING]
> 应始终对 `orWhere` 调用进行分组，避免应用全局作用域时出现意外行为。

<a name="where-not-clauses"></a>
### Where Not 子句

`whereNot` 和 `orWhereNot` 方法可以对一组查询约束取反。例如，以下查询会排除正在清仓或价格低于 10 的商品：

```php
$products = DB::table('products')
    ->whereNot(function (Builder $query) {
        $query->where('clearance', true)
            ->orWhere('price', '<', 10);
        })
    ->get();
```

<a name="where-any-all-none-clauses"></a>
### Where Any / All / None 子句

有时，你可能需要将相同的查询约束应用于多个列。例如，获取指定列中任意一列与给定值 `LIKE` 匹配的所有记录，可以使用 `whereAny` 方法：

```php
$users = DB::table('users')
    ->where('active', true)
    ->whereAny([
        'name',
        'email',
        'phone',
    ], 'like', 'Example%')
    ->get();
```

上述查询会生成以下 SQL：

```sql
SELECT *
FROM users
WHERE active = true AND (
    name LIKE 'Example%' OR
    email LIKE 'Example%' OR
    phone LIKE 'Example%'
)
```

类似地，`whereAll` 方法可以获取所有指定列都满足给定约束的记录：

```php
$posts = DB::table('posts')
    ->where('published', true)
    ->whereAll([
        'title',
        'content',
    ], 'like', '%Laravel%')
    ->get();
```

上述查询会生成以下 SQL：

```sql
SELECT *
FROM posts
WHERE published = true AND (
    title LIKE '%Laravel%' AND
    content LIKE '%Laravel%'
)
```

`whereNone` 方法可以获取所有指定列都不满足给定约束的记录：

```php
$albums = DB::table('albums')
    ->where('published', true)
    ->whereNone([
        'title',
        'lyrics',
        'tags',
    ], 'like', '%explicit%')
    ->get();
```

上述查询会生成以下 SQL：

```sql
SELECT *
FROM albums
WHERE published = true AND NOT (
    title LIKE '%explicit%' OR
    lyrics LIKE '%explicit%' OR
    tags LIKE '%explicit%'
)
```

<a name="json-where-clauses"></a>
### JSON Where 子句

对于支持 JSON 列类型的数据库，Laravel 也支持查询 JSON 列。目前包括 MariaDB 10.3+、MySQL 8.0+、PostgreSQL 12.0+、SQL Server 2017+ 和 SQLite 3.39.0+。查询 JSON 列时，请使用 `->` 运算符：

```php
$users = DB::table('users')
    ->where('preferences->dining->meal', 'salad')
    ->get();

$users = DB::table('users')
    ->whereIn('preferences->dining->meal', ['pasta', 'salad', 'sandwiches'])
    ->get();
```

你可以使用 `whereJsonContains` 和 `whereJsonDoesntContain` 方法查询 JSON 数组：

```php
$users = DB::table('users')
    ->whereJsonContains('options->languages', 'en')
    ->get();

$users = DB::table('users')
    ->whereJsonDoesntContain('options->languages', 'en')
    ->get();
```

如果应用使用 MariaDB、MySQL 或 PostgreSQL 数据库，可以向 `whereJsonContains` 和 `whereJsonDoesntContain` 方法传入值数组：

```php
$users = DB::table('users')
    ->whereJsonContains('options->languages', ['en', 'de'])
    ->get();

$users = DB::table('users')
    ->whereJsonDoesntContain('options->languages', ['en', 'de'])
    ->get();
```

此外，你可以使用 `whereJsonContainsKey` 或 `whereJsonDoesntContainKey` 方法，获取包含或不包含指定 JSON 键的结果：

```php
$users = DB::table('users')
    ->whereJsonContainsKey('preferences->dietary_requirements')
    ->get();

$users = DB::table('users')
    ->whereJsonDoesntContainKey('preferences->dietary_requirements')
    ->get();
```

最后，你可以使用 `whereJsonLength` 方法按 JSON 数组的长度进行查询：

```php
$users = DB::table('users')
    ->whereJsonLength('options->languages', 0)
    ->get();

$users = DB::table('users')
    ->whereJsonLength('options->languages', '>', 1)
    ->get();
```

<a name="additional-where-clauses"></a>
### 其他 Where 子句

**whereLike / orWhereLike / whereNotLike / orWhereNotLike**

`whereLike` 方法允许你添加「LIKE」子句进行模式匹配。这组方法提供了不依赖具体数据库的字符串匹配方式，并支持切换是否区分大小写。默认情况下，匹配不区分大小写：

```php
$users = DB::table('users')
    ->whereLike('name', '%John%')
    ->get();
```

你可以通过 `caseSensitive` 参数启用区分大小写的搜索：

```php
$users = DB::table('users')
    ->whereLike('name', '%John%', caseSensitive: true)
    ->get();
```

`orWhereLike` 方法允许你添加带有 LIKE 条件的「or」子句：

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhereLike('name', '%John%')
    ->get();
```

`whereNotLike` 方法允许你向查询添加「NOT LIKE」子句：

```php
$users = DB::table('users')
    ->whereNotLike('name', '%John%')
    ->get();
```

类似地，你可以使用 `orWhereNotLike` 添加带有 NOT LIKE 条件的「or」子句：

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhereNotLike('name', '%John%')
    ->get();
```

> [!WARNING]
> SQL Server 目前不支持 `whereLike` 的区分大小写搜索选项。

**whereIn / whereNotIn / orWhereIn / orWhereNotIn**

`whereIn` 方法用于判断指定列的值是否包含在给定数组中：

```php
$users = DB::table('users')
    ->whereIn('id', [1, 2, 3])
    ->get();
```

`whereNotIn` 方法用于判断指定列的值是否不在给定数组中：

```php
$users = DB::table('users')
    ->whereNotIn('id', [1, 2, 3])
    ->get();
```

你也可以将查询对象作为 `whereIn` 方法的第二个参数传入：

```php
$activeUsers = DB::table('users')->select('id')->where('is_active', 1);

$comments = DB::table('comments')
    ->whereIn('user_id', $activeUsers)
    ->get();
```

上述示例会生成以下 SQL：

```sql
select * from comments where user_id in (
    select id
    from users
    where is_active = 1
)
```

> [!WARNING]
> 如果需要向查询绑定大量整数，可以使用 `whereIntegerInRaw` 或 `whereIntegerNotInRaw` 方法，大幅减少内存占用。

**whereBetween / orWhereBetween**

`whereBetween` 方法用于判断列的值是否位于两个值之间：

```php
$users = DB::table('users')
    ->whereBetween('votes', [1, 100])
    ->get();
```

**whereNotBetween / orWhereNotBetween**

`whereNotBetween` 方法用于判断列的值是否位于两个值所构成的区间之外：

```php
$users = DB::table('users')
    ->whereNotBetween('votes', [1, 100])
    ->get();
```

**whereBetweenColumns / whereNotBetweenColumns / orWhereBetweenColumns / orWhereNotBetweenColumns**

`whereBetweenColumns` 方法用于判断列的值是否位于同一行中另外两列的值之间：

```php
$patients = DB::table('patients')
    ->whereBetweenColumns('weight', ['minimum_allowed_weight', 'maximum_allowed_weight'])
    ->get();
```

`whereNotBetweenColumns` 方法用于判断列的值是否位于同一行中另外两列的值所构成的区间之外：

```php
$patients = DB::table('patients')
    ->whereNotBetweenColumns('weight', ['minimum_allowed_weight', 'maximum_allowed_weight'])
    ->get();
```

**whereValueBetween / whereValueNotBetween / orWhereValueBetween / orWhereValueNotBetween**

`whereValueBetween` 方法用于判断给定值是否位于同一行中两个同类型列的值之间：

```php
$products = DB::table('products')
    ->whereValueBetween(100, ['min_price', 'max_price'])
    ->get();
```

`whereValueNotBetween` 方法用于判断给定值是否位于同一行中两列的值所构成的区间之外：

```php
$products = DB::table('products')
    ->whereValueNotBetween(100, ['min_price', 'max_price'])
    ->get();
```

**whereNull / whereNotNull / orWhereNull / orWhereNotNull**

`whereNull` 方法用于判断指定列的值是否为 `NULL`：

```php
$users = DB::table('users')
    ->whereNull('updated_at')
    ->get();
```

`whereNotNull` 方法用于判断列的值是否不为 `NULL`：

```php
$users = DB::table('users')
    ->whereNotNull('updated_at')
    ->get();
```

**whereNullSafeEquals / orWhereNullSafeEquals**

`whereNullSafeEquals` 和 `orWhereNullSafeEquals` 方法可以将列的值与给定值进行比较，并将两个 `NULL` 视为相等：

```php
$lastLoginIp = $request->input('last_login_ip');

$users = DB::table('users')
    ->whereNullSafeEquals('last_login_ip', $lastLoginIp)
    ->get();
```

**whereDate / whereMonth / whereDay / whereYear / whereTime**

`whereDate` 方法可以将列的值与日期进行比较：

```php
$users = DB::table('users')
    ->whereDate('created_at', '2016-12-31')
    ->get();
```

`whereMonth` 方法可以将列的值与指定月份进行比较：

```php
$users = DB::table('users')
    ->whereMonth('created_at', '12')
    ->get();
```

`whereDay` 方法可以将列的值与一个月中的指定日期进行比较：

```php
$users = DB::table('users')
    ->whereDay('created_at', '31')
    ->get();
```

`whereYear` 方法可以将列的值与指定年份进行比较：

```php
$users = DB::table('users')
    ->whereYear('created_at', '2016')
    ->get();
```

`whereTime` 方法可以将列的值与指定时间进行比较：

```php
$users = DB::table('users')
    ->whereTime('created_at', '=', '11:20:45')
    ->get();
```

**wherePast / whereFuture / whereToday / whereBeforeToday / whereAfterToday**

`wherePast` 和 `whereFuture` 方法可以判断列的值是否位于过去或未来：

```php
$invoices = DB::table('invoices')
    ->wherePast('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereFuture('due_at')
    ->get();
```

`whereNowOrPast` 和 `whereNowOrFuture` 方法可以判断列的值是否位于过去或未来，并将当前日期和时间包含在内：

```php
$invoices = DB::table('invoices')
    ->whereNowOrPast('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereNowOrFuture('due_at')
    ->get();
```

`whereToday`、`whereBeforeToday` 和 `whereAfterToday` 方法分别用于判断列的值是否为今天、早于今天或晚于今天：

```php
$invoices = DB::table('invoices')
    ->whereToday('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereBeforeToday('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereAfterToday('due_at')
    ->get();
```

类似地，`whereTodayOrBefore` 和 `whereTodayOrAfter` 方法可以判断列的值是否早于或晚于今天，并包含今天：

```php
$invoices = DB::table('invoices')
    ->whereTodayOrBefore('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereTodayOrAfter('due_at')
    ->get();
```

**whereColumn / orWhereColumn**

`whereColumn` 方法可以判断两列的值是否相等：

```php
$users = DB::table('users')
    ->whereColumn('first_name', 'last_name')
    ->get();
```

你也可以向 `whereColumn` 方法传入比较运算符：

```php
$users = DB::table('users')
    ->whereColumn('updated_at', '>', 'created_at')
    ->get();
```

你还可以向 `whereColumn` 方法传入列比较条件的数组。这些条件会通过 `and` 运算符连接：

```php
$users = DB::table('users')
    ->whereColumn([
        ['first_name', '=', 'last_name'],
        ['updated_at', '>', 'created_at'],
    ])->get();
```

<a name="logical-grouping"></a>
### 逻辑分组

有时，你可能需要用括号对多个「where」子句分组，以实现所需的查询逻辑。通常应始终用括号对 `orWhere` 方法的调用分组，避免意外的查询行为。为此，可以向 `where` 方法传入闭包：

```php
$users = DB::table('users')
    ->where('name', '=', 'John')
    ->where(function (Builder $query) {
        $query->where('votes', '>', 100)
            ->orWhere('title', '=', 'Admin');
    })
    ->get();
```

如上所示，向 `where` 方法传入闭包，就会让查询构建器创建一个约束组。闭包会接收一个查询构建器实例，你可以用它设置括号内的约束。上述示例会生成以下 SQL：

```sql
select * from users where name = 'John' and (votes > 100 or title = 'Admin')
```

> [!WARNING]
> 应始终对 `orWhere` 调用进行分组，避免应用全局作用域时出现意外行为。

<a name="advanced-where-clauses"></a>
## 高级 Where 子句

<a name="where-exists-clauses"></a>
### Where Exists 子句

`whereExists` 方法允许你编写「where exists」SQL 子句。该方法接受一个闭包，闭包会接收查询构建器实例，让你可以定义「exists」子句内部的查询：

```php
$users = DB::table('users')
    ->whereExists(function (Builder $query) {
        $query->select(DB::raw(1))
            ->from('orders')
            ->whereColumn('orders.user_id', 'users.id');
    })
    ->get();
```

你也可以向 `whereExists` 方法传入查询对象来代替闭包：

```php
$orders = DB::table('orders')
    ->select(DB::raw(1))
    ->whereColumn('orders.user_id', 'users.id');

$users = DB::table('users')
    ->whereExists($orders)
    ->get();
```

上述两个示例都会生成以下 SQL：

```sql
select * from users
where exists (
    select 1
    from orders
    where orders.user_id = users.id
)
```

<a name="subquery-where-clauses"></a>
### 子查询 Where 子句

有时，你可能需要构建「where」子句，将子查询结果与给定值进行比较。向 `where` 方法传入闭包和值即可实现。例如，以下查询会获取最近一条「membership」记录属于指定类型的所有用户：

```php
use App\Models\User;
use Illuminate\Database\Query\Builder;

$users = User::where(function (Builder $query) {
    $query->select('type')
        ->from('membership')
        ->whereColumn('membership.user_id', 'users.id')
        ->orderByDesc('membership.start_date')
        ->limit(1);
}, 'Pro')->get();
```

你也可能需要将某列与子查询结果进行比较。向 `where` 方法传入列名、运算符和闭包即可实现。例如，以下查询会获取金额低于平均值的所有收入记录：

```php
use App\Models\Income;
use Illuminate\Database\Query\Builder;

$incomes = Income::where('amount', '<', function (Builder $query) {
    $query->selectRaw('avg(i.amount)')->from('incomes as i');
})->get();
```

<a name="full-text-where-clauses"></a>
### 全文 Where 子句

> [!WARNING]
> 目前，MariaDB、MySQL 和 PostgreSQL 支持全文 Where 子句。

`whereFullText` 和 `orWhereFullText` 方法可以为具有[全文索引](/docs/{{version}}/migrations#available-index-types)的列添加全文「where」子句。Laravel 会根据底层数据库系统，将这些方法转换为相应的 SQL。例如，使用 MariaDB 或 MySQL 时，会生成 `MATCH AGAINST` 子句：

```php
$users = DB::table('users')
    ->whereFullText('bio', 'web developer')
    ->get();
```

<a name="vector-similarity-clauses"></a>
### 向量相似度子句

> [!NOTE]
> 目前，使用 `pgvector` 扩展的 PostgreSQL 连接以及 MariaDB 11.7 及更高版本支持向量相似度子句。有关定义向量列和索引的信息，请参阅[迁移文档](/docs/{{version}}/migrations#available-column-types)。

`whereVectorSimilarTo` 方法根据与给定向量的余弦相似度筛选结果，并按相关性排序。`minSimilarity` 阈值应介于 `0.0` 和 `1.0` 之间，其中 `1.0` 表示完全相同：

```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', $queryEmbedding, minSimilarity: 0.4)
    ->limit(10)
    ->get();
```

如果向量参数传入的是普通字符串，Laravel 会使用 [Laravel AI SDK](/docs/{{version}}/ai-sdk#embeddings) 自动为其生成嵌入向量：

```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', 'Best wineries in Napa Valley')
    ->limit(10)
    ->get();
```

默认情况下，`whereVectorSimilarTo` 还会按距离对结果排序，相似度最高的结果排在前面。你可以将 `order` 参数设为 `false`，禁用此排序：

```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', $queryEmbedding, minSimilarity: 0.4, order: false)
    ->orderBy('created_at', 'desc')
    ->limit(10)
    ->get();
```

如果需要更精细的控制，可以分别使用 `selectVectorDistance`、`whereVectorDistanceLessThan` 和 `orderByVectorDistance` 方法：

```php
$documents = DB::table('documents')
    ->select('*')
    ->selectVectorDistance('embedding', $queryEmbedding, as: 'distance')
    ->whereVectorDistanceLessThan('embedding', $queryEmbedding, maxDistance: 0.3)
    ->orderByVectorDistance('embedding', $queryEmbedding)
    ->limit(10)
    ->get();
```

使用 PostgreSQL 时，必须先加载 `pgvector` 扩展，才能创建 `vector` 列：

```php
Schema::ensureVectorExtensionExists();
```

<a name="ordering-grouping-limit-and-offset"></a>
## 排序、分组、条数限制和偏移量

<a name="ordering"></a>
### 排序

<a name="orderby"></a>
#### `orderBy` 方法

`orderBy` 方法可以按指定列对查询结果排序。第一个参数是要排序的列，第二个参数是排序方向，可以是 `asc` 或 `desc`：

```php
$users = DB::table('users')
    ->orderBy('name', 'desc')
    ->get();
```

要按多列排序，只需多次调用 `orderBy`：

```php
$users = DB::table('users')
    ->orderBy('name', 'desc')
    ->orderBy('email', 'asc')
    ->get();
```

排序方向是可选的，默认为升序。如果要降序排列，可以指定 `orderBy` 的第二个参数，或直接使用 `orderByDesc`：

```php
$users = DB::table('users')
    ->orderByDesc('verified_at')
    ->get();
```

此外，使用 `->` 运算符，可以按 JSON 列内部的值对结果排序：

```php
$corporations = DB::table('corporations')
    ->where('country', 'US')
    ->orderBy('location->state')
    ->get();
```

<a name="latest-oldest"></a>
#### `latest` 和 `oldest` 方法

`latest` 和 `oldest` 方法可以轻松按日期对结果排序。默认按表的 `created_at` 列排序，你也可以传入要排序的列名：

```php
$user = DB::table('users')
    ->latest()
    ->first();
```

<a name="random-ordering"></a>
#### 随机排序

`inRandomOrder` 方法可以随机排列查询结果。例如，下面会随机获取一个用户：

```php
$randomUser = DB::table('users')
    ->inRandomOrder()
    ->first();
```

<a name="removing-existing-orderings"></a>
#### 移除现有排序

`reorder` 方法会移除查询中已有的所有「order by」子句：

```php
$query = DB::table('users')->orderBy('name');

$unorderedUsers = $query->reorder()->get();
```

调用 `reorder` 时，你可以传入列名和排序方向，移除已有的所有「order by」子句，并应用全新的排序：

```php
$query = DB::table('users')->orderBy('name');

$usersOrderedByEmail = $query->reorder('email', 'desc')->get();
```

为方便使用，你可以通过 `reorderDesc` 方法将查询结果重新按降序排列：

```php
$query = DB::table('users')->orderBy('name');

$usersOrderedByEmail = $query->reorderDesc('email')->get();
```

<a name="grouping"></a>
### 分组

<a name="groupby-having"></a>
#### `groupBy` 和 `having` 方法

`groupBy` 和 `having` 方法可以对查询结果进行分组及筛选。`having` 的方法签名与 `where` 类似：

```php
$users = DB::table('users')
    ->groupBy('account_id')
    ->having('account_id', '>', 100)
    ->get();
```

你可以使用 `havingBetween` 方法筛选位于指定范围内的结果：

```php
$report = DB::table('orders')
    ->selectRaw('count(id) as number_of_orders, customer_id')
    ->groupBy('customer_id')
    ->havingBetween('number_of_orders', [5, 15])
    ->get();
```

向 `groupBy` 方法传入多个参数，即可按多列分组：

```php
$users = DB::table('users')
    ->groupBy('first_name', 'status')
    ->having('account_id', '>', 100)
    ->get();
```

要构建更复杂的 `having` 语句，请参阅 [havingRaw](#raw-methods) 方法。

<a name="limit-and-offset"></a>
### 条数限制和偏移量

你可以使用 `limit` 和 `offset` 方法，限制查询返回的结果数量，或跳过指定数量的结果：

```php
$users = DB::table('users')
    ->offset(10)
    ->limit(5)
    ->get();
```

<a name="conditional-clauses"></a>
## 条件子句

有时，你可能希望根据其他条件决定是否应用某些查询子句。例如，仅当传入的 HTTP 请求中存在某个输入值时，才应用 `where` 语句。可以通过 `when` 方法实现：

```php
$role = $request->input('role');

$users = DB::table('users')
    ->when($role, function (Builder $query, string $role) {
        $query->where('role_id', $role);
    })
    ->get();
```

`when` 方法仅在第一个参数求值为 `true` 时执行指定闭包；求值为 `false` 时则不执行。因此，在上述示例中，只有请求中存在 `role` 字段且其值求值为 `true` 时，才会调用传给 `when` 的闭包。

你可以将另一个闭包作为 `when` 的第三个参数传入。该闭包仅在第一个参数求值为 `false` 时执行。下面的示例使用此功能配置查询的默认排序：

```php
$sortByVotes = $request->boolean('sort_by_votes');

$users = DB::table('users')
    ->when($sortByVotes, function (Builder $query, bool $sortByVotes) {
        $query->orderBy('votes');
    }, function (Builder $query) {
        $query->orderBy('name');
    })
    ->get();
```

<a name="insert-statements"></a>
## 插入语句

查询构建器还提供了 `insert` 方法，用于向数据库表插入记录。该方法接受由列名和值组成的数组：

```php
DB::table('users')->insert([
    'email' => 'kayla@example.com',
    'votes' => 0
]);
```

传入二维数组可以一次插入多条记录，每个子数组代表要插入表中的一条记录：

```php
DB::table('users')->insert([
    ['email' => 'picard@example.com', 'votes' => 0],
    ['email' => 'janeway@example.com', 'votes' => 0],
]);
```

`insertOrIgnore` 方法会忽略插入数据库记录时发生的错误。请注意，该方法会忽略重复记录错误，某些数据库引擎还可能忽略其他类型的错误。例如，`insertOrIgnore` 会[绕过 MySQL 的严格模式](https://dev.mysql.com/doc/refman/en/sql-mode.html#ignore-effect-on-execution)：

```php
DB::table('users')->insertOrIgnore([
    ['id' => 1, 'email' => 'sisko@example.com'],
    ['id' => 2, 'email' => 'archer@example.com'],
]);
```

`insertUsing` 方法可以通过子查询确定要插入的数据，并将新记录插入表中：

```php
DB::table('pruned_users')->insertUsing([
    'id', 'name', 'email', 'email_verified_at'
], DB::table('users')->select(
    'id', 'name', 'email', 'email_verified_at'
)->where('updated_at', '<=', now()->minus(months: 1)));
```

<a name="auto-incrementing-ids"></a>
#### 自增 ID

如果表具有自增 ID，可以使用 `insertGetId` 方法插入记录并获取该 ID：

```php
$id = DB::table('users')->insertGetId(
    ['email' => 'john@example.com', 'votes' => 0]
);
```

> [!WARNING]
> 使用 PostgreSQL 时，`insertGetId` 方法默认自增列名为 `id`。如果要从其他「序列」获取 ID，可以将列名作为该方法的第二个参数传入。

<a name="upserts"></a>
### 插入或更新

`upsert` 方法会插入不存在的记录，并使用指定的新值更新已有记录。第一个参数是要插入或更新的值，第二个参数列出在表中唯一标识记录的列。第三个也是最后一个参数是列名数组，指定存在匹配记录时应更新哪些列：

```php
DB::table('flights')->upsert(
    [
        ['departure' => 'Oakland', 'destination' => 'San Diego', 'price' => 99],
        ['departure' => 'Chicago', 'destination' => 'New York', 'price' => 150]
    ],
    ['departure', 'destination'],
    ['price']
);
```

在上述示例中，Laravel 会尝试插入两条记录。如果已存在 `departure` 和 `destination` 列值相同的记录，就更新该记录的 `price` 列。

> [!WARNING]
> 除 SQL Server 外，所有数据库都要求 `upsert` 第二个参数中的列具有「主键」或「唯一」索引。此外，MariaDB 和 MySQL 数据库驱动会忽略第二个参数，始终通过表的「主键」和「唯一」索引来检测现有记录。

<a name="update-statements"></a>
## 更新语句

除了插入记录，查询构建器还可以通过 `update` 方法更新已有记录。与 `insert` 一样，该方法接受由列名和值组成的数组，指定要更新的列，并返回受影响的行数。你可以使用 `where` 子句限制 `update` 查询的范围：

```php
$affected = DB::table('users')
    ->where('id', 1)
    ->update(['votes' => 1]);
```

<a name="update-or-insert"></a>
#### 更新或插入

有时，你可能希望更新已有记录，并在不存在匹配记录时创建记录。这时可以使用 `updateOrInsert` 方法。该方法接受两个参数：用于查找记录的条件数组，以及指定要更新的列和值的数组。

`updateOrInsert` 会使用第一个参数中的列和值查找匹配记录。如果记录存在，就使用第二个参数中的值更新它。如果找不到记录，则合并两个参数中的属性，插入一条新记录：

```php
DB::table('users')
    ->updateOrInsert(
        ['email' => 'john@example.com', 'name' => 'John'],
        ['votes' => '2']
    );
```

你可以向 `updateOrInsert` 传入闭包，根据匹配记录是否存在，自定义要更新或插入数据库的属性：

```php
DB::table('users')->updateOrInsert(
    ['user_id' => $user_id],
    fn ($exists) => $exists ? [
        'name' => $data['name'],
        'email' => $data['email'],
    ] : [
        'name' => $data['name'],
        'email' => $data['email'],
        'marketable' => true,
    ],
);
```

<a name="updating-json-columns"></a>
### 更新 JSON 列

更新 JSON 列时，应使用 `->` 语法更新 JSON 对象中的对应键。MariaDB 10.3+、MySQL 5.7+ 和 PostgreSQL 9.5+ 支持此操作：

```php
$affected = DB::table('users')
    ->where('id', 1)
    ->update(['options->enabled' => true]);
```

<a name="increment-and-decrement"></a>
### 自增与自减

查询构建器还提供了便捷的方法，用于增加或减少指定列的值。这两种方法都至少接受一个参数，即要修改的列。你可以传入第二个参数，指定增加或减少的数量：

```php
DB::table('users')->increment('votes');

DB::table('users')->increment('votes', 5);

DB::table('users')->decrement('votes');

DB::table('users')->decrement('votes', 5);
```

如有需要，你还可以指定在自增或自减操作中一并更新的其他列：

```php
DB::table('users')->increment('votes', 1, ['name' => 'John']);
```

此外，你可以通过 `incrementEach` 和 `decrementEach` 方法，一次增加或减少多列的值：

```php
DB::table('users')->incrementEach([
    'votes' => 5,
    'balance' => 100,
]);
```

<a name="delete-statements"></a>
## 删除语句

查询构建器的 `delete` 方法可以删除表中的记录，并返回受影响的行数。你可以在调用该方法前添加「where」子句，限制删除范围：

```php
$deleted = DB::table('users')->delete();

$deleted = DB::table('users')->where('votes', '>', 100)->delete();
```

<a name="pessimistic-locking"></a>
## 悲观锁

查询构建器还提供了一些方法，帮助你在执行 `select` 语句时使用「悲观锁」。调用 `sharedLock` 方法可以使用「共享锁」执行查询。共享锁会防止选中的行被修改，直到事务提交：

```php
DB::table('users')
    ->where('votes', '>', 100)
    ->sharedLock()
    ->get();
```

你也可以使用 `lockForUpdate` 方法。「for update」锁会防止选中的记录被修改，或被其他共享锁选中：

```php
DB::table('users')
    ->where('votes', '>', 100)
    ->lockForUpdate()
    ->get();
```

虽然并非强制要求，但建议将悲观锁放在[事务](/docs/{{version}}/database#database-transactions)中使用。这可以确保整个操作完成之前，获取的数据在数据库中不会被修改。如果操作失败，事务会自动回滚所有更改并释放锁：

```php
DB::transaction(function () {
    $sender = DB::table('users')
        ->lockForUpdate()
        ->find(1);

    $receiver = DB::table('users')
        ->lockForUpdate()
        ->find(2);

    if ($sender->balance < 100) {
        throw new RuntimeException('Balance too low.');
    }

    DB::table('users')
        ->where('id', $sender->id)
        ->update([
            'balance' => $sender->balance - 100
        ]);

    DB::table('users')
        ->where('id', $receiver->id)
        ->update([
            'balance' => $receiver->balance + 100
        ]);
});
```

<a name="reusable-query-components"></a>
## 可复用的查询组件

如果应用中存在重复的查询逻辑，可以使用查询构建器的 `tap` 和 `pipe` 方法，将这些逻辑提取为可复用的对象。假设应用中有以下两个查询：

```php
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\DB;

$destination = $request->query('destination');

DB::table('flights')
    ->when($destination, function (Builder $query, string $destination) {
        $query->where('destination', $destination);
    })
    ->orderByDesc('price')
    ->get();

// ...

$destination = $request->query('destination');

DB::table('flights')
    ->when($destination, function (Builder $query, string $destination) {
        $query->where('destination', $destination);
    })
    ->where('user', $request->user()->id)
    ->orderBy('destination')
    ->get();
```

你可以将两个查询共有的目的地筛选逻辑提取为可复用的对象：

```php
<?php

namespace App\Scopes;

use Illuminate\Database\Query\Builder;

class DestinationFilter
{
    public function __construct(
        private ?string $destination,
    ) {
        //
    }

    public function __invoke(Builder $query): void
    {
        $query->when($this->destination, function (Builder $query) {
            $query->where('destination', $this->destination);
        });
    }
}
```

然后，使用查询构建器的 `tap` 方法，将该对象的逻辑应用到查询中：

```php
use App\Scopes\DestinationFilter;
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\DB;

DB::table('flights')
    ->when($destination, function (Builder $query, string $destination) { // [tl! remove]
        $query->where('destination', $destination); // [tl! remove]
    }) // [tl! remove]
    ->tap(new DestinationFilter($destination)) // [tl! add]
    ->orderByDesc('price')
    ->get();

// ...

DB::table('flights')
    ->when($destination, function (Builder $query, string $destination) { // [tl! remove]
        $query->where('destination', $destination); // [tl! remove]
    }) // [tl! remove]
    ->tap(new DestinationFilter($destination)) // [tl! add]
    ->where('user', $request->user()->id)
    ->orderBy('destination')
    ->get();
```

<a name="query-pipes"></a>
#### 查询管道

`tap` 方法始终返回查询构建器。如果希望提取的对象执行查询并返回其他值，可以改用 `pipe` 方法。

下面的查询对象包含整个应用共用的[分页](/docs/{{version}}/pagination)逻辑。`DestinationFilter` 只为查询添加条件，而 `Paginate` 对象会执行查询并返回分页器实例：

```php
<?php

namespace App\Scopes;

use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Database\Query\Builder;

class Paginate
{
    public function __construct(
        private string $sortBy = 'timestamp',
        private string $sortDirection = 'desc',
        private int $perPage = 25,
    ) {
        //
    }

    public function __invoke(Builder $query): LengthAwarePaginator
    {
        return $query->orderBy($this->sortBy, $this->sortDirection)
            ->paginate($this->perPage, pageName: 'p');
    }
}
```

通过查询构建器的 `pipe` 方法，就可以使用该对象应用共用的分页逻辑：

```php
$flights = DB::table('flights')
    ->tap(new DestinationFilter($destination))
    ->pipe(new Paginate);
```

<a name="debugging"></a>
## 调试

构建查询时，你可以使用 `dd` 和 `dump` 方法输出当前查询的绑定值和 SQL。`dd` 会显示调试信息并停止执行请求；`dump` 则会显示调试信息，并让请求继续执行：

```php
DB::table('users')->where('votes', '>', 100)->dd();

DB::table('users')->where('votes', '>', 100)->dump();
```

你也可以调用查询的 `dumpRawSql` 和 `ddRawSql` 方法，输出已正确代入所有绑定参数的完整 SQL：

```php
DB::table('users')->where('votes', '>', 100)->dumpRawSql();

DB::table('users')->where('votes', '>', 100)->ddRawSql();
```
