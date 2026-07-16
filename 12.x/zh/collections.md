# 集合

- [简介](#introduction)
  - [创建集合](#creating-collections)
  - [扩展集合](#extending-collections)
- [可用方法](#available-methods)
- [高阶消息](#higher-order-messages)
- [惰性集合](#lazy-collections)
  - [简介](#lazy-collection-introduction)
  - [创建惰性集合](#creating-lazy-collections)
  - [可枚举契约](#the-enumerable-contract)
  - [惰性集合方法](#lazy-collection-methods)

<a name="introduction"></a>
## 简介

`Illuminate\Support\Collection` 类为处理数据数组提供了一个流畅、便捷的封装。例如，查看下面的代码。我们使用 `collect` 辅助函数从数组创建一个新的集合实例，对每个元素运行 `strtoupper` 函数，然后移除所有空元素：

```php
$collection = collect(['Taylor', 'Abigail', null])->map(function (?string $name) {
    return strtoupper($name);
})->reject(function (string $name) {
    return empty($name);
});
```

如您所见，`Collection` 类允许您链式调用其方法以对底层数组执行流畅的映射和缩减。通常，集合是不可变的，这意味着每个 `Collection` 方法都会返回一个全新的 `Collection` 实例。

<a name="creating-collections"></a>
### 创建集合

如上所述，`collect` 辅助函数为给定数组返回一个新的 `Illuminate\Support\Collection` 实例。因此，创建一个集合非常简单：

```php
$collection = collect([1, 2, 3]);
```

您也可以使用 [make](#method-make) 和 [fromJson](#method-fromjson) 方法创建集合。

> [!NOTE]
> [Eloquent](/docs/laravel/12.x/eloquent) 查询的结果总是以 `Collection` 实例的形式返回。

<a name="extending-collections"></a>
### 扩展集合

集合是“可宏扩展的”，这允许您在运行时向 `Collection` 类添加额外的方法。`Illuminate\Support\Collection` 类的 `macro` 方法接受一个闭包，该闭包将在调用宏时执行。宏闭包可以通过 `$this` 访问集合的其他方法，就像它是集合类的真实方法一样。例如，以下代码向 `Collection` 类添加了一个 `toUpper` 方法：

```php
use Illuminate\Support\Collection;
use Illuminate\Support\Str;

Collection::macro('toUpper', function () {
    return $this->map(function (string $value) {
        return Str::upper($value);
    });
});

$collection = collect(['first', 'second']);

$upper = $collection->toUpper();

// ['FIRST', 'SECOND']
```

通常，您应该在[服务提供者](/docs/laravel/12.x/providers)的 `boot` 方法中声明集合宏。

<a name="macro-arguments"></a>
#### 宏参数

如果需要，您可以定义接受额外参数的宏：

```php
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Lang;

Collection::macro('toLocale', function (string $locale) {
    return $this->map(function (string $value) use ($locale) {
        return Lang::get($value, [], $locale);
    });
});

$collection = collect(['first', 'second']);

$translated = $collection->toLocale('es');
```

<a name="available-methods"></a>
## 可用方法

在集合文档的剩余大部分内容中，我们将讨论 `Collection` 类上可用的每个方法。请记住，所有这些方法都可以链式调用，以流畅地操作底层数组。此外，几乎每个方法都会返回一个新的 `Collection` 实例，允许您在需要时保留集合的原始副本：

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

<div class="collection-method-list" markdown="1">

[after](#method-after)
[all](#method-all)
[average](#method-average)
[avg](#method-avg)
[before](#method-before)
[chunk](#method-chunk)
[chunkWhile](#method-chunkwhile)
[collapse](#method-collapse)
[collapseWithKeys](#method-collapsewithkeys)
[collect](#method-collect)
[combine](#method-combine)
[concat](#method-concat)
[contains](#method-contains)
[containsOneItem](#method-containsoneitem)
[containsStrict](#method-containsstrict)
[count](#method-count)
[countBy](#method-countBy)
[crossJoin](#method-crossjoin)
[dd](#method-dd)
[diff](#method-diff)
[diffAssoc](#method-diffassoc)
[diffAssocUsing](#method-diffassocusing)
[diffKeys](#method-diffkeys)
[doesntContain](#method-doesntcontain)
[dot](#method-dot)
[dump](#method-dump)
[duplicates](#method-duplicates)
[duplicatesStrict](#method-duplicatesstrict)
[each](#method-each)
[eachSpread](#method-eachspread)
[ensure](#method-ensure)
[every](#method-every)
[except](#method-except)
[filter](#method-filter)
[first](#method-first)
[firstOrFail](#method-first-or-fail)
[firstWhere](#method-first-where)
[flatMap](#method-flatmap)
[flatten](#method-flatten)
[flip](#method-flip)
[forget](#method-forget)
[forPage](#method-forpage)
[fromJson](#method-fromjson)
[get](#method-get)
[groupBy](#method-groupby)
[has](#method-has)
[hasAny](#method-hasany)
[implode](#method-implode)
[intersect](#method-intersect)
[intersectUsing](#method-intersectusing)
[intersectAssoc](#method-intersectAssoc)
[intersectAssocUsing](#method-intersectassocusing)
[intersectByKeys](#method-intersectbykeys)
[isEmpty](#method-isempty)
[isNotEmpty](#method-isnotempty)
[join](#method-join)
[keyBy](#method-keyby)
[keys](#method-keys)
[last](#method-last)
[lazy](#method-lazy)
[macro](#method-macro)
[make](#method-make)
[map](#method-map)
[mapInto](#method-mapinto)
[mapSpread](#method-mapspread)
[mapToGroups](#method-maptogroups)
[mapWithKeys](#method-mapwithkeys)
[max](#method-max)
[median](#method-median)
[merge](#method-merge)
[mergeRecursive](#method-mergerecursive)
[min](#method-min)
[mode](#method-mode)
[multiply](#method-multiply)
[nth](#method-nth)
[only](#method-only)
[pad](#method-pad)
[partition](#method-partition)
[percentage](#method-percentage)
[pipe](#method-pipe)
[pipeInto](#method-pipeinto)
[pipeThrough](#method-pipethrough)
[pluck](#method-pluck)
[pop](#method-pop)
[prepend](#method-prepend)
[pull](#method-pull)
[push](#method-push)
[put](#method-put)
[random](#method-random)
[range](#method-range)
[reduce](#method-reduce)
[reduceSpread](#method-reduce-spread)
[reject](#method-reject)
[replace](#method-replace)
[replaceRecursive](#method-replacerecursive)
[reverse](#method-reverse)
[search](#method-search)
[select](#method-select)
[shift](#method-shift)
[shuffle](#method-shuffle)
[skip](#method-skip)
[skipUntil](#method-skipuntil)
[skipWhile](#method-skipwhile)
[slice](#method-slice)
[sliding](#method-sliding)
[sole](#method-sole)
[some](#method-some)
[sort](#method-sort)
[sortBy](#method-sortby)
[sortByDesc](#method-sortbydesc)
[sortDesc](#method-sortdesc)
[sortKeys](#method-sortkeys)
[sortKeysDesc](#method-sortkeysdesc)
[sortKeysUsing](#method-sortkeysusing)
[splice](#method-splice)
[split](#method-split)
[splitIn](#method-splitin)
[sum](#method-sum)
[take](#method-take)
[takeUntil](#method-takeuntil)
[takeWhile](#method-takewhile)
[tap](#method-tap)
[times](#method-times)
[toArray](#method-toarray)
[toJson](#method-tojson)
[transform](#method-transform)
[undot](#method-undot)
[union](#method-union)
[unique](#method-unique)
[uniqueStrict](#method-uniquestrict)
[unless](#method-unless)
[unlessEmpty](#method-unlessempty)
[unlessNotEmpty](#method-unlessnotempty)
[unwrap](#method-unwrap)
[value](#method-value)
[values](#method-values)
[when](#method-when)
[whenEmpty](#method-whenempty)
[whenNotEmpty](#method-whennotempty)
[where](#method-where)
[whereStrict](#method-wherestrict)
[whereBetween](#method-wherebetween)
[whereIn](#method-wherein)
[whereInStrict](#method-whereinstrict)
[whereInstanceOf](#method-whereinstanceof)
[whereNotBetween](#method-wherenotbetween)
[whereNotIn](#method-wherenotin)
[whereNotInStrict](#method-wherenotinstrict)
[whereNotNull](#method-wherenotnull)
[whereNull](#method-wherenull)
[wrap](#method-wrap)
[zip](#method-zip)

</div>

<a name="method-listing"></a>
## 方法列表

<style>
    .collection-method code {
        font-size: 14px;
    }

    .collection-method:not(.first-collection-method) {
        margin-top: 50px;
    }
</style>

<a name="method-after"></a>
#### `after()` {.collection-method .first-collection-method}

`after` 方法返回给定项之后的项。如果未找到给定项或该项是最后一项，则返回 `null`：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->after(3);

// 4

$collection->after(5);

// null
```

此方法使用"松散"比较搜索给定项，这意味着包含整数值的字符串将被视为等于相同值的整数。要使用"严格"比较，您可以向方法提供 `strict` 参数：

```php
collect([2, 4, 6, 8])->after('4', strict: true);

// null
```

或者，您可以提供自己的闭包来搜索通过给定真值测试的第一个项：

```php
collect([2, 4, 6, 8])->after(function (int $item, int $key) {
    return $item > 5;
});

// 8
```

<a name="method-all"></a>
#### `all()` {.collection-method}

`all` 方法返回集合所代表的底层数组：

```php
collect([1, 2, 3])->all();

// [1, 2, 3]
```

<a name="method-average"></a>
#### `average()` {.collection-method}

[avg](#method-avg) 方法的别名。

<a name="method-avg"></a>
#### `avg()` {.collection-method}

`avg` 方法返回给定键的[平均值](https://en.wikipedia.org/wiki/Average)：

```php
$average = collect([
    ['foo' => 10],
    ['foo' => 10],
    ['foo' => 20],
    ['foo' => 40]
])->avg('foo');

// 20

$average = collect([1, 1, 2, 4])->avg();

// 2
```

<a name="method-before"></a>
#### `before()` {.collection-method}

`before` 方法与 [after](#method-after) 方法相反。它返回给定项之前的项。如果未找到给定项或该项是第一项，则返回 `null`：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->before(3);

// 2

$collection->before(1);

// null

collect([2, 4, 6, 8])->before('4', strict: true);

// null

collect([2, 4, 6, 8])->before(function (int $item, int $key) {
    return $item > 5;
});

// 4
```

#### `chunk()` {.collection-method}

`chunk` 方法将集合拆分为多个较小的集合，每个集合的大小由你指定：

```php
$collection = collect([1, 2, 3, 4, 5, 6, 7]);

$chunks = $collection->chunk(4);

$chunks->all();

// [[1, 2, 3, 4], [5, 6, 7]]
```

此方法在使用网格系统（如 [Bootstrap](https://getbootstrap.com/docs/5.3/layout/grid/)）的[视图](/docs/laravel/12.x/views)中非常有用。例如，假设你有一个要在网格中显示的 [Eloquent](/docs/laravel/12.x/eloquent) 模型集合：

```blade
@foreach ($products->chunk(3) as $chunk)
    <div class="row">
        @foreach ($chunk as $product)
            <div class="col-xs-4">{{ $product->name }}</div>
        @endforeach
    </div>
@endforeach
```

#### `chunkWhile()` {.collection-method}

`chunkWhile` 方法根据给定回调的返回值，将集合拆分为多个较小的集合。传递给闭包的 `$chunk` 变量可以用来检查前一个元素：

```php
$collection = collect(str_split('AABBCCCD'));

$chunks = $collection->chunkWhile(function (string $value, int $key, Collection $chunk) {
    return $value === $chunk->last();
});

$chunks->all();

// [['A', 'A'], ['B', 'B'], ['C', 'C', 'C'], ['D']]
```

#### `collapse()` {.collection-method}

`collapse` 方法将一个包含数组或集合的集合，合并成一个单一的扁平集合：

```php
$collection = collect([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]);

$collapsed = $collection->collapse();

$collapsed->all();

// [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

#### `collapseWithKeys()` {.collection-method}

`collapseWithKeys` 方法将一个包含数组或集合的集合扁平化为单一集合，同时保持原始键名不变：

```php
$collection = collect([
    ['first'  => collect([1, 2, 3])],
    ['second' => [4, 5, 6]],
    ['third'  => collect([7, 8, 9])]
]);

$collapsed = $collection->collapseWithKeys();

$collapsed->all();

// [
//     'first'  => [1, 2, 3],
//     'second' => [4, 5, 6],
//     'third'  => [7, 8, 9],
// ]
```

#### `collect()` {.collection-method}

`collect` 方法返回一个新的 `Collection` 实例，包含当前集合中的所有项：

```php
$collectionA = collect([1, 2, 3]);

$collectionB = $collectionA->collect();

$collectionB->all();

// [1, 2, 3]
```



`collect` 方法主要用于将[懒集合](#lazy-collections)转换为标准的 `Collection` 实例：

```php
$lazyCollection = LazyCollection::make(function () {
    yield 1;
    yield 2;
    yield 3;
});

$collection = $lazyCollection->collect();

$collection::class;

// 'Illuminate\Support\Collection'

$collection->all();

// [1, 2, 3]
```

> [!注意]
> 当你拥有一个 `Enumerable` 实例并且需要一个非懒集合实例时，`collect` 方法特别有用。由于 `collect()` 是 `Enumerable` 合约的一部分，你可以安全地使用它获取一个 `Collection` 实例。

#### `combine()` {.collection-method}

`combine` 方法将集合中的值作为键，与另一个数组或集合中的值组合起来：

```php
$collection = collect(['name', 'age']);

$combined = $collection->combine(['George', 29]);

$combined->all();

// ['name' => 'George', 'age' => 29]
```

#### `concat()` {.collection-method}

`concat` 方法会将给定数组或集合的值追加到原集合的末尾：

```php
$collection = collect(['John Doe']);

$concatenated = $collection->concat(['Jane Doe'])->concat(['name' => 'Johnny Doe']);

$concatenated->all();

// ['John Doe', 'Jane Doe', 'Johnny Doe']
```

`concat` 方法会对追加到原集合的元素重新按数字索引进行排序。
如果想在关联集合中保持原有键，请使用 [merge](#method-merge) 方法。

#### `contains()` {.collection-method}

`contains` 方法用于判断集合是否包含某个元素。
你可以传递一个闭包给 `contains` 方法，以判断集合中是否存在满足给定条件的元素：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->contains(function (int $value, int $key) {
    return $value > 5;
});

// false
```

另外，你也可以直接传递一个值给 `contains` 方法，以判断集合中是否包含该值：

```php
$collection = collect(['name' => 'Desk', 'price' => 100]);

$collection->contains('Desk');

// true

$collection->contains('New York');

// false
```



你也可以向 `contains` 方法传递一个键/值对，用于判断集合中是否存在该键值对：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
]);

$collection->contains('product', 'Bookcase');

// false
```

`contains` 方法在检查元素值时使用“宽松”（loose）比较，这意味着一个字符串形式的整数会被视为等于相同值的整数。
如果需要使用“严格”（strict）比较，请使用 [containsStrict](#method-containsstrict) 方法。

如果想要获取 `contains` 的反向结果，请使用 [doesntContain](#method-doesntcontain) 方法。

#### `containsOneItem()` {.collection-method}

`containsOneItem` 方法用于判断集合是否只包含一个元素：

```php
collect([])->containsOneItem();

// false

collect(['1'])->containsOneItem();

// true

collect(['1', '2'])->containsOneItem();

// false

collect([1, 2, 3])->containsOneItem(fn (int $item) => $item === 2);

// true
```

#### `containsStrict()` {.collection-method}

该方法与 [contains](#method-contains) 方法的签名相同，但所有值都会使用“严格”比较进行判断。

> [!注意]
> 在使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-contains) 时，该方法的行为会有所不同。

#### `count()` {.collection-method}

`count` 方法返回集合中元素的总数：

```php
$collection = collect([1, 2, 3, 4]);

$collection->count();

// 4
```

#### `countBy()` {.collection-method}

`countBy` 方法用于统计集合中值的出现次数。
默认情况下，它会统计每个元素的出现次数，从而可以统计集合中某类元素的数量：

```php
$collection = collect([1, 2, 2, 2, 3]);

$counted = $collection->countBy();

$counted->all();

// [1 => 1, 2 => 3, 3 => 1]
```

你也可以向 `countBy` 方法传递一个闭包，以自定义统计逻辑：

```php
$collection = collect(['alice@gmail.com', 'bob@yahoo.com', 'carlos@gmail.com']);

$counted = $collection->countBy(function (string $email) {
    return substr(strrchr($email, '@'), 1);
});

$counted->all();

// ['gmail.com' => 2, 'yahoo.com' => 1]
```



#### `crossJoin()` {.collection-method}

`crossJoin` 方法会将集合的值与给定的数组或集合进行交叉连接（Cross Join），返回一个**笛卡尔积**（Cartesian product），即所有可能排列组合的结果：

```php
$collection = collect([1, 2]);

$matrix = $collection->crossJoin(['a', 'b']);

$matrix->all();

/*
    [
        [1, 'a'],
        [1, 'b'],
        [2, 'a'],
        [2, 'b'],
    ]
*/

$collection = collect([1, 2]);

$matrix = $collection->crossJoin(['a', 'b'], ['I', 'II']);

$matrix->all();

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

#### `dd()` {.collection-method}

`dd` 方法会**输出集合中的所有项目**，并**立即终止脚本执行**：

```php
$collection = collect(['John Doe', 'Jane Doe']);

$collection->dd();

/*
    array:2 [
        0 => "John Doe"
        1 => "Jane Doe"
    ]
*/
```

如果你不希望中断脚本执行，可以使用 [`dump`](#method-dump) 方法代替。

#### `diff()` {.collection-method}

`diff` 方法会根据**值**将当前集合与另一个集合或普通 PHP 数组进行比较。
它会返回那些**在原集合中存在，但不在给定集合中存在**的值：

```php
$collection = collect([1, 2, 3, 4, 5]);

$diff = $collection->diff([2, 4, 6, 8]);

$diff->all();

// [1, 3, 5]
```

> [!NOTE]
> 当使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-diff) 时，此方法的行为会有所不同。

#### `diffAssoc()` {.collection-method}

`diffAssoc` 方法会根据**键和值**将当前集合与另一个集合或普通 PHP 数组进行比较。
它会返回那些**在原集合中存在但不在给定集合中存在**的键值对：

```php
$collection = collect([
    'color' => 'orange',
    'type' => 'fruit',
    'remain' => 6,
]);

$diff = $collection->diffAssoc([
    'color' => 'yellow',
    'type' => 'fruit',
    'remain' => 3,
    'used' => 6,
]);

$diff->all();

// ['color' => 'orange', 'remain' => 6]
```



#### `diffAssocUsing()` {.collection-method}

与 `diffAssoc` 不同，`diffAssocUsing` 方法允许你传入一个**自定义回调函数**来比较键名（索引）：

```php
$collection = collect([
    'color' => 'orange',
    'type' => 'fruit',
    'remain' => 6,
]);

$diff = $collection->diffAssocUsing([
    'Color' => 'yellow',
    'Type' => 'fruit',
    'Remain' => 3,
], 'strnatcasecmp');

$diff->all();

// ['color' => 'orange', 'remain' => 6]
```

这个回调函数必须是一个**比较函数**，它需要返回一个整数：

-   小于 0 表示第一个参数小于第二个参数；
-   等于 0 表示两者相等；
-   大于 0 表示第一个参数大于第二个参数。

更多信息请参考 PHP 文档中关于 [`array_diff_uassoc`](https://www.php.net/array_diff_uassoc#refsect1-function.array-diff-uassoc-parameters) 的说明。
`diffAssocUsing` 方法在内部正是基于此函数实现的。

#### `diffKeys()` {.collection-method}

`diffKeys` 方法根据**键名**将当前集合与另一个集合或普通 PHP 数组进行比较。
它会返回那些**在原集合中存在但不在给定集合中存在**的键值对：

```php
$collection = collect([
    'one' => 10,
    'two' => 20,
    'three' => 30,
    'four' => 40,
    'five' => 50,
]);

$diff = $collection->diffKeys([
    'two' => 2,
    'four' => 4,
    'six' => 6,
    'eight' => 8,
]);

$diff->all();

// ['one' => 10, 'three' => 30, 'five' => 50]
```

#### `doesntContain()` {.collection-method}

`doesntContain` 方法用于判断集合**是否不包含**指定的项目。
你可以传入一个闭包（回调函数）来判断集合中是否不存在满足特定条件的元素：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->doesntContain(function (int $value, int $key) {
    return $value < 5;
});

// false
```

也可以直接传入一个字符串或值来判断集合中是否**不包含**指定的值：

```php
$collection = collect(['name' => 'Desk', 'price' => 100]);

$collection->doesntContain('Table');

// true

$collection->doesntContain('Desk');

// false
```

还可以传入一个**键 / 值对**来判断集合中是否不存在该键值组合：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
]);

$collection->doesntContain('product', 'Bookcase');

// true
```



`doesntContain` 方法在检查项目值时使用**宽松（loose）比较**，这意味着**字符串形式的数字**会被视为与相同值的整数**相等**。

#### `dot()` {.collection-method}

`dot` 方法会将一个**多维集合**扁平化为**单层集合**，并使用“点号（dot）”表示层级关系：

```php
$collection = collect(['products' => ['desk' => ['price' => 100]]]);

$flattened = $collection->dot();

$flattened->all();

// ['products.desk.price' => 100]
```

#### `dump()` {.collection-method}

`dump` 方法会输出集合中的所有项目：

```php
$collection = collect(['John Doe', 'Jane Doe']);

$collection->dump();

/*
    array:2 [
        0 => "John Doe"
        1 => "Jane Doe"
    ]
*/
```

如果你希望在输出后**终止脚本执行**，请改用 [`dd`](#method-dd) 方法。

#### `duplicates()` {.collection-method}

`duplicates` 方法用于从集合中获取并返回**重复的值**：

```php
$collection = collect(['a', 'b', 'a', 'c', 'b']);

$collection->duplicates();

// [2 => 'a', 4 => 'b']
```

如果集合中包含数组或对象，你可以传入一个**属性键名**，指定要检查哪个字段的重复值：

```php
$employees = collect([
    ['email' => 'abigail@example.com', 'position' => 'Developer'],
    ['email' => 'james@example.com', 'position' => 'Designer'],
    ['email' => 'victoria@example.com', 'position' => 'Developer'],
]);

$employees->duplicates('position');

// [2 => 'Developer']
```

#### `duplicatesStrict()` {.collection-method}

此方法与 [`duplicates`](#method-duplicates) 方法具有相同的用法，但会使用**严格（strict）比较**来判断值是否相等。

#### `each()` {.collection-method}

`each` 方法会遍历集合中的每个项目，并将项目传递给一个闭包函数：

```php
$collection = collect([1, 2, 3, 4]);

$collection->each(function (int $item, int $key) {
    // ...
});
```

如果希望在遍历过程中**中断循环**，可以在闭包中返回 `false`：

```php
$collection->each(function (int $item, int $key) {
    if (/* condition */) {
        return false;
    }
});
```



#### `eachSpread()` {.collection-method}

`eachSpread` 方法会遍历集合中的项目，并将**每个嵌套项的值**依次传递给指定的回调函数：

```php
$collection = collect([['John Doe', 35], ['Jane Doe', 33]]);

$collection->eachSpread(function (string $name, int $age) {
    // ...
});
```

你可以通过在回调函数中返回 `false` 来**停止遍历**：

```php
$collection->eachSpread(function (string $name, int $age) {
    return false;
});
```

#### `ensure()` {.collection-method}

`ensure` 方法用于验证集合中的所有元素是否属于指定的类型或类型列表。
如果存在不符合要求的元素，将抛出 `UnexpectedValueException` 异常：

```php
return $collection->ensure(User::class);

return $collection->ensure([User::class, Customer::class]);
```

你也可以指定原始类型（primitive types），如 `string`、`int`、`float`、`bool` 和 `array`：

```php
return $collection->ensure('int');
```

> [!WARNING]
> `ensure` 方法并**不能保证**在之后的操作中不会再向集合中添加不同类型的元素。

#### `every()` {.collection-method}

`every` 方法用于验证集合中的所有元素是否都通过给定的**条件判断（truth test）**：

```php
collect([1, 2, 3, 4])->every(function (int $value, int $key) {
    return $value > 2;
});

// false
```

如果集合为空，`every` 方法将返回 `true`：

```php
$collection = collect([]);

$collection->every(function (int $value, int $key) {
    return $value > 2;
});

// true
```

#### `except()` {.collection-method}

`except` 方法会返回集合中**除指定键之外**的所有项目：

```php
$collection = collect(['product_id' => 1, 'price' => 100, 'discount' => false]);

$filtered = $collection->except(['price', 'discount']);

$filtered->all();

// ['product_id' => 1]
```

若要获取与 `except` 相反的结果，请参阅 [`only`](#method-only) 方法。

> [!注意]
> 当使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-except) 时，此方法的行为会有所不同。



#### `filter()` {.collection-method}

`filter` 方法使用给定的回调函数过滤集合，仅保留那些**通过指定条件判断（truth test）**的项目：

```php
$collection = collect([1, 2, 3, 4]);

$filtered = $collection->filter(function (int $value, int $key) {
    return $value > 2;
});

$filtered->all();

// [3, 4]
```

如果没有传入回调函数，`filter` 会移除集合中所有等价于 `false` 的元素（即假值，如 `null`、`false`、`''`、`0`、空数组等）：

```php
$collection = collect([1, 2, 3, null, false, '', 0, []]);

$collection->filter()->all();

// [1, 2, 3]
```

想要获取与 `filter` 相反的结果，请参阅 [`reject`](#method-reject) 方法。

#### `first()` {.collection-method}

`first` 方法会返回集合中**第一个通过指定条件判断的元素**：

```php
collect([1, 2, 3, 4])->first(function (int $value, int $key) {
    return $value > 2;
});

// 3
```

你也可以在不传递任何参数的情况下调用 `first` 方法，以获取集合中的**第一个元素**。
如果集合为空，则返回 `null`：

```php
collect([1, 2, 3, 4])->first();

// 1
```

#### `firstOrFail()` {.collection-method}

`firstOrFail` 方法与 `first` 方法功能相同；但如果**未找到任何结果**，则会抛出
`Illuminate\Support\ItemNotFoundException` 异常：

```php
collect([1, 2, 3, 4])->firstOrFail(function (int $value, int $key) {
    return $value > 5;
});


// 抛出 ItemNotFoundException 异常...
```

同样地，如果在不传入回调的情况下调用该方法，而集合又是空的，
也会抛出 `ItemNotFoundException` 异常：

```php
collect([])->firstOrFail();

// 抛出 ItemNotFoundException 异常...
```

#### `firstWhere()` {.collection-method}

`firstWhere` 方法会返回集合中**第一个符合给定键 / 值条件**的元素：

```php
$collection = collect([
    ['name' => 'Regena', 'age' => null],
    ['name' => 'Linda', 'age' => 14],
    ['name' => 'Diego', 'age' => 23],
    ['name' => 'Linda', 'age' => 84],
]);

$collection->firstWhere('name', 'Linda');

// ['name' => 'Linda', 'age' => 14]
```



你也可以在调用 `firstWhere` 方法时使用**比较运算符**：

```php
$collection->firstWhere('age', '>=', 18);

// ['name' => 'Diego', 'age' => 23]
```

与 [`where`](#method-where) 方法类似，你也可以只传递一个参数给 `firstWhere` 方法。
在这种情况下，`firstWhere` 会返回集合中**第一个给定键的值为“真”（truthy）**的元素：

```php
$collection->firstWhere('age');

// ['name' => 'Linda', 'age' => 14]
```

#### `flatMap()` {.collection-method}

`flatMap` 方法会遍历集合中的每个元素，并将每个值传递给指定的闭包。
闭包可以自由地修改并返回该元素，从而形成一个新的集合。
之后，该集合会被**扁平化一层**：

```php
$collection = collect([
    ['name' => 'Sally'],
    ['school' => 'Arkansas'],
    ['age' => 28]
]);

$flattened = $collection->flatMap(function (array $values) {
    return array_map('strtoupper', $values);
});

$flattened->all();

// ['name' => 'SALLY', 'school' => 'ARKANSAS', 'age' => '28'];
```

#### `flatten()` {.collection-method}

`flatten` 方法会将一个**多维集合**扁平化为**单层集合**：

```php
$collection = collect([
    'name' => 'Taylor',
    'languages' => [
        'PHP', 'JavaScript'
    ]
]);

$flattened = $collection->flatten();

$flattened->all();

// ['Taylor', 'PHP', 'JavaScript'];
```

如有需要，你可以为 `flatten` 方法传入一个“深度”（`depth`）参数，用来指定要扁平化的层级数：

```php
$collection = collect([
    'Apple' => [
        [
            'name' => 'iPhone 6S',
            'brand' => 'Apple'
        ],
    ],
    'Samsung' => [
        [
            'name' => 'Galaxy S7',
            'brand' => 'Samsung'
        ],
    ],
]);

$products = $collection->flatten(1);

$products->values()->all();

/*
    [
        ['name' => 'iPhone 6S', 'brand' => 'Apple'],
        ['name' => 'Galaxy S7', 'brand' => 'Samsung'],
    ]
*/
```

在上面的例子中，如果不传入 `depth` 参数直接调用 `flatten`，
结果会进一步展开成：
`['iPhone 6S', 'Apple', 'Galaxy S7', 'Samsung']`。
通过指定“深度”，你可以控制扁平化操作应当展开的嵌套层级数量。



#### `flip()` {.collection-method}

`flip` 方法会**交换集合中的键和值**：

```php
$collection = collect(['name' => 'Taylor', 'framework' => 'Laravel']);

$flipped = $collection->flip();

$flipped->all();

// ['Taylor' => 'name', 'Laravel' => 'framework']
```

#### `forget()` {.collection-method}

`forget` 方法会根据**键名**从集合中移除一个项目：

```php
$collection = collect(['name' => 'Taylor', 'framework' => 'Laravel']);

// 删除单个键...
$collection->forget('name');

// ['framework' => 'Laravel']

// 删除多个键...
$collection->forget(['name', 'framework']);

// []
```

> [!警告]
> 与大多数其他集合方法不同，`forget` **不会返回一个新的集合实例**。
它会**直接修改原集合**并返回自身。

#### `forPage()` {.collection-method}

`forPage` 方法会返回一个新的集合，其中包含指定页码上的项目。
该方法的第一个参数是**页码**，第二个参数是**每页显示的项目数量**：

```php
$collection = collect([1, 2, 3, 4, 5, 6, 7, 8, 9]);

$chunk = $collection->forPage(2, 3);

$chunk->all();

// [4, 5, 6]
```

#### `fromJson()` {.collection-method}

静态方法 `fromJson` 会通过 PHP 的 `json_decode` 函数解码给定的 JSON 字符串，
并据此创建一个新的集合实例：

```php
use Illuminate\Support\Collection;

$json = json_encode([
    'name' => 'Taylor Otwell',
    'role' => 'Developer',
    'status' => 'Active',
]);

$collection = Collection::fromJson($json);
```

#### `get()` {.collection-method}

`get` 方法根据指定的**键名**返回对应的项目。
如果键不存在，则返回 `null`：

```php
$collection = collect(['name' => 'Taylor', 'framework' => 'Laravel']);

$value = $collection->get('name');

// Taylor
```

你还可以传入一个**默认值**作为第二个参数：
当键不存在时，将返回该默认值：

```php
$collection = collect(['name' => 'Taylor', 'framework' => 'Laravel']);

$value = $collection->get('age', 34);

// 34
```



你甚至可以将回调函数作为方法的默认值传入。如果指定的键不存在，那么回调函数的返回结果将会被返回：

```php
$collection->get('email', function () {
    return 'taylor@example.com';
});

// taylor@example.com
```

#### `groupBy()` {.collection-method}

`groupBy` 方法会根据给定的键将集合中的项目进行分组：

```php
$collection = collect([
    ['account_id' => 'account-x10', 'product' => 'Chair'],
    ['account_id' => 'account-x10', 'product' => 'Bookcase'],
    ['account_id' => 'account-x11', 'product' => 'Desk'],
]);

$grouped = $collection->groupBy('account_id');

$grouped->all();

/*
    [
        'account-x10' => [
            ['account_id' => 'account-x10', 'product' => 'Chair'],
            ['account_id' => 'account-x10', 'product' => 'Bookcase'],
        ],
        'account-x11' => [
            ['account_id' => 'account-x11', 'product' => 'Desk'],
        ],
    ]
*/
```

除了传入字符串形式的键，你也可以传入一个回调函数。该回调函数应返回用于分组的值：

```php
$grouped = $collection->groupBy(function (array $item, int $key) {
    return substr($item['account_id'], -3);
});

$grouped->all();

/*
    [
        'x10' => [
            ['account_id' => 'account-x10', 'product' => 'Chair'],
            ['account_id' => 'account-x10', 'product' => 'Bookcase'],
        ],
        'x11' => [
            ['account_id' => 'account-x11', 'product' => 'Desk'],
        ],
    ]
*/
```

可以通过传入数组来指定多个分组条件。数组中的每个元素会应用于多维数组中对应层级的分组：

```php
$data = new Collection([
    10 => ['user' => 1, 'skill' => 1, 'roles' => ['Role_1', 'Role_3']],
    20 => ['user' => 2, 'skill' => 1, 'roles' => ['Role_1', 'Role_2']],
    30 => ['user' => 3, 'skill' => 2, 'roles' => ['Role_1']],
    40 => ['user' => 4, 'skill' => 2, 'roles' => ['Role_2']],
]);

$result = $data->groupBy(['skill', function (array $item) {
    return $item['roles'];
}], preserveKeys: true);

/*
[
    1 => [
        'Role_1' => [
            10 => ['user' => 1, 'skill' => 1, 'roles' => ['Role_1', 'Role_3']],
            20 => ['user' => 2, 'skill' => 1, 'roles' => ['Role_1', 'Role_2']],
        ],
        'Role_2' => [
            20 => ['user' => 2, 'skill' => 1, 'roles' => ['Role_1', 'Role_2']],
        ],
        'Role_3' => [
            10 => ['user' => 1, 'skill' => 1, 'roles' => ['Role_1', 'Role_3']],
        ],
    ],
    2 => [
        'Role_1' => [
            30 => ['user' => 3, 'skill' => 2, 'roles' => ['Role_1']],
        ],
        'Role_2' => [
            40 => ['user' => 4, 'skill' => 2, 'roles' => ['Role_2']],
        ],
    ],
];
*/
```



#### `has()` {.collection-method}

`has` 方法用于判断集合中是否存在指定的键：

```php
$collection = collect(['account_id' => 1, 'product' => 'Desk', 'amount' => 5]);

$collection->has('product');

// true

$collection->has(['product', 'amount']);

// true

$collection->has(['amount', 'price']);

// false
```

#### `hasAny()` {.collection-method}

`hasAny` 方法用于判断给定的键中是否有任意一个存在于集合中：

```php
$collection = collect(['account_id' => 1, 'product' => 'Desk', 'amount' => 5]);

$collection->hasAny(['product', 'price']);

// true

$collection->hasAny(['name', 'price']);

// false
```

#### `implode()` {.collection-method}

`implode` 方法用于将集合中的项目连接成字符串。
其参数取决于集合中项目的类型。
如果集合包含数组或对象，你应该传入要连接的属性键名，以及连接它们时使用的“连接符”字符串：

```php
$collection = collect([
    ['account_id' => 1, 'product' => 'Desk'],
    ['account_id' => 2, 'product' => 'Chair'],
]);

$collection->implode('product', ', ');

// 'Desk, Chair'
```

如果集合中包含的是简单的字符串或数值，你只需传入一个“连接符”作为参数：

```php
collect([1, 2, 3, 4, 5])->implode('-');

// '1-2-3-4-5'
```

如果你想在连接前格式化这些值，可以向 `implode` 方法传入一个闭包：

```php
$collection->implode(function (array $item, int $key) {
    return strtoupper($item['product']);
}, ', ');

// 'DESK, CHAIR'
```

#### `intersect()` {.collection-method}

`intersect` 方法会从原集合中移除那些**不在**给定数组或集合中的值。
结果集合会保留原集合的键：

```php
$collection = collect(['Desk', 'Sofa', 'Chair']);

$intersect = $collection->intersect(['Desk', 'Chair', 'Bookcase']);

$intersect->all();

// [0 => 'Desk', 2 => 'Chair']
```

> [!注意]
> 当使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-intersect) 时，此方法的行为会有所不同。



#### `intersectUsing()` {.collection-method}

`intersectUsing` 方法会从原集合中移除那些**不在**给定数组或集合中的值，并使用自定义回调函数来比较这些值。
结果集合会保留原集合的键：

```php
$collection = collect(['Desk', 'Sofa', 'Chair']);

$intersect = $collection->intersectUsing(['desk', 'chair', 'bookcase'], function (string $a, string $b) {
    return strcasecmp($a, $b);
});

$intersect->all();

// [0 => 'Desk', 2 => 'Chair']
```

#### `intersectAssoc()` {.collection-method}

`intersectAssoc` 方法将原集合与另一个集合或数组进行比较，
返回那些在所有给定集合中都存在的键 / 值对：

```php
$collection = collect([
    'color' => 'red',
    'size' => 'M',
    'material' => 'cotton'
]);

$intersect = $collection->intersectAssoc([
    'color' => 'blue',
    'size' => 'M',
    'material' => 'polyester'
]);

$intersect->all();

// ['size' => 'M']
```

#### `intersectAssocUsing()` {.collection-method}

`intersectAssocUsing` 方法将原集合与另一个集合或数组进行比较，
返回两者中都存在的键 / 值对，并使用自定义的比较回调函数来判断键和值是否相等：

```php
$collection = collect([
    'color' => 'red',
    'Size' => 'M',
    'material' => 'cotton',
]);

$intersect = $collection->intersectAssocUsing([
    'color' => 'blue',
    'size' => 'M',
    'material' => 'polyester',
], function (string $a, string $b) {
    return strcasecmp($a, $b);
});

$intersect->all();

// ['Size' => 'M']
```

#### `intersectByKeys()` {.collection-method}

`intersectByKeys` 方法会从原集合中移除那些键（及其对应的值）不在给定数组或集合中的项目：

```php
$collection = collect([
    'serial' => 'UX301', 'type' => 'screen', 'year' => 2009,
]);

$intersect = $collection->intersectByKeys([
    'reference' => 'UX404', 'type' => 'tab', 'year' => 2011,
]);

$intersect->all();

// ['type' => 'screen', 'year' => 2009]
```



#### `isEmpty()` {.collection-method}

`isEmpty` 方法在集合为空时返回 `true`，否则返回 `false`：

```php
collect([])->isEmpty();

// true
```

#### `isNotEmpty()` {.collection-method}

`isNotEmpty` 方法在集合**不为空**时返回 `true`，否则返回 `false`：

```php
collect([])->isNotEmpty();

// false
```

#### `join()` {.collection-method}

`join` 方法使用一个字符串将集合中的值连接起来。
通过该方法的第二个参数，你还可以指定在连接最后一个元素时所使用的字符串：

```php
collect(['a', 'b', 'c'])->join(', '); // 'a, b, c'
collect(['a', 'b', 'c'])->join(', ', ', and '); // 'a, b, and c'
collect(['a', 'b'])->join(', ', ' and '); // 'a and b'
collect(['a'])->join(', ', ' and '); // 'a'
collect([])->join(', ', ' and '); // ''
```

#### `keyBy()` {.collection-method}

`keyBy` 方法会根据给定的键为集合重新建立键名。
如果多个项目具有相同的键，只有最后一个会出现在新的集合中：

```php
$collection = collect([
    ['product_id' => 'prod-100', 'name' => 'Desk'],
    ['product_id' => 'prod-200', 'name' => 'Chair'],
]);

$keyed = $collection->keyBy('product_id');

$keyed->all();

/*
    [
        'prod-100' => ['product_id' => 'prod-100', 'name' => 'Desk'],
        'prod-200' => ['product_id' => 'prod-200', 'name' => 'Chair'],
    ]
*/
```

你也可以向该方法传入一个回调函数。
该回调函数应返回用于作为键名的值：

```php
$keyed = $collection->keyBy(function (array $item, int $key) {
    return strtoupper($item['product_id']);
});

$keyed->all();

/*
    [
        'PROD-100' => ['product_id' => 'prod-100', 'name' => 'Desk'],
        'PROD-200' => ['product_id' => 'prod-200', 'name' => 'Chair'],
    ]
*/
```



#### `keys()` {.collection-method}

`keys` 方法返回集合中所有的键：

```php
$collection = collect([
    'prod-100' => ['product_id' => 'prod-100', 'name' => 'Desk'],
    'prod-200' => ['product_id' => 'prod-200', 'name' => 'Chair'],
]);

$keys = $collection->keys();

$keys->all();

// ['prod-100', 'prod-200']
```

#### `last()` {.collection-method}

`last` 方法返回集合中**最后一个**通过给定条件测试的元素：

```php
collect([1, 2, 3, 4])->last(function (int $value, int $key) {
    return $value < 3;
});

// 2
```

你也可以不传入任何参数来获取集合中的最后一个元素。
如果集合为空，则返回 `null`：

```php
collect([1, 2, 3, 4])->last();

// 4
```

#### `lazy()` {.collection-method}

`lazy` 方法会基于集合的底层数组返回一个新的 [LazyCollection](#lazy-collections) 实例：

```php
$lazyCollection = collect([1, 2, 3, 4])->lazy();

$lazyCollection::class;

// Illuminate\Support\LazyCollection

$lazyCollection->all();

// [1, 2, 3, 4]
```

这在需要对包含大量项目的 `Collection` 进行转换操作时特别有用：

```php
$count = $hugeCollection
    ->lazy()
    ->where('country', 'FR')
    ->where('balance', '>', '100')
    ->count();
```

通过将集合转换为 `LazyCollection`，我们避免了分配大量额外内存。
虽然原始集合的值仍会保存在内存中，但后续的筛选操作不会。
因此，在过滤集合结果时几乎不会再占用额外的内存。

#### `macro()` {.collection-method}

静态方法 `macro` 允许你在运行时向 `Collection` 类中添加自定义方法。
有关更多信息，请参阅 [扩展集合](#extending-collections) 的相关文档。



#### `make()` {.collection-method}

静态方法 `make` 用于创建一个新的集合实例。
参见 [创建集合](#creating-collections) 部分。

```php
use Illuminate\Support\Collection;

$collection = Collection::make([1, 2, 3]);
```

#### `map()` {.collection-method}

`map` 方法会遍历集合中的每个项目，并将每个值传递给给定的回调函数。
回调函数可以对项目进行修改并返回修改后的值，从而形成一个包含修改后项目的新集合：

```php
$collection = collect([1, 2, 3, 4, 5]);

$multiplied = $collection->map(function (int $item, int $key) {
    return $item * 2;
});

$multiplied->all();

// [2, 4, 6, 8, 10]
```

> [!警告]
> 与大多数其他集合方法一样，`map` 会返回一个新的集合实例；它不会修改被调用的原始集合。
如果你想直接转换原集合，请使用 [transform](#method-transform) 方法。

#### `mapInto()` {.collection-method}

`mapInto()` 方法会遍历集合中的每个项目，并将项目的值传递给给定类的构造函数，从而创建该类的新实例：

```php
class Currency
{
    /**
     * 创建一个新的 Currency 实例。
     */
    function __construct(
        public string $code,
    ) {}
}

$collection = collect(['USD', 'EUR', 'GBP']);

$currencies = $collection->mapInto(Currency::class);

$currencies->all();

// [Currency('USD'), Currency('EUR'), Currency('GBP')]
```

#### `mapSpread()` {.collection-method}

`mapSpread` 方法会遍历集合中的项目，并将每个嵌套项目的值依次传入给定的闭包。
闭包可以自由修改这些值并返回结果，从而形成一个包含修改后项目的新集合：

```php
$collection = collect([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);

$chunks = $collection->chunk(2);

$sequence = $chunks->mapSpread(function (int $even, int $odd) {
    return $even + $odd;
});

$sequence->all();

// [1, 5, 9, 13, 17]
```

#### `mapToGroups()` {.collection-method}

`mapToGroups` 方法会根据给定的闭包对集合中的项目进行分组。
闭包应返回一个仅包含单个键 / 值对的关联数组，从而形成一个新的分组集合：

```php
$collection = collect([
    [
        'name' => 'John Doe',
        'department' => 'Sales',
    ],
    [
        'name' => 'Jane Doe',
        'department' => 'Sales',
    ],
    [
        'name' => 'Johnny Doe',
        'department' => 'Marketing',
    ]
]);

$grouped = $collection->mapToGroups(function (array $item, int $key) {
    return [$item['department'] => $item['name']];
});

$grouped->all();

/*
    [
        'Sales' => ['John Doe', 'Jane Doe'],
        'Marketing' => ['Johnny Doe'],
    ]
*/

$grouped->get('Sales')->all();

// ['John Doe', 'Jane Doe']
```



#### `mapWithKeys()` {.collection-method}

`mapWithKeys` 方法会遍历集合，并将每个值传递给指定的回调函数。
回调函数应返回一个只包含**单个键值对**的关联数组：

```php
$collection = collect([
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
]);

$keyed = $collection->mapWithKeys(function (array $item, int $key) {
    return [$item['email'] => $item['name']];
});

$keyed->all();

/*
    [
        'john@example.com' => 'John',
        'jane@example.com' => 'Jane',
    ]
*/
```

#### `max()` {.collection-method}

`max` 方法返回指定键的最大值：

```php
$max = collect([
    ['foo' => 10],
    ['foo' => 20]
])->max('foo');

// 20

$max = collect([1, 2, 3, 4, 5])->max();

// 5
```

#### `median()` {.collection-method}

`median` 方法返回指定键的[中位数值](https://en.wikipedia.org/wiki/Median)：

```php
$median = collect([
    ['foo' => 10],
    ['foo' => 10],
    ['foo' => 20],
    ['foo' => 40]
])->median('foo');

// 15

$median = collect([1, 1, 2, 4])->median();

// 1.5
```

#### `merge()` {.collection-method}

`merge` 方法会将给定的数组或集合与原集合合并。
如果给定数据中的**字符串键**与原集合的字符串键相同，则新值会覆盖旧值：

```php
$collection = collect(['product_id' => 1, 'price' => 100]);

$merged = $collection->merge(['price' => 200, 'discount' => false]);

$merged->all();

// ['product_id' => 1, 'price' => 200, 'discount' => false]
```

如果给定数据的键是**数字索引**，则这些值会被追加到集合的末尾：

```php
$collection = collect(['Desk', 'Chair']);

$merged = $collection->merge(['Bookcase', 'Door']);

$merged->all();

// ['Desk', 'Chair', 'Bookcase', 'Door']
```

#### `mergeRecursive()` {.collection-method}

`mergeRecursive` 方法会**递归地**将给定数组或集合与原集合合并。
如果给定数据中的字符串键与原集合的键相同，则这些键的值会被合并成数组，并递归执行此操作：

```php
$collection = collect(['product_id' => 1, 'price' => 100]);

$merged = $collection->mergeRecursive([
    'product_id' => 2,
    'price' => 200,
    'discount' => false
]);

$merged->all();

// ['product_id' => [1, 2], 'price' => [100, 200], 'discount' => false]
```



#### `min()` {.collection-method}

`min` 方法返回指定键的最小值：

```php
$min = collect([['foo' => 10], ['foo' => 20]])->min('foo');

// 10

$min = collect([1, 2, 3, 4, 5])->min();

// 1
```

#### `mode()` {.collection-method}

`mode` 方法返回指定键的[众数值](https://en.wikipedia.org/wiki/Mode_(statistics))（即出现次数最多的值）：

```php
$mode = collect([
    ['foo' => 10],
    ['foo' => 10],
    ['foo' => 20],
    ['foo' => 40]
])->mode('foo');

// [10]

$mode = collect([1, 1, 2, 4])->mode();

// [1]

$mode = collect([1, 1, 2, 2])->mode();

// [1, 2]
```

#### `multiply()` {.collection-method}

`multiply` 方法会为集合中的所有元素创建指定数量的副本：

```php
$users = collect([
    ['name' => 'User #1', 'email' => 'user1@example.com'],
    ['name' => 'User #2', 'email' => 'user2@example.com'],
])->multiply(3);

/*
    [
        ['name' => 'User #1', 'email' => 'user1@example.com'],
        ['name' => 'User #2', 'email' => 'user2@example.com'],
        ['name' => 'User #1', 'email' => 'user1@example.com'],
        ['name' => 'User #2', 'email' => 'user2@example.com'],
        ['name' => 'User #1', 'email' => 'user1@example.com'],
        ['name' => 'User #2', 'email' => 'user2@example.com'],
    ]
*/
```

#### `nth()` {.collection-method}

`nth` 方法会创建一个新的集合，包含原集合中每隔 n 个元素的一个：

```php
$collection = collect(['a', 'b', 'c', 'd', 'e', 'f']);

$collection->nth(4);

// ['a', 'e']
```

你也可以传入第二个参数来指定起始偏移量：

```php
$collection->nth(4, 1);

// ['b', 'f']
```

#### `only()` {.collection-method}

`only` 方法返回集合中指定键的项目：

```php
$collection = collect([
    'product_id' => 1,
    'name' => 'Desk',
    'price' => 100,
    'discount' => false
]);

$filtered = $collection->only(['product_id', 'name']);

$filtered->all();

// ['product_id' => 1, 'name' => 'Desk']
```

若要实现相反的效果，请参阅 [`except`](#method-except) 方法。

> [!注意]
> 当使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-only) 时，此方法的行为会有所不同。



#### `pad()` {.collection-method}

`pad` 方法会用指定的值填充数组，直到数组达到指定的大小。
该方法的行为与 PHP 的 [array_pad](https://secure.php.net/manual/en/function.array-pad.php) 函数相同。

如果要**向左填充**，应指定一个**负数**大小。
如果给定大小的绝对值小于或等于数组的长度，则不会进行填充：

```php
$collection = collect(['A', 'B', 'C']);

$filtered = $collection->pad(5, 0);

$filtered->all();

// ['A', 'B', 'C', 0, 0]

$filtered = $collection->pad(-5, 0);

$filtered->all();

// [0, 0, 'A', 'B', 'C']
```

#### `partition()` {.collection-method}

`partition` 方法可以与 PHP 的**数组解构**结合使用，用于将满足条件的元素与不满足条件的元素分开：

```php
$collection = collect([1, 2, 3, 4, 5, 6]);

[$underThree, $equalOrAboveThree] = $collection->partition(function (int $i) {
    return $i < 3;
});

$underThree->all();

// [1, 2]

$equalOrAboveThree->all();

// [3, 4, 5, 6]
```

> [!注意]
> 当与 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-partition) 一起使用时，此方法的行为会有所不同。

#### `percentage()` {.collection-method}

`percentage` 方法可用于快速计算集合中**满足指定条件的元素所占的百分比**：

```php
$collection = collect([1, 1, 2, 2, 2, 3]);

$percentage = $collection->percentage(fn (int $value) => $value === 1);

// 33.33
```

默认情况下，百分比会保留两位小数。
但你可以通过传递第二个参数来自定义精度：

```php
$percentage = $collection->percentage(fn (int $value) => $value === 1, precision: 3);

// 33.333
```

#### `pipe()` {.collection-method}

`pipe` 方法会将集合传递给指定的闭包，并返回闭包执行的结果：

```php
$collection = collect([1, 2, 3]);

$piped = $collection->pipe(function (Collection $collection) {
    return $collection->sum();
});

// 6
```



#### `pipeInto()` {.collection-method}

`pipeInto` 方法会创建给定类的新实例，并将当前集合传递给该类的构造函数：

```php
class ResourceCollection
{
    /**
     * 创建一个新的 ResourceCollection 实例。
     */
    public function __construct(
        public Collection $collection,
    ) {}
}

$collection = collect([1, 2, 3]);

$resource = $collection->pipeInto(ResourceCollection::class);

$resource->collection->all();

// [1, 2, 3]
```

#### `pipeThrough()` {.collection-method}

`pipeThrough` 方法会将集合依次传递给给定的闭包数组，并返回闭包执行后的最终结果：

```php
use Illuminate\Support\Collection;

$collection = collect([1, 2, 3]);

$result = $collection->pipeThrough([
    function (Collection $collection) {
        return $collection->merge([4, 5]);
    },
    function (Collection $collection) {
        return $collection->sum();
    },
]);

// 15
```

#### `pluck()` {.collection-method}

`pluck` 方法用于获取指定键对应的所有值：

```php
$collection = collect([
    ['product_id' => 'prod-100', 'name' => 'Desk'],
    ['product_id' => 'prod-200', 'name' => 'Chair'],
]);

$plucked = $collection->pluck('name');

$plucked->all();

// ['Desk', 'Chair']
```

你还可以指定结果集合的键名：

```php
$plucked = $collection->pluck('name', 'product_id');

$plucked->all();

// ['prod-100' => 'Desk', 'prod-200' => 'Chair']
```

`pluck` 方法也支持使用 “点（dot）” 语法来获取嵌套值：

```php
$collection = collect([
    [
        'name' => 'Laracon',
        'speakers' => [
            'first_day' => ['Rosa', 'Judith'],
        ],
    ],
    [
        'name' => 'VueConf',
        'speakers' => [
            'first_day' => ['Abigail', 'Joey'],
        ],
    ],
]);

$plucked = $collection->pluck('speakers.first_day');

$plucked->all();

// [['Rosa', 'Judith'], ['Abigail', 'Joey']]
```

如果存在重复的键，最后一个匹配的元素将会覆盖之前的值：

```php
$collection = collect([
    ['brand' => 'Tesla',  'color' => 'red'],
    ['brand' => 'Pagani', 'color' => 'white'],
    ['brand' => 'Tesla',  'color' => 'black'],
    ['brand' => 'Pagani', 'color' => 'orange'],
]);

$plucked = $collection->pluck('color', 'brand');

$plucked->all();

// ['Tesla' => 'black', 'Pagani' => 'orange']
```



`pop` 方法会**移除并返回集合中的最后一个元素**。
如果集合为空，则会返回 `null`：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->pop();

// 5

$collection->all();

// [1, 2, 3, 4]
```

你也可以向 `pop` 方法传入一个整数，用来**移除并返回集合末尾的多个元素**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->pop(3);

// collect([5, 4, 3])

$collection->all();

// [1, 2]
```

#### `prepend()` {.collection-method}

`prepend` 方法会在集合的开头添加一个元素：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->prepend(0);

$collection->all();

// [0, 1, 2, 3, 4, 5]
```

你也可以传入第二个参数来指定新元素的键名：

```php
$collection = collect(['one' => 1, 'two' => 2]);

$collection->prepend(0, 'zero');

$collection->all();

// ['zero' => 0, 'one' => 1, 'two' => 2]
```

#### `pull()` {.collection-method}

`pull` 方法根据指定的键**移除并返回集合中的一个元素**：

```php
$collection = collect(['product_id' => 'prod-100', 'name' => 'Desk']);

$collection->pull('name');

// 'Desk'

$collection->all();

// ['product_id' => 'prod-100']
```

#### `push()` {.collection-method}

`push` 方法会将一个元素**追加到集合的末尾**：

```php
$collection = collect([1, 2, 3, 4]);

$collection->push(5);

$collection->all();

// [1, 2, 3, 4, 5]
```

#### `put()` {.collection-method}

`put` 方法会在集合中**设置指定的键和值**：

```php
$collection = collect(['product_id' => 1, 'name' => 'Desk']);

$collection->put('price', 100);

$collection->all();

// ['product_id' => 1, 'name' => 'Desk', 'price' => 100]
```

#### `random()` {.collection-method}

`random` 方法会**从集合中随机返回一个元素**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->random();

// 4 - （随机返回）
```

你也可以传入一个整数，指定要随机获取的元素数量。
当显式指定数量时，返回的总是一个新的集合：

```php
$random = $collection->random(3);

$random->all();

// [2, 4, 5] - (retrieved randomly)
```



如果集合中的项目数量**少于请求的数量**，`random` 方法将抛出一个 `InvalidArgumentException` 异常。

`random` 方法还可以接受一个闭包（closure），该闭包会接收当前的集合实例作为参数：

```php
use Illuminate\Support\Collection;

$random = $collection->random(fn (Collection $items) => min(10, count($items)));

$random->all();

// [1, 2, 3, 4, 5] - （随机返回）
```

#### `range()` {.collection-method}

`range` 方法返回一个包含指定范围内整数的集合：

```php
$collection = collect()->range(3, 6);

$collection->all();

// [3, 4, 5, 6]
```

#### `reduce()` {.collection-method}

`reduce` 方法会将集合**归约为单个值**，在每次迭代中将上一次迭代的结果传递到下一次迭代中：

```php
$collection = collect([1, 2, 3]);

$total = $collection->reduce(function (?int $carry, int $item) {
    return $carry + $item;
});

// 6
```

第一次迭代时，`$carry` 的值为 `null`；
不过，你可以通过传递第二个参数来指定初始值：

```php
$collection->reduce(function (int $carry, int $item) {
    return $carry + $item;
}, 4);

// 10
```

`reduce` 方法还会将数组的键名作为参数传递给回调函数：

```php
$collection = collect([
    'usd' => 1400,
    'gbp' => 1200,
    'eur' => 1000,
]);

$ratio = [
    'usd' => 1,
    'gbp' => 1.37,
    'eur' => 1.22,
];

$collection->reduce(function (int $carry, int $value, string $key) use ($ratio) {
    return $carry + ($value * $ratio[$key]);
}, 0);

// 4264
```

#### `reduceSpread()` {.collection-method}

`reduceSpread` 方法会将集合**归约为一个值数组**，并在每次迭代中将结果传递到下一次迭代中。
该方法与 `reduce` 类似，但它**可以接收多个初始值**：

```php
[$creditsRemaining, $batch] = Image::where('status', 'unprocessed')
    ->get()
    ->reduceSpread(function (int $creditsRemaining, Collection $batch, Image $image) {
        if ($creditsRemaining >= $image->creditsRequired()) {
            $batch->push($image);

            $creditsRemaining -= $image->creditsRequired();
        }

        return [$creditsRemaining, $batch];
    }, $creditsAvailable, collect());
```



#### `reject()` {.collection-method}

`reject` 方法会使用给定的闭包（closure）来过滤集合。
如果闭包返回 `true`，则该项会被**从结果集合中移除**：

```php
$collection = collect([1, 2, 3, 4]);

$filtered = $collection->reject(function (int $value, int $key) {
    return $value > 2;
});

$filtered->all();

// [1, 2]
```

若要获得与 `reject` 相反的效果，请参阅 [`filter`](#method-filter) 方法。

#### `replace()` {.collection-method}

`replace` 方法与 `merge` 方法类似；
但与 `merge` 不同的是，`replace` 除了会覆盖具有相同字符串键的项目外，
还会**覆盖集合中具有相同数字键**的项目：

```php
$collection = collect(['Taylor', 'Abigail', 'James']);

$replaced = $collection->replace([1 => 'Victoria', 3 => 'Finn']);

$replaced->all();

// ['Taylor', 'Victoria', 'James', 'Finn']
```

#### `replaceRecursive()` {.collection-method}

`replaceRecursive` 方法与 `replace` 类似，
但它会**递归地进入数组**，并对内部值执行相同的替换逻辑：

```php
$collection = collect([
    'Taylor',
    'Abigail',
    [
        'James',
        'Victoria',
        'Finn'
    ]
]);

$replaced = $collection->replaceRecursive([
    'Charlie',
    2 => [1 => 'King']
]);

$replaced->all();

// ['Charlie', 'Abigail', ['James', 'King', 'Finn']]
```

#### `reverse()` {.collection-method}

`reverse` 方法会**反转集合中项目的顺序**，同时**保留原始的键名**：

```php
$collection = collect(['a', 'b', 'c', 'd', 'e']);

$reversed = $collection->reverse();

$reversed->all();

/*
    [
        4 => 'e',
        3 => 'd',
        2 => 'c',
        1 => 'b',
        0 => 'a',
    ]
*/
```

#### `search()` {.collection-method}

`search` 方法在集合中**查找给定的值**，并在找到时返回其键。
如果未找到该项，则返回 `false`：

```php
$collection = collect([2, 4, 6, 8]);

$collection->search(4);

// 1
```

搜索默认使用**宽松比较（loose comparison）**，
即数字字符串会被视为与相同值的整数相等。
若要使用**严格比较（strict comparison）**，
可以将第二个参数设置为 `true`：

```php
collect([2, 4, 6, 8])->search('4', strict: true);

// false
```



或者，你也可以提供你自己的闭包（closure）来查找通过给定条件测试的第一个元素：

```php
collect([2, 4, 6, 8])->search(function (int $item, int $key) {
    return $item > 5;
});

// 2
```

#### `select()` {.collection-method}

`select` 方法从集合中选择指定的键，类似于 SQL 的 `SELECT` 语句：

```php
$users = collect([
    ['name' => 'Taylor Otwell', 'role' => 'Developer', 'status' => 'active'],
    ['name' => 'Victoria Faith', 'role' => 'Researcher', 'status' => 'active'],
]);

$users->select(['name', 'role']);

/*
    [
        ['name' => 'Taylor Otwell', 'role' => 'Developer'],
        ['name' => 'Victoria Faith', 'role' => 'Researcher'],
    ],
*/
```

#### `shift()` {.collection-method}

`shift` 方法会移除并返回集合中的第一个元素：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->shift();

// 1

$collection->all();

// [2, 3, 4, 5]
```

你可以向 `shift` 方法传入一个整数，以移除并返回集合开头的多个元素：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->shift(3);

// collect([1, 2, 3])

$collection->all();

// [4, 5]
```

#### `shuffle()` {.collection-method}

`shuffle` 方法会随机打乱集合中的元素顺序：

```php
$collection = collect([1, 2, 3, 4, 5]);

$shuffled = $collection->shuffle();

$shuffled->all();

// [3, 2, 5, 1, 4] - (generated randomly)
```

#### `skip()` {.collection-method}

`skip` 方法返回一个新集合，从原集合的开头移除指定数量的元素：

```php
$collection = collect([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

$collection = $collection->skip(4);

$collection->all();

// [5, 6, 7, 8, 9, 10]
```

#### `skipUntil()` {.collection-method}

`skipUntil` 方法会跳过集合中的元素，直到给定的回调函数返回 `true`。
一旦回调返回 `true`，剩下的所有元素都会作为一个新集合返回：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->skipUntil(function (int $item) {
    return $item >= 3;
});

$subset->all();

// [3, 4]
```



你也可以向 `skipUntil` 方法传入一个简单的值，以跳过所有元素，直到找到给定的值为止：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->skipUntil(3);

$subset->all();

// [3, 4]
```

> [!警告]
> 如果未找到给定的值，或者回调函数从未返回 `true`，`skipUntil` 方法将返回一个空集合。

#### `skipWhile()` {.collection-method}

`skipWhile` 方法会跳过集合中的元素，只要给定的回调函数返回 `true`。
一旦回调返回 `false`，集合中剩余的所有元素将作为一个新集合返回：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->skipWhile(function (int $item) {
    return $item <= 3;
});

$subset->all();

// [4]
```

> [!警告]
> 如果回调函数从未返回 `false`，`skipWhile` 方法将返回一个空集合。

#### `slice()` {.collection-method}

`slice` 方法从给定的索引位置开始，返回集合的一部分（切片）：

```php
$collection = collect([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

$slice = $collection->slice(4);

$slice->all();

// [5, 6, 7, 8, 9, 10]
```

如果你希望限制返回切片的大小，可以将期望的大小作为第二个参数传递给该方法：

```php
$slice = $collection->slice(4, 2);

$slice->all();

// [5, 6]
```

返回的切片默认会保留原始的键（key）。
如果你不希望保留原始键，可以使用 [values](#method-values) 方法重新为它们建立索引。

#### `sliding()` {.collection-method}

`sliding` 方法返回一个新的集合，其中包含表示“滑动窗口”视图的分块（chunk）：

```php
$collection = collect([1, 2, 3, 4, 5]);

$chunks = $collection->sliding(2);

$chunks->toArray();

// [[1, 2], [2, 3], [3, 4], [4, 5]]
```

这在与 [eachSpread](#method-eachspread) 方法结合使用时特别有用：

```php
$transactions->sliding(2)->eachSpread(function (Collection $previous, Collection $current) {
    $current->total = $previous->total + $current->amount;
});
```



你还可以选择传递第二个“步长”（`step`）参数，用于指定每个分块第一个元素之间的间隔距离：

```php
$collection = collect([1, 2, 3, 4, 5]);

$chunks = $collection->sliding(3, step: 2);

$chunks->toArray();

// [[1, 2, 3], [3, 4, 5]]
```

#### `sole()` {.collection-method}

`sole` 方法返回集合中第一个通过给定条件测试的元素，但前提是该条件只匹配**一个**元素：

```php
collect([1, 2, 3, 4])->sole(function (int $value, int $key) {
    return $value === 2;
});

// 2
```

你也可以向 `sole` 方法传递一个键/值对，它将返回集合中第一个与给定键值对匹配的元素，但同样要求只有**一个**元素匹配：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
]);

$collection->sole('product', 'Chair');

// ['product' => 'Chair', 'price' => 100]
```

另外，你还可以在不传递任何参数的情况下调用 `sole` 方法，以在集合中只有一个元素时返回该元素：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
]);

$collection->sole();

// ['product' => 'Desk', 'price' => 200]
```

如果集合中没有任何元素符合 `sole` 方法的条件，将会抛出 `\Illuminate\Collections\ItemNotFoundException` 异常。
如果有多个元素符合条件，则会抛出 `\Illuminate\Collections\MultipleItemsFoundException` 异常。

#### `some()` {.collection-method}

`some` 方法是 [contains](#method-contains) 方法的别名。

#### `sort()` {.collection-method}

`sort` 方法用于对集合进行排序。
排序后的集合会保留原始的数组键，因此在以下示例中，我们使用 [values](#method-values) 方法重置键为连续的数字索引：
```php
$collection = collect([5, 3, 1, 2, 4]);

$sorted = $collection->sort();

$sorted->values()->all();

// [1, 2, 3, 4, 5]
```



如果你的排序需求更加复杂，你可以向 `sort` 方法传递一个回调函数，以使用你自己的排序算法。
请参阅 PHP 文档中关于 [uasort](https://secure.php.net/manual/en/function.uasort.php#refsect1-function.uasort-parameters) 的说明，集合的 `sort` 方法在内部正是调用了该函数。

> [!注意]
> 如果你需要对嵌套数组或对象的集合进行排序，请参阅 [sortBy](#method-sortby) 和 [sortByDesc](#method-sortbydesc) 方法。

#### `sortBy()` {.collection-method}

`sortBy` 方法根据给定的键对集合进行排序。
排序后的集合会保留原始数组的键，因此在以下示例中，我们使用 [values](#method-values) 方法重置键为连续编号的索引：

```php
$collection = collect([
    ['name' => 'Desk', 'price' => 200],
    ['name' => 'Chair', 'price' => 100],
    ['name' => 'Bookcase', 'price' => 150],
]);

$sorted = $collection->sortBy('price');

$sorted->values()->all();

/*
    [
        ['name' => 'Chair', 'price' => 100],
        ['name' => 'Bookcase', 'price' => 150],
        ['name' => 'Desk', 'price' => 200],
    ]
*/
```

`sortBy` 方法的第二个参数可以接受 [排序标志（sort flags）](https://www.php.net/manual/en/function.sort.php)：

```php
$collection = collect([
    ['title' => 'Item 1'],
    ['title' => 'Item 12'],
    ['title' => 'Item 3'],
]);

$sorted = $collection->sortBy('title', SORT_NATURAL);

$sorted->values()->all();

/*
    [
        ['title' => 'Item 1'],
        ['title' => 'Item 3'],
        ['title' => 'Item 12'],
    ]
*/
```

此外，你也可以传递你自己的闭包来决定集合值的排序方式：

```php
$collection = collect([
    ['name' => 'Desk', 'colors' => ['Black', 'Mahogany']],
    ['name' => 'Chair', 'colors' => ['Black']],
    ['name' => 'Bookcase', 'colors' => ['Red', 'Beige', 'Brown']],
]);

$sorted = $collection->sortBy(function (array $product, int $key) {
    return count($product['colors']);
});

$sorted->values()->all();

/*
    [
        ['name' => 'Chair', 'colors' => ['Black']],
        ['name' => 'Desk', 'colors' => ['Black', 'Mahogany']],
        ['name' => 'Bookcase', 'colors' => ['Red', 'Beige', 'Brown']],
    ]
*/
```



如果你希望按照多个属性对集合进行排序，可以向 `sortBy` 方法传递一个由多个排序操作组成的数组。每个排序操作都应该是一个数组，包含你希望排序的属性名称以及排序方向：

```php
$collection = collect([
    ['name' => 'Taylor Otwell', 'age' => 34],
    ['name' => 'Abigail Otwell', 'age' => 30],
    ['name' => 'Taylor Otwell', 'age' => 36],
    ['name' => 'Abigail Otwell', 'age' => 32],
]);

$sorted = $collection->sortBy([
    ['name', 'asc'],
    ['age', 'desc'],
]);

$sorted->values()->all();

/*
    [
        ['name' => 'Abigail Otwell', 'age' => 32],
        ['name' => 'Abigail Otwell', 'age' => 30],
        ['name' => 'Taylor Otwell', 'age' => 36],
        ['name' => 'Taylor Otwell', 'age' => 34],
    ]
*/
```

当按照多个属性对集合进行排序时，你也可以提供定义每个排序操作的闭包：

```php
$collection = collect([
    ['name' => 'Taylor Otwell', 'age' => 34],
    ['name' => 'Abigail Otwell', 'age' => 30],
    ['name' => 'Taylor Otwell', 'age' => 36],
    ['name' => 'Abigail Otwell', 'age' => 32],
]);

$sorted = $collection->sortBy([
    fn (array $a, array $b) => $a['name'] <=> $b['name'],
    fn (array $a, array $b) => $b['age'] <=> $a['age'],
]);

$sorted->values()->all();

/*
    [
        ['name' => 'Abigail Otwell', 'age' => 32],
        ['name' => 'Abigail Otwell', 'age' => 30],
        ['name' => 'Taylor Otwell', 'age' => 36],
        ['name' => 'Taylor Otwell', 'age' => 34],
    ]
*/
```

#### `sortByDesc()` {.collection-method}

此方法与 [sortBy](#method-sortby) 方法具有相同的函数签名，但会以相反的顺序对集合进行排序。

#### `sortDesc()` {.collection-method}

此方法会以与 [sort](#method-sort) 方法相反的顺序对集合进行排序：

```php
$collection = collect([5, 3, 1, 2, 4]);

$sorted = $collection->sortDesc();

$sorted->values()->all();

// [5, 4, 3, 2, 1]
```

与 `sort` 不同，`sortDesc` 不支持传递闭包。
如果你需要使用自定义排序逻辑，请使用 [sort](#method-sort) 方法并反转你的比较结果。


#### `sortKeys()` {.collection-method}

`sortKeys` 方法根据底层关联数组的 **键（key）** 对集合进行排序：

```php
$collection = collect([
    'id' => 22345,
    'first' => 'John',
    'last' => 'Doe',
]);

$sorted = $collection->sortKeys();

$sorted->all();

/*
    [
        'first' => 'John',
        'id' => 22345,
        'last' => 'Doe',
    ]
*/
```

#### `sortKeysDesc()` {.collection-method}

该方法与 [sortKeys](#method-sortkeys) 方法具有相同的签名，但会以相反的顺序对集合进行排序。

#### `sortKeysUsing()` {.collection-method}

`sortKeysUsing` 方法使用一个回调函数，根据底层关联数组的 **键（key）** 对集合进行排序：

```php
$collection = collect([
    'ID' => 22345,
    'first' => 'John',
    'last' => 'Doe',
]);

$sorted = $collection->sortKeysUsing('strnatcasecmp');

$sorted->all();

/*
    [
        'first' => 'John',
        'ID' => 22345,
        'last' => 'Doe',
    ]
*/
```

回调函数必须是一个比较函数，返回一个小于、等于或大于零的整数。
更多信息请参考 PHP 文档中关于 [uksort](https://www.php.net/manual/en/function.uksort.php#refsect1-function.uksort-parameters) 的说明，`sortKeysUsing` 方法在内部正是使用了该函数。

#### `splice()` {.collection-method}

`splice` 方法会从指定索引开始，**移除并返回** 一段集合片段：

```php
$collection = collect([1, 2, 3, 4, 5]);

$chunk = $collection->splice(2);

$chunk->all();

// [3, 4, 5]

$collection->all();

// [1, 2]
```

你可以传入第二个参数来 **限制返回的集合长度**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$chunk = $collection->splice(2, 1);

$chunk->all();

// [3]

$collection->all();

// [1, 2, 4, 5]
```

此外，你还可以传入第三个参数，用于 **替换被移除的项**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$chunk = $collection->splice(2, 1, [10, 11]);

$chunk->all();

// [3]

$collection->all();

// [1, 2, 10, 11, 4, 5]
```

#### `split()` {.collection-method}

`split` 方法将集合 **平均分成指定数量的组**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$groups = $collection->split(3);

$groups->all();

// [[1, 2], [3, 4], [5]]
```



#### `splitIn()` {.collection-method}

`splitIn` 方法将集合拆分为指定数量的组，**在分配剩余元素到最后一组之前，会优先填满前面的组**：

```php
$collection = collect([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

$groups = $collection->splitIn(3);

$groups->all();

// [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
```

#### `sum()` {.collection-method}

`sum` 方法返回集合中所有元素的 **总和**：

```php
collect([1, 2, 3, 4, 5])->sum();

// 15
```

如果集合包含嵌套数组或对象，可以传入一个键名，用于指定求和的字段：

```php
$collection = collect([
    ['name' => 'JavaScript: The Good Parts', 'pages' => 176],
    ['name' => 'JavaScript: The Definitive Guide', 'pages' => 1096],
]);

$collection->sum('pages');

// 1272
```

此外，你也可以传入一个 **自定义闭包** 来确定要累加的值：

```php
$collection = collect([
    ['name' => 'Chair', 'colors' => ['Black']],
    ['name' => 'Desk', 'colors' => ['Black', 'Mahogany']],
    ['name' => 'Bookcase', 'colors' => ['Red', 'Beige', 'Brown']],
]);

$collection->sum(function (array $product) {
    return count($product['colors']);
});

// 6
```

#### `take()` {.collection-method}

`take` 方法返回一个 **包含指定数量元素的新集合**：

```php
$collection = collect([0, 1, 2, 3, 4, 5]);

$chunk = $collection->take(3);

$chunk->all();

// [0, 1, 2]
```

你也可以传入一个 **负整数**，从集合的末尾取出指定数量的元素：

```php
$collection = collect([0, 1, 2, 3, 4, 5]);

$chunk = $collection->take(-2);

$chunk->all();

// [4, 5]
```

#### `takeUntil()` {.collection-method}

`takeUntil` 方法会从集合中返回元素，**直到给定的回调函数返回 `true` 为止**：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->takeUntil(function (int $item) {
    return $item >= 3;
});

$subset->all();

// [1, 2]
```

你也可以传入一个 **简单值**，方法会返回直到遇到该值为止的所有元素：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->takeUntil(3);

$subset->all();

// [1, 2]
```

> [!警告]
> 如果未找到指定的值，或回调函数始终未返回 `true`，则 `takeUntil` 方法会返回集合中的所有元素。



#### `takeWhile()` {.collection-method}

`takeWhile` 方法会从集合中返回元素，**直到给定的回调函数返回 `false` 为止**：

```php
$collection = collect([1, 2, 3, 4]);

$subset = $collection->takeWhile(function (int $item) {
    return $item < 3;
});

$subset->all();

// [1, 2]
```

> [!警告]
> 如果回调函数始终未返回 `false`，`takeWhile` 方法会返回集合中的所有元素。

#### `tap()` {.collection-method}

`tap` 方法会将集合传递给给定的回调函数，让你在特定位置“查看”集合或对其做一些操作，同时 **不改变原集合本身**。`tap` 方法返回原集合：

```php
collect([2, 4, 3, 1, 5])
    ->sort()
    ->tap(function (Collection $collection) {
        Log::debug('Values after sorting', $collection->values()->all());
    })
    ->shift();

// 1
```

#### `times()` {.collection-method}

静态方法 `times` 会通过调用给定闭包指定次数来创建一个新集合：

```php
$collection = Collection::times(10, function (int $number) {
    return $number * 9;
});

$collection->all();

// [9, 18, 27, 36, 45, 54, 63, 72, 81, 90]
```

#### `toArray()` {.collection-method}

`toArray` 方法将集合 **转换为普通 PHP 数组**。如果集合中的值是 [Eloquent](/docs/laravel/12.x/eloquent) 模型，它们也会被转换为数组：

```php
$collection = collect(['name' => 'Desk', 'price' => 200]);

$collection->toArray();

/*
    [
        ['name' => 'Desk', 'price' => 200],
    ]
*/
```

> [!警告]
> `toArray` 会将集合中所有实现了 `Arrayable` 接口的嵌套对象也转换为数组。如果你只想获取集合的底层原始数组，请使用 [all](#method-all) 方法。

#### `toJson()` {.collection-method}

`toJson` 方法将集合 **转换为 JSON 字符串**：

```php
$collection = collect(['name' => 'Desk', 'price' => 200]);

$collection->toJson();

// '{"name":"Desk", "price":200}'
```



#### `transform()` {.collection-method}

`transform` 方法会遍历集合，并对每个元素调用给定的回调函数。集合中的元素将被回调函数返回的值 **替换**：

```php
$collection = collect([1, 2, 3, 4, 5]);

$collection->transform(function (int $item, int $key) {
    return $item * 2;
});

$collection->all();

// [2, 4, 6, 8, 10]
```

> [!警告]
> 与大多数集合方法不同，`transform` 会 **修改原集合本身**。如果你希望生成一个新的集合，请使用 [map](#method-map) 方法。

#### `undot()` {.collection-method}

`undot` 方法可以将使用 **点（dot）表示法** 的一维集合展开为多维集合：

```php
$person = collect([
    'name.first_name' => 'Marie',
    'name.last_name' => 'Valentine',
    'address.line_1' => '2992 Eagle Drive',
    'address.line_2' => '',
    'address.suburb' => 'Detroit',
    'address.state' => 'MI',
    'address.postcode' => '48219'
]);

$person = $person->undot();

$person->toArray();

/*
    [
        "name" => [
            "first_name" => "Marie",
            "last_name" => "Valentine",
        ],
        "address" => [
            "line_1" => "2992 Eagle Drive",
            "line_2" => "",
            "suburb" => "Detroit",
            "state" => "MI",
            "postcode" => "48219",
        ],
    ]
*/
```

#### `union()` {.collection-method}

`union` 方法会将给定数组 **合并到集合中**。如果给定数组中的键在原集合中已存在，则原集合的值会被保留：

```php
$collection = collect([1 => ['a'], 2 => ['b']]);

$union = $collection->union([3 => ['c'], 1 => ['d']]);

$union->all();

// [1 => ['a'], 2 => ['b'], 3 => ['c']]
```

#### `unique()` {.collection-method}

`unique` 方法返回集合中 **所有唯一的元素**。返回的集合会保留原数组的键，因此通常需要使用 [values](#method-values) 方法来重置为连续的索引：

```php
$collection = collect([1, 1, 2, 2, 3, 4, 2]);

$unique = $collection->unique();

$unique->values()->all();

// [1, 2, 3, 4]
```



在处理嵌套数组或对象时，你可以指定用于判断唯一性的键：

```php
$collection = collect([
    ['name' => 'iPhone 6', 'brand' => 'Apple', 'type' => 'phone'],
    ['name' => 'iPhone 5', 'brand' => 'Apple', 'type' => 'phone'],
    ['name' => 'Apple Watch', 'brand' => 'Apple', 'type' => 'watch'],
    ['name' => 'Galaxy S6', 'brand' => 'Samsung', 'type' => 'phone'],
    ['name' => 'Galaxy Gear', 'brand' => 'Samsung', 'type' => 'watch'],
]);

$unique = $collection->unique('brand');

$unique->values()->all();

/*
    [
        ['name' => 'iPhone 6', 'brand' => 'Apple', 'type' => 'phone'],
        ['name' => 'Galaxy S6', 'brand' => 'Samsung', 'type' => 'phone'],
    ]
*/
```

你也可以传入自定义闭包来指定哪个值用于判断元素的唯一性：

```php
$unique = $collection->unique(function (array $item) {
    return $item['brand'].$item['type'];
});

$unique->values()->all();

/*
    [
        ['name' => 'iPhone 6', 'brand' => 'Apple', 'type' => 'phone'],
        ['name' => 'Apple Watch', 'brand' => 'Apple', 'type' => 'watch'],
        ['name' => 'Galaxy S6', 'brand' => 'Samsung', 'type' => 'phone'],
        ['name' => 'Galaxy Gear', 'brand' => 'Samsung', 'type' => 'watch'],
    ]
*/
```
`unique` 方法在检查元素值时使用 **宽松比较**，意味着字符串形式的数字会被认为等于相同值的整数。若要使用 **严格比较**，请使用 [uniqueStrict](#method-uniquestrict) 方法。

> [!注意]
> 当使用 [Eloquent 集合](/docs/laravel/12.x/eloquent-collections#method-unique) 时，该方法的行为会有所不同。

#### `uniqueStrict()` {.collection-method}

此方法与 [unique](#method-unique) 方法签名相同，但所有值都使用 **严格比较** 进行判断。

#### `unless()` {.collection-method}

`unless` 方法会在给定条件 **不为 true** 时执行回调函数。集合实例和方法的第一个参数会传递给闭包：

```php
$collection = collect([1, 2, 3]);

$collection->unless(true, function (Collection $collection, bool $value) {
    return $collection->push(4);
});

$collection->unless(false, function (Collection $collection, bool $value) {
    return $collection->push(5);
});

$collection->all();

// [1, 2, 3, 5]
```



`unless` 方法可以接受第二个回调函数。当传递给 `unless` 方法的第一个参数计算结果为 `true` 时，第二个回调函数将会被执行：

```php
$collection = collect([1, 2, 3]);

$collection->unless(true, function (Collection $collection, bool $value) {
    return $collection->push(4);
}, function (Collection $collection, bool $value) {
    return $collection->push(5);
});

$collection->all();

// [1, 2, 3, 5]
```

`unless` 的反义方法请参阅 [`when`](#method-when) 方法。

#### `unlessEmpty()` {.collection-method}

是 [`whenNotEmpty`](#method-whennotempty) 方法的别名。

#### `unlessNotEmpty()` {.collection-method}

是 [`whenEmpty`](#method-whenempty) 方法的别名。

#### `unwrap()` {.collection-method}

静态方法 `unwrap` 会从给定的值中返回集合的底层元素（如果适用）：

```php
Collection::unwrap(collect('John Doe'));

// ['John Doe']

Collection::unwrap(['John Doe']);

// ['John Doe']

Collection::unwrap('John Doe');

// 'John Doe'
```

#### `value()` {.collection-method}

`value` 方法从集合的第一个元素中获取指定的值：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Speaker', 'price' => 400],
]);

$value = $collection->value('price');

// 200
```

#### `values()` {.collection-method}

`values` 方法返回一个键被重置为连续整数的新集合：

```php
$collection = collect([
    10 => ['product' => 'Desk', 'price' => 200],
    11 => ['product' => 'Desk', 'price' => 200],
]);

$values = $collection->values();

$values->all();

/*
    [
        0 => ['product' => 'Desk', 'price' => 200],
        1 => ['product' => 'Desk', 'price' => 200],
    ]
*/
```

#### `when()` {.collection-method}

`when` 方法会在传递给它的第一个参数计算结果为 `true` 时执行给定的回调函数。
集合实例以及传递给 `when` 方法的第一个参数都会被传入闭包中：

```php
$collection = collect([1, 2, 3]);

$collection->when(true, function (Collection $collection, bool $value) {
    return $collection->push(4);
});

$collection->when(false, function (Collection $collection, bool $value) {
    return $collection->push(5);
});

$collection->all();

// [1, 2, 3, 4]
```



`when` 方法可以接受第二个回调函数。当传递给 `when` 方法的第一个参数计算结果为 `false` 时，第二个回调函数将会被执行：

```php
$collection = collect([1, 2, 3]);

$collection->when(false, function (Collection $collection, bool $value) {
    return $collection->push(4);
}, function (Collection $collection, bool $value) {
    return $collection->push(5);
});

$collection->all();

// [1, 2, 3, 5]
```

`when` 的反义方法请参阅 [`unless`](#method-unless) 方法。

#### `whenEmpty()` {.collection-method}

`whenEmpty` 方法会在集合为空时执行给定的回调函数：

```php
$collection = collect(['Michael', 'Tom']);

$collection->whenEmpty(function (Collection $collection) {
    return $collection->push('Adam');
});

$collection->all();

// ['Michael', 'Tom']

$collection = collect();

$collection->whenEmpty(function (Collection $collection) {
    return $collection->push('Adam');
});

$collection->all();

// ['Adam']
```

`whenEmpty` 方法也可以接受第二个闭包，当集合 **不为空** 时执行该闭包：

```php
$collection = collect(['Michael', 'Tom']);

$collection->whenEmpty(function (Collection $collection) {
    return $collection->push('Adam');
}, function (Collection $collection) {
    return $collection->push('Taylor');
});

$collection->all();

// ['Michael', 'Tom', 'Taylor']
```

`whenEmpty` 的反义方法请参阅 [`whenNotEmpty`](#method-whennotempty) 方法。

#### `whenNotEmpty()` {.collection-method}

`whenNotEmpty` 方法会在集合 **不为空** 时执行给定的回调函数：

```php
$collection = collect(['Michael', 'Tom']);

$collection->whenNotEmpty(function (Collection $collection) {
    return $collection->push('Adam');
});

$collection->all();

// ['Michael', 'Tom', 'Adam']

$collection = collect();

$collection->whenNotEmpty(function (Collection $collection) {
    return $collection->push('Adam');
});

$collection->all();

// []
```

`whenNotEmpty` 方法也可以接受第二个闭包，当集合 **为空** 时执行该闭包：

```php
$collection = collect();

$collection->whenNotEmpty(function (Collection $collection) {
    return $collection->push('Adam');
}, function (Collection $collection) {
    return $collection->push('Taylor');
});

$collection->all();

// ['Taylor']
```



`whenNotEmpty` 的反义方法请参阅 [`whenEmpty`](#method-whenempty) 方法。

#### `where()` {.collection-method}

`where` 方法根据指定的键 / 值对来过滤集合：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
    ['product' => 'Bookcase', 'price' => 150],
    ['product' => 'Door', 'price' => 100],
]);

$filtered = $collection->where('price', 100);

$filtered->all();

/*
    [
        ['product' => 'Chair', 'price' => 100],
        ['product' => 'Door', 'price' => 100],
    ]
*/
```

`where` 方法在比较元素值时使用“宽松（loose）”比较，也就是说，一个字符串形式的数字会被视为与相同数值的整数相等。
若要使用“严格（strict）”比较，请使用 [`whereStrict`](#method-wherestrict) 方法。

此外，你还可以将比较运算符作为第二个参数传入。支持的运算符包括：
`'==='`, `'!=='`, `'!='`, `'=='`, `'='`, `'<'>'`, `'>'`, `'<'`, `'>='`, 和 `'<='`：

```php
$collection = collect([
    ['name' => 'Jim', 'deleted_at' => '2019-01-01 00:00:00'],
    ['name' => 'Sally', 'deleted_at' => '2019-01-02 00:00:00'],
    ['name' => 'Sue', 'deleted_at' => null],
]);

$filtered = $collection->where('deleted_at', '!=', null);

$filtered->all();

/*
    [
        ['name' => 'Jim', 'deleted_at' => '2019-01-01 00:00:00'],
        ['name' => 'Sally', 'deleted_at' => '2019-01-02 00:00:00'],
    ]
*/
```

#### `whereStrict()` {.collection-method}

此方法与 [`where`](#method-where) 方法具有相同的签名；
不同之处在于它使用“严格（strict）”比较来比较所有值。

#### `whereBetween()` {.collection-method}

`whereBetween` 方法通过判断指定的元素值是否位于给定范围内来过滤集合：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 80],
    ['product' => 'Bookcase', 'price' => 150],
    ['product' => 'Pencil', 'price' => 30],
    ['product' => 'Door', 'price' => 100],
]);

$filtered = $collection->whereBetween('price', [100, 200]);

$filtered->all();

/*
    [
        ['product' => 'Desk', 'price' => 200],
        ['product' => 'Bookcase', 'price' => 150],
        ['product' => 'Door', 'price' => 100],
    ]
*/
```



#### `whereIn()` {.collection-method}

`whereIn` 方法会移除集合中那些其指定键的值 **不在** 给定数组中的元素：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
    ['product' => 'Bookcase', 'price' => 150],
    ['product' => 'Door', 'price' => 100],
]);

$filtered = $collection->whereIn('price', [150, 200]);

$filtered->all();

/*
    [
        ['product' => 'Desk', 'price' => 200],
        ['product' => 'Bookcase', 'price' => 150],
    ]
*/
```

`whereIn` 方法在比较元素值时使用“宽松（loose）”比较，也就是说，一个字符串形式的数字会被视为与相同数值的整数相等。
若要使用“严格（strict）”比较，请使用 [`whereInStrict`](#method-whereinstrict) 方法。

#### `whereInStrict()` {.collection-method}

此方法与 [`whereIn`](#method-wherein) 方法具有相同的签名；
不同之处在于它使用“严格（strict）”比较来比较所有值。

#### `whereInstanceOf()` {.collection-method}

`whereInstanceOf` 方法根据指定的类类型过滤集合：

```php
use App\Models\User;
use App\Models\Post;

$collection = collect([
    new User,
    new User,
    new Post,
]);

$filtered = $collection->whereInstanceOf(User::class);

$filtered->all();

// [App\Models\User, App\Models\User]
```

#### `whereNotBetween()` {.collection-method}

`whereNotBetween` 方法通过判断指定的元素值是否 **不在** 给定范围内来过滤集合：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 80],
    ['product' => 'Bookcase', 'price' => 150],
    ['product' => 'Pencil', 'price' => 30],
    ['product' => 'Door', 'price' => 100],
]);

$filtered = $collection->whereNotBetween('price', [100, 200]);

$filtered->all();

/*
    [
        ['product' => 'Chair', 'price' => 80],
        ['product' => 'Pencil', 'price' => 30],
    ]
*/
```

#### `whereNotIn()` {.collection-method}

`whereNotIn` 方法会移除集合中那些其指定键的值 **包含在** 给定数组中的元素：

```php
$collection = collect([
    ['product' => 'Desk', 'price' => 200],
    ['product' => 'Chair', 'price' => 100],
    ['product' => 'Bookcase', 'price' => 150],
    ['product' => 'Door', 'price' => 100],
]);

$filtered = $collection->whereNotIn('price', [150, 200]);

$filtered->all();

/*
    [
        ['product' => 'Chair', 'price' => 100],
        ['product' => 'Door', 'price' => 100],
    ]
*/
```



`whereNotIn` 方法在比较元素值时使用“宽松（loose）”比较，也就是说，一个字符串形式的数字会被视为与相同数值的整数相等。
若要使用“严格（strict）”比较，请使用 [`whereNotInStrict`](#method-wherenotinstrict) 方法。

#### `whereNotInStrict()` {.collection-method}

此方法与 [`whereNotIn`](#method-wherenotin) 方法具有相同的签名；
不同之处在于它使用“严格（strict）”比较来比较所有值。

#### `whereNotNull()` {.collection-method}

`whereNotNull` 方法返回集合中指定键的值 **不为 `null`** 的元素：

```php
$collection = collect([
    ['name' => 'Desk'],
    ['name' => null],
    ['name' => 'Bookcase'],
]);

$filtered = $collection->whereNotNull('name');

$filtered->all();

/*
    [
        ['name' => 'Desk'],
        ['name' => 'Bookcase'],
    ]
*/
```

#### `whereNull()` {.collection-method}

`whereNull` 方法返回集合中指定键的值 **为 `null`** 的元素：

```php
$collection = collect([
    ['name' => 'Desk'],
    ['name' => null],
    ['name' => 'Bookcase'],
]);

$filtered = $collection->whereNull('name');

$filtered->all();

/*
    [
        ['name' => null],
    ]
*/
```

#### `wrap()` {.collection-method}

静态方法 `wrap` 会在适用的情况下，将给定的值包装成一个集合：

```php
use Illuminate\Support\Collection;

$collection = Collection::wrap('John Doe');

$collection->all();

// ['John Doe']

$collection = Collection::wrap(['John Doe']);

$collection->all();

// ['John Doe']

$collection = Collection::wrap(collect('John Doe'));

$collection->all();

// ['John Doe']
```

#### `zip()` {.collection-method}

`zip` 方法会将给定数组的值与原始集合中对应索引的值合并在一起：

```php
$collection = collect(['Chair', 'Desk']);

$zipped = $collection->zip([100, 200]);

$zipped->all();

// [['Chair', 100], ['Desk', 200]]
```

## Higher Order Messages

集合还支持 “高阶消息”（Higher Order Messages），
它们是用于在集合上执行常见操作的简写形式。

支持高阶消息的集合方法包括：
[`average`](#method-average)、[`avg`](#method-avg)、[`contains`](#method-contains)、[`each`](#method-each)、[`every`](#method-every)、[`filter`](#method-filter)、[`first`](#method-first)、[`flatMap`](#method-flatmap)、[`groupBy`](#method-groupby)、[`keyBy`](#method-keyby)、[`map`](#method-map)、[`max`](#method-max)、[`min`](#method-min)、[`partition`](#method-partition)、[`reject`](#method-reject)、[`skipUntil`](#method-skipuntil)、[`skipWhile`](#method-skipwhile)、[`some`](#method-some)、[`sortBy`](#method-sortby)、[`sortByDesc`](#method-sortbydesc)、[`sum`](#method-sum)、[`takeUntil`](#method-takeuntil)、[`takeWhile`](#method-takewhile)、以及 [`unique`](#method-unique)。



每个高阶消息（Higher Order Message）都可以作为集合实例的动态属性来访问。
例如，我们可以使用 `each` 高阶消息来对集合中的每个对象调用某个方法：

```php
use App\Models\User;

$users = User::where('votes', '>', 500)->get();

$users->each->markAsVip();
```

同样地，我们可以使用 `sum` 高阶消息来获取某个用户集合中所有“votes”的总数：

```php
$users = User::where('group', 'Development')->get();

return $users->sum->votes;
```

## 惰性集合（Lazy Collections）

### 简介

> [!警告]
> 在学习 Laravel 的惰性集合之前，请先熟悉一下 [PHP 生成器（Generators）](https://www.php.net/manual/en/language.generators.overview.php)。

为了补充功能强大的 `Collection` 类，`LazyCollection` 类利用 PHP 的 [生成器（generators）](https://www.php.net/manual/en/language.generators.overview.php)，让你可以在处理超大数据集时保持低内存占用。

举个例子，假设你的应用需要处理一个数GB大小的日志文件，并希望借助 Laravel 的集合方法来解析这些日志。
与一次性将整个文件读入内存不同，惰性集合可以让你在任意时间只保留文件的一小部分在内存中：

```php
use App\Models\LogEntry;
use Illuminate\Support\LazyCollection;

LazyCollection::make(function () {
    $handle = fopen('log.txt', 'r');

    while (($line = fgets($handle)) !== false) {
        yield $line;
    }

    fclose($handle);
})->chunk(4)->map(function (array $lines) {
    return LogEntry::fromLines($lines);
})->each(function (LogEntry $logEntry) {
    // 处理日志条目...
});
```



或者，假设你需要遍历 10,000 个 Eloquent 模型。
当使用传统的 Laravel 集合时，所有 10,000 个 Eloquent 模型都必须同时被加载到内存中：

```php
use App\Models\User;

$users = User::all()->filter(function (User $user) {
    return $user->id > 500;
});
```

然而，查询构建器的 `cursor` 方法会返回一个 `LazyCollection` 实例。
这使得你仍然只需对数据库执行一次查询，但在任意时刻内存中只保留一个 Eloquent 模型。
在此示例中，`filter` 回调函数在我们真正逐个遍历用户时才会被执行，从而大幅降低内存使用：

```php
use App\Models\User;

$users = User::cursor()->filter(function (User $user) {
    return $user->id > 500;
});

foreach ($users as $user) {
    echo $user->id;
}
```

### 创建惰性集合

要创建一个惰性集合实例，你应当将一个 PHP 生成器函数传递给集合的 `make` 方法：

```php
use Illuminate\Support\LazyCollection;

LazyCollection::make(function () {
    $handle = fopen('log.txt', 'r');

    while (($line = fgets($handle)) !== false) {
        yield $line;
    }

    fclose($handle);
});
```

### Enumerable 接口（Contract）

几乎所有可用于 `Collection` 类的方法，在 `LazyCollection` 类中同样可用。
这两个类都实现了 `Illuminate\Support\Enumerable` 接口，该接口定义了以下方法：

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

<div class="collection-method-list" markdown="1">

[all](#method-all)
[average](#method-average)
[avg](#method-avg)
[chunk](#method-chunk)
[chunkWhile](#method-chunkwhile)
[collapse](#method-collapse)
[collect](#method-collect)
[combine](#method-combine)
[concat](#method-concat)
[contains](#method-contains)
[containsStrict](#method-containsstrict)
[count](#method-count)
[countBy](#method-countBy)
[crossJoin](#method-crossjoin)
[dd](#method-dd)
[diff](#method-diff)
[diffAssoc](#method-diffassoc)
[diffKeys](#method-diffkeys)
[dump](#method-dump)
[duplicates](#method-duplicates)
[duplicatesStrict](#method-duplicatesstrict)
[each](#method-each)
[eachSpread](#method-eachspread)
[every](#method-every)
[except](#method-except)
[filter](#method-filter)
[first](#method-first)
[firstOrFail](#method-first-or-fail)
[firstWhere](#method-first-where)
[flatMap](#method-flatmap)
[flatten](#method-flatten)
[flip](#method-flip)
[forPage](#method-forpage)
[get](#method-get)
[groupBy](#method-groupby)
[has](#method-has)
[implode](#method-implode)
[intersect](#method-intersect)
[intersectAssoc](#method-intersectAssoc)
[intersectByKeys](#method-intersectbykeys)
[isEmpty](#method-isempty)
[isNotEmpty](#method-isnotempty)
[join](#method-join)
[keyBy](#method-keyby)
[keys](#method-keys)
[last](#method-last)
[macro](#method-macro)
[make](#method-make)
[map](#method-map)
[mapInto](#method-mapinto)
[mapSpread](#method-mapspread)
[mapToGroups](#method-maptogroups)
[mapWithKeys](#method-mapwithkeys)
[max](#method-max)
[median](#method-median)
[merge](#method-merge)
[mergeRecursive](#method-mergerecursive)
[min](#method-min)
[mode](#method-mode)
[nth](#method-nth)
[only](#method-only)
[pad](#method-pad)
[partition](#method-partition)
[pipe](#method-pipe)
[pluck](#method-pluck)
[random](#method-random)
[reduce](#method-reduce)
[reject](#method-reject)
[replace](#method-replace)
[replaceRecursive](#method-replacerecursive)
[reverse](#method-reverse)
[search](#method-search)
[shuffle](#method-shuffle)
[skip](#method-skip)
[slice](#method-slice)
[sole](#method-sole)
[some](#method-some)
[sort](#method-sort)
[sortBy](#method-sortby)
[sortByDesc](#method-sortbydesc)
[sortKeys](#method-sortkeys)
[sortKeysDesc](#method-sortkeysdesc)
[split](#method-split)
[sum](#method-sum)
[take](#method-take)
[tap](#method-tap)
[times](#method-times)
[toArray](#method-toarray)
[toJson](#method-tojson)
[union](#method-union)
[unique](#method-unique)
[uniqueStrict](#method-uniquestrict)
[unless](#method-unless)
[unlessEmpty](#method-unlessempty)
[unlessNotEmpty](#method-unlessnotempty)
[unwrap](#method-unwrap)
[values](#method-values)
[when](#method-when)
[whenEmpty](#method-whenempty)
[whenNotEmpty](#method-whennotempty)
[where](#method-where)
[whereStrict](#method-wherestrict)
[whereBetween](#method-wherebetween)
[whereIn](#method-wherein)
[whereInStrict](#method-whereinstrict)
[whereInstanceOf](#method-whereinstanceof)
[whereNotBetween](#method-wherenotbetween)
[whereNotIn](#method-wherenotin)
[whereNotInStrict](#method-wherenotinstrict)
[wrap](#method-wrap)
[zip](#method-zip)

</div>

> [!警告]
> 会改变集合内容的方法（例如 `shift`、`pop`、`prepend` 等）在 `LazyCollection` 类中 **不可用**。



### 惰性集合方法（Lazy Collection Methods）

除了 `Enumerable` 接口中定义的方法之外，`LazyCollection` 类还包含以下方法：

#### `takeUntilTimeout()` {.collection-method}

`takeUntilTimeout` 方法会返回一个新的惰性集合，该集合会在指定的时间之前持续枚举（遍历）值。
当到达该时间后，集合将停止枚举：

```php
$lazyCollection = LazyCollection::times(INF)
    ->takeUntilTimeout(now()->addMinute());

$lazyCollection->each(function (int $number) {
    dump($number);

    sleep(1);
});

// 1
// 2
// ...
// 58
// 59
```

为了说明此方法的用法，假设某个应用需要通过数据库游标（cursor）提交发票。
你可以定义一个 [计划任务](/docs/laravel/12.x/scheduling)，让它每 15 分钟运行一次，并且每次最多只处理 14 分钟的发票提交：

```php
use App\Models\Invoice;
use Illuminate\Support\Carbon;

Invoice::pending()->cursor()
    ->takeUntilTimeout(
        Carbon::createFromTimestamp(LARAVEL_START)->add(14, 'minutes')
    )
    ->each(fn (Invoice $invoice) => $invoice->submit());
```

#### `tapEach()` {.collection-method}

`each` 方法会立即对集合中的每一项调用指定的回调函数，
而 `tapEach` 方法则是在项目被**逐个取出时**才调用回调函数：

```php
// 到目前为止还没有输出任何内容...
$lazyCollection = LazyCollection::times(INF)->tapEach(function (int $value) {
    dump($value);
});

// 取出三个项目时输出内容...
$array = $lazyCollection->take(3)->all();

// 1
// 2
// 3
```

#### `throttle()` {.collection-method}

`throttle` 方法会限制（节流）惰性集合的处理速度，使得每个值都在指定的秒数之后才返回。
该方法在你需要与具有请求速率限制的外部 API 交互时尤其有用：

```php
use App\Models\User;

User::where('vip', true)
    ->cursor()
    ->throttle(seconds: 1)
    ->each(function (User $user) {
        // Call external API...
    });
```



<a name="method-remember"></a>
#### `remember()`

`remember` 方法返回一个新的惰性集合，这个集合已经记住（缓存）已枚举的所有值，当再次枚举该集合时不会获取它们：

```php
// 没执行任何查询
$users = User::cursor()->remember();

// 执行了查询操作
// 并且前 5 个用户数据已经在数据库中查询完成
$users->take(5)->all();

// 前 5 个用户数据从缓存中获取
// 剩余的（15 个）用户数据从数据库中查询
$users->take(20)->all();
```
