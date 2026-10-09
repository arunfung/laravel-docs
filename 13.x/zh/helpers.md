# 辅助函数

- [简介](#introduction)
- [可用方法](#available-methods)
- [其他实用工具](#other-utilities)
    - [基准测试](#benchmarking)
    - [日期和时间](#dates)
    - [延迟函数](#deferred-functions)
    - [抽奖机制](#lottery)
    - [管道](#pipeline)
    - [休眠](#sleep)
    - [时间盒](#timebox)
    - [URI](#uri)

<a name="introduction"></a>
## 简介

Laravel 包含多种全局 PHP「辅助函数」。框架本身也使用了其中许多函数；如果觉得方便，也可以在自己的应用程序中使用它们。

<a name="available-methods"></a>
## 可用方法

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

<a name="arrays-and-objects-method-list"></a>
### 数组和对象

<div class="collection-method-list" markdown="1">

[Arr::accessible](#method-array-accessible)
[Arr::add](#method-array-add)
[Arr::array](#method-array-array)
[Arr::boolean](#method-array-boolean)
[Arr::collapse](#method-array-collapse)
[Arr::crossJoin](#method-array-crossjoin)
[Arr::divide](#method-array-divide)
[Arr::dot](#method-array-dot)
[Arr::every](#method-array-every)
[Arr::except](#method-array-except)
[Arr::exceptValues](#method-array-except-values)
[Arr::exists](#method-array-exists)
[Arr::first](#method-array-first)
[Arr::flatten](#method-array-flatten)
[Arr::float](#method-array-float)
[Arr::forget](#method-array-forget)
[Arr::from](#method-array-from)
[Arr::get](#method-array-get)
[Arr::has](#method-array-has)
[Arr::hasAll](#method-array-hasall)
[Arr::hasAny](#method-array-hasany)
[Arr::integer](#method-array-integer)
[Arr::isAssoc](#method-array-isassoc)
[Arr::isList](#method-array-islist)
[Arr::join](#method-array-join)
[Arr::keyBy](#method-array-keyby)
[Arr::last](#method-array-last)
[Arr::map](#method-array-map)
[Arr::mapSpread](#method-array-map-spread)
[Arr::mapWithKeys](#method-array-map-with-keys)
[Arr::only](#method-array-only)
[Arr::onlyValues](#method-array-only-values)
[Arr::partition](#method-array-partition)
[Arr::pluck](#method-array-pluck)
[Arr::prepend](#method-array-prepend)
[Arr::prependKeysWith](#method-array-prependkeyswith)
[Arr::pull](#method-array-pull)
[Arr::push](#method-array-push)
[Arr::query](#method-array-query)
[Arr::random](#method-array-random)
[Arr::reject](#method-array-reject)
[Arr::select](#method-array-select)
[Arr::set](#method-array-set)
[Arr::shuffle](#method-array-shuffle)
[Arr::sole](#method-array-sole)
[Arr::some](#method-array-some)
[Arr::sort](#method-array-sort)
[Arr::sortDesc](#method-array-sort-desc)
[Arr::sortRecursive](#method-array-sort-recursive)
[Arr::string](#method-array-string)
[Arr::take](#method-array-take)
[Arr::toCssClasses](#method-array-to-css-classes)
[Arr::toCssStyles](#method-array-to-css-styles)
[Arr::undot](#method-array-undot)
[Arr::where](#method-array-where)
[Arr::whereNotNull](#method-array-where-not-null)
[Arr::wrap](#method-array-wrap)
[data_fill](#method-data-fill)
[data_get](#method-data-get)
[data_set](#method-data-set)
[data_forget](#method-data-forget)
[head](#method-head)
[last](#method-last)
</div>

<a name="numbers-method-list"></a>
### 数字处理

<div class="collection-method-list" markdown="1">

[Number::abbreviate](#method-number-abbreviate)
[Number::clamp](#method-number-clamp)
[Number::currency](#method-number-currency)
[Number::defaultCurrency](#method-default-currency)
[Number::defaultLocale](#method-default-locale)
[Number::fileSize](#method-number-file-size)
[Number::forHumans](#method-number-for-humans)
[Number::format](#method-number-format)
[Number::ordinal](#method-number-ordinal)
[Number::pairs](#method-number-pairs)
[Number::parse](#method-number-parse)
[Number::parseInt](#method-number-parse-int)
[Number::parseFloat](#method-number-parse-float)
[Number::percentage](#method-number-percentage)
[Number::spell](#method-number-spell)
[Number::spellOrdinal](#method-number-spell-ordinal)
[Number::trim](#method-number-trim)
[Number::useLocale](#method-number-use-locale)
[Number::withLocale](#method-number-with-locale)
[Number::useCurrency](#method-number-use-currency)
[Number::withCurrency](#method-number-with-currency)

</div>

<a name="paths-method-list"></a>
### 路径处理

<div class="collection-method-list" markdown="1">

[app_path](#method-app-path)
[base_path](#method-base-path)
[config_path](#method-config-path)
[database_path](#method-database-path)
[lang_path](#method-lang-path)
[public_path](#method-public-path)
[resource_path](#method-resource-path)
[storage_path](#method-storage-path)

</div>

<a name="urls-method-list"></a>
### URLs

<div class="collection-method-list" markdown="1">

[action](#method-action)
[asset](#method-asset)
[route](#method-route)
[secure_asset](#method-secure-asset)
[secure_url](#method-secure-url)
[to_action](#method-to-action)
[to_route](#method-to-route)
[uri](#method-uri)
[url](#method-url)

</div>

<a name="miscellaneous-method-list"></a>
### 其他方法

<div class="collection-method-list" markdown="1">

[abort](#method-abort)
[abort_if](#method-abort-if)
[abort_unless](#method-abort-unless)
[app](#method-app)
[auth](#method-auth)
[back](#method-back)
[bcrypt](#method-bcrypt)
[blank](#method-blank)
[broadcast](#method-broadcast)
[broadcast_if](#method-broadcast-if)
[broadcast_unless](#method-broadcast-unless)
[cache](#method-cache)
[class_uses_recursive](#method-class-uses-recursive)
[collect](#method-collect)
[config](#method-config)
[context](#method-context)
[cookie](#method-cookie)
[csrf_field](#method-csrf-field)
[csrf_token](#method-csrf-token)
[decrypt](#method-decrypt)
[dd](#method-dd)
[dispatch](#method-dispatch)
[dispatch_sync](#method-dispatch-sync)
[dump](#method-dump)
[encrypt](#method-encrypt)
[env](#method-env)
[event](#method-event)
[fake](#method-fake)
[filled](#method-filled)
[info](#method-info)
[literal](#method-literal)
[logger](#method-logger)
[method_field](#method-method-field)
[now](#method-now)
[old](#method-old)
[once](#method-once)
[optional](#method-optional)
[policy](#method-policy)
[redirect](#method-redirect)
[report](#method-report)
[report_if](#method-report-if)
[report_unless](#method-report-unless)
[request](#method-request)
[rescue](#method-rescue)
[resolve](#method-resolve)
[response](#method-response)
[retry](#method-retry)
[session](#method-session)
[tap](#method-tap)
[throw_if](#method-throw-if)
[throw_unless](#method-throw-unless)
[today](#method-today)
[trait_uses_recursive](#method-trait-uses-recursive)
[transform](#method-transform)
[validator](#method-validator)
[value](#method-value)
[view](#method-view)
[with](#method-with)
[when](#method-when)

</div>

<a name="arrays"></a>
## 数组与对象

<a name="method-array-accessible"></a>
#### `Arr::accessible()` {.collection-method .first-collection-method}

`Arr::accessible` 方法用于判断给定的值是否可通过数组方式访问：

```php
use Illuminate\Support\Arr;
use Illuminate\Support\Collection;

$isAccessible = Arr::accessible(['a' => 1, 'b' => 2]);

// true

$isAccessible = Arr::accessible(new Collection);

// true

$isAccessible = Arr::accessible('abc');

// false

$isAccessible = Arr::accessible(new stdClass);

// false
```

<a name="method-array-add"></a>
#### `Arr::add()` {.collection-method}

`Arr::add` 方法会在数组中指定键不存在或对应值为 `null` 时，向数组添加该键值对：

```php
use Illuminate\Support\Arr;

$array = Arr::add(['name' => 'Desk'], 'price', 100);

// ['name' => 'Desk', 'price' => 100]

$array = Arr::add(['name' => 'Desk', 'price' => null], 'price', 100);

// ['name' => 'Desk', 'price' => 100]
```

<a name="method-array-array"></a>
#### `Arr::array()` {.collection-method}

`Arr::array` 方法使用「点」语法从深层嵌套数组中获取值（与 [Arr::get()](#method-array-get) 类似），但如果请求的值不是数组，则会抛出 `InvalidArgumentException` 异常：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$value = Arr::array($array, 'languages');

// ['PHP', 'Ruby']

$value = Arr::array($array, 'name');

// 抛出 InvalidArgumentException
```

<a name="method-array-boolean"></a>
#### `Arr::boolean()` {.collection-method}

`Arr::boolean` 方法使用「点」语法从深层嵌套数组中获取值（与 [Arr::get()](#method-array-get) 类似），但如果请求的值不是布尔值，则会抛出 `InvalidArgumentException` 异常：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'available' => true];

$value = Arr::boolean($array, 'available');

// true

$value = Arr::boolean($array, 'name');

// 抛出 InvalidArgumentException
```


<a name="method-array-collapse"></a>
#### `Arr::collapse()` {.collection-method}

`Arr::collapse` 方法：把数组里的所有子数组合并成一个新数组。

```php
use Illuminate\Support\Arr;

$array = Arr::collapse([[1, 2, 3], [4, 5, 6], [7, 8, 9]]);

// [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

<a name="method-array-crossjoin"></a>
#### `Arr::crossJoin()` {.collection-method}

`Arr::crossJoin` 方法会把几个数组交叉放在一起，把所有可能的组合全部列出来。

```php
use Illuminate\Support\Arr;

$matrix = Arr::crossJoin([1, 2], ['a', 'b']);

/*
    [
        [1, 'a'],
        [1, 'b'],
        [2, 'a'],
        [2, 'b'],
    ]
*/

$matrix = Arr::crossJoin([1, 2], ['a', 'b'], ['I', 'II']);

/*
    [
        [1, 'a', 'I'],
        [1, 'a', 'II'],
        [1, 'b', 'I'],
        [1, 'b', 'II'],
        [2, 'a', 'I'],
        [2, 'a', 'II'],
        [2, 'b', 'I'],
        [2, 'b', 'II'],
    ]
*/
```

<a name="method-array-divide"></a>
#### `Arr::divide()` {.collection-method}

`Arr::divide` 方法把一个数组返回两个数组，一个包含给定数组的键，另一个包含给定数组的值。

```php
use Illuminate\Support\Arr;

[$keys, $values] = Arr::divide(['name' => 'Desk']);

// $keys: ['name']

// $values: ['Desk']
```

<a name="method-array-dot"></a>
#### `Arr::dot()` {.collection-method}

`Arr::dot` 方法将多维数组展平为单层数组，使用「点」表示法在键名中表示嵌套层级：

```php
use Illuminate\Support\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

$flattened = Arr::dot($array);

// ['products.desk.price' => 100]
```

<a name="method-array-every"></a>
#### `Arr::every()` {.collection-method}

`Arr::every` 方法判断数组中的所有值是否都通过给定的条件测试：

```php
use Illuminate\Support\Arr;

$array = [1, 2, 3];

Arr::every($array, fn ($i) => $i > 0);

// true

Arr::every($array, fn ($i) => $i > 2);

// false
```

<a name="method-array-except"></a>
#### `Arr::except()` {.collection-method}

`Arr::except` 方法从数组中移除指定的键值对。

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Desk', 'price' => 100];

$filtered = Arr::except($array, ['price']);

// ['name' => 'Desk']
```

<a name="method-array-except-values"></a>
#### `Arr::exceptValues()` {.collection-method}

`Arr::exceptValues` 方法从数组中移除指定的值：

```php
use Illuminate\Support\Arr;

$array = ['foo', 'bar', 'baz', 'qux'];

$filtered = Arr::exceptValues($array, ['foo', 'baz']);

// ['bar', 'qux']
```

还可以将 `strict` 参数设为 `true`，在筛选时进行严格的类型比较：

```php
use Illuminate\Support\Arr;

$array = [1, '1', 2, '2'];

$filtered = Arr::exceptValues($array, [1, 2], strict: true);

// ['1', '2']
```

<a name="method-array-exists"></a>
#### `Arr::exists()` {.collection-method}

`Arr::exists` 方法检查给定的键是否存在于数组中：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'John Doe', 'age' => 17];

$exists = Arr::exists($array, 'name');

// true

$exists = Arr::exists($array, 'salary');

// false
```

<a name="method-array-first"></a>
#### `Arr::first()` {.collection-method}

`Arr::first` 方法用于获取数组里首个满足指定条件的元素。

```php
use Illuminate\Support\Arr;

$array = [100, 200, 300];

$first = Arr::first($array, function (int $value, int $key) {
    return $value >= 150;
});

// 200
```

还可以将默认值作为第三个参数传递给该方法。当数组里没有任何元素满足条件时，方法就会直接返回这个默认值。

```php
use Illuminate\Support\Arr;

$first = Arr::first($array, $callback, $default);
```

<a name="method-array-flatten"></a>
#### `Arr::flatten()` {.collection-method}

`Arr::flatten` 方法将一个多维数组展平成单层数组。

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$flattened = Arr::flatten($array);

// ['Joe', 'PHP', 'Ruby']
```

<a name="method-array-float"></a>
#### `Arr::float()` {.collection-method}

`Arr::float` 方法使用「点」表示法从深层嵌套数组中获取值（与 [Arr::get()](#method-array-get) 类似），但如果请求的值不是 `float`，则会抛出 `InvalidArgumentException`：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'balance' => 123.45];

$value = Arr::float($array, 'balance');

// 123.45

$value = Arr::float($array, 'name');

// 抛出 InvalidArgumentException
```

<a name="method-array-forget"></a>
#### `Arr::forget()` {.collection-method}

`Arr::forget` 方法使用「点」表示法从深层嵌套数组中移除指定的键值对：

```php
use Illuminate\Support\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

Arr::forget($array, 'products.desk');

// ['products' => []]
```

<a name="method-array-from"></a>
#### `Arr::from()` {.collection-method}

`Arr::from` 方法将给定值转换为数组，支持数组、对象以及常见的 Laravel 接口，如 `Arrayable`、`Enumerable`、`Jsonable`、`JsonSerializable`，也支持 `Traversable` 和 `WeakMap`：

```php
use Illuminate\Support\Arr;

Arr::from((object) ['foo' => 'bar']); // ['foo' => 'bar']

class TestJsonableObject implements Jsonable
{
    public function toJson($options = 0)
    {
        return json_encode(['foo' => 'bar']);
    }
}

Arr::from(new TestJsonableObject); // ['foo' => 'bar']
```

<a name="method-array-get"></a>
#### `Arr::get()` {.collection-method}

`Arr::get` 方法使用 「.」 表示法从深度嵌套数组中检索值：

```php
use Illuminate\Support\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

$price = Arr::get($array, 'products.desk.price');

// 100
```

`Arr::get` 方法还接受一个默认值，如果指定的键不在数组中，则返回该默认值：

```php
use Illuminate\Support\Arr;

$discount = Arr::get($array, 'products.desk.discount', 0);

// 0
```

<a name="method-array-has"></a>
#### `Arr::has()` {.collection-method}

`Arr::has` 方法使用 「.」 表示法检查给定的一个或多个元素是否存在于数组中：

```php
use Illuminate\Support\Arr;

$array = ['product' => ['name' => 'Desk', 'price' => 100]];

$contains = Arr::has($array, 'product.name');

// true

$contains = Arr::has($array, ['product.price', 'product.discount']);

// false
```

<a name="method-array-hasall"></a>
#### `Arr::hasAll()` {.collection-method}

`Arr::hasAll` 方法使用 「.」 表示法来确定给定数组中是否存在所有指定的键：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Taylor', 'language' => 'PHP'];

Arr::hasAll($array, ['name']); // true
Arr::hasAll($array, ['name', 'language']); // true
Arr::hasAll($array, ['name', 'IDE']); // false
```

<a name="method-array-hasany"></a>
#### `Arr::hasAny()` {.collection-method}

`Arr::hasAny` 方法使用 「.」 表示法检查给定集合中的任何元素是否存在于数组中：

```php
use Illuminate\Support\Arr;

$array = ['product' => ['name' => 'Desk', 'price' => 100]];

$contains = Arr::hasAny($array, 'product.name');

// true

$contains = Arr::hasAny($array, ['product.name', 'product.discount']);

// true

$contains = Arr::hasAny($array, ['category', 'product.discount']);

// false
```

<a name="method-array-integer"></a>
#### `Arr::integer()` {.collection-method}

`Arr::integer` 方法使用 「.」 表示法从深度嵌套数组中检索值（就像 [Arr::get()](#method-array-get) 一样），但如果请求的值不是 int ，则会抛出 `InvalidArgumentException` 异常：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'age' => 42];

$value = Arr::integer($array, 'age');

// 42

$value = Arr::integer($array, 'name');

// 抛出 InvalidArgumentException
```

<a name="method-array-isassoc"></a>
#### `Arr::isAssoc()` {.collection-method}

如果提供的数组是一个关联数组，那么`Arr::isAssoc` 方法将返回 `true` 。 如果一个数组没有从 0 开始的连续数值键，可以被认为是「关联的」：

```php
use Illuminate\Support\Arr;

$isAssoc = Arr::isAssoc(['product' => ['name' => 'Desk', 'price' => 100]]);

// true

$isAssoc = Arr::isAssoc([1, 2, 3]);

// false
```

<a name="method-array-islist"></a>
#### `Arr::isList()` {.collection-method}

如果提供的数组的键是从 0 开始的连续数值键，那么 `Arr::isList` 方法将返回 `true` ：

```php
use Illuminate\Support\Arr;

$isList = Arr::isList(['foo', 'bar', 'baz']);

// true

$isList = Arr::isList(['product' => ['name' => 'Desk', 'price' => 100]]);

// false
```

<a name="method-array-join"></a>
#### `Arr::join()` {.collection-method}

`Arr::join` 方法使用字符串连接数组元素。通过第三个参数，还可以为数组的最后一个元素指定不同的连接字符串：

```php
use Illuminate\Support\Arr;

$array = ['Tailwind', 'Alpine', 'Laravel', 'Livewire'];

$joined = Arr::join($array, ', ');

// Tailwind, Alpine, Laravel, Livewire

$joined = Arr::join($array, ', ', ', and ');

// Tailwind, Alpine, Laravel, and Livewire
```

<a name="method-array-keyby"></a>
#### `Arr::keyBy()` {.collection-method}

`Arr::keyBy` 方法将按照提供的键对数组进行加键。如果多个元素存在相同的键，则只有最后一个元素出现在新数组中：

```php
use Illuminate\Support\Arr;

$array = [
    ['product_id' => 'prod-100', 'name' => 'Desk'],
    ['product_id' => 'prod-200', 'name' => 'Chair'],
];

$keyed = Arr::keyBy($array, 'product_id');

/*
    [
        'prod-100' => ['product_id' => 'prod-100', 'name' => 'Desk'],
        'prod-200' => ['product_id' => 'prod-200', 'name' => 'Chair'],
    ]
*/
```

<a name="method-array-last"></a>
#### `Arr::last()` {.collection-method}

`Arr::last` 方法返回数组中最后一个符合条件的元素：

```php
use Illuminate\Support\Arr;

$array = [100, 200, 300, 110];

$last = Arr::last($array, function (int $value, int $key) {
    return $value >= 150;
});

// 300
```

将一个默认值作为第三个参数传入该方法。当数组中没有值符合条件时将返回该默认值：

```php
use Illuminate\Support\Arr;

$last = Arr::last($array, $callback, $default);
```

<a name="method-array-map"></a>
#### `Arr::map()` {.collection-method}

`Arr::map` 方法遍历数组并将每个元素的值和键传递给回调函数。数组将会被回调函数的返回值替代：

```php
use Illuminate\Support\Arr;

$array = ['first' => 'james', 'last' => 'kirk'];

$mapped = Arr::map($array, function (string $value, string $key) {
    return ucfirst($value);
});

// ['first' => 'James', 'last' => 'Kirk']
```

<a name="method-array-map-spread"></a>
#### `Arr::mapSpread()` {.collection-method}

`Arr::mapSpread` 方法遍历数组，将每个嵌套的元素传递给闭包。这个闭包可以自由修改元素并返回，从而形成一个由修改后元素组成的新数组：

```php
use Illuminate\Support\Arr;

$array = [
    [0, 1],
    [2, 3],
    [4, 5],
    [6, 7],
    [8, 9],
];

$mapped = Arr::mapSpread($array, function (int $even, int $odd) {
    return $even + $odd;
});

/*
    [1, 5, 9, 13, 17]
*/
```

<a name="method-array-map-with-keys"></a>
#### `Arr::mapWithKeys()` {.collection-method}

`Arr::mapWithKeys` 方法遍历数组并将每个值都传递给指定的回调函数。这个回调函数应该返回一个包含单个键值对的关联数组：

```php
use Illuminate\Support\Arr;

$array = [
    [
        'name' => 'John',
        'department' => 'Sales',
        'email' => 'john@example.com',
    ],
    [
        'name' => 'Jane',
        'department' => 'Marketing',
        'email' => 'jane@example.com',
    ]
];

$mapped = Arr::mapWithKeys($array, function (array $item, int $key) {
    return [$item['email'] => $item['name']];
});

/*
    [
        'john@example.com' => 'John',
        'jane@example.com' => 'Jane',
    ]
*/
```

<a name="method-array-only"></a>
#### `Arr::only()` {.collection-method}

`Arr::only` 方法从指定的数组中返回特定键值对：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Desk', 'price' => 100, 'orders' => 10];

$slice = Arr::only($array, ['name', 'price']);

// ['name' => 'Desk', 'price' => 100]
```

<a name="method-array-only-values"></a>
#### `Arr::onlyValues()` {.collection-method}

`Arr::onlyValues` 方法仅返回数组中指定的值：

```php
use Illuminate\Support\Arr;

$array = ['foo', 'bar', 'baz', 'qux'];

$filtered = Arr::onlyValues($array, ['foo', 'baz']);

// ['foo', 'baz']
```

还可以将 `strict` 参数设为 `true`，在筛选时进行严格的类型比较：

```php
use Illuminate\Support\Arr;

$array = [1, '1', 2, '2'];

$filtered = Arr::onlyValues($array, [1, 2], strict: true);

// [1, 2]
```

<a name="method-array-partition"></a>
#### `Arr::partition()` {.collection-method}

`Arr::partition` 方法可以结合 PHP 数组结构来分离数组中符合条件和不符条件的元素：

```php
<?php

use Illuminate\Support\Arr;

$numbers = [1, 2, 3, 4, 5, 6];

[$underThree, $equalOrAboveThree] = Arr::partition($numbers, function (int $i) {
    return $i < 3;
});

dump($underThree);

// [1, 2]

dump($equalOrAboveThree);

// [3, 4, 5, 6]
```

<a name="method-array-pluck"></a>
#### `Arr::pluck()` {.collection-method}

`Arr::pluck` 方法从数组中检索给定键的全部值：

```php
use Illuminate\Support\Arr;

$array = [
    ['developer' => ['id' => 1, 'name' => 'Taylor']],
    ['developer' => ['id' => 2, 'name' => 'Abigail']],
];

$names = Arr::pluck($array, 'developer.name');

// ['Taylor', 'Abigail']
```

你也可以指定生产列表的键：

```php
use Illuminate\Support\Arr;

$names = Arr::pluck($array, 'developer.name', 'developer.id');

// [1 => 'Taylor', 2 => 'Abigail']
```

<a name="method-array-prepend"></a>
#### `Arr::prepend()` {.collection-method}

`Arr::prepend` 方法将会在数组头部添加一个元素：

```php
use Illuminate\Support\Arr;

$array = ['one', 'two', 'three', 'four'];

$array = Arr::prepend($array, 'zero');

// ['zero', 'one', 'two', 'three', 'four']
```

如果需要，你也可以指定这个值对应的键：

```php
use Illuminate\Support\Arr;

$array = ['price' => 100];

$array = Arr::prepend($array, 'Desk', 'name');

// ['name' => 'Desk', 'price' => 100]
```

<a name="method-array-prependkeyswith"></a>
#### `Arr::prependKeysWith()` {.collection-method}

`Arr::prependKeysWith` 对关联数组的全部键都添加一个指定的前缀：

```php
use Illuminate\Support\Arr;

$array = [
    'name' => 'Desk',
    'price' => 100,
];

$keyed = Arr::prependKeysWith($array, 'product.');

/*
    [
        'product.name' => 'Desk',
        'product.price' => 100,
    ]
*/
```

<a name="method-array-pull"></a>
#### `Arr::pull()` {.collection-method}

`Arr::pull` 方法从数组中返回并删除一个键值对：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Desk', 'price' => 100];

$name = Arr::pull($array, 'name');

// $name: Desk

// $array: ['price' => 100]
```

方法第三个参数传一个默认值。则这个值在键不存在时返回：

```php
use Illuminate\Support\Arr;

$value = Arr::pull($array, $key, $default);
```

<a name="method-array-push"></a>
#### `Arr::push()` {.collection-method}

`Arr::push` 方法使用「点」表示法将元素推入数组。如果指定键对应的数组不存在，则会创建该数组：

```php
use Illuminate\Support\Arr;

$array = [];

Arr::push($array, 'office.furniture', 'Desk');

// $array: ['office' => ['furniture' => ['Desk']]]
```

<a name="method-array-query"></a>
#### `Arr::query()` {.collection-method}

`Arr::query` 方法将数组转换为查询字符串（URL 问号后的部分 ）：

```php
use Illuminate\Support\Arr;

$array = [
    'name' => 'Taylor',
    'order' => [
        'column' => 'created_at',
        'direction' => 'desc'
    ]
];

Arr::query($array);

// name=Taylor&order%5Bcolumn%5D=created_at&order%5Bdirection%5D=desc
```

<a name="method-array-random"></a>
#### `Arr::random()` {.collection-method}

`Arr::random` 方法从数组中随机返回一个值：

```php
use Illuminate\Support\Arr;

$array = [1, 2, 3, 4, 5];

$random = Arr::random($array);

// 4 -（随机获取）
```

你可以通过可选的第二个参数来指定返回的元素数量。注意当提供这个参数时，即使只需要一个元素它也会返回一个数组：

```php
use Illuminate\Support\Arr;

$items = Arr::random($array, 2);

// [2, 5] -（随机获取）
```

<a name="method-array-reject"></a>
#### `Arr::reject()` {.collection-method}

`Arr::reject` 方法通过闭包来移除数组中的元素：

```php
use Illuminate\Support\Arr;

$array = [100, '200', 300, '400', 500];

$filtered = Arr::reject($array, function (string|int $value, int $key) {
    return is_string($value);
});

// [0 => 100, 2 => 300, 4 => 500]
```

<a name="method-array-select"></a>
#### `Arr::select()` {.collection-method}

`Arr::select` 方法从数组中的每个元素选取指定的值，组成一个新数组：

```php
use Illuminate\Support\Arr;

$array = [
    ['id' => 1, 'name' => 'Desk', 'price' => 200],
    ['id' => 2, 'name' => 'Table', 'price' => 150],
    ['id' => 3, 'name' => 'Chair', 'price' => 300],
];

Arr::select($array, ['name', 'price']);

// [['name' => 'Desk', 'price' => 200], ['name' => 'Table', 'price' => 150], ['name' => 'Chair', 'price' => 300]]
```

<a name="method-array-set"></a>
#### `Arr::set()` {.collection-method}

`Arr::set` 方法使用 「点」 符号在深层嵌套数组中设置一个值：

```php
use Illuminate\Support\Arr;

$array = ['products' => ['desk' => ['price' => 100]]];

Arr::set($array, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 200]]]
```

<a name="method-array-shuffle"></a>
#### `Arr::shuffle()` {.collection-method}

`Arr::shuffle` 方法会随机打乱数组中的元素:

```php
use Illuminate\Support\Arr;

$array = Arr::shuffle([1, 2, 3, 4, 5]);

// [3, 2, 5, 1, 4] -（随机生成）
```

<a name="method-array-sole"></a>
#### `Arr::sole()` {.collection-method}

`Arr::sole` 方法使用给定的闭包从数组中获取单个值。如果数组中有多个值与给定的真值测试匹配，将会抛出 `Illuminate\Support\MultipleItemsFoundException` 异常。如果没有值与真值测试匹配，将会抛出 `Illuminate\Support\ItemNotFoundException` 异常：

```php
use Illuminate\Support\Arr;

$array = ['Desk', 'Table', 'Chair'];

$value = Arr::sole($array, fn (string $value) => $value === 'Desk');

// 'Desk'
```

<a name="method-array-some"></a>
#### `Arr::some()` {.collection-method}

`Arr::some` 方法判断数组中是否至少有一个值通过给定的条件测试：

```php
use Illuminate\Support\Arr;

$array = [1, 2, 3];

Arr::some($array, fn ($i) => $i > 2);

// true
```

<a name="method-array-sort"></a>
#### `Arr::sort()` {.collection-method}

`Arr::sort` 方法会按数组的值对数组进行排序：

```php
use Illuminate\Support\Arr;

$array = ['Desk', 'Table', 'Chair'];

$sorted = Arr::sort($array);

// ['Chair', 'Desk', 'Table']
```

你也可以根据给定闭包的结果对数组进行排序：

```php
use Illuminate\Support\Arr;

$array = [
    ['name' => 'Desk'],
    ['name' => 'Table'],
    ['name' => 'Chair'],
];

$sorted = array_values(Arr::sort($array, function (array $value) {
    return $value['name'];
}));

/*
    [
        ['name' => 'Chair'],
        ['name' => 'Desk'],
        ['name' => 'Table'],
    ]
*/
```

<a name="method-array-sort-desc"></a>
#### `Arr::sortDesc()` {.collection-method}

`Arr::sortDesc` 方法按值对数组进行降序排序：

```php
use Illuminate\Support\Arr;

$array = ['Desk', 'Table', 'Chair'];

$sorted = Arr::sortDesc($array);

// ['Table', 'Desk', 'Chair']
```

你也可以根据给定闭包的结果对数组进行排序：

```php
use Illuminate\Support\Arr;

$array = [
    ['name' => 'Desk'],
    ['name' => 'Table'],
    ['name' => 'Chair'],
];

$sorted = array_values(Arr::sortDesc($array, function (array $value) {
    return $value['name'];
}));

/*
    [
        ['name' => 'Table'],
        ['name' => 'Desk'],
        ['name' => 'Chair'],
    ]
*/
```

<a name="method-array-sort-recursive"></a>
#### `Arr::sortRecursive()` {.collection-method}

`Arr::sortRecursive` 方法会递归地对数组进行排序，对于数值索引的子数组使用 `sort` 函数，对于关联子数组使用 `ksort` 函数：

```php
use Illuminate\Support\Arr;

$array = [
    ['Roman', 'Taylor', 'Li'],
    ['PHP', 'Ruby', 'JavaScript'],
    ['one' => 1, 'two' => 2, 'three' => 3],
];

$sorted = Arr::sortRecursive($array);

/*
    [
        ['JavaScript', 'PHP', 'Ruby'],
        ['one' => 1, 'three' => 3, 'two' => 2],
        ['Li', 'Roman', 'Taylor'],
    ]
*/
```

如果您希望结果按降序排序，可以使用`Arr::sortRecursiveDesc` 方法。

```php
$sorted = Arr::sortRecursiveDesc($array);
```

<a name="method-array-string"></a>
#### `Arr::string()` {.collection-method}

`Arr::string` 方法使用 「点」 表示法从深度嵌套的数组中检索值（就像 [Arr::get()](#method-array-get) 所做的那样），但如果请求的值不是 `string`，则会抛出 `InvalidArgumentException`：

```php
use Illuminate\Support\Arr;

$array = ['name' => 'Joe', 'languages' => ['PHP', 'Ruby']];

$value = Arr::string($array, 'name');

// Joe

$value = Arr::string($array, 'languages');

// 抛出 InvalidArgumentException
```

<a name="method-array-take"></a>
#### `Arr::take()` {.collection-method}

`Arr::take` 方法返回一个包含指定数量元素的新数组：

```php
use Illuminate\Support\Arr;

$array = [0, 1, 2, 3, 4, 5];

$chunk = Arr::take($array, 3);

// [0, 1, 2]
```

你也可以传入一个负整数，从数组的末尾获取指定数量的元素：

```php
$array = [0, 1, 2, 3, 4, 5];

$chunk = Arr::take($array, -2);

// [4, 5]
```

<a name="method-array-to-css-classes"></a>
#### `Arr::toCssClasses()` {.collection-method}

`Arr::toCssClasses` 方法会有条件地编译一个 CSS 类字符串。该方法接收一个类数组，数组的键包含你希望添加的类，而值是一个布尔表达式。如果数组元素具有数字键，则它将始终包含在渲染的类列表中：

```php
use Illuminate\Support\Arr;

$isActive = false;
$hasError = true;

$array = ['p-4', 'font-bold' => $isActive, 'bg-red' => $hasError];

$classes = Arr::toCssClasses($array);

/*
    'p-4 bg-red'
*/
```

<a name="method-array-to-css-styles"></a>
#### `Arr::toCssStyles()` {.collection-method}

`Arr::toCssStyles` 方法根据条件生成 CSS 样式字符串。该方法接受一个 CSS 声明数组，数组键包含希望添加的 CSS 声明，值为布尔表达式。如果数组元素使用数字键，则始终包含在生成的 CSS 样式字符串中：

```php
use Illuminate\Support\Arr;

$hasColor = true;

$array = ['background-color: blue', 'color: blue' => $hasColor];

$classes = Arr::toCssStyles($array);

/*
    'background-color: blue; color: blue;'
*/
```

此方法为 Laravel 的 [Blade 组件属性包类名合并功能](/docs/{{version}}/blade#conditionally-merge-classes) 以及 `@class` [Blade 指令](/docs/{{version}}/blade#conditional-classes) 提供了支持。

<a name="method-array-undot"></a>
#### `Arr::undot()` {.collection-method}

`Arr::undot` 方法会将使用 「点」 符号的一维数组展开为多维数组：

```php
use Illuminate\Support\Arr;

$array = [
    'user.name' => 'Kevin Malone',
    'user.occupation' => 'Accountant',
];

$array = Arr::undot($array);

// ['user' => ['name' => 'Kevin Malone', 'occupation' => 'Accountant']]
```

<a name="method-array-where"></a>
#### `Arr::where()` {.collection-method}

`Arr::where` 方法使用给定的闭包来过滤数组：

```php
use Illuminate\Support\Arr;

$array = [100, '200', 300, '400', 500];

$filtered = Arr::where($array, function (string|int $value, int $key) {
    return is_string($value);
});

// [1 => '200', 3 => '400']
```

<a name="method-array-where-not-null"></a>
#### `Arr::whereNotNull()` {.collection-method}

`Arr::whereNotNull` 方法会从给定数组中移除所有`null`值：

```php
use Illuminate\Support\Arr;

$array = [0, null];

$filtered = Arr::whereNotNull($array);

// [0 => 0]
```

<a name="method-array-wrap"></a>
#### `Arr::wrap()` {.collection-method}

`Arr::wrap` 方法会将给定的值包装到一个数组中。如果给定的值已经是一个数组，它将被原样返回，不做任何修改：

```php
use Illuminate\Support\Arr;

$string = 'Laravel';

$array = Arr::wrap($string);

// ['Laravel']
```

如果给定值为 `null`，则会返回一个空数组：

```php
use Illuminate\Support\Arr;

$array = Arr::wrap(null);

// []
```

<a name="method-data-fill"></a>
#### `data_fill()` {.collection-method}

`data_fill` 函数使用「.」表示法在嵌套数组或对象中设置缺失值：

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_fill($data, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 100]]]

data_fill($data, 'products.desk.discount', 10);

// ['products' => ['desk' => ['price' => 100, 'discount' => 10]]]
```

此函数也接受「星号」作为通配符，并会相应地填充目标位置：

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2'],
    ],
];

data_fill($data, 'products.*.price', 200);

/*
    [
        'products' => [
            ['name' => 'Desk 1', 'price' => 100],
            ['name' => 'Desk 2', 'price' => 200],
        ],
    ]
*/
```

<a name="method-data-get"></a>
#### `data_get()` {.collection-method}

`data_get` 函数使用「.」符号从嵌套数组或对象中检索值：

```php
$data = ['products' => ['desk' => ['price' => 100]]];

$price = data_get($data, 'products.desk.price');

// 100
```

`data_get` 函数也接受一个默认值，如果找不到指定的键，则会返回该默认值：

```php
$discount = data_get($data, 'products.desk.discount', 0);

// 0
```

该函数也支持使用「星号」作为通配符，可以匹配数组或对象中的任何键：

```php
$data = [
    'product-one' => ['name' => 'Desk 1', 'price' => 100],
    'product-two' => ['name' => 'Desk 2', 'price' => 150],
];

data_get($data, '*.name');

// ['Desk 1', 'Desk 2'];
```

可以使用 `{first}` 和 `{last}` 占位符来获取数组中的第一个或最后一个元素：

```php
$flight = [
    'segments' => [
        ['from' => 'LHR', 'departure' => '9:00', 'to' => 'IST', 'arrival' => '15:00'],
        ['from' => 'IST', 'departure' => '16:00', 'to' => 'PKX', 'arrival' => '20:00'],
    ],
];

data_get($flight, 'segments.{first}.arrival');

// 15:00
```

<a name="method-data-set"></a>
#### `data_set()` {.collection-method}

`data_set` 函数使用「点（dot）」表示法，在嵌套数组或对象中设置一个值：

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_set($data, 'products.desk.price', 200);

// ['products' => ['desk' => ['price' => 200]]]
```

该函数同样支持使用星号（`*`）作为通配符，并会相应地在目标上设置值：

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2', 'price' => 150],
    ],
];

data_set($data, 'products.*.price', 200);

/*
    [
        'products' => [
            ['name' => 'Desk 1', 'price' => 200],
            ['name' => 'Desk 2', 'price' => 200],
        ],
    ]
*/
```

默认情况下，任何已存在的值都会被覆盖。如果你希望仅在值不存在时才进行设置，可以将 `false` 作为第四个参数传递给该函数：

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_set($data, 'products.desk.price', 200, overwrite: false);

// ['products' => ['desk' => ['price' => 100]]]
```

<a name="method-data-forget"></a>
#### `data_forget()` {.collection-method}

`data_forget` 函数使用「点（dot）」表示法，从嵌套数组或对象中移除一个值：

```php
$data = ['products' => ['desk' => ['price' => 100]]];

data_forget($data, 'products.desk.price');

// ['products' => ['desk' => []]]
```

该函数同样支持使用星号（`*`）作为通配符，并会相应地移除目标中的值：

```php
$data = [
    'products' => [
        ['name' => 'Desk 1', 'price' => 100],
        ['name' => 'Desk 2', 'price' => 150],
    ],
];

data_forget($data, 'products.*.price');

/*
    [
        'products' => [
            ['name' => 'Desk 1'],
            ['name' => 'Desk 2'],
        ],
    ]
*/
```

<a name="method-head"></a>
#### `head()` {.collection-method}

`head` 函数返回给定数组中的第一个元素：

```php
$array = [100, 200, 300];

$first = head($array);

// 100
```

<a name="method-last"></a>
#### `last()` {.collection-method}

`last` 函数返回给定数组中的最后一个元素：

```php
$array = [100, 200, 300];

$last = last($array);

// 300
```

<a name="numbers"></a>
## 数值（Numbers）

<a name="method-number-abbreviate"></a>
#### `Number::abbreviate()` {.collection-method}

`Number::abbreviate` 方法返回所提供数值的人类可读格式，并对单位进行缩写表示：

```php
use Illuminate\Support\Number;

$number = Number::abbreviate(1000);

// 1K

$number = Number::abbreviate(489939);

// 490K

$number = Number::abbreviate(1230000, precision: 2);

// 1.23M
```

<a name="method-number-clamp"></a>
#### `Number::clamp()` {.collection-method}

`Number::clamp` 方法用于确保给定的数字保持在指定的范围内。如果该数字小于最小值，则返回最小值；如果该数字大于最大值，则返回最大值：

```php
use Illuminate\Support\Number;

$number = Number::clamp(105, min: 10, max: 100);

// 100

$number = Number::clamp(5, min: 10, max: 100);

// 10

$number = Number::clamp(10, min: 10, max: 100);

// 10

$number = Number::clamp(20, min: 10, max: 100);

// 20
```

<a name="method-number-currency"></a>
#### `Number::currency()` {.collection-method}

`Number::currency` 方法以字符串形式返回给定数值的货币表示：

```php
use Illuminate\Support\Number;

$currency = Number::currency(1000);

// $1,000.00

$currency = Number::currency(1000, in: 'EUR');

// €1,000.00

$currency = Number::currency(1000, in: 'EUR', locale: 'de');

// 1.000,00 €

$currency = Number::currency(1000, in: 'EUR', locale: 'de', precision: 0);

// 1.000 €
```

<a name="method-default-currency"></a>
#### `Number::defaultCurrency()` {.collection-method}

`Number::defaultCurrency` 方法返回 `Number` 类当前使用的默认货币：

```php
use Illuminate\Support\Number;

$currency = Number::defaultCurrency();

// USD
```

<a name="method-default-locale"></a>
#### `Number::defaultLocale()` {.collection-method}

`Number::defaultLocale` 方法返回 `Number` 类当前使用的默认区域设置（locale）：

```php
use Illuminate\Support\Number;

$locale = Number::defaultLocale();

// en
```

<a name="method-number-file-size"></a>
#### `Number::fileSize()` {.collection-method}

`Number::fileSize` 方法以字符串形式返回给定字节值的文件大小表示：

```php
use Illuminate\Support\Number;

$size = Number::fileSize(1024);

// 1 KB

$size = Number::fileSize(1024 * 1024);

// 1 MB

$size = Number::fileSize(1024, precision: 2);

// 1.00 KB
```

<a name="method-number-for-humans"></a>
#### `Number::forHumans()` {.collection-method}

`Number::forHumans` 方法返回所提供数值的人类可读格式：

```php
use Illuminate\Support\Number;

$number = Number::forHumans(1000);

// 1 thousand

$number = Number::forHumans(489939);

// 490 thousand

$number = Number::forHumans(1230000, precision: 2);

// 1.23 million
```

<a name="method-number-format"></a>
#### `Number::format()` {.collection-method}

`Number::format` 方法将给定的数字格式化为特定区域设置（locale）的字符串：

```php
use Illuminate\Support\Number;

$number = Number::format(100000);

// 100,000

$number = Number::format(100000, precision: 2);

// 100,000.00

$number = Number::format(100000.123, maxPrecision: 2);

// 100,000.12

$number = Number::format(100000, locale: 'de');

// 100.000
```

<a name="method-number-ordinal"></a>
#### `Number::ordinal()` {.collection-method}

`Number::ordinal` 方法返回数字的序数形式：

```php
use Illuminate\Support\Number;

$number = Number::ordinal(1);

// 1st

$number = Number::ordinal(2);

// 2nd

$number = Number::ordinal(21);

// 21st
```

<a name="method-number-pairs"></a>
#### `Number::pairs()` {.collection-method}

`Number::pairs` 方法基于指定的范围和步长值生成一组数字对（子区间）数组。该方法可用于将较大的数字范围拆分为更小、易于管理的子区间，例如用于分页或批量任务处理。`pairs` 方法返回一个数组，其中每个内部数组表示一对数字（一个子区间）：

```php
use Illuminate\Support\Number;

$result = Number::pairs(25, 10);

// [[0, 9], [10, 19], [20, 25]]

$result = Number::pairs(25, 10, offset: 0);

// [[0, 10], [10, 20], [20, 25]]
```

<a name="method-number-parse"></a>
#### `Number::parse()` {.collection-method}

`Number::parse` 方法使用 PHP 的 `NumberFormatter` 解析本地化的数字字符串：

```php
use Illuminate\Support\Number;

$result = Number::parse('10,123', locale: 'en');

// 10123.0

$result = Number::parse('10,123', locale: 'fr');

// 10.123
```

<a name="method-number-parse-int"></a>
#### `Number::parseInt()` {.collection-method}

`Number::parseInt` 方法根据指定的区域设置，将字符串解析为整数：

```php
use Illuminate\Support\Number;

$result = Number::parseInt('10.123');

// (int) 10

$result = Number::parseInt('10,123', locale: 'fr');

// (int) 10
```

<a name="method-number-parse-float"></a>
#### `Number::parseFloat()` {.collection-method}

`Number::parseFloat` 方法根据指定的区域设置，将字符串解析为浮点数：

```php
use Illuminate\Support\Number;

$result = Number::parseFloat('10');

// (float) 10.0

$result = Number::parseFloat('10', locale: 'fr');

// (float) 10.0
```

<a name="method-number-percentage"></a>
#### `Number::percentage()` {.collection-method}

`Number::percentage` 方法以字符串形式返回给定数值的百分比表示：

```php
use Illuminate\Support\Number;

$percentage = Number::percentage(10);

// 10%

$percentage = Number::percentage(10, precision: 2);

// 10.00%

$percentage = Number::percentage(10.123, maxPrecision: 2);

// 10.12%

$percentage = Number::percentage(10, precision: 2, locale: 'de');

// 10,00%
```

<a name="method-number-spell"></a>
#### `Number::spell()` {.collection-method}

`Number::spell` 方法将给定的数字转换为文字形式的字符串：

```php
use Illuminate\Support\Number;

$number = Number::spell(102);

// one hundred and two

$number = Number::spell(88, locale: 'fr');

// quatre-vingt-huit
```

`after` 参数允许你指定一个值，在该值之后的所有数字将被拼写为文字形式：

```php
$number = Number::spell(10, after: 10);

// 10

$number = Number::spell(11, after: 10);

// eleven
```

`until` 参数允许你指定一个值，在该值之前的所有数字将被拼写为文字形式：

```php
$number = Number::spell(5, until: 10);

// five

$number = Number::spell(10, until: 10);

// 10
```

<a name="method-number-spell-ordinal"></a>
#### `Number::spellOrdinal()` {.collection-method}

`Number::spellOrdinal` 方法以文字形式的字符串返回数字的序数表示：

```php
use Illuminate\Support\Number;

$number = Number::spellOrdinal(1);

// first

$number = Number::spellOrdinal(2);

// second

$number = Number::spellOrdinal(21);

// twenty-first
```

<a name="method-number-trim"></a>
#### `Number::trim()` {.collection-method}

`Number::trim` 方法会移除给定数字中小数点后多余的尾随零：

```php
use Illuminate\Support\Number;

$number = Number::trim(12.0);

// 12

$number = Number::trim(12.30);

// 12.3
```

<a name="method-number-use-locale"></a>
#### `Number::useLocale()` {.collection-method}

`Number::useLocale` 方法在全局范围内设置默认的数字区域设置（locale），这将影响随后对 `Number` 类方法的调用中数字和货币的格式化方式：

```php
use Illuminate\Support\Number;

/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    Number::useLocale('de');
}
```

<a name="method-number-with-locale"></a>
#### `Number::withLocale()` {.collection-method}

`Number::withLocale` 方法使用指定的区域设置执行给定的闭包，并在回调执行完成后恢复原始的区域设置：

```php
use Illuminate\Support\Number;

$number = Number::withLocale('de', function () {
    return Number::format(1500);
});
```

<a name="method-number-use-currency"></a>
#### `Number::useCurrency()` {.collection-method}

`Number::useCurrency` 方法在全局范围内设置默认的数字货币，这将影响随后对 `Number` 类方法的调用中货币的格式化方式：

```php
use Illuminate\Support\Number;

/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    Number::useCurrency('GBP');
}
```

<a name="method-number-with-currency"></a>
#### `Number::withCurrency()` {.collection-method}

`Number::withCurrency` 方法使用指定的货币执行给定的闭包，并在回调执行完成后恢复原来的货币：

```php
use Illuminate\Support\Number;

$number = Number::withCurrency('GBP', function () {
    // ...
});
```

<a name="paths"></a>
## 路径

<a name="method-app-path"></a>
#### `app_path()` {.collection-method}

`app_path` 函数返回应用程序 `app` 目录的完全限定路径。你也可以使用 `app_path` 函数生成相对于应用目录的某个文件的完全限定路径：

```php
$path = app_path();

$path = app_path('Http/Controllers/Controller.php');
```

<a name="method-base-path"></a>
#### `base_path()` {.collection-method}

`base_path` 函数返回应用程序根目录的完全限定路径。你也可以使用 `base_path` 函数生成相对于项目根目录的某个文件的完全限定路径：

```php
$path = base_path();

$path = base_path('vendor/bin');
```

<a name="method-config-path"></a>
#### `config_path()` {.collection-method}

`config_path` 函数返回应用程序 `config` 目录的完全限定路径。你也可以使用 `config_path` 函数生成应用程序配置目录中某个文件的完全限定路径：

```php
$path = config_path();

$path = config_path('app.php');
```

<a name="method-database-path"></a>
#### `database_path()` {.collection-method}

`database_path` 函数返回应用程序 `database` 目录的完全限定路径。你也可以使用 `database_path` 函数生成数据库目录中某个文件的完全限定路径：

```php
$path = database_path();

$path = database_path('factories/UserFactory.php');
```

<a name="method-lang-path"></a>
#### `lang_path()` {.collection-method}

`lang_path` 函数返回应用程序 `lang` 目录的完全限定路径。你也可以使用 `lang_path` 函数生成该目录中某个文件的完全限定路径：

```php
$path = lang_path();

$path = lang_path('en/messages.php');
```

> [!NOTE]
> 默认情况下，Laravel 应用程序骨架并不包含 `lang` 目录。如果你希望自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令将它们发布出来。

<a name="method-public-path"></a>
#### `public_path()` {.collection-method}

`public_path` 函数返回应用程序 `public` 目录的完全限定路径。你也可以使用 `public_path` 函数生成 public 目录中某个文件的完全限定路径：

```php
$path = public_path();

$path = public_path('css/app.css');
```

<a name="method-resource-path"></a>
#### `resource_path()` {.collection-method}

`resource_path` 函数返回应用程序 `resources` 目录的完全限定路径。你也可以使用 `resource_path` 函数生成 resources 目录中某个文件的完全限定路径：

```php
$path = resource_path();

$path = resource_path('sass/app.scss');
```

<a name="method-storage-path"></a>
#### `storage_path()` {.collection-method}

`storage_path` 函数返回应用程序 `storage` 目录的完全限定路径。你也可以使用 `storage_path` 函数生成 storage 目录中某个文件的完全限定路径：

```php
$path = storage_path();

$path = storage_path('app/file.txt');
```

<a name="urls"></a>
## URLs

<a name="method-action"></a>
#### `action()` {.collection-method}

`action` 函数为给定的控制器操作生成一个 URL：

```php
use App\Http\Controllers\HomeController;

$url = action([HomeController::class, 'index']);
```

如果该方法接收路由参数，你可以将它们作为第二个参数传递给该方法：

```php
$url = action([UserController::class, 'profile'], ['id' => 1]);
```

<a name="method-asset"></a>
#### `asset()` {.collection-method}

`asset` 函数使用当前请求的协议（HTTP 或 HTTPS）为一个资源生成 URL：

```php
$url = asset('img/photo.jpg');
```

你可以通过在 `.env` 文件中设置 `ASSET_URL` 变量来配置资源 URL 的主机。这在你将资源托管在诸如 Amazon S3 或其他 CDN 等外部服务上时非常有用：

```php
// ASSET_URL=http://example.com/assets

$url = asset('img/photo.jpg'); // http://example.com/assets/img/photo.jpg
```

<a name="method-route"></a>
#### `route()` {.collection-method}

`route` 函数为给定的 [命名路由](/docs/{{version}}/routing#named-routes) 生成一个 URL：

```php
$url = route('route.name');
```

如果该路由接收参数，你可以将它们作为第二个参数传递给该函数：

```php
$url = route('route.name', ['id' => 1]);
```

默认情况下，`route` 函数会生成一个绝对 URL。如果你希望生成相对 URL，可以将 `false` 作为第三个参数传递给该函数：

```php
$url = route('route.name', ['id' => 1], false);
```

<a name="method-secure-asset"></a>
#### `secure_asset()` {.collection-method}

`secure_asset` 函数使用 HTTPS 为一个资源生成 URL：

```php
$url = secure_asset('img/photo.jpg');
```

<a name="method-secure-url"></a>
#### `secure_url()` {.collection-method}

`secure_url` 函数为给定的路径生成一个完全限定的 HTTPS URL。你可以在该函数的第二个参数中传递额外的 URL 片段：

```php
$url = secure_url('user/profile');

$url = secure_url('user/profile', [1]);
```

<a name="method-to-action"></a>
#### `to_action()` {.collection-method}

`to_action` 函数为指定的控制器动作生成 [HTTP 重定向响应](/docs/{{version}}/responses#redirects)：

```php
use App\Http\Controllers\UserController;

return to_action([UserController::class, 'show'], ['user' => 1]);
```

如有需要，可以将重定向响应的 HTTP 状态码和额外的响应标头作为 `to_action` 方法的第三个和第四个参数传入：

```php
return to_action(
    [UserController::class, 'show'],
    ['user' => 1],
    302,
    ['X-Framework' => 'Laravel']
);
```

<a name="method-to-route"></a>
#### `to_route()` {.collection-method}

`to_route` 函数为给定的 [命名路由](/docs/{{version}}/routing#named-routes) 生成一个 [重定向 HTTP 响应](/docs/{{version}}/responses#redirects)：

```php
return to_route('users.show', ['user' => 1]);
```

如有需要，你可以将应分配给该重定向的 HTTP 状态码以及任何额外的响应头，作为第三个和第四个参数传递给 `to_route` 方法：

```php
return to_route('users.show', ['user' => 1], 302, ['X-Framework' => 'Laravel']);
```

<a name="method-uri"></a>
#### `uri()` {.collection-method}

`uri` 函数为给定的 URI 生成一个 [流式（fluent）URI 实例](#uri)：

```php
$uri = uri('https://example.com')
    ->withPath('/users')
    ->withQuery(['page' => 1]);
```

如果传递给 `uri` 函数的是一个包含可调用控制器和方法对的数组，该函数将为该控制器方法的路由路径创建一个 `Uri` 实例：

```php
use App\Http\Controllers\UserController;

$uri = uri([UserController::class, 'show'], ['user' => $user]);
```

如果该控制器是可调用的（invokable），你只需提供控制器类名即可：

```php
use App\Http\Controllers\UserIndexController;

$uri = uri(UserIndexController::class);
```

如果传递给 `uri` 函数的值与某个 [命名路由](/docs/{{version}}/routing#named-routes) 的名称匹配，则会为该路由的路径生成一个 `Uri` 实例：

```php
$uri = uri('users.show', ['user' => $user]);
```

<a name="method-url"></a>
#### `url()` {.collection-method}

`url` 函数为指定路径生成完整的 URL：

```php
$url = url('user/profile');

$url = url('user/profile', [1]);
```

如果未提供路径，则会返回一个 `Illuminate\Routing\UrlGenerator` 实例：

```php
$current = url()->current();

$full = url()->full();

$previous = url()->previous();
```

有关使用 `url` 函数的更多信息，请参阅 [URL 生成文档](/docs/{{version}}/urls#generating-urls)。

<a name="miscellaneous"></a>
## 其他

<a name="method-abort"></a>
#### `abort()` {.collection-method}

`abort` 函数会抛出一个 [HTTP 异常](/docs/{{version}}/errors#http-exceptions)，该异常将由 [异常处理器](/docs/{{version}}/errors#handling-exceptions) 进行渲染：

```php
abort(403);
```

你也可以提供该异常的消息以及应发送到浏览器的自定义 HTTP 响应头：

```php
abort(403, 'Unauthorized.', $headers);
```

<a name="method-abort-if"></a>
#### `abort_if()` {.collection-method}

`abort_if` 函数在给定的布尔表达式计算结果为 `true` 时抛出一个 HTTP 异常：

```php
abort_if(! Auth::user()->isAdmin(), 403);
```

与 `abort` 方法一样，你也可以将异常的响应文本作为第三个参数传递给该函数，并将自定义响应头数组作为第四个参数传递给该函数。

<a name="method-abort-unless"></a>
#### `abort_unless()` {.collection-method}

`abort_unless` 函数在给定的布尔表达式计算结果为 `false` 时抛出一个 HTTP 异常：

```php
abort_unless(Auth::user()->isAdmin(), 403);
```

与 `abort` 方法一样，你也可以将异常的响应文本作为第三个参数传递给该函数，并将自定义响应头数组作为第四个参数传递给该函数。

<a name="method-app"></a>
#### `app()` {.collection-method}

`app` 函数返回 [服务容器](/docs/{{version}}/container) 实例：

```php
$container = app();
```

你可以传递一个类名或接口名，以便从容器中解析它：

```php
$api = app('HelpSpot\API');
```

<a name="method-auth"></a>
#### `auth()` {.collection-method}

`auth` 函数返回一个 [认证器](/docs/{{version}}/authentication) 实例。你可以将其作为 `Auth` 门面的替代方案来使用：

```php
$user = auth()->user();
```

如有需要，你可以指定要访问的守卫实例：

```php
$user = auth('admin')->user();
```

<a name="method-back"></a>
#### `back()` {.collection-method}

`back` 函数生成一个指向用户上一个位置的 [重定向 HTTP 响应](/docs/{{version}}/responses#redirects)：

```php
return back($status = 302, $headers = [], $fallback = '/');

return back();
```

<a name="method-bcrypt"></a>
#### `bcrypt()` {.collection-method}

`bcrypt` 函数使用 Bcrypt 对给定的值进行 [哈希处理](/docs/{{version}}/hashing)。你可以将该函数作为 `Hash` 门面的替代方案来使用：

```php
$password = bcrypt('my-secret-password');
```

<a name="method-blank"></a>
#### `blank()` {.collection-method}

`blank` 函数用于判断给定的值是否为「空白」：

```php
blank('');
blank('   ');
blank(null);
blank(collect());

// true

blank(0);
blank(true);
blank(false);

// false
```

关于 `blank` 的相反判断，请参阅 [filled](#method-filled) 方法。

<a name="method-broadcast"></a>
#### `broadcast()` {.collection-method}

`broadcast` 函数将给定的 [事件](/docs/{{version}}/events) [广播](/docs/{{version}}/broadcasting) 给其监听器：

```php
broadcast(new UserRegistered($user));

broadcast(new UserRegistered($user))->toOthers();
```

<a name="method-broadcast-if"></a>
#### `broadcast_if()` {.collection-method}

当给定的布尔表达式求值为 `true` 时，`broadcast_if` 函数会将指定的 [事件](/docs/{{version}}/events) [广播](/docs/{{version}}/broadcasting) 给其监听器：

```php
broadcast_if($user->isActive(), new UserRegistered($user));

broadcast_if($user->isActive(), new UserRegistered($user))->toOthers();
```

<a name="method-broadcast-unless"></a>
#### `broadcast_unless()` {.collection-method}

当给定的布尔表达式求值为 `false` 时，`broadcast_unless` 函数会将指定的 [事件](/docs/{{version}}/events) [广播](/docs/{{version}}/broadcasting) 给其监听器：

```php
broadcast_unless($user->isBanned(), new UserRegistered($user));

broadcast_unless($user->isBanned(), new UserRegistered($user))->toOthers();
```

<a name="method-cache"></a>
#### `cache()` {.collection-method}

`cache` 函数可用于从 [缓存](/docs/{{version}}/cache) 中获取值。如果给定的键在缓存中不存在，则会返回一个可选的默认值：

```php
$value = cache('key');

$value = cache('key', 'default');
```

你可以通过向该函数传递一个由键 / 值对组成的数组来向缓存中添加项目。你还应传递缓存值应被视为有效的秒数或持续时间：

```php
cache(['key' => 'value'], 300);

cache(['key' => 'value'], now()->plus(seconds: 10));
```

<a name="method-class-uses-recursive"></a>
#### `class_uses_recursive()` {.collection-method}

`class_uses_recursive` 函数返回某个类所使用的所有 trait，包括其所有父类所使用的 trait：

```php
$traits = class_uses_recursive(App\Models\User::class);
```

<a name="method-collect"></a>
#### `collect()` {.collection-method}

`collect` 函数从给定的值创建一个 [集合](/docs/{{version}}/collections) 实例：

```php
$collection = collect(['Taylor', 'Abigail']);
```

<a name="method-config"></a>
#### `config()` {.collection-method}

`config` 函数获取某个 [配置](/docs/{{version}}/configuration) 变量的值。配置值可以使用「点」语法来访问，其中包含你希望访问的文件名和选项。如果配置选项不存在，可以指定一个默认值并在此情况下返回：

```php
$value = config('app.timezone');

$value = config('app.timezone', $default);
```

你可以通过传递一个由键 / 值对组成的数组在运行时设置配置变量。不过请注意，该函数只会影响当前请求的配置值，并不会更新实际的配置文件中的值：

```php
config(['app.debug' => true]);
```

<a name="method-context"></a>
#### `context()` {.collection-method}

`context` 函数从 [当前上下文](/docs/{{version}}/context) 中获取一个值。如果上下文键不存在，可以指定一个默认值并在此情况下返回：

```php
$value = context('trace_id');

$value = context('trace_id', $default);
```

你可以通过传递一个由键 / 值对组成的数组来设置上下文值：

```php
use Illuminate\Support\Str;

context(['trace_id' => Str::uuid()->toString()]);
```

<a name="method-cookie"></a>
#### `cookie()` {.collection-method}

`cookie` 函数创建一个新的 [Cookie](/docs/{{version}}/requests#cookies) 实例：

```php
$cookie = cookie('name', 'value', $minutes);
```

<a name="method-csrf-field"></a>
#### `csrf_field()` {.collection-method}

`csrf_field` 函数生成一个包含 CSRF 令牌值的 HTML `hidden` 输入字段。例如，使用 [Blade 语法](/docs/{{version}}/blade)：

```blade
{{ csrf_field() }}
```

<a name="method-csrf-token"></a>
#### `csrf_token()` {.collection-method}

`csrf_token` 函数获取当前 CSRF 令牌的值：

```php
$token = csrf_token();
```

<a name="method-decrypt"></a>
#### `decrypt()` {.collection-method}

`decrypt` 函数 [解密](/docs/{{version}}/encryption) 给定的值。可以使用此函数代替 `Crypt` 门面：

```php
$password = decrypt($value);
```

有关 `decrypt` 的逆操作，请参阅 [encrypt](#method-encrypt) 函数。

<a name="method-dd"></a>
#### `dd()` {.collection-method}

`dd` 函数输出（dump）给定的变量并终止脚本的执行：

```php
dd($value);

dd($value1, $value2, $value3, ...);
```

如果你不希望中断脚本的执行，请改用 [dump](#method-dump) 函数。

<a name="method-dispatch"></a>
#### `dispatch()` {.collection-method}

`dispatch` 函数将给定的 [任务（job）](/docs/{{version}}/queues#creating-jobs) 推送到 Laravel 的 [任务队列](/docs/{{version}}/queues) 中：

```php
dispatch(new App\Jobs\SendEmails);
```

<a name="method-dispatch-sync"></a>
#### `dispatch_sync()` {.collection-method}

`dispatch_sync` 函数将给定的任务推送到 [同步（sync）](/docs/{{version}}/queues#synchronous-dispatching) 队列中，以便立即处理：

```php
dispatch_sync(new App\Jobs\SendEmails);
```

<a name="method-dump"></a>
#### `dump()` {.collection-method}

`dump` 函数用于输出给定的变量：

```php
dump($value);

dump($value1, $value2, $value3, ...);
```

如果你希望在输出变量后停止脚本的执行，请改用 [dd](#method-dd) 函数。

<a name="method-encrypt"></a>
#### `encrypt()` {.collection-method}

`encrypt` 函数 [加密](/docs/{{version}}/encryption) 给定的值。可以使用此函数代替 `Crypt` 门面：

```php
$secret = encrypt('my-secret-value');
```

有关 `encrypt` 的逆操作，请参阅 [decrypt](#method-decrypt) 函数。

<a name="method-env"></a>
#### `env()` {.collection-method}

`env` 函数用于获取[环境变量](/docs/{{version}}/configuration#environment-configuration)的值，或者在环境变量不存在时返回一个默认值：

```php
$env = env('APP_ENV');

$env = env('APP_ENV', 'production');
```

> [!WARNING]
> 如果你在部署过程中执行了 `config:cache` 命令，请确保你只在配置文件中调用 `env` 函数。一旦配置被缓存，`.env` 文件将不会被加载，所有对 `env` 函数的调用都将返回 `null`。

<a name="method-event"></a>
#### `event()` {.collection-method}

`event` 函数会将给定的[事件](/docs/{{version}}/events)分发给其监听器：

```php
event(new UserRegistered($user));
```

<a name="method-fake"></a>
#### `fake()` {.collection-method}

`fake` 函数从容器中解析一个 [Faker](https://github.com/FakerPHP/Faker) 单例，这在创建模型工厂、数据库填充、测试以及原型视图中的虚假数据时非常有用：

```blade
@for ($i = 0; $i < 10; $i++)
    <dl>
        <dt>Name</dt>
        <dd>{{ fake()->name() }}</dd>

        <dt>Email</dt>
        <dd>{{ fake()->unique()->safeEmail() }}</dd>
    </dl>
@endfor
```

默认情况下，`fake` 函数将使用 `config/app.php` 配置文件中的 `app.faker_locale` 配置选项。通常，该配置选项是通过 `APP_FAKER_LOCALE` 环境变量来设置的。你也可以通过向 `fake` 函数传递参数来指定语言环境。每种语言环境都会解析为一个独立的单例：

```php
fake('nl_NL')->name();
```

<a name="method-filled"></a>
#### `filled()` {.collection-method}

`filled` 函数用于判断给定的值是否不是「空白（blank）」：

```php
filled(0);
filled(true);
filled(false);

// true

filled('');
filled('   ');
filled(null);
filled(collect());

// false
```

`filled` 的反向判断请参见 [blank](#method-blank) 方法。

<a name="method-info"></a>
#### `info()` {.collection-method}

`info` 函数会将信息写入应用程序的[日志](/docs/{{version}}/logging)中：

```php
info('Some helpful information!');
```

也可以向该函数传递一个包含上下文数据的数组：

```php
info('User login attempt failed.', ['id' => $user->id]);
```

<a name="method-literal"></a>
#### `literal()` {.collection-method}

`literal` 函数使用给定的具名参数作为属性，创建一个新的 [stdClass](https://www.php.net/manual/en/class.stdclass.php) 实例：

```php
$obj = literal(
    name: 'Joe',
    languages: ['PHP', 'Ruby'],
);

$obj->name; // 'Joe'
$obj->languages; // ['PHP', 'Ruby']
```

<a name="method-logger"></a>
#### `logger()` {.collection-method}

`logger` 函数可用于向[日志](/docs/{{version}}/logging)中写入一条 `debug` 级别的消息：

```php
logger('Debug message');
```

也可以向该函数传递一个包含上下文数据的数组：

```php
logger('User has logged in.', ['id' => $user->id]);
```

如果在调用该函数时未传入任何值，则会返回一个 [logger](/docs/{{version}}/logging) 实例：

```php
logger()->error('You are not allowed here.');
```

<a name="method-method-field"></a>
#### `method_field()` {.collection-method}

`method_field` 函数会生成一个 HTML 的 `hidden` 输入字段，其中包含表单 HTTP 动词的伪造（spoofed）值。例如，使用 [Blade 语法](/docs/{{version}}/blade)：

```blade
<form method="POST">
    {{ method_field('DELETE') }}
</form>
```

<a name="method-now"></a>
#### `now()` {.collection-method}

`now` 函数会为当前时间创建一个新的 `Illuminate\Support\Carbon` 实例：

```php
$now = now();
```

<a name="method-old"></a>
#### `old()` {.collection-method}

`old` 函数用于[获取](/docs/{{version}}/requests#retrieving-input)闪存到 session 中的[旧输入值](/docs/{{version}}/requests#old-input)：

```php
$value = old('value');

$value = old('value', 'default');
```

由于传递给 `old` 函数的第二个参数（「默认值」）通常是一个 Eloquent 模型的属性，Laravel 允许你直接将整个 Eloquent 模型作为第二个参数传入 `old` 函数。在这种情况下，Laravel 会假定传给 `old` 函数的第一个参数是应当作为「默认值」的 Eloquent 属性名称：

```blade
{{ old('name', $user->name) }}

// 等价于...

{{ old('name', $user) }}
```

<a name="method-once"></a>
#### `once()` {.collection-method}

`once` 函数会执行给定的回调，并在一次请求的生命周期内将结果缓存到内存中。之后任何使用相同回调再次调用 `once` 函数时，都会返回之前缓存的结果：

```php
function random(): int
{
    return once(function () {
        return random_int(1, 1000);
    });
}

random(); // 123
random(); // 123 (cached result)
random(); // 123 (cached result)
```

当 `once` 函数在对象实例内部执行时，缓存的结果将只对该对象实例唯一：

```php
<?php

class NumberService
{
    public function all(): array
    {
        return once(fn () => [1, 2, 3]);
    }
}

$service = new NumberService;

$service->all();
$service->all(); // (cached result)

$secondService = new NumberService;

$secondService->all();
$secondService->all(); // (cached result)
```
<a name="method-optional"></a>
#### `optional()` {.collection-method}

`optional` 函数接受任意参数，并允许你访问该对象的属性或调用其方法。如果给定的对象为 `null`，则访问属性或调用方法时会返回 `null`，而不会引发错误：

```php
return optional($user->address)->street;

{!! old('name', optional($user)->name) !!}
```

`optional` 函数还可以接受一个闭包作为第二个参数。当作为第一个参数传入的值不为 `null` 时，该闭包将会被调用：

```php
return optional(User::find($id), function (User $user) {
    return $user->name;
});
```

<a name="method-policy"></a>
#### `policy()` {.collection-method}

`policy` 方法用于获取指定类的一个 [policy](/docs/{{version}}/authorization#creating-policies) 实例：

```php
$policy = policy(App\Models\User::class);
```

<a name="method-redirect"></a>
#### `redirect()` {.collection-method}

`redirect` 函数会返回一个[重定向 HTTP 响应](/docs/{{version}}/responses#redirects)，如果在调用时未传入任何参数，则会返回重定向器（redirector）实例：

```php
return redirect($to = null, $status = 302, $headers = [], $secure = null);

return redirect('/home');

return redirect()->route('route.name');
```

<a name="method-report"></a>
#### `report()` {.collection-method}

`report` 函数会使用你的[异常处理器](/docs/{{version}}/errors#handling-exceptions)来上报一个异常：

```php
report($e);
```

`report` 函数同样接受一个字符串作为参数。当向该函数传入字符串时，函数会使用该字符串作为异常消息来创建一个异常：

```php
report('Something went wrong.');
```

<a name="method-report-if"></a>
#### `report_if()` {.collection-method}

当给定的条件为 `true` 时，`report_if` 函数会使用你的[异常处理器](/docs/{{version}}/errors#handling-exceptions)来上报一个异常：

```php
report_if($shouldReport, $e);

report_if($shouldReport, 'Something went wrong.');
```

<a name="method-report-unless"></a>
#### `report_unless()` {.collection-method}

当给定的条件为 `false` 时，`report_unless` 函数会使用你的[异常处理器](/docs/{{version}}/errors#handling-exceptions)来上报一个异常：

```php
report_unless($reportingDisabled, $e);

report_unless($reportingDisabled, 'Something went wrong.');
```

<a name="method-request"></a>
#### `request()` {.collection-method}

`request` 函数会返回当前的[请求](/docs/{{version}}/requests)实例，或者获取当前请求中的某个输入字段的值：

```php
$request = request();

$value = request('key', $default);
```

<a name="method-rescue"></a>
#### `rescue()` {.collection-method}

`rescue` 函数会执行给定的闭包，并捕获执行过程中发生的任何异常。所有捕获的异常都会发送到你的[异常处理器](/docs/{{version}}/errors#handling-exceptions)；但是请求会继续处理：

```php
return rescue(function () {
    return $this->method();
});
```

你也可以向 `rescue` 函数传递第二个参数。该参数将在执行闭包时发生异常时作为「默认值」返回：

```php
return rescue(function () {
    return $this->method();
}, false);

return rescue(function () {
    return $this->method();
}, function () {
    return $this->failure();
});
```

可以向 `rescue` 函数提供一个 `report` 参数，用于确定异常是否应该通过 `report` 函数上报：

```php
return rescue(function () {
    return $this->method();
}, report: function (Throwable $throwable) {
    return $throwable instanceof InvalidArgumentException;
});
```

<a name="method-resolve"></a>
#### `resolve()` {.collection-method}

`resolve` 函数使用[服务容器](/docs/{{version}}/container)将给定的类或接口名称解析为一个实例：

```php
$api = resolve('HelpSpot\API');
```

<a name="method-response"></a>
#### `response()` {.collection-method}

`response` 函数会创建一个[响应](/docs/{{version}}/responses)实例，或者获取响应工厂的实例：

```php
return response('Hello World', 200, $headers);

return response()->json(['foo' => 'bar'], 200, $headers);
```

<a name="method-retry"></a>
#### `retry()` {.collection-method}

`retry` 函数会尝试执行给定的回调，直到达到指定的最大尝试次数。如果回调没有抛出异常，则返回其返回值。如果回调抛出异常，则会自动重试。如果超过最大尝试次数，则会抛出异常：

```php
return retry(5, function () {
    // 尝试 5 次，每次尝试之间休眠 100 毫秒...
}, 100);
```

休眠时长也可以传入 `CarbonInterval` 实例：

```php
use function Illuminate\Support\seconds;

return retry(5, function () {
    // 尝试 5 次，每次尝试之间休眠 5 秒...
}, seconds(5));
```

如果你希望手动计算两次尝试之间需要休眠的毫秒数，可以将一个闭包作为第三个参数传递给 `retry` 函数：

```php
use Exception;

return retry(5, function () {
    // ...
}, function (int $attempt, Exception $exception) {
    return $attempt * 100;
});
```

为了方便起见，你可以将一个数组作为第一个参数传递给 `retry` 函数。该数组将用于确定后续每次尝试之间需要休眠的毫秒数：

```php
return retry([100, 200], function () {
    // 第一次重试前休眠 100 毫秒，第二次重试前休眠 200 毫秒...
});
```

如果只希望在特定条件下进行重试，可以将一个闭包作为第四个参数传递给 `retry` 函数：

```php
use App\Exceptions\TemporaryException;
use Exception;

return retry(5, function () {
    // ...
}, 100, function (Exception $exception) {
    return $exception instanceof TemporaryException;
});
```

<a name="method-session"></a>
#### `session()` {.collection-method}

`session` 函数可用于获取或设置 [会话](/docs/{{version}}/session) 的值：

```php
$value = session('key');
```

你可以通过向该函数传递一个键 / 值对数组来设置值：

```php
session(['chairs' => 7, 'instruments' => 3]);
```

如果未向该函数传递任何值，则将返回会话存储实例：

```php
$value = session()->get('key');

session()->put('key', $value);
```

<a name="method-tap"></a>
#### `tap()` {.collection-method}

`tap` 函数接收两个参数：一个任意的 `$value` 和一个闭包。`$value` 会被传递给该闭包，然后由 `tap` 函数返回。闭包的返回值并不重要：

```php
$user = tap(User::first(), function (User $user) {
    $user->name = 'Taylor';

    $user->save();
});
```

如果没有向 `tap` 函数传递闭包，你可以在给定的 `$value` 上调用任意方法。无论你调用的方法在其定义中实际返回什么，该方法的返回值始终都会是 `$value`。例如，Eloquent 的 `update` 方法通常返回一个整数。然而，我们可以通过 `tap` 函数链式调用 `update` 方法：强制该方法返回模型本身：

```php
$user = tap($user)->update([
    'name' => $name,
    'email' => $email,
]);
```

要向一个类中添加 `tap` 方法：你可以将 `Illuminate\Support\Traits\Tappable` trait 添加到该类中。该 trait 的 `tap` 方法只接收一个 `Closure` 作为参数。对象实例本身会被传递给该闭包，然后由 `tap` 方法返回：

```php
return $user->tap(function (User $user) {
    // ...
});
```

<a name="method-throw-if"></a>
#### `throw_if()` {.collection-method}

如果给定的布尔表达式计算结果为 `true`，`throw_if` 函数将抛出指定的异常：

```php
throw_if(! Auth::user()->isAdmin(), AuthorizationException::class);

throw_if(
    ! Auth::user()->isAdmin(),
    AuthorizationException::class,
    'You are not allowed to access this page.'
);
```

<a name="method-throw-unless"></a>
#### `throw_unless()` {.collection-method}

如果给定的布尔表达式计算结果为 `false`，`throw_unless` 函数将抛出指定的异常：

```php
throw_unless(Auth::user()->isAdmin(), AuthorizationException::class);

throw_unless(
    Auth::user()->isAdmin(),
    AuthorizationException::class,
    'You are not allowed to access this page.'
);
```

<a name="method-today"></a>
#### `today()` {.collection-method}

`today` 函数会为当前日期创建一个新的 `Illuminate\Support\Carbon` 实例：

```php
$today = today();
```

<a name="method-trait-uses-recursive"></a>
#### `trait_uses_recursive()` {.collection-method}

`trait_uses_recursive` 函数返回某个 trait 所使用的所有 trait：

```php
$traits = trait_uses_recursive(\Illuminate\Notifications\Notifiable::class);
```

<a name="method-transform"></a>
#### `transform()` {.collection-method}

如果给定的值不是 [blank](#method-blank)，`transform` 函数会对该值执行一个闭包，并返回该闭包的返回值：

```php
$callback = function (int $value) {
    return $value * 2;
};

$result = transform(5, $callback);

// 10
```

你可以将一个默认值或闭包作为该函数的第三个参数传入。如果给定的值是 blank，则会返回该值：

```php
$result = transform(null, $callback, 'The value is blank');

// The value is blank
```

<a name="method-validator"></a>
#### `validator()` {.collection-method}

`validator` 函数会使用给定的参数创建一个新的 [验证器](/docs/{{version}}/validation) 实例。你可以将其作为 `Validator` 门面（facade）的替代方案来使用：

```php
$validator = validator($data, $rules, $messages);
```

<a name="method-value"></a>
#### `value()` {.collection-method}

`value` 函数会返回传入的值。不过，如果你向该函数传递一个闭包，则会执行该闭包，并返回其返回值：

```php
$result = value(true);

// true

$result = value(function () {
    return false;
});

// false
```

你可以向 `value` 函数传递额外的参数。如果第一个参数是一个闭包，那么这些附加参数将作为参数传递给该闭包；否则它们将被忽略：

```php
$result = value(function (string $name) {
    return $name;
}, 'Taylor');

// 'Taylor'
```

<a name="method-view"></a>
#### `view()` {.collection-method}

`view` 函数用于获取一个 [视图](/docs/{{version}}/views) 实例：

```php
return view('auth.login');
```

<a name="method-with"></a>
#### `with()` {.collection-method}

`with` 函数会返回传入的值。如果向该函数传递一个闭包作为第二个参数，则会执行该闭包，并返回其返回值：

```php
$callback = function (mixed $value) {
    return is_numeric($value) ? $value * 2 : 0;
};

$result = with(5, $callback);

// 10

$result = with(null, $callback);

// 0

$result = with(5, null);

// 5
```

<a name="method-when"></a>
#### `when()` {.collection-method}

当给定的条件计算结果为 `true` 时，`when` 函数会返回传入的值；否则返回 `null`。如果向该函数传递一个闭包作为第二个参数，则会执行该闭包，并返回其返回值：

```php
$value = when(true, 'Hello World');

$value = when(true, fn () => 'Hello World');
```

`when` 函数主要用于有条件地渲染 HTML 属性：

```blade
<div {!! when($condition, 'wire:poll="calculate"') !!}>
    ...
</div>
```

<a name="other-utilities"></a>
## 其他工具

<a name="benchmarking"></a>
### 基准测试（Benchmarking）

有时你可能希望快速测试应用程序中某些部分的性能。在这种情况下，你可以使用 `Benchmark` 支持类来测量给定回调执行完成所需的毫秒数：

```php
<?php

use App\Models\User;
use Illuminate\Support\Benchmark;

Benchmark::dd(fn () => User::find(1)); // 0.1 ms

Benchmark::dd([
    'Scenario 1' => fn () => User::count(), // 0.5 ms
    'Scenario 2' => fn () => User::all()->count(), // 20.0 ms
]);
```

默认情况下，给定的回调只会执行一次（一次迭代），并且其耗时会显示在浏览器 / 控制台中。

如果希望多次调用某个回调，可以将该回调应执行的迭代次数作为方法的第二个参数指定。当回调被执行多次时，`Benchmark` 类将返回该回调在所有迭代中的平均执行时间（毫秒）：

```php
Benchmark::dd(fn () => User::count(), iterations: 10); // 0.5 ms
```

有时，你可能希望在对回调执行进行基准测试的同时，仍然获取该回调返回的值。`value` 方法会返回一个元组，其中包含回调返回的值以及执行该回调所花费的毫秒数：

```php
[$count, $duration] = Benchmark::value(fn () => User::count());
```

<a name="dates"></a>
### 日期和时间

Laravel 包含功能强大的日期和时间处理库 [Carbon](https://carbon.nesbot.com/guide/getting-started/introduction.html)。可以调用 `now` 函数创建新的 `Carbon` 实例，该函数在 Laravel 应用程序中全局可用：

```php
$now = now();
```

也可以通过 `Illuminate\Support\Carbon` 类创建新的 `Carbon` 实例：

```php
use Illuminate\Support\Carbon;

$now = Carbon::now();
```

Laravel 还为 `Carbon` 实例扩展了 `plus` 和 `minus` 方法：方便调整实例的日期和时间：

```php
return now()->plus(minutes: 5);
return now()->plus(hours: 8);
return now()->plus(weeks: 4);

return now()->minus(minutes: 5);
return now()->minus(hours: 8);
return now()->minus(weeks: 4);
```

有关 Carbon 及其功能的详细介绍，请参阅 [Carbon 官方文档](https://carbon.nesbot.com/guide/getting-started/introduction.html)。

<a name="interval-functions"></a>
#### 时间间隔函数

Laravel 还提供了 `milliseconds`、`seconds`、`minutes`、`hours`、`days`、`weeks`、`months` 和 `years` 函数，用于返回 `CarbonInterval` 实例。该类继承自 PHP 的 [DateInterval](https://www.php.net/manual/en/class.dateinterval.php) 类。这些函数可用于 Laravel 中任何接受 `DateInterval` 实例的地方：

```php
use Illuminate\Support\Facades\Cache;

use function Illuminate\Support\{minutes};

Cache::put('metrics', $metrics, minutes(10));
```

<a name="deferred-functions"></a>
### 延迟函数（Deferred Functions）

Laravel 的 [队列任务](/docs/{{version}}/queues) 可以将任务交给后台处理，但有时你只是希望延后执行一些简单任务，而无需配置或维护长期运行的队列工作进程。

延迟函数可以将闭包的执行推迟到 HTTP 响应发送给用户之后，让应用程序保持快速响应。要延后执行闭包，只需将其传给 `Illuminate\Support\defer` 函数：

```php
use App\Services\Metrics;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use function Illuminate\Support\defer;

Route::post('/orders', function (Request $request) {
    // 创建订单...

    defer(fn () => Metrics::reportOrder($order));

    return $order;
});
```

默认情况下，只有调用 `Illuminate\Support\defer` 的 HTTP 响应、Artisan 命令或队列任务成功完成后，延迟函数才会执行。因此，当请求返回 `4xx` 或 `5xx` HTTP 响应时，延迟函数不会执行。如果希望延迟函数始终执行，可以链式调用其 `always` 方法：

```php
defer(fn () => Metrics::reportOrder($order))->always();
```

> [!WARNING]
> 如果安装了 [Swoole PHP 扩展](https://www.php.net/manual/en/book.swoole.php)，Laravel 的 `defer` 函数可能与 Swoole 自带的全局 `defer` 函数冲突，导致 Web 服务器错误。请显式导入命名空间，确保调用 Laravel 的 `defer` 辅助函数：`use function Illuminate\Support\defer;`

<a name="cancelling-deferred-functions"></a>
#### 取消延迟函数（Cancelling Deferred Functions）

如果你需要在延迟函数执行之前将其取消，可以使用 `forget` 方法根据函数名称来取消该延迟函数。要为延迟函数命名，可以在调用 `Illuminate\Support\defer` 函数时提供第二个参数：

```php
defer(fn () => Metrics::report(), 'reportMetrics');

defer()->forget('reportMetrics');
```

<a name="disabling-deferred-functions-in-tests"></a>
#### 测试中禁用延迟函数

在编写测试时，禁用延迟函数可能会很有用。 你可以在测试中调用 `withoutDefer` 来让 Laravel 立即调用延迟函数：

```php tab=Pest
test('without defer', function () {
    $this->withoutDefer();

    // ...
});
```

```php tab=PHPUnit
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_without_defer(): void
    {
        $this->withoutDefer();

        // ...
    }
}
```

如果你想禁用测试用例中所有测试的延迟函数，你可以在 `TestCase` 类的`setUp` 方法中调用 `withoutDefer` 方法：

```php
<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    protected function setUp(): void// [tl! add:start]
    {
        parent::setUp();

        $this->withoutDefer();
    }// [tl! add:end]
}
```

<a name="lottery"></a>
### 抽奖机制（Lottery）

Laravel 的 `Lottery` 类可以用于根据给定的概率执行回调函数。当你只想对一部分传入请求执行代码时，这尤其有用：

```php
use Illuminate\Support\Lottery;

Lottery::odds(1, 20)
    ->winner(fn () => $user->won())
    ->loser(fn () => $user->lost())
    ->choose();
```

你可以将 Laravel 的 `Lottery` 类与其他 Laravel 功能结合使用。例如，你可能只想将一小部分慢查询报告给异常处理程序。而且，由于 `Lottery` 类是可调用的，我们可以将该类的实例传递给任何接受可调用对象的方法：

```php
use Carbon\CarbonInterval;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Lottery;

DB::whenQueryingForLongerThan(
    CarbonInterval::seconds(2),
    Lottery::odds(1, 100)->winner(fn () => report('Querying > 2 seconds.')),
);
```

<a name="testing-lotteries"></a>
#### 测试抽奖

Laravel 提供了一些简单的方法：使你可以轻松地测试应用程序中的抽奖（Lottery）调用：

```php
// 抽奖将始终获胜...
Lottery::alwaysWin();

// 抽奖将始终失败...
Lottery::alwaysLose();

// 抽奖先获胜，再失败，最后恢复正常行为...
Lottery::fix([true, false]);

// 抽奖将恢复正常行为...
Lottery::determineResultsNormally();
```

<a name="pipeline"></a>
### 管道（Pipeline）

Laravel 的 `Pipeline` 门面可以将给定输入依次传递给一组可调用的类、闭包或其他可调用对象，让每一步都有机会检查或修改输入，然后调用管道中的下一步：

```php
use Closure;
use App\Models\User;
use Illuminate\Support\Facades\Pipeline;

$user = Pipeline::send($user)
    ->through([
        function (User $user, Closure $next) {
            // ...

            return $next($user);
        },
        function (User $user, Closure $next) {
            // ...

            return $next($user);
        },
    ])
    ->then(fn (User $user) => $user);
```

如上所示，管道中的每个可调用类或闭包都会接收输入和一个 `$next` 闭包。调用 `$next` 闭包会执行管道中的下一个可调用对象，这与 [中间件](/docs/{{version}}/middleware) 非常相似。

当管道中的最后一个可调用对象调用 `$next` 闭包时，就会执行传给 `then` 方法的可调用对象。通常，它只需返回给定的输入。如果仅希望返回处理后的输入，可以直接使用 `thenReturn` 方法。

如前所述，管道不仅可以接收闭包，也可以接收可调用的类。如果提供类名，Laravel 会通过 [服务容器](/docs/{{version}}/container) 实例化该类，从而向类中注入依赖：

```php
$user = Pipeline::send($user)
    ->through([
        GenerateProfilePhoto::class,
        ActivateSubscription::class,
        SendWelcomeEmail::class,
    ])
    ->thenReturn();
```

可以在管道上调用 `withinTransaction` 方法：将管道中的所有步骤自动包裹在同一个数据库事务中：

```php
$user = Pipeline::send($user)
    ->withinTransaction()
    ->through([
        ProcessOrder::class,
        TransferFunds::class,
        UpdateInventory::class,
    ])
    ->thenReturn();
```

<a name="sleep"></a>
### 休眠（Sleep）

Laravel 的 `Sleep` 类是对 PHP 原生 `sleep` 和 `usleep` 函数的一个轻量级封装，在提供更强可测试性的同时，也暴露了一个对开发者友好的时间处理 API：

```php
use Illuminate\Support\Sleep;

$waiting = true;

while ($waiting) {
    Sleep::for(1)->second();

    $waiting = /* ... */;
}
```

`Sleep` 类提供了多种方法：允许你使用不同的时间单位进行操作：

```php
// 休眠后返回一个值...
$result = Sleep::for(1)->second()->then(fn () => 1 + 1);

// 当给定值为 true 时持续休眠...
Sleep::for(1)->second()->while(fn () => shouldKeepSleeping());

// 暂停执行 90 秒...
Sleep::for(1.5)->minutes();

// 暂停执行 2 秒...
Sleep::for(2)->seconds();

// 暂停执行 500 毫秒...
Sleep::for(500)->milliseconds();

// 暂停执行 5,000 微秒...
Sleep::for(5000)->microseconds();

// 暂停执行直到指定时间...
Sleep::until(now()->plus(minutes: 1));

// PHP 原生 sleep 函数的别名...
Sleep::sleep(2);

// PHP 原生 usleep 函数的别名...
Sleep::usleep(5000);
```

为了方便组合多个时间单位，你可以使用 `and` 方法：

```php
Sleep::for(1)->second()->and(10)->milliseconds();
```

<a name="testing-sleep"></a>
#### 测试 Sleep

在测试使用了 `Sleep` 类或 PHP 原生 sleep 函数的代码时，测试将会暂停执行。正如你所预期的那样，这会使你的测试套件明显变慢。例如，假设你正在测试下面的代码：

```php
$waiting = /* ... */;

$seconds = 1;

while ($waiting) {
    Sleep::for($seconds++)->seconds();

    $waiting = /* ... */;
}
```

通常情况下，测试这段代码将至少花费 1 秒。幸运的是，`Sleep` 类允许我们「伪造（fake）」睡眠行为，从而使测试套件保持快速：

```php tab=Pest
it('waits until ready', function () {
    Sleep::fake();

    // ...
});
```

```php tab=PHPUnit
public function test_it_waits_until_ready()
{
    Sleep::fake();

    // ...
}
```

当对 `Sleep` 类进行伪造（fake）时，实际的执行暂停将被绕过，从而使测试速度大幅提升。

一旦 `Sleep` 类被伪造，就可以对预期发生的「睡眠」行为进行断言。为了说明这一点，假设我们正在测试一段代码，该代码会暂停执行三次，并且每次暂停都会增加一秒。使用 `assertSequence` 方法：我们可以断言代码以正确的时间长度进行了「睡眠」，同时保持测试的高速度：

```php tab=Pest
it('checks if ready three times', function () {
    Sleep::fake();

    // ...

    Sleep::assertSequence([
        Sleep::for(1)->second(),
        Sleep::for(2)->seconds(),
        Sleep::for(3)->seconds(),
    ]);
});
```

```php tab=PHPUnit
public function test_it_checks_if_ready_three_times()
{
    Sleep::fake();

    // ...

    Sleep::assertSequence([
        Sleep::for(1)->second(),
        Sleep::for(2)->seconds(),
        Sleep::for(3)->seconds(),
    ]);
}
```

当然，在测试时，`Sleep` 类还提供了多种你可以使用的其他断言方法：

```php
use Carbon\CarbonInterval as Duration;
use Illuminate\Support\Sleep;

// 断言休眠被调用了 3 次...
Sleep::assertSleptTimes(3);

// 断言休眠的时长...
Sleep::assertSlept(function (Duration $duration): bool {
    return /* ... */;
}, times: 1);

// 断言从未调用 Sleep 类...
Sleep::assertNeverSlept();

// 断言即使调用了 Sleep，也没有暂停执行...
Sleep::assertInsomniac();
```

有时，在应用程序代码中每当发生一次伪造的睡眠时执行某个操作会很有用。为此，你可以向 `whenFakingSleep` 方法提供一个回调。在下面的示例中，我们使用 Laravel 的 [时间操作辅助函数](/docs/{{version}}/mocking#interacting-with-time)，在每次睡眠的持续时间内立即推进时间：

```php
use Carbon\CarbonInterval as Duration;

$this->freezeTime();

Sleep::fake();

Sleep::whenFakingSleep(function (Duration $duration) {
    // 模拟休眠时推进时间...
    $this->travel($duration->totalMilliseconds)->milliseconds();
});
```

由于推进时间是一个常见需求，`fake` 方法接受一个 `syncWithCarbon` 参数，用于在测试中睡眠时保持 Carbon 时间同步：

```php
Sleep::fake(syncWithCarbon: true);

$start = now();

Sleep::for(1)->second();

$start->diffForHumans(); // 1 second ago
```

Laravel 在内部只要需要暂停执行，就会使用 `Sleep` 类。例如，[retry](#method-retry) 辅助函数在睡眠时就使用了 `Sleep` 类，这使得在使用该辅助函数时具有更好的可测试性。

<a name="timebox"></a>
### 时间盒（Timebox）

Laravel 的 `Timebox` 类确保给定的回调始终在固定的时间内执行，即使其实际执行提前完成也是如此。这在密码学操作和用户身份验证检查中特别有用，因为攻击者可能会利用执行时间的差异来推断敏感信息。

如果执行时间超过了固定的持续时间，`Timebox` 将不会产生任何影响。开发者需要自行选择一个足够长的固定时间，以覆盖最坏情况下的场景。

`call` 方法接收一个闭包和一个以微秒为单位的时间限制，然后执行该闭包并等待直到达到时间限制：

```php
use Illuminate\Support\Timebox;

(new Timebox)->call(function ($timebox) {
    // ...
}, microseconds: 10000);
```

如果在闭包内部抛出了异常，该类将遵循已定义的延迟，并在延迟结束后重新抛出该异常。

<a name="uri"></a>
### URI

Laravel 的 `Uri` 类提供了一个方便且流畅的接口，用于创建和操作 URI。该类封装了底层 League URI 包所提供的功能，并与 Laravel 的路由系统无缝集成。

你可以使用静态方法轻松创建一个 `Uri` 实例：

```php
use App\Http\Controllers\UserController;
use App\Http\Controllers\InvokableController;
use Illuminate\Support\Uri;

// 从给定字符串生成 URI 实例...
$uri = Uri::of('https://example.com/path');

// 为路径、命名路由或控制器动作生成 URI 实例...
$uri = Uri::to('/dashboard');
$uri = Uri::route('users.show', ['user' => 1]);
$uri = Uri::signedRoute('users.show', ['user' => 1]);
$uri = Uri::temporarySignedRoute('user.index', now()->plus(minutes: 5));
$uri = Uri::action([UserController::class, 'index']);
$uri = Uri::action(InvokableController::class);

// 从当前请求 URL 生成 URI 实例...
$uri = $request->uri();
```

一旦你拥有了一个 URI 实例，就可以以流畅的方式对其进行修改：

```php
$uri = Uri::of('https://example.com')
    ->withScheme('http')
    ->withHost('test.com')
    ->withPort(8000)
    ->withPath('/users')
    ->withQuery(['page' => 2])
    ->withFragment('section-1');
```

<a name="inspecting-uris"></a>
#### 检查 URI

`Uri` 类还允许你轻松检查底层 URI 的各个组成部分：

```php
$scheme = $uri->scheme();
$authority = $uri->authority();
$host = $uri->host();
$port = $uri->port();
$path = $uri->path();
$segments = $uri->pathSegments();
$query = $uri->query();
$fragment = $uri->fragment();
```

<a name="manipulating-query-strings"></a>
#### 操作查询字符串

`Uri` 类提供了多种方法：可用于操作 URI 的查询字符串。`withQuery` 方法可用于将额外的查询字符串参数合并到现有的查询字符串中：

```php
$uri = $uri->withQuery(['sort' => 'name']);
```

`withQueryIfMissing` 方法可用于在给定键尚不存在于查询字符串中的情况下，将额外的查询字符串参数合并到现有的查询字符串中：

```php
$uri = $uri->withQueryIfMissing(['page' => 1]);
```

`replaceQuery` 方法可用于将现有查询字符串完全替换为新的查询字符串：

```php
$uri = $uri->replaceQuery(['page' => 1]);
```

`pushOntoQuery` 方法可以向值为数组的查询字符串参数中追加元素：

```php
$uri = $uri->pushOntoQuery('filter', ['active', 'pending']);
```

`withoutQuery` 方法可以移除查询字符串中的参数：

```php
$uri = $uri->withoutQuery(['page']);
```

<a name="generating-responses-from-uris"></a>
#### 从 URI 生成响应

`redirect` 方法可用于生成指向给定 URI 的 `RedirectResponse` 实例：

```php
$uri = Uri::of('https://example.com');

return $uri->redirect();
```

或者，你可以直接从路由或控制器操作返回 `Uri` 实例，这将自动生成重定向响应，指向返回的 URI：

```php
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Uri;

Route::get('/redirect', function () {
    return Uri::to('/index')
        ->withQuery(['sort' => 'name']);
});
```
