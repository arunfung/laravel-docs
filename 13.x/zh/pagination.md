# 数据库：分页

- [简介](#introduction)
- [基本用法](#basic-usage)
    - [对查询构建器结果分页](#paginating-query-builder-results)
    - [对 Eloquent 结果分页](#paginating-eloquent-results)
    - [游标分页](#cursor-pagination)
    - [手动创建分页器](#manually-creating-a-paginator)
    - [自定义分页 URL](#customizing-pagination-urls)
- [显示分页结果](#displaying-pagination-results)
    - [调整分页链接窗口](#adjusting-the-pagination-link-window)
    - [将结果转换为 JSON](#converting-results-to-json)
- [自定义分页视图](#customizing-the-pagination-view)
    - [使用 Bootstrap](#using-bootstrap)
- [Paginator 和 LengthAwarePaginator 实例方法](#paginator-instance-methods)
- [游标分页器实例方法](#cursor-paginator-instance-methods)

<a name="introduction"></a>
## 简介

在其他框架中，实现分页可能十分繁琐。我们希望 Laravel 的分页方式能让你耳目一新。Laravel 的分页器与[查询构建器](/docs/{{version}}/queries)和 [Eloquent ORM](/docs/{{version}}/eloquent) 集成，无需配置即可方便地对数据库记录分页。

默认情况下，分页器生成的 HTML 兼容 [Tailwind CSS 框架](https://tailwindcss.com/)，同时也提供了 Bootstrap 分页支持。

<a name="tailwind"></a>
#### Tailwind

如果你使用 Tailwind 4.x 和 Laravel 默认的 Tailwind 分页视图，应用的 `resources/css/app.css` 文件已配置好通过 `@source` 引入 Laravel 的分页视图：

```css
@import 'tailwindcss';

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
```

<a name="basic-usage"></a>
## 基本用法

<a name="paginating-query-builder-results"></a>
### 对查询构建器结果分页

对数据项分页有多种方式。最简单的是在[查询构建器](/docs/{{version}}/queries)或 [Eloquent 查询](/docs/{{version}}/eloquent)上使用 `paginate` 方法。该方法会根据用户当前查看的页面，自动设置查询的「limit」和「offset」。默认情况下，Laravel 会自动从 HTTP 请求的 `page` 查询字符串参数获取当前页码，并将其自动添加到分页器生成的链接中。

下面的示例只向 `paginate` 方法传入一个参数，指定「每页」显示的数据项数量。这里设为每页显示 `15` 项：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * 显示应用中的所有用户。
     */
    public function index(): View
    {
        return view('user.index', [
            'users' => DB::table('users')->paginate(15)
        ]);
    }
}
```

<a name="simple-pagination"></a>
#### 简单分页

`paginate` 方法会先统计符合查询条件的记录总数，再从数据库获取记录，以便分页器计算总页数。如果应用界面不需要显示总页数，就无需执行这条计数查询。

因此，如果应用界面只需要简单的「下一页」和「上一页」链接，可以使用 `simplePaginate` 方法，只执行一次高效的查询：

```php
$users = DB::table('users')->simplePaginate(15);
```

<a name="paginating-eloquent-results"></a>
### 对 Eloquent 结果分页

你也可以对 [Eloquent](/docs/{{version}}/eloquent) 查询分页。下面的示例会对 `App\Models\User` 模型分页，每页显示 15 条记录。可以看到，其语法与对查询构建器结果分页几乎完全相同：

```php
use App\Models\User;

$users = User::paginate(15);
```

你也可以先为查询设置 `where` 子句等其他约束，再调用 `paginate` 方法：

```php
$users = User::where('votes', '>', 100)->paginate(15);
```

对 Eloquent 模型分页时，也可以使用 `simplePaginate` 方法：

```php
$users = User::where('votes', '>', 100)->simplePaginate(15);
```

同样，你可以使用 `cursorPaginate` 方法对 Eloquent 模型进行游标分页：

```php
$users = User::where('votes', '>', 100)->cursorPaginate(15);
```

<a name="multiple-paginator-instances-per-page"></a>
#### 同一页面中的多个分页器实例

有时，你可能需要在同一个页面中显示两个独立的分页器。如果两个分页器都用 `page` 查询字符串参数存储当前页码，就会产生冲突。要解决此问题，可以通过 `paginate`、`simplePaginate` 或 `cursorPaginate` 方法的第三个参数，指定该分页器用于存储当前页码的查询字符串参数名：

```php
use App\Models\User;

$users = User::where('votes', '>', 100)->paginate(
    $perPage = 15, $columns = ['*'], $pageName = 'users'
);
```

<a name="cursor-pagination"></a>
### 游标分页

`paginate` 和 `simplePaginate` 使用 SQL 的「offset」子句构建查询，而游标分页通过「where」子句比较查询中排序列的值，在 Laravel 的各种分页方式中提供最高的数据库查询效率。这种分页方式尤其适合大型数据集和「无限滚动」界面。

偏移量分页会在生成的 URL 查询字符串中包含页码；游标分页则放入一个「cursor」字符串。游标是经过编码的字符串，包含下一次分页查询的起始位置和分页方向：

```text
http://localhost/users?cursor=eyJpZCI6MTUsIl9wb2ludHNUb05leHRJdGVtcyI6dHJ1ZX0
```

你可以通过查询构建器的 `cursorPaginate` 方法创建游标分页器。该方法返回一个 `Illuminate\Pagination\CursorPaginator` 实例：

```php
$users = DB::table('users')->orderBy('id')->cursorPaginate(15);
```

获取游标分页器实例后，就可以像使用 `paginate` 和 `simplePaginate` 时一样[显示分页结果](#displaying-pagination-results)。关于游标分页器提供的方法，请参阅[游标分页器实例方法文档](#cursor-paginator-instance-methods)。

> [!WARNING]
> 使用游标分页时，查询必须包含「order by」子句，且排序列必须属于正在分页的表。

<a name="cursor-vs-offset-pagination"></a>
#### 游标分页与偏移量分页

下面通过 SQL 查询示例说明两种分页方式的区别。以下两个查询都会返回 `users` 表按 `id` 排序后的「第二页」结果：

```sql
# 偏移量分页……
select * from users order by id asc limit 15 offset 15;

# 游标分页……
select * from users where id > 15 order by id asc limit 15;
```

与偏移量分页相比，游标分页查询具有以下优势：

- 对于大型数据集，如果「order by」列有索引，游标分页的性能会更好。这是因为「offset」子句需要扫描此前所有匹配的数据。
- 对于频繁写入的数据集，如果用户当前查看的页面最近有记录被添加或删除，偏移量分页可能会跳过记录或显示重复记录。

不过，游标分页也有以下限制：

- 与 `simplePaginate` 一样，游标分页只能显示「下一页」和「上一页」链接，不支持生成带页码的链接。
- 排序必须基于至少一个唯一列，或一组组合值唯一的列。不支持包含 `null` 值的列。
- 「order by」子句中的查询表达式必须设置别名，并同时添加到「select」子句中，才受支持。
- 不支持带参数的查询表达式。

<a name="manually-creating-a-paginator"></a>
### 手动创建分页器

有时，你可能希望手动创建分页器实例，将内存中已有的数据项数组传给它。你可以根据需要创建 `Illuminate\Pagination\Paginator`、`Illuminate\Pagination\LengthAwarePaginator` 或 `Illuminate\Pagination\CursorPaginator` 实例。

`Paginator` 和 `CursorPaginator` 无需知道结果集的数据项总数，因此也没有获取最后一页页码的方法。`LengthAwarePaginator` 接受的参数与 `Paginator` 基本相同，但需要提供结果集的数据项总数。

换言之，`Paginator` 对应查询构建器的 `simplePaginate` 方法，`CursorPaginator` 对应 `cursorPaginate` 方法，而 `LengthAwarePaginator` 对应 `paginate` 方法。

> [!WARNING]
> 手动创建分页器实例时，应自行对传入的结果数组进行「切片」。如果不清楚如何操作，请参阅 PHP 的 [array_slice](https://secure.php.net/manual/en/function.array-slice.php) 函数。

<a name="customizing-pagination-urls"></a>
### 自定义分页 URL

默认情况下，分页器会使用当前请求的 URI 生成链接。你可以通过 `withPath` 方法自定义该 URI。例如，要生成 `http://example.com/admin/users?page=N` 这样的链接，应向 `withPath` 传入 `/admin/users`：

```php
use App\Models\User;

Route::get('/users', function () {
    $users = User::paginate(15);

    $users->withPath('/admin/users');

    // ...
});
```

<a name="appending-query-string-values"></a>
#### 追加查询字符串参数

你可以使用 `appends` 方法为分页链接追加查询字符串参数。例如，要为每个分页链接追加 `sort=votes`，可以这样调用：

```php
use App\Models\User;

Route::get('/users', function () {
    $users = User::paginate(15);

    $users->appends(['sort' => 'votes']);

    // ...
});
```

如果希望将当前请求的所有查询字符串参数追加到分页链接，可以使用 `withQueryString` 方法：

```php
$users = User::paginate(15)->withQueryString();
```

<a name="appending-hash-fragments"></a>
#### 追加哈希片段

如果需要为分页器生成的 URL 追加「哈希片段」，可以使用 `fragment` 方法。例如，要在每个分页链接末尾追加 `#users`，可以这样调用：

```php
$users = User::paginate(15)->fragment('users');
```

<a name="displaying-pagination-results"></a>
## 显示分页结果

调用 `paginate` 方法会得到 `Illuminate\Pagination\LengthAwarePaginator` 实例；调用 `simplePaginate` 会得到 `Illuminate\Pagination\Paginator` 实例；调用 `cursorPaginate` 则会得到 `Illuminate\Pagination\CursorPaginator` 实例。

这些对象提供了多种获取结果集信息的方法。此外，分页器实例也是迭代器，可以像数组一样遍历。因此，获取结果后，就可以使用 [Blade](/docs/{{version}}/blade) 显示结果并渲染分页链接：

```blade
<div class="container">
    @foreach ($users as $user)
        {{ $user->name }}
    @endforeach
</div>

{{ $users->links() }}
```

`links` 方法会渲染指向结果集中其他页面的链接，每个链接都已包含正确的 `page` 查询字符串参数。请记住，该方法生成的 HTML 兼容 [Tailwind CSS 框架](https://tailwindcss.com)。

<a name="adjusting-the-pagination-link-window"></a>
### 调整分页链接窗口

分页器显示分页链接时，会显示当前页码，以及当前页前后各三页的链接。使用 `onEachSide` 方法，可以控制分页链接中间的滑动窗口在当前页两侧各显示多少个链接：

```blade
{{ $users->onEachSide(5)->links() }}
```

<a name="converting-results-to-json"></a>
### 将结果转换为 JSON

Laravel 的分页器类实现了 `Illuminate\Contracts\Support\Jsonable` 接口，并提供 `toJson` 方法，因此可以轻松将分页结果转换为 JSON。你也可以直接从路由或控制器方法返回分页器实例，将其转换为 JSON：

```php
use App\Models\User;

Route::get('/users', function () {
    return User::paginate();
});
```

分页器生成的 JSON 包含 `total`、`current_page`、`last_page` 等元信息，结果记录位于 `data` 键下。以下是从路由返回分页器实例时生成的 JSON 示例：

```json
{
   "total": 50,
   "per_page": 15,
   "current_page": 1,
   "last_page": 4,
   "first_page_url": "http://laravel.app?page=1",
   "last_page_url": "http://laravel.app?page=4",
   "next_page_url": "http://laravel.app?page=2",
   "prev_page_url": null,
   "path": "http://laravel.app",
   "from": 1,
   "to": 15,
   "data":[
        {
            // 记录……
        },
        {
            // 记录……
        }
   ]
}
```

<a name="customizing-the-pagination-view"></a>
## 自定义分页视图

默认情况下，用于显示分页链接的视图兼容 [Tailwind CSS](https://tailwindcss.com) 框架。如果不使用 Tailwind，也可以自定义视图来渲染这些链接。调用分页器实例的 `links` 方法时，可以将视图名作为第一个参数传入：

```blade
{{ $paginator->links('view.name') }}

<!-- 向视图传递额外数据…… -->
{{ $paginator->links('view.name', ['foo' => 'bar']) }}
```

自定义分页视图最简单的方式，是使用 `vendor:publish` 命令将视图导出到 `resources/views/vendor` 目录：

```shell
php artisan vendor:publish --tag=laravel-pagination
```

该命令会将视图放入应用的 `resources/views/vendor/pagination` 目录。其中的 `tailwind.blade.php` 对应默认分页视图，编辑该文件即可修改分页的 HTML。

如果希望指定其他文件作为默认分页视图，可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用分页器的 `defaultView` 和 `defaultSimpleView` 方法：

```php
<?php

namespace App\Providers;

use Illuminate\Pagination\Paginator;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 启动应用服务。
     */
    public function boot(): void
    {
        Paginator::defaultView('view-name');

        Paginator::defaultSimpleView('view-name');
    }
}
```

<a name="using-bootstrap"></a>
### 使用 Bootstrap

Laravel 也提供了基于 [Bootstrap CSS](https://getbootstrap.com/) 的分页视图。要使用它们替代默认的 Tailwind 视图，可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用分页器的 `useBootstrapFour` 或 `useBootstrapFive` 方法：

```php
use Illuminate\Pagination\Paginator;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Paginator::useBootstrapFive();
    Paginator::useBootstrapFour();
}
```

<a name="paginator-instance-methods"></a>
## Paginator / LengthAwarePaginator 实例方法

每个分页器实例都可以通过以下方法提供更多分页信息：

<div class="overflow-auto">

| 方法                                  | 说明                                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `$paginator->count()`                   | 获取当前页的数据项数量。                                                                |
| `$paginator->currentPage()`             | 获取当前页码。                                                                                 |
| `$paginator->firstItem()`               | 获取当前页第一项在整个结果集中的序号。                                                      |
| `$paginator->getOptions()`              | 获取分页器的配置选项。                                                                                   |
| `$paginator->getUrlRange($start, $end)` | 生成指定页码范围的分页 URL。                                                                           |
| `$paginator->hasPages()`                | 判断是否有足够的数据项分成多页。                                            |
| `$paginator->hasMorePages()`            | 判断数据存储中是否还有更多数据项。                                                         |
| `$paginator->items()`                   | 获取当前页的数据项。                                                                          |
| `$paginator->lastItem()`                | 获取当前页最后一项在整个结果集中的序号。                                                       |
| `$paginator->lastPage()`                | 获取最后一页的页码。（使用 `simplePaginate` 时不可用。）                 |
| `$paginator->nextPageUrl()`             | 获取下一页的 URL。                                                                               |
| `$paginator->onFirstPage()`             | 判断分页器是否位于第一页。                                                             |
| `$paginator->onLastPage()`              | 判断分页器是否位于最后一页。                                                              |
| `$paginator->perPage()`                 | 每页显示的数据项数量。                                                                    |
| `$paginator->previousPageUrl()`         | 获取上一页的 URL。                                                                           |
| `$paginator->total()`                   | 获取数据存储中符合条件的数据项总数。（使用 `simplePaginate` 时不可用。） |
| `$paginator->url($page)`                | 获取指定页码的 URL。                                                                         |
| `$paginator->getPageName()`             | 获取用于存储页码的查询字符串参数名。                                                        |
| `$paginator->setPageName($name)`        | 设置用于存储页码的查询字符串参数名。                                                        |
| `$paginator->through($callback)`        | 使用回调转换每个数据项。                                                                        |

</div>

<a name="cursor-paginator-instance-methods"></a>
## 游标分页器实例方法

每个游标分页器实例都可以通过以下方法提供更多分页信息：

<div class="overflow-auto">

| 方法                          | 说明                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| `$paginator->count()`           | 获取当前页的数据项数量。                     |
| `$paginator->cursor()`          | 获取当前游标实例。                                  |
| `$paginator->getOptions()`      | 获取分页器的配置选项。                                        |
| `$paginator->hasPages()`        | 判断是否有足够的数据项分成多页。 |
| `$paginator->hasMorePages()`    | 判断数据存储中是否还有更多数据项。              |
| `$paginator->getCursorName()`   | 获取用于存储游标的查询字符串参数名。           |
| `$paginator->items()`           | 获取当前页的数据项。                               |
| `$paginator->nextCursor()`      | 获取下一组数据项的游标实例。                |
| `$paginator->nextPageUrl()`     | 获取下一页的 URL。                                    |
| `$paginator->onFirstPage()`     | 判断分页器是否位于第一页。                  |
| `$paginator->onLastPage()`      | 判断分页器是否位于最后一页。                   |
| `$paginator->perPage()`         | 每页显示的数据项数量。                         |
| `$paginator->previousCursor()`  | 获取上一组数据项的游标实例。            |
| `$paginator->previousPageUrl()` | 获取上一页的 URL。                                |
| `$paginator->setCursorName()`   | 设置用于存储游标的查询字符串参数名。           |
| `$paginator->url($cursor)`      | 获取指定游标实例的 URL。                          |

</div>
