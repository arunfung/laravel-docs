
# 数据库：查询构建器
-   [简介](#introduction)
-   [运行数据库查询](#running-database-queries)
    -   [分块结果](#chunking-results)
    -   [惰性流式结果](#streaming-results-lazily)
    -   [聚合](#aggregates)
-   [Select 语句](#select-statements)
-   [原始表达式](#raw-expressions)
-   [连接 (Joins)](#joins)
-   [联合 (Unions)](#unions)
-   [基础 Where 子句](#basic-where-clauses)
    -   [Where 子句](#where-clauses)
    -   [Or Where 子句](#or-where-clauses)
    -   [Where Not 子句](#where-not-clauses)
    -   [Where Any / All / None 子句](#where-any-all-none-clauses)
    -   [JSON Where 子句](#json-where-clauses)
    -   [附加 Where 子句](#additional-where-clauses)
    -   [逻辑分组](#logical-grouping)
-   [高级 Where 子句](#advanced-where-clauses)
    -   [Where Exists 子句](#where-exists-clauses)
    -   [子查询 Where 子句](#subquery-where-clauses)
    -   [全文本 Where 子句](#full-text-where-clauses)
-   [排序、分组、限制和偏移](#ordering-grouping-limit-and-offset)
    -   [排序](#ordering)
    -   [分组](#grouping)
    -   [限制和偏移](#limit-and-offset)
-   [条件子句](#conditional-clauses)
-   [插入语句](#insert-statements)
    -   [插入或更新 (Upserts)](#upserts)
-   [更新语句](#update-statements)
    -   [更新 JSON 列](#updating-json-columns)
    -   [自增与自减](#increment-and-decrement)
-   [删除语句](#delete-statements)
-   [悲观锁](#pessimistic-locking)
-   [可重用的查询组件](#reusable-query-components)
-   [调试](#debugging)

## 简介

Laravel 的数据库查询构建器提供了一个方便、流畅的接口，用于创建和运行数据库查询。
它可以用来执行你应用程序中的大多数数据库操作，并且与 Laravel 支持的所有数据库系统完美兼容。

Laravel 的查询构建器使用 **PDO 参数绑定** 来保护你的应用程序免受 SQL 注入攻击。
对于传递给查询构建器的查询绑定字符串，无需进行清理或过滤。

> [!警告]
> PDO 不支持绑定列名。因此，你绝不应该允许用户输入来决定查询中引用的列名，包括 “order by” 子句中的列。



<a name="running-database-queries"></a>
## 运行数据库查询

<a name="retrieving-all-rows-from-a-table"></a>
#### 从表中检索所有记录

可以使用 `DB` facade 提供的 `table` 方法开始查询。`table` 方法为指定表返回链式查询构造器实例，允许在查询上链接更多约束，最后使用 `get` 方法检索查询结果：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * Show a list of all of the application's users.
     */
    public function index(): View
    {
        $users = DB::table('users')->get();

        return view('user.index', ['users' => $users]);
    }
}
```
`get` 方法返回包含查询结果的 `Illuminate\Support\Collection` 实例，每个结果都是 PHP `stdClass` 对象的实例。可以将列作为对象的属性来访问每个列的值：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')->get();

foreach ($users as $user) {
    echo $user->name;
}
```
>[!注意]
>Laravel 集合提供了各种及其强大的方法来映射和裁切数据。有关 Laravel 集合的更多信息，[查看 集合文档 ]((https://learnku.com/docs/laravel/12.x/collections "查看 集合文档 ")。
<a name="retrieving-a-single-row-column-from-a-table"></a>
#### 从表中检索单行或单列

如果只需要从数据库表中检索单行，可以使用 `DB` facade 中的 `first` 方法。 此方法将返回单个 `stdClass` 对象：

```php
$user = DB::table('users')->where('name', 'John')->first();

return $user->email;
```



如果您想从数据库表中检索单行数据，但在找不到匹配行时抛出 `Illuminate\Database\RecordNotFoundException` 异常，可以使用 `firstOrFail` 方法。如果未捕获 `RecordNotFoundException` 异常，系统将自动向客户端返回 404 HTTP 响应：
```php
$user = DB::table('users')->where('name', 'John')->firstOrFail();
```
如果你不需要整行，可以使用 `value` 方法从记录中提取单个值。此方法将直接返回列的值：

```php
$email = DB::table('users')->where('name', 'John')->value('email');
```

要通过 `id` 列检索单行，使用 `find` 方法：

```php
$user = DB::table('users')->find(3);
```

<a name="retrieving-a-list-of-column-values"></a>
### 获取某一列的值列表

如果要检索包含单个列值的 `Illuminate\Support\Collection` 实例，则可以使用 `pluck` 方法。在此示例中，将检索 user 表中 title 的集合：

```php
use Illuminate\Support\Facades\DB;

$titles = DB::table('users')->pluck('title');

foreach ($titles as $title) {
    echo $title;
}
```

可以通过向 `pluck` 方法提供第二个参数来指定结果集中应该用作 `key` 的列：

```php
$titles = DB::table('users')->pluck('title', 'name');

foreach ($titles as $name => $title) {
    echo $title;
}
```

<a name="chunking-results"></a>
### 分块结果

如果需要处理数千条数据库记录，可以考虑使用 `DB` facade 提供的 `chunk` 方法。此方法每次检索一小块结果，并将每个块传入闭包进行处理。例如，每次以 100 条记录为块检索整个 `users` 表：

```php
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

DB::table('users')->orderBy('id')->chunk(100, function (Collection $users) {
    foreach ($users as $user) {
        // ...
    }
});
```



可以通过从闭包中返回 `false` 来停止处理其余的块：

```php
DB::table('users')->orderBy('id')->chunk(100, function (Collection $users) {
    // Process the records...

    return false;
});
```

如果在对结果进行分块时更新数据库记录，那分块结果可能会以意想不到的方式更改。如果计划在分块时更新检索到的记录，最好使用 `chunkById` 方法。此方法将根据记录的主键自动对结果进行分页:

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

由于 `chunkById` 和 `lazyById` 方法会向执行的查询添加它们自己的 「where」 条件，因此你通常应该 [逻辑分组](https://learnku.com/docs/laravel/12.x/logical-grouping "逻辑分组") 自己的条件到一个闭包中：

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

> [!警告]
> 当在更新或删除块回调中的记录时，对主键或外键的任何更改都可能影响块查询。这可能会导致记录未包含在分块结果中。

<a name="streaming-results-lazily"></a>
### 延迟流式结果

`lazy` 方法的工作原理类似于 [`chunk` 方法](https://learnku.com/docs/laravel/12.x/chunking-results)，因为都是以块的形式执行查询。但是，`lazy()` 方法不是将每个块传递给回调，而是返回[`LazyCollection`](https://learnku.com/docs/laravel/12.x/collections#lazy-collections) ，可以以单个流的形式与结果进行交互：

```php
use Illuminate\Support\Facades\DB;

DB::table('users')->orderBy('id')->lazy()->each(function (object $user) {
    // ...
});
```



再一次说明，如果你计划在遍历已检索的记录时更新它们，最好改用 `lazyById` 或 `lazyByIdDesc` 方法。这些方法会基于记录的主键自动分页结果：

```php
DB::table('users')->where('active', false)
    ->lazyById()->each(function (object $user) {
        DB::table('users')
            ->where('id', $user->id)
            ->update(['active' => true]);
    });
```

> [!警告]
> 当在遍历记录时更新或删除它们时，对主键或外键的任何更改都可能影响分块查询。这可能会导致某些记录未被包含在结果中。

### 聚合

查询构建器还提供了多种方法来获取聚合值，比如 `count`、`max`、`min`、`avg` 和 `sum`。你可以在构建查询后调用这些方法：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')->count();

$price = DB::table('orders')->max('price');
```

当然，你也可以将这些方法与其他子句结合，以精细化地计算聚合值：

```php
$price = DB::table('orders')
    ->where('finalized', 1)
    ->avg('price');
```

#### 判断记录是否存在

与其使用 `count` 方法来判断是否存在符合查询条件的记录，你可以使用 `exists` 和 `doesntExist` 方法：

```php
if (DB::table('orders')->where('finalized', 1)->exists()) {
    // ...
}

if (DB::table('orders')->where('finalized', 1)->doesntExist()) {
    // ...
}
```

## Select 语句

#### 指定一个 Select 子句



你可能并不总是希望从数据库表中选择所有列。使用 `select` 方法，你可以为查询指定一个自定义的 "select" 子句：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')
    ->select('name', 'email as user_email')
    ->get();
```

`distinct` 方法允许你强制查询返回不重复的结果：

```php
$users = DB::table('users')->distinct()->get();
```

如果你已经有一个查询构建器实例，并且希望在它已有的 select 子句中再添加一列，可以使用 `addSelect` 方法：

```php
$query = DB::table('users')->select('name');

$users = $query->addSelect('age')->get();
```

## 原始表达式（Raw Expressions）

有时候，你可能需要在查询中插入一个任意的字符串。要创建一个原始字符串表达式，你可以使用 `DB` facade 提供的 `raw` 方法：

```php
$users = DB::table('users')
    ->select(DB::raw('count(*) as user_count, status'))
    ->where('status', '<>', 1)
    ->groupBy('status')
    ->get();
```

> [!警告]
> 原始语句会以字符串的形式被注入到查询中，因此你必须极其小心，避免产生 SQL 注入漏洞。

### 原始方法（Raw Methods）

除了使用 `DB::raw` 方法，你也可以使用下面的方法在查询的不同部分插入原始表达式。**请记住，Laravel 不能保证任何使用原始表达式的查询都能避免 SQL 注入漏洞。**

#### `selectRaw`

`selectRaw` 方法可以替代 `addSelect(DB::raw(/* ... */))`。此方法的第二个参数可以接受一个可选的绑定数组：

```php
$orders = DB::table('orders')
    ->selectRaw('price * ? as price_with_tax', [1.0825])
    ->get();
```



#### `whereRaw / orWhereRaw`

`whereRaw` 和 `orWhereRaw` 方法可用于向查询中注入原始的 "where" 子句。这些方法的第二个参数可以接受一个可选的绑定数组：

```php
$orders = DB::table('orders')
    ->whereRaw('price > IF(state = "TX", ?, 100)', [200])
    ->get();
```

#### `havingRaw / orHavingRaw`

`havingRaw` 和 `orHavingRaw` 方法可用于为 "having" 子句提供原始字符串。这些方法的第二个参数也可以接受一个可选的绑定数组：

```php
$orders = DB::table('orders')
    ->select('department', DB::raw('SUM(price) as total_sales'))
    ->groupBy('department')
    ->havingRaw('SUM(price) > ?', [2500])
    ->get();
```

#### `orderByRaw`

`orderByRaw` 方法可用于为 "order by" 子句提供原始字符串：

```php
$orders = DB::table('orders')
    ->orderByRaw('updated_at - created_at DESC')
    ->get();
```

### `groupByRaw`

`groupByRaw` 方法可用于为 `group by` 子句提供原始字符串：

```php
$orders = DB::table('orders')
    ->select('city', 'state')
    ->groupByRaw('city, state')
    ->get();
```

## 联接（Joins）

#### 内连接子句（Inner Join Clause）

查询构建器也可以用于向查询添加联接子句。要执行基本的 "inner join"（内连接），可以在查询构建器实例上使用 `join` 方法。传递给 `join` 方法的第一个参数是要联接的表名，其余参数用于指定联接的列约束。你甚至可以在单个查询中联接多个表：

```php
use Illuminate\Support\Facades\DB;

$users = DB::table('users')
    ->join('contacts', 'users.id', '=', 'contacts.user_id')
    ->join('orders', 'users.id', '=', 'orders.user_id')
    ->select('users.*', 'contacts.phone', 'orders.price')
    ->get();
```



<a name="left-join-right-join-clause"></a>
#### Left Join / Right Join 子句

如果你想使用「left join」或者「right join」代替「inner join」，可以使用 `leftJoin` 或者 `rightJoin` 方法。这两个方法与 `join` 方法用法相同：

```php
$users = DB::table('users')
    ->leftJoin('posts', 'users.id', '=', 'posts.user_id')
    ->get();

$users = DB::table('users')
    ->rightJoin('posts', 'users.id', '=', 'posts.user_id')
    ->get();
```

<a name="cross-join-clause"></a>
#### 交叉连接子句

你可以使用 `crossJoin` 方法来执行「交叉连接」。交叉连接会在第一个表和连接的表之间生成笛卡尔积：

```php
$sizes = DB::table('sizes')
    ->crossJoin('colors')
    ->get();
```

<a name="advanced-join-clauses"></a>
#### 高级连接子句

你也可以指定更高级的连接子句。为此，可以将一个闭包作为 `join` 方法的第二个参数传递。该闭包将接收到一个 `Illuminate\Database\Query\JoinClause` 实例，允许你对「join」子句指定约束：

```php
DB::table('users')
    ->join('contacts', function (JoinClause $join) {
        $join->on('users.id', '=', 'contacts.user_id')->orOn(/* ... */);
    })
    ->get();
```

如果你想在连接中使用 「where」子句，可以使用 `JoinClause` 实例提供的 `where` 和 `orWhere` 方法。这些方法不是比较两个列，而是将列与一个值进行比较：

```php
DB::table('users')
    ->join('contacts', function (JoinClause $join) {
        $join->on('users.id', '=', 'contacts.user_id')
            ->where('contacts.user_id', '>', 5);
    })
    ->get();
```



#### 子查询联接（Subquery Joins）

你可以使用 `joinSub`、`leftJoinSub` 和 `rightJoinSub` 方法将一个查询与子查询联接。每个方法接收三个参数：子查询、子查询的表别名，以及定义相关列的闭包。在下面的示例中，我们将获取用户集合，并在每条用户记录中包含该用户最近发布博客文章的 `created_at` 时间戳：

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

#### 横向联接（Lateral Joins）

> [!警告]
> 横向联接目前支持 PostgreSQL、MySQL >= 8.0.14 和 SQL Server。

你可以使用 `joinLateral` 和 `leftJoinLateral` 方法对子查询执行“横向联接”。每个方法接收两个参数：子查询和子查询的表别名。联接条件应在给定子查询的 `where` 子句中指定。横向联接会对每一行进行评估，并且可以引用子查询之外的列。

在下面的示例中，我们将获取用户集合及每个用户最近的三篇博客文章。每个用户在结果集中最多会生成三行：每一行对应一篇最近的博客文章。联接条件通过子查询中的 `whereColumn` 子句指定，并引用当前用户行：

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



## 并集

查询构建器还提供了一个方便的方法，用于将两个或多个查询“合并”为并集。例如，你可以先创建一个初始查询，然后使用 `union` 方法将其与其他查询合并：

```php
use Illuminate\Support\Facades\DB;

$first = DB::table('users')
    ->whereNull('first_name');

$users = DB::table('users')
    ->whereNull('last_name')
    ->union($first)
    ->get();
```

除了 `union` 方法之外，查询构建器还提供了 `unionAll` 方法。使用 `unionAll` 方法合并的查询不会去重重复结果。`unionAll` 方法的参数和 `union` 方法相同。

## 基本的 Where 条件（Basic Where Clauses）

### Where 条件

你可以使用查询构建器的 `where` 方法向查询添加 “where” 条件。最基本的 `where` 方法调用需要三个参数：第一个参数是列名，第二个参数是操作符（可以是数据库支持的任意操作符），第三个参数是要与列的值进行比较的值。

例如，下面的查询会检索 `votes` 列的值等于 `100` 且 `age` 列的值大于 `35` 的用户：

```php
$users = DB::table('users')
    ->where('votes', '=', 100)
    ->where('age', '>', 35)
    ->get();
```

为了方便，如果你只是想验证某列是否等于给定值，你可以将该值作为 `where` 方法的第二个参数传入。Laravel 会默认使用 `=` 操作符：

```php
$users = DB::table('users')->where('votes', 100)->get();
```



如前所述，你可以使用数据库系统支持的任何操作符：

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

你也可以将一个条件数组传递给 `where` 函数。数组的每个元素应该是一个包含通常传递给 `where` 方法的三个参数的数组：

```php
$users = DB::table('users')->where([
    ['status', '=', '1'],
    ['subscribed', '<>', '1'],
])->get();
```

> [!警告]
> PDO 不支持绑定列名。因此，你万万不可允许用户输入来决定查询中引用的列名，包括「order by」列。

> [!警告]
> MySQL和MariaDB在进行字符串与数字比较时会自动将字符串强制转换为整数。在此过程中，非数字字符串会被转换为0，这可能导致预期之外的结果。例如，若表中 `secret` 列存有值 `aaa`，当执行`User::where('secret', 0)` 时，该行记录仍会被返回。为避免此问题，请确保所有值在用于查询前都已转换为适当的数据类型。

<a name="or-where-clauses"></a>
### Or Where 子句

当在查询构建器的 `where` 方法之间进行链式调用时，「where」子句将使用 and 操作符连接在一起。然而，你可以使用 `orWhere` 方法使用 `or` 操作符将子句连接到查询中。`orWhere` 方法接受与 `where` 方法相同的参数：

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhere('name', 'John')
    ->get();
```



如果你需要在括号内分组一个 「or」条件，可以将一个闭包作为 `orWhere` 方法的第一个参数传递：

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

上述示例将生成以下 SQL：

```sql
select * from users where votes > 100 or (name = 'Abigail' and votes > 50)
```

> [!警告]
> 你应始终对 `orWhere` 调用进行分组，以避免在应用全局作用域时出现意外行为。

<a name="where-not-clauses"></a>
### Where Not 子句

`whereNot` 和 `orWhereNot` 方法可用于否定一组给定的查询约束条件。例如，以下查询排除正在清仓的产品或价格低于 10 的产品：

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

有时你可能需要对多列采用相同的查询约束。例如，你可能想要检索给定列表中任何列与给定值 `LIKE` 匹配的所有记录。你可以使用 `whereAny` 方法来实现这一点：

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

上面的查询将生成以下 SQL：

```sql
SELECT *
FROM users
WHERE active = true AND (
    name LIKE 'Example%' OR
    email LIKE 'Example%' OR
    phone LIKE 'Example%'
)
```



同样地，`whereAll` 方法可用于检索满足给定约束的所有列都匹配的记录：

```php
$posts = DB::table('posts')
    ->where('published', true)
    ->whereAll([
        'title',
        'content',
    ], 'like', '%Laravel%')
    ->get();
```

上面的查询会生成如下 SQL：

```sql
SELECT *
FROM posts
WHERE published = true AND (
    title LIKE '%Laravel%' AND
    content LIKE '%Laravel%'
)
```

`whereNone` 方法可用于检索给定列中**没有任何列**匹配指定约束的记录：

```php
$posts = DB::table('albums')
    ->where('published', true)
    ->whereNone([
        'title',
        'lyrics',
        'tags',
    ], 'like', '%explicit%')
    ->get();
```

上面的查询会生成如下 SQL：

```sql
SELECT *
FROM albums
WHERE published = true AND NOT (
    title LIKE '%explicit%' OR
    lyrics LIKE '%explicit%' OR
    tags LIKE '%explicit%'
)
```

### JSON 类型的 Where 条件

Laravel 也支持对 JSON 类型的列进行查询，前提是数据库支持 JSON 列类型。目前支持的数据库包括 MariaDB 10.3+、MySQL 8.0+、PostgreSQL 12.0+、SQL Server 2017+ 和 SQLite 3.39.0+。要查询 JSON 列，可以使用 `->` 操作符：

```php
$users = DB::table('users')
    ->where('preferences->dining->meal', 'salad')
    ->get();
```

你可以使用 `whereJsonContains` 方法查询 JSON 数组：

```php
$users = DB::table('users')
    ->whereJsonContains('options->languages', 'en')
    ->get();
```

如果你的应用使用 MariaDB、MySQL 或 PostgreSQL 数据库，你可以向 `whereJsonContains` 方法传递一个值数组：

```php
$users = DB::table('users')
    ->whereJsonContains('options->languages', ['en', 'de'])
    ->get();
```

你还可以使用 `whereJsonLength` 方法根据 JSON 数组的长度进行查询：

```php
$users = DB::table('users')
    ->whereJsonLength('options->languages', 0)
    ->get();

$users = DB::table('users')
    ->whereJsonLength('options->languages', '>', 1)
    ->get();
```



<a name="additional-where-clauses"></a>
### 附加 Where 子句

**whereLike / orWhereLike / whereNotLike / orWhereNotLike**

`whereLike` 方法允许你在查询中添加 「LIKE」 子句以进行模式匹配。这些方法提供了一种与数据库无关的字符串匹配查询方式，并支持切换大小写敏感选项。默认情况下，字符串匹配是大小写不敏感的：

```php
$users = DB::table('users')
    ->whereLike('name', '%John%')
    ->get();
```

您可以通过 `caseSensitive` 参数启用区分大小写的搜索：

```php
$users = DB::table('users')
    ->whereLike('name', '%John%', caseSensitive: true)
    ->get();
```

`orWhereLike` 方法允许您添加带有 LIKE 条件的 「or」 子句：

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhereLike('name', '%John%')
    ->get();
```

`whereNotLike` 方法允许您向查询中添加 「NOT LIKE」 子句。

```php
$users = DB::table('users')
    ->whereNotLike('name', '%John%')
    ->get();
```

同样地，你可以使用 `orWhereNotLike` 来添加一个带有 NOT LIKE 条件的 「or」 子句。

```php
$users = DB::table('users')
    ->where('votes', '>', 100)
    ->orWhereNotLike('name', '%John%')
    ->get();
```

> [!警告  ]
> `whereLike` 区分大小写的搜索选项目前在 SQL Server 上不受支持。

**whereIn / whereNotIn / orWhereIn / orWhereNotIn**

`whereIn` 方法验证给定列的值是否包含在给定的数组中：

```php
$users = DB::table('users')
    ->whereIn('id', [1, 2, 3])
    ->get();
```

`whereNotIn` 方法验证给定列的值是否不包含在给定的数组中：

```php
$users = DB::table('users')
    ->whereNotIn('id', [1, 2, 3])
    ->get();
```

你也可以将一个查询对象作为 `whereIn1 方法的第二个参数：

```php
$activeUsers = DB::table('users')->select('id')->where('is_active', 1);

$users = DB::table('comments')
    ->whereIn('user_id', $activeUsers)
    ->get();
```



上述示例将生成以下 SQL：

```sql
select * from comments where user_id in (
    select id
    from users
    where is_active = 1
)
```

> [!警告 ]
> 如果你向查询中添加大量整数绑定，可以使用 `whereIntegerInRaw` 或 `whereIntegerNotInRaw` 方法来大大减少内存使用。

**whereBetween / orWhereBetween**

`whereBetween` 方法验证一个列的值是否在两个值之间：

```php
$users = DB::table('users')
    ->whereBetween('votes', [1, 100])
    ->get();
```

**whereNotBetween / orWhereNotBetween**

`whereNotBetween` 方法验证一个列的值是否在两个值之外：

```php
$users = DB::table('users')
    ->whereNotBetween('votes', [1, 100])
    ->get();
```

**whereBetweenColumns / whereNotBetweenColumns / orWhereBetweenColumns / orWhereNotBetweenColumns**

`whereBetweenColumns` 方法验证一个列的值是否在同一表行中两个列的两个值之间：

```php
$patients = DB::table('patients')
    ->whereBetweenColumns('weight', ['minimum_allowed_weight', 'maximum_allowed_weight'])
    ->get();
```

`whereNotBetweenColumns` 方法验证一个列的值是否在同一表行中两个列的两个值之外：

```php
$patients = DB::table('patients')
    ->whereNotBetweenColumns('weight', ['minimum_allowed_weight', 'maximum_allowed_weight'])
    ->get();
```

**whereNull / whereNotNull / orWhereNull / orWhereNotNull**

`whereNull` 方法验证给定列的值是否为 `NULL`：

```php
$users = DB::table('users')
    ->whereNull('updated_at')
    ->get();
```

`whereNotNull` 方法验证列的值是否不为 `NULL`：

```php
$users = DB::table('users')
    ->whereNotNull('updated_at')
    ->get();
```

**whereDate / whereMonth / whereDay / whereYear / whereTime**

`whereDate` 方法可用于将列的值与日期进行比较：

```php
$users = DB::table('users')
    ->whereDate('created_at', '2016-12-31')
    ->get();
```



`whereMonth` 方法可用于将列的值与特定月份进行比较：

```php
$users = DB::table('users')
    ->whereMonth('created_at', '12')
    ->get();
```

`whereDay` 方法可用于将列的值与月份的某一天进行比较：

```php
$users = DB::table('users')
    ->whereDay('created_at', '31')
    ->get();
```

`whereYear `方法可用于将列的值与特定年份进行比较：

```php
$users = DB::table('users')
    ->whereYear('created_at', '2016')
    ->get();
```

`whereTime` 方法可用于将列的值与特定时间进行比较：

```php
$users = DB::table('users')
    ->whereTime('created_at', '=', '11:20:45')
    ->get();
```

**wherePast / whereFuture / whereToday / whereBeforeToday / whereAfterToday**

`wherePast` 和 `whereFuture` 方法可用于判断某列的值是否属于过去或未来：

```php
$invoices = DB::table('invoices')
    ->wherePast('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereFuture('due_at')
    ->get();
```

`whereNowOrPast` 和 `whereNowOrFuture` 方法可用于判断某列的值是否属于过去或将来（包含当前日期和时间）：

```php
$invoices = DB::table('invoices')
    ->whereNowOrPast('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereNowOrFuture('due_at')
    ->get();
```

`whereToday`、`whereBeforeToday` 和 `whereAfterToday `方法可用于分别判断某列的值是否为今天、早于今天或晚于今天：

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



类似地，`whereTodayOrBefore` 和 `whereTodayOrAfter` 方法可用于判断列的值是否为今天之前或今天之后（包含今天的日期）：

```php
$invoices = DB::table('invoices')
    ->whereTodayOrBefore('due_at')
    ->get();

$invoices = DB::table('invoices')
    ->whereTodayOrAfter('due_at')
    ->get();
```

**whereColumn / orWhereColumn**

`whereColumn` 方法可用于验证两列是否相等：

```php
$users = DB::table('users')
    ->whereColumn('first_name', 'last_name')
    ->get();
```

你也可以向 `whereColumn` 方法传递一个比较运算符：

```php
$users = DB::table('users')
    ->whereColumn('updated_at', '>', 'created_at')
    ->get();
```

你也可以向 `whereColumn` 方法传递一个列比较数组。这些条件将使用 `and` 运算符进行连接：


```php
$users = DB::table('users')
    ->whereColumn([
        ['first_name', '=', 'last_name'],
        ['updated_at', '>', 'created_at'],
    ])->get();
```

<a name="logical-grouping"></a>
### 逻辑分组

有时，您可能需要将多个 「where」 子句用括号分组，以实现查询所需的逻辑分组。实际上，通常应该始终将 `orWhere` 方法的调用放在括号内，以避免意外的查询行为。为此，您可以向 `where` 方法传递一个闭包：

```php
$users = DB::table('users')
    ->where('name', '=', 'John')
    ->where(function (Builder $query) {
        $query->where('votes', '>', 100)
            ->orWhere('title', '=', 'Admin');
    })
    ->get();
```

如您所见，向 `where` 方法传递一个闭包会指示查询构建器开始一个约束组。该闭包将接收一个查询构建器实例，您可以用它来设置在括号分组内应包含的约束条件。上面的示例将生成如下 SQL 语句：

```sql
select * from users where name = 'John' and (votes > 100 or title = 'Admin')
```

> [!警告]
> 应当始终将 `orWhere` 调用进行分组，以避免应用全局作用域时出现意外行为。



<a name="advanced-where-clauses"></a>
## 高级 Where 子句

<a name="where-exists-clauses"></a>
### Where Exists 子句

`whereExists` 方法允许你编写「where exists」 SQL 子句。`whereExists` 方法接受一个闭包，该闭包将接收到一个查询构建器实例，允许你定义应放置在「exists」子句内部的查询：

```php
$users = DB::table('users')
    ->whereExists(function (Builder $query) {
        $query->select(DB::raw(1))
            ->from('orders')
            ->whereColumn('orders.user_id', 'users.id');
    })
    ->get();
```

或者，你可以将一个查询对象提供给 `whereExists` 方法，而不是闭包：

```php
$orders = DB::table('orders')
    ->select(DB::raw(1))
    ->whereColumn('orders.user_id', 'users.id');

$users = DB::table('users')
    ->whereExists($orders)
    ->get();
```

上述两个示例都将生成以下 SQL：

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

有时你可能需要构建一个「where」子句，将子查询的结果与给定值进行比较。你可以通过向 `where` 方法传递一个闭包和一个值来实现这一点。例如，以下查询将检索拥有最近给定类型「membership」的所有用户；

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

或者，你可能需要构建一个「where」子句，将一列与子查询的结果进行比较。你可以通过向 `where` 方法传递一个列、操作符和闭包来实现这一点。例如，以下查询将检索所有金额小于平均值的收入记录；

```php
use App\Models\Income;
use Illuminate\Database\Query\Builder;

$incomes = Income::where('amount', '<', function (Builder $query) {
    $query->selectRaw('avg(i.amount)')->from('incomes as i');
})->get();
```



<a name="full-text-where-clauses"></a>
### 全文 Where 子句

> [!警告]
> 全文 where 子句目前由 MariaDB，MySQL 和 PostgreSQL 支持。

`whereFullText` 和 `orWhereFullText` 方法可用于为具有[全文索引](https://learnku.com/docs/laravel/12.x/migrations#available-index-types "全文索引")的列添加全文「where」子句。这些方法将由 Laravel 转换成适合的 SQL 给底层数据库系统。例如，对于使用 MySQL 的应用程序，将生成一个 MATCH AGAINST 子句：

```php
$users = DB::table('users')
    ->whereFullText('bio', 'web developer')
    ->get();
```

<a name="ordering-grouping-limit-and-offset"></a>
## 排序、分组、条数限制和偏移量

<a name="ordering"></a>
### 排序

<a name="orderby"></a>
####  `orderBy` 方法

`orderBy` 方法允许你按给定列对查询结果进行排序。`orderBy` 方法接受的第一个参数应该是你要排序的列，而第二个参数确定排序方向，可以是 `asc` 或 `desc`：

```php
$users = DB::table('users')
    ->orderBy('name', 'desc')
    ->get();
```

要按多个列排序，你可以简单地按需多次调用 `orderBy`：

```php
$users = DB::table('users')
    ->orderBy('name', 'desc')
    ->orderBy('email', 'asc')
    ->get();
```

<a name="latest-oldest"></a>
#### latest 和 oldest 方法#

`latest` 和 `oldest` 方法允许你按日期轻松排序结果。默认情况下，结果将按表的 `created_at` 列排序。或者，你可以传递要排序的列名：

```php
$user = DB::table('users')
    ->latest()
    ->first();
```



<a name="random-ordering"></a>
#### 随机排序

`inRandomOrder` 方法可用于随机排序查询结果。例如，你可以使用此方法获取一个随机用户：

```php
$randomUser = DB::table('users')
    ->inRandomOrder()
    ->first();
```

<a name="removing-existing-orderings"></a>
#### 移除现有排序#

`reorder` 方法移除已应用于查询的所有「order by」子句

```php
$query = DB::table('users')->orderBy('name');

$unorderedUsers = $query->reorder()->get();
```

你可以在调用 `reorder` 方法时传递列和方向，以便移除所有现有的「order by」子句，并为查询应用一个全新的排序：

```php
$query = DB::table('users')->orderBy('name');

$usersOrderedByEmail = $query->reorder('email', 'desc')->get();
```

<a name="grouping"></a>
### 分组

<a name="groupby-having"></a>
#### `groupBy` 和 `having` 方法

如你所料，`groupBy` 和 `having` 方法可用于对查询结果进行分组。`having` 方法的签名类似于 `where` 方法：

```php
$users = DB::table('users')
    ->groupBy('account_id')
    ->having('account_id', '>', 100)
    ->get();
```

你可以使用 `havingBetween` 方法在给定范围内过滤结果：

```php
$report = DB::table('orders')
    ->selectRaw('count(id) as number_of_orders, customer_id')
    ->groupBy('customer_id')
    ->havingBetween('number_of_orders', [5, 15])
    ->get();
```

你可以向 `groupBy` 方法传递多个参数，以按多个列进行分组：

```php
$users = DB::table('users')
    ->groupBy('first_name', 'status')
    ->having('account_id', '>', 100)
    ->get();
```



要构建更复杂的 `having` 语句，请参考 [havingRaw](https://learnku.com/docs/laravel/12.x/#raw-methods "havingRaw") 方法。

<a name="limit-and-offset"></a>
### 条数限制和偏移量

<a name="skip-take"></a>
#### The `skip` 和 `take` 方法

你可以使用 `skip` 和 `take` 方法来限制从查询返回的结果数量，或者在查询中跳过给定数量的结果：

```php
$users = DB::table('users')->skip(10)->take(5)->get();
```

你可以使用 `limit` 和 `offset` 方法作为替代方案。这两个方法在功能上分别等同于 `take` 和 `skip` 方法：
```php
$users = DB::table('users')
    ->offset(10)
    ->limit(5)
    ->get();
```

<a name="conditional-clauses"></a>
## 前提子句

有时你可能希望根据另一个条件将某些查询子句应用于查询。例如，如果给定的输入值存在于传入的 HTTP 请求中，你可能只想应用一个 `where` 语句。你可以使用 `when`	 方法来实现这一点：

```php
$role = $request->input('role');

$users = DB::table('users')
    ->when($role, function (Builder $query, string $role) {
        $query->where('role_id', $role);
    })
    ->get();
```

`when` 方法仅在第一个参数为 `true` 时执行给定的闭包。如果第一个参数为 `false`，闭包将不会执行。因此，在上面的示例中，传递给 `when` 方法的闭包仅在 `role` 字段存在于传入请求中且评估为 `true` 时才会被调用。

你可以将另一个闭包作为 `when` 方法的第三个参数传递。这个闭包仅在第一个参数评估为 `false` 时才会执行。为了说明如何使用此功能，我们将使用它来配置查询的默认排序：

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

查询构建器还提供了一个 `insert` 方法，可用于将记录插入数据库表中。`insert` 方法接受一个列名和值的数组：

```php
DB::table('users')->insert([
    'email' => 'kayla@example.com',
    'votes' => 0
]);
```

你可以通过传入一个二维数组一次性插入多条记录，其中每个子数组代表要插入到表中的一条记录:

```php
DB::table('users')->insert([
    ['email' => 'picard@example.com', 'votes' => 0],
    ['email' => 'janeway@example.com', 'votes' => 0],
]);
```
`insertOrIgnore` 方法将在插入记录到数据库时忽略错误。使用此方法时，你应该注意，重复记录错误将被忽略，其他类型的错误也可能根据数据库引擎被忽略。例如，`insertOrIgnore` 将绕过 [MySQL 的严格模式](https://dev.mysql.com/doc/refman/en/sql-mode.html#ignore-effect-on-execution "MySQL 的严格模式")：

```php
DB::table('users')->insertOrIgnore([
    ['id' => 1, 'email' => 'sisko@example.com'],
    ['id' => 2, 'email' => 'archer@example.com'],
]);
```

当使用子查询确定应插入的数据时候，`insertUsing` 方法会将新记录插入进表中：

```php
DB::table('pruned_users')->insertUsing([
    'id', 'name', 'email', 'email_verified_at'
], DB::table('users')->select(
    'id', 'name', 'email', 'email_verified_at'
)->where('updated_at', '<=', now()->subMonth()));
```

<a name="auto-incrementing-ids"></a>
#### 自增 ID

如果表有一个自增 ID，使用 `insertGetId` 方法插入记录并检索 ID：

```php
$id = DB::table('users')->insertGetId(
    ['email' => 'john@example.com', 'votes' => 0]
);
```

> [!警告]
> 当使用 PostgreSQL 时，`insertGetId` 方法期望自增列名为 `id`。如果你想从不同的「序列」中检索 ID，可以将列名作为 `insertGetId` 方法的第二个参数传递。



<a name="upserts"></a>
### 更新插入#

`upsert` 方法将插入不存在的记录，并更新已存在的记录为指定的新值。方法的第一个参数包含要插入或更新的值，而第二个参数列出关联表中唯一标识记录的列。方法的第三个也是最后一个参数是一个列数组，如果数据库中已存在匹配记录，则应更新这些列：


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

在上面的示例中，Laravel 将尝试插入两条记录。如果记录已存在相同的 `departure` 和 `destination` 列值，Laravel 将更新该记录的 `price` 列。

> [!警告]
> 除 SQL Server 外的所有数据库都要求 `upsert` 方法的第二个参数中的列具有「主键」或「唯一」索引。此外，MariaDB  和 MySQL 数据库驱动程序忽略 `upsert` 方法的第二个参数，并始终使用表的「主键」或「唯一」索引来检测现有记录。

<a name="update-statements"></a>
## 更新语句#

除了向数据库插入记录外，查询构建器还可以使用 `update` 方法更新现有记录。`update` 方法与 `insert` 方法类似，接受一个列和值对的数组，指示要更新的列。`update` 方法返回受影响的行数。你可以使用 `where` 子句约束 `update` 查询：

```php
$affected = DB::table('users')
    ->where('id', 1)
    ->update(['votes' => 1]);
```



<a name="update-or-insert"></a>
#### 更新或者插入

有时你可能希望更新数据库中的现有记录，或者如果不存在匹配记录则创建它。在这种情况下，可以使用 `updateOrInsert` 方法。`updateOrInsert` 方法接受两个参数：一个用于查找记录的条件数组，以及一个指示要更新的列的列和值对数组。

`updateOrInsert` 方法将尝试使用第一个参数的列和值对查找匹配的数据库记录。如果记录存在，将使用第二个参数中的值进行更新。如果记录找不到，将插入一个新记录，其属性为两个参数的合并：

```php
DB::table('users')
    ->updateOrInsert(
        ['email' => 'john@example.com', 'name' => 'John'],
        ['votes' => '2']
    );
```

你可以向 `updateOrInsert` 方法提供一个闭包，以根据匹配记录的存在自定义更新或插入到数据库中的属性：

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
### 更新 JSON 字段

当更新一个 JSON 列的时候，你可以使用 `->` 语法来更新 JSON 对象中恰当的键。此操作 MariaDB 10.3+  MySQL 5.7+ 和 PostgreSQL 9.5+ 的数据库：
```php
$affected = DB::table('users')
    ->where('id', 1)
    ->update(['options->enabled' => true]);
```

<a name="increment-and-decrement"></a>
### 自增与自减

查询构造器还提供了方便的方法来增加或减少给定列的值。这两种方法都至少接受一个参数：要修改的列。可以提供第二个参数来指定列应该增加或减少的数量：

```php
DB::table('users')->increment('votes');

DB::table('users')->increment('votes', 5);

DB::table('users')->decrement('votes');

DB::table('users')->decrement('votes', 5);
```



你还可以在操作期间指定要更新的其他列：

```php
DB::table('users')->increment('votes', 1, ['name' => 'John']);
```

此外，你可以使用 `incrementEach` 和 `decrementEach` 方法同时增加或减少多个列:

```php
DB::table('users')->incrementEach([
    'votes' => 5,
    'balance' => 100,
]);
```

<a name="delete-statements"></a>
## 删除语句

查询构造器的 `delete`方法可以用于从表中删除记录.  `delete`  方法返回受影响行数。你可以通过在调用 `delete` 方法之前添加 「where」 子句来限制 delete 语句：

```php
$deleted = DB::table('users')->delete();

$deleted = DB::table('users')->where('votes', '>', 100)->delete();
```

<a name="pessimistic-locking"></a>
## 悲观锁

查询构建器还包括一些函数，可帮助你在执行 `select` 语句时实现「悲观锁」。 要使用「共享锁」执行语句，你可以调用 「sharedLock」 方法。共享锁可防止选定的行被修改，直到你的事务被提交：

```php
DB::table('users')
    ->where('votes', '>', 100)
    ->sharedLock()
    ->get();
```

或者，你可以使用 `lockForUpdate` 方法。「update」锁可防止所选记录被修改或被另一个共享锁选中：

```php
DB::table('users')
    ->where('votes', '>', 100)
    ->lockForUpdate()
    ->get();
```


虽然这不是强制要求，但建议将悲观锁包裹在 [事务](https://learnku.com/docs/laravel/12.x/database#database-transactions "事务") 中使用。这样可以确保在操作完成前，数据库中被检索的数据不会被修改。如果操作失败，事务将自动回滚所有变更并释放锁：

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



## 可复用的查询组件

如果你的应用中有重复的查询逻辑，可以使用查询构建器的 `tap` 和 `pipe` 方法，将这些逻辑提取到可复用的对象中。假设你的应用中有以下两个不同的查询：

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

你可以将查询中公共的目的地筛选逻辑提取到一个可复用的对象中：

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

然后，你可以使用查询构建器的 `tap` 方法将该对象的逻辑应用到查询中：

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



#### 查询管道（Query Pipes）

`tap` 方法总是会返回查询构建器实例。如果你希望提取一个对象来执行查询并返回其他值，可以使用 `pipe` 方法。

假设你有一个查询对象，其中包含在整个应用中共享的分页逻辑。与 `DestinationFilter` 不同，`Paginate` 对象执行查询并返回分页器实例，而不是仅仅修改查询条件：

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
        private string $perPage = 25,
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

使用查询构建器的 `pipe` 方法，可以利用该对象应用共享的分页逻辑：

```php
$flights = DB::table('flights')
    ->tap(new DestinationFilter($destination))
    ->pipe(new Paginate);
```

## 调试

在构建查询时，你可以使用 `dd` 和 `dump` 方法来输出当前查询绑定和 SQL。`dd` 方法会显示调试信息并停止请求执行，而 `dump` 方法会显示信息但允许请求继续执行：

```php
DB::table('users')->where('votes', '>', 100)->dd();

DB::table('users')->where('votes', '>', 100)->dump();
```

你也可以使用 `dumpRawSql` 和 `ddRawSql` 方法来输出查询的完整 SQL（包括所有参数绑定替换后的 SQL）：

```php
DB::table('users')->where('votes', '>', 100)->dumpRawSql();

DB::table('users')->where('votes', '>', 100)->ddRawSql();
```
