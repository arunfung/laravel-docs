
# 数据库：分页
-   [介绍](#introduction)
-   [基础用法](#basic-usage)
    -   [对查询构建器结果进行分页](#paginating-query-builder-results)
    -   [对 Eloquent 结果进行分页](#paginating-eloquent-results)
    -   [游标分页](#cursor-pagination)
    -   [手动创建分页器](#manually-creating-a-paginator)
    -   [自定义分页 URL](#customizing-pagination-urls)
-   [显示分页结果](#displaying-pagination-results)
    -   [调整分页链接窗口](#adjusting-the-pagination-link-window)
    -   [将结果转换为 JSON](#converting-results-to-json)
-   [自定义分页视图](#customizing-the-pagination-view)
    -   [使用 Bootstrap](#using-bootstrap)
-   [Paginator 与 LengthAwarePaginator 实例方法](#paginator-instance-methods)
-   [Cursor Paginator 实例方法](#cursor-paginator-instance-methods)

## 介绍

## 介绍

在其他框架中，分页可能会非常痛苦。我们希望 Laravel 的分页方法能让人耳目一新。Laravel 的分页器与 [查询构建器](/docs/laravel/12.x/queries) 和 [Eloquent ORM](/docs/laravel/12.x/eloquent) 集成，并提供了便捷、易用的数据库记录分页功能，且无需任何配置。

默认情况下，分页器生成的 HTML 与 [Tailwind CSS 框架](https://tailwindcss.com/) 兼容；然而，也提供对 Bootstrap 分页的支持。

#### Tailwind

如果你在 Tailwind 4.x 中使用 Laravel 默认的 Tailwind 分页视图，你的应用的 `resources/css/app.css` 文件已经正确配置，可以 `@source` Laravel 的分页视图：

```css
@import 'tailwindcss';

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
```

## 基础用法

### 对查询构建器结果进行分页

有几种方式可以对项目进行分页。最简单的方法是对 [查询构建器](/docs/laravel/12.x/queries) 或 [Eloquent 查询](/docs/laravel/12.x/eloquent) 使用 `paginate` 方法。`paginate` 方法会自动处理查询的「limit」和「offset」，并根据用户当前查看的页面进行设置。默认情况下，当前页面是由 HTTP 请求中的 `page` 查询字符串参数的值检测到的。这个值会被 Laravel 自动检测到，并且也会自动插入到分页器生成的链接中。




在这个例子中，传递给 `paginate` 方法的唯一参数是你希望「每页」显示的项目数量。在本例中，我们指定每页显示 `15` 个项目：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class UserController extends Controller
{
    /**
     * 显示所有应用用户。
     */
    public function index(): View
    {
        return view('user.index', [
            'users' => DB::table('users')->paginate(15)
        ]);
    }
}
```

#### 简单分页

`paginate` 方法会在从数据库检索记录之前，先统计与查询匹配的记录总数。这样做是为了让分页器知道总共有多少页记录。
然而，如果你并不打算在应用的 UI 中显示总页数，那么这个统计记录数量的查询就是不必要的。

因此，如果你只需要在应用的 UI 中显示简单的「下一页」和「上一页」链接，可以使用 `simplePaginate` 方法来执行一个更高效的单一查询：

```php
$users = DB::table('users')->simplePaginate(15);
```

### 对 Eloquent 结果进行分页

你也可以对 [Eloquent](/docs/laravel/12.x/eloquent) 查询进行分页。
在这个例子中，我们将对 `App\Models\User` 模型进行分页，并指定每页显示 15 条记录。
如你所见，语法与对查询构建器结果进行分页几乎完全相同：

```php
use App\Models\User;

$users = User::paginate(15);
```

当然，你也可以在查询上设置其他约束（例如 `where` 子句）之后，再调用 `paginate` 方法：

```php
$users = User::where('votes', '>', 100)->paginate(15);
```



你也可以在对 Eloquent 模型分页时使用 `simplePaginate` 方法：

```php
$users = User::where('votes', '>', 100)->simplePaginate(15);
```

同样地，你也可以使用 `cursorPaginate` 方法对 Eloquent 模型进行游标分页：

```php
$users = User::where('votes', '>', 100)->cursorPaginate(15);
```

#### 每页多个分页器实例

有时，你可能需要在应用渲染的同一个页面上显示两个独立的分页器。
然而，如果这两个分页器实例都使用 `page` 查询字符串参数来存储当前页码，那么这两个分页器就会发生冲突。

为了解决这个冲突，你可以通过传递第三个参数来指定要用于存储分页器当前页码的查询字符串参数名，该参数可用于 `paginate`、`simplePaginate` 和 `cursorPaginate` 方法：

```php
use App\Models\User;

$users = User::where('votes', '>', 100)->paginate(
    $perPage = 15, $columns = ['*'], $pageName = 'users'
);
```

### 游标分页

虽然 `paginate` 和 `simplePaginate` 使用 SQL 的「offset」子句来创建查询，但游标分页的工作方式是通过构建「where」子句来比较查询中包含的排序列的值，从而在 Laravel 的所有分页方法中提供最高效的数据库性能。
这种分页方法特别适合大型数据集和「无限滚动」的用户界面。

与基于 offset 的分页不同，offset 分页会在分页器生成的 URL 的查询字符串中包含一个页码，而基于游标的分页会在查询字符串中放置一个「cursor」字符串。
这个游标是一个编码后的字符串，其中包含下一次分页查询应从何处开始分页以及它应该分页的方向：

```text
http://localhost/users?cursor=eyJpZCI6MTUsIl9wb2ludHNUb05leHRJdGVtcyI6dHJ1ZX0
```



你可以通过查询构建器提供的 `cursorPaginate` 方法来创建一个基于游标的分页器实例。
此方法会返回一个 `Illuminate\Pagination\CursorPaginator` 实例：

```php
$users = DB::table('users')->orderBy('id')->cursorPaginate(15);
```

一旦你获取到一个游标分页器实例，你可以像使用 `paginate` 和 `simplePaginate` 方法时那样 [显示分页结果](#displaying-pagination-results)。
有关游标分页器所提供的实例方法的更多信息，请参阅 [游标分页器实例方法文档](#cursor-paginator-instance-methods)。

> [!警告]
> 你的查询必须包含一个「order by」子句，才能使用游标分页。
此外，查询所排序的列必须属于你正在分页的表。

#### 游标分页 vs. 偏移量分页

为了说明偏移量分页和游标分页之间的区别，让我们看一些示例 SQL 查询。
以下两个查询都会显示 `users` 表按 `id` 排序的「第二页」结果：

```sql
# Offset Pagination...
select * from users order by id asc limit 15 offset 15;

# Cursor Pagination...
select * from users where id > 15 order by id asc limit 15;
```

游标分页查询相较于偏移量分页，具有以下优势：

-   对于大型数据集，如果「order by」列有索引，游标分页会提供更好的性能。这是因为「offset」子句会扫描所有之前匹配的数据。

-   对于频繁写入的数据集，如果用户正在查看的页面最近新增或删除了数据，偏移量分页可能会跳过记录或显示重复记录。



然而，游标分页具有以下限制：

-   与 `simplePaginate` 一样，游标分页只能用于显示「下一页」和「上一页」链接，并且不支持生成带页码的链接。
-   它要求排序基于至少一个唯一列，或者是唯一的列组合。包含 `null` 值的列不被支持。
-   「order by」子句中的查询表达式仅在它们被起别名并同时添加到「select」子句时才被支持。
-   不支持带参数的查询表达式。

### 手动创建分页器

有时你可能希望手动创建一个分页实例，并传递一个你已经在内存中的项目数组。
根据你的需求，你可以创建一个 `Illuminate\Pagination\Paginator`、`Illuminate\Pagination\LengthAwarePaginator` 或 `Illuminate\Pagination\CursorPaginator` 实例。

`Paginator` 和 `CursorPaginator` 类不需要知道结果集中的项目总数；然而，正因如此，这些类没有获取最后一页索引的方法。
`LengthAwarePaginator` 接受的参数与 `Paginator` 几乎相同；但它需要结果集中的项目总数。

换句话说：

-   `Paginator` 对应查询构建器上的 `simplePaginate` 方法，
-   `CursorPaginator` 对应 `cursorPaginate` 方法，
-   `LengthAwarePaginator` 对应 `paginate` 方法。

> [!警告]
> 当手动创建分页器实例时，你应当手动对传递给分页器的结果数组进行「切片」。
如果你不确定如何操作，可以查看 PHP 函数 [array_slice](https://secure.php.net/manual/en/function.array-slice.php)。



### 自定义分页 URL

默认情况下，分页器生成的链接会与当前请求的 URI 匹配。
然而，分页器的 `withPath` 方法允许你在生成链接时自定义分页器使用的 URI。
例如，如果你希望分页器生成类似 `http://example.com/admin/users?page=N` 的链接，你应该将 `/admin/users` 传递给 `withPath` 方法：

```php
use App\Models\User;

Route::get('/users', function () {
    $users = User::paginate(15);

    $users->withPath('/admin/users');

    // ...
});
```

#### 添加查询字符串值

你可以使用 `appends` 方法为分页链接追加查询字符串。
例如，要为每个分页链接追加 `sort=votes`，你应当这样调用 `appends`：

```php
use App\Models\User;

Route::get('/users', function () {
    $users = User::paginate(15);

    $users->appends(['sort' => 'votes']);

    // ...
});
```

如果你希望将当前请求的所有查询字符串值都追加到分页链接中，可以使用 `withQueryString` 方法：

```php
$users = User::paginate(15)->withQueryString();
```

#### 添加哈希片段

如果你需要为分页器生成的 URL 追加「哈希片段」，可以使用 `fragment` 方法。
例如，要在每个分页链接的末尾追加 `#users`，你应当这样调用 `fragment` 方法：

```php
$users = User::paginate(15)->fragment('users');
```

## 显示分页结果

当调用 `paginate` 方法时，你将会得到一个 `Illuminate\Pagination\LengthAwarePaginator` 实例；
而调用 `simplePaginate` 方法时，会返回一个 `Illuminate\Pagination\Paginator` 实例；
最后，调用 `cursorPaginate` 方法则会返回一个 `Illuminate\Pagination\CursorPaginator` 实例。




这些对象提供了若干描述结果集的方法。
除了这些辅助方法外，分页器实例本身是迭代器，可以像数组一样循环遍历。
因此，一旦你获取到结果，就可以使用 [Blade](/docs/laravel/12.x/blade) 来显示结果并渲染分页链接：

```blade
<div class="container">
    @foreach ($users as $user)
        {{ $user->name }}
    @endforeach
</div>

{{ $users->links() }}
```

`links` 方法会渲染结果集中剩余页面的链接。
这些链接中已经包含了正确的 `page` 查询字符串变量。
请记住，`links` 方法生成的 HTML 与 [Tailwind CSS 框架](https://tailwindcss.com) 兼容。

### 调整分页链接窗口

当分页器显示分页链接时，会显示当前页码以及当前页码之前和之后的三个页面链接。
通过使用 `onEachSide` 方法，你可以控制在分页器生成的中间滑动窗口中，每一侧额外显示多少个链接：

```blade
{{ $users->onEachSide(5)->links() }}
```

### 将结果转换为 JSON

Laravel 的分页器类实现了 `Illuminate\Contracts\Support\Jsonable` 接口契约，并提供了 `toJson` 方法，因此将分页结果转换为 JSON 非常容易。
你也可以通过从路由或控制器动作返回分页器实例，将其转换为 JSON：

```php
use App\Models\User;

Route::get('/users', function () {
    return User::paginate();
});
```

分页器生成的 JSON 将包含诸如 `total`、`current_page`、`last_page` 等元信息。
结果记录可通过 JSON 数组中的 `data` 键获取。
以下是从路由返回分页器实例时生成的 JSON 示例：

```json
{
   "total": 50,
   "per_page": 15,
   "current_page": 1,
   "last_page": 4,
   "current_page_url": "http://laravel.app?page=1",
   "first_page_url": "http://laravel.app?page=1",
   "last_page_url": "http://laravel.app?page=4",
   "next_page_url": "http://laravel.app?page=2",
   "prev_page_url": null,
   "path": "http://laravel.app",
   "from": 1,
   "to": 15,
   "data":[
        {
            // Record...
        },
        {
            // Record...
        }
   ]
}
```



## 自定义分页视图

默认情况下，用于显示分页链接的视图与 [Tailwind CSS](https://tailwindcss.com) 框架兼容。
但是，如果你没有使用 Tailwind，你也可以自由定义自己的视图来渲染这些链接。
当在分页器实例上调用 `links` 方法时，你可以将视图名称作为第一个参数传递给该方法：

```blade
{{ $paginator->links('view.name') }}

<!-- 向视图传递额外数据... -->
{{ $paginator->links('view.name', ['foo' => 'bar']) }}
```

然而，最简单的自定义分页视图的方法是使用 `vendor:publish` 命令将它们导出到 `resources/views/vendor` 目录：

```shell
php artisan vendor:publish --tag=laravel-pagination
```
该命令会将视图放置到应用的 `resources/views/vendor/pagination` 目录中。
该目录下的 `tailwind.blade.php` 文件对应默认的分页视图。
你可以编辑此文件来修改分页的 HTML。

如果你想指定一个不同的文件作为默认分页视图，可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用分页器的 `defaultView` 和 `defaultSimpleView` 方法：

```php
<?php

namespace App\Providers;

use Illuminate\Pagination\Paginator;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 启动任意应用服务。
     */
    public function boot(): void
    {
        Paginator::defaultView('view-name');

        Paginator::defaultSimpleView('view-name');
    }
}
```

### 使用 Bootstrap

Laravel 还包含了使用 [Bootstrap CSS](https://getbootstrap.com/) 构建的分页视图。
如果你希望使用这些视图来替代默认的 Tailwind 视图，可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用分页器的 `useBootstrapFour` 或 `useBootstrapFive` 方法：

```php
use Illuminate\Pagination\Paginator;

/**
 * 启动任意应用服务。
 */
public function boot(): void
{
    Paginator::useBootstrapFive();
    Paginator::useBootstrapFour();
}
```



## Paginator / LengthAwarePaginator 实例方法

每个分页器实例都提供了一些额外的分页信息，可以通过以下方法获取：

| 方法 | 描述 |
| --- | --- |
| `$paginator->count()` | 获取当前页的项目数量。 |
| `$paginator->currentPage()` | 获取当前页码。 |
| `$paginator->firstItem()` | 获取结果集中第一个项目的序号。 |
| `$paginator->getOptions()` | 获取分页器的配置选项。 |
| `$paginator->getUrlRange($start, $end)` | 创建一段分页 URL 范围。 |
| `$paginator->hasPages()` | 判断是否有足够的项目可以分成多页。 |
| `$paginator->hasMorePages()` | 判断数据存储中是否还有更多项目。 |
| `$paginator->items()` | 获取当前页的所有项目。 |
| `$paginator->lastItem()` | 获取结果集中最后一个项目的序号。 |
| `$paginator->lastPage()` | 获取最后一页的页码。（`simplePaginate` 时不可用） |
| `$paginator->nextPageUrl()` | 获取下一页的 URL。 |
| `$paginator->onFirstPage()` | 判断分页器是否在第一页。 |
| `$paginator->onLastPage()` | 判断分页器是否在最后一页。 |
| `$paginator->perPage()` | 每页显示的项目数量。 |
| `$paginator->previousPageUrl()` | 获取上一页的 URL。 |
| `$paginator->total()` | 获取数据存储中匹配的项目总数。（`simplePaginate` 时不可用） |
| `$paginator->url($page)` | 获取指定页码的 URL。 |
| `$paginator->getPageName()` | 获取用于存储页码的查询字符串变量名。 |
| `$paginator->setPageName($name)` | 设置用于存储页码的查询字符串变量名。 |
| `$paginator->through($callback)` | 使用回调函数转换每个项目。 |

</div>



## Cursor Paginator 实例方法

每个游标分页器实例都提供了一些额外的分页信息，可以通过以下方法获取：

| 方法 | 描述 |
| --- | --- |
| `$paginator->count()` | 获取当前页的项目数量。 |
| `$paginator->cursor()` | 获取当前的游标实例。 |
| `$paginator->getOptions()` | 获取分页器的配置选项。 |
| `$paginator->hasPages()` | 判断是否有足够的项目可以分成多页。 |
| `$paginator->hasMorePages()` | 判断数据存储中是否还有更多项目。 |
| `$paginator->getCursorName()` | 获取用于存储游标的查询字符串变量名。 |
| `$paginator->items()` | 获取当前页的所有项目。 |
| `$paginator->nextCursor()` | 获取下一组项目的游标实例。 |
| `$paginator->nextPageUrl()` | 获取下一页的 URL。 |
| `$paginator->onFirstPage()` | 判断分页器是否在第一页。 |
| `$paginator->onLastPage()` | 判断分页器是否在最后一页。 |
| `$paginator->perPage()` | 每页显示的项目数量。 |
| `$paginator->previousCursor()` | 获取上一组项目的游标实例。 |
| `$paginator->previousPageUrl()` | 获取上一页的 URL。 |
| `$paginator->setCursorName()` | 设置用于存储游标的查询字符串变量名。 |
| `$paginator->url($cursor)` | 获取指定游标实例的 URL。 |

</div>
